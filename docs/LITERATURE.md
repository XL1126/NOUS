# 文献底座（NOUS）

> 论文/专著驱动的架构选择。不声称实现全文，只实现可运行的工程对应物。  
> 完整检索报告见 `docs/脑部意识信息/07_联网检索报告_2026-09.md`。

## 1. 意识的全局工作空间

- Baars, B. J. (1988). *A Cognitive Theory of Consciousness*. — 舞台/广播隐喻
- Dehaene, S., & Naccache, L. (2001). Towards a cognitive neuroscience of consciousness. *Cognition*. — 点火+全局可及
- **Mashour, G. A., Roelfsema, P., Changeux, J.-P., & Dehaene, S. (2020). Conscious Processing and the Global Neuronal Workspace Hypothesis. *Neuron*, 105(5), 776–798.** DOI: 10.1016/j.neuron.2020.01.026
- **Cogitate Consortium et al. (2025). Adversarial testing of GNW and IIT. *Nature*, 642, 133–142.** DOI: 10.1038/s41586-025-08888-1 — **两理论核心预测都未完全通过；前额叶点火不可作唯一判据**

**工程对应**：候选竞争 → 点火阈值 → 广播到记忆/语言/目标；可报告内容=广播集。**COGITATE 约束**：不能只看前额叶点火；需后部持续整合 + 预注册证伪条件。

## 2. 预测加工 / 自由能

- Friston, K. (2010). The free-energy principle: a unified brain theory? *Nat Rev Neurosci*.
- Clark, A. (2013). Whatever next? Predictive brains, situated agents… *BBS*.
- Rao, R. P., & Ballard, D. H. (1999). Predictive coding in the visual cortex. *Nat Neurosci*.
- **Seth, A. K. (2021). *Being You*. Faber.** — 预测性自我、在场感
- **Schoeller, F. et al. (2024). Interoceptive technologies... *Neurosci Biobehav Rev*, 156, 105478.** DOI: 10.1016/j.neubiorev.2023.105478 — **内感受通道可驱动，可作为设定点漂移的内生来源**

**工程对应**：层级生成模型预测下一状态；预测误差驱动注意、学习率、新奇寻求；内感受预测误差 → 异稳态设定点漂移。

## 3. 身体与内感受（意识的情绪底座）

- Damasio, A. (1994). *Descartes' Error*. — 躯体标记
- Barrett, L. F. (2017). *How Emotions Are Made*. — 构造情绪
- Craig, A. D. (2002). How do you feel? Interoception… *Nat Rev Neurosci*.
- Sterling, P. (2012). *Allostasis: A theory of adaptive life*. — 异稳态

**工程对应**：SOMA 状态向量持续演化；情绪=内感受×评价的构造标签；异稳态漂移设定点。

## 3b. 丘脑皮层（意识枢纽）

- **Whyte, C. J., Redinbaugh, M. J., Shine, J. M., & Saalmann, Y. B. (2024). Thalamic contributions to the state and contents of consciousness. *Neuron*, 112(10), 1611–1625.** DOI: 10.1016/j.neuron.2024.04.019  
  - matrix → 觉醒 + 知觉阈值；core → 内容恒常；TRN → 除法归一化门控
- Sherman, S. M. & Guillery, R. W. (2002/2006). core 驱动 / matrix 调节
- **Grady, F. S. et al. (2022). A Century Searching for the Neurons Necessary for Wakefulness. *Front Neurosci*, 16, 930514.** DOI: 10.3389/fnins.2022.930514 — **无单一调质是意识开关**

**工程对应**：core/matrix/TRN 三角；调质=增益/设定点参数，非必要条件。

## 3c. 最小自我 / 时间意识

- **Metzinger, T. (2003). *Being No One*. MIT Press.** — 透明自我模型
- **Damasio, A. (1999). *The Feeling of What Happens*.** — 核心意识 vs 自传体自我
- **Frontiers Neural Circuits (2026). Self-other inference model.** DOI: 10.3389/fncir.2026.1781653 — **SOI 贝叶斯自我归属**
- Husserl / Varela 神经现象学 — retention / now / protention

**工程对应**：`self_pole`（SOI 贝叶斯更新）+ `temporal_topology`（retention/now/protention）。

## 4. 记忆与睡眠巩固

- Tulving, E. (1972). Episodic and semantic memory. — 情景/语义分离
- Buzsáki, G. (1989/2015). Hippocampal sharp wave ripples… — 离线重放
- Frankland, P. W., & Bontempi, B. (2005). The organization of recent and remote memories. *Nat Rev Neurosci*.

**工程对应**：WM 有限；情景按向量索引；睡眠=压缩+写自传+修剪弱联结。

## 5. 语义与组合语义（无 LLM）

- Eliasmith, C. (2013). *How to Build a Brain*. — SPA 语义指针
- Kanerva, P. (2009). Hyperdimensional computing. — 高维绑定
- Goldberg, A. E. (2006). *Constructions at Work*. — 构式语法
- Jackendoff, R. (2002). *Foundations of Language*.

**工程对应**：概念=单位向量；角色-填充绑定；语言=构式槽位填充+组合，不是预训练 LM。

## 6. 目标、认知控制、内在动机

- Miller, E. K., & Cohen, J. D. (2001). An integrative theory of prefrontal cortex function. *Annu Rev Neurosci*.
- Oudeyer, P.-Y., Kaplan, F., & Hafner, V. V. (2007). Intrinsic motivation systems for autonomous mental development. *IEEE TEC*.
- Schmidhuber, J. (2010). Formal theory of creativity, fun, and intrinsic motivation. *IEEE AMD*.

**工程对应**：目标栈；疲惫抢占；好奇=预测误差/知识空白驱动探索。

## 7. 元认知与自我模型

- Fleming, S. M., & Dolan, R. J. (2012). The neural basis of metacognitive ability. *Phil Trans R Soc B*.
- Christoff, K., et al. (2016). Mind-wandering as spontaneous thought. *Nat Rev Neurosci*. — DMN/自发思维
- Graziano, M. S. A., & Kastner, S. (2011). Human consciousness and its relationship to social neuroscience. *Front Psychol*. — 注意 schema

**工程对应**：置信=理解×不确定性；内言=自我提问；叙事身份=自传串。

## 8. 具身/生成认知与主动推理

- Varela, F., Thompson, E., & Rosch, E. (1991). *The Embodied Mind*.
- Friston, K., et al. (2017). Active inference: a process theory. *Neural Computation*.

**工程对应**：行动（含言语）选择=降低预期自由能/满足驱动；身体不是外设。

## 9. 发展与社会

- Tomasello, M. (2005). *Constructing a Language*. — 用法学习
- Meltzoff, A. N. (2007). ‘Like me’: a foundation for social cognition. *Dev Sci*.

**工程对应**：从非语言驱动 → 短语 → 多轮；OtherModel 跟踪对话者耐心/专长。

## 10. 与 Transformer 的刻意决裂

- Vaswani et al. (2017) 的注意力语言模型**不在本架构内**。
- 选择：符号-向量 + 构式 + 竞争工作空间 + 在线学习，换取可解释状态与身体闭环，而非开放域流畅续写。

---

实现时每条机制在代码注释/模块 docstring 中回链到上表编号。
