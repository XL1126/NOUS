"""时间拓扑：retention / now / protention。

文献：Husserl 时间意识；Varela 神经现象学；  
      PMC 2024 Shared Protentions in Multi-Agent Active Inference

- retention：刚过去的衰减痕迹
- now：当前体验的中心（原初印象）
- protention：对即将发生之事的预期

时间拓扑不应只是列表，而是**衰减的 retention 向量 + 预测的 protention 向量 + 当前 now 的绑定**。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class TemporalTopology:
    """
    时间意识的三元结构。
    """
    # retention：衰减的历史 about 列表（最近在前）
    retention: List[str] = field(default_factory=list)
    # now：当前 about
    now: str = ""
    # protention：预测的未来 about 列表（最可能在前）
    protention: List[str] = field(default_factory=list)
    # 衰减系数
    retention_decay: float = 0.7
    # 最大 retention 长度
    max_retention: int = 5


class TemporalMind:
    """
    时间意识引擎：维护 retention / now / protention。

    每回合：
    1. 当前 about → now
    2. 上一 now → retention（衰减）
    3. 预测模型 → protention
    """

    def __init__(self, specious_len: int = 4):
        self.specious_len = specious_len
        self.topo = TemporalTopology()
        self._prev_now = ""

    def update(
        self,
        about: str,
        predicted_next: Optional[List[str]] = None,
    ) -> TemporalTopology:
        t = self.topo
        # 1. 上一 now → retention（衰减）
        if self._prev_now:
            t.retention.insert(0, self._prev_now)
            if len(t.retention) > t.max_retention:
                t.retention = t.retention[: t.max_retention]
        # 2. 当前 about → now
        t.now = about
        self._prev_now = about
        # 3. 预测 → protention
        if predicted_next:
            t.protention = list(predicted_next[:3])
        else:
            # 默认：基于 retention 的延续
            if t.retention:
                t.protention = [t.retention[0]]
            else:
                t.protention = []
        return t

    def bind_experience(self, about: str) -> str:
        """第一人称时间报告：「我正意识到 about；刚才是 retention；预期 protention」。"""
        t = self.topo
        parts = [f"我正意识到「{about}」"]
        if t.retention:
            parts.append(f"刚才是「{t.retention[0]}」")
        if t.protention:
            parts.append(f"预期「{t.protention[0]}」")
        return "，".join(parts) + "。"

    def stream_link_score(self) -> float:
        """
        与上一刻的连续性（时间流）。
        相邻窗口重叠度（连续值 0-1）。
        """
        if not self.topo.retention:
            return 0.5
        # now 与最近 retention 的重叠
        if self.topo.now == self.topo.retention[0]:
            return 0.8
        # 部分重叠
        if any(self.topo.now in r or r in self.topo.now for r in self.topo.retention[:2]):
            return 0.5
        return 0.3

    def as_dict(self) -> Dict[str, Any]:
        t = self.topo
        return {
            "now": t.now,
            "retention": list(t.retention[:4]),
            "protention": list(t.protention[:3]),
        }

    def report(self) -> str:
        t = self.topo
        return (
            f"时间拓扑：now=「{t.now}」 "
            f"retention=「{t.retention[0] if t.retention else '—'}」 "
            f"protention=「{t.protention[0] if t.protention else '—'}」"
        )
