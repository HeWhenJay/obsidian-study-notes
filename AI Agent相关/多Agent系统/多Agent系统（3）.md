## 背景介绍

本节对应 PPT《5、多Agent系统.pptx》第 40-51 页，主题是 CrewAI 的基础认知、安装部署和 Job Posting 项目。前一节 [[多Agent系统（2）]] 讲 AutoGen 更偏对话协作、灵活交互和代码执行；本节的 CrewAI 更像结构清晰的项目团队。

本节保存的示例代码位于：

```text
代码/job-posting-v2/
代码/CrewAI/install_crewai.ps1
```

## CrewAI 基础认知

PPT 第 42 页给出一个直观定义：CrewAI 可以理解为用于组建和管理“AI 项目团队”的框架。

![[CrewAI项目团队概念图.png]]

CrewAI 提供一套清晰组件：

| 组件      | 含义                    |
| ------- | --------------------- |
| Agent   | 团队成员，承担某个角色           |
| Task    | 具体任务，定义输入、产出和期望       |
| Crew    | 多个 Agent 和 Task 组成的团队 |
| Process | 任务执行流程，例如顺序执行         |
| Tools   | Agent 可以调用的外部工具       |

可以把它和 AutoGen 做一个直觉区分：

- AutoGen 更像一个动态讨论组或聊天室网络。
- CrewAI 更像一个结构化项目团队。

## CrewAI 和 AutoGen 对比

PPT 第 43 页给出对比选择：

![[CrewAI与AutoGen对比选择图.png]]

| 维度 | CrewAI | AutoGen |
| --- | --- | --- |
| 核心理念 | 协作、角色扮演、任务导向、流程化 | 对话驱动、灵活交互、模式化对话 |
| 架构风格 | `Agent -> Task -> Crew -> Process` | Agent 之间直接或间接通信，常见 GroupChat |
| 易用性 | 对结构化任务更简单，上手曲线更平缓 | 配置更灵活，但也可能更复杂 |
| 控制流 | 预定义顺序或分层流程 | 轮流、广播、人工输入等高度定制对话模式 |
| 典型用例 | 研究到报告、内容生成流水线、招聘信息生成 | 复杂模拟、辩论、协同编码、人类深度参与流程 |

选择建议：

- 如果要做结构清晰、按部就班完成任务的 AI 团队，CrewAI 更直观。
- 如果要模拟复杂对话、灵活交互或人类深度参与，AutoGen 更合适。

## 安装部署

PPT 第 44-45 页讲 CrewAI 安装。官方安装文档：

- [CrewAI Installation](https://docs.crewai.com/installation)

课程强调：CrewAI 使用 `uv` 作为依赖管理和包处理工具，所以需要先安装 `uv`。

命令已保存为：

```text
代码/CrewAI/install_crewai.ps1
```

安装 `uv`：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

![[CrewAI安装uv命令图.png]]

安装 CrewAI：

```powershell
uv tool install crewai -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

![[CrewAI安装命令图.png]]

注意点：

- 课程提到安装过程可能需要科学上网。
- `uv tool install crewai` 会下载较多依赖，需要等待。
- 如果使用课程提供的项目和虚拟环境，不必重复从零下载所有依赖。

## Job Posting 项目

第 46-51 页通过官方项目讲 CrewAI。

项目名：

```text
job-posting-v2
```

项目代码已保存到：

```text
代码/job-posting-v2/
```

![[CrewAI Job Posting项目介绍图.png]]

项目目标：用 CrewAI 自动创建招聘信息。CrewAI 协调多个自主 Agent，让它们围绕职位发布任务协同工作。

核心文件：

| 文件 | 作用 |
| --- | --- |
| `代码/job-posting-v2/src/job_posting/main.py` | 准备输入参数并启动 Crew |
| `代码/job-posting-v2/src/job_posting/crew.py` | 定义 Agent、Task、Crew 和执行流程 |
| `代码/job-posting-v2/src/job_posting/config/agents.yaml` | 定义研究员、撰写者、审阅者等角色 |
| `代码/job-posting-v2/src/job_posting/config/tasks.yaml` | 定义公司文化研究、职位要求研究、草稿撰写、审阅等任务 |
| `代码/job-posting-v2/src/job_posting/job_description_example.md` | 招聘描述示例 |
| `代码/job-posting-v2/job.md` | 示例输出结果 |

## 项目角色和任务

`agents.yaml` 中定义了三个核心 Agent：

| Agent | 角色 | 作用 |
| --- | --- | --- |
| `research_agent` | 研究分析师 | 分析公司网站、公司文化、价值观和职位需求 |
| `writer_agent` | 职位描述撰写者 | 根据研究结果撰写详细、有吸引力的招聘信息 |
| `review_agent` | 审阅和编辑专家 | 检查清晰度、吸引力、语法和公司价值观一致性 |

`tasks.yaml` 中定义了任务链：

1. `research_company_culture_task`：分析公司文化、价值观和使命。
2. `industry_analysis_task`：分析行业趋势、挑战和机会。
3. `research_role_requirements_task`：提取候选人所需技能、经验和素质。
4. `draft_job_posting_task`：撰写招聘启事。
5. `review_and_edit_job_posting_task`：审查并润色最终内容。

`crew.py` 中的关键代码是：

```text
Crew(
    agents=self.agents,
    tasks=self.tasks,
    process=Process.sequential,
    verbose=True
)
```

这说明项目是顺序流程：先研究，再写作，再审阅。

## PyCharm 配置和运行

PPT 第 47-49 页说明 PyCharm 2024 和 2025 版本的解释器配置。

PyCharm 2024 初次打开项目：

![[CrewAI PyCharm2024初次配置图.png]]

选择已有解释器：

![[CrewAI PyCharm2024解释器选择图.png]]

PyCharm 2025 配置界面略有不同：

![[CrewAI PyCharm2025解释器配置图.png]]

课程建议：项目中已经具备相关虚拟环境，配置解释器时进入项目的 `.venv` 文件夹选择即可。

运行命令：

```powershell
crewai run
```

![[CrewAI运行命令图.png]]

运行结果：

![[CrewAI运行结果图.png]]

PPT 提醒：期间可能出现与互联网搜索有关的失败信息，智能体会自动重试。复习时要把这点和 [[多Agent系统（1）]] 中的“验证机制”和“失败重试”联系起来。

## 小结

CrewAI 的学习重点是结构化协作：

- 用 `agents.yaml` 定义角色。
- 用 `tasks.yaml` 定义任务。
- 用 `crew.py` 把角色和任务组装成 Crew。
- 用 `Process.sequential` 等流程控制执行顺序。

它比 AutoGen 更像传统项目管理：角色、任务和流程边界都比较明确。因此 CrewAI 特别适合招聘信息生成、研究报告、内容流水线、运营分析等“步骤清楚、产出明确”的场景。

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| 多Agent系统（3） | 属于技能 | [[AI Agent相关/AI Agent]] |
| 多Agent系统（3） | 前置知识 | [[多Agent系统（1）]] |
| 多Agent系统（3） | 前置知识 | [[多Agent系统（2）]] |
| 多Agent系统（3） | 相关知识 | CrewAI |
| 多Agent系统（3） | 相关知识 | AutoGen |
| 多Agent系统（3） | 相关知识 | Agent |
| 多Agent系统（3） | 相关知识 | Task |
| 多Agent系统（3） | 相关知识 | Crew |
| 多Agent系统（3） | 相关知识 | Process |
| 多Agent系统（3） | 相关知识 | Tools |
| CrewAI安装部署 | 有示例代码 | 代码/CrewAI/install_crewai.ps1 |
| Job Posting项目 | 有示例代码 | 代码/job-posting-v2/src/job_posting/main.py |
| Job Posting项目 | 有示例代码 | 代码/job-posting-v2/src/job_posting/crew.py |
| Job Posting项目 | 有示例代码 | 代码/job-posting-v2/src/job_posting/config/agents.yaml |
| Job Posting项目 | 有示例代码 | 代码/job-posting-v2/src/job_posting/config/tasks.yaml |
| Job Posting项目 | 有示例代码 | 代码/job-posting-v2/job.md |
| Job Posting项目 | 应用于 | 招聘信息自动生成 |
| 多Agent系统（3） | 被考察于 | CrewAI 和 AutoGen 的核心区别是什么 |
| 多Agent系统（3） | 被考察于 | CrewAI 中 Agent、Task、Crew、Process 分别是什么 |
| 多Agent系统（3） | 被考察于 | Job Posting 项目的任务链如何组织 |
