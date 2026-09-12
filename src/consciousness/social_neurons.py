"""自我/镜像/他者神经元（SOI 2026）。

文献：Oka & Isoda (2026) Front Neural Circuits DOI:10.3389/fncir.2026.1781653
- 自我神经元：当 z 接近「自我」时增加发放
- 他人神经元：当 z 接近「他人」时增加发放
- 镜像神经元：当 z 接近「自我」或「他人」时都响应
- 混合选择性神经元：根据任务背景改变调谐曲线
- 无反应神经元

状态空间点过程（SSPP）模型：连接不可观察潜在状态与可观察神经尖峰数据。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np


@dataclass
class SocialNeuronState:
    """社会神经元群体状态。"""
    # 潜在状态 z：0=自我，1=他人
    z: float = 0.5
    # 自我神经元发放率
    self_rate: float = 0.5
    # 他人神经元发放率
    other_rate: float = 0.5
    # 镜像神经元发放率（对自我和他人都响应）
    mirror_rate: float = 0.5
    # 泄漏参数 λ：自我信念向他人模型的渗漏程度
    leakage: float = 0.1


class SocialNeurons:
    """
    社会神经元群体：自我/他人/镜像。
    基于 SOI 模型的贝叶斯更新。
    """

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.state = SocialNeuronState()
        self.history: List[float] = []

    def update(
        self,
        *,
        # SOI 线索
        appearance: float = 0.5,
        contiguity: float = 0.5,
        perspective: float = 0.5,
        # 他者在场
        other_present: bool = False,
        other_is_similar: bool = True,
        # 任务背景
        task_partner_is_self: bool = True,
    ) -> SocialNeuronState:
        s = self.state
        # 贝叶斯更新潜在状态 z
        # P(self|cues) = P(cues|self)·P(self) / P(cues)
        prior = 1.0 - s.z  # z 越大越「他人」，所以 P(self) = 1-z
        # 线索似然
        def lik(x: float, center: float = 0.7, sigma: float = 0.25) -> float:
            return float(np.exp(-0.5 * ((x - center) / sigma) ** 2))

        l_app = lik(appearance)
        l_con = lik(contiguity)
        l_per = lik(perspective)
        joint_lik = (l_app * l_con * l_per) ** (1/3)
        # 后验
        posterior_self = (joint_lik * prior) / (joint_lik * prior + (1 - joint_lik) * (1 - prior) + 1e-9)
        s.z = float(np.clip(1.0 - posterior_self, 0, 1))

        # 泄漏：他者在场时，自我信念向他人模型渗漏
        if other_present and other_is_similar:
            s.z = float(np.clip(s.z + s.leakage * 0.3, 0, 1))

        # 神经元发放率
        s.self_rate = float(np.clip(1.0 - s.z + 0.1 * self.rng.standard_normal(), 0, 1))
        s.other_rate = float(np.clip(s.z + 0.1 * self.rng.standard_normal(), 0, 1))
        # 镜像：对自我和他人都响应
        s.mirror_rate = float(np.clip(0.5 + 0.3 * (1.0 - abs(s.z - 0.5) * 2), 0, 1))

        self.history.append(s.z)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        return s

    def is_self_dominant(self) -> bool:
        return self.state.z < 0.4

    def is_other_dominant(self) -> bool:
        return self.state.z > 0.6

    def report(self) -> str:
        s = self.state
        return (
            f"社会神经元：z={s.z:.2f} "
            f"自我率={s.self_rate:.2f} 他人率={s.other_rate:.2f} "
            f"镜像率={s.mirror_rate:.2f} 泄漏={s.leakage:.2f}"
        )
