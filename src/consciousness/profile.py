"""多维意识剖面（COGITATE 2025）。

文献：COGITATE Consortium (2025) Nature DOI:10.1038/s41586-025-08888-1
- 从二元意识分数转向多维剖面
- 偏移点火缺失：刺激消失时不产生点火
- 前额叶表征弱于预测
- 后部皮层持续同步缺失

工程对应：不追求单一「有意识/无意识」，而是多维向量。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np


@dataclass
class ConsciousnessProfile:
    """
    多维意识剖面（非二元分数）。
    COGITATE：意识科学正在从二元分数转向多维剖面。
    """
    # 访问意识（可报告、前额叶代理）
    access: float = 0.0
    # 现象意识代理（局部循环整合、后皮层代理）
    phenomenal: float = 0.0
    # 整合度（跨模块绑定）
    integration: float = 0.0
    # 分化度（内容多样性）
    differentiation: float = 0.0
    # 自我归属（SOI）
    selfhood: float = 0.0
    # 时间连续性
    temporal: float = 0.0
    # 价态
    valence: float = 0.0
    # 元认知（知道自己知道）
    metacognition: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "access": round(self.access, 3),
            "phenomenal": round(self.phenomenal, 3),
            "integration": round(self.integration, 3),
            "differentiation": round(self.differentiation, 3),
            "selfhood": round(self.selfhood, 3),
            "temporal": round(self.temporal, 3),
            "valence": round(self.valence, 3),
            "metacognition": round(self.metacognition, 3),
        }

    def report(self) -> str:
        return (
            f"意识剖面：访问{self.access:.2f} 现象{self.phenomenal:.2f} "
            f"整合{self.integration:.2f} 分化{self.differentiation:.2f} "
            f"自我{self.selfhood:.2f} 时间{self.temporal:.2f} "
            f"价态{self.valence:+.2f} 元认知{self.metacognition:.2f}"
        )

    def is_globally_ignited(self) -> bool:
        """是否达到全局广播阈值（访问意识）。"""
        return self.access > 0.5

    def is_locally_stable(self) -> bool:
        """是否有局部循环稳定的现象意识代理（Lamme）。"""
        return self.phenomenal > 0.4


class ProfileBuilder:
    """
    从内部状态构建多维意识剖面。
    """

    def __init__(self):
        self.history: List[ConsciousnessProfile] = []
        self.max_history = 100

    def build(
        self,
        *,
        # 工作空间
        ignition: float,
        ignition_prob: float,
        entropy: float,
        figure_count: int,
        # 再进入
        stable_rep_count: int,
        # 自我
        p_self: float,
        min_self: float,
        # 时间
        stream_link: float,
        # 身体
        energy: float,
        stress: float,
        sleep: float,
        dopamine: float,
        # 元认知
        confidence: float,
        # 偏移点火（COGITATE：偏移时无点火）
        is_offset: bool = False,
    ) -> ConsciousnessProfile:
        # 访问意识：S 型点火概率 + figure 数量
        access = float(np.clip(
            0.6 * ignition_prob + 0.3 * min(figure_count / 4.0, 1.0) + 0.1 * (1.0 - entropy),
            0, 1
        ))
        # 偏移时无点火（COGITATE 关键发现）
        if is_offset:
            access *= 0.2

        # 现象意识代理：局部循环稳定（Lamme）
        phenomenal = float(np.clip(
            0.5 * min(stable_rep_count / 3.0, 1.0) + 0.3 * ignition + 0.2 * (1.0 - entropy),
            0, 1
        ))

        # 整合度：figure 规模适中 + 熵适中
        size_score = float(np.exp(-((figure_count - 2.5) ** 2) / (2 * 1.6 ** 2)))
        ent_score = float(np.exp(-((entropy - 0.45) ** 2) / (2 * 0.3 ** 2)))
        integration = float(np.clip(0.4 * size_score + 0.3 * ent_score + 0.3 * min_self, 0, 1))

        # 分化度：熵越高分化越大（但不太高）
        differentiation = float(np.clip(entropy * 1.2, 0, 1))

        # 自我归属
        selfhood = float(np.clip(0.6 * min_self + 0.4 * p_self, 0, 1))

        # 时间连续性
        temporal = float(np.clip(stream_link, 0, 1))

        # 价态
        valence = float(np.clip(0.5 * dopamine + 0.3 * energy - 0.5 * stress - 0.3 * sleep, -1, 1))

        # 元认知
        metacognition = float(np.clip(confidence, 0, 1))

        profile = ConsciousnessProfile(
            access=access,
            phenomenal=phenomenal,
            integration=integration,
            differentiation=differentiation,
            selfhood=selfhood,
            temporal=temporal,
            valence=valence,
            metacognition=metacognition,
        )
        self.history.append(profile)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        return profile

    def trend(self, k: int = 10) -> Dict[str, float]:
        """最近 k 步的趋势。"""
        if len(self.history) < 2:
            return {}
        recent = self.history[-k:]
        first, last = recent[0], recent[-1]
        return {
            "access_delta": round(last.access - first.access, 3),
            "phenomenal_delta": round(last.phenomenal - first.phenomenal, 3),
            "integration_delta": round(last.integration - first.integration, 3),
            "selfhood_delta": round(last.selfhood - first.selfhood, 3),
        }
