"""发展阶段：前语言 → 独词句 → 双词 → 多轮。

文献：Tomasello 用法学习；儿童语言发展阶段的工程简化。
不是复现儿童语言学全文，而是控制语言输出复杂度与学习策略。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class StageProfile:
    name: str
    min_development: float
    max_clauses: int
    allow_questions: bool
    allow_teach_ack: bool
    vocab_bonus: float


STAGES: List[StageProfile] = [
    StageProfile("sensorimotor", 0.0, 1, False, False, 0.0),
    StageProfile("holophrase", 2.0, 1, False, True, 0.1),
    StageProfile("two_word", 5.0, 2, False, True, 0.3),
    StageProfile("telegraphic", 10.0, 2, True, True, 0.5),
    StageProfile("conversational", 20.0, 4, True, True, 1.0),
    StageProfile("reflective", 40.0, 5, True, True, 1.2),
]


def stage_for(development: float) -> StageProfile:
    chosen = STAGES[0]
    for s in STAGES:
        if development >= s.min_development:
            chosen = s
    return chosen


def clamp_output(text: str, stage: StageProfile, intent: str = "") -> str:
    """按阶段压短输出：早期更像独词句/电报句。教学/内省不强制截断。"""
    if not text:
        return text
    if intent in ("remember", "teach_fact", "think", "counterfactual", "status", "why"):
        return text
    if stage.name == "sensorimotor":
        core = text.replace("。", " ").replace("，", " ").split()
        if core:
            return core[0][:12]
        return text[:8]
    if stage.name == "holophrase":
        parts = [p for p in text.replace("。", "。|").split("|") if p.strip()]
        return (parts[0] if parts else text)[:24]
    if stage.name == "two_word":
        if len(text) > 48:
            return text[:46] + "…"
    if stage.name == "telegraphic" and len(text) > 80:
        return text[:76] + "…"
    return text


def can_do(stage: StageProfile, skill: str) -> bool:
    if skill == "question":
        return stage.allow_questions
    if skill == "teach_ack":
        return stage.allow_teach_ack
    if skill == "reflect":
        return stage.name in ("conversational", "reflective")
    return True
