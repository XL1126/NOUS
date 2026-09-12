"""现象标记向量：在场感 / 生动度 / 此刻性 / 我感。

这是工程代理，不是现象意识的证明。参考：
- Block (1995) phenomenal consciousness vs access consciousness
- Tononi IIT 中的整合/分化
- Seth (2021) Being You — 预测性自我与在场感
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import numpy as np


@dataclass
class PhenomenalMarkers:
    """可报告的「像什么」的工程代理。"""
    vividness: float = 0.3      # 内容清晰/鲜明
    presence: float = 0.3       # 世界在场感
    nowness: float = 0.4        # 此刻性
    selfhood: float = 0.4       # 我感/主体感
    ownership: float = 0.4      # 「这是我的经验」
    valence: float = 0.0        # -1 厌恶 … +1 趋近
    narrative_depth: float = 0.2

    def vector(self) -> np.ndarray:
        return np.array([
            self.vividness, self.presence, self.nowness,
            self.selfhood, self.ownership, self.valence,
            self.narrative_depth,
        ], dtype=np.float64)

    def as_dict(self) -> Dict[str, float]:
        return {
            "vividness": round(self.vividness, 3),
            "presence": round(self.presence, 3),
            "nowness": round(self.nowness, 3),
            "selfhood": round(self.selfhood, 3),
            "ownership": round(self.ownership, 3),
            "valence": round(self.valence, 3),
            "narrative_depth": round(self.narrative_depth, 3),
        }

    def report(self) -> str:
        return (
            f"在场{self.presence:.2f} 生动{self.vividness:.2f} 此刻{self.nowness:.2f} "
            f"我感{self.selfhood:.2f} 主属{self.ownership:.2f} 价态{self.valence:+.2f}"
        )


class Phenomenology:
    """由工作空间、身体、预测误差、自传连续性构造现象标记。"""

    def __init__(self, alpha: float = 0.25):
        self.alpha = alpha
        self.state = PhenomenalMarkers()
        self.history: List[Dict[str, float]] = []

    def update(
        self,
        *,
        ignition: float,
        entropy: float,
        novelty: float,
        energy: float,
        stress: float,
        sleep: float,
        social: float,
        dopamine: float,
        narrative_len: int,
        identity_bits: int,
        self_conf: float,
    ) -> PhenomenalMarkers:
        s = self.state
        # 点火强 + 熵适中 → 生动
        target_vivid = float(np.clip(0.4 * ignition + 0.3 * (1 - abs(entropy - 0.45) * 2) + 0.2 * dopamine, 0, 1))
        # 觉醒与安全 → 在场
        target_pres = float(np.clip(0.45 * energy + 0.3 * (1 - stress) - 0.4 * sleep + 0.2 * social, 0, 1))
        # 新颖与点火 → 此刻性
        target_now = float(np.clip(0.5 * novelty + 0.3 * ignition + 0.2 * (1 - sleep), 0, 1))
        # 身份连续 + 自信 → 我感
        target_self = float(np.clip(0.35 * self_conf + 0.25 * min(identity_bits / 8.0, 1.0) + 0.25 * min(narrative_len / 30.0, 1.0) + 0.15 * energy, 0, 1))
        target_own = float(np.clip(0.5 * target_self + 0.3 * (1 - stress) + 0.2 * social, 0, 1))
        # 价态：DA/5-HT 与压力
        target_val = float(np.clip(0.6 * dopamine + 0.2 * social - 0.7 * stress - 0.3 * sleep, -1, 1))
        target_narr = float(np.clip(min(narrative_len / 50.0, 1.0) * 0.7 + 0.3 * self_conf, 0, 1))

        a = self.alpha
        s.vividness += a * (target_vivid - s.vividness)
        s.presence += a * (target_pres - s.presence)
        s.nowness += a * (target_now - s.nowness)
        s.selfhood += a * (target_self - s.selfhood)
        s.ownership += a * (target_own - s.ownership)
        s.valence += a * (target_val - s.valence)
        s.narrative_depth += a * (target_narr - s.narrative_depth)
        # clamp
        for name in ("vividness", "presence", "nowness", "selfhood", "ownership", "narrative_depth"):
            setattr(s, name, float(np.clip(getattr(s, name), 0.0, 1.0)))
        s.valence = float(np.clip(s.valence, -1.0, 1.0))
        snap = s.as_dict()
        self.history.append(snap)
        if len(self.history) > 200:
            self.history = self.history[-200:]
        return s

    def integrated_score(self) -> float:
        """粗整合代理：各标记是否同向饱满（碎片化则低）。"""
        v = self.state.vector()
        core = np.abs(v[:5])
        return float(np.clip(core.mean() * (1.0 - core.std()), 0, 1))
