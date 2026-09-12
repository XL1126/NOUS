import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind
from src.consciousness.stream import ConsciousnessStream, ConsciousState, SleepWakeMachine
from src.soma.body import Soma
from src.workspace.global_ws import GlobalWorkspace
from src.consciousness.core import ConsciousnessCore
from src.consciousness.dream import DreamCycle
from src.self_model.meta import InnerSpeech


def _make_stream():
    soma = Soma()
    ws = GlobalWorkspace()
    core = ConsciousnessCore()
    dreams = DreamCycle()
    inner = InnerSpeech()
    return ConsciousnessStream(soma=soma, workspace=ws, core=core, dreams=dreams, inner_speech=inner)


def test_sleep_wake_transitions():
    m = SleepWakeMachine()
    assert m.state == ConsciousState.WAKE
    # 高睡压 → 困倦
    for _ in range(10):
        m.step(sleep_pressure=0.7, energy=0.3, external_input=False)
    assert m.state in (ConsciousState.DROWSY, ConsciousState.NREM)
    # 外部输入 → 唤醒
    for _ in range(5):
        m.step(sleep_pressure=0.7, energy=0.3, external_input=True)
    assert m.state == ConsciousState.WAKE


def test_consciousness_stream_autonomous():
    s = _make_stream()
    s.add_topic("猫")
    s.add_topic("意识")
    cycles = s.run_autonomous(n_cycles=5)
    assert len(cycles) == 5
    assert s.cycle_count == 5
    # 至少有一些是自主的
    assert any(c.is_autonomous for c in cycles)


def test_consciousness_stream_with_input():
    s = _make_stream()
    c = s.tick(external_input="你好", external_broadcast={"你好": 0.8})
    assert c.about == "你好"
    assert c.state == ConsciousState.WAKE
    assert not c.is_autonomous


def test_nrem_has_no_global_broadcast():
    s = _make_stream()
    # 强制进入 NREM，且能量低睡压高（不会被唤醒）
    s.sleep_wake.state = ConsciousState.NREM
    s.sleep_wake.cycles_in_state = 10
    s.soma.state.energy = 0.2
    s.soma.state.sleep_pressure = 0.8
    c = s.tick()
    assert c.state == ConsciousState.NREM
    assert len(c.access_contents) == 0  # 无全局广播


def test_stream_report():
    s = _make_stream()
    s.add_topic("存在")
    s.run_autonomous(n_cycles=3)
    r = s.report()
    assert "意识流" in r
    assert "周期" in r


def test_mind_has_stream():
    m = NousMind({"seed": 50})
    assert m.stream is not None
    assert m.stream.cycle_count >= 0
    r = m.respond("你好")
    assert m.stream.cycle_count >= 1
    s = m.summary()
    assert "consciousness_stream" in s
    assert "sleep_wake_state" in s


def test_mind_stream_status_intent():
    m = NousMind({"seed": 51})
    r = m.respond("意识流状态")
    assert r["intent"] == "stream_status"
    assert "意识流" in r["reply"] or "周期" in r["reply"]


def test_mind_autonomous_intent():
    m = NousMind({"seed": 52})
    r = m.respond("自主思维")
    assert r["intent"] == "autonomous"
    assert "周期" in r["reply"] or "自主" in r["reply"]
