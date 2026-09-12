"""NOUS 状态持久化（JSON）。无 LLM 权重，只存符号-向量侧状态。"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


def save_mind(mind, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "saved_at": time.time(),
        "version": "0.2.0",
        "name": mind.name,
        "identity": mind.identity,
        "turn": mind.turn,
        "development": mind.development,
        "user_profile": mind.user_profile,
        "runtime_knowledge": mind.runtime_knowledge[-300:],
        "topic": mind.topic,
        "focus": mind.focus,
        "last_user": mind.last_user,
        "last_reply": mind.last_reply,
        "last_intent": mind.last_intent,
        "last_thought": mind.last_thought,
        "soma": mind.soma.state.snapshot(),
        "soma_set_point": mind.soma.set_point,
        "semantic_facts": mind.mem.semantic.facts,
        "semantic_keys": mind.mem.semantic.keys,
        "autobiography": mind.mem.auto.chapters[-200:],
        "identity_bits": mind.self_model.identity_bits,
        "narrative": mind.self_model.narrative[-40:],
        "other": {
            "name": mind.other.name,
            "patience": mind.other.patience,
            "expertise": mind.other.expertise,
            "corrections": mind.other.corrections,
            "turns": mind.other.turns,
        },
        "goals": [
            {"text": g.text, "priority": g.priority, "source": g.source, "progress": g.progress}
            for g in mind.goals.goals
        ],
        "graph_triples": mind.graph.triples[-500:],
        "graph_fillers": mind.graph.fillers,
        "procedural": mind.mem.procedural.rules,
        "consolidations": mind.mem.consolidations,
        "inner_log": mind.inner.log[-30:],
        "vocab_names": list(mind.space.vocab.keys())[:2000],
    }
    # 可选：保存常用概念向量（体积可控）
    vecs = {}
    for name in list(mind.space.vocab.keys())[:400]:
        vecs[name] = mind.space.vocab[name].astype(np.float32).round(4).tolist()
    payload["concept_vecs"] = vecs
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def load_mind(mind, path: str | Path) -> bool:
    path = Path(path)
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict):
        return False

    mind.turn = int(data.get("turn", 0))
    mind.development = float(data.get("development", 0.0))
    mind.user_profile = dict(data.get("user_profile") or {})
    mind.runtime_knowledge = [tuple(x) for x in (data.get("runtime_knowledge") or [])]
    mind.topic = data.get("topic", mind.topic)
    mind.focus = data.get("focus", mind.focus)
    mind.last_user = data.get("last_user", "")
    mind.last_reply = data.get("last_reply", "")
    mind.last_intent = data.get("last_intent", "")
    mind.last_thought = data.get("last_thought", "")

    snap = data.get("soma") or {}
    st = mind.soma.state
    for k in ("energy", "sleep_pressure", "stress", "social", "curiosity", "safety",
              "arousal", "dopamine", "norepinephrine", "serotonin", "acetylcholine", "glucose"):
        if k in snap:
            setattr(st, k, float(snap[k]))
    for k, v in (data.get("soma_set_point") or {}).items():
        if k in mind.soma.set_point:
            mind.soma.set_point[k] = float(v)

    for concept, gloss in (data.get("semantic_facts") or {}).items():
        keys = (data.get("semantic_keys") or {}).get(concept) or [concept]
        mind.mem.semantic.learn(concept, gloss, list(keys))
    mind.mem.auto.chapters = list(data.get("autobiography") or [])
    mind.self_model.identity_bits = list(data.get("identity_bits") or [])
    mind.self_model.narrative = list(data.get("narrative") or [])
    o = data.get("other") or {}
    mind.other.name = o.get("name", mind.other.name)
    mind.other.patience = float(o.get("patience", 0.7))
    mind.other.expertise = float(o.get("expertise", 0.4))
    mind.other.corrections = int(o.get("corrections", 0))
    mind.other.turns = int(o.get("turns", 0))

    from .self_model.meta import Goal
    mind.goals.goals = []
    for g in data.get("goals") or []:
        mind.goals.push(Goal(
            text=g.get("text", ""),
            priority=float(g.get("priority", 0.5)),
            source=g.get("source", "intrinsic"),
            progress=float(g.get("progress", 0.0)),
        ))

    mind.graph.triples = [tuple(x) for x in (data.get("graph_triples") or [])]
    for role, items in (data.get("graph_fillers") or {}).items():
        for item in items:
            mind.graph.bind(role, item)

    rules = data.get("procedural") or {}
    for k, v in rules.items():
        mind.mem.procedural.rules[k] = float(v)
    mind.mem.consolidations = int(data.get("consolidations", 0))
    mind.inner.log = list(data.get("inner_log") or [])

    for name, vec in (data.get("concept_vecs") or {}).items():
        arr = np.asarray(vec, dtype=np.float64)
        if arr.shape[0] == mind.space.dim:
            mind.space.vocab[name] = arr
    return True
