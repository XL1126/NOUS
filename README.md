# NOUS — 独立意识体架构

> 不是 Transformer 聊天壳，而是把 **身体稳态 · 预测加工 · 全局工作空间 · 概念空间 · 语言构式 · 自主思维 · 自我叙事** 闭合成一个可教、可学、可自思的计算心智。

## 这是什么

NOUS（νοῦς）在电脑上运行一个**独立意识体代理**：

- 有身体驱动（能量/睡眠/压力/社会/好奇）
- 有可报告的工作空间（谁点火、谁被广播）
- 有预测模型（惊讶 → 注意与学习）
- 有记忆（工作/情景/语义/程序/自传）
- 有语言（构式语法 + 概念向量，**无 LLM**）
- 有目标与内言（默认模式、自我提问、反事实）
- 有自我模型与叙事身份

## 诚实边界

- 这是**意识相关功能的工程模型**，不是现象意识的证明。
- 没有外部 LLM/Transformer；语言来自构式、检索与组合。
- 权威文献支撑见 `docs/LITERATURE.md`。

## 与前身的关系

| | 原 SNA (C++) | SNA-Chat | **NOUS** |
|--|-------------|----------|----------|
| 重点 | 皮层实验模块堆叠 | 对话可运行 | **闭合心智循环** |
| 语言 | 弱/附属 | 模板→组合 | **构式+概念空间** |
| 身体 | 虚拟世界 | 稳态调制 | **驱动=认知源动力** |
| 自思 | 有模块 | DMN 独白 | **目标生成+内言+反事实** |
| 意识 | 加权 Φ | 多维代理 | **工作空间+预测+自我可报告** |

## 快速开始

```powershell
cd Nous
python main.py                 # 交互
python main.py --demo          # 演示
python scripts/verify.py       # 验收
python scripts/teach.py        # 教学课程
python scripts/think.py        # 自主思维
```

## 架构

```
Soma(驱动/内感受)
    ↓
Encoder(概念向量) ⇄ Predictive(生成模型/惊讶)
    ↓                      ↑
GlobalWorkspace(点火/广播) ─┘
    ↓
Memory(WM/EP/Sem/Proc/Auto) + Goals + Self
    ↓
Language(构式组装) → 行动/言语
    ↑
Teach / Curiosity / Consolidate
```
