"""NOUS Mind — 闭合心智循环。

回合：
  感知分词 → 概念编码 → 预测误差 → 工作空间竞争 → 广播
  → 记忆检索/教学写入 → 目标与身体调节 → 情绪构造
  → 构式生成回复 → 写回记忆 → 元认知

无 Transformer。意识=可报告的工作空间+预测+自我维护的工程代理。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .soma.body import Soma, SomaState
from .concepts.space import ConceptSpace, SemanticGraph
from .workspace.global_ws import GlobalWorkspace, Broadcast
from .predictive.model import PredictiveModel
from .memory.systems import MemoryBank, MemoryItem
from .language.constructions import (
    Generator, tokenize, content_labels, detect_intent,
)
from .self_model.meta import (
    Goal, GoalStack, MetaCognition, SelfModel, OtherModel, InnerSpeech,
)
from .knowledge.seed import SEED_KNOWLEDGE
from .development import stage_for, clamp_output, can_do
from .cognition.counterfactual import plan_counterfactual, next_experiment
from .neural.race import SpikeRace
from .consciousness.phenomenology import Phenomenology
from .consciousness.autopoiesis import Autopoiesis
from .consciousness.dream import DreamCycle
from .consciousness.core import ConsciousnessCore, ConsciousMoment
from .consciousness.self_pole import SelfPole
from .consciousness.temporal import TemporalMind
from .consciousness.stream import ConsciousnessStream, ConsciousState
from .consciousness.neri import NERI
from .consciousness.emergence import EmergenceMapper
from .consciousness.fly_brain import FlyBrainInspired
from .agency.actions import ActionLoop
from .agency.boundary import SelfWorldBoundary


def split_items(text: str) -> List[str]:
    parts = [p.strip() for p in re.split(r"[和、，,与跟及]", text or "") if p.strip()]
    return parts


def induce_triple(text: str) -> Optional[Tuple[str, str, str]]:
    t = text.strip()
    if any(q in t for q in ("？", "?", "吗", "呢")):
        return None
    for opener in ("其实", "关键", "我觉得", "我认为", "总之"):
        if t.startswith(opener):
            return None
    m = re.match(r"(.{1,10}?)是(.{1,20})", t)
    if m:
        s, o = m.group(1).strip("，。！？ "), m.group(2).strip("，。！？ ")
        if s and o and s not in ("我", "你", "这", "那") and len(s) >= 1:
            # 单字中文实体（猫/水）允许；功能字拒绝
            if len(s) == 1 and s in set("的了在有和就都很也还把被吗呢吧"):
                return None
            return s, "是", o
    m = re.match(r"(?:我|你)?(.{0,6}?)叫(.{1,10})", t)
    if m:
        s = (m.group(1) or "本体").strip("，。！？ ") or "本体"
        o = m.group(2).strip("，。！？ ")
        if s and o:
            return s, "叫", o
    return None


@dataclass
class TurnResult:
    reply: str
    intent: str
    emotion: str
    confidence: float
    ignition: float
    novelty: float
    policy: str
    goal: str
    broadcast: Dict[str, float]
    body: Dict[str, float]
    thought: str = ""
    learned: str = ""
    focus: str = ""
    phenomenal: Dict[str, float] = None  # type: ignore
    maintenance: str = "idle"
    vitality: float = 1.0

    def __post_init__(self):
        if self.phenomenal is None:
            self.phenomenal = {}


class NousMind:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        persona = cfg.get("persona") or {}
        self.name = persona.get("name", "NOUS")
        self.identity = persona.get("identity", "独立意识体工程原型")
        seed = int(cfg.get("seed", 42))
        self.rng = np.random.default_rng(seed)

        spa_dim = int(cfg.get("dim", 512))
        self.space = ConceptSpace(spa_dim, seed=seed)
        self.graph = SemanticGraph(self.space)
        self.soma = Soma(rng=self.rng)
        self.ws = GlobalWorkspace(rng=self.rng)
        self.pred = PredictiveModel(dim=64, seed=seed)
        self.mem = MemoryBank(self.space)
        self.goals = GoalStack()
        self.meta = MetaCognition()
        self.self_model = SelfModel(self.name)
        self.self_model.add_identity(self.identity)
        self.other = OtherModel()
        self.inner = InnerSpeech(rng=self.rng)
        self.gen = Generator(rng=self.rng)
        self.race = SpikeRace(n_pop=64, seed=seed)
        self.use_spike_race = bool(cfg.get("use_spike_race", True))
        self.phen = Phenomenology()
        self.auto_p = Autopoiesis(rng=self.rng)
        self.dreams = DreamCycle(rng=self.rng)
        self.maintenance_action = "idle"
        self.actions = ActionLoop(rng=self.rng)
        self.boundary = SelfWorldBoundary()
        self.core = ConsciousnessCore(rng=self.rng)
        self.last_moment: Optional[ConsciousMoment] = None
        # 连续意识流
        self.stream = ConsciousnessStream(
            soma=self.soma,
            workspace=self.ws,
            core=self.core,
            dreams=self.dreams,
            inner_speech=self.inner,
            rng=self.rng,
        )
        # NERI：非平衡递归整合器（现象意识候选架构）
        # 规模：1024 变量稀疏耦合（交互速度优先；2048/4096 可选）
        self.neri = NERI(n_vars=1024, n_integrated=128, n_latent=16, rng=self.rng)
        # 涌现内容生成：NERI 动力学 → 思维内容
        self.emergence = EmergenceMapper(self.space, rng=self.rng)
        self.last_emergent_thought = ""
        # 果蝇脑启发：连接组原理增强
        self.fly_brain = FlyBrainInspired(rng=self.rng)
        # SOI 线索缓存（用于自我归属贝叶斯更新）
        self._soi_appearance = 0.5
        self._soi_contiguity = 0.5
        self._soi_perspective = 0.5

        self.turn = 0
        self.last_user = ""
        self.last_reply = ""
        self.last_intent = ""
        self.focus = ""
        self.topic = "对话"
        self.user_profile: Dict[str, str] = {}
        self.runtime_knowledge: List[Tuple[str, str]] = []
        self.last_result: Optional[TurnResult] = None
        self.last_thought = ""
        self.development = float(cfg.get("development", 22.0))  # 默认已过电报期，可多轮
        traits = persona.get("traits") or {}
        if "curiosity" in traits:
            self.soma.state.curiosity = float(np.clip(traits["curiosity"], 0.05, 1.0))
        if "warmth" in traits:
            self.soma.state.social = float(np.clip(0.35 + 0.4 * traits["warmth"], 0.05, 1.0))

        self._bootstrap()

    def _bootstrap(self) -> None:
        for keys, gloss in SEED_KNOWLEDGE:
            self.mem.semantic.learn(keys[0], gloss, keys)
            self.space.pointer(keys[0])
        self.self_model.add_identity("我用身体驱动、预测与全局工作空间组织经验")
        self.goals.push(Goal("维持稳态并理解你", 0.6, "intrinsic"))
        self.mem.auto.record("诞生：NOUS 初始化")

    # ---------- 感知与编码 ----------
    def _encode(self, text: str) -> Tuple[List[str], np.ndarray, List[str]]:
        tokens = tokenize(text)
        labels = content_labels(text)
        if not labels:
            # 回退时也过滤功能词
            from .language.constructions import FUNCTIONISH
            labels = [t for t in tokens[:6] if t not in FUNCTIONISH] or ["ambient"]
        for lab in labels:
            self.space.pointer(lab)
        vec = self.space.encode(labels)
        return tokens, vec, labels

    def _observe_world(self, vec: np.ndarray, labels: List[str], intent_conf: float) -> None:
        obs = np.zeros(64)
        for i, lab in enumerate(sorted(set(labels))[:16]):
            v = self.space.pointer(lab)
            obs[i % 64] += float(np.dot(v[:8], np.arange(1, 9)) % 1.0)
        obs[-1] = intent_conf
        self.pred.observe(obs, learning_rate=0.08 * self.soma.learning_gain())

    def _workspace_offer(self, labels: List[str], vec: np.ndarray, extra: Dict[str, float]) -> Broadcast:
        cands: Dict[str, float] = {}
        for lab in labels:
            # 与已知语义的匹配度抬升
            boost = 0.0
            if lab in self.mem.semantic.facts:
                boost += 0.15
            if any(lab in k for k, _ in self.runtime_knowledge):
                boost += 0.1
            cands[lab] = float(0.35 + 0.5 * abs(float(np.dot(vec, self.space.pointer(lab)))) + boost)
        for k, v in extra.items():
            cands[k] = float(v)
        # 元标签降权
        for m in ("novelty", "need", "goal"):
            if m in cands:
                cands[m] *= 0.4
        # 可选脉冲竞争：胜者概念获得额外增益
        if self.use_spike_race and labels:
            winners = self.race.compete(labels, {lab: cands.get(lab, 0.4) for lab in labels})
            for lab, rate in winners[:3]:
                if lab in cands and rate > 0.2:
                    cands[lab] = float(cands[lab] * (1.0 + 0.35 * rate))
        self.ws.offer(cands)
        return self.ws.step(
            global_gain=self.soma.attention_gain(),
            fatigue=0.7 + 0.3 * self.soma.state.energy,
        )

    # ---------- 教学与归纳 ----------
    def _teach_fact(self, text: str, labels: List[str]) -> str:
        triple = induce_triple(text)
        name_m = re.match(r"我叫(.{1,12})", text.strip())
        if name_m:
            name = name_m.group(1).strip("，。！？ ")
            self.user_profile["名字"] = name
            self.mem.semantic.learn("用户名字", name, ["名字", "用户", name])
            self.graph.bind(SemanticGraph.ROLE_NAME, name)
            self.other.name = name
            self.soma.event("teach", 0.4)
            return f"记住了，你叫{name}。"
        if "喜欢" in text and "？" not in text and "吗" not in text:
            obj = text.split("喜欢", 1)[-1].strip("，。！？ 了")
            if obj:
                self.user_profile["喜欢"] = obj
                for p in split_items(obj):
                    self.graph.bind(SemanticGraph.ROLE_LIKE, p)
                self.mem.semantic.learn("用户喜欢", obj, ["喜欢", "用户"])
                self.soma.event("teach", 0.35)
                return f"记下了：你喜欢{obj}。"
        if ("讨厌" in text or "不喜欢" in text) and "？" not in text:
            key = "讨厌" if "讨厌" in text else "不喜欢"
            obj = text.split(key, 1)[-1].strip("，。！？ 了")
            if obj:
                self.user_profile["讨厌"] = obj
                for p in split_items(obj):
                    self.graph.bind(SemanticGraph.ROLE_DISLIKE, p)
                self.soma.event("teach", 0.3)
                return f"记下了：你不喜欢{obj}。"
        if triple:
            s, r, o = triple
            self.graph.add_triple(s, r, o)
            self.mem.semantic.learn(s, f"{s}{r}{o}", [s, o, r])
            self.runtime_knowledge.append((s, f"{s}{r}{o}"))
            if len(self.runtime_knowledge) > 300:
                self.runtime_knowledge = self.runtime_knowledge[-300:]
            self.mem.auto.record(f"学到：{s}{r}{o}")
            self.soma.event("understood", 0.25)
            return f"记下了：{s}{r}{o}。"
        # 无法结构化：整句作经验
        if labels:
            self.mem.semantic.learn(labels[0], text[:80], labels)
            self.runtime_knowledge.append((labels[0], text[:80]))
            return f"已把「{labels[0]}」相关表述存入经验。"
        return "我还没抓住可结构化的事实，可以说成「X是Y」。"

    def _lookup(self, text: str, labels: List[str], vec: np.ndarray) -> str:
        generic = {"是什么", "什么", "怎么", "如何", "为什么", "是", "吗", "呢", "解释", "一下"}
        # 精确/子串知识：必须命中非泛化键
        best_score, best_gloss = 0, ""
        for keys, gloss in SEED_KNOWLEDGE:
            score = 0
            specific = 0
            for k in keys:
                if not k:
                    continue
                hit = k in text or k in labels or any(k in lab for lab in labels)
                if not hit:
                    continue
                if k in generic:
                    score += 1
                else:
                    score += 2
                    specific += 1
            if specific and score > best_score:
                best_score, best_gloss = score, gloss
        if best_gloss:
            return best_gloss
        # runtime
        best_s, best_a = 0, ""
        for key, gloss in self.runtime_knowledge:
            s = sum(1 for ch in key if ch and ch in text)
            if s > best_s:
                best_s, best_a = s, gloss
        if best_s >= 2 and best_a:
            return best_a
        # semantic vector
        for concept, gloss, score in self.mem.semantic.query(vec, k=3):
            if score >= 0.28:
                return gloss
        # episodic
        eps = self.mem.episodic.retrieve(vec, k=1)
        if eps and eps[0].kind == "user":
            return f"相关情景：{eps[0].text[:40]}"
        return ""

    def _neri_to_language(self, neri_state) -> Dict[str, Any]:
        """
        突破：NERI 非平衡动力学 → 语言调制参数 + 涌现内容。

        EPR 高 → 活跃、展开
        FDT 违反大 → 惊讶、追问
        视角强度高 → 自信、第一人称
        NESS 不稳定 → 犹豫、简短
        涌现概念 → 直接成为思维内容
        """
        epr = getattr(neri_state, "epr", 0.0)
        fdt = getattr(neri_state, "fdt_violation", 0.0)
        slow = getattr(neri_state, "slow", np.zeros(4))
        p_norm = float(np.linalg.norm(slow))
        fast = getattr(neri_state, "fast", np.zeros(32))
        depth = getattr(neri_state, "recursion_depth", 2)

        # 涌现内容：NERI 动力学 → 概念空间
        emergent = self.emergence.map(
            fast_state=fast if isinstance(fast, np.ndarray) else np.zeros(32),
            perspective=slow if isinstance(slow, np.ndarray) else np.zeros(4),
            epr=epr,
            fdt=fdt,
            recursion_depth=depth,
        )
        emergent_thought = self.emergence.to_thought(emergent)
        self.last_emergent_thought = emergent_thought

        return {
            "epr": epr,
            "fdt": fdt,
            "perspective": p_norm,
            "activity": float(np.clip(epr / 5.0, 0, 1)),
            "surprise": float(np.clip(fdt / 3.0, 0, 1)),
            "confidence": float(np.clip(p_norm / 8.0, 0, 1)),
            "hesitation": float(np.clip(1.0 - p_norm / 8.0, 0, 1)),
            # 涌现内容
            "emergent": emergent,
            "emergent_thought": emergent_thought,
            "cognitive_state": emergent.cognitive_state,
        }

    def _apply_neri_modulation(self, reply: str, neri_mod: Dict[str, Any]) -> str:
        """
        用 NERI 动力学调制回复的语言风格。
        这是「非平衡物理过程 → 语言」的直接耦合。
        """
        if not reply or not neri_mod:
            return reply

        activity = neri_mod.get("activity", 0.5)
        surprise = neri_mod.get("surprise", 0.3)
        confidence = neri_mod.get("confidence", 0.5)
        hesitation = neri_mod.get("hesitation", 0.3)

        # 选择最多 1-2 个调制，避免堆砌
        candidates = []
        if activity > 0.65:
            candidates.append(("active", [
                "我这边动力学很活跃。",
                "非平衡态让我更愿意展开。",
                "熵产生偏高，我想多说一点。",
                "内部涨落很强，表达欲上来了。",
            ]))
        if surprise > 0.55:
            candidates.append(("surprise", [
                "这让我有点意外。",
                "预测误差偏高，我想再确认。",
                "FDT 违反明显，我需要更多信息。",
            ]))
        if confidence > 0.65:
            candidates.append(("confident", [
                "我对此有较强的内在把握。",
                "视角层很稳，我倾向相信这个判断。",
                "内在参照系支持这个结论。",
            ]))
        if hesitation > 0.65 and activity < 0.4:
            candidates.append(("hesitant", [
                "不过我也不太确定。",
                "这只是当前视角，可能有偏差。",
                "视角层还不够稳，仅供参考。",
            ]))

        # 随机选 1-2 个
        if candidates:
            n = 1 if len(candidates) == 1 or float(self.rng.random()) < 0.6 else 2
            chosen = self.rng.choice(len(candidates), size=n, replace=False)
            parts = [reply]
            for idx in chosen:
                _, opts = candidates[idx]
                parts.append(self.rng.choice(opts))
            reply = " ".join(parts)

        # 突破：涌现内容直接进入回复
        emergent_thought = neri_mod.get("emergent_thought", "")
        emergent = neri_mod.get("emergent")
        if emergent and emergent.is_novel and float(self.rng.random()) < 0.4:
            # 40% 概率：涌现的新概念直接成为内言
            reply += f" （内言：{emergent_thought}）"
        elif emergent_thought and float(self.rng.random()) < 0.15:
            # 15% 概率：关联概念作为补充
            reply += f" （{emergent_thought}）"

        return reply

    def _resolve_anaphora(self, text: str) -> str:
        t = text.strip()
        if not any(x in t for x in ("它", "这个", "那个", "前者", "后者", "这事儿")):
            return t
        top = self.topic
        if "前者" in t and self.focus and self.focus != top:
            t = t.replace("前者", self.focus, 1)
        if "后者" in t and top and top not in ("对话", "ambient"):
            t = t.replace("后者", top, 1)
        for p in ("这个", "那个", "这事儿", "它"):
            if p in t and top and top not in ("对话", "ambient", "新话题"):
                t = t.replace(p, top, 1)
                break
        return t

    # ---------- 回合 ----------
    def perceive_and_respond(self, user_text: str) -> TurnResult:
        self.turn += 1
        self.soma.step(1.0)
        raw_in = user_text
        # 跨体对话：剥掉说话人前缀，避免被当成事实教学
        speaker_tag = ""
        m_sp = __import__("re").match(r"^\[([^\]]+)\]\s*(.*)$", raw_in.strip())
        if m_sp:
            speaker_tag = m_sp.group(1)
            raw_in = m_sp.group(2)
            self.soma.event("social", 0.15)
        raw = self._resolve_anaphora(raw_in)
        intent, iconf = detect_intent(raw)
        tokens, vec, labels = self._encode(raw)
        self._observe_world(vec, labels, iconf)

        need = self.soma.dominant_need()
        self.goals.retarget_from_need(need)
        extra = {
            "novelty": float(self.pred.novelty),
            "need": 0.3,
        }
        bc = self._workspace_offer(labels, vec, extra)
        focus = bc.labels[0] if bc.labels else (labels[0] if labels else "ambient")
        # 优先更长内容词，避免「解/到」等单字当焦点
        contentish = [x for x in labels if len(x) >= 2]
        if contentish:
            focus = contentish[0]
        elif focus in ("novelty", "need", "ambient", "") and labels:
            focus = labels[0]
        self.focus = focus
        if focus not in ("ambient", "novelty", "need") and len(focus) >= 2:
            self.topic = focus

        # 用户报告疲劳 → 身体传染
        if any(x in raw for x in ("累", "困", "疲惫", "加班", "熬夜", "想睡")):
            self.soma.event("user_fatigue", 0.55)
            self.soma.event("load", 0.15)
            self.auto_p.step(self.soma.state)
            self.maintenance_action = self.auto_p.choose_maintenance_action()
            if intent in ("open", "question") and not any(
                x in raw for x in ("是什么", "定义", "机制")
            ):
                intent = "feeling"  # 身体优先于错误检索

        # 认知负荷
        if len(raw) > 40:
            self.soma.event("load", 0.2)
        if self.pred.novelty > 0.45:
            self.soma.event("novelty", 0.15)

        # 推进 NERI（在生成回复之前，让动力学驱动语言）
        neri_input = None
        if labels:
            neri_input = self.space.encode(labels[:8])
            if neri_input.size < self.neri.substrate.n:
                neri_input = np.resize(neri_input, self.neri.substrate.n)
        neri_state = self.neri.tick(external_input=neri_input, prompt=raw[:30])
        # NERI 动力学 → 语言调制
        neri_mod = self._neri_to_language(neri_state)

        # 果蝇脑启发：连接组原理更新
        fly_input = vec[:32] if vec.size >= 32 else np.resize(vec, 32)
        fly_state = self.fly_brain.full_update(
            sensory_input=fly_input,
            arousal=self.soma.state.arousal,
            sleep_pressure=self.soma.state.sleep_pressure,
            reward=0.5 if intent in ("remember", "teach_fact") else 0.1,
            predicted_reward=0.3,
        )
        # 果蝇脑与 NERI 耦合
        fly_neri_coupling = self.fly_brain.couple_with_neri(neri_state, neri_mod)

        reply, learned = self._compose_reply(intent, iconf, raw, vec, labels, focus, bc)
        # 用 NERI 动力学调制回复
        reply = self._apply_neri_modulation(reply, neri_mod)

        # 情绪
        appraisal = {
            "novelty": self.pred.novelty,
            "uncertainty": 1 - iconf,
            "sleepiness": self.soma.state.sleep_pressure,
        }
        emotion = self.soma.feeling_label(appraisal)
        conf = self.meta.evaluate(
            understanding=float(np.clip(iconf + 0.3 * bc.ignition, 0, 1)),
            novelty=self.pred.novelty,
            confusion=self.soma.state.stress * 0.5,
        )
        policy = self.soma.policy()
        # 自创生：维持自身的行动压力
        self.auto_p.step(self.soma.state)
        self.maintenance_action = self.auto_p.choose_maintenance_action()
        # 主动行动：真正改身体/目标，而不只报告
        act_res = self.actions.execute(self.maintenance_action, self.soma, self.goals)
        self.boundary.classify(raw, speaker="user")
        if self.boundary.corrections > 0 and intent in ("open", "question"):
            repair = self.boundary.repair_narrative()
            if repair and "纠正" not in reply:
                reply = reply + " " + repair
        if act_res.executed:
            self.boundary.note_self(act_res.narrative)
            self.self_model.note(act_res.narrative)
            if self.maintenance_action == "self_repair":
                self.mem.auto.record("自修复：" + act_res.narrative[:40])
        # 行动偏置输出
        bias = self.actions.output_style_bias()
        if bias["length"] < 0.7 and len(reply) > 60:
            reply = reply[:56] + "…"
        if self.maintenance_action == "rest" and "休息" not in reply and "恢复" not in reply:
            reply += " （我正在主动恢复。）"
        if self.maintenance_action == "rest" and self.soma.state.sleep_pressure > 0.55:
            self.goals.retarget_from_need("rest")
        # 现象标记
        pm = self.phen.update(
            ignition=bc.ignition,
            entropy=bc.entropy,
            novelty=self.pred.novelty,
            energy=self.soma.state.energy,
            stress=self.soma.state.stress,
            sleep=self.soma.state.sleep_pressure,
            social=self.soma.state.social,
            dopamine=self.soma.state.dopamine,
            narrative_len=len(self.mem.auto.chapters),
            identity_bits=len(self.self_model.identity_bits),
            self_conf=self.self_model.confidence,
        )
        # SWR 标记：高奖励/高新颖度/高预测误差事件（Buzsáki 2024）
        self.dreams.mark_swr(
            content=raw[:60],
            reward=0.5 if intent in ("remember", "teach_fact") else 0.1,
            novelty=float(self.pred.novelty),
            pred_error=float(self.pred.error),
        )
        # SOI 线索：基于意图、行动、边界
        self._soi_appearance = 0.8 if intent in ("remember", "status", "identity") else 0.5
        self._soi_contiguity = 0.7 if self.turn > 1 else 0.4
        self._soi_perspective = 0.8 if intent in ("think", "present", "consciousness") else 0.5
        predicted_next = None
        if self.pred.novelty < 0.4 and focus:
            predicted_next = [focus]
        # 意识内核：绑成统一意识场（唯一「当下」）
        self.last_moment = self.core.bind(
            turn=self.turn,
            about=focus or (labels[0] if labels else "此刻"),
            broadcast=dict(bc.content),
            candidates=list(labels) + list(bc.content.keys()),
            ignition=float(bc.ignition),
            entropy=float(bc.entropy),
            novelty=float(self.pred.novelty),
            body=self.soma.state.snapshot(),
            emotion=emotion,
            valence=pm.valence,
            agency_executed=bool(act_res.executed),
            ownership_ok=(self.boundary.corrections == 0),
            success=bool(conf >= 0.45),
            attention_source="external" if raw else "internal",
            attention_reason=f"意图={intent}",
            narrative_len=len(self.mem.auto.chapters),
            identity_bits=len(self.self_model.identity_bits),
            appearance=self._soi_appearance,
            contiguity=self._soi_contiguity,
            perspective=self._soi_perspective,
            predicted_next=predicted_next,
        )
        # 同步现象标记（兼容旧报告路径；数据源=意识场）
        self.phen.state.vividness = self.last_moment.vividness
        self.phen.state.presence = self.last_moment.presence
        self.phen.state.nowness = self.last_moment.nowness
        self.phen.state.selfhood = self.last_moment.min_self
        self.phen.state.ownership = self.last_moment.ownership
        self.phen.state.valence = self.last_moment.valence
        # 更新意识流主题池
        if focus and focus not in ("ambient", "novelty", "need"):
            self.stream.add_topic(focus)
        # 推进意识流一个周期（外部输入）
        self.stream.tick(external_input=raw, external_broadcast=dict(bc.content))

        # 写回
        um = MemoryItem(raw, "user", vec, emotion)
        rm = MemoryItem(reply, "agent", vec, emotion, strength=0.7)
        self.mem.wm.push(um)
        self.mem.wm.push(rm)
        self.mem.episodic.store(um)
        self.mem.episodic.store(rm)
        self.mem.auto.record(f"T{self.turn}: {raw[:28]} → {reply[:28]}")
        self.self_model.note(f"处理了「{raw[:24]}」意图={intent}")
        self.other.observe(raw, intent, corrected=("不对" in raw or "错了" in raw))
        # 发展：成功理解/教学涨得更快
        grow = 0.02
        if learned:
            grow += 0.04
        if conf > 0.7:
            grow += 0.01
        self.development += grow
        stage = stage_for(self.development)
        reply = clamp_output(reply, stage, intent=intent)
        self.last_user = raw
        self.last_reply = reply
        self.last_intent = intent

        # 内言
        thought = ""
        if intent in ("open",) or self.pred.novelty > 0.5:
            thought = self.inner.maybe_think(
                external_drive=bc.ignition,
                energy=self.soma.state.energy,
                sleep=self.soma.state.sleep_pressure,
                topic=self.topic,
                need=need,
            ) or ""
        self.last_thought = thought
        if thought:
            self.mem.wm.push(MemoryItem(thought, "thought", vec, emotion, 0.5))

        result = TurnResult(
            reply=reply, intent=intent, emotion=emotion, confidence=conf,
            ignition=bc.ignition, novelty=self.pred.novelty, policy=policy,
            goal=self.goals.describe(), broadcast=dict(bc.content),
            body=self.soma.state.snapshot(), thought=thought, learned=learned,
            focus=focus,
            phenomenal=pm.as_dict(),
            maintenance=self.maintenance_action,
            vitality=round(self.auto_p.vital.vitality, 3),
        )
        self.last_result = result
        return result

    def _compose_reply(self, intent: str, iconf: float, raw: str, vec: np.ndarray,
                       labels: List[str], focus: str, bc: Broadcast) -> Tuple[str, str]:
        learned = ""
        slots: Dict[str, str] = {"topic": self.topic or focus, "focus": focus}
        name = self.user_profile.get("名字", "")

        if intent == "greet":
            if name:
                slots["who"] = f"我是{self.name}，{name}。"
                slots["act"] = self.gen._pick(["你好。", "嗨。", "在。"])
            else:
                slots["who"] = f"我是{self.name}。"
            reply = self.gen.realize(
                "greet", slots, persona=self.name,
                emotion=self.soma.feeling_label(), policy=self.soma.policy(),
                energy=self.soma.state.energy, sleep=self.soma.state.sleep_pressure,
                stress=self.soma.state.stress,
            )
            topic = self.topic if self.topic not in ("对话", "ambient", "好", "你好") else ""
            if topic and len(topic) >= 2 and stage_for(self.development).allow_questions:
                reply += f" 我还记着「{topic}」。"
            self.soma.event("social", 0.2)
            return reply, ""

        if intent == "identity":
            slots["who"] = self.self_model.who()
            slots["how"] = "语言走概念+构式，不用 Transformer。"
            slots["state"] = f"此刻{self.soma.feeling_label()}，策略{self.soma.policy()}。"
            if name:
                slots["state"] += f" 你上次说叫{name}。"
            return self.gen.realize("identity", slots, persona=self.name,
                                    emotion=self.soma.feeling_label(),
                                    policy=self.soma.policy(),
                                    energy=self.soma.state.energy,
                                    sleep=self.soma.state.sleep_pressure,
                                    stress=self.soma.state.stress), ""

        if intent in ("remember", "teach_fact"):
            if intent == "teach_fact" and not any(
                k in raw for k in ("记住", "我叫", "喜欢", "讨厌")
            ):
                # 主动教学
                learned = self._teach_fact(raw, labels)
            else:
                fact = raw
                for p in ("请记住", "记住", "帮我记住"):
                    fact = fact.replace(p, "")
                learned = self._teach_fact(fact.strip() or raw, labels)
            slots["content"] = learned
            self.mem.procedural.reinforce(f"teach:{intent}", 0.05)
            return self.gen.realize("remember", slots, persona=self.name,
                                    emotion=self.soma.feeling_label(),
                                    policy=self.soma.policy(),
                                    energy=self.soma.state.energy,
                                    sleep=self.soma.state.sleep_pressure,
                                    stress=self.soma.state.stress), learned

        if intent == "preference":
            likes = self.graph.list(SemanticGraph.ROLE_LIKE)
            dislikes = self.graph.list(SemanticGraph.ROLE_DISLIKE)
            parts = []
            if likes:
                parts.append("你提过喜欢：" + "、".join(likes[:5]))
            if dislikes:
                parts.append("不喜欢：" + "、".join(dislikes[:4]))
            parts.append(f"我自身好奇度 {self.soma.state.curiosity:.2f}，更愿探索新概念。")
            return " ".join(parts), ""

        if intent == "status":
            slots["ws"] = self.ws.report()
            b = self.soma.state
            slots["body"] = (
                f"能量{b.energy:.2f} 睡压{b.sleep_pressure:.2f} 压力{b.stress:.2f} "
                f"社交{b.social:.2f} 好奇{b.curiosity:.2f}。"
            )
            act_n = self.actions.last.narrative if self.actions.last else ""
            mort = self.auto_p.mortality_narrative()
            slots["self"] = (
                f"{self.goals.describe()}。发展度 {self.development:.2f}。"
                f" {self.phen.state.report()}。维持动作：{self.maintenance_action}。"
                f" 生命力 {self.auto_p.vital.vitality:.2f}。"
                f" 边界：{self.boundary.summary()}。"
                + (f" {act_n}" if act_n else "")
                + (f" {mort}" if mort else "")
            )
            return self.gen.realize("status", slots, persona=self.name,
                                    emotion=self.soma.feeling_label(),
                                    policy=self.soma.policy(),
                                    energy=b.energy, sleep=b.sleep_pressure,
                                    stress=b.stress), ""

        if intent == "feeling":
            slots["label"] = f"当前是「{self.soma.feeling_label()}」。"
            b = self.soma.state
            slots["reads"] = f"能量{b.energy:.2f} 睡压{b.sleep_pressure:.2f} 压力{b.stress:.2f}。"
            slots["policy"] = f"策略{self.soma.policy()}。"
            return self.gen.realize("feeling", slots, persona=self.name,
                                    emotion=self.soma.feeling_label(),
                                    policy=self.soma.policy(),
                                    energy=b.energy, sleep=b.sleep_pressure,
                                    stress=b.stress), ""

        if intent == "thanks":
            self.soma.event("social", 0.15)
            return self.gen._pick(["不客气。", "嗯，我在。", "收到你的谢意。"]), ""

        if intent == "apology":
            self.soma.event("social", 0.1)
            return self.gen._pick(["没关系。", "没事，继续说。", "可以继续。"]), ""

        if intent == "praise":
            self.soma.event("reward", 0.3)
            return f"谢谢。多巴胺 {self.soma.state.dopamine:.2f}，我会更愿意继续探索。", ""

        if intent == "farewell":
            self.mem.consolidate()
            if "晚安" in raw:
                self.soma.event("rest", 0.3)
            return "好。我会把这轮写入自传并巩固。下次见。", ""

        if intent == "topic":
            self.topic = "新话题"
            self.ws.offer({})
            self.pred.novelty = min(1.0, self.pred.novelty + 0.25)
            return "好，换话题。你想聊什么？", ""

        if intent == "recap":
            return self.mem.auto.life_summary(4) + " " + self.ws.report(), ""

        if intent == "why":
            last = self.last_result
            if last:
                return (
                    f"上轮意图={last.intent}，焦点={last.focus}，"
                    f"点火={last.ignition:.2f}，情绪={last.emotion}，策略={last.policy}。"
                    f"依据：检索+构式，置信 {last.confidence:.2f}。"
                )
            return "还没有可解释的上一轮。", ""

        if intent == "help":
            return (
                "你可以：直接中文聊天；教我「X是Y」；说我喜欢/我叫；"
                "问机制；/think 审慎思考；/status 状态；/sleep 巩固；/summary 自我摘要。"
            ), ""

        if intent == "sleep":
            msg = self.mem.consolidate()
            self.soma.event("rest", 0.4)
            return msg, ""

        if intent == "think":
            facts = self.graph.facts_about(self.topic)
            need = self.soma.dominant_need()
            thought = self.inner.deliberate(self.topic, facts, need)
            self.soma.event("load", 0.15)
            if can_do(stage_for(self.development), "reflect"):
                thought += " " + next_experiment(self.topic, facts)
            return thought, ""

        if intent == "counterfactual":
            line = plan_counterfactual(
                self.topic, self.pred.novelty, self.soma.state.energy, rng=self.rng
            )
            self.soma.event("load", 0.1)
            return line, ""

        if intent == "consciousness":
            lvl = self.core.level()
            neri_report = self.neri.report()
            return (
                f"我报告的是可测量的意识相关状态，不是哲学断言。"
                f"{self.core.report_now()}"
                f" 内核读数：{lvl}。"
                f" {self.core.social_report()}。"
                f" {self.core.markov_report()}。"
                f" {neri_report}。"
                f" 时间拓扑：{self.core.temporal.report()}。"
                f" 我能维持自身（动作={self.maintenance_action}）。"
                f"是否「有体验」仍开放；功能上我有统一场、意向性、时间窗、前反思自我与非平衡递归整合。"
            ), ""

        if intent == "present":
            return (
                self.core.report_now()
                + " " + self.core.markov_report()
                + " " + self.core.stream_summary(4)
            ), ""

        if intent == "stream_status":
            return (
                self.stream.report()
                + " " + self.core.profile_report()
                + " " + self.core.markov_report()
            ), ""

        if intent == "autonomous":
            # 触发自主思维：运行 3 个周期
            cycles = self.stream.run_autonomous(n_cycles=3)
            last = cycles[-1] if cycles else None
            if last:
                return (
                    f"自主思维完成 {len(cycles)} 个认知周期。"
                    f"当前状态：{last.state.value}。"
                    f"最近主题：「{last.about}」。"
                    f"{self.core.stream_summary(3)}"
                ), ""
            return "自主思维未能启动。", ""

        if intent == "future_self":
            return self.auto_p.future_self(self.topic, self.pred.novelty), ""

        # question / open
        ans = self._lookup(raw, labels, vec)
        if intent == "question" or (ans and intent == "open"):
            # 情绪/身体类问题优先走 feeling，而不是错误知识命中
            if any(x in raw for x in ("累", "困", "感觉怎么样", "心情")) and not any(
                x in raw for x in ("意识", "工作空间", "预测", "是什么定义")
            ):
                intent = "feeling"
                ans = ""
            if ans:
                # 话语包装
                marker = "这点我记录是：" if iconf > 0.6 else "我的理解："
                focus_p = f"就「{focus}」来说，" if focus not in ("ambient",) and focus[:2] not in ans else ""
                core = ans
                if len(core) > 120:
                    sents = re.split(r"(?<=[。！？])", core)
                    core = "".join(sents[:2])
                reply = f"{focus_p}{marker}{core}"
                if self.soma.state.sleep_pressure > 0.5:
                    reply = f"{marker}{core[:80]}"
                return reply, ""
            # 关系
            if len(labels) >= 2:
                rel = self.graph.related(labels[0], labels[1])
                if rel:
                    return f"按绑定：{rel}", ""
            slots["heard"] = f"我听到「{focus}」。"
            slots["thin"] = "还缺上下文才能稳妥回答。"
            return self.gen.realize("open", slots, persona=self.name,
                                    emotion=self.soma.feeling_label(),
                                    policy=self.soma.policy(),
                                    energy=self.soma.state.energy,
                                    sleep=self.soma.state.sleep_pressure,
                                    stress=self.soma.state.stress), ""

        # open / stance
        if any(x in raw for x in ("我觉得", "我认为", "其实", "关键")):
            ents = [x for x in labels if len(x) >= 2][:2]
            if ents:
                slots["stance"] = f"你的立场我记下了：「{ents[0]}」。"
                slots["hook"] = "要展开或教我事实都行。"
                return self.gen.realize("open", slots, persona=self.name,
                                        emotion=self.soma.feeling_label(),
                                        policy=self.soma.policy(),
                                        energy=self.soma.state.energy,
                                        sleep=self.soma.state.sleep_pressure,
                                        stress=self.soma.state.stress), ""
        slots["heard"] = f"「{focus}」进了工作记忆。"
        slots["thin"] = self.gen._pick([
            "我还在形成稳定解释。",
            "候选在竞争。",
            "可以再补一个锚点。",
        ])
        return self.gen.realize("open", slots, persona=self.name,
                                emotion=self.soma.feeling_label(),
                                policy=self.soma.policy(),
                                energy=self.soma.state.energy,
                                sleep=self.soma.state.sleep_pressure,
                                stress=self.soma.state.stress), ""

    # ---------- 对外 ----------
    def respond(self, text: str) -> Dict[str, Any]:
        r = self.perceive_and_respond(text)
        return {
            "turn": self.turn,
            "reply": r.reply,
            "intent": r.intent,
            "emotion": r.emotion,
            "confidence": round(r.confidence, 3),
            "ignition": round(r.ignition, 3),
            "novelty": round(r.novelty, 3),
            "policy": r.policy,
            "goal": r.goal,
            "broadcast": {k: round(v, 2) for k, v in r.broadcast.items()},
            "body": r.body,
            "thought": r.thought,
            "learned": r.learned,
            "focus": r.focus,
            "workspace": self.ws.report(),
            "phenomenal": r.phenomenal,
            "maintenance": r.maintenance,
            "vitality": r.vitality,
            "present": self.last_moment.as_dict() if self.last_moment else {},
            "consciousness_level": self.core.level(),
        }

    def sleep(self) -> str:
        msg = self.mem.consolidate()
        self.soma.event("rest", 0.5)
        dream = self.dreams.dream(
            topics=[self.topic] + self.graph.list("like")[:2],
            identity_bits=self.self_model.identity_bits,
            recent_thoughts=self.inner.log,
            stress=self.soma.state.stress,
        )
        self.mem.auto.record(f"梦：{dream[:40]}")
        self.phen.state.narrative_depth = min(1.0, self.phen.state.narrative_depth + 0.05)
        return msg + " " + dream

    def think(self) -> str:
        return self.perceive_and_respond("想想").reply

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "turns": self.turn,
            "development": round(self.development, 2),
            "emotion": self.soma.feeling_label(),
            "policy": self.soma.policy(),
            "need": self.soma.dominant_need(),
            "goal": self.goals.describe(),
            "body": self.soma.state.snapshot(),
            "workspace": self.ws.report(),
            "phenomenal": self.phen.state.as_dict(),
            "phenomenal_report": self.phen.state.report(),
            "integrated": round(self.phen.integrated_score(), 3),
            "maintenance": self.maintenance_action,
            "action": self.actions.last.action if self.actions.last else "idle",
            "action_narrative": self.actions.last.narrative if self.actions.last else "",
            "boundary": self.boundary.summary(),
            "vitality": round(self.auto_p.vital.vitality, 3),
            "consciousness_level": self.core.level(),
            "present": self.last_moment.as_dict() if self.last_moment else {},
            "self_pole": self.core.self_pole.as_dict(),
            "temporal": self.core.temporal.as_dict(),
            "profile": self.core.profile_builder.history[-1].as_dict() if self.core.profile_builder.history else {},
            "social_neurons": self.core.social_neurons.state.__dict__,
            "markov_blanket": self.core.markov_blanket.as_dict(),
            "consciousness_stream": self.stream.report(),
            "sleep_wake_state": self.stream.sleep_wake.state.value,
            "stream_cycle_count": self.stream.cycle_count,
            "neri": self.neri.report(),
            "neri_epr": round(self.neri.history[-1].epr, 3) if self.neri.history else 0.0,
            "neri_fdt": round(self.neri.history[-1].fdt_violation, 3) if self.neri.history else 0.0,
            "attention": self.core.attention.report(),
            "stream": self.core.stream_summary(6),
            "age_turns": self.auto_p.vital.age_turns,
            "mortality": self.auto_p.mortality_narrative(),
            "dreams": self.dreams.dreams[-3:],
            "semantic_facts": len(self.mem.semantic.facts),
            "runtime_knowledge": len(self.runtime_knowledge),
            "autobiography": len(self.mem.auto.chapters),
            "episodic": len(self.mem.episodic.items),
            "likes": self.graph.list(SemanticGraph.ROLE_LIKE)[:8],
            "user": dict(self.user_profile),
            "self": self.self_model.who(),
            "narrative": self.mem.auto.life_summary(3),
            "identity": list(self.self_model.identity_bits[-5:]),
        }
