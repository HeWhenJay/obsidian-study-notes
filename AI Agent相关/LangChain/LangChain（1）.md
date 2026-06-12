## 背景介绍

本节对应 `LangChain01` 资料，主题是 LangChain 的定位、体系、应用生命周期、Model I/O，以及如何把链部署成 API。

本节保存的示例代码位于：

- `代码/langchain_day01/`
- `代码/langchain_day01/ModelIO/`
- `代码/langchain_day01/ModelIO/exh_prmpt/`
- `代码/langchain_day01/ModelIO/exh_prsr/`

课程讲义同时强调了 V1.0 的新定位：LangChain 不再只是“链式调用工具箱”，而是更偏向构建 Agent 的高层入口；底层复杂编排交给 [[LangGraph/LangGraph总结]]，LangChain 用 `create_agent`、模型接口、工具、消息、短期记忆、中间件等组件提供更快的工程入口。

## 英文术语中文名

代码标识符保留英文，正文里优先按下面的中文名理解：

| 英文术语 | 中文名 | 说明 |
| --- | --- | --- |
| LangChain | 大模型应用开发框架 | 把模型、Prompt、工具、检索、部署和观测接到一个应用流程中 |
| LangGraph | 状态图编排框架 | V1.0 Agent 的底层运行时，也可独立使用 |
| LangSmith | 调试评估与观测平台 | 用于 trace、测试、评估和线上监控 |
| LangServe | 链服务部署工具 | 把 LangChain 链暴露为 REST API |
| Model I/O | 模型输入输出流程 | Prompt 格式化、模型调用、输出解析 |
| PromptTemplate | 提示词模板 | 把变量填入提示词文本 |
| ChatPromptTemplate | 聊天提示词模板 | 组织 system、human、AI 等多角色消息 |
| OutputParser | 输出解析器 | 把模型文本解析成字符串、JSON、日期或自定义结构 |
| Chat Model | 聊天模型包装器 | 以消息列表为输入，返回模型消息 |
| Embedding Model | 嵌入模型包装器 | 把文本转成向量，用于 RAG 和语义检索 |
| Runnable | 可运行组件 | 支持 `invoke`、`stream`、`batch` 的统一接口 |

## LangChain 的定位

课程给 LangChain 的核心定义是：面向 LLM 应用开发的框架，用标准化组件把大模型和外部数据源、工具、业务系统连接起来。

在工程上可以这样理解：

| 层次 | 作用 |
| --- | --- |
| 模型层 | 用统一接口调用通义千问、DeepSeek、OpenAI 兼容模型等 |
| Prompt 层 | 管理提示词模板、少样本示例、局部变量 |
| 输出层 | 把模型生成的自然语言解析成可继续处理的数据 |
| 链和 Runnable 层 | 把 Prompt、模型、解析器、检索器、工具等组合成流程 |
| Agent 层 | 让模型在循环中决定是否调用工具，直到完成任务 |
| 观测和部署层 | 用 LangSmith 做 trace，用 LangServe 或 FastAPI 对外提供服务 |

V1.0 后更推荐把 LangChain 看成“Agent 快速通道”：需要高层 Agent 时用 `create_agent`，需要精细状态图时下钻到 [[LangGraph/LangGraph总结]]，需要旧链或兼容旧教程时再使用 `langchain-classic`。

## LangChain 体系

讲义中列出的生态组件可以按职责分成几类：

| 组件 | 作用 |
| --- | --- |
| `langchain` | V1.0 主入口，聚焦 Agent、模型、工具和消息等核心构建块 |
| `langchain-core` | 核心抽象和接口，例如 prompts、messages、runnables |
| `langchain-community` | 社区集成，例如加载器、向量库、第三方模型包装器 |
| `langchain-classic` | 旧版 chains、AgentExecutor 和遗留工具的迁移位置 |
| `langchain-openai` 等 provider 包 | 各模型厂商的轻量集成包 |
| `LangGraph` | 有状态图编排、持久化、人机协作和复杂控制流 |
| `LangServe` | 将链或 Runnable 暴露为 REST API |
| `LangSmith` | 调试、测试、评估和监控 LLM 应用 |

这里最容易混的是 `langchain` 和 `langchain-classic`。课程代码里仍会看到 `create_stuff_documents_chain`、`create_sql_query_chain` 等 classic chain；新项目如果是 Agent 应用，优先从 `create_agent` 和 middleware 入手。

## 应用程序生命周期

LangChain 简化的是 LLM 应用从开发到部署的生命周期：

| 阶段 | 关注点 | 典型工具 |
| --- | --- | --- |
| 开发 | 快速组合模型、Prompt、解析器、检索器、工具 | LangChain、LCEL、provider 包 |
| 调试测试 | 观察每一步输入输出、定位失败链路 | LangSmith trace、回放、评估 |
| 生产部署 | 暴露 API、接入业务系统、管理密钥和日志 | LangServe、FastAPI、Uvicorn |
| 持续优化 | 评估回答质量、优化 Prompt、检索和工具选择 | LangSmith、RAG 评估、线上反馈 |

`代码/langchain_day01/ModelIO/deploy_service.py` 用 `FastAPI` 和 `langserve.add_routes` 把翻译链注册成服务；`deploy_client.py` 用 `RemoteRunnable` 调用远程链。这个例子说明 LangChain 的链不是只能在脚本里跑，也可以成为后端 API 的一部分。

## Model I/O

课程把模型使用过程拆成三步：

```text
Format（提示词格式化） -> Predict（模型调用） -> Parse（输出解析）
```

对应到 LangChain：

| 环节 | LangChain 组件 | 代码入口 |
| --- | --- | --- |
| Format | `PromptTemplate`、`ChatPromptTemplate`、`FewShotPromptTemplate` | `代码/langchain_day01/ModelIO/exh_prmpt/` |
| Predict | `ChatOpenAI`、`ChatTongyi`、自定义 `models.py` 包装 | `代码/langchain_day01/ModelIO/modelIO.py` |
| Parse | `StrOutputParser`、`JsonOutputParser`、自定义 parser | `代码/langchain_day01/ModelIO/exh_prsr/` |

学习时不要只记 API 名。更重要的是把模型调用看成一个可组合的流水线：Prompt 决定模型看到什么，模型决定生成什么，Parser 决定后续程序拿到什么类型的数据。

## Prompt 模板

`exh_prmpt` 目录覆盖了几类模板：

| 代码 | 学习重点 |
| --- | --- |
| `stringTemplate.py` | 普通字符串模板，适合单轮补全或简单翻译 |
| `chatTemplate.py` | 多消息模板，适合 system/human 角色分离 |
| `fewshot_prmpt.py`、`fewshot_prmpt2.py` | 少样本提示词，把示例作为模型行为参照 |
| `partial_prompt.py` | 预填固定变量，减少调用时重复传参 |

Prompt 模板的价值不是“格式更漂亮”，而是把提示词从散落的字符串变成可复用、可测试、可替换的组件。

## 输出解析

`exh_prsr` 目录展示了几类输出解析：

| 代码 | 解析目标 | 使用场景 |
| --- | --- | --- |
| `string_parser.py` | 纯文本字符串 | 翻译、摘要、普通问答 |
| `json_parsar.py` | JSON 结构 | 分类、抽取、表单字段、前后端交互 |
| `csv_parser.py` | CSV 风格输出 | 批量结构化数据 |
| `datetime_parser.py` | 日期时间 | 需要标准时间字段的业务 |
| `test.py` | 自定义 `BaseOutputParser` | 模型输出有特殊格式时 |

如果后续流程要依赖模型结果，尽量不要直接处理自由文本。先用 parser 把结果收敛成可校验的数据结构，再交给业务逻辑。

## 环境变量

课程代码中的模型包装器主要读取这些变量：

| 变量 | 用途 |
| --- | --- |
| `DASHSCOPE_API_KEY` | 阿里通义千问 / DashScope 兼容 OpenAI 接口 |
| `TENCENT_HUNYUAN_API_KEY` | 腾讯混元接口 |
| `DEEPSEEK_API_KEY` | DeepSeek 接口 |
| `BAICHUAN_API_KEY` | 百川嵌入模型 |
| `TENCENT_SECRET_ID`、`TENCENT_SECRET_KEY` | 腾讯云相关鉴权 |

运行课程代码前，先检查 `代码/langchain_day01/models.py` 中的 base URL 和模型名是否与当前账号支持的模型一致。

## 易错点

| 易错点 | 正确理解 |
| --- | --- |
| LangChain 等于旧版 Chain | V1.0 更聚焦 Agent，旧链迁到 `langchain-classic` |
| 只会调用模型就是会 LangChain | LangChain 的重点是把模型接入 Prompt、Parser、工具、检索和部署 |
| Prompt 输出可以随便让业务代码解析 | 生产中应优先用 parser 或结构化输出约束 |
| `ChatOpenAI` 只能调用 OpenAI | 只要兼容 OpenAI 协议，也可用于 DashScope、DeepSeek 等 |
| LangServe 可以替代全部后端 | LangServe 适合暴露链，复杂业务仍要结合 FastAPI、权限、日志和队列 |

## 补充资料

- [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain v1 migration guide](https://docs.langchain.com/oss/python/migrate/langchain-v1)
- [LangChain install](https://docs.langchain.com/oss/python/langchain/install)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangChain（1） | 属于技能 | [[AI Agent]] |
| LangChain（1） | 相关知识 | [[LangChain总结]] |
| LangChain（1） | 相关知识 | [[LangGraph/LangGraph总结]] |
| LangChain（1） | 前置知识 | Python 基础 |
| LangChain（1） | 前置知识 | FastAPI |
| LangChain（1） | 有示例代码 | 代码/langchain_day01/ModelIO/helloworld.py |
| LangChain（1） | 有示例代码 | 代码/langchain_day01/ModelIO/deploy_service.py |
| LangChain（1） | 有示例代码 | 代码/langchain_day01/ModelIO/exh_prsr/json_parsar.py |
| Model I/O | 相关知识 | PromptTemplate |
| Model I/O | 相关知识 | OutputParser |
| LangServe | 应用于 | 链服务 API 部署 |

相关：[[LangChain总结]] [[LangChain（2）]] [[LangChain（3）]] [[LangChain（4）]] [[LangGraph/LangGraph总结]]
