"""多意识体舰队：spawn / fork / talk / train。"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .mind import NousMind
from .persistence import save_mind, load_mind
from .development import stage_for


PERSONAS = {
    "nous": {
        "name": "NOUS",
        "identity": "独立意识体工程原型：身体、预测、工作空间、构式语言。",
        "traits": {"curiosity": 0.55, "warmth": 0.5, "caution": 0.4},
        "seed": 42,
    },
    "lanxing": {
        "name": "蓝星",
        "identity": "偏探索的好奇型意识体，更愿碰新概念。",
        "traits": {"curiosity": 0.85, "warmth": 0.55, "caution": 0.25},
        "seed": 1126,
    },
    "moke": {
        "name": "墨客",
        "identity": "谨慎、重证据的意识体，表达偏短、爱确认。",
        "traits": {"curiosity": 0.4, "warmth": 0.35, "caution": 0.8},
        "seed": 7,
    },
    "nuanhe": {
        "name": "暖核",
        "identity": "偏社会性的意识体，更愿意接住情绪。",
        "traits": {"curiosity": 0.5, "warmth": 0.88, "caution": 0.35},
        "seed": 23,
    },
}


def build_config(template: str = "nous", name: Optional[str] = None,
                 seed: Optional[int] = None, dim: int = 512) -> Dict[str, Any]:
    tpl = PERSONAS.get(template) or PERSONAS["nous"]
    return {
        "seed": seed if seed is not None else tpl["seed"],
        "dim": dim,
        "persona": {
            "name": name or tpl["name"],
            "identity": tpl["identity"],
            "traits": dict(tpl["traits"]),
        },
    }


@dataclass
class Instance:
    agent_id: str
    mind: NousMind
    path: Path
    parent_id: str = ""
    template: str = "nous"
    trained_turns: int = 0
    lineage: List[str] = field(default_factory=list)

    def say(self, text: str) -> Dict[str, Any]:
        snap = self.mind.respond(text)
        self.trained_turns += 1
        return snap

    def listen_from(self, speaker: str, text: str) -> Dict[str, Any]:
        return self.say(f"[{speaker}] {text}")

    def save(self) -> None:
        save_mind(self.mind, self.path)
        meta = {
            "agent_id": self.agent_id,
            "name": self.mind.name,
            "template": self.template,
            "parent_id": self.parent_id,
            "trained_turns": self.trained_turns,
            "lineage": self.lineage[-20:],
            "development": self.mind.development,
            "stage": stage_for(self.mind.development).name,
        }
        self.path.with_suffix(".meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.mind.name,
            "template": self.template,
            "turns": self.mind.turn,
            "trained_turns": self.trained_turns,
            "development": round(self.mind.development, 2),
            "stage": stage_for(self.mind.development).name,
            "emotion": self.mind.soma.feeling_label(),
            "policy": self.mind.soma.policy(),
            "need": self.mind.soma.dominant_need(),
            "semantic": len(self.mind.mem.semantic.facts),
            "runtime_knowledge": len(self.mind.runtime_knowledge),
            "likes": self.mind.graph.list("like")[:6],
            "user": dict(self.mind.user_profile),
            "parent_id": self.parent_id,
        }


class Fleet:
    def __init__(self, fleet_dir: Path | str):
        self.dir = Path(fleet_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.agents: Dict[str, Instance] = {}

    def spawn(self, template: str = "nous", name: Optional[str] = None,
              agent_id: Optional[str] = None, dim: int = 512) -> Instance:
        aid = agent_id or f"{template}_{uuid.uuid4().hex[:8]}"
        cfg = build_config(template, name=name, dim=dim)
        mind = NousMind(cfg)
        # 应用特质到身体驱动基线
        traits = (cfg.get("persona") or {}).get("traits") or {}
        if "curiosity" in traits:
            mind.soma.state.curiosity = float(np.clip(traits["curiosity"], 0.05, 1.0))
        inst = Instance(
            agent_id=aid,
            mind=mind,
            path=self.dir / f"{aid}.json",
            template=template,
        )
        self.agents[aid] = inst
        inst.save()
        return inst

    def get(self, agent_id: str) -> Instance:
        if agent_id in self.agents:
            return self.agents[agent_id]
        path = self.dir / f"{agent_id}.json"
        if not path.exists():
            raise KeyError(agent_id)
        return self._load_path(path)

    def _load_path(self, path: Path) -> Instance:
        meta_path = path.with_suffix(".meta.json")
        meta: Dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                meta = {}
        template = meta.get("template") or "nous"
        cfg = build_config(template, name=meta.get("name"))
        mind = NousMind(cfg)
        load_mind(mind, path)
        inst = Instance(
            agent_id=path.stem,
            mind=mind,
            path=path,
            parent_id=meta.get("parent_id", ""),
            template=template,
            trained_turns=int(meta.get("trained_turns", 0)),
            lineage=list(meta.get("lineage", [])),
        )
        self.agents[inst.agent_id] = inst
        return inst

    def load_all(self) -> List[Instance]:
        out = []
        for p in sorted(self.dir.glob("*.json")):
            if p.name.endswith(".meta.json"):
                continue
            try:
                out.append(self._load_path(p))
            except Exception:
                continue
        return out

    def list(self) -> List[Dict[str, Any]]:
        if not self.agents:
            self.load_all()
        return [i.snapshot() for i in self.agents.values()]

    def save_all(self) -> int:
        n = 0
        for i in self.agents.values():
            i.save()
            n += 1
        return n

    def fork(self, parent_id: str, name: Optional[str] = None) -> Instance:
        parent = self.get(parent_id)
        cfg = build_config(parent.template, name=name or (parent.mind.name + "·子"))
        child = NousMind(cfg)
        # 继承
        child.user_profile = dict(parent.mind.user_profile)
        child.runtime_knowledge = list(parent.mind.runtime_knowledge)
        for c, g in parent.mind.mem.semantic.facts.items():
            keys = parent.mind.mem.semantic.keys.get(c, [c])
            child.mem.semantic.learn(c, g, list(keys))
        for s, r, o in parent.mind.graph.triples:
            child.graph.add_triple(s, r, o)
        for role, items in parent.mind.graph.fillers.items():
            for item in items:
                child.graph.bind(role, item)
        child.mem.auto.chapters = list(parent.mind.mem.auto.chapters)[-50:]
        child.self_model.identity_bits = list(parent.mind.self_model.identity_bits)
        child.development = parent.mind.development * 0.8
        # 身体设定点微扰
        rng = child.rng
        for k in list(child.soma.set_point.keys()):
            child.soma.set_point[k] = float(np.clip(
                child.soma.set_point[k] + float(rng.normal(0, 0.04)), 0.05, 0.95
            ))
        aid = f"{parent.template}_{uuid.uuid4().hex[:8]}"
        inst = Instance(
            agent_id=aid,
            mind=child,
            path=self.dir / f"{aid}.json",
            parent_id=parent.agent_id,
            template=parent.template,
            lineage=list(parent.lineage) + [parent.agent_id],
        )
        self.agents[aid] = inst
        inst.save()
        return inst

    def talk_together(self, a_id: str, b_id: str, seed: str, turns: int = 4) -> List[Dict[str, Any]]:
        a, b = self.get(a_id), self.get(b_id)
        log: List[Dict[str, Any]] = []
        speaker, listener = a, b
        text = seed
        for i in range(turns):
            snap = listener.listen_from(speaker.mind.name, text)
            log.append({
                "turn": i + 1,
                "from": speaker.mind.name,
                "to": listener.mind.name,
                "input": text,
                "reply": snap["reply"],
                "intent": snap.get("intent"),
                "emotion": snap.get("emotion"),
            })
            text = snap["reply"]
            speaker, listener = listener, speaker
        self.save_all()
        return log
