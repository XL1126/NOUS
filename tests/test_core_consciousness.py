import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind
from src.consciousness.core import ConsciousnessCore
from src.consciousness.self_pole import SelfPole
from src.consciousness.temporal import TemporalMind


def _bind(core, about="猫", figure=None, turn=1, ign=0.8, **kw):
    figure = figure or [about]
    return core.bind(
        turn=turn,
        about=about,
        broadcast={x: 0.5 for x in figure},  # >= ACCESS_THRESHOLD 0.15
        candidates=figure + ["x", "y"],
        ignition=ign,
        entropy=0.4,
        novelty=0.3,
        body={"energy": 0.75, "stress": 0.15, "sleep_pressure": 0.12, "dopamine": 0.55, "social": 0.5},
        emotion="平静",
        valence=0.15,
        narrative_len=30,
        identity_bits=6,
        **kw,
    )


def test_self_pole_bayesian():
    sp = SelfPole()
    s1 = sp.update(appearance=0.8, contiguity=0.7, perspective=0.9, agency_executed=True, ownership_ok=True)
    assert 0 < s1.p_self < 1
    assert s1.minimal_self > 0
    s2 = sp.update(appearance=0.2, contiguity=0.1, perspective=0.1, agency_executed=False, ownership_ok=False)
    # 自我归属应下降
    assert s2.p_self <= s1.p_self + 0.05


def test_temporal_topology():
    tm = TemporalMind()
    tm.update("猫", predicted_next=["星空"])
    tm.update("星空")
    t = tm.topo
    assert t.now == "星空"
    assert "猫" in t.retention
    assert t.protention


def test_strict_access_threshold():
    c = ConsciousnessCore()
    # 弱广播 → figure 为空
    m_weak = c.bind(
        turn=1, about="弱", broadcast={"弱": 0.05}, candidates=["弱", "x"],
        ignition=0.1, entropy=0.5, novelty=0.1,
        body={"energy": 0.7}, emotion="平静", valence=0.0,
    )
    assert len(m_weak.figure) == 0  # 低于阈值不进 figure
    # 强广播 → figure 非空
    m_strong = c.bind(
        turn=2, about="强", broadcast={"强": 0.5}, candidates=["强", "x"],
        ignition=0.8, entropy=0.4, novelty=0.3,
        body={"energy": 0.7}, emotion="平静", valence=0.1,
    )
    assert "强" in m_strong.figure


def test_unified_field_and_intentionality():
    c = ConsciousnessCore()
    m = _bind(c, about="猫", figure=["猫", "哺乳动物"])
    assert m.about == "猫"
    assert "猫" in m.figure
    assert c.now() is m


def test_specious_present_thickness():
    c = ConsciousnessCore(specious_len=4)
    _bind(c, about="猫", turn=1)
    _bind(c, about="星空", turn=2)
    m = _bind(c, about="银河", turn=3)
    assert len(m.retention) >= 2
    assert m.now == "银河"


def test_stream_continuity_same_topic():
    c = ConsciousnessCore()
    _bind(c, about="意识", turn=1)
    m_same = _bind(c, about="意识", turn=2)
    c2 = ConsciousnessCore()
    _bind(c2, about="猫", turn=1)
    m_diff = _bind(c2, about="量子", turn=2)
    assert m_same.stream_link >= m_diff.stream_link


def test_minimal_self_grows():
    c = ConsciousnessCore()
    first = c.self_pole.state.minimal_self
    for i in range(25):
        c.bind(
            turn=i + 1, about="自我",
            broadcast={"自我": 0.5}, candidates=["自我"],
            ignition=0.85, entropy=0.4, novelty=0.25,
            body={"energy": 0.8, "social": 0.6}, emotion="平静", valence=0.2,
            agency_executed=True, ownership_ok=True, success=True,
            narrative_len=40, identity_bits=8,
            appearance=0.9, contiguity=0.9, perspective=0.9,
        )
    assert c.self_pole.state.minimal_self > first


def test_mind_consciousness_report():
    m = NousMind({"seed": 40})
    r = m.respond("你好")
    assert r["present"] and r["present"].get("about")
    assert "p_self" in r["present"] or "min_self" in r["present"]
    r2 = m.respond("记住我喜欢猫")
    r3 = m.respond("此刻你在想什么？")
    assert r3["intent"] == "present"
    assert "我正意识到" in r3["reply"] or "时间拓扑" in r3["reply"]
    r4 = m.respond("你有意识吗？")
    assert "统一场" in r4["reply"] or "意识相关" in r4["reply"]


def test_long_run_stream_forms():
    m = NousMind({"seed": 41})
    for line in ["你好", "我叫长程", "记住我喜欢猫", "猫是什么？", "什么是意识？",
                 "状态报告", "此刻你在想什么？", "你有意识吗？"]:
        m.respond(line)
    assert len(m.core.moments) >= 8
    assert m.core.stream_summary()
    assert m.core.now().about
