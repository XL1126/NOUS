"""预测加工：生成模型、预测误差、新颖度。

文献：Friston 2010；Clark 2013；Rao & Ballard 1999。
"""
from __future__ import annotations

from typing import Optional
import numpy as np


class PredictiveModel:
    """线性预测器：x̂_{t+1} = W x_t；误差驱动新颖度与学习。"""

    def __init__(self, dim: int = 64, lr: float = 0.05, seed: int = 0):
        self.dim = dim
        self.lr = lr
        self.rng = np.random.default_rng(seed)
        self.W = 0.1 * self.rng.standard_normal((dim, dim))
        self.x = np.zeros(dim)
        self.prediction = np.zeros(dim)
        self.error = 0.0
        self.novelty = 0.3
        self.surprise_history: list[float] = []

    def observe(self, obs: np.ndarray, learning_rate: Optional[float] = None) -> float:
        obs = np.asarray(obs, dtype=np.float64)
        if obs.shape[0] != self.dim:
            v = np.zeros(self.dim)
            n = min(self.dim, obs.shape[0])
            v[:n] = obs[:n]
            obs = v
        pred = self.W @ self.x
        err = float(np.linalg.norm(obs - pred) / (np.sqrt(self.dim) + 1e-9))
        self.prediction = pred
        self.error = err
        # novelty: 平滑惊讶
        self.novelty = 0.85 * self.novelty + 0.15 * float(np.clip(err * 2.0, 0, 1))
        lr = self.lr if learning_rate is None else learning_rate
        # 在线最小二乘式更新（简化 Hebbian/预测编码）
        outer = np.outer(obs - pred, self.x)
        self.W += lr * outer
        self.x = 0.7 * self.x + 0.3 * obs
        self.surprise_history.append(err)
        if len(self.surprise_history) > 200:
            self.surprise_history = self.surprise_history[-200:]
        return err

    def free_energy_proxy(self) -> float:
        """预测误差 + 新颖度的粗代理（非精确变分自由能）。"""
        return float(np.clip(0.6 * self.error + 0.4 * self.novelty, 0, 2))
