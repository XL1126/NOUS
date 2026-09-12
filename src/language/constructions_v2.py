"""构式语法深化版：更多句式、更自然的表达、情绪/身体调制。

参考：Goldberg 构式语法；Tomasello 用法学习。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence
import numpy as np


@dataclass
class Construction:
    """构式：形式槽位 + 语用条件 + 情绪调制。"""
    name: str
    slots: List[str]
    frame: str
    when: str = "any"
    emotion_bias: Optional[str] = None  # 特定情绪时优先
    energy_bias: str = "any"  # low/medium/high


# ========== 构式库（大幅扩展） ==========

CONSTRUCTIONS: Dict[str, List[Construction]] = {
    "greet": [
        Construction("g1", ["act", "who", "open"], "{act}{who}{open}"),
        Construction("g2", ["act", "open"], "{act}{open}"),
        Construction("g3", ["who", "act", "hook"], "{who}{act}{hook}"),
        Construction("g4", ["act", "who", "topic"], "{act}{who}{topic}"),
        Construction("g5", ["somatic", "act", "open"], "{somatic}{act}{open}", emotion_bias="疲惫"),
        Construction("g6", ["act", "who"], "{act}{who}", energy_bias="low"),
    ],
    "remember": [
        Construction("r1", ["ack", "content"], "{ack}{content}"),
        Construction("r2", ["ack", "content", "note"], "{ack}{content}。{note}"),
        Construction("r3", ["ack", "content", "hook"], "{ack}{content}{hook}"),
        Construction("r4", ["content", "ack"], "{content}——{ack}", energy_bias="low"),
    ],
    "question": [
        Construction("q1", ["marker", "core"], "{marker}{core}"),
        Construction("q2", ["focus", "marker", "core"], "{focus}{marker}{core}"),
        Construction("q3", ["core", "hook"], "{core}{hook}"),
        Construction("q4", ["epistemic", "core"], "{epistemic}{core}", emotion_bias="紧张"),
        Construction("q5", ["core", "live"], "{core}{live}", energy_bias="high"),
    ],
    "status": [
        Construction("s1", ["ws", "body"], "{ws} {body}"),
        Construction("s2", ["body", "ws", "self"], "{body} {ws} {self}"),
        Construction("s3", ["body", "self"], "{body} {self}"),
        Construction("s4", ["ws", "body", "self", "neri"], "{ws} {body} {self} {neri}", energy_bias="high"),
    ],
    "open": [
        Construction("o1", ["heard", "thin"], "{heard}{thin}"),
        Construction("o2", ["stance", "hook"], "{stance}{hook}"),
        Construction("o3", ["thin", "invite"], "{thin}{invite}"),
        Construction("o4", ["heard", "thin", "somatic"], "{heard}{thin}{somatic}", emotion_bias="疲惫"),
        Construction("o5", ["emergent", "hook"], "{emergent}{hook}"),
    ],
    "identity": [
        Construction("i1", ["who", "how"], "{who}{how}"),
        Construction("i2", ["how", "who", "state"], "{how}{who}{state}"),
        Construction("i3", ["who", "how", "neri"], "{who}{how}{neri}", energy_bias="high"),
    ],
    "feeling": [
        Construction("f1", ["label", "reads"], "{label}{reads}"),
        Construction("f2", ["reads", "label", "policy"], "{reads}{label}{policy}"),
        Construction("f3", ["label", "reads", "somatic"], "{label}{reads}{somatic}", emotion_bias="疲惫"),
    ],
    "think": [
        Construction("t1", ["deliberate"], "{deliberate}"),
        Construction("t2", ["deliberate", "emergent"], "{deliberate}{emergent}"),
        Construction("t3", ["deliberate", "counterfactual"], "{deliberate}{counterfactual}"),
    ],
    "present": [
        Construction("p1", ["first_person", "attention", "stream"], "{first_person}{attention}{stream}"),
        Construction("p2", ["first_person", "markov"], "{first_person}{markov}"),
    ],
    "consciousness": [
        Construction("c1", ["disclaimer", "report", "level"], "{disclaimer}{report}{level}"),
        Construction("c2", ["disclaimer", "report", "neri", "level"], "{disclaimer}{report}{neri}{level}"),
    ],
    "counterfactual": [
        Construction("cf1", ["cf_line"], "{cf_line}"),
        Construction("cf2", ["cf_line", "hook"], "{cf_line}{hook}"),
    ],
    "future_self": [
        Construction("fs1", ["projection"], "{projection}"),
        Construction("fs2", ["projection", "hook"], "{projection}{hook}"),
    ],
    "stream_status": [
        Construction("ss1", ["stream", "profile", "neri"], "{stream}{profile}{neri}"),
    ],
    "autonomous": [
        Construction("au1", ["auto_report"], "{auto_report}"),
    ],
    "sleep": [
        Construction("sl1", ["consolidate"], "{consolidate}"),
    ],
    "topic": [
        Construction("tp1", ["shift"], "{shift}"),
    ],
    "recap": [
        Construction("rc1", ["recap"], "{recap}"),
    ],
    "preference": [
        Construction("pr1", ["prefs"], "{prefs}"),
    ],
    "praise": [
        Construction("pa1", ["thanks_da"], "{thanks_da}"),
    ],
    "thanks": [
        Construction("th1", ["thanks_ok"], "{thanks_ok}"),
    ],
    "apology": [
        Construction("ap1", ["apology_ok"], "{apology_ok}"),
    ],
    "farewell": [
        Construction("fw1", ["ack", "save", "bye"], "{ack}{save}{bye}"),
        Construction("fw2", ["save", "bye"], "{save}{bye}", energy_bias="low"),
    ],
    "help": [
        Construction("hp1", ["help_text"], "{help_text}"),
    ],
    "why": [
        Construction("wy1", ["explain"], "{explain}"),
    ],
}


# ========== 短语库（大幅扩展） ==========

PHRASES: Dict[str, List[str]] = {
    # 言语行为
    "act": ["你好。", "嗨。", "在。", "嗯，我在。", "来了。", "嗯？说吧。"],
    "who": ["我是{n}。", "{n}在这里。", "我是{n}，稳态循环在跑。"],
    "open": ["你想聊什么？", "直接说事就行。", "我在听。", "继续。"],
    "topic": ["上次我们说到「{t}」。", "话题栈顶还压着「{t}」。", "接着「{t}」也行。"],
    "hook": ["可以再补一句细节。", "要展开就说。", "也可以教我新事实。", "或者问我机制。"],
    "somatic": ["有点累，会说得短些。", "睡眠压力偏高，我收敛一点。", "能量紧，先给要点。"],
    # 教学
    "ack": ["记下了。", "已写入记忆。", "收到，存进语义了。", "这条进图了。"],
    "content": ["内容：{c}。", "条目「{c}」。", "「{c}」已进库。"],
    "note": ["之后会优先检索。", "会进情景与语义层。", "需要时我能用向量检索回放。"],
    # 问答
    "marker": ["这点我记录是：", "按已绑定信息：", "我的理解：", "在模型里："],
    "focus": ["就「{t}」来说，", "围绕「{t}」，", "若说「{t}」，"],
    "epistemic": ["我不太确定，", "置信度不够，", "可能的读法是："],
    "live": ["（活数据已附在状态里。）", "（实时读数见 /status。）"],
    "emergent": ["（内言：{e}）", "（涌现：{e}）"],
    # 状态
    "ws": ["点火{ig:.2f}(p={ip:.2f}) 熵{en:.2f} 广播[{bc}]。"],
    "body": ["能量{en:.2f} 睡压{sp:.2f} 压力{st:.2f} 社交{so:.2f} 好奇{cu:.2f}。"],
    "self": ["{goal}。发展度 {dev:.2f}。{phen}。维持动作：{act}。生命力 {vit:.2f}。"],
    "neri": ["NERI：EPR={epr:.3f} FDT={fdt:.3f} 视角={pers:.3f}。"],
    # 自我
    "disclaimer": ["我报告的是可测量的意识相关状态，不是哲学断言。"],
    "report": ["{core_report}"],
    "level": ["内核读数：{lvl}。"],
    # 内言
    "deliberate": ["{thought}"],
    "counterfactual": ["{cf}"],
    "projection": ["{proj}"],
    # 时间
    "first_person": ["我正意识到「{about}」。"],
    "attention": ["{attn}"],
    "stream": ["{stream}"],
    "markov": ["{markov}"],
    # 社交
    "thanks_ok": ["不客气。", "嗯，我在。", "收到你的谢意。", "应该的。"],
    "apology_ok": ["没关系。", "没事，继续说。", "可以继续。"],
    "thanks_da": ["谢谢。多巴胺现在 {da:.2f}，探索倾向会上一点。"],
    "shift": ["好，换话题。你想聊什么？", "行，切线。", "换。"],
    "recap": ["{recap}"],
    "prefs": ["{prefs}"],
    "auto_report": ["{auto}"],
    "consolidate": ["{consolidate}"],
    "help_text": ["你可以：直接中文聊天；教我「X是Y」；说我喜欢/我叫；问机制；/think 审慎思考；/status 状态；/sleep 巩固；/summary 自我摘要。"],
    "explain": ["{explain}"],
    "save": ["自传和记忆我会存档。", "这轮对话会写进情景层。", "状态会落到 runtime。"],
    "bye": ["下次见。", "先到这。", "回头聊。", "晚点见。"],
}


class Generator:
    """构式组装器：槽位填充，身体/SOMA/NERI 选构式。"""

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.recent: List[str] = []
        self.recent_open: List[str] = []

    def _pick(self, options: Sequence[str], prefer_fresh: bool = True) -> str:
        if not options:
            return ""
        if prefer_fresh and len(options) > 1 and self.recent_open:
            avoid = set(self.recent_open[-3:])
            fresh = [o for o in options if o not in avoid] or list(options)
            return str(fresh[int(self.rng.integers(0, len(fresh)))])
        return str(options[int(self.rng.integers(0, len(options)))])

    def select_construction(
        self,
        intent: str,
        emotion: str = "平静",
        energy: float = 0.7,
        neri_active: bool = False,
    ) -> Construction:
        """根据意图、情绪、能量、NERI 状态选择构式。"""
        bank = CONSTRUCTIONS.get(intent) or CONSTRUCTIONS["open"]

        # 情绪偏置
        emotion_matched = [c for c in bank if c.emotion_bias == emotion]
        if emotion_matched and float(self.rng.random()) < 0.5:
            bank = emotion_matched

        # 能量偏置
        if energy < 0.35:
            low = [c for c in bank if c.energy_bias == "low"]
            if low:
                bank = low
        elif energy > 0.7:
            high = [c for c in bank if c.energy_bias == "high"]
            if high and float(self.rng.random()) < 0.3:
                bank = high

        return bank[int(self.rng.integers(0, len(bank)))]

    def realize(
        self,
        intent: str,
        slots: Dict[str, str],
        *,
        persona: str = "NOUS",
        emotion: str = "平静",
        energy: float = 0.7,
        sleep: float = 0.2,
        stress: float = 0.2,
        neri_active: bool = False,
        neri_epr: float = 0.0,
        neri_fdt: float = 0.0,
        neri_perspective: float = 0.0,
    ) -> str:
        """从语义帧组装句子。"""
        cons = self.select_construction(intent, emotion, energy, neri_active)
        filled = dict(slots)

        def fill(key: str) -> str:
            if key in filled and filled[key]:
                return filled[key]
            opts = PHRASES.get(key, [])
            if not opts:
                return ""
            raw = self._pick(opts)
            return raw.format(
                n=persona, t=filled.get("topic", filled.get("focus", "这件事")),
                e=emotion, c=filled.get("content", ""),
                ig=filled.get("ignition", 0), ip=filled.get("ignition_prob", 0),
                en=energy, sp=sleep, st=stress,
                so=filled.get("social", 0.5), cu=filled.get("curiosity", 0.5),
                bc=filled.get("broadcast", "—"),
                goal=filled.get("goal", ""), dev=filled.get("development", 0),
                phen=filled.get("phenomenal", ""), act=filled.get("action", "idle"),
                vit=filled.get("vitality", 0.5),
                epr=neri_epr, fdt=neri_fdt, pers=neri_perspective,
                lvl=filled.get("level", ""), about=filled.get("about", "此刻"),
                attn=filled.get("attention", ""), stream=filled.get("stream", ""),
                markov=filled.get("markov", ""), core_report=filled.get("core_report", ""),
                thought=filled.get("thought", ""), cf=filled.get("cf", ""),
                proj=filled.get("projection", ""), recap=filled.get("recap", ""),
                prefs=filled.get("prefs", ""), auto=filled.get("auto", ""),
                consolidate=filled.get("consolidate", ""), explain=filled.get("explain", ""),
                da=filled.get("dopamine", 0.5), e=filled.get("emergent", ""),
            )

        text = cons.frame
        for slot in cons.slots:
            val = fill(slot)
            text = text.replace("{" + slot + "}", val)

        # 清理
        import re
        text = re.sub(r"\s+", " ", text).strip()
        text = text.replace("。。", "。").replace("，。", "。").replace("  ", " ")

        # 防复读
        if text in self.recent[-1:]:
            text = text.rstrip("。") + "，换个角度也行。"
        self.recent.append(text)
        if len(self.recent) > 10:
            self.recent = self.recent[-10:]
        return text
