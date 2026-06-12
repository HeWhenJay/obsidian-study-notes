## 背景介绍

本节对应 `LangGraphV1.x/persistence` 和 `LangGraphV1.x/multi-agent` 目录，主题是持久化、聊天记录管理、长期会话摘要、Redis/MongoDB checkpoint（状态检查点）、自定义 checkpointer（检查点保存器），以及多 Agent 交接。

前面三节解决了图、控制流和工具调用。本节解决两个更接近真实项目的问题：

1. Agent 如何记住同一用户、同一会话、同一任务的历史。
2. 多个 Agent 如何通过工具或 `Command` 进行交接。

## 英文术语中文名

代码标识符保留英文，正文里优先按下面的中文名理解：

| 英文术语 | 中文名 | 说明 |
| --- | --- | --- |
| persistence | 持久化 | 把图状态保存到内存外或可恢复的存储中 |
| checkpoint | 状态检查点 | 某一步图执行后的状态快照 |
| checkpointer | 检查点保存器 | 保存和读取状态检查点的组件 |
| MemorySaver | 内存检查点保存器 | 把检查点保存在当前进程内存里 |
| RedisSaver | Redis 检查点保存器 | 把检查点保存到 Redis |
| MongoDBSaver | MongoDB 检查点保存器 | 把检查点保存到 MongoDB |
| Saver | 保存器 | checkpointer 实现类的常见后缀 |
| thread_id | 会话线程标识 | 关联同一会话或任务的多次调用 |
| MessagesState | 消息状态模板 | 用消息列表保存对话上下文 |
| RemoveMessage | 消息删除标记 | 从消息状态中删除指定消息的特殊对象 |
| summary | 会话摘要 | 对旧消息压缩后的长期上下文 |
| token | 词元 / 计费片段 | 模型处理文本的基本长度单位 |
| namespace | 命名空间 | 用来隔离不同业务或检查点范围的前缀 |
| writes | 节点写入记录 | 节点执行时产生的中间状态更新 |
| multi-agent | 多智能体 | 多个 Agent 分工协作的系统 |
| handoff / transfer | 交接 / 转交 | 把控制权从一个 Agent 交给另一个 Agent |
| transfer tool | 交接工具 | 模型通过工具调用表达“需要转交”的工具 |

## 课程脉络

本节代码可以分成两组：

| 目录 | 代码 | 主题 |
| --- | --- | --- |
| `persistence` | `简单Agent聊天消息管理.py`、`如何添加会话历史摘要.py`、`RemoveMessage删除消息.py`、`删除消息节点.py`、`通过函数修剪消息.py` | 会话记忆、消息删除、摘要压缩 |
| `persistence` | `示例14_如何使用Redis检查点.py`、`示例15_如何使用MongoDB检查点.py`、`示例14_如何创建自定义检查点.py` | checkpoint（状态检查点）后端 |
| `multi-agent` | `如何构建多智能体网络.py`、`使用Command进行交接.py`、`使用工具实现交接.py` | 多 Agent 交接 |

## MemorySaver（内存检查点保存器）和 thread_id（会话线程标识）

`简单Agent聊天消息管理.py` 展示了最小持久化对话：

```text
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}
```

第一次输入“你好，我是云帆”，第二次输入“我叫什么名字？”，因为两次调用使用同一个 `thread_id`（会话线程标识），图可以从 checkpointer（检查点保存器）中恢复同一条消息历史。

![[LangGraph如何管理聊天记录.png]]

核心理解：

| 概念 | 作用 |
| --- | --- |
| `MemorySaver` | 内存中的 checkpointer（检查点保存器），适合开发和演示 |
| `compile(checkpointer=...)` | 让图在执行过程中保存状态 |
| `thread_id` | 把多次调用归到同一条会话/任务线程 |
| `MessagesState` | 用消息列表保存对话状态的消息状态模板 |

官方持久化文档说明，checkpointer（检查点保存器）使用 `thread_id` 存取 checkpoint（状态检查点）；没有它，就无法保存状态或在 interrupt（中断等待）后恢复。补充资料见：[LangGraph persistence threads](https://langchain-ai.github.io/langgraph/cloud/concepts/threads/)。

## 聊天记录不能无限增长

持久化之后会出现新问题：消息越积越多，模型上下文越来越长。

课程给了三类处理方式：

| 方式 | 示例 | 思路 |
| --- | --- | --- |
| 删除旧消息 | `RemoveMessage删除消息.py`、`删除消息节点.py` | 用 `RemoveMessage(id=...)`（消息删除标记）从 state 中删除 |
| 函数修剪 | `通过函数修剪消息.py` | 保留最近 N 条或按 token（词元）预算保留 |
| 摘要压缩 | `如何添加会话历史摘要.py` | 把旧对话压缩为 `summary` 字段 |

删除消息适合无关上下文，摘要适合长期记忆。两者可以组合：旧消息压缩成摘要后，再删除原始消息。

## 会话摘要

`如何添加会话历史摘要.py` 在 `MessagesState` 上扩展了 `summary` 字段：

```text
class State(MessagesState):
    summary: str
```

当消息数量超过阈值时，图进入 `summarize_conversation` 节点：

1. 如果已有摘要，就基于旧摘要和新消息扩展摘要。
2. 如果没有摘要，就创建摘要。
3. 用 `RemoveMessage`（消息删除标记）删除较早消息，只保留最近几条。
4. 后续调用模型时，把摘要作为 system message（系统消息）补回上下文。

![[LangGraph添加会话历史摘要.png]]

这个模式适合长对话，但要注意摘要会丢细节。对于简历、订单、合同、代码变更这类高精度信息，不能只依赖摘要，应该保留结构化状态或外部存储。

## Redis 和 MongoDB checkpoint（状态检查点）

`示例14_如何使用Redis检查点.py` 展示 Redis checkpointer（Redis 检查点保存器）：

```text
from langgraph.checkpoint.redis import RedisSaver
DB_URI = "redis://localhost:6379"
```

代码注释写明需要：

```text
pip install -U langgraph-checkpoint-redis
```

`示例15_如何使用MongoDB检查点.py` 展示 MongoDB checkpointer（MongoDB 检查点保存器），并提示课程当时依赖兼容性可能有问题：`langchain-mongodb 0.7.2` 只支持 V1.0 以下的 LangGraph，可能造成版本冲突。这个提醒很重要，复现时要先确认当前包版本。

可以按环境选后端：

| 后端 | 适合场景 | 注意点 |
| --- | --- | --- |
| MemorySaver（内存检查点保存器） | 本地开发、课堂演示 | 进程结束后状态丢失 |
| RedisSaver（Redis 检查点保存器） | 会话级短中期状态、低延迟恢复 | 需要 Redis 服务和过期策略 |
| MongoDBSaver（MongoDB 检查点保存器） | 文档型存储、较复杂 checkpoint（状态检查点）数据 | 注意包版本兼容 |
| 自定义 Saver（自定义保存器） | 企业内部存储或特殊审计需求 | 需要实现 checkpoint（状态检查点）读写协议 |

## 自定义 checkpointer（检查点保存器）

`示例14_如何创建自定义检查点.py` 文件很长，核心是在演示如何实现 Redis 风格的 checkpoint（状态检查点）保存器。

复习时不需要死背 600 多行实现，抓住四类能力：

| 能力 | 含义 |
| --- | --- |
| 生成 key | 按 namespace（命名空间）、`thread_id`、checkpoint namespace、checkpoint ID 组织键 |
| 保存 checkpoint（状态检查点） | 把状态快照序列化写入后端 |
| 保存 writes（节点写入记录） | 记录节点写入的中间更新 |
| 查询历史 | 按 thread（执行线程）读取最新或历史 checkpoint |

真实项目里优先用官方或成熟社区 saver（保存器）。只有当公司有特殊存储、审计、加密或数据隔离要求时，才考虑自定义。

## 多 Agent（多智能体）交接：Command 方式

`multi-agent/如何构建多智能体网络.py` 和 `使用Command进行交接.py` 用旅行顾问和酒店顾问演示多 Agent 网络。

流程是：

```text
travel_advisor -> hotel_advisor -> END
```

当旅游顾问认为需要酒店推荐时，返回：

```text
Command(goto="hotel_advisor", update={"messages": [ai_msg, tool_msg]})
```

![[LangGraph构建多智能体网络.png]]

这种方式的优点是交接明确：节点直接决定下一位 Agent（智能体），并把交接消息写入历史。适合 Agent 角色固定、流程可控的系统。

## 多 Agent（多智能体）交接：工具信号方式

`multi-agent/使用工具实现交接.py` 使用“transfer 工具”（交接工具）作为交接信号。模型调用类似 `transfer_to_hotel_advisor` 的工具，图或工具节点再把控制权交给目标 Agent。

![[LangGraph使用工具实现交接-多个agent.png]]

这种方式更接近 LLM 的工具调用习惯：模型通过工具调用表达“我要交接”。但工程上要防止模型频繁无意义转交，最好增加：

- 明确的系统提示，说明什么时候允许交接。
- 交接次数上限。
- 目标 Agent 的职责边界。
- 交接消息格式。
- 最终答案归口规则。

## 多 Agent（多智能体）设计要点

多 Agent（多智能体）的难点不是“多创建几个节点”，而是状态和职责边界：

| 问题 | 设计原则 |
| --- | --- |
| 谁能看到历史 | 用 state 和 prompt 控制上下文范围 |
| 谁负责最终回答 | 明确最终输出 Agent |
| 谁能调用工具 | 每个 Agent 绑定自己的工具集合 |
| 如何避免来回踢皮球 | 限制交接次数，设置终止条件 |
| 如何恢复中断任务 | 使用 checkpointer（检查点保存器）和稳定 `thread_id` |

LangGraph 的优势在于它把这些协作关系显式画成图，而不是隐藏在自然语言 Prompt 里。

## 复习重点

1. 持久化图需要 `compile(checkpointer=...)` 和稳定的 `thread_id`（会话线程标识）。
2. `MemorySaver`（内存检查点保存器）适合开发演示，生产要考虑 Redis、Postgres、MongoDB 或自定义后端。
3. 消息历史不能无限增长，要通过删除、修剪或摘要压缩控制上下文。
4. 摘要适合长期语义记忆，不适合替代精确结构化数据。
5. Redis/MongoDB checkpointer（检查点保存器）要先确认依赖版本和服务可用性。
6. 多 Agent（多智能体）交接可以用 `Command(goto=...)`，也可以用工具调用作为交接信号。
7. 多 Agent 要设计职责边界、上下文共享、交接次数和最终输出归口。

## 补充资料

- [LangGraph persistence threads](https://langchain-ai.github.io/langgraph/cloud/concepts/threads/)
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangGraph（4） | 属于技能 | [[AI Agent相关/AI Agent]] |
| LangGraph（4） | 前置知识 | [[LangGraph（1）]] |
| LangGraph（4） | 前置知识 | [[LangGraph（2）]] |
| LangGraph（4） | 前置知识 | [[多Agent系统/多Agent系统（1）]] |
| LangGraph（4） | 相关知识 | MemorySaver（内存检查点保存器） |
| LangGraph（4） | 相关知识 | Checkpoint |
| LangGraph（4） | 相关知识 | RedisSaver（Redis 检查点保存器） |
| LangGraph（4） | 相关知识 | MongoDBSaver（MongoDB 检查点保存器） |
| LangGraph（4） | 相关知识 | RemoveMessage（消息删除标记） |
| LangGraph（4） | 相关知识 | 多Agent交接 |
| LangGraph（4） | 相关知识 | [[LangGraph总结]] |
| LangGraph持久化 | 有示例代码 | 代码/LangGraphV1.x/persistence/简单Agent聊天消息管理.py |
| LangGraph会话摘要 | 有示例代码 | 代码/LangGraphV1.x/persistence/如何添加会话历史摘要.py |
| LangGraph消息管理 | 有示例代码 | 代码/LangGraphV1.x/persistence/RemoveMessage删除消息.py |
| LangGraph消息管理 | 有示例代码 | 代码/LangGraphV1.x/persistence/通过函数修剪消息.py |
| LangGraph检查点 | 有示例代码 | 代码/LangGraphV1.x/persistence/示例14_如何使用Redis检查点.py |
| LangGraph检查点 | 有示例代码 | 代码/LangGraphV1.x/persistence/示例15_如何使用MongoDB检查点.py |
| LangGraph多Agent | 有示例代码 | 代码/LangGraphV1.x/multi-agent/如何构建多智能体网络.py |
| LangGraph多Agent | 有示例代码 | 代码/LangGraphV1.x/multi-agent/使用Command进行交接.py |
| LangGraph多Agent | 有示例代码 | 代码/LangGraphV1.x/multi-agent/使用工具实现交接.py |
| LangGraph（4） | 被考察于 | thread_id（会话线程标识）在持久化中的作用是什么 |
| LangGraph（4） | 被考察于 | 长对话为什么需要摘要或修剪 |
| LangGraph（4） | 应用于 | 多 Agent 旅游规划和酒店推荐 |
