## 背景介绍

本节对应 `LangChain03` 资料中的工具调用和中间件部分，主题是工具定义、Function Calling、SQL 工具链、`create_agent`、短期记忆和 Agent middleware。

本节保存的示例代码位于：

- `代码/tools/`
- `代码/middleware/`
- `代码/tools/world_full.sql`

这节和 [[LangGraph/LangGraph（3）]] 关系很近：LangChain 提供更高层的 Agent 和 middleware 入口，LangGraph 负责更底层的工具循环、状态注入、重试和复杂控制流。

## 英文术语中文名

| 英文术语 | 中文名 | 说明 |
| --- | --- | --- |
| Tool | 工具 | Agent、链或模型可调用的外部能力 |
| Function Calling | 函数调用 | 模型生成工具名和参数的能力 |
| Toolkits | 工具包 | 一组服务于同一目标的工具集合 |
| `@tool` | 工具装饰器 | 把 Python 函数声明为 LangChain 工具 |
| `bind_tools` | 绑定工具 | 告诉模型有哪些工具可用 |
| `create_agent` | 创建 Agent | LangChain V1.0 推荐的 Agent 入口 |
| checkpointer | 检查点保存器 | 保存短期记忆和线程状态 |
| InMemorySaver | 内存检查点 | 开发演示用的短期记忆 |
| Middleware | 中间件 | 在 Agent 生命周期中插入控制逻辑 |
| before_model | 模型前钩子 | 模型调用前修改消息、上下文或状态 |
| after_model | 模型后钩子 | 模型响应后做记录或校验 |
| wrap_model_call | 模型调用包裹钩子 | 在模型调用周围做重试、fallback、日志 |
| PII | 个人敏感信息 | 邮箱、手机号等需要脱敏的信息 |

## 工具的组成

课程 PPT 对工具的定义很直接：工具是 AI Agent、链或 LLM 与外部世界互动的接口。一个工具通常包含：

| 要素 | 作用 |
| --- | --- |
| 名称 | 让模型知道工具叫什么 |
| 描述 | 让模型判断什么时候该用 |
| 参数 schema | 让模型生成正确参数 |
| 执行函数 | 真正访问 API、数据库、文件或业务系统 |
| 返回策略 | 工具结果是直接给用户，还是回传给模型继续推理 |

`代码/tools/Test_Tool.py` 用 `@tool` 定义了查询日期和打开浏览器的工具，并用 `model.bind_tools([...])` 让模型能产生工具调用。

## bind_tools 不等于执行工具

这是工具调用最容易混的点：

| 步骤 | 说明 |
| --- | --- |
| `bind_tools` | 把工具 schema 绑定给模型，让模型知道可调用工具 |
| 模型输出 `tool_calls` | 模型决定要调用哪个工具、传什么参数 |
| 工具执行 | 程序或 Agent runtime 真正运行函数 |
| ToolMessage 回传 | 把工具结果作为消息放回模型上下文 |
| 模型最终回答 | 模型根据工具结果生成自然语言答案 |

如果只是 `bind_tools`，模型可能只返回工具调用请求；要真正执行，通常需要 Agent runtime、`ToolNode` 或自己写调度逻辑。这个机制和 [[LangGraph/LangGraph（3）]] 里的 `ToolNode` 是同一个核心问题。

## SQL 工具链

`代码/tools/use_tools_query_sql.py` 展示了一个确定性 SQL 问答链：

```text
用户问题
-> create_sql_query_chain 生成 SQL
-> SQLCleaner 清理 markdown 代码块和前缀
-> QuerySQLDatabaseTool 执行 SQL
-> Prompt 汇总 question/query/result
-> 模型生成自然语言回答
```

这个例子不是让模型自由决定是否查询数据库，而是把 SQL 生成和 SQL 执行固定成链。它适合场景明确、数据源明确、查询动作必然发生的业务。

需要注意：

| 风险 | 处理建议 |
| --- | --- |
| 数据库账号写死 | 生产中用环境变量或密钥管理 |
| 模型生成危险 SQL | 限制只读账号、SQL 白名单、表级权限 |
| SQL 代码块无法直接执行 | 用 `SQLCleaner` 做输出解析 |
| 查询结果太大 | 限制 `LIMIT`、分页、超时 |
| schema 泄露 | 只暴露必要表和字段 |

## create_agent

课程代码 `代码/tools/lc-functioncall-demo2.py` 和中间件示例都使用 `create_agent`。V1.0 的推荐理解是：

```text
Agent = Model + Tools + System Prompt + Middleware + Memory
```

Agent 的循环通常是：

```text
模型调用 -> 判断是否需要工具 -> 执行工具 -> 工具结果回到模型 -> 直到模型不再调用工具
```

适合用 Agent 的条件：

| 条件 | 说明 |
| --- | --- |
| 工具是否调用不固定 | 模型需要根据问题决定 |
| 工具调用次数不固定 | 可能查一次，也可能多步查询 |
| 需要短期记忆 | 同一 `thread_id` 下继续上下文 |
| 需要中间件控制 | 日志、脱敏、摘要、限流、人工审批 |

如果流程是固定的，仍优先 LCEL；如果流程是模型自主决策的，再用 Agent。

## 中间件

LangChain V1.0 的 middleware 用来控制 Agent 生命周期。官方内置中间件覆盖摘要、人机协作、调用次数限制、PII 检测、重试、fallback、工具选择等常见模式。

课程代码里有三类示例：

| 代码 | 主题 |
| --- | --- |
| `custom_mw_by_class.py` | 通过继承 `AgentMiddleware` 实现日志中间件 |
| `custom_mw_by_decorators.py` | 通过装饰器写 `before_model`、`wrap_model_call` |
| `custom_mw_desensitize.py` | 在模型调用前对邮箱和手机号脱敏 |
| `SummarizationMiddleware_test.py` | 长对话到阈值后自动摘要 |

中间件的价值是把横切逻辑从业务 Prompt 里拿出来。脱敏、日志、限流、模型 fallback、摘要、人工审批都不应该散落在每个 Prompt 中。

## 短期记忆

`create_agent` 可以传入 checkpointer 实现 thread 级短期记忆。课程代码使用 `InMemorySaver`：

```text
agent = create_agent(..., checkpointer=memory)
agent.invoke(..., config={"configurable": {"thread_id": "xxx"}})
```

理解重点：

| 概念 | 说明 |
| --- | --- |
| checkpointer | 保存 Agent 执行状态 |
| thread_id | 区分不同会话线程 |
| InMemorySaver | 内存保存，适合演示，不适合生产长期保存 |
| 持久化后端 | 生产需要数据库、Redis 或 LangGraph 持久化方案 |

这和 [[LangGraph/LangGraph（4）]] 的 checkpoint 思路一致，只是 LangChain 在 `create_agent` 入口做了更高层封装。

## 工具调用与 MCP、A2A

LangChain 工具调用是“单个 Agent 调用外部能力”的基础。和已有笔记可以这样连接：

| 能力 | 对应笔记 |
| --- | --- |
| 单 Agent 调工具 | [[LangGraph/LangGraph（3）]] |
| 多 Agent 交接 | [[LangGraph/LangGraph（4）]] |
| 标准化外部工具协议 | [[MCP、A2A与Agent Skills/MCP、A2A与Agent Skills总结]] |
| Agent Skills 文件化能力 | [[MCP、A2A与Agent Skills/MCP、A2A与Agent Skills（3）]] |

如果工具只是当前应用内部的 Python 函数，用 `@tool` 即可；如果工具要跨进程、跨语言、跨平台复用，再考虑 MCP。

## 易错点

| 易错点 | 正确理解 |
| --- | --- |
| 工具描述无所谓 | 模型靠描述判断何时调用工具，描述质量会影响稳定性 |
| `bind_tools` 会自动执行函数 | 它只让模型产生工具调用请求，执行还需要 runtime |
| 所有数据库问答都要 Agent | 固定 SQL 问答链用 LCEL 更可控 |
| 中间件只是日志 | middleware 可做摘要、脱敏、重试、fallback、人机审批 |
| InMemorySaver 可用于生产 | 它适合演示，生产要用持久化 checkpointer |
| 工具调用天然安全 | 工具必须做权限、参数校验、超时和审计 |

## 补充资料

- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain middleware overview](https://docs.langchain.com/oss/python/langchain/middleware/overview)
- [LangChain custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom)
- [LangChain prebuilt middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangChain（4） | 属于技能 | [[AI Agent]] |
| LangChain（4） | 相关知识 | [[LangChain总结]] |
| LangChain（4） | 前置知识 | [[LangChain（2）]] |
| LangChain（4） | 相关知识 | [[LangGraph/LangGraph（3）]] |
| LangChain（4） | 相关知识 | [[MCP、A2A与Agent Skills/MCP、A2A与Agent Skills总结]] |
| LangChain（4） | 有示例代码 | 代码/tools/Test_Tool.py |
| LangChain（4） | 有示例代码 | 代码/tools/use_tools_query_sql.py |
| LangChain（4） | 有示例代码 | 代码/middleware/custom_mw_desensitize.py |
| LangChain（4） | 有示例代码 | 代码/middleware/SummarizationMiddleware_test.py |
| Function Calling | 应用于 | 外部工具调用 |
| Middleware | 应用于 | Agent 安全控制和上下文工程 |
| SQL 工具链 | 被考察于 | 如何让自然语言问题转 SQL 并返回业务答案 |

相关：[[LangChain（1）]] [[LangChain（2）]] [[LangChain（3）]] [[LangChain总结]] [[LangGraph/LangGraph（3）]]
