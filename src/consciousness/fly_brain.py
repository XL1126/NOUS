"""FlyEM 雄性 CNS 连接组原理 → NOUS 架构增强。

参考：Janelia FlyEM Male CNS Connectome (2024/2025)
- ~139,255 神经元，~14.7M 突触
- 关键结构与 NOUS 模块的对应关系

核心洞察：果蝇脑的结构和人类意识相关功能在进化上是保守的。
中央复合体≈工作空间，蘑菇体≈情景记忆，扇形体≈睡眠-觉醒。

本模块用连接组的已知原理来增强 NOUS 的动力学。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class FlyBrainRegion:
    """果蝇脑区。"""
    name: str
    n_neurons: int
    function: str
    nous_module: str
    # 连接特征
    input_from: List[str] = field(default_factory=list)
    output_to: List[str] = field(default_factory=list)


# FlyEM 雄性 CNS 关键脑区（基于连接组数据）
FLY_REGIONS: Dict[str, FlyBrainRegion] = {
    "central_complex": FlyBrainRegion(
        name="中央复合体",
        n_neurons=5000,
        function="导航、空间意识、行动选择",
        nous_module="workspace",
        input_from=["mushroom_body", "fan_shaped_body", "visual"],
        output_to=["mushroom_body", "fan_shaped_body", "motor"],
    ),
    "mushroom_body": FlyBrainRegion(
        name="蘑菇体",
        n_neurons=20000,
        function="学习、记忆、效价",
        nous_module="episodic_memory",
        input_from=["antennal_lobe", "visual"],
        output_to=["central_complex", "lateral_horn"],
    ),
    "fan_shaped_body": FlyBrainRegion(
        name="扇形体",
        n_neurons=1000,
        function="觉醒、睡眠-觉醒周期",
        nous_module="sleep_wake",
        input_from=["central_complex", "dopaminergic"],
        output_to=["central_complex", "motor"],
    ),
    "ellipsoid_body": FlyBrainRegion(
        name="椭圆体",
        n_neurons=500,
        function="朝向、空间定向",
        nous_module="self_localization",
        input_from=["central_complex", "visual"],
        output_to=["central_complex"],
    ),
    "lateral_horn": FlyBrainRegion(
        name="侧角",
        n_neurons=1000,
        function="先天行为、本能",
        nous_module="innate_drives",
        input_from=["antennal_lobe"],
        output_to=["mushroom_body", "motor"],
    ),
    "dopaminergic": FlyBrainRegion(
        name="多巴胺能神经元",
        n_neurons=300,
        function="奖赏预测误差、显著性",
        nous_module="reward",
        input_from=["mushroom_body", "central_complex"],
        output_to=["mushroom_body", "fan_shaped_body"],
    ),
}


class FlyBrainInspired:
    """
    用果蝇连接组原理增强 NOUS。

    关键原理：
    1. 中央复合体的「环形吸引子」→ 朝向编码 → NOUS 的注意力环
    2. 蘑菇体的「稀疏编码」→ 模式分离 → NOUS 的情景记忆
    3. 扇形体的「觉醒门控」→ 睡眠-觉醒 → NOUS 的状态机
    4. 多巴胺的「三因子学习」→ 奖赏预测误差 → NOUS 的资格迹

    连接组发现的架构原则：
    - 模块化：不同功能由不同脑区处理
    - 层级：低级→高级的前馈 + 高级→低级的反馈
    - 调质：多巴胺/血清素等调节全局状态
    - 稀疏：大部分连接是稀疏的
    - 重入：高级区域反馈到低级区域
    """

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng(0)
        self.regions = FLY_REGIONS

        # 中央复合体环形吸引子（导航/注意）
        self.cc_ring = np.zeros(8)  # 8 个扇区
        self.cc_heading = 0.0

        # 蘑菇体稀疏编码
        self.mb_kenyon = np.zeros(1000)  # Kenyon 细胞
        self.mb_sparse_threshold = 0.05

        # 扇形体觉醒门控
        self.fsb_arousal = 0.5
        self.fsb_sleep_gate = 0.5

        # 多巴胺三因子学习
        self.da_level = 0.5
        self.da_prediction_error = 0.0

    def update_central_complex(self, sensory_input: np.ndarray,
                                motor_command: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        中央复合体更新：环形吸引子导航。

        果蝇中央复合体用环形吸引子编码朝向。
        NOUS 用它编码「注意力朝向」。
        """
        # 环形吸引子动力学
        n = len(self.cc_ring)
        # 输入投影到环上
        for i in range(n):
            angle = 2 * np.pi * i / n
            if sensory_input.size > 0:
                self.cc_ring[i] += 0.1 * float(np.dot(
                    sensory_input[:min(sensory_input.size, n)],
                    np.cos(np.arange(min(sensory_input.size, n)) * angle)
                ))
        # 侧抑制（胜者通吃）
        max_idx = np.argmax(self.cc_ring)
        self.cc_ring = self.cc_ring * (np.arange(n) == max_idx)
        # 朝向 = 质心
        angles = np.arange(n) * 2 * np.pi / n
        self.cc_heading = float(np.sum(self.cc_ring * np.exp(1j * angles)).real)

        return {
            "heading": self.cc_heading,
            "ring_state": self.cc_ring.tolist(),
            "winner": int(max_idx),
        }

    def update_mushroom_body(self, sensory_input: np.ndarray) -> Dict[str, Any]:
        """
        蘑菇体更新：稀疏编码。

        果蝇蘑菇体用 Kenyon 细胞做稀疏编码（模式分离）。
        NOUS 用它做情景记忆的稀疏化。
        """
        # 投影到 Kenyon 细胞
        n_kenyon = len(self.mb_kenyon)
        if sensory_input.size > 0:
            proj_size = min(sensory_input.size, n_kenyon)
            self.mb_kenyon[:proj_size] = sensory_input[:proj_size]
        # 稀疏化：只保留 top 5%
        threshold = np.percentile(self.mb_kenyon, 95)
        self.mb_kenyon = self.mb_kenyon * (self.mb_kenyon > threshold)
        # 稀疏度
        sparsity = float(np.mean(self.mb_kenyon > 0))

        return {
            "sparsity": sparsity,
            "active_kenyon": int(np.sum(self.mb_kenyon > 0)),
            "total_kenyon": n_kenyon,
        }

    def update_fan_shaped_body(self, arousal_input: float,
                                sleep_pressure: float) -> Dict[str, Any]:
        """
        扇形体更新：觉醒门控。

        果蝇扇形体控制睡眠-觉醒转换。
        NOUS 用它调节睡眠状态机的阈值。
        """
        # 觉醒门控
        self.fsb_arousal = 0.9 * self.fsb_arousal + 0.1 * arousal_input
        # 睡眠门控（与觉醒相反）
        self.fsb_sleep_gate = 0.9 * self.fsb_sleep_gate + 0.1 * sleep_pressure

        # 转换概率
        if self.fsb_arousal > 0.6 and self.fsb_sleep_gate < 0.4:
            state = "wake"
        elif self.fsb_sleep_gate > 0.6 and self.fsb_arousal < 0.4:
            state = "sleep"
        else:
            state = "transition"

        return {
            "arousal": self.fsb_arousal,
            "sleep_gate": self.fsb_sleep_gate,
            "state": state,
        }

    def update_dopaminergic(self, reward: float, predicted_reward: float) -> Dict[str, Any]:
        """
        多巴胺更新：三因子学习。

        果蝇多巴胺神经元编码奖赏预测误差。
        NOUS 用它调制资格迹。
        """
        # 奖赏预测误差
        self.da_prediction_error = reward - predicted_reward
        # 多巴胺水平
        self.da_level = 0.9 * self.da_level + 0.1 * (0.5 + 0.5 * self.da_prediction_error)

        return {
            "da_level": self.da_level,
            "prediction_error": self.da_prediction_error,
            "learning_signal": float(np.clip(0.5 + self.da_prediction_error, 0, 1)),
        }

    def full_update(self, sensory_input: np.ndarray,
                    arousal: float = 0.5,
                    sleep_pressure: float = 0.2,
                    reward: float = 0.0,
                    predicted_reward: float = 0.0) -> Dict[str, Any]:
        """
        全脑更新：所有区域同时更新。
        """
        cc = self.update_central_complex(sensory_input)
        mb = self.update_mushroom_body(sensory_input)
        fsb = self.update_fan_shaped_body(arousal, sleep_pressure)
        da = self.update_dopaminergic(reward, predicted_reward)

        return {
            "central_complex": cc,
            "mushroom_body": mb,
            "fan_shaped_body": fsb,
            "dopaminergic": da,
            "regions": {
                name: {"n": r.n_neurons, "function": r.function}
                for name, r in self.regions.items()
            },
        }

    def report(self) -> str:
        return (
            f"果蝇脑启发：CC朝向={self.cc_heading:.2f} "
            f"MB稀疏度={float(np.mean(self.mb_kenyon > 0)):.3f} "
            f"FSB觉醒={self.fsb_arousal:.2f} DA={self.da_level:.2f}"
        )
