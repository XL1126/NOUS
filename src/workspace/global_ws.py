"""全局工作空间 — TRN 除法归一化 + S 型点火 + 再进入循环。

文献：
- Whyte et al. (2024) Neuron: TRN 除法归一化，core/matrix 双通路
- COGITATE 2025 Nature: 点火不是全或无，是渐进非线性
- Reynolds & Heeger (2009) Neuron: 除法归一化模型
- Lamme (2006) TiCS: 再进入循环
- Cowan (2001) BBS: 工作记忆容量 ~4 块
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class Broadcast:
    ignition: float = 0.0
    entropy: float = 0.0
    content: Dict[str, float] = field(default_factory=dict)
    labels: List[str] = field(default_factory=list)
    ignited: bool = False
    # S 型点火概率（COGITATE：渐进过渡）
    ignition_prob: float = 0.0
    # 现象意识代理（Lamme：局部循环稳定）
    stable_representation: List[str] = field(default_factory=list)


class GlobalWorkspace:
    """
    全局工作空间：
    1. TRN 除法归一化竞争（Whyte 2024）
    2. S 型点火（COGITATE 2025）
    3. 再进入循环（Lamme 2006）
    4. Cowan 4 块容量限制
    """

    def __init__(self, n_slots: int = 48, threshold: float = 0.28,
                 decay: float = 0.9, rng: Optional[np.random.Generator] = None):
        self.n_slots = n_slots
        self.threshold = threshold
        self.decay = decay
        self.rng = rng or np.random.default_rng(0)
        self.activity = np.zeros(n_slots)
        self.labels = [""] * n_slots
        self.last = Broadcast()
        self.history: List[Broadcast] = []
        # TRN 除法归一化参数
        self.sigma = 0.1  # 基线常数
        self.n_exp = 2    # 非线性指数
        self.gamma = 1.0  # 全局增益（调质）
        # S 型点火参数
        self.k_steep = 8.0  # 陡度
        # 再进入循环参数
        self.reentrant_iters = 3
        self.reentrant_eps = 0.05
        # Cowan 4 块
        self.max_figure = 4

    def offer(self, candidates: Dict[str, float]) -> None:
        self.activity *= 0.4
        ranked = sorted(candidates.items(), key=lambda kv: -kv[1])[: self.n_slots]
        for i, (lab, val) in enumerate(ranked):
            self.activity[i] = float(val)
            self.labels[i] = lab
        for j in range(len(ranked), self.n_slots):
            self.labels[j] = ""

    def _divisive_normalization(self, drive: np.ndarray, gain: float = 1.0) -> np.ndarray:
        """
        TRN 除法归一化（Whyte 2024 / Reynolds & Heeger 2009）：
        R_i = γ · D_i^n / (σ^n + Σ_k D_k^n)
        """
        D = np.clip(drive, 0, None)
        Dn = D ** self.n_exp
        pool = Dn.sum() + self.sigma ** self.n_exp
        R = gain * Dn / pool
        return R

    def _sigmoid_ignition(self, activation: float, gain: float = 1.0) -> float:
        """
        S 型点火函数（COGITATE 2025）：
        p = 1 / (1 + exp(-k·(activation - θ)))
        阈值 θ 受调质增益动态调整
        """
        theta = self.threshold / max(gain, 0.1)
        return float(1.0 / (1.0 + np.exp(-self.k_steep * (activation - theta))))

    def _reentrant_stabilize(self, labels: List[str], activations: np.ndarray) -> Tuple[List[str], np.ndarray]:
        """
        再进入循环（Lamme 2006）：
        高层向低层反馈，稳定表征，产生知觉恒常性。
        """
        if not labels:
            return labels, activations
        act = activations.copy()
        prev = act.copy()
        for _ in range(self.reentrant_iters):
            # 反馈：胜者增强，竞争者抑制（模拟高层→低层预测）
            max_a = act.max() if act.max() > 0 else 1.0
            # 胜者通吃 + 侧抑制
            act = act * (act >= 0.3 * max_a)
            # 再进入：胜者获得额外增益
            act = act * (1.0 + 0.2 * (act / max_a))
            # 收敛判定
            if np.abs(act - prev).max() < self.reentrant_eps:
                break
            prev = act.copy()
        return labels, act

    def step(self, global_gain: float = 1.0, fatigue: float = 1.0) -> Broadcast:
        # 矩阵通路：全局增益（matrix 代理）
        self.gamma = global_gain * fatigue
        act = np.clip(self.activity * self.gamma, 0.0, 5.0)

        # TRN 除法归一化竞争
        act = self._divisive_normalization(act, gain=self.gamma)

        # 熵
        total = float(act.sum()) + 1e-9
        p = act / total
        ent = float(-(p[p > 0] * np.log(p[p > 0])).sum())
        max_e = float(np.log(self.n_slots)) if self.n_slots > 1 else 1.0
        ent = ent / max_e if max_e > 0 else 0.0

        # 再进入循环稳定
        active_idx = np.where(act > 0.01)[0]
        if len(active_idx) > 0:
            active_labels = [self.labels[i] for i in active_idx]
            active_act = act[active_idx]
            stable_labels, stable_act = self._reentrant_stabilize(active_labels, active_act)
            act[active_idx] = stable_act

        # Cowan 4 块：figure 容量限制
        top_idx = np.argsort(-act)[: self.max_figure + 2]
        content: Dict[str, float] = {}
        labels: List[str] = []
        max_a = float(act.max()) if act.max() > 0 else 1.0
        for idx in top_idx:
            if self.labels[idx] and act[idx] > 0.1 * max_a:
                # S 型点火概率
                prob = self._sigmoid_ignition(float(act[idx]), gain=self.gamma)
                content[self.labels[idx]] = float(act[idx] / (max_a + 1e-9))
                if len(labels) < self.max_figure:
                    labels.append(self.labels[idx])

        # 整体点火强度 = 最大激活的 S 型概率
        w = int(np.argmax(act)) if act.size else -1
        wv = float(act[w]) if w >= 0 else 0.0
        ignition_prob = self._sigmoid_ignition(wv, gain=self.gamma)
        ignition = float(np.clip(0.5 * wv + 0.5 * ignition_prob, 0.0, 2.0))
        ignited = ignition_prob > 0.5

        # 现象意识代理：再进入循环稳定的表征（Lamme）
        stable_rep = [l for l in labels if content.get(l, 0) > 0.3]

        self.last = Broadcast(
            ignition=ignition,
            entropy=ent,
            content=content,
            labels=labels,
            ignited=ignited,
            ignition_prob=ignition_prob,
            stable_representation=stable_rep,
        )
        self.history.append(self.last)
        if len(self.history) > 80:
            self.history = self.history[-80:]
        self.activity *= self.decay
        return self.last

    def report(self) -> str:
        b = self.last
        tops = " → ".join(f"{k}({v:.2f})" for k, v in list(b.content.items())[:4])
        return f"点火{b.ignition:.2f}(p={b.ignition_prob:.2f}) 熵{b.entropy:.2f} 广播[{tops or '—'}]"
