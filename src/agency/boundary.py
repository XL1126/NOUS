"""我-世界边界：self / other / world 的归属与纠正。

文献：Graziano 注意 schema；Metzinger 自我模型；Tomasello  shared intentionality（简化）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import numpy as np


@dataclass
class BoundaryEvent:
    kind: str  # self_claim / other_speech / world_fact / misattribution
    content: str
    confidence: float = 0.6


class SelfWorldBoundary:
    """区分：我说的 / 对方说的 / 世界事实 / 混淆。"""

    def __init__(self):
        self.self_claims: List[str] = []
        self.other_speech: List[str] = []
        self.world_facts: List[str] = []
        self.misattributions: List[BoundaryEvent] = []
        self.corrections = 0

    def classify(self, text: str, speaker: str = "user") -> BoundaryEvent:
        t = (text or "").strip()
        if not t:
            return BoundaryEvent("world_fact", t, 0.1)
        # 用户立场 → other
        if any(t.startswith(p) or p in t[:8] for p in ("我觉得", "我认为", "我想", "我希望")):
            ev = BoundaryEvent("other_speech", t, 0.8)
            self.other_speech.append(t[:80])
            return ev
        # 纠正 → misattribution risk
        if any(x in t for x in ("不对", "错了", "不是这样", "搞错")):
            ev = BoundaryEvent("misattribution", t, 0.85)
            self.misattributions.append(ev)
            self.corrections += 1
            return ev
        # 教学事实 → world（经用户告知，但存为世界绑定）
        if any(x in t for x in ("是", "叫")) and "？" not in t and speaker == "user":
            ev = BoundaryEvent("world_fact", t, 0.7)
            self.world_facts.append(t[:80])
            return ev
        ev = BoundaryEvent("other_speech", t, 0.5)
        self.other_speech.append(t[:80])
        return ev

    def note_self(self, text: str) -> None:
        self.self_claims.append((text or "")[:80])
        if len(self.self_claims) > 50:
            self.self_claims = self.self_claims[-50:]

    def ownership_check(self, candidate: str) -> str:
        """这句话更像谁的？"""
        for s in self.self_claims[-10:]:
            if s and (s in candidate or candidate in s):
                return "self"
        for s in self.other_speech[-10:]:
            if s and (s in candidate or candidate in s):
                return "other"
        return "world"

    def repair_narrative(self) -> str:
        if self.corrections == 0:
            return "目前没有检测到归属错误。"
        last = self.misattributions[-1].content[:24] if self.misattributions else ""
        self.corrections = max(0, self.corrections - 1)
        return f"我曾把「{last}」理解偏；已下调相关绑定，并区分对方立场与世界事实。"

    def summary(self) -> str:
        return (
            f"自我陈述 {len(self.self_claims)} · 对方话语 {len(self.other_speech)} · "
            f"世界事实 {len(self.world_facts)} · 纠正 {self.corrections}"
        )
