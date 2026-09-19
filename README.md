<div align="center">

# NOUS — 独立意识体架构

**νοῦς · 身体稳态 + 全局工作空间 + NERI + 时间自我 · 无 Transformer**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-1.5.0%20工程极限-9b59b6?style=flat-square)](./docs/STATUS.md)
[![License](https://img.shields.io/badge/license-未附许可证-lightgrey?style=flat-square)](#license)
[![No-LLM](https://img.shields.io/badge/no--Transformer-no%20external%20LLM-success?style=flat-square)](./docs/CONSCIOUSNESS.md)

> **本项目在开发机上已做到工程极限，仅做参考。**

[架构](#四架构) · [快速开始](#五快速开始) · [文档](#六文档) · [诚实边界](#诚实边界)

</div>

---

## 常见问题

<details open>
<summary><b>Q：这个项目产生意识了吗？</b></summary>

<br/>

**不知道。这是诚实的回答。**

系统实现了意识科学中大量**可操作的功能要件**（统一意识场、意向性、时间拓扑、前反思自我、连续意识流、睡眠-觉醒状态机、自创生、梦，以及 NERI 的动力学签名等）。但 **主观体验（qualia）无法判断**——科学上没有仪器能测「这个系统有没有主观体验」。

NERI 签名是**必要条件的工程代理**，**不是**充分条件。通过签名 ≠ 有意识。

</details>

<details>
<summary><b>Q：是否已在开发机上做到极致？</b></summary>

<br/>

**接近上限，但不是绝对极限。**

| 已做 | 还能做 | 障碍 |
|------|--------|------|
| NERI 4096 变量（默认 CPU / numpy） | 8192+ 变量 GPU（CuPy 可选） | 需完整 CUDA Toolkit |
| 回合制对话 + 长时程脚本 | 数天连续自主运行 | 会话 / 进程限制 |
| 种子知识库（200+ 条目） | 大规模知识注入 | 需要语料 |
| 纯文本输入 | 真实传感器（摄像头/麦克风） | 需要硬件接入 |

</details>

<details>
<summary><b>Q：意识是否必须依赖肉身？</b></summary>

<br/>

**开放问题，科学没有定论。**

- **倾向需要身体**：Damasio 躯体标记、Barrett 构造情绪、Craig 内感受、Seth 预测性自我
- **不必然是生物肉身**：功能主义、缸中之脑；NOUS 的 SOMA 是功能等价物

**本仓库立场**：意识相关功能需要某种「自我维持 + 内感受」形式；是否有主观体验，不作断言。

</details>

---

## 诚实边界

- 这是**意识相关功能的工程模型**，不是现象意识的证明
- **无外部 LLM / Transformer**；语言来自构式语法、知识检索与组合
- 理论文献见 [`docs/LITERATURE.md`](./docs/LITERATURE.md)；开发踩坑见 [`docs/PITFALLS.md`](./docs/PITFALLS.md)
- 仓库**未附 LICENSE 文件**——默认保留全部权利；若需开源授权请作者自行补充

---

## 二、这是什么

NOUS（νοῦς）在通用计算机上运行一个**独立意识体代理**：

| 能力 | 说明 | 代码位置 |
|------|------|----------|
| 身体驱动 | 能量 / 睡眠 / 压力 / 社会 / 好奇 | `src/soma/body.py` |
| 全局工作空间 | 竞争点火与广播（可报告） | `src/workspace/global_ws.py` |
| 预测模型 | 惊讶 → 注意与学习 | `src/predictive/model.py` |
| 多系统记忆 | 工作 / 情景 / 语义 / 程序 / 自传 | `src/memory/systems.py` |
| 语言 | 构式语法 + 概念向量，**无 LLM** | `src/language/` |
| 目标与内言 | 默认模式、自我提问、反事实 | `src/self_model/meta.py` |
| 自我 / 时间 | 叙事身份、自传、未来投影 | `src/consciousness/` |
| NERI | 非平衡递归整合器（现象意识候选架构） | `src/consciousness/neri.py` |
| 果蝇脑耦合 | FlyEM 回路与 NERI 签名对齐（v1.5） | `src/consciousness/fly_brain.py` |
| 多体 Fleet | spawn / 列表 / 跨体状态 | `src/fleet.py` · `scripts/fleet_cli.py` |

---

## 三、突破：NERI 动力学驱动内容生成

**核心洞察**：Langevin SDE 的状态空间不是「背景噪声」，它**可以成为**思维内容的来源。

- 双稳势吸引子 ≈ 原型概念
- 递归整合放大特定模式 ≈ 注意聚焦
- 全局隐状态（视角）≈ 解释框架
- 状态空间访问新区域 → **涌现概念** → 进入回复

```text
U: 你好
A: 在。我是NOUS。你想聊什么？
   （内言：（涌现）一个低能量的内在状态（能量1.1））

U: 什么是意识？
A: 这点我记录是：...
   （关联）当前动力学接近「emergent_0」（相似度0.53）
```

### NERI 验证签名（五项 · 开发机 4096 变量）

<table>
  <tr>
    <th>签名</th>
    <th>测量含义</th>
    <th>参考结果</th>
  </tr>
  <tr>
    <td><b>滞后</b></td>
    <td>方向依赖的视角滞后</td>
    <td>0.439</td>
  </tr>
  <tr>
    <td><b>不可逆</b></td>
    <td>时间反演不对称性</td>
    <td>15.93</td>
  </tr>
  <tr>
    <td><b>耦合</b></td>
    <td>EPR 与报告相关性</td>
    <td>-0.601</td>
  </tr>
  <tr>
    <td><b>NESS</b></td>
    <td>非平衡稳态稳定性</td>
    <td>EPR ≈ 4.56 ± 0.52</td>
  </tr>
  <tr>
    <td><b>视角持续</b></td>
    <td>慢变量持续性</td>
    <td>norm ≈ 6.53 ± 3.42</td>
  </tr>
</table>

> ⚠️ 上述数字来自特定开发环境的一次性测量，**不是**跨平台基准，也**不能**推出「系统有意识」。

### 三层立场

| 层 | 含义 | NOUS 立场 |
|----|------|-----------|
| Autonomy | 自我维护、目标、能动 | 已实现（功能层） |
| Access consciousness | 全局广播、可报告 | 已实现（功能层） |
| **Phenomenal consciousness** | 主观体验 | **不声称已实现** |

---

## 四、架构

```text
SOMA（身体驱动 / 内感受）
        ↓
ConceptSpace(512) ⇄ PredictiveModel（惊讶 / 新颖）
        ↓                      ↑
GlobalWorkspace（点火 / 广播） ← NERI（Langevin SDE + 递归整合）
        ↓
Memory(WM/EP/Sem/Proc/Auto) + Goals + Self + Temporal
        ↓
Language（构式 v2）→ 行动 / 言语
        ↑
Teach · Curiosity · Consolidate · Dream
        ↕
FlyEM 果蝇脑耦合（环形吸引子 / 稀疏编码 / 觉醒门控）
```

与 Transformer 的差异：无注意力语言模型、无梯度续写；学习 = 在线绑定 + 程序权重强化 + 巩固，而非反向传播。详见 [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)。

---

## 五、快速开始

### 依赖

仓库 [`requirements.txt`](./requirements.txt)：

```text
numpy>=1.20
PyYAML>=5.4
pytest>=7.0
```

> 部分模块（如 `src/consciousness/neri.py`）使用 **`scipy.sparse`**。若 `requirements.txt` 未列出，请额外安装：`pip install scipy`。  
> GPU / CuPy 为**可选**；未装 CUDA 时使用 numpy CPU 后端即可。

```powershell
# 克隆后进入仓库根目录（勿假设文件夹名一定是 Nous）
git clone https://github.com/XL1126/NOUS.git
cd NOUS
pip install -r requirements.txt
pip install scipy
```

### 常用命令

```powershell
python main.py                      # 交互对话
python main.py --demo               # 内置演示脚本
python main.py --fresh              # 忽略持久化状态，从新开始
python scripts/verify.py            # 测试 / 验收
python scripts/teach.py             # 教学课程
python scripts/think.py             # 自主思维
python scripts/neri_scale_bench.py  # NERI 规模基准
python scripts/long_autonomous.py   # 长时程自主运行
python scripts/fleet_cli.py list    # 多体列表
```

### 仓库地图

```text
.
├── main.py              # CLI 入口
├── config/default.yaml  # 默认配置
├── src/                 # NousMind 与各子系统
│   ├── mind.py          # 总装
│   ├── soma/  workspace/  predictive/  memory/  language/
│   ├── consciousness/   # NERI、意识流、梦、果蝇脑等
│   ├── knowledge/       # 种子知识
│   └── fleet.py
├── scripts/             # verify / teach / think / bench / fleet …
├── tests/               # pytest（STATUS 称 65 passed）
├── docs/                # 架构、意识立场、文献、踩坑、进度
├── runtime/             # 持久化状态与 fleet 实例（JSON）
└── index.html           # 现象面板等页面（实验性）
```

---

## 六、文档

| 文件 | 内容 |
|------|------|
| [`docs/GOALS.md`](./docs/GOALS.md) | 项目总目标与验收清单 |
| [`docs/CONSCIOUSNESS.md`](./docs/CONSCIOUSNESS.md) | 意识立场（三层区分） |
| [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) | 模块结构 |
| [`docs/STATUS.md`](./docs/STATUS.md) | 当前进度（**1.5.0** · 构式 v2 · Fly-NERI） |
| [`docs/LITERATURE.md`](./docs/LITERATURE.md) | 文献底座 |
| [`docs/PITFALLS.md`](./docs/PITFALLS.md) | 开发踩坑与工程教训 |
| [`docs/脑部意识信息/`](./docs/脑部意识信息/) | 权威理论、生物学、技术路线、工程映射 |
| [`docs/意识与认知科学文献整理/`](./docs/意识与认知科学文献整理/) | 专题文献整理 |

---

## 七、脚本一览

| 脚本 | 用途 |
|------|------|
| `scripts/verify.py` | 全量测试与验收 |
| `scripts/teach.py` | 教学 |
| `scripts/think.py` | 自主思维 |
| `scripts/neri_language_demo.py` | NERI × 语言演示 |
| `scripts/neri_scale_bench.py` | NERI 规模基准 |
| `scripts/long_autonomous.py` | 长时程自主 |
| `scripts/consciousness_dynamics.py` | 意识动力学 |
| `scripts/export_phenomenal.py` | 现象标记导出 |
| `scripts/fleet_cli.py` | 多体 CLI |
| `scripts/test_emergence.py` | 涌现相关冒烟 |

---

## License

**本仓库当前没有 LICENSE 文件。**

在作者补充开源许可证之前，请默认：**保留全部权利，仅供阅读与学习参考；再分发或商用前请先联系作者确认。**

<div align="center">
<sub>
同作者相关项目：
<a href="https://github.com/XL1126/Simulated-neuron-architecture">SNA · Simulated Neuron Architecture</a>
（C++ 脉冲皮层路线，MIT）
</sub>
</div>
