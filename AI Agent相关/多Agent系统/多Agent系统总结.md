## 总览

本总结用于汇总《多Agent系统》这份 PPT 的分段笔记。当前已完成整份 PPT：

- [[多Agent系统（1）]]：第 1-18 页，MAS 概念、失败模式和框架对比。
- [[多Agent系统（2）]]：第 19-39 页，AutoGen、AutoGen Studio、AgentChat、短视频项目和协同代码生成。
- [[多Agent系统（3）]]：第 40-51 页，CrewAI、安装部署和 Job Posting 项目。

这份 PPT 的主线是：先理解多 Agent 为什么需要角色分工、上下文交接和验证机制，再分别看 AutoGen 与 CrewAI 两种不同工程路线。

## 已覆盖内容

| 笔记 | PPT 范围 | 主题 |
| --- | --- | --- |
| [[多Agent系统（1）]] | 第 1-18 页 | MAS 定义、AI 小镇、MAST 失败分类、改进策略、框架对比、AutoGen Studio 开场 |
| [[多Agent系统（2）]] | 第 19-39 页 | AutoGen Studio、AgentChat、短视频自动生成、多智能体协同代码生成 |
| [[多Agent系统（3）]] | 第 40-51 页 | CrewAI 基础、安装部署、Job Posting 项目 |

## 核心结论

1. MAS 是多个自主 Agent 在共享环境中协作，不是简单复制多个 LLM 调用。
2. 多 Agent 适合市场研究、软件开发、智能营销、供应链、智能电网等天然需要分工的任务。
3. MAST 把常见失败归为规格问题、智能体间不对齐、任务验证问题。
4. 上下文工程要处理保存、选择、压缩、隔离四件事。
5. 框架选型不能只看评分，要看任务是对话协作、结构化流水线还是可控状态流。
6. AutoGen 更偏动态对话、多角色协作、人类参与和代码执行。
7. CrewAI 更偏结构化团队、任务链和顺序流程。
8. 示例代码已经集中保存到 `代码` 文件夹，复习时优先看入口文件和配置文件。

## 关键图

- ![[Generative Agents架构图.png]]
- ![[MAST失败分类图.png]]
- ![[多智能体框架对比图.png]]
- ![[AutoGen技术架构图.png]]
- ![[AutoGen短视频角色职责流程图.png]]
- ![[CrewAI与AutoGen对比选择图.png]]

## 代码索引

| 目录 | 内容 |
| --- | --- |
| `代码/AutoGen_Studio/` | AutoGen Studio 安装、启动、模型能力配置和角色选择 Prompt |
| `代码/autogen_generate_video/` | 短视频自动生成系统，包含 `短视频生成主程序.py`、`工具函数.py`、学习示例和依赖 |
| `代码/autogen_code/` | 多 Agent 协同代码生成、股价分析、可视化和数据分析示例 |
| `代码/job-posting-v2/` | CrewAI Job Posting 项目，包含 Agent/Task 配置和 Crew 入口 |
| `代码/CrewAI/install_crewai.ps1` | CrewAI 和 uv 安装命令 |

## 补充资料

- 面试题：[飞书 Wiki](https://my.feishu.cn/wiki/Nj0dwEj64iB4NtkBGxUcR9IOnKh)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| 多Agent系统总结 | 属于技能 | [[AI Agent相关/AI Agent]] |
| 多Agent系统总结 | 相关知识 | [[多Agent系统（1）]] |
| 多Agent系统总结 | 相关知识 | [[多Agent系统（2）]] |
| 多Agent系统总结 | 相关知识 | [[多Agent系统（3）]] |
| 多Agent系统总结 | 相关知识 | MAS |
| 多Agent系统总结 | 相关知识 | MAST |
| 多Agent系统总结 | 相关知识 | Generative Agents |
| 多Agent系统总结 | 相关知识 | AutoGen |
| 多Agent系统总结 | 相关知识 | AutoGen Studio |
| 多Agent系统总结 | 相关知识 | AgentChat |
| 多Agent系统总结 | 相关知识 | CodeExecutorAgent |
| 多Agent系统总结 | 相关知识 | CrewAI |
| 多Agent系统总结 | 相关知识 | LangGraph |
| 多Agent系统总结 | 有示例代码 | 代码/AutoGen_Studio/autogen_studio_start.ps1 |
| 多Agent系统总结 | 有示例代码 | 代码/autogen_generate_video/短视频生成主程序.py |
| 多Agent系统总结 | 有示例代码 | 代码/autogen_generate_video/工具函数.py |
| 多Agent系统总结 | 有示例代码 | 代码/autogen_code/数据可视化示例.py |
| 多Agent系统总结 | 有示例代码 | 代码/job-posting-v2/src/job_posting/crew.py |
| 多Agent系统总结 | 被考察于 | 多 Agent 系统为什么需要上下文工程 |
| 多Agent系统总结 | 被考察于 | AutoGen 和 CrewAI 如何选型 |
| 多Agent系统总结 | 应用于 | 复杂任务自动化协作 |
| 多Agent系统总结 | 应用于 | 短视频自动生成 |
| 多Agent系统总结 | 应用于 | 招聘信息自动生成 |
