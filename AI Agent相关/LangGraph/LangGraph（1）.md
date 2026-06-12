## 背景介绍

本节对应 `LangGraphV1.x/base` 目录，主题是 LangGraph 的基础图结构：状态、节点、边、条件边、编译执行、消息合并和多 schema。

前置内容是 [[AI Agent全景/AI Agent（2）]] 和 [[MCP、A2A与Agent Skills/MCP、A2A与Agent Skills（1）]]。LangGraph 不是单纯的聊天封装，而是把 Agent 执行过程建模为“带状态的图”：节点负责执行动作，边负责控制流，状态负责在节点之间传递上下文。

本节保存的示例代码位于：

- `代码/LangGraphV1.x/base/`
- `代码/LangGraphV1.x/.env.example`

原始资料中的 `.env` 含 API Key，没有复制到笔记目录。运行代码时按 `.env.example` 填写 `DASHSCOPE_API_KEY`、`API_BASE_URL`、`DEEPSEEK_API_KEY`、`DEEPSEEK_URL`。

## 英文术语中文名

代码标识符保留英文，正文里优先按下面的中文名理解：

| 英文术语 | 中文名 | 说明 |
| --- | --- | --- |
| LangGraph | 状态图编排框架 | 用图结构编排 Agent 执行流程 |
| Agent | 智能体 | 能基于上下文决策并执行动作的程序单元 |
| Prompt | 提示词 | 给模型的任务说明和约束 |
| schema | 数据模式 / 数据结构约束 | 规定状态、输入和输出有哪些字段 |
| State | 状态对象 | 节点之间传递的上下文数据 |
| StateGraph | 状态图构建器 | 用来注册节点、边和状态模式的图构建对象 |
| Node | 节点 | 图中的一步动作，例如调用模型或工具 |
| Edge | 边 | 节点之间的流转关系 |
| Reducer | 状态合并器 / 归并器 | 决定节点返回的局部更新如何合并进旧状态 |
| MessagesState | 消息状态模板 | LangGraph 为聊天消息准备的状态模板 |
| add_messages | 消息合并器 | 追加消息并按消息 ID 处理覆盖或去重 |
| RunnableConfig | 运行配置对象 | 执行图时传入的用户、线程、租户等运行时配置 |
| thread_id | 会话线程标识 | 用来区分和恢复同一轮对话或任务 |
| Function Calling | 函数调用 | 模型生成工具/函数调用名和参数的能力 |
| TypedDict | 类型字典 | Python 里给字典字段加类型提示的写法 |
| Pydantic BaseModel | 数据校验模型 | 带字段校验和默认值的数据模型 |

## 课程脉络

`base` 目录可以分成四组：

| 代码 | 主题 | 学习重点 |
| --- | --- | --- |
| `初识Graph.py`、`深入Graph.py`、`llm_nodes.py` | 从空图到聊天图 | `StateGraph`、`START`、`END`、节点函数、`invoke` 和 `stream` |
| `BaseGraph.py` | 条件边和运行配置 | `add_conditional_edges`、`RunnableConfig`（运行配置对象）、路由函数 |
| `Schema.py`、`Multiple_schemas_a.py`、`Multiple_schemas_b.py` | 状态 schema | `TypedDict`、Pydantic、输入/输出 schema 分离 |
| `Reducers.py`、`Messages_Reducer.py`、`Messages_Customize_Reducer.py`、`Messages_std.py` | 状态合并和消息历史 | `Annotated`、`operator.add`、`add_messages`、`MessagesState` |

学习顺序建议是：先能画出一个最小图，再理解状态如何更新，最后再理解为什么消息列表不能简单覆盖。

## LangGraph 的最小执行模型

`初识Graph.py` 里展示了最小聊天图：

```text
START -> chatbot -> END
```

构建过程是四步：

1. 定义状态类型，例如 `messages`。
2. 用 `StateGraph(State)` 创建图构建器。
3. 注册节点和边：`add_node`、`add_edge`。
4. `compile()` 得到可执行图，再用 `invoke()` 或 `stream()` 运行。

这里最重要的是分清“图定义”和“图执行”：

| 概念           | 含义                          |
| ------------ | --------------------------- |
| `StateGraph` | 构建阶段的图对象，用来注册节点、边和状态 schema |
| 节点函数         | 接收当前 state，返回局部状态更新         |
| 边            | 决定下一个节点是谁                   |
| `compile()`  | 把图定义编译为可运行对象                |
| `invoke()`   | 一次性执行并返回最终状态                |
| `stream()`   | 边执行边返回节点更新或状态快照             |

在 Agent 工程里，节点通常对应“调用模型”“调用工具”“人工审核”“写入记忆”“结果校验”等动作。LangGraph 的价值是把这些动作显式连接起来，而不是把所有流程塞进一个 Prompt。

## State（状态对象）是节点之间的契约

`Schema.py` 和 `初识Graph.py` 展示了两种常见写法：

| 写法 | 特点 | 适合场景 |
| --- | --- | --- |
| `TypedDict` | 轻量，只做类型提示 | 快速原型、字段结构简单 |
| Pydantic `BaseModel` | 有默认值、字段校验能力 | 需要更明确的数据约束 |

状态不是普通的“全局变量”。节点函数不应该随意修改任意字段，而是返回一个局部更新，例如：

```text
return {"messages": [response]}
```

图运行时会根据 reducer（状态合并器）把这个局部更新合并到旧状态里。没有 reducer 的字段通常按“新值覆盖旧值”理解；有 reducer 的字段会按指定策略合并。

## Reducer（状态合并器 / 归并器）决定状态如何合并

`Reducers.py` 是本节最关键的代码之一。它用：

```text
bar: Annotated[list[str], operator.add]
```

表示 `bar` 字段更新时不是覆盖，而是列表拼接。

可以这样记：

| 字段类型 | 默认更新方式 | 加 reducer（状态合并器）后 |
| --- | --- | --- |
| 普通字段 | 新值覆盖旧值 | 按 reducer（状态合并器）合并 |
| 列表字段 | 新列表覆盖旧列表 | 可用 `operator.add` 追加 |
| 消息字段 | 容易丢历史 | 用 `add_messages` 追加并按消息 ID 去重 |

官方 Graph API 文档也强调：State（状态对象）不只是 schema（数据模式），还包含 reducer（状态合并器）；reducer 决定节点返回的更新如何应用到状态。补充资料见：[LangGraph state reducers](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)。

## 消息历史不要简单覆盖

`Messages_Reducer.py` 和 `Messages_Customize_Reducer.py` 处理的是聊天类 Agent 最常见的问题：每轮模型返回一条消息，如何让消息历史持续增长。

课程代码中出现了三种方式：

| 方式 | 示例 | 说明 |
| --- | --- | --- |
| 手动维护消息列表 | `Messages_Reducer.py` | 自己截取最近消息、追加新消息 |
| `Annotated[..., operator.add]` | `messages: Annotated[Sequence[AnyMessage], operator.add]` | 简单追加，但不处理消息 ID 去重 |
| `add_messages` / `MessagesState` | `Messages_Customize_Reducer.py` | 更适合 LangGraph 消息流 |

`MessagesState` 可以理解为 LangGraph 给聊天场景准备的状态模板，核心字段是 `messages`。如果是工具调用、ReAct Agent、多轮对话、持久化记忆，优先用 `MessagesState` 或 `add_messages`，不要手写一个容易覆盖历史的 `list`。

## 条件边和路由函数

`BaseGraph.py` 展示了条件边：

```text
processor -> node_a 或 node_b
node_b -> finalizer -> END
node_a -> END
```

路由函数 `route_tools` 根据 `extra_field` 的奇偶决定下一步。这个例子虽然没有真实业务含义，但它说明 LangGraph 的控制流可以由状态驱动。

条件边的核心是：

| 组件 | 作用 |
| --- | --- |
| 路由函数 | 读取 state，返回下一个节点名或 `END` |
| `add_conditional_edges` | 把路由函数的返回值映射到具体节点 |
| `path_map` | 显式约束返回值和节点之间的对应关系 |

在 Agent 项目中，条件边通常用于：

- 模型有 `tool_calls`（工具调用请求）时进入工具节点。
- 没有工具调用时结束。
- 审核通过时执行动作。
- 审核拒绝时回到生成节点。
- 错误过多时进入兜底节点。

## RunnableConfig（运行配置对象）

`BaseGraph.py` 的 `process_input_node(state, config: RunnableConfig)` 演示了节点读取运行配置：

```text
config.get("configurable", {}).get("user_id", "default_user")
```

这类配置不属于图状态本身，而是运行时上下文。常见用途包括：

| 配置 | 用途 |
| --- | --- |
| `user_id` | 按用户隔离数据、权限和记忆 |
| `thread_id` | 配合 checkpointer（检查点保存器）恢复同一执行线程 |
| `model_name` | 运行时切换模型 |
| `tenant_id` | 多租户隔离 |

不要把 API Key、用户权限、租户信息直接塞进 Prompt；更合理的方式是通过 config 或后端服务控制。

## 多 Schema（多套数据模式）的意义

`Multiple_schemas_a.py` 和 `Multiple_schemas_b.py` 展示了输入、内部状态、输出 schema 可以不同。

这对复杂 Agent 很重要：用户输入可能只需要 `question`，内部状态需要保存 `documents`、`tool_results`、`messages`，最后输出可能只暴露 `answer` 和 `citations`。如果所有字段都对外暴露，接口会变得混乱。

可以按三层理解：

| Schema（数据模式） | 作用 |
| --- | --- |
| Input schema | 接收外部调用时允许传入什么 |
| Internal state schema | 图内部节点共享什么 |
| Output schema | 最终对外返回什么 |

## 复习重点

1. LangGraph 的基本单位是状态图，不是单轮模型调用。
2. 节点接收 state，返回局部更新；边决定节点之间的执行顺序。
3. `START` 和 `END` 是图的起点和终点标记。
4. Reducer（状态合并器）决定状态字段是覆盖还是合并。
5. 聊天消息建议使用 `MessagesState` 或 `add_messages`，避免历史被覆盖。
6. 条件边让流程由状态驱动，适合工具调用、审核、错误分支和结束判断。
7. `RunnableConfig`（运行配置对象）适合承载用户 ID、线程 ID、租户、模型配置等运行时信息。

## 补充资料

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph state reducers](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangGraph（1） | 属于技能 | [[AI Agent相关/AI Agent]] |
| LangGraph（1） | 前置知识 | [[AI Agent全景/AI Agent（2）]] |
| LangGraph（1） | 前置知识 | Function Calling |
| LangGraph（1） | 相关知识 | StateGraph |
| LangGraph（1） | 相关知识 | State |
| LangGraph（1） | 相关知识 | Reducer |
| LangGraph（1） | 相关知识 | MessagesState |
| LangGraph（1） | 相关知识 | add_messages |
| LangGraph（1） | 相关知识 | RunnableConfig（运行配置对象） |
| LangGraph（1） | 相关知识 | [[LangGraph总结]] |
| LangGraph基础图 | 有示例代码 | 代码/LangGraphV1.x/base/初识Graph.py |
| LangGraph基础图 | 有示例代码 | 代码/LangGraphV1.x/base/深入Graph.py |
| LangGraph基础图 | 有示例代码 | 代码/LangGraphV1.x/base/BaseGraph.py |
| LangGraph状态合并 | 有示例代码 | 代码/LangGraphV1.x/base/Reducers.py |
| LangGraph消息状态 | 有示例代码 | 代码/LangGraphV1.x/base/Messages_Reducer.py |
| LangGraph消息状态 | 有示例代码 | 代码/LangGraphV1.x/base/Messages_Customize_Reducer.py |
| LangGraph（1） | 被考察于 | LangGraph 中节点、边和状态分别负责什么 |
| LangGraph（1） | 被考察于 | reducer（状态合并器）为什么能避免消息历史被覆盖 |
| LangGraph（1） | 应用于 | 可控 Agent 工作流编排 |
