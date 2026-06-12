## 背景介绍

本节对应 PPT《MCP & A2A & Agent Skills》第 13-17 页，主题是 A2A 协议、A2A 当前热度不如 MCP 的原因，以及 MCP 与 A2A 如何协同。

A2A 的全称是 Agent to Agent / Agent2Agent。它关注的是不同框架、不同厂商、不同部署环境里的 Agent 如何互相发现、通信、委托任务和返回结果。和 MCP 相比，A2A 的对象更“横向”：MCP 连接 Agent 和工具，A2A 连接 Agent 和 Agent。

## A2A 协议定位

PPT 给出的定义是：A2A 是 Google 推出的一种开放协议，目标是让不同框架和供应商的 AI Agents 能够互相通信与协作。官方 A2A 文档里也把它描述为面向独立 Agent 系统互操作的协议。

可以用一句话记住：

```text
MCP 让 Agent 会用工具；A2A 让 Agent 会找别的 Agent 做事。
```

A2A 的核心不是“把所有 Agent 合并成一个系统”，而是把远端 Agent 当作一个保留内部实现的黑盒服务来协作。调用方不需要知道远端 Agent 内部用了什么模型、记忆、工具或工作流，只需要知道它声明了什么能力、如何鉴权、能接收什么输入、会返回什么结果。

## 为什么 A2A 没有 MCP 热

PPT 第 16 页给了三个原因，适合从“基础能力、生态激励、责任边界”三个角度理解：

| 原因 | 解释 |
| --- | --- |
| Agent 自身能力还不稳定 | 很多 Agent 在复杂任务完成率、稳定性、泛化能力上仍达不到生产预期；Agent 之间协作会放大不稳定性 |
| 统一通信和资源调度难 | A2A 要求 Agent 具备统一通信标准、可信身份认证和资源调度能力，还涉及不同平台之间的利益分配 |
| 法律伦理框架不足 | 多 Agent 协作后，任务失败、数据泄露、越权调用、错误决策的责任归属更难界定 |

这也是为什么 MCP 更容易先落地：MCP 的调用对象通常是工具或数据源，边界相对清楚；A2A 的调用对象是另一个自治系统，信任和责任成本更高。

## A2A 工作原理

官方文档中 A2A 的核心角色包括：

| 角色 | 含义 |
| --- | --- |
| User | 发起目标的人或自动化服务 |
| A2A Client / Client Agent | 代表用户发起 A2A 请求的应用、服务或 Agent |
| A2A Server / Remote Agent | 暴露 A2A HTTP 端点的远端 Agent 或 Agent 系统 |

关键通信元素包括：

| 元素 | 作用 |
| --- | --- |
| Agent Card | JSON 元数据，描述 Agent 身份、能力、服务端点、skills 和认证要求 |
| Message | 一轮通信内容，包含角色和 Parts |
| Part | Message 或 Artifact 内的内容单元，可以是文本、文件引用或结构化数据 |
| Task | 有状态任务单元，用于追踪长任务、多轮协作和状态变化 |
| Artifact | Agent 在任务中产生的可交付结果，如文档、图片、结构化数据 |

典型流程是：Client 根据 Agent Card 发现远端 Agent 能力，然后发送 Message。对于简单问题，远端 Agent 可以直接返回 Message；对于复杂任务，远端 Agent 返回 Task，并通过轮询、SSE 或推送通知返回状态和 Artifact。

## MCP 协同 A2A

![[MCP协同A2A示意图.png]]

PPT 第 17 页的图很关键：一个 Agentic Application 内部有 LLM、Agent Framework 和 Agent；它通过 MCP Server 访问 resources/tools，同时通过 A2A protocol 与外部 Blackbox Agent 通信。

这说明 MCP 和 A2A 不是替代关系，而是两个方向的协议：

| 协议 | 连接对象 | 典型问题 | 适合场景 |
| --- | --- | --- | --- |
| MCP | Agent / Host 连接工具、资源、提示模板 | 我如何安全地调用外部能力？ | 本地文件、数据库、搜索、业务 API、开发工具 |
| A2A | Agent 连接另一个 Agent | 我如何委托另一个自治 Agent 完成任务？ | 跨团队 Agent、跨厂商 Agent、供应商能力协作、黑盒智能体服务 |
| Skills | Agent 加载本地/项目内工作流知识 | 我如何让 Agent 学会某类稳定流程？ | 写报告、做数据分析、生成课件、创建 MCP Server |

工程上可以按这个顺序选型：

1. 如果只是调用 API、数据库、文件、搜索、浏览器等外部能力，优先 MCP。
2. 如果是把一个复杂能力封装成可复用工作流，优先 Skills。
3. 如果对方本身就是自治 Agent，并且需要发现能力、异步任务、状态更新和 Artifact，才考虑 A2A。

## A2A 的工程注意点

A2A 比普通 API 调用多了几层边界：

- Agent Card 不能泄露静态密钥，认证信息应该通过 HTTP 头、OAuth、mTLS 等机制处理。
- 远端 Agent 是黑盒，返回的 Agent Card、Message、Artifact 都应按不可信输入处理。
- 长任务要设计 Task 状态、超时、取消、重试和幂等语义。
- 如果只需要一次同步结果，不必为了追热点把普通工具包装成 A2A。
- 如果远端能力可以稳定抽象成 API，MCP Server 往往比 A2A 更轻。

## 小结

1. A2A 的重点是 Agent 间互操作，不是工具调用协议。
2. A2A 的关键数据结构是 Agent Card、Message、Part、Task、Artifact。
3. MCP 和 A2A 的边界是：MCP 面向工具/资源，A2A 面向自治 Agent。
4. A2A 当前落地慢，主要因为 Agent 可靠性、身份认证、生态激励和责任边界都更复杂。
5. 在实际项目里，优先把确定性外部能力做成 MCP，把可沉淀流程做成 Skills，只有跨 Agent 委托时再引入 A2A。

## 补充资料

- [A2A 官方核心概念](https://a2a-protocol.org/latest/topics/key-concepts/)
- [A2A 官方规范](https://a2a-protocol.org/latest/specification/)
- [MCP 官方架构说明](https://modelcontextprotocol.io/docs/learn/architecture)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| MCP、A2A与Agent Skills（2） | 属于技能 | [[AI Agent相关/AI Agent]] |
| MCP、A2A与Agent Skills（2） | 前置知识 | [[MCP、A2A与Agent Skills（1）]] |
| MCP、A2A与Agent Skills（2） | 前置知识 | 多智能体系统 |
| MCP、A2A与Agent Skills（2） | 相关知识 | A2A |
| MCP、A2A与Agent Skills（2） | 相关知识 | Agent Card |
| MCP、A2A与Agent Skills（2） | 相关知识 | Task |
| MCP、A2A与Agent Skills（2） | 相关知识 | Message |
| MCP、A2A与Agent Skills（2） | 相关知识 | Artifact |
| MCP、A2A与Agent Skills（2） | 相关知识 | MCP |
| MCP、A2A与Agent Skills（2） | 相关知识 | [[MCP、A2A与Agent Skills总结]] |
| MCP | 相关知识 | 工具调用 |
| A2A | 相关知识 | Agent间通信 |
| A2A | 被考察于 | A2A 为什么不如 MCP 容易落地 |
| MCP协同A2A | 应用于 | 跨 Agent 任务委托 |
