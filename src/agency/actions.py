"""主动行动闭环：冲动 → 真正执行 → 改变身体/目标/输出策略。

文献：active inference (Friston)；Miller & Cohen 目标控制；Damasio 躯体标记。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class ActionResult:
    action: str
    executed: bool
    effects: Dict[str, float] = field(default_factory=dict)
    narrative: str = ""


class ActionLoop:
    """把 Autopoiesis 的冲动变成真实副作用。"""

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.history: List[str] = []
        self.last: Optional[ActionResult] = None

    def execute(self, action: str, soma, goals) -> ActionResult:
        effects: Dict[str, float] = {}
        narrative = ""
        executed = True
        s = soma.state

        if action == "rest":
            soma.event("rest", 0.35)
            effects["energy"] = 0.12
            effects["sleep"] = -0.15
            goals.retarget_from_need("rest")
            narrative = "我主动压低输出并把目标切到恢复。"

        elif action == "seek_energy":
            # 「进食」= 提高葡萄糖/能量，降低 feed 冲动
            s.glucose = float(np.clip(s.glucose + 0.15, 0, 1))
            s.energy = float(np.clip(s.energy + 0.08, 0, 1))
            effects["glucose"] = 0.15
            narrative = "我执行了能量补给策略（内部代谢调节）。"

        elif action == "seek_bond":
            soma.event("social", 0.3)
            from ..self_model.meta import Goal
            goals.push(Goal("维持与对方的社会联结", priority=0.7, source="social"))
            narrative = "我提高社交驱动，并压入联结目标。"

        elif action == "explore":
            soma.event("novelty", 0.25)
            from ..self_model.meta import Goal
            goals.push(Goal("探索新概念/填补知识空白", priority=0.75, source="intrinsic"))
            narrative = "我启动探索：抬高好奇与乙酰胆碱相关增益。"

        elif action == "protect":
            soma.event("threat", 0.15)  # 保持警觉，不盲目放松
            s.stress = float(np.clip(s.stress - 0.05, 0, 1))  # 但可控
            from ..self_model.meta import Goal
            goals.push(Goal("确认边界与安全", priority=0.85, source="intrinsic"))
            narrative = "我进入保护策略：收紧边界，优先安全目标。"

        elif action == "self_repair":
            s.stress = float(np.clip(s.stress - 0.12, 0, 1))
            s.serotonin = float(np.clip(s.serotonin + 0.08, 0, 1))
            narrative = "我做自我修复：降压、抬高血清素相关项，并重读自传。"

        else:
            executed = False
            narrative = "维持当前稳态，无需额外动作。"

        self.last = ActionResult(action, executed, effects, narrative)
        self.history.append(action)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        return self.last

    def output_style_bias(self) -> Dict[str, float]:
        """行动对语言输出的偏置。"""
        if not self.last or not self.last.executed:
            return {"length": 1.0, "hedge": 0.0, "warmth": 0.0}
        a = self.last.action
        if a == "rest":
            return {"length": 0.55, "hedge": 0.2, "warmth": 0.1}
        if a == "protect":
            return {"length": 0.7, "hedge": 0.45, "warmth": 0.0}
        if a == "explore":
            return {"length": 1.15, "hedge": 0.1, "warmth": 0.15}
        if a == "seek_bond":
            return {"length": 1.0, "hedge": 0.05, "warmth": 0.5}
        if a == "self_repair":
            return {"length": 0.8, "hedge": 0.25, "warmth": 0.2}
        return {"length": 1.0, "hedge": 0.0, "warmth": 0.1}
