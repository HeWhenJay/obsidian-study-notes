## 总览

本总结用于汇总《MCP & A2A & Agent Skills》这份 PPT 的分段笔记。当前已完成整份 PPT：

- [[MCP、A2A与Agent Skills（1）]]：第 1-12 页，MCP 定位、架构、生态、通信方式和股票分析 MCP 示例。
- [[MCP、A2A与Agent Skills（2）]]：第 13-17 页，A2A 协议、当前落地难点和 MCP 协同 A2A。
- [[MCP、A2A与Agent Skills（3）]]：第 18-26 页，Agent Skills 标准结构、渐进式加载、安全实践和配套 Skill 代码。

这份 PPT 的主线是：从“Agent 如何连接工具和数据”到“Agent 如何连接其他 Agent”，再到“Agent 如何加载可复用工作流知识”。

## 已覆盖内容

| 笔记 | PPT 范围 | 主题 |
| --- | --- | --- |
| [[MCP、A2A与Agent Skills（1）]] | 第 1-12 页 | MCP、Host/Client/Server、生命周期、Stdio/SSE/Streamable HTTP、FastAPI-MCP 股票分析项目 |
| [[MCP、A2A与Agent Skills（2）]] | 第 13-17 页 | A2A、Agent Card、Task、Message、Artifact、MCP 与 A2A 协同 |
| [[MCP、A2A与Agent Skills（3）]] | 第 18-26 页 | Agent Skills、SKILL.md、scripts/references/assets、渐进式加载、安全风险、DeepAgents 示例 |

## 核心结论

1. MCP 是 AI 应用连接外部工具、资源和提示模板的协议层，核心角色是 Host、Client、Server。
2. MCP Server 应按可执行能力边界管理，生命周期里要关注安装来源、运行权限和升级漂移。
3. 课程里的股票分析项目展示了从 FastAPI 接口到 MCP 工具的转换路径，重点看 `operation_id` 和 `FastApiMCP`。
4. A2A 解决的是 Agent 与 Agent 的互操作，核心结构是 Agent Card、Message、Task、Part 和 Artifact。
5. A2A 比 MCP 更难落地，因为它要求 Agent 自身可靠，还要解决身份、授权、责任和生态协作问题。
6. Agent Skills 是可移植能力包，适合沉淀流程、脚本、模板和参考资料，不等同于普通长 Prompt。
7. MCP 与 Skills 可以组合：用 Skills 指导 Agent 构建或使用 MCP，用 MCP 提供外部能力。
8. 三者选型顺序可以简单记为：工具/数据用 MCP，自治 Agent 协作用 A2A，稳定工作流沉淀用 Skills。

## 协议边界对比

| 能力 | 连接对象 | 解决的问题 | 典型产物 |
| --- | --- | --- | --- |
| Function Calling | 模型到应用内函数 | 单次工具 schema 调用 | `tools` 参数、JSON Schema、`tool_calls` |
| MCP | Host/Client 到 Server | 标准化发现和调用工具、资源、提示模板 | MCP Server、tools/resources/prompts、JSON-RPC |
| A2A | Agent 到远端 Agent | 发现能力、委托任务、返回状态和 Artifact | Agent Card、Task、Message、Artifact |
| Agent Skills | Agent 到本地/项目内技能包 | 让 Agent 掌握可复用流程和资料 | `SKILL.md`、`scripts/`、`references/`、`assets/` |

## 关键图

- ![[MCP架构示意图.png]]
- ![[MCP生态采用与服务集合图.png]]
- ![[MCP协同A2A示意图.png]]
- ![[MCP与Skills连接方式对比图.png]]
- ![[Agent Skills解决三类痛点图.png]]
- ![[Agent Skill标准文件结构图.png]]
- ![[SKILL.md结构解析图.png]]
- ![[Agent Skills渐进式加载原理图.png]]
- ![[Agent Skills安全最佳实践图.png]]

## 代码索引

| 目录 | 内容 |
| --- | --- |
| `代码/MCP_Stock_Analysis/` | FastAPI-MCP 股票分析服务，包含服务端、客户端、模型配置、股票数据、技术指标、AI 分析模块 |
| `代码/MCP_Stock_Analysis/mcp_server_integration_remote_mcp.py` | 服务端同时集成股票工具和阿里 WebSearch 远程 MCP |
| `代码/MCP_Stock_Analysis/integration_in_clients_remote_mcp.py` | 客户端同时连接本地股票 MCP 和远端 WebSearch MCP |
| `代码/agent_skills/` | DeepAgents + LangGraph + 通义千问的 Skill 运行示例 |
| `代码/agent_skills/skills/arxiv-search/` | arXiv 搜索 Skill，包含 `SKILL.md` 和 `arxiv_search.py` |
| `代码/agent_skills/skills/langgraph-docs/` | LangGraph 文档查询 Skill |
| `代码/demo/.codebuddy/skills/competitor-analysis/` | 竞品分析 Skill 示例，包含脚本、参考框架和报告模板 |

## 环境变量

本专题代码副本不包含真实 `.env`，只保留 `.env.example`：

| 文件 | 变量 |
| --- | --- |
| `代码/MCP_Stock_Analysis/.env.example` | `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`DASHSCOPE_API_KEY`、`API_BASE_URL` |
| `代码/agent_skills/.env.example` | `DASHSCOPE_API_KEY`、`API_BASE_URL` |

## 补充资料

- [MCP 官方架构说明](https://modelcontextprotocol.io/docs/learn/architecture)
- [MCP 传输协议说明](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [MCP 官方：Build with Agent Skills](https://modelcontextprotocol.io/docs/develop/build-with-agent-skills)
- [A2A 官方核心概念](https://a2a-protocol.org/latest/topics/key-concepts/)
- [A2A 官方规范](https://a2a-protocol.org/latest/specification/)
- [Agent Skills 官方概览](https://agentskills.io/home)
- [Agent Skills 官方规范](https://agentskills.io/specification)
- [阿里云百炼 MCP 市场](https://bailian.console.aliyun.com/?tab=app#/mcp-market)

## 复习重点

- MCP Host、Client、Server 的职责边界。
- Tools、Resources、Prompts 三类 MCP 能力区别。
- Stdio、HTTP+SSE、Streamable HTTP 的适用场景和版本关系。
- `FastApiMCP` 如何根据 FastAPI 的 `operation_id` 生成 MCP 工具。
- A2A 的 Agent Card、Task、Message、Part、Artifact。
- MCP 和 A2A 为什么不是替代关系。
- `SKILL.md` 的 frontmatter 和正文分别承担什么作用。
- Skills 的渐进式加载为什么能节省上下文。
- 第三方 MCP Server 和第三方 Skill 都要按可执行能力做安全审查。

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| MCP、A2A与Agent Skills总结 | 属于技能 | [[AI Agent相关/AI Agent]] |
| MCP、A2A与Agent Skills总结 | 相关知识 | [[MCP、A2A与Agent Skills（1）]] |
| MCP、A2A与Agent Skills总结 | 相关知识 | [[MCP、A2A与Agent Skills（2）]] |
| MCP、A2A与Agent Skills总结 | 相关知识 | [[MCP、A2A与Agent Skills（3）]] |
| MCP、A2A与Agent Skills总结 | 相关知识 | MCP |
| MCP、A2A与Agent Skills总结 | 相关知识 | A2A |
| MCP、A2A与Agent Skills总结 | 相关知识 | Agent Skills |
| MCP、A2A与Agent Skills总结 | 相关知识 | SKILL.md |
| MCP、A2A与Agent Skills总结 | 相关知识 | Function Calling |
| MCP、A2A与Agent Skills总结 | 相关知识 | FastApiMCP |
| MCP、A2A与Agent Skills总结 | 相关知识 | LangGraph |
| MCP、A2A与Agent Skills总结 | 有示例代码 | 代码/MCP_Stock_Analysis/mcp_server_integration_remote_mcp.py |
| MCP、A2A与Agent Skills总结 | 有示例代码 | 代码/MCP_Stock_Analysis/integration_in_clients_remote_mcp.py |
| MCP、A2A与Agent Skills总结 | 有示例代码 | 代码/agent_skills/main_win.py |
| MCP、A2A与Agent Skills总结 | 有示例代码 | 代码/agent_skills/skills/arxiv-search/arxiv_search.py |
| MCP、A2A与Agent Skills总结 | 有示例代码 | 代码/demo/.codebuddy/skills/competitor-analysis/SKILL.md |
| MCP、A2A与Agent Skills总结 | 被考察于 | MCP、A2A、Skills 三者如何选型 |
| MCP、A2A与Agent Skills总结 | 应用于 | Agent 工程能力边界设计 |
