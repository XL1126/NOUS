"""涌现内容生成：NERI 动力学 → 思维内容。

核心突破：Langevin SDE 的状态空间不是「背景噪声」，它**就是**思维本身。
- 双稳势的吸引子 = 原型概念
- 递归整合放大特定模式 = 注意聚焦
- 全局隐状态（视角）= 解释框架
- EPR/FDT = 当前认知状态

当 NERI 访问某个吸引子区域时，对应一个「原型概念」。
如果该区域没有已知概念，就**涌现一个新概念**。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class EmergentContent:
    """从 NERI 动力学涌现的内容。"""
    # 最近的已知概念（如果有）
    nearest_concept: str
    # 相似度（0-1）
    similarity: float
    # 是否是新涌现的概念
    is_novel: bool
    # 涌现概念的描述（如果是新的）
    emergent_description: str
    # 原始状态向量摘要
    state_summary: str
    # 认知状态标签
    cognitive_state: str  # active / stable / dormant / chaotic


class EmergenceMapper:
    """
    将 NERI 动力学映射到概念空间。

    原理：
    1. Langevin SDE 的状态向量 x ∈ R^n
    2. 通过随机投影降到概念空间维度
    3. 找最近的已知概念
    4. 如果距离太远 → 涌现新概念
    5. 递归整合的深度 = 注意聚焦强度
    6. EPR/FDT = 认知状态
    """

    def __init__(self, concept_space, rng: Optional[np.random.Generator] = None):
        self.space = concept_space
        self.rng = rng or np.random.default_rng(0)
        # 随机投影矩阵：NERI 状态 → 概念空间
        self.W_proj = None
        self.emergent_concepts: List[Dict[str, Any]] = []
        self.max_emergent = 50

    def _ensure_proj(self, n_vars: int) -> None:
        if self.W_proj is None or self.W_proj.shape[1] != n_vars:
            dim = self.space.dim
            self.W_proj = self.rng.standard_normal((dim, n_vars)) / np.sqrt(n_vars)

    def map(
        self,
        fast_state: np.ndarray,
        perspective: np.ndarray,
        epr: float,
        fdt: float,
        recursion_depth: int,
    ) -> EmergentContent:
        """
        将 NERI 状态映射到涌现内容。
        """
        n_vars = fast_state.size
        self._ensure_proj(n_vars)

        # 1. 投影到概念空间
        proj = self.W_proj @ fast_state
        norm = np.linalg.norm(proj)
        if norm > 1e-9:
            proj = proj / norm

        # 2. 视角调制：perspective 影响投影方向
        p_norm = np.linalg.norm(perspective)
        if p_norm > 0.01:
            # 视角越强，投影越偏向 perspective 指向的方向
            p_proj = np.resize(perspective, self.space.dim)
            p_proj = p_proj / (np.linalg.norm(p_proj) + 1e-9)
            alpha = float(np.clip(p_norm * 0.3, 0, 0.5))
            proj = (1 - alpha) * proj + alpha * p_proj
            proj = proj / (np.linalg.norm(proj) + 1e-9)

        # 3. 找最近的已知概念
        nearest = self.space.nearest(proj, k=3)
        if nearest:
            best_name, best_sim = nearest[0]
        else:
            best_name, best_sim = "", 0.0

        # 4. 判断是否涌现新概念
        # 阈值：相似度 < 0.15 视为新概念
        novelty_threshold = 0.15
        is_novel = best_sim < novelty_threshold

        emergent_desc = ""
        if is_novel:
            # 涌现新概念：用状态特征描述
            emergent_desc = self._describe_emergent(
                fast_state, perspective, epr, fdt, recursion_depth
            )
            # 注册到概念空间
            concept_name = f"emergent_{len(self.emergent_concepts)}"
            self.space.vocab[concept_name] = proj
            self.emergent_concepts.append({
                "name": concept_name,
                "description": emergent_desc,
                "state": proj[:8].tolist(),  # 存摘要
                "epr": epr,
                "fdt": fdt,
            })
            if len(self.emergent_concepts) > self.max_emergent:
                self.emergent_concepts = self.emergent_concepts[-self.max_emergent:]
            best_name = concept_name
            best_sim = 0.0

        # 5. 认知状态标签
        cognitive = self._cognitive_state(epr, fdt, p_norm, recursion_depth)

        # 6. 状态摘要
        summary = (
            f"状态能量={float(np.linalg.norm(fast_state)):.2f} "
            f"视角强度={p_norm:.2f} EPR={epr:.3f} FDT={fdt:.3f} "
            f"递归深度={recursion_depth}"
        )

        return EmergentContent(
            nearest_concept=best_name,
            similarity=best_sim,
            is_novel=is_novel,
            emergent_description=emergent_desc,
            state_summary=summary,
            cognitive_state=cognitive,
        )

    def _describe_emergent(
        self,
        fast: np.ndarray,
        perspective: np.ndarray,
        epr: float,
        fdt: float,
        depth: int,
    ) -> str:
        """描述涌现的新概念。"""
        energy = float(np.linalg.norm(fast))
        p_norm = float(np.linalg.norm(perspective))

        if epr > 0.5 and p_norm > 0.3:
            return f"一个活跃的、有视角的内在状态（能量{energy:.1f}，视角{p_norm:.1f}）"
        elif epr > 0.3:
            return f"一个平稳的内在动力学模式（能量{energy:.1f}）"
        elif p_norm > 0.4:
            return f"一个强烈的内在视角（视角{p_norm:.1f}）"
        elif depth >= 3:
            return f"一个深度递归整合的模式（深度{depth}）"
        else:
            return f"一个低能量的内在状态（能量{energy:.1f}）"

    def _cognitive_state(self, epr: float, fdt: float, p_norm: float, depth: int) -> str:
        """认知状态标签。"""
        if epr > 0.5 and fdt > 0.3:
            return "active"
        elif epr > 0.2:
            return "stable"
        elif epr < 0.05:
            return "dormant"
        else:
            return "transitional"

    def get_emergent_summary(self) -> str:
        """涌现概念摘要。"""
        if not self.emergent_concepts:
            return "尚未涌现新概念。"
        n = len(self.emergent_concepts)
        recent = self.emergent_concepts[-3:]
        descs = [c["description"] for c in recent]
        return f"已涌现 {n} 个新概念。最近：{'；'.join(descs)}"

    def to_thought(self, content: EmergentContent) -> str:
        """将涌现内容转化为思维语句。"""
        if content.is_novel:
            return f"（涌现）{content.emergent_description}"
        elif content.nearest_concept:
            return f"（关联）当前动力学接近「{content.nearest_concept}」（相似度{content.similarity:.2f}）"
        else:
            return f"（状态）{content.cognitive_state}：{content.state_summary}"
