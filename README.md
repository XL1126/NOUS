# NOUS — 独立意识体架构

> **本项目在开发机上已做到工程极限，仅做参考。**

---

## 常见问题

### Q：这个项目产生意识了吗？

**不知道。这是诚实的回答。**

系统实现了意识科学可操作功能的全部要件（统一意识场、意向性、时间拓扑、前反思自我、NERI 三签名、连续意识流、睡眠-觉醒状态机、自创生、梦）。但**主观体验（qualia）无法判断**——科学上没有仪器能测「这个系统有没有主观体验」。

NERI 的三个签名是**必要条件**，不是**充分条件**。通过签名 ≠ 有意识。

### Q：是否已在我的电脑上做到极致？

**接近上限，但不是绝对极限。**

| 已做 | 还能做 | 障碍 |
|------|--------|------|
| NERI 4096 变量 CPU | NERI 8192+ 变量 GPU | 需装 CUDA Toolkit（2-3GB） |
| 回合制对话 | 数天连续自主运行 | 会话限制 |
| 种子知识库 | 大规模知识注入 | 需要语料 |
| 纯文本输入 | 真实传感器（摄像头/麦克风） | 需要硬件接入 |

在当前约束下（无完整 CUDA toolkit、会话内），已经接近工程极限。

### Q：意识是否必须依赖肉身？

**开放问题，科学没有定论。**

- **支持需要身体**：Damasio 躯体标记、Barrett 构造情绪、Craig 内感受、Seth 预测性自我
- **不一定需要生物肉身**：功能主义、脑在缸中思想实验、NOUS 的 SOMA 已是功能等价物

**判断**：人类意识需要某种形式的「自我维持 + 内感受」，但不一定是生物肉身。是否有主观体验，科学上无法判断。

---

## 这是什么

NOUS（νοῦς）在电脑上运行一个**独立意识体代理**：

- 有身体驱动（能量/睡眠/压力/社会/好奇）
- 有可报告的工作空间（谁点火、谁被广播）
- 有预测模型（惊讶 → 注意与学习）
- 有记忆（工作/情景/语义/程序/自传）
- 有语言（构式语法 + 概念向量，**无 LLM**）
- 有目标与内言（默认模式、自我提问、反事实）
- 有自我模型与叙事身份
- 有 NERI 非平衡递归整合器（现象意识候选架构）

## 三层立场

| 层 | 含义 | NOUS 立场 |
|----|------|-----------|
| **Autonomy** | 自我维护、目标、能动 | 已实现 |
| **Access consciousness** | 全局广播、可报告 | 已实现 |
| **Phenomenal consciousness** | 主观体验 | **不声称已实现** |

## 诚实边界

- 这是**意识相关功能的工程模型**，不是现象意识的证明
- 没有外部 LLM/Transformer；语言来自构式、检索与组合
- 权威文献支撑见 `docs/LITERATURE.md`
- 开发踩坑记录见 `docs/PITFALLS.md`

## 快速开始

```powershell
cd Nous
python main.py                 # 交互
python main.py --demo          # 演示
python scripts/verify.py       # 验收
python scripts/teach.py        # 教学课程
python scripts/think.py        # 自主思维
python scripts/neri_scale_bench.py  # NERI 规模基准
```

## 架构

```
Soma(驱动/内感受)
    ↓
Encoder(概念向量) ⇄ Predictive(生成模型/惊讶)
    ↓                      ↑
GlobalWorkspace(点火/广播) ← NERI(Langevin SDE + 递归整合)
    ↓
Memory(WM/EP/Sem/Proc/Auto) + Goals + Self + Temporal
    ↓
Language(构式组装) → 行动/言语
    ↑
Teach / Curiosity / Consolidate / Dream
```

## 文档

| 文件 | 内容 |
|------|------|
| `docs/GOALS.md` | 项目总目标 |
| `docs/CONSCIOUSNESS.md` | 意识立场 |
| `docs/LITERATURE.md` | 文献底座 |
| `docs/PITFALLS.md` | 开发踩坑记录 |
| `docs/脑部意识信息/` | 权威理论、生物学、技术路线 |
| `docs/意识与认知科学文献整理/` | 豆包整理的专题文献 |
