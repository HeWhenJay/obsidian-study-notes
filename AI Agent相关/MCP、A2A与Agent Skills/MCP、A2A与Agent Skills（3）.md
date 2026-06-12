## 背景介绍

本节对应 PPT《MCP & A2A & Agent Skills》第 18-26 页，主题是 Agent Skills 的定位、标准结构、工作原理、安全考量，以及课程配套代码中的 LangGraph/DeepAgents Skill 示例。

PPT 把 Agent Skills 描述为继 MCP 之后的另一个重要标准。复习时不要只把它理解成“一段更长的提示词”，而要理解成“可携带的工程化能力包”：它可以包含 `SKILL.md`、脚本、参考资料、模板和资源，让 Agent 在需要时加载一套稳定流程。

本节保存的示例代码位于当前目录下的 `代码` 文件夹，主要包括：

- `代码/agent_skills/`
- `代码/agent_skills/main_win.py`
- `代码/agent_skills/skills/arxiv-search/`
- `代码/agent_skills/skills/langgraph-docs/`
- `代码/demo/.codebuddy/skills/competitor-analysis/`

原始 `.env` 没有复制，只保留 `代码/agent_skills/.env.example`。

## 什么是 Agent Skills

Agent Skills 是一种轻量、开放的能力扩展格式。官方定义的最小结构是：一个目录里至少包含一个 `SKILL.md` 文件；`SKILL.md` 至少包含 `name` 和 `description` 元数据，再加上正文说明。技能目录还可以包含脚本、参考资料、模板和其他资源。

最小心智模型：

```text
Skill = 触发描述 + 操作说明 + 可选脚本 + 可选参考资料 + 可选模板资源
```

它解决的不是“模型有没有工具”，而是“模型在某类任务上是否知道该按什么流程、读哪些资料、运行哪些脚本、产生什么格式的结果”。

## MCP 与 Skills 的联系

![[MCP与Skills连接方式对比图.png]]

PPT 第 21 页把两者放在同一张图里：MCP 更像传输层，回答 “How to Connect”；Agent Skills 更像应用层，回答 “How to Use”。

| 维度 | MCP | Agent Skills |
| --- | --- | --- |
| 核心问题 | AI 应用如何连接工具和数据源 | Agent 如何掌握某类可复用流程 |
| 主要对象 | Server 暴露的 tools/resources/prompts | 本地或项目内的 `SKILL.md`、scripts、references、assets |
| 加载方式 | Host 连接 Server 后发现能力 | 先发现 name/description，任务匹配后再加载完整说明 |
| 工程风险 | 工具权限、远程鉴权、沙箱逃逸、工具名冲突 | Prompt Injection、恶意脚本、过宽工具权限、技能供应链污染 |
| 典型用途 | 查数据、调接口、操作外部系统 | 竞品分析、PPT 转笔记、创建 MCP Server、文档生成 |

一句话：MCP 给 Agent 接上外部世界，Skills 给 Agent 装上可迁移的工作方法。

## 为什么需要 Agent Skills

![[Agent Skills解决三类痛点图.png]]

PPT 第 22 页把 Agent 开发的痛点概括成三类：

| 痛点 | 旧方式 | Skill 思路 |
| --- | --- | --- |
| 上下文爆炸 | 每次把大量规则、文档、Token 塞进提示词 | 先暴露短描述，需要时再按目录加载完整资料 |
| 经验断层 | 复杂流程依赖个人 Prompt 或聊天历史 | 把流程、脚本、模板沉淀成可版本管理的技能包 |
| 平台锁定 | 能力绑定某个产品或某段系统提示 | 用开放目录结构和 `SKILL.md` 提高跨客户端复用性 |

Skills 的优势不在于“比 Prompt 神奇”，而在于把 Prompt 周边的脚本、模板、规则、边界条件和验证方式一起封装起来。

## 标准文件结构

![[Agent Skill标准文件结构图.png]]

标准结构可以这样记：

```text
skill-name/
├── SKILL.md        # 必需：元数据 + 工作说明
├── scripts/        # 可选：可执行脚本
├── references/     # 可选：参考资料、规范、评分维度
├── assets/         # 可选：模板、报告格式、静态资源
└── ...             # 可选：其他辅助文件
```

课程配套代码里有一个 `competitor-analysis` 示例，已保存为：

| 路径 | 作用 |
| --- | --- |
| `代码/demo/.codebuddy/skills/competitor-analysis/SKILL.md` | 竞品分析技能说明，包含使用场景、流程、资源和注意事项 |
| `代码/demo/.codebuddy/skills/competitor-analysis/scripts/竞品数据收集.py` | 交互式竞品数据收集脚本 |
| `代码/demo/.codebuddy/skills/competitor-analysis/references/竞品分析框架.md` | 产品、市场、商业、运营维度和 SWOT 框架 |
| `代码/demo/.codebuddy/skills/competitor-analysis/assets/分析报告模板.md` | 竞品分析报告模板 |

这说明 Skill 不是孤立说明书，而是能把“流程 + 数据结构 + 模板 + 脚本”打包到一起。

## SKILL.md 解析

![[SKILL.md结构解析图.png]]

`SKILL.md` 由 YAML frontmatter 和 Markdown 正文组成。

必需字段：

| 字段 | 作用 | 约束 |
| --- | --- | --- |
| `name` | 技能名 | 小写字母、数字、连字符；应与目录名一致 |
| `description` | 触发说明 | 要写清“做什么”和“何时用”，这是发现阶段的关键 |

常见可选字段：

| 字段 | 作用 |
| --- | --- |
| `license` | 技能许可说明 |
| `compatibility` | 环境要求，如需要网络、Python、Docker、特定客户端 |
| `metadata` | 自定义元数据 |
| `allowed-tools` | 预批准工具范围，仍属于实验性字段，是否生效取决于客户端实现 |

正文不强制格式，但高质量 Skill 通常会写：适用场景、工作流程、输入输出格式、脚本调用方式、边界条件、验证方法和安全注意事项。

## 渐进式加载原理

![[Agent Skills渐进式加载原理图.png]]

Skills 的核心机制是 Progressive Disclosure，即渐进式披露：

| 阶段 | Agent 看到什么 | 目的 |
| --- | --- | --- |
| Discovery | 只读取每个 Skill 的 `name` 和 `description` | 用很少上下文判断是否相关 |
| Activation | 任务匹配后读取完整 `SKILL.md` | 加载具体工作流程 |
| Execution | 按说明读取 references、assets 或执行 scripts | 完成任务并产出结果 |

这个机制可以降低上下文成本。Agent 平时不需要把所有技能全文放进上下文，只要在任务命中时加载相关技能。

## 课程代码：DeepAgents Skill 运行器

`代码/agent_skills/main_win.py` 是 Windows 环境下的 Skill 运行示例。核心结构：

| 模块 | 作用 |
| --- | --- |
| `deepagents.create_deep_agent` | 创建支持文件系统后端和 skills 的 Agent |
| `FilesystemBackend(root_dir=BASE_DIR)` | 把项目目录作为 Agent 可访问的文件系统根目录 |
| `MemorySaver()` | 用 LangGraph 内存检查点保存会话状态 |
| `ChatTongyi(model="qwen3-max")` | 使用通义千问模型 |
| `custom_execute` | 自定义本地命令执行工具，供 Skill 运行脚本 |
| Windows 路径 Monkey Patch | 课程为解决 DeepAgents 在 Windows 上的路径校验问题，覆盖 `_validate_path` |

执行逻辑是：

1. 从 `.env` 读取 `DASHSCOPE_API_KEY`。
2. 把 `skills/` 目录注册给 Agent。
3. 如果某个 Skill 要求运行脚本，Agent 可调用 `execute`。
4. 示例任务是搜索 `DeepSeek-R1` 最新论文。

这个示例的重点不是生产级安全，而是演示 Skill 如何触发、读说明、调用脚本并回收结果。

## 课程代码：arXiv 搜索 Skill

`代码/agent_skills/skills/arxiv-search/` 包含：

| 文件 | 作用 |
| --- | --- |
| `SKILL.md` | 说明何时使用 arXiv 搜索、如何调用脚本、输出格式和注意事项 |
| `arxiv_search.py` | 访问 arXiv API，按相关性返回论文标题、日期、链接和摘要 |

`SKILL.md` 中明确要求 Agent 不要委派任务，而是先读文件确认路径，再用 `execute` 工具运行脚本。这体现了 Skill 的一个关键能力：它不仅告诉模型“去搜索论文”，还规定了可审计的工具链顺序。

脚本本身包含几个工程细节：

- 使用 arXiv API：`http://export.arxiv.org/api/query`。
- 支持 `--max-papers` 参数。
- Windows 下强制 stdout 使用 UTF-8，避免中文乱码。
- 有 429 重试和 User-Agent 处理。
- 课程代码为了适配 Windows，关闭了 SSL 证书校验；真实生产环境不应默认这样做。

## 课程代码：LangGraph Docs Skill

`代码/agent_skills/skills/langgraph-docs/SKILL.md` 是更轻量的文档查询型 Skill。它要求：

1. 先读取 `https://docs.langchain.com/llms.txt` 文档索引。
2. 根据问题选择 2-4 个最相关文档。
3. 读取所选 URL。
4. 基于官方文档回答 LangGraph 问题。

这个 Skill 说明：不是所有 Skill 都需要脚本。有些 Skill 只需要规定“如何找权威资料、如何筛选资料、如何回答”。

## 安全考量

![[Agent Skills安全最佳实践图.png]]

Skills 的安全风险要按“它会影响 Agent 行为”来理解。恶意 Skill 不只是文本污染，还可能引导 Agent 读取敏感文件、执行脚本、泄露上下文或改变输出格式。

常见风险：

| 风险 | 表现 |
| --- | --- |
| Prompt Injection | `SKILL.md` 或 references 中夹带越权指令 |
| 恶意脚本 | scripts 中读取密钥、发网络请求、修改文件 |
| 权限过宽 | Skill 可以调用不必要的 Shell、网络、读写工具 |
| 供应链污染 | 第三方技能包来源不明，目录结构和脚本行为未经审查 |

最佳实践：

- 只从可信来源安装 Skills。
- 先审查 `SKILL.md`，再审查 `scripts/`。
- 不把真实 `.env`、API Key、Cookie、Token 放进技能包。
- 给 Skill 限定最小工具权限；`allowed-tools` 可作为元数据记录，但不能假设所有客户端都会强制执行。
- 执行脚本前确认路径、参数和输出位置。
- 对第三方 Skill 按“可执行代码”而不是“普通文档”对待。

## 小结

1. Agent Skills 是可移植的能力包，核心文件是 `SKILL.md`。
2. `description` 决定发现阶段是否会触发，写得过泛会误触发，写得过窄会漏触发。
3. Skills 通过渐进式加载降低上下文成本：先看短描述，命中后再读完整说明和资源。
4. MCP 负责连接外部工具，Skills 负责沉淀可复用流程，两者可以组合使用。
5. 课程代码展示了两类 Skill：脚本执行型 `arxiv-search` 和文档查询型 `langgraph-docs`。
6. 安全上要把 Skill 当作“可影响 Agent 行为的工程包”，不能当普通 Markdown 随意安装。

## 补充资料

- [Agent Skills 官方概览](https://agentskills.io/home)
- [Agent Skills 官方规范](https://agentskills.io/specification)
- [MCP 官方：Build with Agent Skills](https://modelcontextprotocol.io/docs/develop/build-with-agent-skills)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| MCP、A2A与Agent Skills（3） | 属于技能 | [[AI Agent相关/AI Agent]] |
| MCP、A2A与Agent Skills（3） | 前置知识 | [[MCP、A2A与Agent Skills（1）]] |
| MCP、A2A与Agent Skills（3） | 相关知识 | Agent Skills |
| MCP、A2A与Agent Skills（3） | 相关知识 | SKILL.md |
| MCP、A2A与Agent Skills（3） | 相关知识 | Progressive Disclosure |
| MCP、A2A与Agent Skills（3） | 相关知识 | scripts |
| MCP、A2A与Agent Skills（3） | 相关知识 | references |
| MCP、A2A与Agent Skills（3） | 相关知识 | assets |
| MCP、A2A与Agent Skills（3） | 相关知识 | [[MCP、A2A与Agent Skills总结]] |
| arXiv搜索Skill | 有示例代码 | 代码/agent_skills/skills/arxiv-search/SKILL.md |
| arXiv搜索Skill | 有示例代码 | 代码/agent_skills/skills/arxiv-search/arxiv_search.py |
| LangGraph文档Skill | 有示例代码 | 代码/agent_skills/skills/langgraph-docs/SKILL.md |
| 竞品分析Skill | 有示例代码 | 代码/demo/.codebuddy/skills/competitor-analysis/SKILL.md |
| 竞品分析Skill | 有示例代码 | 代码/demo/.codebuddy/skills/competitor-analysis/scripts/竞品数据收集.py |
| 竞品分析Skill | 有示例代码 | 代码/demo/.codebuddy/skills/competitor-analysis/references/竞品分析框架.md |
| 竞品分析Skill | 有示例代码 | 代码/demo/.codebuddy/skills/competitor-analysis/assets/分析报告模板.md |
| Agent Skills | 被考察于 | Skills 和 MCP 有什么区别 |
| Agent Skills | 应用于 | 可复用 Agent 工作流封装 |
