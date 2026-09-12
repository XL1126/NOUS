"""可选脉冲竞争底物：轻量胜者通路，不是完整 Izhikevich 仿真。

用途：把概念标签映射到群体，用侧抑制选出“当前胜者概念”，
再反馈给工作空间。保持纯 numpy、可关断。
"""
from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np


class SpikeRace:
    def __init__(self, n_pop: int = 64, seed: int = 0):
        self.n = n_pop
        self.rng = np.random.default_rng(seed)
        self.v = np.zeros(n_pop)
        self.labels: List[str] = ["" for _ in range(n_pop)]
        self.last_winners: List[Tuple[str, float]] = []

    def map_labels(self, labels: List[str]) -> Dict[str, int]:
        """稳定哈希把标签映射到群体下标。"""
        mapping = {}
        for i, lab in enumerate(labels[: self.n]):
            h = 0
            for ch in lab:
                h = (h * 131 + ord(ch)) % self.n
            mapping[lab] = h
            self.labels[h] = lab
        return mapping

    def compete(self, labels: List[str], drive: Dict[str, float], steps: int = 8) -> List[Tuple[str, float]]:
        mapping = self.map_labels(labels)
        I = np.zeros(self.n)
        for lab, idx in mapping.items():
            I[idx] += float(drive.get(lab, 0.4))
        v = self.v.copy()
        fired = np.zeros(self.n)
        for _ in range(steps):
            v = 0.8 * v + I + 0.05 * self.rng.standard_normal(self.n)
            # 侧抑制
            win = v.max()
            v = v * (v >= 0.7 * max(win, 1e-6))
            fired += (v > 0.55).astype(np.float64)
        rates = fired / steps
        ranked = []
        for lab, idx in mapping.items():
            ranked.append((lab, float(rates[idx])))
        ranked.sort(key=lambda x: -x[1])
        self.v = 0.3 * v
        self.last_winners = ranked[:5]
        return self.last_winners
