## 总览

本专题对应资料目录 `LangGraphV1.x`，已整理为四节：

- [[LangGraph（1）]]：基础图、状态、节点、边、reducer（状态合并器）、消息状态。
- [[LangGraph（2）]]：进阶控制流、并行、`Command`（命令式跳转对象）、`interrupt`（中断等待）、checkpoint（状态检查点）、子图。
- [[LangGraph（3）]]：工具调用、`ToolNode`（工具执行节点）、大量工具选择、工具上下文、重试。
- [[LangGraph（4）]]：持久化、聊天记录管理、Redis/MongoDB checkpoint（状态检查点）、多 Agent 交接。

代码已保存到 `代码/LangGraphV1.x/`。原始 `.env` 含 API Key，未复制；运行时使用 `代码/LangGraphV1.x/.env.example`。

## 术语总表

代码标识符保留英文，复习时先用中文名抓住含义：

| 英文术语 | 中文名 | 所属主题 |
| --- | --- | --- |
| LangGraph | 状态图编排框架 | 总体 |
| Agent | 智能体 | 总体 |
| State | 状态对象 | 基础图 |
| StateGraph | 状态图构建器 | 基础图 |
| Node | 节点 | 基础图 |
| Edge | 边 | 基础图 |
| conditional edge | 条件边 | 控制流 |
| schema | 数据模式 / 数据结构约束 | 状态建模 |
| Reducer | 状态合并器 / 归并器 | 状态合并 |
| MessagesState | 消息状态模板 | 消息状态 |
| add_messages | 消息合并器 | 消息状态 |
| RunnableConfig | 运行配置对象 | 运行配置 |
| Command | 命令式跳转对象 | 控制流 |
| Send | 并行分发指令 | 并行分支 |
| MapReduce | 映射归约 | 并行分支 |
| interrupt | 中断等待 | 人机协作 |
| checkpoint | 状态检查点 | 持久化 |
| checkpointer | 检查点保存器 | 持久化 |
| thread_id | 会话线程标识 | 持久化 |
| ToolNode | 工具执行节点 | 工具调用 |
| bind_tools | 绑定工具 | 工具调用 |
| tool_calls | 工具调用请求 | 工具调用 |
| tools_condition | 工具路由条件 | 工具调用 |
| InjectedState | 状态注入器 | 工具上下文 |
| RetryPolicy | 重试策略 | 稳定性 |
| MemorySaver | 内存检查点保存器 | 持久化 |
| RedisSaver | Redis 检查点保存器 | 持久化 |
| MongoDBSaver | MongoDB 检查点保存器 | 持久化 |
| RemoveMessage | 消息删除标记 | 消息管理 |
| Function Calling | 函数调用 | 工具调用 |
| transfer tool | 交接工具 | 多 Agent |

## 核心结论

LangGraph 的核心不是“再封装一次 LLM”，而是把 Agent 应用建模为可控的状态图：

```text
State（状态对象） + Node（节点） + Edge（边） + Reducer（状态合并器） + Checkpointer（检查点保存器）
```

可以按五个问题理解：

| 问题 | LangGraph 对应能力 |
| --- | --- |
| 当前任务有哪些上下文 | State schema（状态数据模式） |
| 每一步做什么 | Node（节点） |
| 下一步去哪里 | Edge（边）、conditional edge（条件边）、`Command`（命令式跳转对象） |
| 节点更新如何合并 | Reducer（状态合并器）、`add_messages`（消息合并器） |
| 中断或多轮后如何恢复 | Checkpointer（检查点保存器）、`thread_id`（会话线程标识） |

## 四节知识地图

| 节次 | 主线 | 关键 API | 代码入口 |
| --- | --- | --- | --- |
| [[LangGraph（1）]] | 从图结构到状态合并 | `StateGraph`（状态图构建器）、`START`、`END`、`add_node`、`add_edge`、`MessagesState`（消息状态模板） | `代码/LangGraphV1.x/base/` |
| [[LangGraph（2）]] | 复杂控制流 | `add_conditional_edges`、`Command`（命令式跳转对象）、`Send`（并行分发指令）、`interrupt`（中断等待）、`compile(checkpointer=...)` | `代码/LangGraphV1.x/adv/` |
| [[LangGraph（3）]] | 工具调用 | `bind_tools`（绑定工具）、`ToolNode`（工具执行节点）、`tools_condition`（工具路由条件）、`RunnableConfig`（运行配置对象）、`InjectedState`（状态注入器）、`RetryPolicy`（重试策略） | `代码/LangGraphV1.x/toolUse/` |
| [[LangGraph（4）]] | 持久化和多 Agent | `MemorySaver`（内存检查点保存器）、`RedisSaver`（Redis 检查点保存器）、`MongoDBSaver`（MongoDB 检查点保存器）、`RemoveMessage`（消息删除标记）、多 Agent `Command` 交接 | `代码/LangGraphV1.x/persistence/`、`代码/LangGraphV1.x/multi-agent/` |

## 关键图

### ToolNode（工具执行节点）工具循环

![[LangGraphLangGraph_ToolNode.png]]

这个图代表最常见的工具增强 Agent：模型先判断是否需要工具，`ToolNode`（工具执行节点）执行后结果回到模型，直到模型不再请求工具。

### interrupt（中断等待）人工输入

![[LangGraph如何使用interrupt等待用户输入.png]]

`interrupt()`（中断等待）让图暂停，外部用 `Command(resume=...)` 恢复。它适合人工审批、补充参数、修改草稿、确认高风险操作。

### 长对话摘要

![[LangGraph添加会话历史摘要.png]]

持久化之后必须控制上下文长度。摘要节点把旧消息压缩为 `summary` 字段，再删除早期消息，只保留最近对话。

### 多 Agent 网络

![[LangGraph构建多智能体网络.png]]

多 Agent 在 LangGraph 中本质上是多个角色节点之间的控制流交接。交接可以通过 `Command(goto=...)`，也可以通过 transfer 工具（交接工具）作为信号。

## 代码索引

| 主题 | 代码 |
| --- | --- |
| 基础聊天图 | `代码/LangGraphV1.x/base/初识Graph.py`、`代码/LangGraphV1.x/base/llm_nodes.py` |
| 条件边 | `代码/LangGraphV1.x/base/BaseGraph.py`、`代码/LangGraphV1.x/adv/示例3.3_条件分支.py` |
| Reducer（状态合并器） | `代码/LangGraphV1.x/base/Reducers.py`、`代码/LangGraphV1.x/base/Messages_Reducer.py` |
| 图可视化 | `代码/LangGraphV1.x/adv/Visualization.py` |
| MapReduce（映射归约）并行 | `代码/LangGraphV1.x/adv/Map-reduce.py`、`代码/LangGraphV1.x/adv/Map-reduce2.py` |
| interrupt（中断等待） | `代码/LangGraphV1.x/adv/interr/interrupt_demo.py`、`代码/LangGraphV1.x/adv/interr/interrupt_hitl.py` |
| 工具审核 | `代码/LangGraphV1.x/adv/interr/审查工具使用.py` |
| ToolNode（工具执行节点） | `代码/LangGraphV1.x/toolUse/LangGraph_ToolNode.py`、`代码/LangGraphV1.x/toolUse/异常ToolNode.py` |
| 大量工具选择 | `代码/LangGraphV1.x/toolUse/如何处理大量工具.py` |
| 工具状态注入 | `代码/LangGraphV1.x/toolUse/如何传递配置给工具.py`、`代码/LangGraphV1.x/toolUse/如何将图状态传递给工具.py` |
| 持久化对话 | `代码/LangGraphV1.x/persistence/简单Agent聊天消息管理.py` |
| 会话摘要 | `代码/LangGraphV1.x/persistence/如何添加会话历史摘要.py` |
| Redis/MongoDB checkpoint（状态检查点） | `代码/LangGraphV1.x/persistence/示例14_如何使用Redis检查点.py`、`代码/LangGraphV1.x/persistence/示例15_如何使用MongoDB检查点.py` |
| 多 Agent 交接 | `代码/LangGraphV1.x/multi-agent/如何构建多智能体网络.py`、`代码/LangGraphV1.x/multi-agent/使用Command进行交接.py`、`代码/LangGraphV1.x/multi-agent/使用工具实现交接.py` |

## 环境变量

课程代码主要读取这些环境变量：

| 变量 | 用途 |
| --- | --- |
| `DASHSCOPE_API_KEY` | 通义千问 / DashScope 兼容 OpenAI 接口 |
| `API_BASE_URL` | DashScope 兼容模式地址，建议为 `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `DASHSCOPE_URL` | 原始 `.env` 中出现的 DashScope 地址，部分代码未直接读取 |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `DEEPSEEK_URL` | DeepSeek API 地址，课程中为 `https://api.deepseek.com/v1` |

注意：原始 `.env` 中使用 `DASHSCOPE_URL`，但很多 Python 文件读取 `API_BASE_URL`。复现代码时需要补上 `API_BASE_URL`，否则模型初始化可能拿不到 base URL。

## 易错点

| 易错点 | 正确理解 |
| --- | --- |
| 节点返回完整 state（状态对象） | 节点通常返回局部更新，图按 reducer（状态合并器）合并 |
| 消息字段直接用 list 覆盖 | 聊天场景优先用 `MessagesState`（消息状态模板）或 `add_messages`（消息合并器） |
| `bind_tools()`（绑定工具）会自动执行工具 | 它只让模型产生工具调用，执行需要 `ToolNode`（工具执行节点）或自定义调度 |
| 并行分支不需要 reducer（状态合并器） | 多分支写同一字段时必须设计合并策略 |
| `interrupt()`（中断等待）可以无状态恢复 | 人机协作需要 checkpointer（检查点保存器）和同一个 `thread_id` |
| MemorySaver（内存检查点保存器）可用于生产长期记忆 | 它适合开发演示，生产要用持久化后端 |
| 多 Agent 只是多个模型 | 关键是角色边界、交接协议、上下文共享和终止条件 |

## 复习重点

1. 能画出最小图：`START -> node -> END`。
2. 能解释 state（状态对象）、node（节点）、edge（边）、reducer（状态合并器）的职责。
3. 能说明 `MessagesState`（消息状态模板）和普通列表的区别。
4. 能写出工具调用循环：`agent -> tools -> agent`。
5. 能解释 `Command(update=..., goto=...)`（命令式跳转对象）的用途。
6. 能解释 `Send`（并行分发指令）如何支持 MapReduce（映射归约）并行。
7. 能解释 `interrupt()`（中断等待）、`Command(resume=...)`、checkpointer（检查点保存器）、`thread_id` 的关系。
8. 能说明长对话为什么要修剪或摘要。
9. 能比较 `Command`（命令式跳转对象）交接和工具信号交接两种多 Agent 方式。
10. 能指出 `.env` 中 `DASHSCOPE_URL` 和代码里 `API_BASE_URL` 的差异。

## 补充资料

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph state reducers](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangGraph persistence threads](https://langchain-ai.github.io/langgraph/cloud/concepts/threads/)
- [tools_condition reference](https://reference.langchain.com/python/langgraph.prebuilt/tool_node/tools_condition)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangGraph总结 | 属于技能 | [[AI Agent相关/AI Agent]] |
| LangGraph总结 | 相关知识 | [[LangGraph（1）]] |
| LangGraph总结 | 相关知识 | [[LangGraph（2）]] |
| LangGraph总结 | 相关知识 | [[LangGraph（3）]] |
| LangGraph总结 | 相关知识 | [[LangGraph（4）]] |
| LangGraph总结 | 相关知识 | StateGraph（状态图构建器） |
| LangGraph总结 | 相关知识 | Reducer（状态合并器） |
| LangGraph总结 | 相关知识 | ToolNode（工具执行节点） |
| LangGraph总结 | 相关知识 | interrupt（中断等待） |
| LangGraph总结 | 相关知识 | Checkpoint（状态检查点） |
| LangGraph总结 | 相关知识 | 多Agent交接 |
| LangGraph总结 | 有示例代码 | 代码/LangGraphV1.x/base/初识Graph.py |
| LangGraph总结 | 有示例代码 | 代码/LangGraphV1.x/toolUse/LangGraph_ToolNode.py |
| LangGraph总结 | 有示例代码 | 代码/LangGraphV1.x/persistence/简单Agent聊天消息管理.py |
| LangGraph总结 | 有示例代码 | 代码/LangGraphV1.x/multi-agent/如何构建多智能体网络.py |
| LangGraph | 被考察于 | LangGraph 和普通 Function Calling 的区别是什么 |
| LangGraph | 被考察于 | 为什么复杂 Agent 需要显式状态图 |
| LangGraph | 应用于 | 企业级 Agent 工作流编排 |
