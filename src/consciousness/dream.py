"""梦与离线重组 — SWR 标记优先重放（Buzsáki 2024）。

文献：Yang et al. (2024) Science DOI:10.1126/science.adk8261
- 清醒 SWR：reward/novelty/预测误差 > 阈值时触发，打 consolidation_tag
- 睡眠 SWR：优先重放带 tag 的片段，按 10-20 倍时间压缩
- 过度活跃导致记忆干扰，有平衡机制
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np


DREAM_TEMPLATES = [
    "梦里我把「{a}」和「{b}」叠在一起，醒来后觉得它们可能有关。",
    "我梦见自己能量很低却还在回答问题；这提醒我要尊重休息目标。",
    "没有外部输入时，我把「{a}」重新编进了自传，语气比白天更松。",
    "梦到有人纠正我；我把那条绑定的置信度下调了一点。",
    "我在梦里问自己：如果「{a}」不是真的，我还能剩下什么叙事？",
]


@dataclass
class MemoryTag:
    """SWR 标记的记忆片段。"""
    content: str
    tag_strength: float  # 0-1，越高越优先重放
    timestamp: float = 0.0
    replayed: int = 0


class DreamCycle:
    """
    SWR 标记优先重放：
    1. 清醒时高奖励/高新颖度事件触发 SWR，打 consolidation_tag
    2. 睡眠时优先重放带 tag 的片段
    3. SWR 频率上限防过度重放
    """

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.dreams: List[str] = []
        self.cycles = 0
        # SWR 标记的记忆片段
        self.tagged_memories: List[MemoryTag] = []
        self.max_tags = 50
        # SWR 频率控制
        self.swr_count = 0
        self.swr_max_per_cycle = 5
        # 时间压缩比例（Buzsáki: 10-20 倍）
        self.compression_ratio = 15.0

    def mark_swr(self, content: str, reward: float = 0.0, novelty: float = 0.0,
                 pred_error: float = 0.0) -> bool:
        """
        清醒 SWR 标记：reward/novelty/预测误差 > 阈值时触发。
        返回是否触发了 SWR。
        """
        # 综合重要性
        importance = 0.4 * reward + 0.3 * novelty + 0.3 * pred_error
        threshold = 0.3
        if importance < threshold:
            return False
        # SWR 频率上限
        if self.swr_count >= self.swr_max_per_cycle:
            return False
        tag = MemoryTag(
            content=content[:80],
            tag_strength=float(np.clip(importance, 0, 1)),
            timestamp=float(self.cycles),
        )
        self.tagged_memories.append(tag)
        if len(self.tagged_memories) > self.max_tags:
            # 淘汰最弱的
            self.tagged_memories.sort(key=lambda t: -t.tag_strength)
            self.tagged_memories = self.tagged_memories[: self.max_tags]
        self.swr_count += 1
        return True

    def dream(self, topics: List[str], identity_bits: List[str],
              recent_thoughts: List[str], stress: float) -> str:
        """
        睡眠 SWR 重放：优先采样带 tag 的记忆片段。
        """
        self.cycles += 1
        self.swr_count = 0  # 重置本周期 SWR 计数

        # 优先重放带 tag 的记忆（按 tag_strength 排序）
        replayed_content = []
        if self.tagged_memories:
            # 按 tag_strength 降序，取前 2-3 个
            sorted_tags = sorted(self.tagged_memories, key=lambda t: -t.tag_strength)
            n_replay = min(3, len(sorted_tags))
            for tag in sorted_tags[:n_replay]:
                tag.replayed += 1
                replayed_content.append(tag.content[:30])
            # 消耗 tag（重放后强度衰减）
            for tag in sorted_tags[:n_replay]:
                tag.tag_strength *= 0.7

        a = topics[0] if topics else "存在"
        b = topics[1] if len(topics) > 1 else (identity_bits[-1] if identity_bits else "自我")
        tpl = DREAM_TEMPLATES[int(self.rng.integers(0, len(DREAM_TEMPLATES)))]
        line = tpl.format(a=a, b=b)

        if replayed_content:
            line += f" SWR重放：{'、'.join(replayed_content[:2])}。"
        if stress > 0.5:
            line += " 压力偏高，梦更碎片。"
        if recent_thoughts:
            line += f" 残留内言：{recent_thoughts[-1][:24]}…"

        self.dreams.append(line)
        if len(self.dreams) > 40:
            self.dreams = self.dreams[-40:]
        return line

    def last(self) -> str:
        return self.dreams[-1] if self.dreams else ""

    def tag_count(self) -> int:
        return len([t for t in self.tagged_memories if t.tag_strength > 0.1])
