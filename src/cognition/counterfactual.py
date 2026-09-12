"""反事实规划：如果…会怎样。

文献：counterfactual simulation / active inference 近似。
"""
from __future__ import annotations

from typing import List, Optional, Tuple


TEMPLATES = [
    "如果「{a}」不成立，我会先怀疑绑定而不是立刻改口。",
    "若把「{a}」换成对立说法，需要你再给一条证据。",
    "假如现在能量更低，我会缩短输出并优先休息目标（涉及「{a}」时尤其如此）。",
    "若预测误差继续升高，我会提高好奇驱动并追问「{a}」的锚点。",
    "假设对方纠正我，我会下调与「{a}」相关的程序权重并写入自我叙事。",
]


def plan_counterfactual(topic: str, novelty: float, energy: float,
                        rng=None) -> str:
    import numpy as np
    r = rng or np.random.default_rng()
    tpl = TEMPLATES[int(r.integers(0, len(TEMPLATES)))]
    line = tpl.format(a=topic or "当前说法")
    if novelty > 0.55:
        line += " 目前新颖度偏高，更倾向探索而不是断言。"
    if energy < 0.35:
        line += " 能量偏低，反事实模拟会压缩深度。"
    return line


def next_experiment(topic: str, known_facts: List[str]) -> str:
    """自主学习：提出下一步该验证/该问什么。"""
    if not known_facts:
        return f"关于「{topic or '这件事'}」我几乎没有绑定，请教我一条「X是Y」。"
    if len(known_facts) == 1:
        return f"我只有「{known_facts[0]}」；下一步想验证它是否导致别的现象。"
    return f"我已有 {len(known_facts)} 条相关绑定；下一步想检查它们是否互相一致。"
