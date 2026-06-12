## 背景介绍

本节对应 `LangChain02` 资料，主题是 LCEL、Runnable 组件、记忆管理，以及电商客服实战。

本节保存的示例代码位于：

- `代码/lcel/`
- `代码/lcel/chatbot/`
- `代码/lcel/customer/`
- `代码/requirements_day02.txt`

LCEL 是课程中最重要的链式组合方式。即使 V1.0 更推荐用 `create_agent` 做 Agent，LCEL 仍适合确定性的工作流：翻译、分类、抽取、RAG chain、SQL chain、数据清洗和后端 API 流程。

## 英文术语中文名

| 英文术语 | 中文名 | 说明 |
| --- | --- | --- |
| LCEL | LangChain 表达式语言 | 用声明式方式组合 LangChain 组件 |
| Runnable | 可运行组件 | 支持 `invoke`、`stream`、`batch` |
| RunnableSequence | 顺序链 | 多个步骤依次执行 |
| RunnableLambda | 函数包装器 | 把普通 Python 函数变成链节点 |
| RunnableParallel / RunnableMap | 并行链 | 多个分支同时处理同一输入 |
| RunnablePassthrough | 透传组件 | 保留原始输入，并可通过 `assign` 增加字段 |
| stream | 流式输出 | 边生成边返回 |
| batch | 批处理 | 一次处理多个输入 |
| ChatMessageHistory | 消息历史 | 管理对话消息列表 |
| RunnableWithMessageHistory | 自动会话历史管理 | 自动读取和写入不同会话的历史 |
| RedisChatMessageHistory | Redis 消息历史 | 把聊天记录持久化到 Redis |

## LCEL 的基本模型

LCEL 的核心是把组件接成一条可执行管道：

```text
Prompt -> Model -> OutputParser
```

代码里通常写成：

```text
prompt | model | parser
```

链上的组件一般都支持三个常用方法：

| 方法 | 含义 | 适合场景 |
| --- | --- | --- |
| `invoke` | 单输入单输出 | 普通问答、单条分类 |
| `stream` | 流式返回 | 聊天前端、长文本生成 |
| `batch` | 批量输入输出 | 批量摘要、批量标签 |

`代码/lcel/lcel_sequence.py` 展示了显式 `RunnableSequence`，`lcel_stream.py` 和 `lcel_batch.py` 分别展示流式和批处理。实际写业务时，优先用管道操作符 `|`，更短也更符合 LCEL 的阅读方式。

## RunnableLambda

`RunnableLambda` 用来把普通 Python 函数塞进链里。

适合这些场景：

| 场景 | 说明 |
| --- | --- |
| 数据清洗 | 去掉空格、正则提取、格式转换 |
| 业务规则 | 根据订单状态、用户等级、风险等级补充字段 |
| 模型前处理 | 把复杂对象转成 Prompt 需要的字符串 |
| 模型后处理 | 把模型结果映射成业务状态 |

`代码/lcel/lcel_lambda.py` 和 `代码/lcel/customer/lcel_customerService.py` 都用到了这个思路。关键点是：不是所有逻辑都要交给模型，确定性逻辑应留在 Python 函数里，再通过 LCEL 接入流程。

## RunnableParallel

`RunnableParallel` / `RunnableMap` 用来把同一个输入并行送到多个分支。

在客服系统里，用户反馈可以并行做这些事：

| 分支 | 作用 |
| --- | --- |
| `sentiment` | 判断情绪倾向 |
| `categories` | 判断问题类别 |
| `urgency` | 判断紧急程度 |
| `order_id` | 提取订单号 |

这比把所有任务塞进一个 Prompt 更容易维护。每个分支可以单独测试，也可以替换为规则、模型或工具。

## RunnablePassthrough

`RunnablePassthrough` 的重点是“保留原输入，同时补充新字段”。

常见写法是：

```text
RunnablePassthrough.assign(new_field=some_chain)
```

课程里的 SQL 和 RAG 示例也大量用到这个思路：先保留用户问题，再把检索结果、SQL 查询或模型分析结果附加到同一个字典里，最后交给 Prompt 汇总。

记忆这个组件时不要只记“透传”。更准确的理解是：它是 LCEL 中构造上下文字典的常用工具。

## 记忆管理

大模型本身无状态，不会自动记住上一次对话。旧版 `ConversationBufferMemory` 等组件已经不推荐作为新项目入口，课程中重点转向：

| 组件 | 作用 |
| --- | --- |
| `ChatMessageHistory` | 保存消息列表 |
| `RedisChatMessageHistory` | 把消息历史存进 Redis |
| `RunnableWithMessageHistory` | 在链调用前后自动注入和保存历史 |

`代码/lcel/chatbot/llm_has_no_memory.py` 展示了无记忆模型的局限；`llm_chatMessageHistory.py` 和 `chatbot.py` 展示了如何把历史消息放进 Prompt；`chatbotwithredis.py` 展示了 Redis 持久化版本。

工程上要注意：记忆不是越多越好。长对话必须做摘要、裁剪或检索式记忆，否则上下文膨胀会增加成本并降低回答稳定性。这个问题在 [[LangGraph/LangGraph（4）]] 的持久化和会话摘要里也会继续出现。

## 电商客服实战

`代码/lcel/customer/lcel_customerService.py` 是本节最完整的业务例子。它不是单纯聊天，而是把用户反馈处理成一个后端工作流：

```text
用户反馈
-> 提取订单号
-> 并行情绪分析、问题分类、紧急度判断
-> 组合上下文
-> 生成客服回复
-> FastAPI 对外提供接口
```

这个例子体现了 LCEL 的工程价值：

| 能力 | 代码体现 |
| --- | --- |
| 规则和模型混编 | 正则提取订单号 + LLM 分类 |
| 并行处理 | `RunnableParallel` 同时做多项分析 |
| 上下文补充 | `RunnablePassthrough.assign` 增加字段 |
| API 化 | FastAPI 暴露 `/process-feedback` |
| 前端联调 | `代码/lcel/customer/index.html` 调用后端 |

这类流程不一定需要 Agent。因为步骤基本固定，LCEL 比工具循环更可控，调试也更直接。

## LCEL 与 Agent 的边界

| 任务类型 | 更适合 |
| --- | --- |
| 固定步骤：分类、抽取、翻译、RAG chain、SQL chain | LCEL |
| 模型需要自主选择工具、可能多轮调用工具 | `create_agent` |
| 需要中断、审批、复杂状态和多 Agent 编排 | LangGraph |
| 需要低代码平台快速验证 | Dify / RAGFlow 等平台 |

不要因为 LangChain V1.0 推 Agent，就把所有任务都改成 Agent。能用确定性链表达清楚的流程，优先用 LCEL。

## 易错点

| 易错点 | 正确理解 |
| --- | --- |
| `|` 只是语法糖 | 它代表 Runnable 组合，组合后的链也能 `invoke`、`stream`、`batch` |
| 所有步骤都要调用模型 | 规则、正则、数据库查询可以用 Python 函数或工具节点完成 |
| 并行链会自动处理依赖 | 并行分支适合互不依赖的任务，有依赖时要拆成顺序步骤 |
| 有消息历史就等于长期记忆 | `ChatMessageHistory` 是短期会话历史，长期记忆还需要存储、检索和更新策略 |
| 客服系统必须做成 Agent | 固定工单处理链用 LCEL 更直接 |

## 补充资料

- [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangChain（2） | 属于技能 | [[AI Agent]] |
| LangChain（2） | 相关知识 | [[LangChain总结]] |
| LangChain（2） | 前置知识 | [[LangChain（1）]] |
| LangChain（2） | 相关知识 | [[LangGraph/LangGraph（4）]] |
| LangChain（2） | 有示例代码 | 代码/lcel/lcel_sequence.py |
| LangChain（2） | 有示例代码 | 代码/lcel/lcel_parallel.py |
| LangChain（2） | 有示例代码 | 代码/lcel/chatbot/chatbot.py |
| LangChain（2） | 有示例代码 | 代码/lcel/customer/lcel_customerService.py |
| LCEL | 应用于 | 电商客服自动处理 |
| RunnableWithMessageHistory | 相关知识 | 短期记忆 |
| RedisChatMessageHistory | 应用于 | 多用户聊天机器人 |

相关：[[LangChain（1）]] [[LangChain（3）]] [[LangChain（4）]] [[LangChain总结]] [[LangGraph/LangGraph（4）]]
