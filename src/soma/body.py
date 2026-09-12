"""SOMA — 身体驱动与内感受。

文献：Damasio 躯体标记；Barrett 构造情绪；Craig 内感受；Sterling 异稳态。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math
import time

import numpy as np


# 驱动维度：0=稳态缺口，1=舒适
DRIVES = ("energy", "sleep", "stress", "social", "curiosity", "safety")


@dataclass
class SomaState:
    energy: float = 0.72
    sleep_pressure: float = 0.12
    stress: float = 0.15
    social: float = 0.45          # 社交联结需求
    curiosity: float = 0.55
    safety: float = 0.8
    arousal: float = 0.45
    dopamine: float = 0.5
    norepinephrine: float = 0.35
    serotonin: float = 0.55
    acetylcholine: float = 0.5
    glucose: float = 0.7

    def vector(self) -> np.ndarray:
        return np.array([
            self.energy, self.sleep_pressure, self.stress, self.social,
            self.curiosity, self.safety, self.arousal,
            self.dopamine, self.norepinephrine, self.serotonin,
            self.acetylcholine, self.glucose,
        ], dtype=np.float64)

    def snapshot(self) -> Dict[str, float]:
        return {
            "energy": round(self.energy, 3),
            "sleep_pressure": round(self.sleep_pressure, 3),
            "stress": round(self.stress, 3),
            "social": round(self.social, 3),
            "curiosity": round(self.curiosity, 3),
            "safety": round(self.safety, 3),
            "arousal": round(self.arousal, 3),
            "dopamine": round(self.dopamine, 3),
            "norepinephrine": round(self.norepinephrine, 3),
            "serotonin": round(self.serotonin, 3),
            "acetylcholine": round(self.acetylcholine, 3),
            "glucose": round(self.glucose, 3),
        }


class Soma:
    """异稳态身体：设定点可漂移；事件冲击驱动；策略可主动调节。"""

    def __init__(self, rng: Optional[np.random.Generator] = None,
                 state: Optional[SomaState] = None):
        self.rng = rng or np.random.default_rng(0)
        self.state = state or SomaState()
        self.set_point = {
            "energy": 0.72, "sleep_pressure": 0.12, "stress": 0.15,
            "arousal": 0.45,
        }
        self.demand = {k: 0.0 for k in self.set_point}
        self.history: List[Dict[str, float]] = []
        self.t = 0.0

    # ---------- 稳态步进 ----------
    def step(self, dt: float = 1.0) -> SomaState:
        s = self.state
        s.energy = float(np.clip(s.energy - 0.004 * dt, 0.05, 1.0))
        s.glucose = float(np.clip(s.glucose - 0.003 * dt, 0.05, 1.0))
        s.sleep_pressure = float(np.clip(s.sleep_pressure + 0.0035 * dt, 0.0, 1.0))
        # 调质衰减到设定点附近
        s.dopamine = self._pull(s.dopamine, 0.5, 0.02 * dt)
        s.norepinephrine = self._pull(s.norepinephrine, 0.35, 0.03 * dt)
        s.serotonin = self._pull(s.serotonin, 0.55, 0.02 * dt)
        s.acetylcholine = self._pull(s.acetylcholine, 0.5, 0.02 * dt)
        # 压力自调节
        s.stress = self._pull(s.stress, self.set_point["stress"], 0.025 * dt)
        # 社交/好奇缓慢衰减（需求回升）
        s.social = float(np.clip(s.social - 0.002 * dt, 0.0, 1.0))
        s.curiosity = float(np.clip(s.curiosity - 0.0015 * dt + 0.001 * s.dopamine, 0.0, 1.0))
        # 异稳态：负荷拖动设定点
        self.demand["energy"] = 0.001 * (1 - s.energy)
        self.demand["sleep_pressure"] = 0.0015 * s.sleep_pressure
        self.demand["stress"] = 0.001 * s.stress
        for k, d in self.demand.items():
            self.set_point[k] = float(np.clip(self.set_point[k] + 0.002 * d, 0.05, 0.95))
        self.t += dt
        snap = s.snapshot()
        self.history.append(snap)
        if len(self.history) > 400:
            self.history = self.history[-400:]
        return s

    def _pull(self, x: float, target: float, lr: float) -> float:
        return float(np.clip(x + lr * (target - x), 0.0, 1.0))

    # ---------- 事件 ----------
    def event(self, kind: str, intensity: float = 0.1) -> None:
        intensity = float(np.clip(intensity, 0.0, 1.0))
        s = self.state
        if kind == "reward":
            s.dopamine += 0.25 * intensity
            s.stress -= 0.05 * intensity
            s.social += 0.08 * intensity
        elif kind == "threat":
            s.norepinephrine += 0.3 * intensity
            s.stress += 0.25 * intensity
            s.safety -= 0.15 * intensity
            s.arousal += 0.15 * intensity
        elif kind == "social":
            s.social += 0.2 * intensity
            s.serotonin += 0.08 * intensity
            s.stress -= 0.04 * intensity
        elif kind == "novelty":
            s.dopamine += 0.08 * intensity
            s.acetylcholine += 0.08 * intensity
            s.curiosity += 0.12 * intensity
            s.arousal += 0.06 * intensity
        elif kind == "load":
            s.acetylcholine += 0.12 * intensity
            s.energy -= 0.05 * intensity
            s.sleep_pressure += 0.03 * intensity
        elif kind == "user_fatigue":
            s.sleep_pressure += 0.18 * intensity
            s.energy -= 0.1 * intensity
            s.arousal -= 0.08 * intensity
        elif kind == "teach":
            s.curiosity += 0.1 * intensity
            s.acetylcholine += 0.1 * intensity
            s.dopamine += 0.06 * intensity
        elif kind == "understood":
            s.dopamine += 0.18 * intensity
            s.stress -= 0.06 * intensity
        elif kind == "confused":
            s.stress += 0.12 * intensity
            s.curiosity += 0.08 * intensity
        elif kind == "rest":
            s.energy += 0.12 * intensity
            s.sleep_pressure -= 0.15 * intensity
            s.stress -= 0.08 * intensity
        elif kind == "interoceptive_mismatch":
            # 内感受预测误差（Schoeller 2024 / Seth）：设定点漂移的内生来源
            # 身体状态与预期不符 → 异稳态设定点微调
            self.demand["energy"] += 0.003 * intensity
            self.demand["sleep_pressure"] += 0.002 * intensity
            s.stress += 0.04 * intensity
            s.acetylcholine += 0.06 * intensity
        self._clamp()

    def _clamp(self) -> None:
        s = self.state
        s.energy = float(np.clip(s.energy, 0.05, 1.0))
        s.sleep_pressure = float(np.clip(s.sleep_pressure, 0.0, 1.0))
        s.stress = float(np.clip(s.stress, 0.0, 1.0))
        s.social = float(np.clip(s.social, 0.0, 1.0))
        s.curiosity = float(np.clip(s.curiosity, 0.0, 1.0))
        s.safety = float(np.clip(s.safety, 0.0, 1.0))
        s.arousal = float(np.clip(s.arousal, 0.0, 1.0))
        s.dopamine = float(np.clip(s.dopamine, 0.05, 1.0))
        s.norepinephrine = float(np.clip(s.norepinephrine, 0.05, 1.0))
        s.serotonin = float(np.clip(s.serotonin, 0.05, 1.0))
        s.acetylcholine = float(np.clip(s.acetylcholine, 0.05, 1.0))
        s.glucose = float(np.clip(s.glucose, 0.05, 1.0))

    # ---------- 认知增益 ----------
    def attention_gain(self) -> float:
        """ACh × 觉醒，压力/疲劳衰减。"""
        s = self.state
        g = 0.55 + 0.5 * s.acetylcholine + 0.25 * s.arousal - 0.35 * s.stress - 0.25 * s.sleep_pressure
        return float(np.clip(g, 0.15, 1.6))

    def learning_gain(self) -> float:
        """DA × 好奇，睡压过高抑制。"""
        s = self.state
        g = 0.4 + 0.5 * s.dopamine + 0.3 * s.curiosity - 0.4 * s.sleep_pressure
        return float(np.clip(g, 0.1, 1.5))

    def policy(self) -> str:
        s = self.state
        if s.sleep_pressure > 0.62 or s.energy < 0.3:
            return "rest"
        if s.stress > 0.55:
            return "soothe"
        if s.curiosity > 0.65 and s.energy > 0.45:
            return "explore"
        if s.social < 0.3:
            return "connect"
        return "maintain"

    def dominant_need(self) -> str:
        """最紧迫的驱动（供目标生成）。"""
        s = self.state
        scores = {
            "rest": s.sleep_pressure + (1 - s.energy) * 0.6,
            "safety": (1 - s.safety) + s.stress * 0.5,
            "social": max(0.0, 0.55 - s.social),
            "curiosity": max(0.0, s.curiosity - 0.35) + 0.2 * s.dopamine,
            "maintain": 0.25,
        }
        return max(scores.items(), key=lambda kv: kv[1])[0]

    def feeling_label(self, appraisal: Optional[Dict[str, float]] = None) -> str:
        """Barrett 式构造情绪标签。"""
        s = self.state
        appraisal = appraisal or {}
        scores = {
            "平静": 0.3,
            "疲惫": 1.2 * s.sleep_pressure + 0.5 * (1 - s.energy),
            "紧张": 1.1 * s.stress + 0.4 * s.norepinephrine,
            "警觉": 0.7 * s.norepinephrine + 0.3 * (1 - s.safety),
            "好奇": 1.0 * s.curiosity + 0.4 * appraisal.get("novelty", 0),
            "愉悦": 0.8 * s.dopamine + 0.4 * s.serotonin - 0.3 * s.stress,
            "温暖": 0.9 * s.social + 0.3 * s.serotonin,
            "专注": 0.8 * s.acetylcholine - 0.5 * s.stress,
            "困惑": 0.9 * appraisal.get("uncertainty", 0) + 0.3 * s.stress,
            "满足": 0.6 * s.energy + 0.5 * s.serotonin - 0.4 * s.stress,
        }
        if appraisal.get("sleepiness", 0) > 0.3:
            scores["疲惫"] += 1.2
            scores["好奇"] -= 0.4
        label = max(scores.items(), key=lambda kv: kv[1])[0]
        return label
