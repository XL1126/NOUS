"""记忆系统：工作/情景/语义/程序/自传 + 睡眠巩固。

文献：Tulving 1972；Buzsáki SWR；Frankland & Bontempi 2005。
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple
import time

import numpy as np


@dataclass
class MemoryItem:
    text: str
    kind: str = "any"  # user/agent/thought/fact/episode
    vec: Optional[np.ndarray] = None
    emotion: str = "平静"
    strength: float = 0.8
    ts: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)


class WorkingMemory:
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.items: Deque[MemoryItem] = deque(maxlen=capacity)

    def push(self, item: MemoryItem) -> None:
        self.items.append(item)

    def recent(self, kind: Optional[str] = None, k: int = 3) -> List[MemoryItem]:
        out = list(self.items)
        if kind:
            out = [x for x in out if x.kind == kind]
        return out[-k:]

    def texts(self, kind: Optional[str] = None, k: int = 3) -> List[str]:
        return [x.text for x in self.recent(kind, k)]


class EpisodicMemory:
    def __init__(self, capacity: int = 800, dim: int = 512):
        self.capacity = capacity
        self.dim = dim
        self.items: List[MemoryItem] = []

    def store(self, item: MemoryItem) -> None:
        self.items.append(item)
        if len(self.items) > self.capacity:
            # 衰减：丢最弱
            self.items.sort(key=lambda x: -x.strength)
            self.items = self.items[: self.capacity]

    def retrieve(self, vec: np.ndarray, k: int = 4) -> List[MemoryItem]:
        if not self.items:
            return []
        scored = []
        for it in self.items:
            if it.vec is None:
                continue
            s = float(np.dot(vec, it.vec) / (
                (np.linalg.norm(vec) + 1e-12) * (np.linalg.norm(it.vec) + 1e-12)
            ))
            scored.append((s * it.strength, it))
        scored.sort(key=lambda x: -x[0])
        return [it for _, it in scored[:k]]


class SemanticMemory:
    def __init__(self, space, capacity: int = 4000):
        self.space = space
        self.capacity = capacity
        self.facts: Dict[str, str] = {}  # concept -> gloss
        self.keys: Dict[str, List[str]] = {}

    def learn(self, concept: str, gloss: str, keys: Optional[List[str]] = None) -> None:
        concept = (concept or "").strip()[:48]
        gloss = (gloss or "").strip()
        if not concept or not gloss:
            return
        self.facts[concept] = gloss
        self.keys[concept] = list(keys or [concept])
        if len(self.facts) > self.capacity:
            # 简单裁剪
            for c in list(self.facts.keys())[:50]:
                del self.facts[c]
                self.keys.pop(c, None)

    def query(self, vec: np.ndarray, k: int = 4) -> List[Tuple[str, str, float]]:
        if not self.facts:
            return []
        scored = []
        for concept, gloss in self.facts.items():
            cv = self.space.encode(self.keys.get(concept, [concept]))
            s = float(np.dot(vec, cv) / (
                (np.linalg.norm(vec) + 1e-12) * (np.linalg.norm(cv) + 1e-12)
            ))
            scored.append((s, concept, gloss))
        scored.sort(key=lambda x: -x[0])
        return [(c, g, s) for s, c, g in scored[:k] if s > 0.12]


class ProceduralMemory:
    """产生式/技能：condition → action，成功强化。"""

    def __init__(self):
        self.rules: Dict[str, float] = {}  # key -> weight

    def reinforce(self, key: str, reward: float = 0.1) -> None:
        self.rules[key] = float(np.clip(self.rules.get(key, 0.5) + reward, 0.05, 2.0))

    def strength(self, key: str) -> float:
        return self.rules.get(key, 0.5)

    def top(self, k: int = 5) -> List[Tuple[str, float]]:
        return sorted(self.rules.items(), key=lambda kv: -kv[1])[:k]


class AutobiographicalMemory:
    def __init__(self, max_chapters: int = 400):
        self.chapters: List[str] = []
        self.max_chapters = max_chapters
        self.identity_facts: List[str] = []

    def record(self, line: str) -> None:
        line = (line or "").strip()
        if not line:
            return
        self.chapters.append(line)
        if len(self.chapters) > self.max_chapters:
            self.chapters = self.chapters[-self.max_chapters:]

    def life_summary(self, k: int = 5) -> str:
        if not self.chapters:
            return "自传还很短，刚开始经历世界。"
        return "自传近况：" + " | ".join(self.chapters[-k:])

    def narrative(self) -> str:
        if not self.identity_facts:
            return "我还在形成对自己的稳定描述。"
        return "我是" + "；".join(self.identity_facts[-4:]) + "。"


class MemoryBank:
    def __init__(self, space, wm_cap: int = 7, ep_cap: int = 800):
        self.space = space
        self.wm = WorkingMemory(wm_cap)
        self.episodic = EpisodicMemory(ep_cap, space.dim)
        self.semantic = SemanticMemory(space)
        self.procedural = ProceduralMemory()
        self.auto = AutobiographicalMemory()
        self.consolidations = 0

    def consolidate(self) -> str:
        """睡眠/休息巩固：WM→语义/自传，弱情景衰减。"""
        self.consolidations += 1
        n = 0
        for it in list(self.wm.items):
            if it.kind in ("user", "agent", "thought") and len(it.text) >= 2:
                self.semantic.learn(f"经历{self.consolidations}_{n}", it.text[:80], [it.text[:12]])
                self.auto.record(f"C{self.consolidations}: {it.text[:40]}")
                n += 1
        for it in self.episodic.items:
            it.strength *= 0.97
        self.episodic.items = [x for x in self.episodic.items if x.strength > 0.08]
        return f"巩固第{self.consolidations}次：压缩{n}条；自传{len(self.auto.chapters)}章。"
