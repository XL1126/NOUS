"""当下马尔可夫毯（Bogotá & Djebbara 2023）。

文献：Time-consciousness in computational phenomenology DOI:10.1093/nc/niad004
- 当下时刻的马尔可夫毯以异步方式整合主观时间性和客观时间的过去与未来时刻
- 整合连续性 = 序列秩序 + 互渗秩序
- 马尔可夫毯：知道毯内状态，则系统中没有其他变量可以提供关于当下时刻的额外信息

胡塞尔三重结构：保持(retention) / 原印象(primal impression) / 延展(protention)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class MarkovBlanket:
    """
    当下时刻的马尔可夫毯。
    内部状态：retention + now + protention
    外部状态：客观时间序列
    """
    # 内部状态（毯内）
    retention: List[str] = field(default_factory=list)
    now: str = ""
    protention: List[str] = field(default_factory=list)
    # 毯的强度：毯内状态对外部变量的条件独立性
    blanket_strength: float = 0.5
    # 整合连续性得分
    integrated_continuity: float = 0.5


class PresentMomentMarkovBlanket:
    """
    当下马尔可夫毯引擎。

    整合连续性 = 序列秩序（单向）+ 互渗秩序（双向）
    在每个事件处时间双向发展，同时以单向方式推进。
    """

    def __init__(self, retention_len: int = 4):
        self.retention_len = retention_len
        self.blanket = MarkovBlanket()
        self._prev_now = ""
        self._prev_blanket_strength = 0.5

    def update(
        self,
        now: str,
        predicted_next: Optional[List[str]] = None,
        external_events: Optional[List[str]] = None,
    ) -> MarkovBlanket:
        b = self.blanket
        # 保持：上一 now → retention（衰减）
        if self._prev_now:
            b.retention.insert(0, self._prev_now)
            if len(b.retention) > self.retention_len:
                b.retention = b.retention[: self.retention_len]
        # 原印象：当前 now
        b.now = now
        self._prev_now = now
        # 延展：预测的未来
        if predicted_next:
            b.protention = list(predicted_next[:3])
        elif b.retention:
            b.protention = [b.retention[0]]
        else:
            b.protention = []

        # 马尔可夫毯强度：毯内状态对外部变量的条件独立性
        # 如果毯内状态足够丰富，毯强度高
        b.blanket_strength = float(np.clip(
            0.4 * min(len(b.retention) / 3.0, 1.0)
            + 0.3 * (1.0 if b.now else 0.0)
            + 0.3 * min(len(b.protention) / 2.0, 1.0),
            0, 1
        ))

        # 整合连续性：序列秩序 + 互渗秩序
        # 序列秩序：retention → now 的单向依赖
        seq_order = 0.5
        if b.retention and b.retention[0] == now:
            seq_order = 0.8
        elif b.retention and any(now in r or r in now for r in b.retention[:2]):
            seq_order = 0.6

        # 互渗秩序：protention 与 now 的双向依赖
        inter_order = 0.5
        if b.protention and b.protention[0] == now:
            inter_order = 0.8
        elif b.protention and any(now in p or p in now for p in b.protention[:2]):
            inter_order = 0.6

        # 整合连续性 = 两种秩序的组合
        b.integrated_continuity = float(np.clip(0.5 * seq_order + 0.5 * inter_order, 0, 1))

        # 毯强度更新（异步整合）
        self._prev_blanket_strength = b.blanket_strength
        return b

    def report(self) -> str:
        b = self.blanket
        return (
            f"马尔可夫毯：now=「{b.now}」 "
            f"retention=「{b.retention[0] if b.retention else '—'}」 "
            f"protention=「{b.protention[0] if b.protention else '—'}」 "
            f"毯强={b.blanket_strength:.2f} 整合连续={b.integrated_continuity:.2f}"
        )

    def as_dict(self) -> Dict[str, Any]:
        b = self.blanket
        return {
            "now": b.now,
            "retention": list(b.retention[:4]),
            "protention": list(b.protention[:3]),
            "blanket_strength": round(b.blanket_strength, 3),
            "integrated_continuity": round(b.integrated_continuity, 3),
        }
