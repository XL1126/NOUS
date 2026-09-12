"""GPU 后端选择器：自动检测 CuPy，回退 numpy。

CuPy 是 numpy 的 GPU 加速替代，API 几乎一致。
安装：pip install cupy-cuda11x（需 CUDA toolkit 运行时 DLL）
"""
from __future__ import annotations

import os
import sys
from typing import Any

# 预加载 CUDA DLL 路径（Windows pip 安装的 nvidia-* 包）
def _setup_cuda_dlls() -> None:
    if sys.platform != "win32":
        return
    try:
        import nvidia
        base = os.path.dirname(nvidia.__file__)
        subdirs = ["cuda_runtime/bin", "cublas/bin", "cufft/bin",
                    "curand/bin", "cusolver/bin", "cusparse/bin", "cuda_nvrtc/bin"]
        for sd in subdirs:
            p = os.path.join(base, sd)
            if os.path.isdir(p) and p not in os.environ.get("PATH", ""):
                os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
    except ImportError:
        pass

_setup_cuda_dlls()

# 尝试导入 CuPy（必须测试 kernel 编译，不只是简单 reduction）
try:
    import cupy as cp
    _test = cp.array([1.0, 2.0, 3.0])
    # 测试 element-wise kernel（需要 nvrtc）
    _ = float(cp.sum(_test * _test * _test))
    GPU_AVAILABLE = True
    xp = cp
    BACKEND = "cupy"
except Exception:
    import numpy as cp
    GPU_AVAILABLE = False
    xp = cp
    BACKEND = "numpy"


def to_gpu(arr):
    """将数组移到 GPU（如果可用）。"""
    if GPU_AVAILABLE:
        return cp.asarray(arr)
    return arr


def to_cpu(arr):
    """将数组移回 CPU。"""
    if GPU_AVAILABLE:
        return cp.asnumpy(arr)
    return arr


def backend_info() -> dict:
    info = {"backend": BACKEND, "gpu_available": GPU_AVAILABLE}
    if GPU_AVAILABLE:
        try:
            dev = cp.cuda.Device()
            info["device_id"] = dev.id
            info["compute_capability"] = f"{dev.compute_capability[0]}.{dev.compute_capability[1]}"
        except Exception:
            pass
    return info


__all__ = ["xp", "GPU_AVAILABLE", "BACKEND", "to_gpu", "to_cpu", "backend_info"]
