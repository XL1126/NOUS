"""目标栈、元认知、自我模型、他者模型、内言。

文献：Miller & Cohen 2001；Fleming & Dolan 2012；Christoff 2016 DMN。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np


@dataclass
class Goal:
    text: str
    priority: float = 0.5
    source: str = "intrinsic"  # intrinsic/user/social
    progress: float = 0.0


class GoalStack:
    def __init__(self, max_depth: int = 6):
        self.goals: List[Goal] = []
        self.max_depth = max_depth

    def push(self, goal: Goal) -> None:
        self.goals = [g for g in self.goals if g.text != goal.text]
        self.goals.insert(0, goal)
        self.goals.sort(key=lambda g: -g.priority)
        self.goals = self.goals[: self.max_depth]

    def pop(self) -> Optional[Goal]:
        return self.goals.pop(0) if self.goals else None

    def current(self) -> Optional[Goal]:
        return self.goals[0] if self.goals else None

    def retarget_from_need(self, need: str) -> None:
        mapping = {
            "rest": ("恢复能量/降低睡压", 0.85),
            "safety": ("确认环境安全并降压", 0.8),
            "social": ("维持对话联结", 0.65),
            "curiosity": ("探索新概念/填补知识空白", 0.7),
            "maintain": ("跟上对话并维护稳态", 0.55),
        }
        text, prio = mapping.get(need, mapping["maintain"])
        self.push(Goal(text, priority=prio, source="intrinsic"))

    def describe(self) -> str:
        if not self.goals:
            return "暂无显式目标。"
        g = self.goals[0]
        extra = f"（栈上还有{len(self.goals)-1}项）" if len(self.goals) > 1 else ""
        return f"当前目标：{g.text}{extra}"


class MetaCognition:
    def __init__(self):
        self.last_confidence = 0.5
        self.uncertainty = 0.5

    def evaluate(self, understanding: float, novelty: float, confusion: float) -> float:
        conf = float(np.clip(
            0.45 * understanding + 0.25 * (1 - novelty) + 0.3 * (1 - confusion),
            0.05, 0.99,
        ))
        self.last_confidence = conf
        self.uncertainty = 1 - conf
        return conf


class SelfModel:
    def __init__(self, name: str = "NOUS"):
        self.name = name
        self.identity_bits: List[str] = []
        self.narrative: List[str] = []
        self.confidence = 0.55
        self.capabilities = {
            "对话": True, "被教学": True, "在线学习": True,
            "自主思维": True, "长篇创作": False, "外部搜索": False,
        }

    def add_identity(self, bit: str) -> None:
        bit = (bit or "").strip()
        if bit and bit not in self.identity_bits:
            self.identity_bits.append(bit)
            if len(self.identity_bits) > 30:
                self.identity_bits = self.identity_bits[-30:]

    def note(self, line: str) -> None:
        self.narrative.append(line)
        if len(self.narrative) > 50:
            self.narrative = self.narrative[-50:]

    def who(self) -> str:
        bits = "；".join(self.identity_bits[-3:]) if self.identity_bits else "一个正在成长的计算心智"
        return f"我是{self.name}。{bits}。"

    def can(self, skill: str) -> bool:
        return bool(self.capabilities.get(skill, False))


class OtherModel:
    """简化心智理论：跟踪对话者。"""

    def __init__(self):
        self.name = ""
        self.patience = 0.7
        self.expertise = 0.4
        self.corrections = 0
        self.turns = 0

    def observe(self, text: str, intent: str, corrected: bool = False) -> None:
        self.turns += 1
        if corrected:
            self.corrections += 1
            self.patience = float(np.clip(self.patience - 0.08, 0.1, 1.0))
        if intent == "teach_fact":
            self.expertise = float(np.clip(self.expertise + 0.05, 0, 1))
        if len(text) < 6:
            self.patience = float(np.clip(self.patience - 0.01, 0.1, 1.0))

    def summary(self) -> str:
        return f"对方耐心~{self.patience:.2f} 教学倾向~{self.expertise:.2f}"


class InnerSpeech:
    """内言/默认模式：自我提问、反事实、重访。"""

    TEMPLATES = [
        "我对「{t}」的理解还缺哪一块？",
        "如果换一种说法，「{t}」会不会更清楚？",
        "刚才关于{t}的预测误差说明了什么？",
        "有没有和{t}相关的旧情景可以对照？",
        "下一步该教自己什么才能更懂{t}？",
        "身体现在更需要{need}还是继续{t}？",
        "如果用户纠正我，我会改哪一条绑定？",
    ]

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.log: List[str] = []

    def maybe_think(self, external_drive: float, energy: float, sleep: float,
                    topic: str, need: str) -> Optional[str]:
        # 外部输入弱时更易走神（Christoff）
        p = 0.08 + 0.25 * (1 - min(external_drive, 1.0)) + 0.15 * (1 - energy) - 0.2 * sleep
        if float(self.rng.random()) > p:
            return None
        tpl = self.TEMPLATES[int(self.rng.integers(0, len(self.TEMPLATES)))]
        thought = tpl.format(t=topic or "当前话题", need=need)
        self.log.append(thought)
        if len(self.log) > 40:
            self.log = self.log[-40:]
        return thought

    def deliberate(self, topic: str, facts: List[str], need: str) -> str:
        """更重的审慎思维（/think）。"""
        bits = []
        bits.append(f"审慎思考「{topic or '当前'}」：")
        if facts:
            bits.append("已绑定：" + "；".join(facts[:3]) + "。")
        else:
            bits.append("语义上还很空，需要你教我或我追问。")
        bits.append(f"身体驱动指向 {need}。")
        bits.append(self.TEMPLATES[int(self.rng.integers(0, len(self.TEMPLATES)))].format(
            t=topic or "这件事", need=need))
        text = " ".join(bits)
        self.log.append(text)
        return text
