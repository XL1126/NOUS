import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind
from src.persistence import save_mind, load_mind
from src.development import stage_for, clamp_output, STAGES
from src.fleet import Fleet
from src.train import train_mind, DEFAULT_CURRICULUM
from src.neural.race import SpikeRace
from src.cognition.counterfactual import plan_counterfactual, next_experiment


def test_development_stages():
    assert stage_for(0).name == "sensorimotor"
    assert stage_for(12).name == "telegraphic"
    assert stage_for(50).name == "reflective"
    t = clamp_output("很长的一句话。还有后半句。", stage_for(0))
    assert len(t) <= 16


def test_persistence_roundtrip(tmp_path):
    m = NousMind({"seed": 11})
    m.respond("我叫持久化测试")
    m.respond("记住我喜欢猫")
    m.respond("北京是中国的首都")
    p = tmp_path / "state.json"
    save_mind(m, p)
    m2 = NousMind({"seed": 99})
    assert load_mind(m2, p)
    assert m2.user_profile.get("名字") == "持久化测试"
    assert any("猫" in x for x in m2.graph.list("like"))
    r = m2.respond("北京是什么？")
    assert "北京" in r["reply"] or "首都" in r["reply"]


def test_fleet_spawn_fork_talk(tmp_path):
    fleet = Fleet(tmp_path / "fleet")
    a = fleet.spawn("lanxing", name="蓝星")
    b = fleet.spawn("moke", name="墨客")
    assert a.mind.name == "蓝星"
    a.say("记住我喜欢星空")
    child = fleet.fork(a.agent_id, name="蓝星·子")
    assert child.parent_id == a.agent_id
    assert any("星空" in x for x in child.mind.graph.list("like"))
    log = fleet.talk_together(a.agent_id, b.agent_id, seed="你好，聊聊身体", turns=3)
    assert len(log) == 3
    assert all(x["reply"] for x in log)


def test_train_progresses_development():
    m = NousMind({"seed": 3})
    report = train_mind(m, DEFAULT_CURRICULUM[:10], epochs=1, sleep_every=6)
    assert report.turns == 10
    assert report.development > 0
    assert report.stage in {s.name for s in STAGES}


def test_spike_race_winners():
    race = SpikeRace(n_pop=32, seed=1)
    winners = race.compete(["猫", "星空", "蓝色"], {"猫": 0.9, "星空": 0.4, "蓝色": 0.2})
    assert winners and winners[0][0] in ("猫", "星空", "蓝色")


def test_counterfactual_and_experiment():
    line = plan_counterfactual("猫", novelty=0.6, energy=0.5)
    assert "猫" in line
    exp = next_experiment("猫", [])
    assert "教我" in exp or "绑定" in exp


def test_mind_counterfactual_intent():
    m = NousMind({"seed": 5})
    r = m.respond("如果能量很低会怎样？")
    assert r["intent"] in ("counterfactual", "question", "open")
    assert r["reply"]


def test_no_llm_deps():
    src = ROOT / "src"
    for p in src.rglob("*.py"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        assert "import torch" not in t
        assert "from transformers" not in t
