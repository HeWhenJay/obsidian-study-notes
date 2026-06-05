## 背景介绍

本节对应 PPT《5、多Agent系统.pptx》第 1-18 页，并参考配套 Markdown《多智能体系统构建1_____笔记.md》。这一段先讲多智能体系统（MAS）的基本概念、应用场景、失败原因、改进策略和框架对比，最后进入 AutoGen Studio 的开场。

前置内容是 [[AI Agent全景/AI Agent（1）]]、[[AI Agent全景/AI Agent（2）]]、[[AI Agent全景/AI Agent（3）]]：单 Agent 已经有规划、记忆、工具调用和执行闭环，多 Agent 则把这些能力拆成多个角色，通过通信和协作完成更复杂的任务。

本节先不要急着背框架命令，重点先建立一个判断：多 Agent 的难点不是“多开几个模型”，而是任务规格、角色边界、上下文交接、通信协议和结果验证是否设计清楚。

## 课程脉络

第 1-18 页的结构如下：

1. 多智能体系统概述。
2. 从 Agent 到 MAS 的演进。
3. MAS 定义和典型应用场景。
4. 斯坦福 Generative Agents “AI 小镇”项目。
5. MAS 失败原因和 MAST 失败分类。
6. MAS 改进策略。
7. 多智能体框架对比。
8. AutoGen 和 AutoGen Studio 开场。

配套 Markdown 的“望未”部分把学习路线概括得比较清楚：先回忆单智能体定义与基本架构，再理解多智能体定义、应用场景、红与黑、架构设计、上下文工程和框架对比。

## 从 Agent 到 MAS

课程先回顾 Agent：在人工智能领域，Agent 是能够感知环境、进行思考或决策，并通过执行器行动以达成目标的计算实体。

多智能体系统（Multi-Agent System，MAS）则是由多个自主 Agent 组成的计算系统。这些 Agent 在共享环境中存在，能够相互通信、协调行为，从而解决单个 Agent 难以完成的问题，或者以更高效、更鲁棒的方式完成任务。

PPT 用“深入市场研究报告”说明为什么需要 MAS：

- 数据搜集需要信息检索能力。
- 数据分析需要结构化分析和计算能力。
- 竞品调研需要行业理解和比较能力。
- 报告撰写需要表达和组织能力。
- 图表制作需要可视化和呈现能力。

如果把这些任务都交给一个 Agent，它要同时承担所有角色、记住所有上下文、判断所有中间结果，失败概率会很高。MAS 的思路是把复杂任务拆成多个角色，例如研究员、分析师、写作者、审稿者、项目协调者。

## AI 小镇和生成式智能体

PPT 第 8 页提到斯坦福 Generative Agents “AI 小镇”项目：

- 论文：[Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442)
- PPT 中给出的 PDF：[https://arxiv.org/pdf/2304.03442v1.pdf](https://arxiv.org/pdf/2304.03442v1.pdf)
- 项目地址：[joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents)

![[多Agent系统AI小镇论文项目链接.png]]

这篇论文的重点不是“做一个小镇游戏”，而是展示多个带有记忆、计划和反思能力的 Agent 如何在共享环境中产生可信的社会行为。论文摘要强调，Generative Agents 会把经历保存为自然语言记忆，动态检索相关记忆，并通过反思和计划生成后续行为。

论文中的架构图可以帮助理解“多 Agent 为什么离不开记忆和上下文工程”：

![[Generative Agents架构图.png]]

这张图的核心链路是：

```text
Perceive -> Memory Stream -> Retrieve -> Retrieved Memories -> Act
```

同时，Plan 和 Reflect 会把计划与反思结果重新写回 Memory Stream。也就是说，Agent 不是只看当前提示词行动，而是通过记忆流维持长期一致性。

## MAS 应用领域

PPT 第 9 页把 MAS 应用场景分成四类：

![[多Agent系统应用领域图.png]]

| 场景 | Agent 分工 | 学习价值 |
| --- | --- | --- |
| 软件开发 | 项目经理、开发人员、测试人员 | 用角色分工覆盖需求拆解、代码生成、调试和测试 |
| 智能营销 | 营销计划、内容生产、效果分析 | 让策略、内容和复盘形成闭环 |
| 供应链优化 | 销售预测、库存管理、物流调度 | 多业务节点之间协同决策 |
| 智能电网 | 传感器、控制器、执行器 | 感知、控制和动作形成反馈系统 |

这几个例子的共同点是：任务天然不是一步完成，而是需要多个角色在不同阶段交换信息、纠正偏差并产出最终结果。

## 多智能体的红与黑

PPT 第 10 页引用论文《Why Do Multi-Agent LLM Systems Fail?》：

- 论文地址：[https://arxiv.org/abs/2503.13657](https://arxiv.org/abs/2503.13657)
- 论文提出 MAST（Multi-Agent System Failure Taxonomy），用经验数据总结多个 MAS 框架中的失败模式。

![[多Agent系统MAST论文失败分类.png]]

该论文的 arXiv 摘要中提到，MAST-Data 覆盖 7 个流行 MAS 框架中的 1600+ 标注轨迹，并把失败模式归纳为 14 种，聚成 3 个大类：系统设计问题、智能体间不对齐、任务验证问题。

更清晰的失败分类图如下：

![[MAST失败分类图.png]]

可以把失败原因先记成三层：

| 失败类别 | 含义 | 典型表现 |
| --- | --- | --- |
| Poor Specification | 任务、角色或终止条件定义不清 | 不遵守任务规格、不遵守角色规格、重复步骤、丢失对话历史、不知道何时停止 |
| Inter-Agent Misalignment | Agent 之间没有对齐 | 对话重置、不追问澄清、任务跑偏、隐瞒信息、忽略其他 Agent 输入、推理和行动不匹配 |
| Task Verification | 验证机制不足 | 提前终止、没有验证或验证不完整、验证错误 |

PPT 第 11 页给出的关键结论是：MAS 的失败不仅是底层 LLM 模型能力的局限，更深层次的原因在于系统设计和组织协调失败。根本问题常常出在智能体交接：系统中的 Agent 无法有效共享上下文、协调工作或验证结果。

## MAST 研究流程

论文中的研究流程图可以作为理解 MAST 的补充：

![[MAST研究流程图.png]]

它的流程大致是：

1. 收集 MAS 执行轨迹。
2. 识别失败案例。
3. 人类标注者反复讨论并形成一致分类。
4. 构建失败分类体系。
5. 用 LLM Annotator 做可扩展的失败检测。

这个流程对工程实践有启发：做多 Agent 系统时，不应该只看最终答案对不对，还要记录 Agent 之间的交互轨迹，并能回放、定位和分类失败原因。

## 改进 MAS 的方法

PPT 第 12 页把改进方法分成战术性方法和结构性策略。

![[MAS改进策略图.png]]

### 战术性方法

- 改进提示词：给每个 Agent 写更明确的系统提示，说明职责、权限、禁止行为和输出格式。
- 增加自我验证和反思步骤：任务完成后让 Agent 回顾推理过程和最终结果，检查是否符合初始要求。
- 优化智能体交互模式：让多个 Agent 独立提出方案，再进行同行评审或辩论。

### 结构性策略

- 强化验证机制：引入单元测试 Agent、端到端验收测试 Agent 或专家审稿 Agent。
- 设计标准化通信协议：减少模糊自然语言交接，改用结构化 JSON 或固定字段。
- 引入外部记忆和状态管理：为系统增加共享、持久化记忆模块，解决长上下文丢失问题。

PPT 第 13 页还用实验图对比了优化前后 MAS 的效果：

![[MAS优化效果对比图.png]]

这里不要死记图上的每个柱状值，复习时抓住结论即可：只改 Prompt 有帮助，但结构性变革通常更接近根因修复，因为很多失败来自交接、验证和拓扑设计。

## 上下文工程

配套 Markdown 特别补充了“上下文工程”，它和 MAS 是同一条主线。

从单 Agent 角度看，上下文包括：

- 用户与 AI 模型的多轮对话。
- 外挂知识库和工具返回结果。
- 推理与决策的中间过程。
- 模型可接收的上下文容量。

课程笔记提醒：即使模型标称有 64K、128K、1M 上下文，真实任务中也不能无差别塞入所有信息。上下文过长时，模型对重点信息的接受和输出处理会打折。

上下文工程可以拆成四个动作：

| 动作 | 含义 | 在 MAS 中的作用 |
| --- | --- | --- |
| 保存 content | 把必要状态和历史保留下来 | 让下一个 Agent 能接住上一个 Agent 的输出 |
| 选择 content | 只给当前角色必要信息 | 避免无关内容干扰角色判断 |
| 压缩 content | 用摘要降低 token 占用 | 提升效率，但可能造成信息损失 |
| 隔离 content | 不同 Agent 看到不同上下文 | 避免角色混乱、权限混乱和目标污染 |

多 Agent 的上下文工程，本质上就是设计谁能看到什么、谁负责保存什么、谁负责验证什么。

## 多智能体框架对比

PPT 第 14 页给了多智能体框架对比：

![[多智能体框架对比图.png]]

可以先按设计取向理解：

| 框架 | 适合场景 | 关键特征 |
| --- | --- | --- |
| AutoGen | 软件开发、数据分析、智能客服、复杂对话协作 | 用户代理和助手代理协作，支持代码生成、调试和可插拔组件 |
| CrewAI | 快速原型、演示汇报、技术用户配置 | 小团队协作理念，强调 Agents、Processes、Tasks |
| LangGraph / LangChain | 企业级复杂系统、多步骤工作流、自适应路径 AI 应用 | 图式流程、状态管理、工具集成、插件生态强 |
| OpenAI Swarm | 快速搭建演示项目、教学案例和实验项目 | 轻量多 Agent 编排，核心是 Agent 和 Handoff |

PPT 第 15 页还有一个网络来源的综合评分表，仅供参考：

![[多智能体框架评分图.png]]

这类评分不要当成严格结论。更实用的判断是：

- 想做复杂对话协作和人类参与：优先看 AutoGen。
- 想做结构化任务流水线：优先看 CrewAI。
- 想做可控状态流和企业级编排：优先看 LangGraph。
- 想快速理解 Agent 交接机制：可以看 OpenAI Swarm 这类轻量框架。

## AutoGen Studio 开场

第 16-18 页进入 AutoGen 部分，先列出后续内容：

- 初识 AutoGen。
- AutoGen Studio。
- AutoGen AgentChat。
- 基于 AutoGen 的短视频自动生成工具。
- 多智能体协同代码生成应用。

第 18 页是 AutoGen Studio 章节开场：

![[AutoGen Studio开场图.png]]

这一页之后才会进入具体安装、模型配置、会话创建和运行示例。因此本节先只记录：AutoGen Studio 是后续要学习的无代码 GUI，用来搭建和观察多 Agent 应用流程。

## 复习重点

1. MAS 的定义：多个自主 Agent 在共享环境中通信、协作、协调，以完成单 Agent 难以完成的任务。
2. MAS 的价值来自角色分工，不来自简单堆模型数量。
3. MAS 最容易失败的地方是交接：上下文没共享好、目标没对齐、结果没验证。
4. MAST 可以先记三类：规格问题、智能体间不对齐、任务验证问题。
5. 改进 MAS 时，Prompt 是战术层；通信协议、验证机制、外部记忆和状态管理是结构层。
6. Generative Agents 的记忆流、检索、计划、反思，是理解多 Agent 长期一致性的经典案例。
7. AutoGen、CrewAI、LangGraph 的差异要按任务形态理解，不要只背评分。

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| 多Agent系统（1） | 属于技能 | [[AI Agent相关/AI Agent]] |
| 多Agent系统（1） | 前置知识 | [[AI Agent全景/AI Agent（1）]] |
| 多Agent系统（1） | 前置知识 | [[AI Agent全景/AI Agent（2）]] |
| 多Agent系统（1） | 前置知识 | 上下文工程 |
| 多Agent系统（1） | 相关知识 | MAS |
| 多Agent系统（1） | 相关知识 | Generative Agents |
| 多Agent系统（1） | 相关知识 | AI小镇 |
| 多Agent系统（1） | 相关知识 | MAST |
| 多Agent系统（1） | 相关知识 | AutoGen |
| 多Agent系统（1） | 相关知识 | AutoGen Studio |
| 多Agent系统（1） | 相关知识 | CrewAI |
| 多Agent系统（1） | 相关知识 | LangGraph |
| 多Agent系统（1） | 相关知识 | OpenAI Swarm |
| 多Agent系统（1） | 相关知识 | 结构化通信协议 |
| 多Agent系统（1） | 相关知识 | 外部记忆和状态管理 |
| Generative Agents | 相关知识 | Memory Stream |
| Generative Agents | 相关知识 | Retrieve |
| Generative Agents | 相关知识 | Plan |
| Generative Agents | 相关知识 | Reflect |
| MAST | 相关知识 | Poor Specification |
| MAST | 相关知识 | Inter-Agent Misalignment |
| MAST | 相关知识 | Task Verification |
| 多Agent系统（1） | 被考察于 | MAS 和单 Agent 的区别是什么 |
| 多Agent系统（1） | 被考察于 | 为什么多 Agent 系统容易失败 |
| 多Agent系统（1） | 被考察于 | MAST 的三类失败问题是什么 |
| 多Agent系统（1） | 被考察于 | 如何用上下文工程改进多 Agent 协作 |
| 多Agent系统（1） | 应用于 | 市场研究报告自动化 |
| 多Agent系统（1） | 应用于 | 软件开发多角色协作 |
| 多Agent系统（1） | 应用于 | 智能营销内容流水线 |
