"""课程训练：教事实、对话、巩固、发展阶段推进。"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .mind import NousMind
from .development import stage_for


DEFAULT_CURRICULUM = [
    {"user": "你好", "kind": "dialogue"},
    {"user": "我叫小狸同学", "kind": "fact"},
    {"user": "我喜欢蓝色、猫和星空", "kind": "fact"},
    {"user": "我讨厌香菜", "kind": "fact"},
    {"user": "北京是中国的首都", "kind": "fact"},
    {"user": "上海是一个大城市", "kind": "fact"},
    {"user": "猫是哺乳动物", "kind": "fact"},
    {"user": "地球是太阳系第三颗行星", "kind": "fact"},
    {"user": "什么是意识？", "kind": "dialogue"},
    {"user": "解释一下全局工作空间", "kind": "dialogue"},
    {"user": "解释一下预测编码", "kind": "dialogue"},
    {"user": "你现在感觉怎么样？", "kind": "dialogue"},
    {"user": "状态报告", "kind": "dialogue"},
    {"user": "其实关键是我觉得周末去河边更好", "kind": "stance"},
    {"user": "如果身体能量很低会怎样？", "kind": "counterfactual"},
    {"user": "想想", "kind": "think"},
    {"user": "你喜欢什么？", "kind": "dialogue"},
    {"user": "谢谢", "kind": "dialogue"},
    {"user": "再见", "kind": "dialogue"},
]


@dataclass
class TrainReport:
    turns: int = 0
    facts_learned: int = 0
    sleeps: int = 0
    development: float = 0.0
    stage: str = ""
    elapsed: float = 0.0
    samples: List[Dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "turns": self.turns,
            "facts_learned": self.facts_learned,
            "sleeps": self.sleeps,
            "development": round(self.development, 2),
            "stage": self.stage,
            "elapsed_s": round(self.elapsed, 3),
            "samples": self.samples[-10:],
        }


def train_mind(mind: NousMind, items: Optional[Sequence[Dict[str, Any]]] = None,
               epochs: int = 1, sleep_every: int = 10) -> TrainReport:
    items = list(items if items is not None else DEFAULT_CURRICULUM)
    report = TrainReport()
    t0 = time.time()
    base_k = len(mind.runtime_knowledge)
    for _ in range(epochs):
        for i, item in enumerate(items):
            snap = mind.respond(item["user"])
            report.turns += 1
            if i in (0, len(items) - 1):
                report.samples.append({
                    "user": item["user"][:40],
                    "reply": snap["reply"][:80],
                    "intent": snap.get("intent"),
                })
            if sleep_every and (i + 1) % sleep_every == 0:
                mind.sleep()
                report.sleeps += 1
    mind.sleep()
    report.sleeps += 1
    report.facts_learned = len(mind.runtime_knowledge) - base_k
    report.development = mind.development
    report.stage = stage_for(mind.development).name
    report.elapsed = time.time() - t0
    return report


def save_report(report: TrainReport, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
