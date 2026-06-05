## 背景介绍

本节对应 PPT 第 40-53 页，是《AI Agent全景》的收尾部分。前一节 [[AI Agent（2）]] 已经讲到 Function Calling 和具体工具调用，本节继续往上抽象，重点看 Agent 在任务执行时常见的认知策略，以及一个垂直应用项目如何把工具、记忆、RAG、Web 服务和部署组合起来。

PPT 中部分页面写作 `React`，这里按 Agent 领域常用写法统一记为 `ReAct`。它不是前端框架 React，而是 Reasoning + Acting 的 Agent 决策模式。

## Agent策略框架总览

第 40-46 页集中介绍了四种 Agent 思考/执行框架：

| 框架 | 核心思路 | 更适合的场景 | 主要注意点 |
| --- | --- | --- | --- |
| ReAct | 推理和行动交替进行，在观察结果后继续思考 | 需要边查边算、边执行边修正的动态任务 | 要有可用工具、清晰的输出格式和停止条件 |
| Plan-and-Execute | 先制定整体计划，再按计划执行 | 复杂项目管理、多步骤决策、任务链较长的场景 | 初始计划可能偏离现实，需要执行中校正 |
| Self-Ask | 让模型先提出追问，再逐步回答追问 | 多跳问答、需要拆解隐含问题的场景 | 对提示词格式要求较高，容易受解析规则影响 |
| Thinking and Self-Reflection | 先批判当前输出，再修正策略或答案 | 复杂决策、质量要求高、需要反复改进的场景 | 需要评价标准，否则容易变成空转反思 |

这几种方法都围绕同一个核心问题：让 Agent 不只是“一次性生成答案”，而是在任务过程中持续观察、拆解、执行、校验和修正。

## ReAct实时决策

![[ReAct观察思考行动循环图.png]]

ReAct 是 Reasoning 和 Acting 的组合。它的关键不是把推理和行动分开，而是让二者形成循环：

```text
Thought -> Action -> Observation -> Thought -> ...
```

模型先思考下一步该做什么，再选择工具执行动作，然后读取工具返回的观察结果，并继续决定下一步。这样可以处理动态和不确定环境中的问题。

课程中的典型示例是玫瑰花进货价与加价计算：

1. 先用搜索工具查询当前市场价格。
2. 再用计算器工具做 5% 加价。
3. 最后把搜索和计算结果组织成自然语言回答。

对应代码线索：

- `cognitive/create-act-agent_for_lcV0.3.py`
- `cognitive/create-react-agent_for_lcV1.py`

代码中可以看到两个重点：

- LangChain V0.3 写法里，`Thought`、`Action`、`Action Input`、`Observation`、`Final Answer` 这类英文格式很关键，解析器会依赖这些字段。
- LangChain V1.0 的 `create_agent` 建立在 LangGraph 引擎之上，底层仍然符合 ReAct 的循环思路，但不像旧版本那样必须在提示词中显式写出完整格式。

## Plan-and-Execute策略蓝图

![[Plan-and-Execute规划执行流程图.png]]

Plan-and-Execute 的思路是先规划，再执行。它适合任务比较复杂、步骤较多、需要先全局考虑再逐步推进的场景。

可以把它理解成两层角色：

- Planner：负责把用户目标拆成计划。
- Executor：负责按计划调用工具并完成每一步。

对应代码线索：

- `cognitive/plan-and-execute_for_lcV0.3.py`
- `cognitive/plan-and-execute_for_lcV1.py`
- `cognitive/plan_and_execute_agent_for_lcV1.py`

示例中使用的工具包括 Search 和 Calculator，用于回答类似“100 元人民币能买几束玫瑰花”这种需要先查价格、再做计算的问题。

和 ReAct 相比，Plan-and-Execute 更强调前置规划；ReAct 更强调每一步执行后根据观察结果立刻修正。真实项目中二者不冲突，复杂任务可以先有计划，再在每一步执行中使用 ReAct 式反馈循环。

## Self-Ask回路验证

![[Self-Ask自问自答流程图.png]]

Self-Ask 的核心是让模型先判断“是否需要追问”，如果需要，就把原问题拆成若干追问，并逐个回答中间问题，最后再得到最终答案。

它适合多跳问题，例如：

```text
问题：A 和 B 的导演是否来自同一个国家？
追问 1：A 的导演是谁？
追问 2：这个导演来自哪里？
追问 3：B 的导演是谁？
追问 4：这个导演来自哪里？
最终回答：比较两个国家是否一致。
```

对应代码线索：

- `cognitive/self-ask_for_lcV0.3.py`
- `cognitive/self-ask_for_lcV1.py`

代码里有一个很重要的实践点：Self-Ask 对输出格式要求很严格。示例中要求模型使用英文格式，例如 `Follow up:`、`Intermediate answer:`、`So the final answer is:`。如果改成中文格式，LangChain 的解析逻辑可能无法识别。

因此 Self-Ask 不只是“让模型自己问自己”，更重要的是把追问链条结构化，让中间答案可以被程序追踪和校验。

## Thinking and Self-Reflection偏差修正

![[Thinking自我反思修正流程图.png]]

Thinking and Self-Reflection 也可以理解为 Critique-Revise：先批判，再修正。

基本过程是：

1. 系统生成当前决策或答案。
2. 批判模块评估当前结果，找出问题、缺陷或与目标不一致的地方。
3. 修正模块根据批判结果调整策略或答案。
4. 必要时继续迭代，直到达到质量要求或触发停止条件。

它和 ReAct 相似，都有“观察结果后调整下一步”的味道；区别在于 ReAct 更关注工具行动循环，Self-Reflection 更关注质量评估和偏差修正。

真实项目中使用这类框架时，要先明确评价标准。例如答案是否覆盖需求、是否事实一致、是否格式正确、是否调用了正确工具。如果没有评价标准，反思很容易变成形式化的重复。

## 垂直应用：命理机器人项目

第 47-53 页进入垂直应用案例：`agent_numerology_v2` 命理机器人项目。

![[命理机器人Agent工作流程图.png]]

这个项目不是单纯聊天机器人，而是一个把 Agent、RAG、本地知识库、第三方接口、Redis 记忆和 Web 服务组合起来的工程实践。

### 项目结构

主要代码线索：

- `agent_numerology_v2.zip`
- `agent_numerology_v2_for_LC1.0.zip`
- `README.md`
- `server.py`
- `mytools.py`
- `models.py`
- `docker-compose.yml`
- `local_qdrand/`
- `templates/index.html`
- `static/`

`README.md` 中说明，该项目默认本地服务地址是：

- 前端页面：`http://127.0.0.1:8000/index`
- API 文档：`http://127.0.0.1:8000/docs`

如果使用 Docker Compose，项目服务会映射到宿主机 `8001`，Redis 容器内部使用 `6379`，宿主机映射端口是 `6380`。

### 核心能力

从 `server.py` 和 `mytools.py` 看，命理机器人包含这些关键模块：

- FastAPI：提供 Web 页面和 `/chat`、`/add_urls` 等接口。
- LangChain Agent：使用 `create_tool_calling_agent` 构建工具调用型 Agent。
- Redis：保存不同用户 session 的短期会话历史。
- Qdrant：保存本地知识库向量数据。
- WebBaseLoader + RecursiveCharacterTextSplitter：把 URL 文档加载并切分进本地知识库。
- 外部 API：对接缘分居接口，提供八字测算、每日一卦、周公解梦等工具。
- 搜索工具：用于 Agent 遇到未知信息时做外部检索。
- 情绪识别链：先判断用户情绪，再切换不同回复风格。

这正好对应前面学到的 Agent 构成：

```text
LLM -> 负责理解和生成
工具 -> 搜索、知识库、八字测算、摇一卦、解梦
记忆 -> Redis 会话历史
知识库 -> Qdrant 本地向量库
执行 -> FastAPI 接口触发 AgentExecutor
部署 -> Docker / docker-compose
```

### 部署和依赖

PPT 中给出的 Redis 本机安装命令：

```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

项目 Docker Compose 部署命令：

```bash
docker-compose -p zhipo-numerology up --build
```

外部接口文档地址：

```text
https://doc.yuanfenju.com/overview/index.html
```

需要注意，真实项目中 API Key 应放在 `.env` 或系统环境变量中，例如 `DASHSCOPE_API_KEY`、`YUANFENJU_API_KEY`，不要硬编码在源码里。课程代码中有教学示例痕迹，部署或展示作品前应先清理密钥、补充错误处理和权限控制。

## 小结

第 40-53 页的主线可以概括为：

```text
Agent认知策略 -> Agent工程项目 -> 部署与外部系统集成
```

ReAct、Plan-and-Execute、Self-Ask、Self-Reflection 解决的是 Agent 如何思考、拆解、行动和修正的问题；命理机器人项目则展示了这些思想落到工程里时，需要补上 Web 服务、会话管理、知识库、第三方接口、容器部署和密钥管理。

复习时可以抓住三组对比：

- ReAct vs Plan-and-Execute：一个重视即时观察和行动循环，一个重视先规划再执行。
- Self-Ask vs Self-Reflection：一个重视追问拆解，一个重视批判和修正。
- Demo Agent vs 工程 Agent：前者通常只需要模型和工具，后者还需要记忆、知识库、服务接口、部署、日志和安全边界。

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| AI Agent（3） | 属于技能 | [[AI Agent相关/AI Agent]] |
| AI Agent（3） | 前置知识 | [[AI Agent（1）]] |
| AI Agent（3） | 前置知识 | [[AI Agent（2）]] |
| AI Agent（3） | 相关知识 | ReAct |
| AI Agent（3） | 相关知识 | Plan-and-Execute |
| AI Agent（3） | 相关知识 | Self-Ask |
| AI Agent（3） | 相关知识 | Thinking and Self-Reflection |
| AI Agent（3） | 相关知识 | [[AI Agent总结]] |
| ReAct | 相关知识 | 工具调用 |
| ReAct | 相关知识 | Observation-Thought-Action循环 |
| Plan-and-Execute | 相关知识 | 任务拆解 |
| Plan-and-Execute | 相关知识 | Planner |
| Plan-and-Execute | 相关知识 | Executor |
| Self-Ask | 相关知识 | 多跳问答 |
| Self-Ask | 相关知识 | Follow up |
| Thinking and Self-Reflection | 相关知识 | Critique-Revise |
| Thinking and Self-Reflection | 相关知识 | 偏差修正 |
| AI Agent（3） | 有示例代码 | cognitive/create-act-agent_for_lcV0.3.py |
| AI Agent（3） | 有示例代码 | cognitive/create-react-agent_for_lcV1.py |
| AI Agent（3） | 有示例代码 | cognitive/plan-and-execute_for_lcV0.3.py |
| AI Agent（3） | 有示例代码 | cognitive/self-ask_for_lcV0.3.py |
| AI Agent（3） | 有示例代码 | agent_numerology_v2_for_LC1.0/server.py |
| 命理机器人项目 | 有示例代码 | agent_numerology_v2_for_LC1.0/mytools.py |
| 命理机器人项目 | 应用于 | 垂直领域智能问答 |
| 命理机器人项目 | 相关知识 | Redis会话记忆 |
| 命理机器人项目 | 相关知识 | Qdrant本地知识库 |
| 命理机器人项目 | 相关知识 | FastAPI |
| 命理机器人项目 | 相关知识 | Docker部署 |
| AI Agent（3） | 被考察于 | ReAct和Plan-and-Execute有什么区别 |
| AI Agent（3） | 被考察于 | Self-Ask如何拆解多跳问题 |
| AI Agent（3） | 被考察于 | Self-Reflection如何做偏差修正 |
| AI Agent（3） | 被考察于 | 命理机器人项目如何体现Agent的工具和记忆 |
| AI Agent（3） | 应用于 | 命理机器人项目 |

相关：[[AI Agent（1）]] [[AI Agent（2）]] [[AI Agent总结]] ReAct Plan-and-Execute Self-Ask Redis Qdrant FastAPI
