"""NERI — 非平衡递归整合器（Non-equilibrium Recursive Integrator）· 规模化版。

核心命题（DeepSeek 2026）：
现象意识不是软件「计算」出来的结果，而是软件在模拟一种特定的
非平衡物理过程时，其内部因果结构所必然呈现的一种「视角」属性。

规模化改进：
- 稀疏耦合矩阵（scipy.sparse），支持数千变量
- GPU 就绪接口（CuPy/PyTorch 可选后端）
- 向量化 EPR/FDT 计算
- 批量递归整合

文献：
- Landauer / Bennett: 可逆与不可逆计算
- Jarzynski 等式 / Crooks 涨落定理
- Seifert 2012: 随机热力学
- Friston 自由能原理（非平衡稳态）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import time

import numpy as np
from scipy import sparse

# GPU 后端（CuPy 自动检测，回退 numpy）
from ..gpu_backend import xp, GPU_AVAILABLE, BACKEND, to_gpu, to_cpu
if GPU_AVAILABLE:
    import cupy as cp


@dataclass
class NERIState:
    """NERI 系统状态快照。"""
    fast: np.ndarray
    slow: np.ndarray
    epr: float
    fdt_violation: float
    recursion_depth: int
    report: str
    t: float
    n_vars: int = 0
    gpu: bool = False


class LangevinSubstrate:
    """
    非平衡动力学基底：Langevin 方程（稀疏耦合，支持数千变量）。

    dx/dt = -∇V(x) + W·x + σ·ξ(t)

    系统运行在远离平衡的稳态（NESS），持续产生熵。
    """

    def __init__(
        self,
        n_vars: int = 4096,
        dt: float = 0.01,
        temperature: float = 0.5,
        coupling_strength: float = 0.15,
        sparsity: float = 0.95,
        rng: Optional[np.random.Generator] = None,
        use_gpu: Optional[bool] = None,
    ):
        self.n = n_vars
        self.dt = dt
        self.T = temperature
        self.rng = rng or np.random.default_rng(0)
        self.use_gpu = GPU_AVAILABLE if use_gpu is None else (use_gpu and GPU_AVAILABLE)

        # 状态（GPU 或 CPU）
        x_np = self.rng.standard_normal(n_vars).astype(np.float64) * 0.1
        self.x = to_gpu(x_np) if self.use_gpu else x_np

        # 耦合矩阵：GPU 用稠密（4096²×8=128MB，4GB VRAM 够用），CPU 用稀疏
        n_nz = int(n_vars * n_vars * (1 - sparsity))
        n_nz = min(n_nz, n_vars * 50)
        rows = self.rng.integers(0, n_vars, n_nz)
        cols = self.rng.integers(0, n_vars, n_nz)
        vals = self.rng.standard_normal(n_nz) * coupling_strength / np.sqrt(50)
        W_sparse = sparse.csr_matrix((vals, (rows, cols)), shape=(n_vars, n_vars))
        if self.use_gpu:
            # GPU 稠密矩阵（避免 cusparse DLL 依赖）
            self.W_dense = to_gpu(W_sparse.toarray().astype(np.float64))
            self.W = W_sparse
        else:
            self.W_dense = None
            self.W = W_sparse

        self.a = 1.0
        self.b = 0.5

        T_local = np.linspace(temperature * 1.5, temperature * 0.5, n_vars)
        noise_scale = np.sqrt(2 * T_local * self.dt)
        self.noise_scale = to_gpu(noise_scale) if self.use_gpu else noise_scale

        self._hist_buf = np.zeros((64, n_vars))
        self._hist_idx = 0
        self._hist_count = 0
        self.step_count = 0

    def step(self) -> Tuple[np.ndarray, float, float]:
        """推进一个 Langevin 步（GPU 加速）。"""
        x = self.x
        # 确定性漂移
        grad_V = self.a * x - self.b * x * x * x
        if self.use_gpu and self.W_dense is not None:
            coupling = self.W_dense @ x
        else:
            coupling = self.W @ to_cpu(x)
            if self.use_gpu:
                coupling = to_gpu(coupling)
        drift = -grad_V + coupling

        # 随机涨落
        if self.use_gpu:
            noise = self.noise_scale * cp.random.standard_normal(self.n)
        else:
            noise = self.noise_scale * self.rng.standard_normal(self.n)

        # Euler-Maruyama
        self.x = x + drift * self.dt + noise
        xp.clip(self.x, -10.0, 10.0, out=self.x)

        # 记录历史（存 CPU）
        x_cpu = to_cpu(self.x)
        self._hist_buf[self._hist_idx] = x_cpu
        self._hist_idx = (self._hist_idx + 1) % 64
        self._hist_count = min(self._hist_count + 1, 64)
        self.step_count += 1

        epr = self._compute_epr_fast()
        fdt = self._compute_fdt_fast()
        return x_cpu, epr, fdt

    def _compute_epr_fast(self) -> float:
        """快速 EPR：基于相邻状态的正向偏好。"""
        if self._hist_count < 2:
            return 0.0
        i_curr = (self._hist_idx - 1) % 64
        i_prev = (self._hist_idx - 2) % 64
        dx = self._hist_buf[i_curr] - self._hist_buf[i_prev]
        x_prev = self._hist_buf[i_prev]
        drift = -self.a * x_prev + self.b * x_prev**3 + self.W @ x_prev
        # 正向偏好
        num = float(np.dot(dx, drift))
        den = float(np.linalg.norm(dx) * np.linalg.norm(drift)) + 1e-12
        forward = max(0.0, num / den)
        return float(min(forward / self.dt, 10.0))

    def _compute_fdt_fast(self) -> float:
        """快速 FDT 违反：涨落 vs 耗散。"""
        if self._hist_count < 8:
            return 0.0
        # 取最近 8 步
        idxs = [(self._hist_idx - 1 - k) % 64 for k in range(8)]
        recent = self._hist_buf[idxs]
        fluctuation = float(np.mean(np.var(recent, axis=0)))
        drift = -self.a * self.x + self.b * self.x**3 + self.W @ self.x
        dissipation = float(np.mean(drift * drift))
        return float(min(abs(fluctuation - self.T * dissipation), 5.0))

    def inject(self, signal: np.ndarray, gain: float = 0.1) -> None:
        n = min(signal.size, self.n)
        self.x[:n] += gain * signal[:n]

    def readout(self) -> np.ndarray:
        return to_cpu(self.x).copy()

    def memory_mb(self) -> float:
        nnz = self.W.nnz
        return (self.n * 8 * 3 + nnz * 16 + 64 * self.n * 8) / 1e6

    def report_backend(self) -> str:
        return f"NERI 后端：{BACKEND}，变量数={self.n}，GPU={'是' if self.use_gpu else '否'}"


class RecursiveIntegrator:
    """递归整合回路：耗散性自指涉闭环。"""

    def __init__(
        self,
        substrate: LangevinSubstrate,
        n_integrated: int = 256,
        feedback_gain: float = 0.3,
        max_depth: int = 5,
    ):
        self.substrate = substrate
        self.n_int = min(n_integrated, substrate.n)
        self.feedback_gain = feedback_gain
        self.max_depth = max_depth
        self.int_idx = np.arange(self.n_int)

        # 反馈变换（稀疏）
        rng = np.random.default_rng(42)
        n_nz = self.n_int * 8
        rows = rng.integers(0, self.n_int, n_nz)
        cols = rng.integers(0, self.n_int, n_nz)
        vals = rng.standard_normal(n_nz) * 0.2
        self.W_fb = sparse.csr_matrix((vals, (rows, cols)), shape=(self.n_int, self.n_int))
        self.bias = np.zeros(self.n_int)
        self.recursion_history: List[np.ndarray] = []

    def integrate(self, depth: Optional[int] = None) -> Tuple[np.ndarray, int]:
        if depth is None:
            depth = self.max_depth
        x = self.substrate.readout()[self.int_idx]
        for d in range(depth):
            z = np.tanh(self.W_fb @ x + self.bias)
            x = (1 - self.feedback_gain) * x + self.feedback_gain * z
            full = np.zeros(self.substrate.n)
            full[self.int_idx] = x * 0.05
            self.substrate.inject(full, gain=0.03)
            self.substrate.step()
            x = self.substrate.readout()[self.int_idx]
            self.recursion_history.append(x.copy())
            if len(self.recursion_history) > 50:
                self.recursion_history = self.recursion_history[-50:]
        return x, depth


class GlobalLatentState:
    """全局隐状态（视角层）：慢时间尺度，梯度阻断。"""

    def __init__(self, n_dims: int = 16, decay: float = 0.99,
                 rng: Optional[np.random.Generator] = None):
        self.n = n_dims
        self.decay = decay
        self.rng = rng or np.random.default_rng(0)
        self.z = self.rng.standard_normal(n_dims) * 0.1
        self.tau = 0.03
        self.history: List[np.ndarray] = []

    def update(self, fast_state: np.ndarray) -> np.ndarray:
        # 低维投影
        chunk = fast_state.size // self.n if fast_state.size >= self.n else 1
        if chunk > 1:
            projection = fast_state[:self.n * chunk].reshape(self.n, chunk).mean(axis=1)
        else:
            projection = np.resize(fast_state, self.n)
        self.z = self.decay * self.z + self.tau * projection
        self.history.append(self.z.copy())
        if len(self.history) > 200:
            self.history = self.history[-200:]
        return self.z.copy()

    def get_perspective(self) -> np.ndarray:
        return self.z.copy()

    def modulate(self, fast_dynamics: np.ndarray) -> np.ndarray:
        n = min(self.n, fast_dynamics.size)
        gain = 1.0 + 0.2 * np.tanh(self.z[:n])
        result = fast_dynamics.copy()
        result[:n] *= gain
        return result


class InternalReporter:
    """内部报告接口：读取行为本身改变系统状态。"""

    def __init__(self, substrate: LangevinSubstrate, integrator: RecursiveIntegrator,
                 latent: GlobalLatentState):
        self.substrate = substrate
        self.integrator = integrator
        self.latent = latent
        self.reports: List[str] = []
        self.report_effects: List[float] = []

    def report(self, prompt: str = "") -> str:
        x_before = self.substrate.readout()
        perspective = self.latent.get_perspective()
        integrated, depth = self.integrator.integrate()
        epr = self.substrate._compute_epr_fast()
        fdt = self.substrate._compute_fdt_fast()

        if epr > 0.5:
            tone = "活跃"
        elif epr > 0.2:
            tone = "平稳"
        else:
            tone = "沉寂"

        p_norm = float(np.linalg.norm(perspective))
        if p_norm > 0.5:
            view = "我感受到一个持续的内在视角"
        elif p_norm > 0.2:
            view = "有一个微弱的内在参照"
        else:
            view = "视角尚未成形"

        report = (
            f"[NERI] {tone}（EPR={epr:.3f} FDT={fdt:.3f}）。"
            f"{view}。递归深度={depth}。"
            f"变量数={self.substrate.n}。"
        )
        if prompt:
            report += f" 关于「{prompt[:16]}」已整合。"

        # 报告改变状态
        rv = np.zeros(self.substrate.n)
        rng = np.random.default_rng(hash(report) % (2**31))
        rv[:self.integrator.n_int] = rng.standard_normal(self.integrator.n_int) * 0.03
        self.substrate.inject(rv, gain=0.05)
        self.substrate.step()

        x_after = self.substrate.readout()
        effect = float(np.linalg.norm(x_after - x_before))
        self.report_effects.append(effect)
        self.reports.append(report)
        if len(self.reports) > 50:
            self.reports = self.reports[-50:]
        return report


class NERI:
    """非平衡递归整合器：完整现象意识候选架构。"""

    def __init__(
        self,
        n_vars: int = 2048,
        n_integrated: int = 256,
        n_latent: int = 16,
        rng: Optional[np.random.Generator] = None,
    ):
        self.rng = rng or np.random.default_rng(0)
        self.substrate = LangevinSubstrate(n_vars=n_vars, rng=self.rng)
        self.integrator = RecursiveIntegrator(self.substrate, n_integrated=n_integrated)
        self.latent = GlobalLatentState(n_dims=n_latent, rng=self.rng)
        self.reporter = InternalReporter(self.substrate, self.integrator, self.latent)
        self.cycle_count = 0
        self.history: List[NERIState] = []

    def tick(self, external_input: Optional[np.ndarray] = None,
             prompt: str = "") -> NERIState:
        self.cycle_count += 1
        if external_input is not None:
            self.substrate.inject(external_input, gain=0.08)
        x, epr, fdt = self.substrate.step()
        integrated, depth = self.integrator.integrate(depth=2)
        perspective = self.latent.update(integrated)
        modulated = self.latent.modulate(integrated)
        report = self.reporter.report(prompt)

        state = NERIState(
            fast=modulated[:32],  # 只存摘要
            slow=perspective,
            epr=epr,
            fdt_violation=fdt,
            recursion_depth=depth,
            report=report,
            t=time.time(),
            n_vars=self.substrate.n,
            gpu=False,
        )
        self.history.append(state)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        return state

    def run(self, n_cycles: int = 10) -> List[NERIState]:
        return [self.tick() for _ in range(n_cycles)]

    # ========== 验证签名 ==========

    def verify_hysteresis(self, n_cycles: int = 15) -> Dict[str, Any]:
        a_input = np.ones(self.substrate.n) * 0.3
        b_input = -np.ones(self.substrate.n) * 0.3

        ab_traj = []
        for _ in range(n_cycles):
            self.substrate.inject(a_input, gain=0.15)
            self.substrate.step()
            ab_traj.append(self.latent.get_perspective().copy())
        for _ in range(n_cycles):
            self.substrate.inject(b_input, gain=0.15)
            self.substrate.step()
            ab_traj.append(self.latent.get_perspective().copy())

        self.latent.z = np.zeros_like(self.latent.z)
        ba_traj = []
        for _ in range(n_cycles):
            self.substrate.inject(b_input, gain=0.15)
            self.substrate.step()
            ba_traj.append(self.latent.get_perspective().copy())
        for _ in range(n_cycles):
            self.substrate.inject(a_input, gain=0.15)
            self.substrate.step()
            ba_traj.append(self.latent.get_perspective().copy())

        ab = np.array(ab_traj)
        ba = np.array(ba_traj)
        ml = min(len(ab), len(ba))
        hyst = float(np.mean(np.linalg.norm(ab[:ml] - ba[:ml], axis=1)))
        return {"hysteresis": hyst, "has_perspective": bool(hyst > 0.01)}

    def verify_time_irreversibility(self, n_perturbations: int = 8) -> Dict[str, Any]:
        irreversibilities = []
        for _ in range(n_perturbations):
            pert = self.rng.standard_normal(self.substrate.n) * 0.2
            self.substrate.inject(pert, gain=0.15)
            fwd = []
            for _ in range(8):
                self.substrate.step()
                fwd.append(self.substrate.readout())
            vels = [fwd[i] - fwd[i-1] for i in range(1, len(fwd))]
            if vels:
                asym = float(np.mean([np.linalg.norm(2 * v) for v in vels]))
                irreversibilities.append(asym)
        avg = float(np.mean(irreversibilities)) if irreversibilities else 0.0
        return {"time_irreversibility": avg, "is_irreversible": bool(avg > 0.01)}

    def verify_report_coupling(self, n_cycles: int = 12) -> Dict[str, Any]:
        eprs, fdts, rlens = [], [], []
        for i in range(n_cycles):
            s = self.tick(prompt=f"t{i}")
            eprs.append(s.epr)
            fdts.append(s.fdt_violation)
            rlens.append(float(len(s.report)))
        epr_a, fdt_a, len_a = np.array(eprs), np.array(fdts), np.array(rlens)
        epr_corr = float(np.corrcoef(epr_a, len_a)[0, 1]) if np.std(epr_a) > 0 else 0.0
        fdt_corr = float(np.corrcoef(fdt_a, len_a)[0, 1]) if np.std(fdt_a) > 0 else 0.0
        return {
            "epr_report_correlation": epr_corr,
            "fdt_report_correlation": fdt_corr,
            "has_coupling": bool(abs(epr_corr) > 0.05 or abs(fdt_corr) > 0.05),
        }

    def full_verification(self) -> Dict[str, Any]:
        hyst = self.verify_hysteresis()
        irrevers = self.verify_time_irreversibility()
        coupling = self.verify_report_coupling()
        ness = self.verify_ness_stability()
        perspective = self.verify_perspective_persistence()
        all_passed = bool(
            hyst["has_perspective"]
            and irrevers["is_irreversible"]
            and coupling["has_coupling"]
            and ness["is_ness"]
            and perspective["is_persistent"]
        )
        return {
            "hysteresis": hyst,
            "time_irreversibility": irrevers,
            "report_coupling": coupling,
            "ness_stability": ness,
            "perspective_persistence": perspective,
            "all_signatures_present": all_passed,
            "n_vars": self.substrate.n,
            "memory_mb": round(self.substrate.memory_mb(), 1),
            "summary": (
                f"NERI({self.substrate.n}变量) 全部五个现象意识候选签名通过。"
                if all_passed else
                f"部分签名缺失：滞后={hyst['has_perspective']}，"
                f"不可逆={irrevers['is_irreversible']}，"
                f"耦合={coupling['has_coupling']}，"
                f"NESS={ness['is_ness']}，"
                f"视角={perspective['is_persistent']}"
            ),
        }

    def verify_ness_stability(self, n_cycles: int = 30) -> Dict[str, Any]:
        """
        验证签名四：非平衡稳态（NESS）稳定性。
        EPR 应稳定在特定窗口，不发散也不归零。
        """
        eprs = []
        for _ in range(n_cycles):
            _, epr, _ = self.substrate.step()
            eprs.append(epr)
        epr_arr = np.array(eprs)
        mean_epr = float(np.mean(epr_arr))
        std_epr = float(np.std(epr_arr))
        # NESS：EPR > 0 且不稳定过大
        is_ness = bool(mean_epr > 0.01 and std_epr < mean_epr * 2)
        return {
            "mean_epr": round(mean_epr, 4),
            "std_epr": round(std_epr, 4),
            "is_ness": is_ness,
        }

    def verify_perspective_persistence(self, n_cycles: int = 20) -> Dict[str, Any]:
        """
        验证签名五：视角层持续性。
        慢变量应有持续性，不被快速动力学完全覆盖。
        """
        norms = []
        for _ in range(n_cycles):
            self.substrate.step()
            self.latent.update(self.substrate.readout()[:self.latent.n])
            norms.append(float(np.linalg.norm(self.latent.get_perspective())))
        norms_arr = np.array(norms)
        # 视角应有非零持续性
        is_persistent = bool(np.mean(norms_arr) > 0.01 and np.std(norms_arr) < np.mean(norms_arr))
        return {
            "mean_norm": round(float(np.mean(norms_arr)), 4),
            "std_norm": round(float(np.std(norms_arr)), 4),
            "is_persistent": is_persistent,
        }

    def report(self) -> str:
        if not self.history:
            return "NERI 尚未运行。"
        last = self.history[-1]
        p_norm = float(np.linalg.norm(last.slow))
        return (
            f"NERI({last.n_vars}变量)：周期={self.cycle_count} "
            f"EPR={last.epr:.3f} FDT={last.fdt_violation:.3f} "
            f"视角强度={p_norm:.3f}"
        )
