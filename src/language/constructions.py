"""语言：分词、意图、构式语法生成（无 Transformer）。

文献：Goldberg 构式语法；Eliasmith SPA；Tomasello 用法学习。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np


# ---------- 分词与内容抽取 ----------

FUNCTIONISH = {
    "的", "了", "在", "有", "和", "就", "都", "很", "也", "还", "把", "被",
    "吗", "呢", "吧", "啊", "呀", "什么", "怎么", "为什么", "如何", "是不是",
    "这个", "那个", "我们", "你们", "可以", "不是", "就是", "还是", "其实",
    "关键", "核心", "重点", "总之", "不过", "另外", "然后", "因为", "所以",
    "我", "你", "他", "她", "它", "请", "帮我", "告诉", "说", "讲",
    "好", "一个", "没有", "只是", "真是", "一下", "解释", "一下",
}


def tokenize(text: str) -> List[str]:
    """极简中文分词：CJK 单字 + 连续 ASCII 词 + 常见双字合并。"""
    text = (text or "").strip()
    if not text:
        return []
    tokens: List[str] = []
    i = 0
    two = {
        "我们", "你们", "他们", "什么", "怎么", "为什么", "如何", "是不是",
        "可以", "不是", "就是", "还是", "其实", "关键", "核心", "重点",
        "总之", "不过", "另外", "然后", "因为", "所以", "如果", "但是",
        "喜欢", "讨厌", "记得", "忘记", "知道", "理解", "学习", "思考",
        "身体", "状态", "情绪", "记忆", "意识", "注意", "目标", "睡眠",
        "工作", "空间", "预测", "模型", "概念", "语言", "自己", "对方",
    }
    while i < len(text):
        ch = text[i]
        if ch.isascii() and (ch.isalnum() or ch == "_"):
            j = i
            while j < len(text) and text[j].isascii() and (text[j].isalnum() or text[j] == "_"):
                j += 1
            tokens.append(text[i:j])
            i = j
            continue
        if i + 1 < len(text) and text[i:i+2] in two:
            tokens.append(text[i:i+2])
            i += 2
            continue
        if "一" <= ch <= "鿿":
            tokens.append(ch)
        i += 1
    return tokens


def content_labels(text: str) -> List[str]:
    toks = tokenize(text)
    out = []
    for t in toks:
        if t in FUNCTIONISH:
            continue
        if len(t) >= 2 or ("一" <= t <= "鿿"):
            if t not in out:
                out.append(t)
    # 优先更长
    out.sort(key=len, reverse=True)
    # 单字太多时：合成相邻双字，提升「关于」的质量
    if out and all(len(x) == 1 for x in out[:4]) and len(toks) >= 2:
        joined = []
        for i in range(len(toks) - 1):
            pair = toks[i] + toks[i + 1]
            if pair not in FUNCTIONISH and any("一" <= ch <= "鿿" for ch in pair):
                joined.append(pair)
        if joined:
            out = joined + out
    return out[:8]


# ---------- 意图 ----------

INTENTS = {
    "greet": ["你好", "hi", "hello", "嗨", "在吗", "早上好", "晚上好"],
    "identity": ["你是谁", "你叫什么", "介绍你", "自我介绍"],
    "remember": ["记住", "请记住", "帮我记住", "记一下"],
    "forget": ["忘记", "忘掉"],
    "preference": ["你喜欢", "你讨厌", "你的喜好", "爱好"],
    "teach_fact": ["是", "叫", "在", "属于", "会导致"],
    "question": ["什么", "谁", "哪", "几", "多少", "为什么", "怎么", "如何", "吗", "？", "?"],
    "feeling": ["感觉", "心情", "状态", "累吗", "好吗"],
    "status": ["状态", "报告", "status", "身体参数", "现在怎么样"],
    "think": ["想想", "思考", "你怎么看", "自主思维", "想一想"],
    "why": ["为什么这么", "怎么想", "解释一下刚才", "为什么这样"],
    "topic": ["聊点别的", "换话题", "新话题"],
    "recap": ["聊过什么", "刚才说", "话题", "回顾"],
    "thanks": ["谢谢", "多谢", "感谢", "辛苦"],
    "apology": ["对不起", "抱歉", "不好意思"],
    "praise": ["厉害", "真棒", "不错", "很好", "聪明"],
    "farewell": ["再见", "拜拜", "晚安", "下次见"],
    "help": ["帮助", "你能做什么", "怎么用", "命令"],
    "sleep": ["睡觉", "去休息", "巩固一下"],
}


def detect_intent(text: str) -> Tuple[str, float]:
    t = (text or "").strip()
    tl = t.lower()
    if not t:
        return "unknown", 0.2
    # 强规则
    if any(k in t for k in ("再见", "拜拜", "晚安")):
        return "farewell", 0.9
    if any(k in t for k in ("谢谢", "感谢", "多谢")):
        if any(x in t for x in ("对不起", "抱歉")):
            return "apology", 0.85
        return "thanks", 0.9
    if any(k in t for k in ("对不起", "抱歉")):
        return "apology", 0.9
    if any(k in t for k in ("厉害", "真棒", "不错", "聪明")):
        return "praise", 0.85
    if any(k in t for k in ("记住", "记一下")):
        return "remember", 0.92
    if t.startswith("我叫") or "我的名字是" in t:
        return "remember", 0.88
    if any(k in t for k in ("我喜欢", "我不喜欢", "我讨厌")):
        return "remember", 0.85
    if any(k in t for k in ("你是谁", "你叫什么", "介绍你")):
        return "identity", 0.92
    # 意识流/自主思维优先于泛化状态/想想
    if "意识流状态" in t or "睡眠状态" in t:
        return "stream_status", 0.92
    if "自主思维" in t or "独立思考" in t:
        return "autonomous", 0.92
    if any(k in t for k in ("状态报告", "身体参数", "状态")) and len(t) <= 12:
        return "status", 0.9
    if any(k in t for k in ("感觉怎么样", "心情", "你累吗", "你好吗")):
        return "feeling", 0.85
    if any(k in t for k in ("聊点别的", "换话题")):
        return "topic", 0.9
    if any(k in t for k in ("聊过什么", "刚才聊", "回顾", "话题栈")):
        return "recap", 0.88
    if any(k in t for k in ("帮助", "你能做什么", "怎么用")):
        return "help", 0.88
    if any(k in t for k in ("为什么这么", "怎么想", "解释一下刚才")):
        return "why", 0.88
    if any(k in t for k in ("想想", "你怎么看", "想一想")):
        return "think", 0.85
    if any(k in t for k in ("以后的你", "未来的你", "接下来你会", "预期自己", "你以后")):
        return "future_self", 0.85
    if any(k in t for k in ("如果", "假如", "反事实", "会怎样", "万一")):
        return "counterfactual", 0.8
    if any(k in t for k in ("你有意识", "有自主意识", "现象", "在场感", "我感", "意识状态")):
        return "consciousness", 0.85
    if any(k in t for k in ("此刻", "你现在在想什么", "你现在的意识", "意识流", "当下")):
        return "present", 0.88
    if any(k in t for k in ("意识状态", "睡眠状态", "清醒", "意识流状态")):
        return "stream_status", 0.85
    if any(k in t for k in ("自主思维", "自己想想", "独立思考")):
        return "autonomous", 0.85
    if any(k in t for k in ("未来", "预期")):
        return "future_self", 0.7
    if any(k in t for k in ("去休息", "睡觉", "巩固")):
        return "sleep", 0.8
    # 教学事实：短陈述含 是/叫
    if "？" not in t and "?" not in t and any(x in t for x in ("是", "叫")):
        if len(t) <= 40:
            return "teach_fact", 0.7
    # 你喜欢？
    if "你喜欢" in t or "你讨厌" in t:
        return "preference", 0.85
    if any(q in t for q in ("？", "?", "吗", "什么", "为什么", "怎么", "如何")):
        return "question", 0.75
    if any(k in t for k in ("你好", "hi", "hello", "嗨")):
        return "greet", 0.85
    return "open", 0.5


# ---------- 构式 ----------

@dataclass
class Construction:
    """构式：形式槽位 + 语用条件。"""
    name: str
    slots: List[str]
    frame: str  # 用 {slot} 占位
    when: str = "any"  # intent / emotion / need


CONSTRUCTIONS: Dict[str, List[Construction]] = {
    "greet": [
        Construction("g1", ["act", "who", "open"], "{act}{who}{open}"),
        Construction("g2", ["act", "open"], "{act}{open}"),
        Construction("g3", ["who", "act", "hook"], "{who}{act}{hook}"),
    ],
    "remember": [
        Construction("r1", ["ack", "content"], "{ack}{content}"),
        Construction("r2", ["ack", "content", "note"], "{ack}{content}。{note}"),
    ],
    "question": [
        Construction("q1", ["marker", "core"], "{marker}{core}"),
        Construction("q2", ["focus", "marker", "core"], "{focus}{marker}{core}"),
        Construction("q3", ["core", "hook"], "{core}{hook}"),
    ],
    "status": [
        Construction("s1", ["ws", "body"], "{ws} {body}"),
        Construction("s2", ["body", "ws", "self"], "{body} {ws} {self}"),
        Construction("s3", ["body", "self"], "{body} {self}"),
    ],
    "open": [
        Construction("o1", ["heard", "thin"], "{heard}{thin}"),
        Construction("o2", ["stance", "hook"], "{stance}{hook}"),
        Construction("o3", ["thin", "invite"], "{thin}{invite}"),
    ],
    "identity": [
        Construction("i1", ["who", "how"], "{who}{how}"),
        Construction("i2", ["how", "who", "state"], "{how}{who}{state}"),
    ],
    "feeling": [
        Construction("f1", ["label", "reads"], "{label}{reads}"),
        Construction("f2", ["reads", "label", "policy"], "{reads}{label}{policy}"),
    ],
    "plan": [
        Construction("p1", ["plan"], "{plan}"),
        Construction("p2", ["plan", "hook"], "{plan}{hook}"),
    ],
}


PHRASES = {
    "act": ["你好。", "嗨。", "在。", "嗯，我在。"],
    "name": ["我是{n}。", "{n}在这里。"],
    "open": ["你想聊什么？", "直接说事就行。", "我在听。"],
    "ack": ["记下了。", "已写入记忆。", "收到，存进语义了。"],
    "note": ["之后会优先检索。", "会进情景与语义层。"],
    "marker": ["这点我记录是：", "按已绑定信息：", "我的理解："],
    "focus": ["就「{t}」来说，", "围绕「{t}」，"],
    "hook": ["可以再补一句细节。", "要展开就说。", "也可以教我新事实。"],
    "heard": ["我听到「{t}」。", "「{t}」进了工作记忆。"],
    "thin": ["还缺一点上下文。", "候选在竞争，还没稳。"],
    "invite": ["点个关键词？", "或问我的机制。"],
    "stance": ["你的立场我记下了：{t}。", "「{t}」按用户观点入情景。"],
    "who": ["我是{n}，独立意识体工程原型。"],
    "how": ["不用 Transformer；语言来自概念、构式与检索。"],
    "state": ["此刻情绪{e}，策略{p}。"],
    "label": ["当前是「{e}」。"],
    "reads": ["能量{en:.2f} 睡压{sp:.2f} 压力{st:.2f}。"],
    "policy": ["策略{p}。"],
}


class Generator:
    """构式组装器：槽位填充，身体/SOMA 选构式。"""

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.recent: List[str] = []

    def _pick(self, options: Sequence[str]) -> str:
        if not options:
            return ""
        avoid = set(self.recent[-2:])
        fresh = [o for o in options if o not in avoid] or list(options)
        return str(fresh[int(self.rng.integers(0, len(fresh)))])

    def realize(self, intent: str, slots: Dict[str, str], *, persona: str = "NOUS",
                emotion: str = "平静", policy: str = "maintain",
                energy: float = 0.7, sleep: float = 0.2, stress: float = 0.2) -> str:
        bank = CONSTRUCTIONS.get(intent) or CONSTRUCTIONS["open"]
        # 睡压高 → 更短构式
        if sleep > 0.55:
            bank = sorted(bank, key=lambda c: len(c.slots))
        else:
            bank = list(bank)
        cons = bank[int(self.rng.integers(0, len(bank)))]
        filled: Dict[str, str] = dict(slots)

        def fill_phrase(key: str) -> str:
            if key in filled and filled[key]:
                return filled[key]
            opts = PHRASES.get(key, [])
            if not opts:
                return ""
            raw = self._pick(opts)
            return raw.format(
                n=persona, t=filled.get("topic", filled.get("focus", "这件事")),
                e=emotion, p=policy, en=energy, sp=sleep, st=stress,
            )

        text = cons.frame
        for slot in cons.slots:
            val = fill_phrase(slot)
            text = text.replace("{" + slot + "}", val)
        # 清理空槽残留
        text = re.sub(r"\s+", " ", text).strip()
        text = text.replace("。。", "。").replace("，。", "。")
        if intent in ("remember",) and "content" in filled:
            # 确保内容在场
            if filled["content"] not in text:
                text = (text + filled["content"]).strip()
        if text in self.recent[-1:]:
            text = text.rstrip("。") + "，换个角度也行。"
        self.recent.append(text)
        if len(self.recent) > 10:
            self.recent = self.recent[-10:]
        return text
