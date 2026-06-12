## 背景介绍

本节对应 PPT《MCP & A2A & Agent Skills》第 1-12 页，主题是 MCP 的定位、架构、生态、通信方式和股票分析 MCP 示例项目。

MCP 的全称是 Model Context Protocol，即模型上下文协议。PPT 第 11 页里出现的 “Model Control Protocol” 应按 MCP 官方名称理解为 “Model Context Protocol”。它要解决的问题不是“模型如何思考”，而是“AI 应用如何用统一协议连接外部工具、数据源和提示模板”。

本节保存的示例代码位于当前目录下的 `代码` 文件夹，主要包括：

- `代码/MCP_Stock_Analysis/`
- `代码/MCP_Stock_Analysis/mcp_server_integration_remote_mcp.py`
- `代码/MCP_Stock_Analysis/mcp_server_integration_client.py`
- `代码/MCP_Stock_Analysis/integration_in_client_mcp_server.py`
- `代码/MCP_Stock_Analysis/integration_in_clients_remote_mcp.py`

原始代码中的 `.env` 没有复制到笔记目录，已替换为 `.env.example`。复习时只记变量名和配置位置，不要在代码中硬编码 API Key。

## MCP 要解决的问题

在 MCP 出现前，大模型应用接外部能力通常有三类方式：手写 API 调用、插件接口、Agent 框架内置工具。这些方式能跑通单点功能，但会带来几个工程问题：

- 每个应用都要重复适配同一批外部系统。
- 工具说明、鉴权、输入参数、返回结构缺少统一语义。
- 当工具数量增加时，模型端上下文和客户端维护成本都会膨胀。
- 本地工具、远程服务、私有数据源的接入方式不一致。

MCP 的价值是把“AI 应用连接外部能力”的接口标准化。官方也常用 USB-C 类比：Host 不需要知道每个外设的内部实现，只需要按协议发现能力、调用能力、接收结果。

## MCP 架构

![[MCP架构示意图.png]]

MCP 采用 Host、Client、Server 三层角色：

| 角色 | 作用 | 课程中的理解 |
| --- | --- | --- |
| MCP Host | 承载 AI 应用，管理一个或多个 MCP Client | Claude Desktop、Cursor、VS Code、Agent 应用本体 |
| MCP Client | 与某个 MCP Server 保持一条连接，完成初始化、能力发现和调用 | Host 内部的协议适配层 |
| MCP Server | 对外暴露工具、资源和提示模板 | 文件系统服务、股票分析服务、联网搜索服务、数据库服务 |

一个 Host 可以连接多个 Server，但通常是“一个 Client 对一个 Server”。这样做的好处是隔离边界清楚：某个 Server 的工具、权限和生命周期不会直接污染其他 Server。

MCP Server 主要暴露三类能力：

| 能力 | 含义 | 例子 |
| --- | --- | --- |
| Tools | 可执行动作，模型可以按 schema 调用 | 查询股票价格、读取网页、执行搜索 |
| Resources | 可读取上下文，通常是文件、数据库记录或状态 | 本地文件、项目文档、业务数据 |
| Prompts | 可复用提示模板或工作流模板 | 分析报告模板、代码审查模板 |

## 生命周期和风险

PPT 把 MCP Server 生命周期分为创建、运行、更新三个阶段。复习时可以按“安装前、运行中、升级后”来记：

| 阶段 | 核心动作 | 主要风险 |
| --- | --- | --- |
| 创建阶段 | 服务器注册、安装程序部署、代码完整性验证 | 名称冲突、安装程序伪造、代码注入、后门 |
| 运行阶段 | 处理请求、执行工具调用、访问外部资源 | 工具名冲突、斜杠命令重叠、沙箱逃逸、越权访问 |
| 更新阶段 | 升级版本、变更配置、适配新需求 | 更新后权限持续、版本漂移、旧配置残留 |

MCP Server 本质上是可执行能力边界，不只是“文档”。因此接入第三方 Server 时要看来源、权限、工具名、输入输出 schema 和日志行为。

## MCP 生态

![[MCP生态采用与服务集合图.png]]

课程里提到的 MCP 生态可以分为三类：

| 类型 | 内容 |
| --- | --- |
| 采用者 | Anthropic、OpenAI、百度地图、BlenderMCP、Replit、Cursor、JetBrains 等 |
| 社区服务集合 | MCP.so、Glama、PulseMCP 等社区目录 |
| SDK 和开发工具 | TypeScript、Python、Java 等 SDK，以及 EasyMCP、FastMCP、Foxy Contexts 等框架工具 |

从工程角度看，MCP 生态是否成熟，主要取决于两个指标：一是高质量 Server 是否足够多，二是 Host 是否能给工具权限、鉴权和审计提供足够好的用户体验。

## 通信方式

PPT 第 11 页列了三种通信方式：Stdio、HTTP+SSE、Streamable HTTP。结合官方文档复习时，要注意版本语义：当前 MCP 规范主推 `stdio` 和 `Streamable HTTP` 两种标准传输；`HTTP+SSE` 是早期远程传输方式，在课件中可作为历史兼容概念理解。

| 方式 | 运行形态 | 适合场景 | 注意点 |
| --- | --- | --- | --- |
| Stdio | Client 启动 Server 子进程，通过标准输入输出传 JSON-RPC | 本地工具、开发调试、单用户本地集成 | stdout 只能输出合法 MCP 消息，日志应走 stderr |
| HTTP+SSE | Server 独立运行，HTTP 请求配合 SSE 返回事件 | 早期远程 MCP 服务 | 新规范中已被 Streamable HTTP 替代 |
| Streamable HTTP | Server 作为远程 HTTP 服务，支持 POST/GET、可选 SSE 流 | 云 API、多人共享服务、需要鉴权的远程服务 | 要校验 Origin、绑定 localhost 或做好认证，避免 DNS rebinding 和越权访问 |

在课程代码中，`langchain_mcp_adapters.client.MultiServerMCPClient` 使用 `transport: "sse"` 连接 `http://localhost:8000/mcp` 和阿里百炼 WebSearch MCP 服务。这里对应的是课程当时的 SSE 接入实践。

## 股票分析 MCP 示例

`代码/MCP_Stock_Analysis/` 是课程的核心 MCP 示例。它用 FastAPI 暴露股票分析 API，再用 `fastapi-mcp` 把 API 端点转换为 MCP 工具。

关键文件：

| 文件 | 作用 |
| --- | --- |
| `代码/MCP_Stock_Analysis/README.md` | 项目说明、运行方式、API 和 MCP 工具列表 |
| `代码/MCP_Stock_Analysis/models.py` | 通义千问兼容 OpenAI 接口的模型配置，环境变量名为 `DASHSCOPE_API_KEY` |
| `代码/MCP_Stock_Analysis/mcp_server_integration_remote_mcp.py` | MCP 服务端，把股票分析和阿里百炼 WebSearch 都封装进同一个 FastAPI-MCP 服务 |
| `代码/MCP_Stock_Analysis/mcp_server_integration_client.py` | MCP 客户端，只连接本地 `http://localhost:8000/mcp` |
| `代码/MCP_Stock_Analysis/integration_in_client_mcp_server.py` | MCP 服务端，只提供股票分析工具 |
| `代码/MCP_Stock_Analysis/integration_in_clients_remote_mcp.py` | MCP 客户端，同时连接本地股票服务和远端阿里 WebSearch 服务 |

两种组合方式要分清：

| 组合 | 远端 WebSearch 集成位置 | 适合理解 |
| --- | --- | --- |
| `integration_in_client_mcp_server.py` + `integration_in_clients_remote_mcp.py` | 客户端 | Client 可以聚合多个 MCP Server |
| `mcp_server_integration_remote_mcp.py` + `mcp_server_integration_client.py` | 服务端 | Server 可以把远端能力再包装成自己的 MCP 工具 |

## API 到工具的映射

FastAPI 端点通过 `operation_id` 变成 MCP 工具名。课程项目里核心映射如下：

| FastAPI 接口 | MCP 工具名 | 能力 |
| --- | --- | --- |
| `GET /stock_analyzer` | `analyze_stock` | 分析单只股票，返回价格、评分、技术指标和 AI 分析 |
| `GET /stock_price` | `get_stock_price` | 获取最新价格、开高低收、成交量和涨跌幅 |
| `GET /stock_technical_analysis` | `get_technical_analysis` | 获取 MA、RSI、MACD、布林带等技术分析 |
| `GET /stock_score` | `get_stock_score` | 获取综合评分和投资建议 |
| `GET /stock_ai_analysis` | `get_ai_analysis` | 调用大模型生成股票分析文本 |
| `GET /ali_search_web` | `ali_search_web` | 调用阿里百炼 WebSearch MCP 服务做联网搜索 |

服务启动后常用入口：

```text
python mcp_server_integration_remote_mcp.py
http://localhost:8000/docs
http://localhost:8000/mcp
http://localhost:8000/health
```

## 和 Function Calling 的关系

Function Calling 解决的是“模型一次调用某个函数”的 schema 问题；MCP 解决的是“Host 如何长期发现、连接、调用和管理外部 Server”的协议问题。

可以这样区分：

| 维度 | Function Calling | MCP |
| --- | --- | --- |
| 范围 | 单次模型调用里的工具 schema | AI 应用与外部能力之间的协议层 |
| 生命周期 | 通常由应用代码内联管理 | 有初始化、能力发现、调用、通知、断开等流程 |
| 工具来源 | 应用自己注册函数 | 独立 MCP Server 暴露能力 |
| 复用性 | 依赖具体应用 | Server 可被多个 MCP Host 复用 |

## 小结

1. MCP 是模型上下文协议，不是模型控制协议。
2. MCP 的核心不是某个工具函数，而是 Host、Client、Server 之间的标准化连接方式。
3. Server 暴露 Tools、Resources、Prompts；Client 负责发现和调用；Host 负责把能力整合进 AI 应用。
4. 本地调试优先理解 Stdio；远程服务重点理解 Streamable HTTP/SSE、鉴权和安全边界。
5. 股票分析项目展示了从 FastAPI 接口到 MCP 工具的工程路径，重点看 `operation_id`、`FastApiMCP`、`mcp.mount()`、`mcp.setup_server()` 和 `MultiServerMCPClient`。

## 补充资料

- [MCP 官方架构说明](https://modelcontextprotocol.io/docs/learn/architecture)
- [MCP 传输协议说明](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [阿里云百炼 MCP 市场](https://bailian.console.aliyun.com/?tab=app#/mcp-market)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| MCP、A2A与Agent Skills（1） | 属于技能 | [[AI Agent相关/AI Agent]] |
| MCP、A2A与Agent Skills（1） | 前置知识 | [[AI Agent全景/AI Agent（2）]] |
| MCP、A2A与Agent Skills（1） | 前置知识 | Function Calling |
| MCP、A2A与Agent Skills（1） | 相关知识 | Model Context Protocol |
| MCP、A2A与Agent Skills（1） | 相关知识 | MCP Host |
| MCP、A2A与Agent Skills（1） | 相关知识 | MCP Client |
| MCP、A2A与Agent Skills（1） | 相关知识 | MCP Server |
| MCP、A2A与Agent Skills（1） | 相关知识 | Stdio |
| MCP、A2A与Agent Skills（1） | 相关知识 | Streamable HTTP |
| MCP、A2A与Agent Skills（1） | 相关知识 | FastApiMCP |
| MCP、A2A与Agent Skills（1） | 相关知识 | [[MCP、A2A与Agent Skills总结]] |
| 股票分析MCP服务 | 有示例代码 | 代码/MCP_Stock_Analysis/mcp_server_integration_remote_mcp.py |
| 股票分析MCP服务 | 有示例代码 | 代码/MCP_Stock_Analysis/mcp_server_integration_client.py |
| 股票分析MCP服务 | 有示例代码 | 代码/MCP_Stock_Analysis/integration_in_client_mcp_server.py |
| 股票分析MCP服务 | 有示例代码 | 代码/MCP_Stock_Analysis/integration_in_clients_remote_mcp.py |
| 股票分析MCP服务 | 有示例代码 | 代码/MCP_Stock_Analysis/models.py |
| MCP | 被考察于 | MCP Host、Client、Server 分别负责什么 |
| MCP | 应用于 | 股票分析 MCP 服务 |
