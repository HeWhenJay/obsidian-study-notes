## 背景介绍

本节对应 `LangGraphV1.x/toolUse` 目录，主题是工具调用：`ToolNode`（工具执行节点）、模型绑定工具、工具调用循环、异常处理、大量工具选择、工具读取运行配置、工具读取图状态、节点重试策略。

前置内容是 [[AI Agent全景/AI Agent（2）]] 中的 Function Calling，以及 [[LangGraph（1）]] 的 `MessagesState` 和 [[LangGraph（2）]] 的条件边。工具调用本质上是一个小循环：

```text
agent -> tools -> agent -> END
```

模型决定是否调用工具；工具节点执行工具；工具结果回到模型；模型再决定继续调用工具还是生成最终答案。

## 英文术语中文名

代码标识符保留英文，正文里优先按下面的中文名理解：

| 英文术语 | 中文名 | 说明 |
| --- | --- | --- |
| Function Calling | 函数调用 | 模型表达要调用哪个函数以及参数 |
| Tool / tool | 工具 | 可被模型请求、由程序执行的函数能力 |
| ToolNode | 工具执行节点 | LangGraph 里负责执行模型工具调用的预置节点 |
| bind_tools | 绑定工具 | 把工具列表暴露给模型，让模型能选择调用 |
| tool_calls | 工具调用请求 | 模型生成的工具名和参数 |
| tools_condition | 工具路由条件 | 根据最后一条 AI 消息是否有工具调用决定是否进入工具节点 |
| ToolMessage | 工具结果消息 | 工具执行结果或错误返回给模型的消息 |
| RunnableConfig | 运行配置对象 | 给节点或工具注入用户、线程、租户等运行时信息 |
| InjectedState | 状态注入器 | 把图状态注入工具，但不暴露给模型填写 |
| RetryPolicy | 重试策略 | 节点失败后自动重试的规则 |
| Document | 文档对象 | 用来承载工具描述或检索内容的数据对象 |
| Embeddings | 向量表示 | 把文本转成向量，便于相似度检索 |
| VectorStore | 向量库 | 保存和检索向量化文档的存储组件 |
| dynamic binding | 动态绑定 | 当前轮只把相关工具绑定给模型 |
| docstring | 函数说明字符串 | Python 函数里的说明文本，常用于生成工具描述 |

## 课程脉络

`toolUse` 目录可以按功能分成五组：

| 代码 | 主题 | 学习重点 |
| --- | --- | --- |
| `模型调用.py` | 模型绑定工具 | `bind_tools()`（绑定工具）、`tool_calls`（工具调用请求） |
| `LangGraph_ToolNode.py`、`异常ToolNode.py` | 工具节点 | `ToolNode`（工具执行节点）、工具循环、错误处理 |
| `如何处理大量工具.py` | 大量工具选择 | 工具注册表、向量检索、动态绑定 |
| `如何传递配置给工具.py`、`如何将图状态传递给工具.py` | 工具上下文注入 | `RunnableConfig`（运行配置对象）、`InjectedState`（状态注入器） |
| `示例9_如何添加节点重试策略.py` | 重试策略 | `RetryPolicy`（重试策略）、数据库查询失败重试 |

## 模型绑定工具（bind_tools）

`模型调用.py` 先不构建完整图，只演示模型如何看到工具。

关键步骤：

1. 用 `@tool` 把普通 Python 函数变成 LangChain 工具。
2. 把工具列表传给 `model.bind_tools(tools)`。
3. 模型根据用户问题生成 `tool_calls`（工具调用请求）。

这个阶段只是“模型决定要不要调用工具”，并不会自动执行工具。工具执行需要 `ToolNode`（工具执行节点）或你自己写工具调度逻辑。

## ToolNode（工具执行节点）工具循环

`LangGraph_ToolNode.py` 是最标准的工具调用图：

![[LangGraphLangGraph_ToolNode.png]]

流程是：

```text
START -> agent -> tools -> agent -> END
```

其中：

| 节点 | 作用 |
| --- | --- |
| `agent` | 调用绑定工具后的模型，产生普通回答或 `tool_calls`（工具调用请求） |
| `tools` | `ToolNode`（工具执行节点）执行模型请求的工具 |
| 条件边 | 如果最后一条消息有 `tool_calls`（工具调用请求），进入工具节点；否则结束 |

`should_continue` 的判断逻辑是：

```text
if last_message.tool_calls:
    return "tools"
return END
```

LangGraph 官方参考中也提供 `tools_condition`（工具路由条件）这类预构建路由函数，用于根据最后一条 AI 消息是否包含工具调用来路由到工具节点。补充资料见：[tools_condition reference](https://reference.langchain.com/python/langgraph.prebuilt/tool_node/tools_condition)。

## 工具错误处理

`异常ToolNode.py` 展示：

```text
ToolNode([get_weather], handle_tool_errors=True)
```

工具调用失败时，如果没有处理，整个图可能直接异常结束。开启错误处理后，工具错误会以 ToolMessage（工具结果消息）的形式回到模型，让模型有机会修正参数或给用户解释。

![[LangGraph异常ToolNode.png]]

工具错误处理的工程含义：

| 场景 | 处理策略 |
| --- | --- |
| 工具参数不合法 | 返回错误消息，让模型重试或解释 |
| 外部 API 临时失败 | 节点级重试或降级 |
| 权限不足 | 不应让模型自行重试，应该返回权限错误 |
| 危险操作失败 | 记录审计日志，避免自动反复执行 |

## 大量工具选择

`如何处理大量工具.py` 解决一个常见问题：工具很多时，不应该把所有工具都塞给模型。

课程代码的做法是：

1. 为每个公司创建一个工具。
2. 把工具描述做成 `Document`。
3. 用 `DashScopeEmbeddings` 和 `InMemoryVectorStore` 检索相关工具。
4. 当前轮只把命中的工具动态绑定给模型。

![[LangGraph如何处理大量工具.png]]

这背后的思想和 RAG 很像：不是把所有工具塞进上下文，而是先检索候选工具，再让模型在小集合里选择。

| 问题 | 直接塞所有工具 | 动态选择工具 |
| --- | --- | --- |
| 上下文成本 | 高 | 低 |
| 工具混淆 | 容易发生 | 明显降低 |
| 工具更新 | 难维护 | 工具注册表可独立维护 |
| 召回失败 | 不存在 | 需要优化工具描述和检索 |

## 工具读取运行配置（RunnableConfig）

`如何传递配置给工具.py` 展示工具函数接收 `RunnableConfig`：

```text
def update_favorite_pets(pets: List[str], config: RunnableConfig) -> None:
    user_id = config.get("configurable", {}).get("user_id")
```

注意：`config` 不应出现在工具 docstring（函数说明字符串）的用户参数描述里。它是系统注入的运行上下文，不是模型需要填写的业务参数。

这个模式适合：

- 按 `user_id` 读写用户偏好。
- 按 `tenant_id` 隔离数据库。
- 按权限决定工具能否执行。
- 按 `thread_id` 写入会话级状态。

![[LangGraph如何将配置传递给工具.png]]

## 工具读取图状态（InjectedState）

`如何将图状态传递给工具.py` 展示 `InjectedState`：

```text
def get_context(question: str, state: Annotated[dict, InjectedState]):
    return "\n\n".join(doc for doc in state["docs"])
```

这里工具的实际输入包含 `question` 和 `state`，但模型只需要看到 `question`。`InjectedState`（状态注入器）会把图状态注入工具，避免模型自己伪造或传入内部字段。

这个设计很关键：工具需要上下文，但上下文不一定应该暴露给模型填写。

适合场景：

- RAG 工具读取已检索文档。
- 审核工具读取待审核草稿。
- 数据库工具读取当前用户权限。
- Agent 交接工具读取当前消息历史。

## 节点重试策略（RetryPolicy）

`示例9_如何添加节点重试策略.py` 用 SQLite 内存库和查询节点演示 `RetryPolicy`（重试策略）。

重试策略适合短暂、可恢复的错误，例如：

| 错误 | 是否适合自动重试 |
| --- | --- |
| 数据库连接短暂失败 | 适合 |
| 网络请求超时 | 适合 |
| SQL 写错 | 不适合盲目重试 |
| 权限不足 | 不适合 |
| 删除操作失败 | 需要谨慎，避免重复副作用 |

Agent 工程里不要把所有异常都交给模型“再试一次”。重试要限定错误类型、次数和退避策略。

## 和 Function Calling 的关系

Function Calling 解决“模型如何表达要调用哪个函数和参数”。LangGraph 工具图解决“工具调用在多步骤工作流中如何执行、循环、失败处理、状态更新和恢复”。

| 维度 | Function Calling（函数调用） | LangGraph ToolNode（工具执行节点） |
| --- | --- | --- |
| 范围 | 单次模型调用中的工具 schema（数据模式） | 图中的工具执行节点 |
| 状态 | 通常由应用代码管理 | 由 graph state（图状态）和 reducer（状态合并器）管理 |
| 控制流 | 应用代码判断 | 条件边、`tools_condition`（工具路由条件）、`Command`（命令式跳转对象） |
| 错误处理 | 应用自定义 | ToolMessage、节点重试、人工审核 |

## 复习重点

1. `bind_tools()`（绑定工具）只让模型“知道工具”，不代表工具已经执行。
2. `ToolNode`（工具执行节点）根据模型生成的 `tool_calls`（工具调用请求）执行工具。
3. 标准工具循环是 `agent -> tools -> agent`。
4. 工具错误要区分可恢复错误、权限错误和危险副作用。
5. 工具很多时，可以先检索相关工具，再动态绑定给模型。
6. `RunnableConfig`（运行配置对象）适合给工具注入用户、租户、线程等运行时信息。
7. `InjectedState`（状态注入器）适合让工具读取图内部状态，而不是让模型填写内部字段。

## 补充资料

- [tools_condition reference](https://reference.langchain.com/python/langgraph.prebuilt/tool_node/tools_condition)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangGraph（3） | 属于技能 | [[AI Agent相关/AI Agent]] |
| LangGraph（3） | 前置知识 | [[LangGraph（1）]] |
| LangGraph（3） | 前置知识 | [[LangGraph（2）]] |
| LangGraph（3） | 前置知识 | Function Calling |
| LangGraph（3） | 相关知识 | ToolNode（工具执行节点） |
| LangGraph（3） | 相关知识 | tools_condition（工具路由条件） |
| LangGraph（3） | 相关知识 | RunnableConfig（运行配置对象） |
| LangGraph（3） | 相关知识 | InjectedState（状态注入器） |
| LangGraph（3） | 相关知识 | RetryPolicy（重试策略） |
| LangGraph（3） | 相关知识 | [[LangGraph总结]] |
| LangGraph工具调用 | 有示例代码 | 代码/LangGraphV1.x/toolUse/模型调用.py |
| LangGraph工具调用 | 有示例代码 | 代码/LangGraphV1.x/toolUse/LangGraph_ToolNode.py |
| LangGraph工具错误处理 | 有示例代码 | 代码/LangGraphV1.x/toolUse/异常ToolNode.py |
| LangGraph大量工具选择 | 有示例代码 | 代码/LangGraphV1.x/toolUse/如何处理大量工具.py |
| LangGraph工具上下文 | 有示例代码 | 代码/LangGraphV1.x/toolUse/如何传递配置给工具.py |
| LangGraph工具上下文 | 有示例代码 | 代码/LangGraphV1.x/toolUse/如何将图状态传递给工具.py |
| LangGraph节点重试 | 有示例代码 | 代码/LangGraphV1.x/toolUse/示例9_如何添加节点重试策略.py |
| LangGraph（3） | 被考察于 | ToolNode（工具执行节点）和 bind_tools（绑定工具）有什么区别 |
| LangGraph（3） | 被考察于 | 工具很多时为什么要先做工具检索 |
| LangGraph（3） | 应用于 | 工具增强型 Agent |
