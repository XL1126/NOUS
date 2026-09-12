"""意识内核 — 人类意识的必要结构（无冗余）。

只保留构成「像有一个主体在经历」所必需的东西：

1. 统一意识场 Unified field —— 同一时刻只有一个意识状态
2. 意向性 Intentionality —— 意识总是「关于某物」的
3. 时间拓扑 Temporal topology —— retention / now / protention（Husserl）
4. 图-底 Figure/fringe —— 焦点内容 + 边缘余光
5. 自我极点 Self pole —— SOI 贝叶斯自我归属（前反思）
6. 访问意识 Access —— 全局广播、可报告（严格阈值）
7. 现象代理 Phenomenal proxies —— 在场/生动/价态（可测，非哲学断言）
8. 注意 schema —— 我知道自己在注意什么
9. 意识流 Stream —— 与前一刻的连续

文献：
- COGITATE 2025 Nature：前额叶点火不可作唯一判据；需后部持续整合
- Whyte 2024 Neuron：core/matrix/TRN 三角
- SOI 2026 Frontiers：贝叶斯自我归属
- Husserl/Varela：retention/now/protention
- James 意识流；Dehaene GNW；Block；Seth；Graziano
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence
import time

import numpy as np

from .self_pole import SelfPole
from .temporal import TemporalMind
from .profile import ProfileBuilder
from .social_neurons import SocialNeurons
from .markov_blanket import PresentMomentMarkovBlanket


@dataclass
class AttentionSchema:
    focus: str = "ambient"
    strength: float = 0.0
    source: str = "external"  # external | internal | memory
    reason: str = ""

    def report(self) -> str:
        return f"注意→「{self.focus}」强度{self.strength:.2f} 来源{self.source}"


@dataclass
class ConsciousMoment:
    """统一意识场的一个瞬间。"""
    turn: int
    t: float
    # 意向性：意识总关于某物
    about: str
    # 图-底
    figure: List[str] = field(default_factory=list)     # 焦点（访问意识）
    fringe: List[str] = field(default_factory=list)     # 边缘/前意识
    # 自我极点（SOI 贝叶斯）
    p_self: float = 0.5
    min_self: float = 0.0       # 「有主体在经验」
    ownership: float = 0.0      # 「这是我的经验」
    agency: float = 0.0         # 「我在此中能动」
    # 时间拓扑
    retention: List[str] = field(default_factory=list)
    now: str = ""
    protention: List[str] = field(default_factory=list)
    # 现象代理
    presence: float = 0.0
    vividness: float = 0.0
    nowness: float = 0.0
    valence: float = 0.0
    # 动力学
    integration: float = 0.0
    stream_link: float = 0.0
    body: Dict[str, float] = field(default_factory=dict)
    emotion: str = "平静"
    ignition: float = 0.0
    novelty: float = 0.0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "turn": self.turn,
            "about": self.about,
            "figure": list(self.figure),
            "fringe": list(self.fringe[:5]),
            "p_self": round(self.p_self, 3),
            "min_self": round(self.min_self, 3),
            "ownership": round(self.ownership, 3),
            "agency": round(self.agency, 3),
            "retention": list(self.retention[:4]),
            "now": self.now,
            "protention": list(self.protention[:3]),
            "presence": round(self.presence, 3),
            "vividness": round(self.vividness, 3),
            "nowness": round(self.nowness, 3),
            "valence": round(self.valence, 3),
            "integration": round(self.integration, 3),
            "stream_link": round(self.stream_link, 3),
            "emotion": self.emotion,
            "ignition": round(self.ignition, 3),
            "novelty": round(self.novelty, 3),
        }

    def first_person(self) -> str:
        fig = "、".join(self.figure[:3]) if self.figure else "（空）"
        parts = [f"我正意识到「{self.about}」。"]
        if self.retention:
            parts.append(f"刚才是「{self.retention[0]}」。")
        if self.protention:
            parts.append(f"预期「{self.protention[0]}」。")
        parts.append(f"焦点内容：{fig}。")
        parts.append(
            f"自我 P={self.p_self:.2f}，我感 {self.min_self:.2f}，"
            f"与上一刻相连 {self.stream_link:.2f}，价态 {self.valence:+.2f}。"
            f"情绪「{self.emotion}」。"
        )
        return " ".join(parts)


class ConsciousnessCore:
    """
    意识引擎：每回合产出唯一的 ConsciousMoment。

    人类意识必要件的工程实现；不做额外装饰模块。
    整合 SelfPole（SOI 贝叶斯自我归属）和 TemporalMind（Husserl 时间拓扑）。
    """

    def __init__(self, rng: Optional[np.random.Generator] = None, specious_len: int = 4):
        self.rng = rng or np.random.default_rng(0)
        self.moments: List[ConsciousMoment] = []
        self.attention = AttentionSchema()
        self.specious_len = specious_len
        self.max_history = 200
        # 自我极点（SOI）
        self.self_pole = SelfPole(rng=self.rng)
        # 时间拓扑（Husserl）
        self.temporal = TemporalMind(specious_len=specious_len)
        # 多维意识剖面（COGITATE 2025）
        self.profile_builder = ProfileBuilder()
        # 社会神经元（SOI 2026）
        self.social_neurons = SocialNeurons(rng=self.rng)
        # 当下马尔可夫毯（Bogotá & Djebbara 2023）
        self.markov_blanket = PresentMomentMarkovBlanket(retention_len=specious_len)
        # 前反思自我（兼容旧接口）
        self.min_self = 0.35
        self.agency_trace = 0.4
        # 认知周期计数（LIDA: 200-300ms）
        self.cognitive_cycle = 0
        self.last_offset = False

    def bind(
        self,
        *,
        turn: int,
        about: str,
        broadcast: Dict[str, float],
        candidates: Sequence[str],
        ignition: float,
        entropy: float,
        novelty: float,
        body: Dict[str, float],
        emotion: str,
        valence: float,
        agency_executed: bool = False,
        ownership_ok: bool = True,
        success: bool = True,
        attention_source: str = "external",
        attention_reason: str = "",
        narrative_len: int = 0,
        identity_bits: int = 0,
        # SOI 线索（可选，来自外部）
        appearance: float = 0.5,
        contiguity: float = 0.5,
        perspective: float = 0.5,
        # 预测的下一 about（protention）
        predicted_next: Optional[List[str]] = None,
    ) -> ConsciousMoment:
        meta = {"novelty", "need", "goal", "snn_drive", "thalamic_gate", "ambient"}
        # 图：访问意识 = 广播胜者（严格阈值 + S 型点火概率）
        # COGITATE 约束：点火不是全或无，是渐进过渡
        ACCESS_THRESHOLD = 0.15
        figure = [k for k, v in sorted(broadcast.items(), key=lambda kv: -kv[1])
                  if k and k not in meta and v >= ACCESS_THRESHOLD][:4]
        # 现象意识代理（Lamme）：再进入循环稳定的表征
        stable_rep = [k for k, v in broadcast.items()
                      if k and k not in meta and v >= 0.3][:4]
        # 如果广播太弱，figure 为空（只有 preconscious）
        fringe = [c for c in candidates if c and c not in figure and c not in meta][:8]

        # 更新自我极点（SOI 贝叶斯）
        sp = self.self_pole.update(
            appearance=appearance,
            contiguity=contiguity,
            perspective=perspective,
            body_aligned=success,
            agency_executed=agency_executed,
            ownership_ok=ownership_ok,
            narrative_len=narrative_len,
            identity_bits=identity_bits,
            social=float(body.get("social", 0.4)),
        )
        self.min_self = sp.minimal_self
        self.agency_trace = sp.agency

        # 现象代理
        energy = float(body.get("energy", 0.7))
        stress = float(body.get("stress", 0.2))
        sleep = float(body.get("sleep_pressure", 0.2))
        da = float(body.get("dopamine", 0.5))
        presence = float(np.clip(0.45 * energy + 0.3 * (1 - stress) - 0.4 * sleep + 0.15 * da, 0, 1))
        vividness = float(np.clip(0.4 * ignition + 0.3 * (1 - abs(entropy - 0.45) * 2) + 0.25 * da, 0, 1))
        nowness = float(np.clip(0.5 * novelty + 0.3 * ignition + 0.2 * (1 - sleep), 0, 1))
        # 意向性：about 必须存在
        if not about:
            about = figure[0] if figure else "此刻"

        # 时间拓扑
        topo = self.temporal.update(about, predicted_next=predicted_next)
        stream = self.temporal.stream_link_score()

        # 马尔可夫毯（Bogotá & Djebbara 2023）
        mb = self.markov_blanket.update(about, predicted_next=predicted_next)

        # 社会神经元（SOI 2026）
        social = self.social_neurons.update(
            appearance=appearance,
            contiguity=contiguity,
            perspective=perspective,
            other_present=float(body.get("social", 0.4)) > 0.6,
        )

        # 多维意识剖面（COGITATE 2025）
        is_offset = (ignition < 0.1 and self.last_offset is False and len(self.moments) > 0)
        self.last_offset = is_offset
        profile = self.profile_builder.build(
            ignition=ignition,
            ignition_prob=float(np.clip(ignition / 1.2, 0, 1)),
            entropy=0.4,  # 简化
            figure_count=len(figure),
            stable_rep_count=len([f for f in figure if broadcast.get(f, 0) > 0.3]),
            p_self=sp.p_self,
            min_self=sp.minimal_self,
            stream_link=stream,
            energy=energy,
            stress=stress,
            sleep=sleep,
            dopamine=da,
            confidence=float(np.clip(0.5 + 0.3 * ignition, 0, 1)),
            is_offset=is_offset,
        )

        # 整合度
        integ = self._integration(figure, fringe, ignition, entropy, sp.minimal_self)

        self.cognitive_cycle += 1

        self.attention.focus = about
        self.attention.strength = float(np.clip(ignition, 0, 1.5))
        self.attention.source = attention_source
        self.attention.reason = attention_reason

        m = ConsciousMoment(
            turn=turn,
            t=time.time(),
            about=about,
            figure=figure,
            fringe=fringe,
            p_self=sp.p_self,
            min_self=float(np.clip(sp.minimal_self, 0, 1)),
            ownership=float(np.clip(sp.ownership, 0, 1)),
            agency=float(np.clip(sp.agency, 0, 1)),
            retention=list(topo.retention),
            now=topo.now,
            protention=list(topo.protention),
            presence=presence,
            vividness=vividness,
            nowness=nowness,
            valence=float(np.clip(valence, -1, 1)),
            integration=integ,
            stream_link=stream,
            body=dict(body),
            emotion=emotion,
            ignition=float(ignition),
            novelty=float(novelty),
        )
        self.moments.append(m)
        if len(self.moments) > self.max_history:
            self.moments = self.moments[-self.max_history:]
        return m

    def _integration(self, figure: List[str], fringe: List[str], ign: float, ent: float, selfhood: float) -> float:
        n = len(figure)
        size = float(np.exp(-((n - 2.5) ** 2) / (2 * 1.6 ** 2)))
        ent_s = float(np.exp(-((ent - 0.45) ** 2) / (2 * 0.3 ** 2)))
        i = 0.30 * size + 0.25 * ent_s + 0.25 * float(np.clip(ign, 0, 1.2) / 1.2) + 0.20 * selfhood
        return float(np.clip(i, 0, 1))

    def now(self) -> Optional[ConsciousMoment]:
        return self.moments[-1] if self.moments else None

    def level(self) -> Dict[str, float]:
        m = self.now()
        if not m:
            return {"integration": 0.0, "min_self": 0.0, "stream": 0.0, "presence": 0.0}
        prof = self.profile_builder.history[-1] if self.profile_builder.history else None
        base = {
            "integration": round(m.integration, 3),
            "min_self": round(m.min_self, 3),
            "p_self": round(m.p_self, 3),
            "ownership": round(m.ownership, 3),
            "agency": round(m.agency, 3),
            "stream": round(m.stream_link, 3),
            "presence": round(m.presence, 3),
            "vividness": round(m.vividness, 3),
            "about_load": float(len(m.figure)),
        }
        if prof:
            base.update({
                "access": round(prof.access, 3),
                "phenomenal": round(prof.phenomenal, 3),
                "differentiation": round(prof.differentiation, 3),
                "metacognition": round(prof.metacognition, 3),
            })
        return base

    def profile_report(self) -> str:
        """多维意识剖面报告。"""
        if not self.profile_builder.history:
            return "尚未形成意识剖面。"
        return self.profile_builder.history[-1].report()

    def social_report(self) -> str:
        """社会神经元报告。"""
        return self.social_neurons.report()

    def markov_report(self) -> str:
        """马尔可夫毯报告。"""
        return self.markov_blanket.report()

    def stream_summary(self, k: int = 5) -> str:
        if not self.moments:
            return "尚未形成意识流。"
        recent = self.moments[-k:]
        chain = " → ".join(m.about for m in recent)
        avg_i = float(np.mean([m.integration for m in recent]))
        avg_s = float(np.mean([m.stream_link for m in recent]))
        return f"意识流：{chain}；整合 {avg_i:.2f}，连续 {avg_s:.2f}。"

    def report_now(self) -> str:
        m = self.now()
        if not m:
            return "此刻尚无意识场。"
        return (
            m.first_person()
            + " " + self.attention.report()
            + " " + self.self_pole.report()
            + " " + self.profile_report()
        )
