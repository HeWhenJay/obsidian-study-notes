## 总览

本总结用于汇总《AI Agent全景》整套 PPT 的核心内容。后续继续整理新的页码时，不再为每一段单独新建总结文件，而是在本文件中持续追加和更新总览、图表和复习重点。

当前已整理范围：

- [[AI Agent（1）]]：AI Agent 核心定义、四大要素、规划、记忆、工具和执行。
- [[AI Agent（2）]]：AI Agent 开发框架、低代码平台、Function Calling 机制和两个实践项目。
- [[AI Agent（3）]]：ReAct、Plan-and-Execute、Self-Ask、自我反思，以及命理机器人垂直项目实践。

## AI Agent核心认知

AI Agent 可以理解为“大模型应用从问答走向行动”的形态。普通 LLM 主要负责理解、推理和生成；AI Agent 则在 LLM 基础上加入记忆、工具、规划和执行能力，使系统能够围绕目标完成任务。

核心公式：

```text
AI Agent = LLM + 记忆 + 工具 + 规划 + 执行
```

### 四大要素

- 规划：观察任务、拆解步骤、选择工具、反思修正并判断何时结束。
- 记忆：包括模型参数中的知识、当前上下文和外部记忆库。
- 工具：搜索、计算器、代码解释器、日历、数据库、业务 API 等。
- 执行：把计划转化为具体动作，并根据结果继续下一步。

完整 Agent 往往形成循环：

```text
用户目标 -> 规划 -> 工具调用/执行 -> 观察结果 -> 反思修正 -> 继续执行或结束
```

## 框架选型图

![[AI Agent开发框架对比图.png]]

### 选型要点

- LangChain V0.3：适合从单智能体入门，理解链、工具、记忆、代理等基础模块。
- LangChain V1.0：更偏预构建 Agent 架构，建立在 LangGraph 之上。
- LangGraph：适合复杂状态流、分支、循环、多步骤任务和多智能体编排。
- Semantic Kernel：适合微软生态，尤其是 Azure、.NET/C#、Teams、Office。
- AutoGen：适合多角色 Agent 自主对话协作。
- CrewAI：适合以角色、任务、流程为核心的多智能体协作。

## 低代码平台选型图

![[AI Agent低代码平台对比图.png]]

### 选型要点

- Coze：非技术人员友好，适合快速原型，但平台依赖较强。
- Dify：易用性、私有化部署、插件和多模型调度相对均衡。
- FastGPT：偏技术用户，适合知识库问答和本地 API 集成。
- n8n：更像通用流程自动化工具，适合 API 串联和工作流编排。
- RagFlow：偏 RAG 文档解析和知识库问答，通用 Agent 能力相对不是重点。

## Function Calling核心流程图

![[Function Calling核心流程说明.png]]

Function Calling 的核心是：模型负责判断函数名和参数，应用程序负责真正执行函数。模型本身并不直接运行 Python 函数。

```text
用户提问 + 函数说明
-> 模型判断函数名和参数
-> 应用程序执行函数
-> 函数结果回传给模型
-> 模型生成最终回答
```

## Function Calling实现过程图

![[Function Calling实现过程图解.png]]

实现时要抓住三个关键点：

- 先写真实可执行函数。
- 再用 JSON Schema 描述函数名称、用途和参数。
- 最后用 `tools` 参数把函数说明交给模型，并处理模型返回的 `tool_calls`。

## 实践项目图

### 动态SQL生成与数据库查询

![[动态SQL生成与数据库查询项目说明.png]]

这个项目的本质是：用户中文问题 -> 模型生成 SQL -> 程序执行 SQL -> 模型解释数据库结果。

相关代码：

- `func/db_init.py`
- `func/dynamic_sql.py`

### 12306实时票务接口对接

![[12306实时票务接口对接流程图.png]]

这个项目的本质是：用户自然语言查询 -> 模型选择查票函数 -> 程序请求 12306 接口 -> 模型基于实时结果回答。

相关代码：

- `func/Ticketing_12306.py`

## Agent认知策略

PPT 第 40-46 页把 Agent 的“怎么想、怎么做、怎么修正”归纳成四类策略。

### ReAct

![[ReAct观察思考行动循环图.png]]

ReAct = Reasoning + Acting，核心是让模型在推理和行动之间循环：

```text
Thought -> Action -> Observation -> Thought -> ...
```

它适合需要实时搜索、计算、读取外部结果并继续调整下一步的任务。课程代码对应 `cognitive/create-act-agent_for_lcV0.3.py` 和 `cognitive/create-react-agent_for_lcV1.py`。

### Plan-and-Execute

![[Plan-and-Execute规划执行流程图.png]]

Plan-and-Execute 先由 Planner 制定计划，再由 Executor 按步骤调用工具执行。它适合多步骤、需要前置蓝图的任务，但执行过程中仍需要根据现实结果调整计划。

### Self-Ask

![[Self-Ask自问自答流程图.png]]

Self-Ask 让模型把复杂问题拆成追问链，再用中间答案推导最终答案。它适合多跳问答，但对提示词输出格式要求很高，课程代码中要求使用 `Follow up:`、`Intermediate answer:` 等英文格式。

### Thinking and Self-Reflection

![[Thinking自我反思修正流程图.png]]

Thinking and Self-Reflection 也可以理解为 Critique-Revise：先批判当前结果，再修正策略或答案。它更关注质量评估和偏差修正，适合复杂决策和高质量输出场景。

## 命理机器人垂直项目实践

![[命理机器人Agent工作流程图.png]]

命理机器人项目 `agent_numerology_v2` 展示了一个工程化 Agent 应用如何组合多种能力：

- FastAPI：提供 Web 页面和接口。
- LangChain Agent：通过 `create_tool_calling_agent` 组织工具调用。
- Redis：保存不同用户的会话历史。
- Qdrant：保存本地知识库向量数据。
- 第三方接口：对接缘分居 API，提供八字测算、每日一卦、周公解梦等工具。
- 搜索工具：在本地知识库或专业接口不足时补充外部检索。
- Docker / docker-compose：完成服务和 Redis 的容器化部署。

本地启动方式：

```bash
python server.py
```

Docker Compose 部署方式：

```bash
docker-compose -p zhipo-numerology up --build
```

复习这个项目时，不要只看“命理”这个垂直场景，而要看它怎样体现 Agent 工程闭环：用户请求进入 Web 服务，系统读取会话记忆，Agent 判断需要调用什么工具，工具可能访问本地知识库、搜索接口或第三方业务接口，最后再把工具结果组织成面向用户的回答。

## 复习重点

- AI Agent 的核心价值是把 LLM 从“回答问题”扩展到“完成任务”。
- 普通 LLM 的限制是知识过期、不能直接访问实时数据、不能直接操作外部系统。
- Function Calling 让模型具备“选择外部函数并生成参数”的能力。
- 真正执行函数的是应用程序，不是模型。
- 多轮工具调用中，应用程序要循环处理 `tool_calls`，直到模型不再请求工具。
- 动态 SQL 项目要重点关注 SQL 安全，不能无约束执行模型生成的 SQL。
- 12306 项目要重点关注接口稳定性、合规性、请求头/Cookie 变化和错误处理。
- ReAct 适合观察、思考、行动不断循环的动态任务。
- Plan-and-Execute 适合先规划再执行的复杂多步骤任务。
- Self-Ask 适合多跳问答，但要注意输出格式约束。
- Self-Reflection 适合偏差修正，但必须有评价标准和停止条件。
- 工程化 Agent 项目还要关注 Redis 会话记忆、Qdrant 知识库、第三方 API、Docker 部署和密钥管理。

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| AI Agent总结 | 属于技能 | [[AI Agent相关/AI Agent]] |
| AI Agent总结 | 相关知识 | [[AI Agent（1）]] |
| AI Agent总结 | 相关知识 | [[AI Agent（2）]] |
| AI Agent总结 | 相关知识 | [[AI Agent（3）]] |
| AI Agent总结 | 相关知识 | Function Calling |
| AI Agent总结 | 相关知识 | AI Agent开发框架 |
| AI Agent总结 | 相关知识 | AI Agent低代码平台 |
| AI Agent总结 | 相关知识 | ReAct |
| AI Agent总结 | 相关知识 | Plan-and-Execute |
| AI Agent总结 | 相关知识 | Self-Ask |
| AI Agent总结 | 相关知识 | Thinking and Self-Reflection |
| AI Agent总结 | 有示例代码 | The First Agent.py |
| AI Agent总结 | 有示例代码 | AIAgentWithMemory.py |
| AI Agent总结 | 有示例代码 | func/fc_flow.py |
| AI Agent总结 | 有示例代码 | func/dynamic_sql.py |
| AI Agent总结 | 有示例代码 | func/Ticketing_12306.py |
| AI Agent总结 | 有示例代码 | cognitive/create-act-agent_for_lcV0.3.py |
| AI Agent总结 | 有示例代码 | cognitive/plan-and-execute_for_lcV0.3.py |
| AI Agent总结 | 有示例代码 | cognitive/self-ask_for_lcV0.3.py |
| AI Agent总结 | 有示例代码 | agent_numerology_v2_for_LC1.0/server.py |
| AI Agent总结 | 被考察于 | AI Agent和普通LLM有什么区别 |
| AI Agent总结 | 被考察于 | Function Calling的完整调用流程是什么 |
| AI Agent总结 | 被考察于 | ReAct和Plan-and-Execute有什么区别 |
| AI Agent总结 | 被考察于 | Self-Ask如何拆解多跳问题 |
| AI Agent总结 | 被考察于 | 命理机器人项目如何体现Agent的工具和记忆 |
| AI Agent总结 | 应用于 | 自然语言查询数据库项目 |
| AI Agent总结 | 应用于 | 实时票务查询项目 |
| AI Agent总结 | 应用于 | 业务自动化助手项目 |
| AI Agent总结 | 应用于 | 命理机器人项目 |

相关：[[AI Agent（1）]] [[AI Agent（2）]] [[AI Agent（3）]] Function Calling LangChain LangGraph Dify ReAct Redis Qdrant
