# LIDA: A Computational Model of Global Workspace Theory and Developmental Learning（LIDA：全局工作空间理论与发展学习的计算模型）

## 基本信息

- **原始链接**：https://ccrg.cs.memphis.edu/assets/papers/LIDA%20paper%20Fall%20AI%20Symposium%20Final.pdf
- **访问状态**：可访问（HTTP 200，PDF文件）
- **访问时间**：2026-09-12
- **文献类型**：会议论文（PDF）
- **会议**：AAAI Fall Symposium（美国人工智能协会秋季研讨会）
- **发表年份**：2007年
- **版权**：© 2007, Association for the Advancement of Artificial Intelligence (AAAI)
- **作者**：Stan Franklin、Uma Ramamurthy、Sidney K. D'Mello、Lee McCauley、Aregahegn Negatu、Rodrigo Silva L.、Vivek Datla
- **作者单位**：孟菲斯大学智能系统研究所和计算机科学系，美国田纳西州孟菲斯38152
- **通讯邮箱**：franklin@memphis.edu

## 摘要

本文介绍了LIDA——一个机器意识的工作模型和理论基础。LIDA的架构和机制受到多种计算范式的启发，LIDA实现了意识的全局工作空间理论（Global Workspace Theory, GWT）。LIDA架构的认知模块包括知觉联想记忆、情景记忆、功能意识、程序记忆和行动选择。由LIDA架构控制的认知机器人和软件代理将具备多种学习机制。以人工感觉和情绪作为主要动机和学习促进者，此类系统将"经历"一个发展期，在此期间它们将以多种类似人类的方式学习如何在其环境中有效行动。本文还提供了LIDA模型与其他意识模型的比较。

## 正文内容

### 引言

LIDA（Learning IDA，学习型IDA）是意识和认知的模型。LIDA实现了全局工作空间理论（GWT）（Baars 1988; 1997），该理论已成为最广泛接受的意识心理学和神经生物学理论（Baars 2002; Dehaene & Naccache 2001; Kanwisher 2001）。

在实现GWT的过程中，LIDA模型还实现了：
- **想象**：以深思（deliberation）作为行动选择的手段（Franklin 2000a; Sloman 1999）
- **意志**（volition）：基于意念运动理论（ideomotor theory，Franklin 2000a; James 1890）

LIDA构成了软件代理（Franklin & Graesser 1997）以及潜在自主机器人（Franklin & McCauley 2003）的完整控制结构。计算型LIDA可被视为构建在一系列其他虚拟机之上的虚拟机（Sloman & Chrisley 2003）：Java开发环境、操作系统、微码等。

LIDA模型始终使用感觉和情绪，既作为动机（Sloman 1987），也作为学习的调节剂。凭借对多种学习形式的强调，LIDA控制的软件代理或自主机器人预计将经历发展期（Franklin 2000b），如同人类婴儿。在此期间，代理/机器人将发展自己的本体论。

LIDA模型明确属于具身或生成认知方法（Varela, Thompson, & Rosch 1991），与许多其他心理学理论一致（Baddeley 1993; Barsalou 1999; Conway 2002; Ericsson & Kintsch 1995; Glenberg 1997）。

### 作为GWT模型的LIDA

全局工作空间理论（GWT）将大量证据整合到一个聚焦于意识在人类认知中作用的概念框架中。

**GWT的核心主张**：
1. 人类认知由大量相对较小的专用处理器实现，几乎总是无意识的（Edelman 1987; Jackson 1987; Minsky 1985; Ornstein 1986）
2. 处理器相对简单，处理器之间的通信相对罕见，通过窄信号带宽发生
3. 处理器联盟（coalition）是协同工作以执行特定任务的集合
4. 大脑支持全局工作空间容量，允许整合和分发独立处理器
5. 获得全局工作空间访问权的处理器联盟可以向所有无意识处理器广播消息，以招募新组件来解释新异情境或解决当前问题

GWT解释了：
- 意识为何处理习惯化无意识过程无法有效处理的新异或有问题情境
- 与意识体验、即时记忆和即时目标相关的认知有限容量悖论——补偿优势是以非常规方式动员许多无意识资源应对新异挑战的能力
- 意识为何是串行的而非并行的——并行广播的消息往往相互覆盖
- 意识的有限容量与长时记忆的巨大容量形成对比

**LIDA作为GWT的概念验证模型**：
- 模型中几乎所有任务由codelets（小代码段，Hofstadter & Mitchell 1994）完成，代表GWT中的处理器
- **注意codelets**：每个都留意其感兴趣的情境，试图将它们带入"意识"聚光灯
- 然后发生广播，招募资源处理当前情境
- LIDA通过后文描述的认知循环实现GWT中意识的串行性
- LIDA模型处理广泛的认知过程：知觉、各种记忆系统、行动选择、发展学习机制、感觉与情绪、深思、意志行动、非常规问题解决和自动化

### LIDA架构

LIDA架构部分是符号的，部分是联结主义的，所有符号都以Brooks（1986）的方式根植于物理世界。实现多个模块的机制受到多种"新AI"技术的启发（Brooks 1986; Drescher 1991; Hofstadter & Mitchell 1994; Jackson 1987; Kanerva 1988; Maes 1989）。

#### 1. 知觉联想记忆（Perceptual Associative Memory）

LIDA以外源和内源方式感知，以Barsalou的知觉符号系统（1999）为指导。该代理的知觉知识库称为知觉联想记忆，采取称为slipnet的带激活语义网形式（Hofstadter和Mitchell的Copycat架构，1994）。

- Slipnet的节点构成代理的知觉符号，代表个体、类别、关系等
- 任何节点都可追溯到其原始特征检测器，这些检测器根植于现实并根据代理的传感器变化
- 包含节点和链接的slipnet片段，加上负责将当前感知内容复制到工作记忆的知觉codelets，构成Barsalou的知觉符号模拟器（1999）
- 共同构成LIDA的整合知觉系统，使系统能够识别、分类和理解

#### 2. 工作空间（Workspace）

LIDA的工作空间类似于人类工作记忆的前意识缓冲器。
- 知觉codelets和其他更内部的codelets写入工作空间
- 注意codelets观察写入工作空间的内容以做出反应
- 工作空间中的项目随时间衰减，可能被覆盖
- 工作空间的另一个关键作用是在多个认知循环上构建临时结构
- 来自slipnet的知觉符号被同化到现有的关系和情境模板中，同时保持符号之间的空间和时间关系
- 工作空间中的结构也迅速衰减

#### 3. 情景记忆（Episodic Memory）

LIDA架构中的情景记忆由以下组成：
- **陈述性记忆**：用于长期存储自传体和语义信息
- **短暂情景记忆**（transient episodic memory）：类似于Conway（2001）的感觉-知觉情景记忆，保留率以小时计

LIDA采用稀疏分布记忆（sparse distributed memory, SDM）的变体来计算建模陈述性和短暂情景记忆（Kanerva 1988; Ramamurthy, D'Mello, & Franklin 2004）。SDM是一种内容可寻址的联想记忆，与人类长时记忆共享若干功能相似性。

#### 4. 功能意识（Functional Consciousness）

LIDA的"意识"模块通过codelets实现全局工作空间理论（Baars 1988）的过程。这些codelets专门用于某些简单任务，通常扮演守护进程的角色，监视适当的行动条件。

功能"意识"的装置包括：
- 联盟管理器（coalition manager）
- 聚光灯控制器（spotlight controller）
- 广播管理器（broadcast manager）
- 识别新异或有问题情境的注意codelets

#### 5. 程序记忆（Procedural Memory）

LIDA中的程序记忆是Drescher图式机制（1991）的修改和简化形式——scheme net。与知觉联想记忆的slipnet一样，scheme net是有向图，其节点是（行动）图式，链接代表"派生自"关系。

- 内置的原始（空）图式直接控制效应器，类似于控制人类肌肉群的运动细胞集合
- 图式由行动及其上下文和结果组成
- scheme net的外围是空图式（简单行动，无上下文或结果），向内移动时发现由行动和行动序列组成的更复杂图式
- 图式要行动，首先需要被实例化，然后根据下文描述的行动选择机制被选择执行

#### 6. 行动选择（Action Selection）

LIDA架构采用Maes行为网（1989）的增强版进行高级行动选择，服务于感觉和情绪。

- 几种不同的感觉和情绪并行运作，可能随时间流逝和环境变化而在紧迫性上变化
- 行为网是由行为（实例化的行动图式）及其各种链接组成的有向图
- 与联结主义模型一样，该有向图传播激活
- 激活来自四个来源：行为中存储的预先存在的激活、环境、感觉和情绪、内部状态
- 要被执行，行为必须是可执行的、激活超过阈值、且具有最高的此类激活

### LIDA认知循环

每个自主代理（人类、动物、软件代理或机器人）在复杂动态环境中都必须频繁且循环地采样（感知）环境并对其行动，这被称为认知循环（Franklin et al., 2005）。

认知循环是灵活的、串行但重叠的活动循环，通常从知觉开始，以行动结束。据信人类的认知循环每秒发生5到10次，级联使得相邻循环中的某些步骤并行发生（Baars & Franklin 2003）。意识广播中保持串行性。

**认知循环的九个步骤**：

1. **知觉**（Perception）：接收和解释外部或内部感觉刺激，产生意义的开端
2. **知觉到前意识缓冲**（Percept to preconscious buffer）：知觉（包括一些数据加意义以及可能的关系结构）存储在LIDA工作记忆的前意识缓冲中，构建临时结构
3. **局部联想**（Local associations）：使用传入知觉和工作记忆残余内容（包括情绪内容）作为线索，从短暂情景记忆和陈述性记忆中自动检索局部联想，存储在长时工作记忆中
4. **意识竞争**（Competition for consciousness）：注意codelets查看长时工作记忆，将新异、相关、紧急或坚持的事件带入意识
5. **意识广播**（Conscious broadcast）：codelets联盟（通常是一个注意codelet及其携带内容的相关信息codelets群）获得全局工作空间访问权并广播其内容。在人类中，这种广播被假设对应于现象意识
6. **资源招募**（Recruitment of resources）：相关图式响应意识广播。这些通常是上下文与意识广播中信息相关的图式。意识因此解决了招募资源的相关性问题
7. **设置目标上下文层级**（Setting goal context hierarchy）：被招募的图式使用意识内容（包括感觉/情绪）将新的目标上下文层级（自身副本）实例化到行为网中，绑定其变量并增加其激活。其他环境条件决定哪些较早的目标上下文也接收变量绑定和/或额外激活
8. **行动选择**（Action chosen）：行为网从刚实例化的行为流或可能先前活跃的流中选择单个行为（图式、目标上下文）。每个行为选择包括生成一个期望codelet
9. **行动执行**（Action taken）：行为（目标上下文）的执行导致行为codelets执行其专门任务，产生外部或内部后果或两者。行动codelets还包括至少一个期望codelet，其任务是监视行动，将预期结果的任何失败带入意识

### LIDA中的多循环过程

高阶认知过程（如推理、问题解决、想象等）在LIDA中跨越多个认知循环发生。

#### 深思（Deliberation）

当面对要解决的问题时，人类常在心中创造不同的策略或可能解决方案，想象执行每种策略的效果而不实际执行。最终选择一种策略并尝试解决问题。这一过程称为深思（Sloman 1999）。

在深思过程中，几个可能冲突的想法竞争被选为问题的策略或解决方案。其中一个被自愿选择。LIDA中的深思通过利用意识信息创建场景并评估其效用来实现（Franklin 2000b）。

#### 意志行动（Voluntary Action）

意志行动涉及对采取行动决定的有意识深思。William James提出了意志行动的意念运动理论（1890）：任何进入心中（进入意识）的行动想法（内部提议）都会被执行，除非它激起一些反对想法或反提议。GWT"原样"采用James的意念运动理论（Baars 1988）并为其提供功能架构。LIDA模型提供了实现意念运动意志理论的底层机制（Franklin 2000b）。

决策过程的参与者包括提议和反对注意codelets以及计时codelet：
- 提议注意codelet的任务是基于其特定偏好模式提议某个行动
- 提议注意codelet将关于自身和提议行动的信息带入"意识"
- 如果没有其他反对注意codelet反对（通过将自身带入"意识"并带有反对信息），且在给定时间跨度内没有其他提议注意codelet做出不同提议，计时codelet将决定提议的行动
- 如果及时提出反对或新提议，计时codelet停止计时或为新提议重置计时

#### 非常规问题解决（Non-Routine Problem Solving）

借助意识机制，LIDA能够处理常规情境的新异实例。但为有效处理新异、有问题和意外情境，模型需要某种形式的非常规问题解决。

非常规问题解决通常指设计解决新异有问题情境的方案的能力。这种解决方案通常称为"meshing"，人类利用先验知识块获得新异问题的解决方案（Glenberg 1997）。

非常规问题解决与经典AI中的规划类似，但经典AI规划假设所有个体算子持续可供考虑，而我们由于其认知不可信性不做此假设。相反，我们的方法依赖意识招募可能与解决方案相关的无意识知识片段。LIDA架构中的非常规问题解决最好被视为在多个循环上运作的独特行为流，每个循环塑造部分行动计划。

#### 自动化（Automatization）

自动化指人类（和动物）将程序任务学习到无需意识干预即可完成的程度的能力。由于意识是有限资源，自动化任务释放这一资源用于更紧迫的认知活动。

在LIDA架构中，部分行动计划由行为流（目标上下文层级，由大致按序列运作的行为组成）表示。对于非自动化任务，需要意识来招募执行实例化流中的下一个行为。自动化在LIDA中通过流中的行为自动建立彼此关联来实现，从而消除意识干预的需要。

一旦任务自动化，个体行为的执行由期望codelets监视。当注意到执行失败并将此信息带入意识时，去自动化过程被招募以暂时暂停自动化，从而恢复意识干预（Negatu, McCauley, & Franklin, in review）。

### LIDA中的发展学习

LIDA模型实现了支撑人类学习大部分的三种基本学习机制：
1. **知觉学习**（perceptual learning）：学习新对象、类别、关系等
2. **情景学习**（episodic learning）：学习事件的内容、时间和地点
3. **程序学习**（procedural learning）：学习新行动和行动序列以完成新任务

三种学习机制共享两个基本前提：
- **前提一**：意识觉知足以进行学习。虽然阈下信息获取似乎发生，但效应量与意识学习相比较小。经典研究中，Standing（1973）表明10,000张不同图片在每张仅5秒意识暴露后可以96%的识别准确率被学习，不需要学习意图。有意识学习的教育材料在50年后仍可回忆（Bahrick 1984）。
- **前提二**：学习受感觉和情绪调节，即学习率随唤醒变化（Yerkes & Dodson 1908）。

发展学习在LIDA中发生在意识广播期间（认知循环的第5步）。意识广播包含意识的全部内容，包括情感部分：
- 知觉联想记忆的内容根据当前意识内容（包括感觉/情绪以及对象、类别和关系）更新（知觉学习）。在一定程度上，情感越强，记忆编码越强
- 短暂情景记忆也用当前意识内容（包括感觉/情绪）作为事件更新（情景学习）
- 程序记忆（最近行动）被更新（强化），强化强度受情感强度影响（程序学习）

### 与其他模型的比较

#### CLARION vs. LIDA

CLARION（Connectionist Learning with Adaptive Rule Induction ON-line，Sun 2003）采取意识的双系统观点：意识过程（顶层知识）可直接访问，无意识过程（底层知识）不可访问。相比之下，LIDA采取意识和无意识的单一系统观点。LIDA实现GWT的观点，即意识的主要功能是解决相关性问题——找到处理当前情境所需的资源。

CLARION支持工作记忆、语义记忆和情景记忆等多种记忆系统；LIDA有独特的短暂情景记忆（TEM），基于只有意识内容存储在TEM中以便稍后巩固到陈述性记忆的假设。两种模型都支持各种学习机制，而发展学习能力存在于LIDA模型中。LIDA还支持深思、意志行动、非常规问题解决和自动化等多循环过程。

#### Schacter模型 vs. LIDA

Schacter模型（1990）在系统中各种知识类型的分离方面有强烈的神经心理学动机。不同知识模块执行专门的无意识任务，并将输出发送到"意识觉知系统"。LIDA的意识觉知方法明显不同：在LIDA中，要采取的行动在意识广播之后被选择。此外，Schacter模型中意识和无意识过程之间没有明确的计算区分。

#### Damasio模型 vs. LIDA

Damasio模型（1990）是神经解剖学动机的，有几个"感觉汇聚区"通过前向和后向突触连接整合来自感觉模态的信息。激活穿过整个系统，产生的"广播"使关于实体存储的信息可用。这被描述为"意识的可及性"。该模型没有中央信息存储。相比之下，LIDA有一个"意识"模块来实现功能意识。Damasio模型在所处理的认知机制范围上比LIDA窄得多。但Damasio模型的一个优势是它处理了多感觉汇聚，这在LIDA模型的知觉模块中尚未明确处理。

#### Cotterill模型 vs. LIDA

Cotterill（1997）的"主模块"意识模型假设意识从运动规划中涌现。系统中的主模块是大脑的运动规划器。运动是该模型的核心方面。在这一点上可与LIDA比较，LIDA的认知循环持续行动和感知环境。LIDA在认知建模范围上比主模块模型广得多。

#### ICARUS vs. LIDA

与LIDA类似，ICARUS架构（Langley, P., in press）在认知建模范围上具有可比性。ICARUS基于Newell（1990）的观点，即代理架构应包含关于心灵本质的强理论假设。LIDA也是如此，试图整合我们从神经科学、认知科学和AI中对认知的了解。

ICARUS有长时和短时多种记忆系统，类似于LIDA。它有单独的"技能或程序"记忆模块，类似于LIDA的程序记忆。与CLARION类似，ICARUS中没有短暂情景记忆系统（在LIDA中发挥独特作用），尽管该模型的短时记忆中有知觉和运动缓冲。

ICARUS有概念推理、技能执行和问题解决的单独性能模块，这些模块在架构的子系统/结构上相互关联。ICARUS有一个学习模块，每当通过问题解决和执行实现目标时生成新技能。与LIDA相比，ICARUS没有多种学习机制，学习是增量式的，没有发展学习，也没有提及"意识"或觉知模块。

### 结论

本文将LIDA模型作为意识模型（MoC）的案例研究呈现，并与其他MoC进行比较。比较表明许多模型中存在若干可能的缺陷，其中许多或大部分可以被填补以改进模型。

**建议的缺陷**：
1. **具身/生成/情境观点**：AI和认知科学都在迅速走向智能和认知的具身/生成/情境观点。LIDA从感觉开始，以行动结束，而许多其他模型假设感觉/知觉已提供，仅建模高级过程，从而冒避开与知觉相关的真正重要问题的风险。
2. **全局工作空间理论**：GWT已成为当前主导的意识生物心理学理论。LIDA实现了GWT的主要部分。Dehaene和Shanahan的理论是仅有的其他利用GWT洞见（特别是其对相关性问题的解决方案，意识的主要功能）的MoC。
3. **学习与发展**：学习和发展正成为认知建模（计算和概念）中日益重要的部分，多种学习形式构成LIDA模型的组成部分。讨论的大多数其他MoC提供某种形式的程序学习（通常通过强化的选择主义程序学习），有些还包括指令主义程序学习。情景学习包含在少数其他MoC中，而知觉学习几乎普遍被遗漏。
4. **意志与深思**：LIDA模型实现意识意志和深思（一种想象形式）的多循环过程，在与之比较的其他MoC中似乎是独特的。

**与人类的比较揭示更多缺陷**：LIDA缺少元认知、大约六种自我感觉、注意学习，以及大量多循环认知过程，还有新技能如何首先在意识积极参与下学习、后来进展为完全无意识运作的感觉-运动自动性的清晰说明（Goodale and Milner 2004）。

## 关键结论

1. LIDA是实现全局工作空间理论（GWT）的机器意识计算模型，由孟菲斯大学Stan Franklin团队开发。
2. LIDA架构包含六大认知模块：知觉联想记忆、工作空间、情景记忆、功能意识、程序记忆、行动选择。
3. LIDA认知循环包含九个步骤，从知觉开始到行动执行结束，每秒发生5-10次，意识广播保持串行性。
4. LIDA实现四种多循环高阶认知过程：深思、意志行动、非常规问题解决、自动化。
5. LIDA支持三种基本学习机制（知觉学习、情景学习、程序学习），均在意识广播期间发生，受感觉和情绪调节。
6. LIDA以人工感觉和情绪为主要动机和学习促进者，经历类似人类婴儿的发展期。
7. 与CLARION、Schacter、Damasio、Cotterill、ICARUS等模型相比，LIDA在GWT实现、发展学习、意志与深思的多循环过程方面具有独特性。
8. LIDA仍缺少元认知、多种自我感觉、注意学习等人类认知能力。

## 参考文献（部分）

本文引用大量认知科学和AI文献，关键引用包括：
- Baars (1988) A Cognitive Theory of Consciousness, Cambridge University Press
- Baars (1997) In the Theatre of Consciousness, Oxford University Press
- Baars & Franklin (2003) How conscious experience and working memory interact, Trends Cogn Sci
- Barsalou (1999) Perceptual symbol systems, Behavioral and Brain Sciences
- Brooks (1986) A robust layered control system for a mobile robot, IEEE J Robotics Automation
- Dehaene & Naccache (2001) Towards a cognitive neuroscience of consciousness, Cognition
- Drescher (1991) Made Up Minds: A Constructivist Approach to Artificial Intelligence, MIT Press
- Franklin (2000a) Deliberation and voluntary action in LIDA
- Hofstadter & Mitchell (1994) The Copycat project
- James (1890) The Principles of Psychology
- Kanerva (1988) Sparse Distributed Memory
- Maes (1989) How to do the right thing
- Sloman (1999) What are the design options for human-like agents?
- Varela, Thompson & Rosch (1991) The Embodied Mind
