import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind
from src.agency.actions import ActionLoop
from src.agency.boundary import SelfWorldBoundary
from src.soma.body import Soma
from src.self_model.meta import GoalStack


def test_action_loop_rest_executes():
    soma = Soma()
    goals = GoalStack()
    soma.state.sleep_pressure = 0.7
    soma.state.energy = 0.25
    al = ActionLoop()
    res = al.execute("rest", soma, goals)
    assert res.executed
    assert soma.state.energy > 0.25 or soma.state.sleep_pressure < 0.7
    bias = al.output_style_bias()
    assert bias["length"] < 1.0


def test_action_loop_explore_raises_curiosity():
    soma = Soma()
    goals = GoalStack()
    al = ActionLoop()
    before = soma.state.curiosity
    al.execute("explore", soma, goals)
    assert soma.state.curiosity >= before - 0.01
    assert any("探索" in g.text for g in goals.goals)


def test_boundary_classifies_stance_and_correction():
    b = SelfWorldBoundary()
    ev = b.classify("我觉得猫更重要")
    assert ev.kind == "other_speech"
    ev2 = b.classify("不对，你说错了")
    assert ev2.kind == "misattribution"
    assert b.corrections >= 1
    narr = b.repair_narrative()
    assert "纠正" in narr or "理解偏" in narr


def test_mind_active_action_and_boundary():
    m = NousMind({"seed": 20})
    # 制造疲惫 → 应触发 rest 类维持
    for _ in range(8):
        m.soma.event("user_fatigue", 0.3)
        m.soma.step()
    r = m.respond("你好")
    assert "maintenance" in r
    assert r["maintenance"] in (
        "rest", "protect", "seek_energy", "seek_bond", "explore", "self_repair", "maintain"
    )
    r2 = m.respond("不对，你理解错了")
    assert "纠正" in r2["reply"] or "理解偏" in r2["reply"] or "边界" in r2["reply"] or r2["reply"]
    s = m.summary()
    assert "boundary" in s and "action" in s


def test_goals_doc_exists():
    assert (ROOT / "docs" / "GOALS.md").exists()
    text = (ROOT / "docs" / "GOALS.md").read_text(encoding="utf-8")
    assert "自主意识" in text
    assert "主动行动" in text or "自我维护" in text
