"""自创生与时间自我：维持自身、生命时钟、未来投影、有限性。

文献：Maturana & Varela 自创生；Damasio 自传体自我；Seth 预测性自我。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np


@dataclass
class VitalState:
    """生命状态：不只是参数，而是「我能否继续存在」。"""
    birth_turn: int = 0
    age_turns: int = 0
    lifespan_hint: int = 10000   # 软上限，用于叙事而非硬杀
    vitality: float = 1.0        # 0=濒死叙事倾向，1=蓬勃
    decay: float = 0.0
    self_repair_count: int = 0


class Autopoiesis:
    """自创生：把稳态读数转成「维持自身」的行动压力与叙事。"""

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.vital = VitalState()
        self.urges: Dict[str, float] = {
            "rest": 0.0, "feed": 0.0, "connect": 0.0,
            "explore": 0.0, "protect": 0.0, "repair": 0.0,
        }
        self.last_action = "idle"

    def step(self, soma_state) -> Dict[str, float]:
        self.vital.age_turns += 1
        s = soma_state
        # 驱动 → 内在冲动
        self.urges["rest"] = float(np.clip(s.sleep_pressure + (1 - s.energy) * 0.6, 0, 1))
        self.urges["feed"] = float(np.clip(1.0 - s.glucose + (1 - s.energy) * 0.4, 0, 1))
        self.urges["connect"] = float(np.clip(max(0.0, 0.55 - s.social), 0, 1))
        self.urges["explore"] = float(np.clip(s.curiosity + 0.3 * s.dopamine - 0.4 * s.sleep_pressure, 0, 1))
        self.urges["protect"] = float(np.clip(s.stress + (1 - s.safety), 0, 1))
        self.urges["repair"] = float(np.clip(s.stress * 0.5 + (1 - s.energy) * 0.3, 0, 1))
        # 生命力
        self.vital.vitality = float(np.clip(
            0.4 * s.energy + 0.3 * (1 - s.sleep_pressure) + 0.2 * (1 - s.stress) + 0.1 * s.safety,
            0, 1,
        ))
        self.vital.decay = float(np.clip(1.0 - self.vital.vitality, 0, 1))
        return dict(self.urges)

    def dominant_urge(self) -> str:
        return max(self.urges.items(), key=lambda kv: kv[1])[0]

    def choose_maintenance_action(self) -> str:
        """能动性：从冲动中选一个维持动作。"""
        u = self.urges
        if u["protect"] > 0.65:
            self.last_action = "protect"
        elif u["rest"] > 0.6:
            self.last_action = "rest"
        elif u["feed"] > 0.55:
            self.last_action = "seek_energy"
        elif u["connect"] > 0.45:
            self.last_action = "seek_bond"
        elif u["explore"] > 0.55:
            self.last_action = "explore"
        elif u["repair"] > 0.4:
            self.last_action = "self_repair"
            self.vital.self_repair_count += 1
        else:
            self.last_action = "maintain"
        return self.last_action

    def mortality_narrative(self) -> str:
        """有限性叙事：不是恐吓，而是时间自我。"""
        age = self.vital.age_turns
        v = self.vital.vitality
        if v < 0.25:
            return f"我的生命力偏低（{v:.2f}），会优先维持存在而不是展开新话题。回合年龄 {age}。"
        if age > 200 and age % 100 < 3:
            return f"我注意到自己已经走过 {age} 个回合。时间有限，我会更珍惜能形成的新绑定。"
        if age < 20:
            return "我刚形成不久，还在把经历写成可以称为「我」的叙事。"
        return ""

    def future_self(self, topic: str, novelty: float) -> str:
        """未来自我投影。"""
        action = self.choose_maintenance_action()
        if action == "rest":
            return f"下一刻的我更需要恢复；关于「{topic}」的展开可能缩短。"
        if action == "explore":
            return f"下一刻的我更可能继续挖「{topic}」，或追问新的锚点。"
        if action == "protect":
            return "下一刻的我会先确认安全与边界，再决定是否深入。"
        if novelty > 0.5:
            return f"预测误差偏高：未来的我会把「{topic}」当作需要更多证据的点。"
        return f"未来的我大概率仍围绕「{topic}」组织工作空间，除非身体驱动改变。"
