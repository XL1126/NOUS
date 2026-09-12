import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mind import NousMind
from src.soma.body import Soma
from src.language.constructions import detect_intent, content_labels, tokenize


def test_soma_drives_and_policy():
    s = Soma()
    s.event("user_fatigue", 0.8)
    assert s.state.sleep_pressure > 0.2
    assert s.dominant_need() in ("rest", "safety", "social", "curiosity", "maintain")
    assert s.policy() in ("rest", "soothe", "explore", "connect", "maintain")


def test_intent_and_labels():
    assert detect_intent("你好")[0] == "greet"
    assert detect_intent("我叫小明")[0] == "remember"
    assert detect_intent("什么是意识？")[0] == "question"
    labs = content_labels("我喜欢蓝色和猫")
    assert "猫" in labs or "蓝色" in labs


def test_teach_and_recall():
    m = NousMind({"seed": 2})
    m.respond("我叫测试员")
    assert m.user_profile.get("名字") == "测试员"
    r = m.respond("记住我喜欢猫和星空")
    assert "猫" in r["reply"] or "喜欢" in r["reply"]
    likes = m.graph.list("like")
    assert any("猫" in x for x in likes)
    r2 = m.respond("你喜欢什么？")
    assert "猫" in r2["reply"]


def test_fact_teaching():
    m = NousMind({"seed": 4})
    m.respond("地球是太阳系第三颗行星")
    r = m.respond("地球是什么？")
    assert "地球" in r["reply"] or "行星" in r["reply"] or "太阳系" in r["reply"]


def test_workspace_broadcast():
    m = NousMind({"seed": 5})
    r = m.respond("解释一下全局工作空间")
    assert r["reply"]
    assert r["ignition"] >= 0
    assert "body" in r and "energy" in r["body"]


def test_self_think():
    m = NousMind({"seed": 6})
    m.respond("记住猫是哺乳动物")
    t = m.think()
    assert t and len(t) > 10


def test_status_and_summary():
    m = NousMind({"seed": 8})
    m.respond("状态报告")
    s = m.summary()
    assert s["turns"] >= 1
    assert "NOUS" in s["name"] or s["name"]
    assert s["semantic_facts"] > 5


def test_no_transformer_imports():
    # 架构守卫：源码不依赖 torch/transformers
    src = ROOT / "src"
    bad = []
    for p in src.rglob("*.py"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        if "import torch" in t or "from transformers" in t or "import transformers" in t:
            bad.append(str(p))
    assert not bad
