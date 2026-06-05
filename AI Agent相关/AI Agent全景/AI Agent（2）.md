## 背景介绍

本节对应 PPT 第 24-39 页，主题从 AI Agent 的整体架构进入两条落地路线：

1. AI Agent 应用开发框架和低代码平台怎么选。
2. Function Calling 为什么出现、怎么运作，以及如何用它完成真实业务接口调用。

前一节 [[AI Agent（1）]] 讲的是 Agent 的定义、规划、记忆、工具和执行闭环。本节重点是“工具调用”这条线：让大模型不只生成文字，而是能根据用户意图选择外部函数、生成参数、执行函数，并基于执行结果继续回答。

## AI Agent开发框架

AI Agent 开发框架的核心差异，通常体现在是否支持多智能体、是否适合复杂状态流、是否提供工具/记忆/文档加载器，以及企业级支持是否成熟。

![[AI Agent开发框架对比图.png]]

### LangChain V0.3

LangChain V0.3 更适合从单智能体入门。它通过链、代理、记忆、工具、文档加载器等模块组合出 Agent 能力，生态广，插件丰富，适合教学中拆解底层原理。

本章课程使用 LangChain V0.3，目的不是追新版本，而是为了更清楚地理解 Agent 的基础构成。

### LangChain V1.0

LangChain V1.0 提供更预构建的智能体架构和模型集成，既支持单智能体，也支持多智能体。它建立在 LangGraph 之上，更强调可控、可扩展的 Agent 应用开发。

如果做新项目，需要注意课程代码和当前框架版本之间可能存在 API 差异。

### LangGraph

LangGraph 更适合复杂状态流、多步骤任务和多智能体场景。它用有向图表达 Agent 流程，其中节点可以表示任务步骤，边可以表示流程逻辑。

它的价值在于：

- 支持循环和分支控制。
- 支持状态管理。
- 支持并行节点执行。
- 更适合严控流程延迟和业务逻辑的复杂 Agent。

可以理解为：LangChain 更像组件生态，LangGraph 更像可控的 Agent 流程编排工具。

### Semantic Kernel

Semantic Kernel 是微软生态里的 Agent/LLM 应用框架，偏向插件化架构。它的关键词是 Skills、Planner 和语义函数，适合紧密绑定 Azure、.NET/C#、Teams、Office 等微软生态的企业场景。

### AutoGen

AutoGen 偏向多智能体协作，强调多角色 Agent 定义和自主对话协商。典型结构是不同 Agent 承担不同角色，通过 GroupChat 一类的协作环境自动分配任务。

### CrewAI

CrewAI 也偏向多智能体，但更强调角色分工和流程管理。常见概念包括 Agent、Task、Process，适合把团队成员、目标和流程显式拆开。

## AI Agent低代码平台

低代码平台的选择不能只看“能不能搭出来”，还要看易用性、功能深度、集成能力、扩展性、模型支持、部署方式和定价。

![[AI Agent低代码平台对比图.png]]

### Coze

Coze 平台版偏向零代码模板，对非技术人员友好，插件生态较丰富，但更依赖官方市场和平台能力。PPT 中提到 Coze 开源版有待观察。

适合：快速搭建对话型 Agent、面向产品验证或非开发人员原型。

### Dify

Dify 对非技术人员较友好，同时支持多模型调度、Agent 工具链、私有化部署和自定义开发。它更适合在易用性和可扩展性之间取得平衡。

适合：企业内部知识助手、业务应用原型、多模型应用编排。

### FastGPT

FastGPT 更偏技术用户，支持本地 API 集成，开源免费，但对话交互和工具调用能力相对需要更多技术配置。

适合：有技术团队、希望快速搭建知识库问答和 API 集成的场景。

### n8n

n8n 本质上是通用流程编排工具，拥有大量通用 API 和代码扩展能力，但不是专门的内置 Agent 框架。要做 Agent，通常需要通过自定义节点、LLM 调用和流程编排来组合。

适合：业务自动化、API 串联、流程触发和系统集成。

### RagFlow

RagFlow 更偏 RAG 深度和文档问答，支持私有化部署，但通用 Agent 框架能力相对弱，扩展方向更垂直。

适合：文档解析、知识库问答、RAG 应用。

## Function Calling诞生的技术必然性

大语言模型本身存在局限：模型参数内的知识会过期，无法直接获取实时信息，也无法直接执行外部操作。

例如用户问“今天的天气怎么样”“今天北京到上海有没有票”“一班学生数学成绩是多少”，普通 LLM 如果只依赖自身知识，无法可靠回答。它需要外部数据源、业务系统或工具函数。

Function Calling 的意义就是让大模型具备“选择并调用外部函数”的能力。它也是 AI Agent 工具调用的核心基础之一。

## Function Calling基本流程

Function Calling 的本质不是让模型真的在内部执行 Python 函数，而是让模型根据函数说明判断应该调用哪个函数，并生成函数参数；真正的函数执行仍然由应用程序完成。

![[Function Calling核心流程说明.png]]

基本流程如下：

```text
用户提问 + 函数说明 -> 大模型判断要调用的函数和参数
应用程序执行本地函数或外部API -> 得到函数结果
函数结果回传给大模型 -> 大模型基于结果生成最终回答
```

更细化地看：

1. 大模型应用或 Agent 将用户问题和函数说明一起发给模型。
2. 模型判断是否需要调用函数，并返回函数名和参数。
3. 应用程序根据模型返回的函数名和参数，调用真实的本地函数、业务接口或外部 API。
4. 应用程序把函数执行结果追加到 messages 中，以 `tool` 角色返回给模型。
5. 模型基于函数结果生成最终自然语言回答。

## Function Calling实现过程

实现 Function Calling 通常需要三个部分。

![[Function Calling实现过程图解.png]]

### 1. 构建函数

先创建真实可执行的函数。例如 `fc_flow.py` 中的 `calculate_total_age_from_split_json` 会把 JSON 格式的数据转成 DataFrame，再计算所有人的年龄总和。

这一步要注意两个层面：

- 真实函数：应用程序最终要执行的 Python 函数或业务接口。
- 函数规范：传给模型看的 JSON Schema，描述函数名称、用途、参数类型、必填字段等。

### 2. 使用 tools 参数传递函数信息

调用模型时，通过 `tools` 参数把函数说明传给模型。模型看不到函数代码本身，它看到的是函数的名称、描述和参数结构。

示例中的核心字段包括：

- `type: function`
- `function.name`
- `function.description`
- `function.parameters`
- `required`

### 3. 加载并执行 Function Calling

模型返回 `tool_calls` 后，应用程序需要：

1. 读取模型返回的函数名。
2. 解析模型生成的 arguments。
3. 用函数名在本地函数映射表中找到真实函数。
4. 执行函数并得到结果。
5. 把结果以 `role: tool`、`tool_call_id`、`name`、`content` 的形式写回 messages。
6. 再次请求模型生成最终回答。

完整实践流程对应代码：`func/fc_flow.py`。

### 两个容易混淆的问题

**函数库是必需的吗？**

如果只是让模型“判断该调用什么”，函数库不是模型侧必需品；但如果要真正完成工具调用，应用程序侧必须有可执行函数或外部 API，并且通常需要一个函数映射表来把模型返回的函数名映射到真实执行逻辑。

**传给大模型的函数名称必须和 Python 函数本名一样吗？**

不一定。传给模型的函数名可以是业务上的别名，只要应用程序能用这个名字找到对应的真实函数即可。实际开发中，为了降低混乱，通常建议保持一致或建立清晰的映射表。

## 支持Function Calling的模型

PPT 中提到，Function Calling 会逐渐成为大模型标配能力。国产主流模型中，支持 Function Calling 的包括：

- 阿里千问。
- 智谱清言 ChatGLM。
- DeepSeek。

选型时不能只看模型是否能聊天，还要检查它是否稳定支持工具调用、参数生成是否可靠、是否兼容 OpenAI 风格接口，以及在业务场景中的实际效果。

## 实践1：动态SQL生成与数据库查询

这个项目要实现的是基于自然语言查询的智能数据库交互系统。用户用中文提问，模型通过 Function Calling 生成 SQL，应用程序执行数据库查询，再把结果交回模型生成最终回答。

![[动态SQL生成与数据库查询项目说明.png]]

核心代码：

- `func/db_init.py`：建表并插入测试数据，执行一次即可。
- `func/dynamic_sql.py`：定义数据库查询函数，并通过 Function Calling 让模型生成 SQL。

### 数据库结构

`db_init.py` 创建了三个表：

- `Classes`：班级表。
- `Students`：学生表。
- `Scores`：成绩表。

测试数据包括班级、学生和成绩，用于回答类似“一班的学生数学成绩是多少？”这类自然语言问题。

### 核心流程

1. 在提示词中把数据库 schema 告诉模型。
2. 定义 `ask_database(query)` 函数，用于执行 SQL。
3. 在 `tools` 中声明 `ask_database` 的函数规范。
4. 用户提出自然语言问题。
5. 模型根据问题和 schema 生成 SQL。
6. 应用程序执行 SQL 并返回查询结果。
7. 模型基于查询结果生成最终回答。

### 注意点

生产环境不能无约束执行模型生成的 SQL。至少要考虑：

- 只允许只读查询。
- 限制可访问表和字段。
- 审查或解析 SQL，避免危险语句。
- 增加权限控制和日志。
- 防止模型误解 schema 生成错误 SQL。

## 实践2：12306实时票务接口对接

这个项目通过请求 12306 网站接口获取车次信息，再利用大模型选择查票函数，查询某日某趟车次或某条路线的余票情况。

![[12306实时票务接口对接流程图.png]]

核心代码：`func/Ticketing_12306.py`。

### 核心流程

1. 定义爬虫/接口函数 `check_tick(date, start, end)`，根据日期、出发站编码和到达站编码查询票务信息。
2. 定义 `check_date()`，用于获取当前日期。
3. 定义 `function_map`，把模型返回的函数名映射到真实函数。
4. 在 `get_completion` 中通过 `tools` 描述可调用函数。
5. 用户提问，例如“查询今天北京到上海的票”。
6. 模型可能先调用 `check_date` 获取日期，再调用 `check_tick` 查询车票。
7. 应用程序循环处理 `tool_calls`，直到模型不再要求调用工具，最后输出最终回答。

代码中还使用了 `inspect.signature` 来判断函数是否有参数，从而决定如何调用函数。这说明工具调用不一定只有一次，也可能是多轮函数调用链。

### 注意点

12306 接口、Cookie、请求头和站点规则都可能变化，因此这类爬虫式工具更适合作为教学示例。真实项目中应关注接口稳定性、合规性、错误处理和限流。

## 相关代码包

本段 PPT 对应的主要代码在：

- `agent_base.zip`
  - `func/fc_flow.py`
  - `func/db_init.py`
  - `func/dynamic_sql.py`
  - `func/Ticketing_12306.py`
  - `func/dataformat.py`
  - `models.py`
- `agent_base_for_LC1.0.zip`
  - 包含与 LangChain V1.0 相关的改写版本，例如 `*_for_lcV1.py`。

`agent_numerology_v2.zip` 和 `agent_numerology_v2_for_LC1.0.zip` 更像后续完整项目包，不是第 24-39 页 Function Calling 主线的直接重点。

## 小结

本节的主线是：Agent 落地离不开框架选型和工具调用。

框架层面，LangChain、LangGraph、Semantic Kernel、AutoGen、CrewAI 适合不同复杂度和生态偏好的开发场景；低代码平台层面，Coze、Dify、FastGPT、n8n、RagFlow 则分别偏向原型、企业应用、知识库问答、流程自动化和 RAG 文档问答。

Function Calling 层面，它解决的是普通 LLM 无法获取实时数据、无法直接执行外部操作的问题。模型负责判断“调用哪个函数、传什么参数”，应用程序负责真正执行函数并把结果交回模型。动态 SQL 和 12306 查票都是这个机制的具体落地。

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| AI Agent（2） | 属于技能 | [[AI Agent相关/AI Agent]] |
| AI Agent（2） | 前置知识 | [[AI Agent（1）]] |
| AI Agent（2） | 前置知识 | Python基础 |
| AI Agent（2） | 前置知识 | OpenAI兼容接口 |
| AI Agent（2） | 相关知识 | Function Calling |
| AI Agent（2） | 相关知识 | LangChain |
| AI Agent（2） | 相关知识 | LangGraph |
| AI Agent（2） | 相关知识 | Dify |
| AI Agent（2） | 相关知识 | Coze |
| AI Agent（2） | 相关知识 | n8n |
| AI Agent（2） | 相关知识 | [[AI Agent总结]] |
| AI Agent开发框架 | 相关知识 | LangChain |
| AI Agent开发框架 | 相关知识 | LangGraph |
| AI Agent开发框架 | 相关知识 | AutoGen |
| AI Agent开发框架 | 相关知识 | CrewAI |
| AI Agent低代码平台 | 相关知识 | Dify |
| AI Agent低代码平台 | 相关知识 | Coze |
| AI Agent低代码平台 | 相关知识 | FastGPT |
| AI Agent低代码平台 | 相关知识 | n8n |
| AI Agent低代码平台 | 相关知识 | RagFlow |
| Function Calling | 属于技能 | [[AI Agent相关/AI Agent]] |
| Function Calling | 相关知识 | 工具调用 |
| Function Calling | 相关知识 | tools参数 |
| Function Calling | 相关知识 | JSON Schema |
| Function Calling | 相关知识 | tool_calls |
| Function Calling | 有示例代码 | func/fc_flow.py |
| 动态SQL生成与数据库查询 | 有示例代码 | func/db_init.py |
| 动态SQL生成与数据库查询 | 有示例代码 | func/dynamic_sql.py |
| 12306实时票务接口对接 | 有示例代码 | func/Ticketing_12306.py |
| AI Agent（2） | 有示例代码 | agent_base.zip |
| AI Agent（2） | 有示例代码 | agent_base_for_LC1.0.zip |
| AI Agent（2） | 被考察于 | Function Calling的完整调用流程是什么 |
| AI Agent（2） | 被考察于 | 为什么普通LLM需要外部工具调用 |
| AI Agent（2） | 被考察于 | Function Calling中函数名必须和本地函数名一致吗 |
| AI Agent（2） | 被考察于 | 如何选择AI Agent开发框架和低代码平台 |
| AI Agent（2） | 应用于 | 自然语言查询数据库项目 |
| AI Agent（2） | 应用于 | 实时票务查询项目 |
| AI Agent（2） | 应用于 | 业务自动化助手项目 |

相关：[[AI Agent（1）]] [[AI Agent总结]] Function Calling LangChain LangGraph Dify Coze
