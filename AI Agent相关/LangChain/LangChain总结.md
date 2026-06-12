## 总览

本专题对应 `LangChain01`、`LangChain02`、`LangChain03` 资料，已整理为四节：

- [[LangChain（1）]]：LangChain 定位、体系、应用生命周期、Model I/O、Prompt、Parser、LangServe/FastAPI 部署。
- [[LangChain（2）]]：LCEL、Runnable、流式/批量、并行、透传、消息历史和电商客服实战。
- [[LangChain（3）]]：LangChain RAG，覆盖文档加载、切分、Document、Embedding、Vector Store、Retriever、RAG chain。
- [[LangChain（4）]]：工具调用、Function Calling、SQL 工具链、`create_agent`、短期记忆和 middleware。

代码已保存到 `代码/`。没有复制 `.venv`、`.idea` 和缓存文件；运行示例前需要按课程环境安装依赖，并配置模型 API Key。

## 术语总表

| 英文术语 | 中文名 | 所属主题 |
| --- | --- | --- |
| LangChain | 大模型应用开发框架 | 总体 |
| LangGraph | 状态图编排框架 | Agent 底层运行时 |
| LangSmith | 调试评估与观测平台 | 观测 |
| LangServe | 链服务部署工具 | 部署 |
| Model I/O | 模型输入输出流程 | 基础 |
| PromptTemplate | 提示词模板 | Model I/O |
| ChatPromptTemplate | 聊天提示词模板 | Model I/O |
| OutputParser | 输出解析器 | Model I/O |
| LCEL | LangChain 表达式语言 | 链 |
| Runnable | 可运行组件 | 链 |
| RunnableLambda | 函数包装器 | 链 |
| RunnableParallel | 并行链 | 链 |
| RunnablePassthrough | 透传组件 | 链 |
| ChatMessageHistory | 消息历史 | 记忆 |
| RunnableWithMessageHistory | 自动会话历史管理 | 记忆 |
| Document | 文档对象 | RAG |
| Text Splitter | 文本切分器 | RAG |
| Embeddings | 嵌入模型包装器 | RAG |
| Vector Store | 向量存储 | RAG |
| Retriever | 检索器 | RAG |
| create_stuff_documents_chain | Stuff 文档链 | RAG |
| create_retrieval_chain | 检索问答链 | RAG |
| Tool | 工具 | Agent |
| Function Calling | 函数调用 | 工具调用 |
| `@tool` | 工具装饰器 | 工具调用 |
| `bind_tools` | 绑定工具 | 工具调用 |
| create_agent | 创建 Agent | V1.0 Agent |
| Middleware | 中间件 | Agent 控制 |
| checkpointer | 检查点保存器 | 短期记忆 |

## 核心结论

LangChain 的核心不是“替你写 Prompt”，而是把 LLM 应用拆成可组合、可调试、可替换的工程组件：

```text
Model + Prompt + Parser + Runnable + Retriever + Tool + Middleware + Observability
```

可以按四个层级理解：

| 层级 | 解决的问题 |
| --- | --- |
| Model I/O | 如何把输入变成模型可理解的消息，再把模型输出变成程序可处理的数据 |
| LCEL | 如何把确定性步骤组合成可运行流程 |
| RAG | 如何把外部知识加载、索引、检索并注入模型上下文 |
| Agent | 如何让模型在循环中选择工具，并通过 middleware 和 memory 受控运行 |

V1.0 后的主线是：简单 Agent 用 LangChain `create_agent`；复杂状态、人工审批、长流程和多 Agent 用 [[LangGraph/LangGraph总结]]；确定性工作流仍然用 LCEL；旧链和旧教程迁移时关注 `langchain-classic`。

## 四节知识地图

| 节次 | 主线 | 关键 API | 代码入口 |
| --- | --- | --- | --- |
| [[LangChain（1）]] | 基础定位和 Model I/O | `PromptTemplate`、`ChatPromptTemplate`、`ChatOpenAI`、`StrOutputParser`、`JsonOutputParser`、`add_routes` | `代码/langchain_day01/` |
| [[LangChain（2）]] | LCEL 和记忆 | `RunnableSequence`、`RunnableLambda`、`RunnableParallel`、`RunnablePassthrough`、`RunnableWithMessageHistory` | `代码/lcel/` |
| [[LangChain（3）]] | RAG 实战 | `Docx2txtLoader`、`RecursiveCharacterTextSplitter`、`DashScopeEmbeddings`、`Chroma`、`as_retriever`、`create_retrieval_chain` | `代码/rag/` |
| [[LangChain（4）]] | 工具调用和中间件 | `@tool`、`bind_tools`、`create_agent`、`QuerySQLDatabaseTool`、`AgentMiddleware`、`SummarizationMiddleware` | `代码/tools/`、`代码/middleware/` |

## 代码索引

| 主题 | 代码 |
| --- | --- |
| 模型调用包装 | `代码/langchain_day01/models.py` |
| 最小模型调用 | `代码/langchain_day01/ModelIO/helloworld.py`、`代码/langchain_day01/ModelIO/modelIO.py` |
| Prompt 模板 | `代码/langchain_day01/ModelIO/exh_prmpt/stringTemplate.py`、`代码/langchain_day01/ModelIO/exh_prmpt/chatTemplate.py`、`代码/langchain_day01/ModelIO/exh_prmpt/fewshot_prmpt2.py` |
| 输出解析 | `代码/langchain_day01/ModelIO/exh_prsr/string_parser.py`、`代码/langchain_day01/ModelIO/exh_prsr/json_parsar.py`、`代码/langchain_day01/ModelIO/exh_prsr/test.py` |
| API 部署 | `代码/langchain_day01/ModelIO/deploy_service.py`、`代码/langchain_day01/ModelIO/deploy_client.py` |
| LCEL 基础 | `代码/lcel/lcel_sequence.py`、`代码/lcel/lcel_stream.py`、`代码/lcel/lcel_batch.py` |
| LCEL 组件 | `代码/lcel/lcel_lambda.py`、`代码/lcel/lcel_parallel.py`、`代码/lcel/lcel_passthrough.py` |
| 预制文档链 | `代码/lcel/use_create_stuff_documents_chain.py` |
| 多用户聊天记忆 | `代码/lcel/chatbot/chatbot.py`、`代码/lcel/chatbot/chatbotwithredis.py` |
| 电商客服实战 | `代码/lcel/customer/lcel_customerService.py`、`代码/lcel/customer/index.html` |
| Word 文档 RAG | `代码/rag/doc_and_llm.py`、`代码/rag/人事管理流程.docx` |
| 网页 RAG | `代码/rag/rag_with_webpage.py` |
| 基础工具调用 | `代码/tools/Test_Tool.py`、`代码/tools/Test_call.py` |
| SQL 工具链 | `代码/tools/use_tools_query_sql.py`、`代码/tools/world_full.sql` |
| Agent 工具循环 | `代码/tools/lc-functioncall-demo2.py`、`代码/tools/lc_functioncall_demo.py` |
| 中间件 | `代码/middleware/custom_mw_by_class.py`、`代码/middleware/custom_mw_by_decorators.py`、`代码/middleware/custom_mw_desensitize.py`、`代码/middleware/SummarizationMiddleware_test.py` |

## 版本迁移要点

| 旧理解 | V1.0 后的理解 |
| --- | --- |
| LangChain 主要是 Chains | LangChain 聚焦 Agent harness，旧链迁到 `langchain-classic` |
| AgentExecutor 是主入口 | 新项目优先 `langchain.agents.create_agent` |
| ConversationBufferMemory 管理记忆 | 新 Agent 用 checkpointer 和 thread 级状态 |
| Hook 写在旧 Agent 结构里 | 使用 middleware 的 `before_model`、`after_model`、`wrap_model_call` 等 |
| 结构化输出靠 Prompt 强约束 | V1.0 更强调结构化输出策略和状态字段 |
| 复杂流程靠链嵌套 | 复杂可控流程下钻到 LangGraph |

课程代码有 V0.3 和 V1.0 内容混用，这是正常的学习资料过渡现象。复现时要先看 import 路径：如果来自 `langchain_classic`，说明是兼容旧链；如果来自 `langchain.agents.create_agent` 或 `langchain.agents.middleware`，说明已经是 V1.0 风格。

## 环境变量

| 变量 | 用途 |
| --- | --- |
| `DASHSCOPE_API_KEY` | 通义千问 / DashScope 兼容接口 |
| `TENCENT_HUNYUAN_API_KEY` | 腾讯混元模型 |
| `DEEPSEEK_API_KEY` | DeepSeek 模型 |
| `BAICHUAN_API_KEY` | 百川嵌入模型 |
| `TENCENT_SECRET_ID`、`TENCENT_SECRET_KEY` | 腾讯云鉴权 |

运行 RAG、工具和中间件示例前，还需要 Redis、MySQL、Chroma、docx2txt、相关模型 provider 包等依赖。具体依赖见 `代码/langchain_day01/requirements.txt`、`代码/requirements_day02.txt`、`代码/requirements_day03.txt`。

## 与已有专题的连接

| LangChain 内容 | 关联专题 |
| --- | --- |
| V1.0 Agent 底层基于 LangGraph | [[LangGraph/LangGraph总结]] |
| ToolNode、工具状态注入、工具重试 | [[LangGraph/LangGraph（3）]] |
| checkpoint、thread_id、短期记忆 | [[LangGraph/LangGraph（4）]] |
| RAG 文档加载到检索生成 | [[RAG相关/RAG]] |
| 查询优化、索引优化、重排序 | [[RAG相关/Pre-Retrieval预检索优化/Pre-Retrieval预检索优化]]、[[RAG相关/Post-Retrieval后检索优化/Post-Retrieval后检索优化]] |
| 外部工具协议化 | [[MCP、A2A与Agent Skills/MCP、A2A与Agent Skills总结]] |
| 多 Agent 与任务交接 | [[多Agent系统/多Agent系统总结]] |

## 复习重点

1. 能解释 Model I/O 的三段：Prompt 格式化、模型调用、输出解析。
2. 能写出最小 LCEL：`prompt | model | parser`。
3. 能说明 `invoke`、`stream`、`batch` 的区别。
4. 能说明 `RunnableLambda`、`RunnableParallel`、`RunnablePassthrough.assign` 各自解决什么问题。
5. 能解释短期消息历史为什么需要 `session_id` / `thread_id`。
6. 能画出 RAG 的两阶段：索引阶段和问答阶段。
7. 能说明 `Document.page_content` 和 `Document.metadata` 的作用。
8. 能比较向量检索、BM25 和混合检索。
9. 能解释 `bind_tools` 和真正执行工具之间的区别。
10. 能解释 middleware 为什么适合做脱敏、摘要、限流、fallback 和人工审批。

## 补充资料

- [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain v1 migration guide](https://docs.langchain.com/oss/python/migrate/langchain-v1)
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)
- [Build a RAG agent with LangChain](https://docs.langchain.com/oss/python/langchain/rag)
- [LangChain middleware overview](https://docs.langchain.com/oss/python/langchain/middleware/overview)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangChain总结 | 属于技能 | [[AI Agent]] |
| LangChain总结 | 相关知识 | [[LangChain（1）]] |
| LangChain总结 | 相关知识 | [[LangChain（2）]] |
| LangChain总结 | 相关知识 | [[LangChain（3）]] |
| LangChain总结 | 相关知识 | [[LangChain（4）]] |
| LangChain总结 | 相关知识 | [[LangGraph/LangGraph总结]] |
| LangChain总结 | 相关知识 | [[RAG相关/RAG]] |
| LangChain总结 | 相关知识 | [[MCP、A2A与Agent Skills/MCP、A2A与Agent Skills总结]] |
| LangChain总结 | 有示例代码 | 代码/langchain_day01/ModelIO/helloworld.py |
| LangChain总结 | 有示例代码 | 代码/lcel/customer/lcel_customerService.py |
| LangChain总结 | 有示例代码 | 代码/rag/doc_and_llm.py |
| LangChain总结 | 有示例代码 | 代码/tools/use_tools_query_sql.py |
| LangChain总结 | 有示例代码 | 代码/middleware/custom_mw_desensitize.py |
| LCEL | 应用于 | 确定性大模型工作流 |
| LangChain RAG | 应用于 | 企业知识库问答 |
| create_agent | 应用于 | 工具增强 Agent |
| Middleware | 应用于 | Agent 安全控制和上下文工程 |

相关：[[LangChain（1）]] [[LangChain（2）]] [[LangChain（3）]] [[LangChain（4）]] [[LangGraph/LangGraph总结]] [[RAG相关/RAG]]
