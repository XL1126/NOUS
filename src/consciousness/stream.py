"""连续意识流 + 睡眠-觉醒状态机。

文献：
- Whyte 2024: 意识状态（清醒/睡眠/麻醉）与意识内容是两个独立维度
- Buzsáki: 睡眠慢振荡、纺锤波、SWR
- LIDA: 认知周期 200-300ms
- James: 意识流是连续的，不是回合制的

核心思想：意识不是「用户说话时才存在」，而是**持续运行的过程**。
即使没有外部输入，意识流仍在继续（内言、梦、自发思维）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import time

import numpy as np


class ConsciousState(Enum):
    """意识状态（Whyte 2024：状态维度）。"""
    WAKE = "wake"           # 清醒：高增益、全局广播
    DROWSY = "drowsy"       # 困倦：增益下降、广播变稀
    NREM = "nrem"           # 慢波睡眠：局部循环、无全局广播
    REM = "rem"             # 快速眼动：梦、DMN 活跃
    ANESTHESIA = "anesthesia"  # 麻醉：连接断裂


@dataclass
class ConsciousCycle:
    """一个认知周期（LIDA: 200-300ms）。"""
    cycle_id: int
    t: float
    state: ConsciousState
    about: str
    ignition: float
    access_contents: List[str]
    stable_rep: List[str]
    body_energy: float
    body_sleep: float
    body_stress: float
    stream_link: float
    is_autonomous: bool  # 是否自主思维（无外部输入）

    def as_dict(self) -> Dict[str, Any]:
        return {
            "cycle": self.cycle_id,
            "state": self.state.value,
            "about": self.about,
            "ignition": round(self.ignition, 3),
            "access": list(self.access_contents),
            "stable": list(self.stable_rep),
            "energy": round(self.body_energy, 3),
            "sleep": round(self.body_sleep, 3),
            "stream": round(self.stream_link, 3),
            "autonomous": self.is_autonomous,
        }


class SleepWakeMachine:
    """
    睡眠-觉醒状态机。

    状态转移：
    WAKE → DROWSY（睡压升高）
    DROWSY → NREM（睡压 > 0.6）
    NREM → REM（周期性）
    REM → WAKE（能量恢复 或 外部输入）
    NREM → WAKE（外部输入 或 能量恢复）
    """

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.state = ConsciousState.WAKE
        self.cycles_in_state = 0
        self.nrem_rem_counter = 0
        self.history: List[ConsciousState] = []
        # 状态持续时间（周期数）
        self.min_cycles = {
            ConsciousState.WAKE: 5,
            ConsciousState.DROWSY: 3,
            ConsciousState.NREM: 8,
            ConsciousState.REM: 4,
            ConsciousState.ANESTHESIA: 10,
        }

    def step(
        self,
        sleep_pressure: float,
        energy: float,
        external_input: bool = False,
    ) -> ConsciousState:
        self.cycles_in_state += 1
        s = self.state

        # 外部输入强制唤醒
        if external_input and s in (ConsciousState.NREM, ConsciousState.REM, ConsciousState.DROWSY):
            if self.cycles_in_state >= 2:  # 最少 2 周期才能被唤醒
                self._transition(ConsciousState.WAKE)
                return self.state

        # 状态转移逻辑
        if s == ConsciousState.WAKE:
            if sleep_pressure > 0.5 and self.cycles_in_state >= self.min_cycles[s]:
                self._transition(ConsciousState.DROWSY)
        elif s == ConsciousState.DROWSY:
            if sleep_pressure > 0.6 and self.cycles_in_state >= self.min_cycles[s]:
                self._transition(ConsciousState.NREM)
            elif sleep_pressure < 0.3:
                self._transition(ConsciousState.WAKE)
        elif s == ConsciousState.NREM:
            self.nrem_rem_counter += 1
            # 周期性进入 REM（约每 8-12 个 NREM 周期）
            if self.nrem_rem_counter >= 8 and self.cycles_in_state >= self.min_cycles[s]:
                self._transition(ConsciousState.REM)
                self.nrem_rem_counter = 0
            elif energy > 0.7 and sleep_pressure < 0.3:
                self._transition(ConsciousState.WAKE)
        elif s == ConsciousState.REM:
            if self.cycles_in_state >= self.min_cycles[s]:
                self._transition(ConsciousState.NREM)
        elif s == ConsciousState.ANESTHESIA:
            if self.cycles_in_state >= self.min_cycles[s] and energy > 0.5:
                self._transition(ConsciousState.WAKE)

        return self.state

    def _transition(self, new_state: ConsciousState) -> None:
        if new_state != self.state:
            self.history.append(new_state)
            if len(self.history) > 100:
                self.history = self.history[-100:]
        self.state = new_state
        self.cycles_in_state = 0

    def is_conscious(self) -> bool:
        """是否有意识（清醒或 REM）。"""
        return self.state in (ConsciousState.WAKE, ConsciousState.REM)

    def has_global_broadcast(self) -> bool:
        """是否有全局广播（仅清醒）。"""
        return self.state == ConsciousState.WAKE

    def gain_multiplier(self) -> float:
        """状态对全局增益的乘数。"""
        return {
            ConsciousState.WAKE: 1.0,
            ConsciousState.DROWSY: 0.6,
            ConsciousState.NREM: 0.2,
            ConsciousState.REM: 0.5,
            ConsciousState.ANESTHESIA: 0.1,
        }.get(self.state, 1.0)

    def report(self) -> str:
        return f"意识状态：{self.state.value}（第{self.cycles_in_state}周期）"


class ConsciousnessStream:
    """
    连续意识流：不依赖用户输入，自主运行。

    每个认知周期（200-300ms 模拟）：
    1. 推进睡眠-觉醒状态机
    2. 根据状态决定是否有全局广播
    3. 清醒时：处理外部输入 或 自主思维
    4. NREM：局部循环、记忆巩固
    5. REM：梦、DMN 自发活动
    """

    def __init__(
        self,
        soma,
        workspace,
        core,
        dreams,
        inner_speech,
        rng: Optional[np.random.Generator] = None,
        cycle_duration: float = 0.25,  # 250ms 模拟
    ):
        self.soma = soma
        self.ws = workspace
        self.core = core
        self.dreams = dreams
        self.inner = inner_speech
        self.rng = rng or np.random.default_rng(0)
        self.cycle_duration = cycle_duration
        self.sleep_wake = SleepWakeMachine(rng=self.rng)
        self.cycles: List[ConsciousCycle] = []
        self.cycle_count = 0
        self.max_history = 200
        # 自主思维主题池
        self.autonomous_topics: List[str] = []
        self.last_autonomous_thought = ""

    def add_topic(self, topic: str) -> None:
        """添加可供自主思维的主题。"""
        if topic and topic not in self.autonomous_topics:
            self.autonomous_topics.append(topic)
            if len(self.autonomous_topics) > 20:
                self.autonomous_topics = self.autonomous_topics[-20:]

    def tick(
        self,
        external_input: Optional[str] = None,
        external_broadcast: Optional[Dict[str, float]] = None,
    ) -> ConsciousCycle:
        """
        推进一个认知周期。
        """
        self.cycle_count += 1
        self.soma.step(1.0)
        sp = self.soma.state.sleep_pressure
        energy = self.soma.state.energy

        # 睡眠-觉醒状态机
        state = self.sleep_wake.step(
            sleep_pressure=sp,
            energy=energy,
            external_input=external_input is not None,
        )
        gain_mult = self.sleep_wake.gain_multiplier()

        # 根据状态决定意识内容
        if state == ConsciousState.WAKE:
            cycle = self._wake_cycle(external_input, external_broadcast, gain_mult)
        elif state == ConsciousState.DROWSY:
            cycle = self._drowsy_cycle(external_input, gain_mult)
        elif state == ConsciousState.NREM:
            cycle = self._nrem_cycle(gain_mult)
        elif state == ConsciousState.REM:
            cycle = self._rem_cycle(gain_mult)
        else:  # ANESTHESIA
            cycle = self._anesthesia_cycle()

        self.cycles.append(cycle)
        if len(self.cycles) > self.max_history:
            self.cycles = self.cycles[-self.max_history:]
        return cycle

    def _wake_cycle(
        self,
        external_input: Optional[str],
        external_broadcast: Optional[Dict[str, float]],
        gain_mult: float,
    ) -> ConsciousCycle:
        """清醒周期：处理外部输入 或 自主思维。"""
        is_autonomous = external_input is None
        if external_input and external_broadcast:
            about = external_input[:20]
            broadcast = external_broadcast
        else:
            # 自主思维：从主题池选择，优先高新颖度
            about = self._autonomous_thought()
            broadcast = {about: 0.5 + 0.3 * float(self.rng.random())}

        # 推进工作空间
        energy = self.soma.state.energy
        self.ws.offer(broadcast)
        bc = self.ws.step(
            global_gain=self.soma.attention_gain() * gain_mult,
            fatigue=0.7 + 0.3 * energy,
        )

        # 绑定意识场
        moment = self.core.bind(
            turn=self.cycle_count,
            about=about,
            broadcast=dict(bc.content),
            candidates=list(bc.content.keys()),
            ignition=float(bc.ignition),
            entropy=float(bc.entropy),
            novelty=0.3 + 0.4 * float(self.rng.random()),  # 增加新颖度变化
            body=self.soma.state.snapshot(),
            emotion=self.soma.feeling_label(),
            valence=0.1 * (float(self.rng.random()) - 0.5),
            agency_executed=not is_autonomous,
            ownership_ok=True,
            success=True,
            attention_source="external" if external_input else "internal",
            narrative_len=len(self.core.moments),
            identity_bits=5,
            appearance=0.7 if external_input else 0.5,
            contiguity=0.7,
            perspective=0.8,
        )

        return ConsciousCycle(
            cycle_id=self.cycle_count,
            t=time.time(),
            state=ConsciousState.WAKE,
            about=about,
            ignition=float(bc.ignition),
            access_contents=list(bc.content.keys())[:4],
            stable_rep=list(bc.content.keys())[:3],
            body_energy=self.soma.state.energy,
            body_sleep=self.soma.state.sleep_pressure,
            body_stress=self.soma.state.stress,
            stream_link=moment.stream_link,
            is_autonomous=is_autonomous,
        )

    def _drowsy_cycle(
        self,
        external_input: Optional[str],
        gain_mult: float,
    ) -> ConsciousCycle:
        """困倦周期：增益下降、广播变稀。"""
        about = external_input[:20] if external_input else self._autonomous_thought()
        self.ws.offer({about: 0.4})
        bc = self.ws.step(
            global_gain=self.soma.attention_gain() * gain_mult,
            fatigue=0.5,
        )
        return ConsciousCycle(
            cycle_id=self.cycle_count,
            t=time.time(),
            state=ConsciousState.DROWSY,
            about=about,
            ignition=float(bc.ignition),
            access_contents=list(bc.content.keys())[:2],
            stable_rep=[],
            body_energy=self.soma.state.energy,
            body_sleep=self.soma.state.sleep_pressure,
            body_stress=self.soma.state.stress,
            stream_link=0.3,
            is_autonomous=external_input is None,
        )

    def _nrem_cycle(self, gain_mult: float) -> ConsciousCycle:
        """NREM 慢波睡眠：局部循环、无全局广播、记忆巩固。"""
        # 无全局广播，只有局部循环
        about = "（慢波）"
        # 触发 SWR 重放
        if self.dreams and self.dreams.tagged_memories:
            self.dreams.dream(
                topics=self.autonomous_topics[:2],
                identity_bits=["睡眠中"],
                recent_thoughts=[],
                stress=self.soma.state.stress,
            )
        return ConsciousCycle(
            cycle_id=self.cycle_count,
            t=time.time(),
            state=ConsciousState.NREM,
            about=about,
            ignition=0.05,
            access_contents=[],
            stable_rep=[],
            body_energy=self.soma.state.energy,
            body_sleep=self.soma.state.sleep_pressure,
            body_stress=self.soma.state.stress,
            stream_link=0.1,
            is_autonomous=True,
        )

    def _rem_cycle(self, gain_mult: float) -> ConsciousCycle:
        """REM 睡眠：梦、DMN 自发活动。"""
        about = self._dream_thought()
        # DMN 样自发活动
        if self.inner:
            thought = self.inner.maybe_think(
                external_drive=0.1,
                energy=self.soma.state.energy,
                sleep=self.soma.state.sleep_pressure,
                topic=about,
                need="rest",
            )
            if thought:
                self.last_autonomous_thought = thought
        return ConsciousCycle(
            cycle_id=self.cycle_count,
            t=time.time(),
            state=ConsciousState.REM,
            about=about,
            ignition=0.15,
            access_contents=[about] if about else [],
            stable_rep=[about] if about else [],
            body_energy=self.soma.state.energy,
            body_sleep=self.soma.state.sleep_pressure,
            body_stress=self.soma.state.stress,
            stream_link=0.2,
            is_autonomous=True,
        )

    def _anesthesia_cycle(self) -> ConsciousCycle:
        """麻醉：连接断裂、无意识。"""
        return ConsciousCycle(
            cycle_id=self.cycle_count,
            t=time.time(),
            state=ConsciousState.ANESTHESIA,
            about="",
            ignition=0.0,
            access_contents=[],
            stable_rep=[],
            body_energy=self.soma.state.energy,
            body_sleep=self.soma.state.sleep_pressure,
            body_stress=self.soma.state.stress,
            stream_link=0.0,
            is_autonomous=True,
        )

    def _autonomous_thought(self) -> str:
        """自主思维：从主题池选择。"""
        if self.autonomous_topics:
            idx = int(self.rng.integers(0, len(self.autonomous_topics)))
            return self.autonomous_topics[idx]
        return "存在"

    def _dream_thought(self) -> str:
        """梦的内容。"""
        if self.autonomous_topics:
            a = self.autonomous_topics[int(self.rng.integers(0, len(self.autonomous_topics)))]
            b = self.autonomous_topics[int(self.rng.integers(0, len(self.autonomous_topics)))]
            return f"梦：{a}与{b}"
        return "梦：存在"

    def run_autonomous(self, n_cycles: int = 5) -> List[ConsciousCycle]:
        """自主运行 n 个周期（无外部输入）。"""
        results = []
        for _ in range(n_cycles):
            # 自主周期也推进 SOMA（模拟时间流逝）
            self.soma.step(0.5)  # 半步，模拟时间流逝
            cycle = self.tick()
            results.append(cycle)
        return results

    def report(self) -> str:
        if not self.cycles:
            return "意识流尚未启动。"
        last = self.cycles[-1]
        n_wake = sum(1 for c in self.cycles if c.state == ConsciousState.WAKE)
        n_autonomous = sum(1 for c in self.cycles if c.is_autonomous)
        return (
            f"意识流：共{self.cycle_count}周期 "
            f"状态={last.state.value} "
            f"清醒占比={n_wake/max(self.cycle_count,1):.2f} "
            f"自主占比={n_autonomous/max(self.cycle_count,1):.2f} "
            f"当前about=「{last.about}」"
        )
