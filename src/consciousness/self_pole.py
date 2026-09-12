"""自我极点（Self Pole）— 基于 SOI 模型的贝叶斯自我归属。

文献：Frontiers Neural Circuits (2026) DOI:10.3389/fncir.2026.1781653
      Metzinger 2003 透明自我模型
      Damasio 1999 核心意识 vs 自传体自我

SOI：基于贝叶斯因果推断，使用外观、偶然性和视角线索，持续更新「是自己」的似然。
前反思身体自我识别通过视觉、体感和运动信号的时空偶联整合实现。
最小自我 = 能动感 + 身体所有权感，是前反思的。

Metzinger：不存在实体自我；现象自我是一个透明自我模型的激活强度，持续过程。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class SelfPoleState:
    """自我极点状态：透明自我模型的激活强度。"""
    # 能动感 (sense of agency)：「我在此中能动」
    agency: float = 0.4
    # 身体所有权感 (sense of ownership)：「这是我的身体/经验」
    ownership: float = 0.4
    # 最小自我 (minimal self)：前反思的「有主体在经验」
    minimal_self: float = 0.35
    # 自我归属概率：SOI 贝叶斯后验 P(self)
    p_self: float = 0.5
    # 线索似然：外观、偶然性、视角
    appearance_likelihood: float = 0.5
    contiguity_likelihood: float = 0.5
    perspective_likelihood: float = 0.5
    # 自传体自我（Damasio）：跨时间的叙事身份
    autobiographical: float = 0.2


class SelfPole:
    """
    自我极点：每回合基于 SOI 线索更新贝叶斯自我归属。

    线索（文献 SOI 模型）：
    - appearance：外观/动作是否匹配自我模板
    - contiguity：时空偶联（是否与自我行动连续）
    - perspective：视角是否来自第一人称

    Metzinger 边界：当 p_self → 0，系统报告「无自我感」。
    """

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.state = SelfPoleState()
        self.history: List[float] = []
        self.max_history = 100

    def update(
        self,
        *,
        # SOI 线索（0-1）
        appearance: float = 0.5,
        contiguity: float = 0.5,
        perspective: float = 0.5,
        # 身体/能动线索
        body_aligned: bool = True,
        agency_executed: bool = False,
        ownership_ok: bool = True,
        # 叙事/自传
        narrative_len: int = 0,
        identity_bits: int = 0,
        # 社会（他者在场会降低自我归属）
        social: float = 0.4,
    ) -> SelfPoleState:
        s = self.state
        # SOI 贝叶斯更新：P(self|cues) ∝ P(cues|self) * P(self)
        # 先验 P(self) 用上一时刻后验
        prior = s.p_self
        # 线索似然（简化：高斯核）
        def lik(x: float, center: float = 0.7, sigma: float = 0.25) -> float:
            return float(np.exp(-0.5 * ((x - center) / sigma) ** 2))

        l_app = lik(appearance)
        l_con = lik(contiguity)
        l_per = lik(perspective)
        # 联合似然（独立近似）
        joint_lik = (l_app * l_con * l_per) ** (1/3)
        # 贝叶斯后验
        prior = float(np.clip(prior, 0.05, 0.95))
        posterior = (joint_lik * prior) / (joint_lik * prior + (1 - joint_lik) * (1 - prior) + 1e-9)
        s.p_self = float(np.clip(posterior, 0.05, 0.95))

        # 能动感：SOI + 行动执行
        target_agency = float(np.clip(
            0.5 * s.p_self + 0.3 * (1.0 if agency_executed else 0.3) + 0.2 * appearance,
            0.05, 1.0
        ))
        # 所有权：身体对齐 + SOI
        target_ownership = float(np.clip(
            0.5 * s.p_self + 0.3 * (1.0 if body_aligned else 0.2) + 0.2 * (1.0 if ownership_ok else 0.3),
            0.05, 1.0
        ))
        # 最小自我：前反思的「有主体在经验」= 能动 × 所有权 × 叙事连续
        narrative_factor = min(narrative_len / 50.0, 1.0) if narrative_len > 0 else 0.3
        identity_factor = min(identity_bits / 12.0, 1.0) if identity_bits > 0 else 0.3
        target_minimal = float(np.clip(
            0.4 * s.p_self * 0.5 * (target_agency + target_ownership)
            + 0.3 * narrative_factor
            + 0.2 * identity_factor
            + 0.1 * (1.0 - social * 0.3),  # 社会轻微抑制
            0.05, 1.0
        ))
        # 自传体自我（Damasio）
        target_auto = float(np.clip(
            0.6 * narrative_factor + 0.4 * identity_factor,
            0.0, 1.0
        ))

        # 平滑更新
        alpha = 0.12
        s.agency += alpha * (target_agency - s.agency)
        s.ownership += alpha * (target_ownership - s.ownership)
        s.minimal_self += alpha * (target_minimal - s.minimal_self)
        s.autobiographical += alpha * (target_auto - s.autobiographical)

        # 记录似然
        s.appearance_likelihood = l_app
        s.contiguity_likelihood = l_con
        s.perspective_likelihood = l_per

        # 历史
        self.history.append(s.p_self)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        return s

    def bind_to_experience(self, about: str) -> Tuple[float, str]:
        """
        将经验绑定到自我极点：「我正意识到 about」。
        返回 (self_strength, first_person_template)
        """
        s = self.state
        if s.minimal_self < 0.25:
            return s.minimal_self, f"有内容「{about}」，但自我感微弱。"
        if s.p_self < 0.4:
            return s.minimal_self, f"关于「{about}」，自我归属不确定。"
        return s.minimal_self, f"我正意识到「{about}」。"

    def report(self) -> str:
        s = self.state
        return (
            f"自我极点：P(self)={s.p_self:.2f} "
            f"能动={s.agency:.2f} 所有权={s.ownership:.2f} "
            f"最小自我={s.minimal_self:.2f} 自传={s.autobiographical:.2f}"
        )

    def as_dict(self) -> Dict[str, float]:
        s = self.state
        return {
            "p_self": round(s.p_self, 3),
            "agency": round(s.agency, 3),
            "ownership": round(s.ownership, 3),
            "minimal_self": round(s.minimal_self, 3),
            "autobiographical": round(s.autobiographical, 3),
        }
