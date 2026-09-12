"""概念空间 + SPA 语义指针 + 角色填充图。

文献：Eliasmith SPA；Kanerva HD computing；Tulving 语义记忆。
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import numpy as np


class ConceptSpace:
    """高维单位向量词表；绑定/捆绑/相似。"""

    def __init__(self, dim: int = 512, seed: int = 42):
        self.dim = int(dim)
        self.rng = np.random.default_rng(seed)
        self.vocab: Dict[str, np.ndarray] = {}

    def pointer(self, name: str) -> np.ndarray:
        if name not in self.vocab:
            v = self.rng.standard_normal(self.dim)
            v /= (np.linalg.norm(v) + 1e-12)
            self.vocab[name] = v.astype(np.float64)
        return self.vocab[name]

    def encode(self, labels: Sequence[str]) -> np.ndarray:
        if not labels:
            return self.pointer("::empty")
        acc = np.zeros(self.dim)
        for lab in labels:
            acc = acc + self.pointer(lab)
        n = np.linalg.norm(acc)
        return acc / n if n > 1e-12 else acc

    def bind(self, a: str, b: str) -> np.ndarray:
        """
        Circular convolution 绑定（Eliasmith SPA / Plate 2003）：
        c = a ⊛ b
        频域：c = IDFT(DFT(a) ⊙ DFT(b))
        """
        va, vb = self.pointer(a), self.pointer(b)
        return self.bind_vecs(va, vb)

    def bind_vecs(self, va: np.ndarray, vb: np.ndarray) -> np.ndarray:
        """向量循环卷积绑定。"""
        c = np.real(np.fft.ifft(np.fft.fft(va) * np.fft.fft(vb)))
        n = np.linalg.norm(c)
        return c / n if n > 1e-12 else c

    def unbind(self, c: np.ndarray, b: str) -> np.ndarray:
        """
        近似逆绑定（解绑定）：
        a ≈ c ⊛ b⁻¹
        b⁻¹ 是 b 的循环相关逆（共轭翻转）
        """
        vb = self.pointer(b)
        # 循环相关逆：IDFT(DFT(c) ⊙ conj(DFT(b)))
        a_approx = np.real(np.fft.ifft(np.fft.fft(c) * np.conj(np.fft.fft(vb))))
        n = np.linalg.norm(a_approx)
        return a_approx / n if n > 1e-12 else a_approx

    def unbind_vecs(self, c: np.ndarray, vb: np.ndarray) -> np.ndarray:
        """向量解绑定。"""
        a_approx = np.real(np.fft.ifft(np.fft.fft(c) * np.conj(np.fft.fft(vb))))
        n = np.linalg.norm(a_approx)
        return a_approx / n if n > 1e-12 else a_approx

    def bundle(self, vecs: Sequence[np.ndarray]) -> np.ndarray:
        if not vecs:
            return self.pointer("::empty")
        acc = np.sum(vecs, axis=0)
        n = np.linalg.norm(acc)
        return acc / n if n > 1e-12 else acc

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / ((np.linalg.norm(a) + 1e-12) * (np.linalg.norm(b) + 1e-12)))

    def nearest(self, vec: np.ndarray, k: int = 5,
                exclude: Iterable[str] = ()) -> List[Tuple[str, float]]:
        exclude = set(exclude)
        scored = []
        for name, v in self.vocab.items():
            if name in exclude:
                continue
            scored.append((name, self.similarity(vec, v)))
        scored.sort(key=lambda x: -x[1])
        return scored[:k]


class SemanticGraph:
    """简单角色-填充绑定图：like/dislike/is/part/cause…"""

    ROLE_LIKE = "like"
    ROLE_DISLIKE = "dislike"
    ROLE_IS = "is"
    ROLE_PART = "part"
    ROLE_CAUSE = "cause"
    ROLE_AT = "at"
    ROLE_NAME = "name"

    def __init__(self, space: Optional[ConceptSpace] = None):
        self.space = space or ConceptSpace()
        self.fillers: Dict[str, List[str]] = {
            self.ROLE_LIKE: [], self.ROLE_DISLIKE: [], self.ROLE_IS: [],
            self.ROLE_PART: [], self.ROLE_CAUSE: [], self.ROLE_AT: [],
            self.ROLE_NAME: [],
        }
        self.triples: List[Tuple[str, str, str]] = []

    def bind(self, role: str, filler: str) -> None:
        filler = (filler or "").strip()
        if not filler:
            return
        self.fillers.setdefault(role, [])
        if filler not in self.fillers[role]:
            self.fillers[role].append(filler)
        # 限量
        if len(self.fillers[role]) > 200:
            self.fillers[role] = self.fillers[role][-200:]

    def add_triple(self, s: str, r: str, o: str) -> None:
        s, r, o = s.strip(), r.strip(), o.strip()
        if not s or not o:
            return
        self.triples.append((s, r, o))
        if len(self.triples) > 2000:
            self.triples = self.triples[-2000:]
        role_map = {
            "是": self.ROLE_IS, "叫": self.ROLE_NAME, "在": self.ROLE_AT,
            "喜欢": self.ROLE_LIKE, "讨厌": self.ROLE_DISLIKE,
            "导致": self.ROLE_CAUSE, "属于": self.ROLE_PART,
            "is": self.ROLE_IS, "named": self.ROLE_NAME, "at": self.ROLE_AT,
        }
        self.bind(role_map.get(r, self.ROLE_IS), f"{s}={o}")

    def list(self, role: str) -> List[str]:
        return list(self.fillers.get(role, []))

    def related(self, a: str, b: str) -> Optional[str]:
        for s, r, o in self.triples:
            if (s == a and o == b) or (s == b and o == a):
                return f"{s}{r}{o}"
        # 共享角色
        for role, items in self.fillers.items():
            if any(a in x for x in items) and any(b in x for x in items):
                return f"{a}与{b}都出现在「{role}」绑定里"
        return None

    def facts_about(self, name: str) -> List[str]:
        out = []
        for s, r, o in self.triples:
            if name in s or name in o:
                out.append(f"{s}{r}{o}")
        return out[:6]
