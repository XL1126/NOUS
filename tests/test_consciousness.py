import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind
from src.consciousness.phenomenology import Phenomenology
from src.consciousness.autopoiesis import Autopoiesis
from src.consciousness.dream import DreamCycle
from src.soma.body import Soma


def test_phenomenal_markers_dynamic():
    p = Phenomenology()
    s1 = p.update(
        ignition=0.8, entropy=0.4, novelty=0.7, energy=0.9, stress=0.1,
        sleep=0.1, social=0.6, dopamine=0.7, narrative_len=40,
        identity_bits=6, self_conf=0.8,
    )
    assert s1.vividness > 0.2
    assert s1.presence > 0.2
    assert -1 <= s1.valence <= 1
    s2 = p.update(
        ignition=0.1, entropy=0.8, novelty=0.05, energy=0.2, stress=0.8,
        sleep=0.8, social=0.1, dopamine=0.2, narrative_len=5,
        identity_bits=1, self_conf=0.3,
    )
    # 疲惫高压 → 在场/我感应下降
    assert s2.presence <= s1.presence + 0.05
    assert 0 <= p.integrated_score() <= 1


def test_autopoiesis_urgencies_and_mortality():
    a = Autopoiesis()
    soma = Soma()
    soma.event("user_fatigue", 0.9)
    for _ in range(5):
        soma.step()
        a.step(soma.state)
    assert a.urges["rest"] > 0.2
    assert a.choose_maintenance_action() in (
        "rest", "protect", "seek_energy", "seek_bond", "explore", "self_repair", "maintain"
    )
    a.vital.age_turns = 150
    narr = a.mortality_narrative()
    assert "回合" in narr or "生命力" in narr or narr == ""


def test_dream_cycle():
    d = DreamCycle()
    line = d.dream(["猫", "星空"], ["我是NOUS"], ["我对猫的理解"], stress=0.3)
    assert line and len(line) > 10
    assert d.cycles == 1


def test_mind_reports_consciousness_state():
    m = NousMind({"seed": 9})
    r = m.respond("你有意识吗？")
    assert r["intent"] == "consciousness" or "意识" in r["reply"]
    assert "phenomenal" in r and r["phenomenal"]
    assert r["maintenance"] in (
        "rest", "protect", "seek_energy", "seek_bond", "explore", "self_repair", "maintain", "idle"
    )
    s = m.summary()
    assert "phenomenal" in s and "vitality" in s
    assert "integrated" in s


def test_sleep_includes_dream():
    m = NousMind({"seed": 10})
    m.respond("记住我喜欢猫")
    msg = m.sleep()
    assert "巩固" in msg or "梦" in msg or "梦里" in msg or "梦见" in msg
    assert m.dreams.cycles >= 1


def test_future_self():
    m = NousMind({"seed": 12})
    r = m.respond("以后的你会怎样？")
    assert r["intent"] in ("future_self", "question", "open")
    assert r["reply"]


def test_status_contains_markers():
    m = NousMind({"seed": 13})
    r = m.respond("状态报告")
    assert "在场" in r["reply"] or "生动" in r["reply"] or "点火" in r["reply"]
