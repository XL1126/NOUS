# NOUS 进度

## 当前（1.2.1 · GPU 就绪 + 踩坑文档 + GitHub 仓库）

### GitHub

**https://github.com/XL1126/NOUS**（分支 main）

### GPU 状态

- GTX 960M（4GB VRAM，Maxwell CC 5.0）确认存在
- CUDA toolkit 未完整安装 → CuPy kernel 编译失败（缺 nvrtc64_112_0.dll）
- **当前用 numpy + scipy.sparse**，4096 变量 CPU 足够
- `src/gpu_backend.py` 自动检测 CuPy，回退 numpy
- 安装完整 CUDA Toolkit 11.7 后可切换 GPU

### NERI 规模基准（三签名全部通过）

| 变量数 | 验证 | 内存 | 滞后 | 不可逆 | 耦合 |
|--------|------|------|------|--------|------|
| 4096 | 0.87s | 5.5MB | 0.439 | 15.93 | -0.604 |
| 8192 | 7.01s | 10.9MB | 0.365 | 23.38 | -0.840 |

### 测试

**55 passed · verify ALL PASSED · dynamics DYNAMICS_OK**

### 文档

- 踩坑记录：`docs/PITFALLS.md`
- 意识立场：`docs/CONSCIOUSNESS.md`
- 总目标：`docs/GOALS.md`
- 文献：`docs/LITERATURE.md` + `docs/意识与认知科学文献整理/`
