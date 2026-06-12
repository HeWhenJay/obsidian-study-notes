## 背景介绍

本节对应 PPT《5、多Agent系统.pptx》第 19-39 页，主题从多智能体系统概念进入 AutoGen 实践。前一节 [[多Agent系统（1）]] 讲 MAS 定义、失败模式、上下文工程和框架对比；本节重点看 AutoGen 如何把多 Agent 对话、代码执行、工具调用和人类协作组合成具体项目。

本节保存的示例代码位于当前目录下的 `代码` 文件夹，主要包括：

- `代码/AutoGen_Studio/`
- `代码/autogen_generate_video/`
- `代码/autogen_code/`

其中源码中的真实密钥已从笔记副本中移除或改为环境变量读取；复习时只记住变量名和配置位置，不要在代码中硬编码 API Key。

## 初识 AutoGen

AutoGen 是微软研究院推出的开源框架，为开发者提供通用、可定制的基础设施，通过多智能体对话简化复杂 LLM 应用开发。

它的核心目标是整合：

- LLM 推理和生成能力。
- 代码执行能力。
- 工具调用能力。
- 人类协作和审批能力。

AutoGen 适合的问题不是“一次问答”，而是需要多个角色共同推进的复杂任务，例如浏览网页、验证信息、生成代码、执行代码、审查结果、再次修正。

## AutoGen 技术架构

PPT 第 20 页把 AutoGen 生态分成三类组件：

![[AutoGen技术架构图.png]]

| 层次 | 组件 | 作用 |
| --- | --- | --- |
| Framework | Core、AgentChat、Extensions | 提供多 Agent 对话和扩展能力 |
| Developer Tools | Studio、Bench | Studio 用无代码 GUI 搭建应用；Bench 用于评估 Agent 性能 |
| Apps | Magentic-One、自定义 App | 基于框架构建具体多 Agent 应用 |

这里要注意：AutoGen Studio 不是 AutoGen 的全部，它只是更易上手的可视化开发工具。真正写代码时，AgentChat 和 Core 才是更底层的 API。

## AutoGen Studio

AutoGen Studio 的定位是“让 AI 开发像搭积木一样简单”。课程项目名是 `AutoGen_Studio`。

PPT 中的安装和启动命令已保存为：

```text
代码/AutoGen_Studio/autogen_studio_start.ps1
```

核心命令如下：

```powershell
pip install -U "autogenstudio"
playwright install
autogenstudio ui --port 8080 --appdir ./my-app
```

启动后打开：

```text
http://127.0.0.1:8080
```

![[AutoGen Studio安装运行命令图.png]]

配套资料中还有完整依赖清单：

- `代码/AutoGen_Studio/Readme.txt`
- `代码/AutoGen_Studio/requiresment.txt`

## 模型配置

第 23-24 页演示在 AutoGen Studio 中配置阿里通义模型。

![[AutoGen Studio通义模型配置图.png]]

PPT 中强调的 `model_info` 已保存为：

```text
代码/AutoGen_Studio/model_info.json
```

关键字段包括：

```json
{
  "vision": "True",
  "function_calling": "True",
  "json_output": "True",
  "family": "unknown",
  "structured_output": "True"
}
```

![[AutoGen Studio模型能力配置图.png]]

这组配置的学习重点是：AutoGen 需要知道模型是否支持视觉、Function Calling、JSON 输出和结构化输出，否则 Agent 能力声明和实际模型能力可能不一致。

## Team、Session 和运行可视化

第 25-27 页展示了默认 Team 配置、创建会话和运行过程。

![[AutoGen Studio默认Team配置图.png]]

![[AutoGen Studio运行可视化图.png]]

PPT 里提到：Sessions 左侧是 Agent 的运行流程，右侧对流程做可视化。复习时把它理解成“可观察的多 Agent 对话轨迹”。它对调试很重要，因为 MAS 失败往往不是最终答案才出错，而是在某个 Agent 交接、验证或选择下一角色时已经偏离。

## 网页浏览智能体示例

第 28-30 页演示 AutoGen Studio 构建网页浏览智能体，任务是：

```text
调研 2024 年 AI 领域十大趋势并总结
```

PPT 给出的流程是：

1. `websurfer_agent` 根据用户问题自动打开浏览器并访问权威媒体。
2. `assistant_agent` 指导 `websurfer_agent` 操作浏览器，直到出现想要的内容。
3. 系统提取关键信息并生成答案。

![[AutoGen Studio网页浏览智能体流程图.png]]

角色选择 Prompt 已保存为：

```text
代码/AutoGen_Studio/selector_prompt.md
```

![[AutoGen Studio角色选择Prompt图.png]]

这个 Prompt 的关键点是：它不是直接回答用户问题，而是从 `{participants}` 中选择下一个应该行动的角色。也就是说，多 Agent 系统里经常需要一个“调度者”决定谁接着说、谁接着做。

## AgentChat

第 31-32 页进入 AgentChat。

![[AutoGen AgentChat说明图.png]]

AgentChat 是用于构建多代理应用程序的高级 API，建立在 `autogen-core` 之上。课程给出的定位是：

- 初学者：优先从 AgentChat 入门。
- 高级用户：使用 `autogen-core` 的事件驱动模型获得更大灵活性。

官方文档：

- [AutoGen AgentChat User Guide](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html)

在示例代码里，常见 Agent 包括：

- `AssistantAgent`：使用大模型并可调用工具。
- `UserProxyAgent`：让人类输入进入多 Agent 流程。
- `CodeExecutorAgent`：执行代码并返回执行结果。
- `MultimodalWebSurfer`：浏览网页和检索信息。
- `FileSurfer`：浏览本地文件。
- `VideoSurfer`：处理视频内容。

## 实战项目 1：短视频自动生成工具

第 33-38 页介绍 `autogen_generate_video`。它用 AutoGen 多 Agent 协作，把文本 Prompt 转为 YouTube Shorts 风格短视频。

项目代码已保存到：

```text
代码/autogen_generate_video/
```

核心文件：

| 文件 | 作用 |
| --- | --- |
| `代码/autogen_generate_video/短视频生成主程序.py` | 定义四个 Agent 和 RoundRobinGroupChat 执行流程 |
| `代码/autogen_generate_video/工具函数.py` | 封装 TTS、图像生成和视频合成工具 |
| `代码/autogen_generate_video/README.md` | 项目说明和架构 |
| `代码/autogen_generate_video/requirements.txt` | 依赖清单 |

项目角色分工如下：

![[AutoGen短视频角色职责流程图.png]]

端到端流程如下：

![[AutoGen短视频端到端流程图.png]]

代码中的四个核心 Agent：

| Agent | 职责 | 对应工具 |
| --- | --- | --- |
| `script_writer` | 根据用户输入生成主题、要点和 5 条字幕 | 结构化 JSON 输出 |
| `voice_actor` | 根据字幕生成配音 | `generate_voiceovers` |
| `graphic_designer` | 根据字幕生成图像提示并生成图片 | `generate_images` |
| `director` | 同步图片、语音、字幕和背景音乐，生成最终视频 | `generate_video` |

AutoGen 团队编排使用：

```text
RoundRobinGroupChat([script_writer, voice_actor, graphic_designer, director])
```

这里的设计很适合复习 MAS：每个 Agent 不是泛泛回答问题，而是只做自己负责的阶段，靠上一阶段的输出推动下一阶段。

### 依赖和环境变量

PPT 第 34 页强调：这个项目需要音视频处理组件和语音大模型支持。

![[AutoGen短视频项目依赖说明图.png]]

需要关注：

- `ffmpeg`：用于音视频合成，需要本地安装并配置环境变量。
- 豆包 TTS：需要 `DOUBAO_APPID`、`DOUBAO_ACCESS_TOKEN`、`clusterid`。
- 图像生成：代码中使用 Pollinations.AI API。
- 大模型接口：使用 `DASHSCOPE_API_KEY` 和 `API_BASE_URL`。

火山引擎配置入口：

![[火山引擎语音技术入口图.png]]

![[火山引擎TTS密钥配置图.png]]

![[火山引擎ClusterID配置图.png]]

注意：课程源码里出现过硬编码 token。整理后的 `代码/autogen_generate_video/工具函数.py` 已改为读取 `POLLINATIONS_API_KEY`，复习时应记住“密钥必须放环境变量，不应写死在源码里”。

## 实战项目 2：多智能体协同代码生成

第 39 页介绍 `autogen_code`，重点是可以执行代码的 Agent：`CodeExecutorAgent`。

![[AutoGen协同代码生成项目图.png]]

项目代码已保存到：

```text
代码/autogen_code/
```

核心示例：

| 文件 | 场景 | 重点 |
| --- | --- | --- |
| `代码/autogen_code/文献搜集示例.py` | LLM 文献搜集 | Planner、Engineer、Scientist、Executor、Critic 多角色协作 |
| `代码/autogen_code/股价变动分析示例.py` | 股价变动分析 | Coder + Executor，用 Docker 执行代码 |
| `代码/autogen_code/数据可视化示例.py` | 数据可视化 | Coder、Executor、Critic 生成并审查图表 |
| `代码/autogen_code/数据分析示例.py` | 数据分析 | 下载数据、统计并接受 Critic 反馈 |

可视化示例输出：

![[AutoGen代码生成可视化结果图.png]]

代码执行类 Agent 的学习重点：

1. `CodeExecutorAgent` 不是“建议你运行代码”，而是把生成代码交给执行器运行。
2. `DockerCommandLineCodeExecutor` 能隔离执行环境，但运行前必须启动 Docker。
3. 复杂任务最好加 Critic/Reviewer，让它检查代码、结果和可视化质量。
4. 代码执行结果要反馈给生成 Agent，形成“生成 -> 执行 -> 观察 -> 修正”的闭环。

## 小结

AutoGen 的核心不是某个 GUI，而是“多 Agent 对话 + 工具调用 + 代码执行 + 人类协作”的组合能力。

从本节可以抽出三种落地形态：

- Studio 低代码搭建：适合观察 Agent 流程、快速原型和演示。
- AgentChat 编程开发：适合写可控的多 Agent 应用。
- CodeExecutorAgent：适合需要生成、执行、验证代码的任务，但必须重视隔离、安全和验收。

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| 多Agent系统（2） | 属于技能 | [[AI Agent相关/AI Agent]] |
| 多Agent系统（2） | 前置知识 | [[多Agent系统（1）]] |
| 多Agent系统（2） | 相关知识 | AutoGen |
| 多Agent系统（2） | 相关知识 | AutoGen Studio |
| 多Agent系统（2） | 相关知识 | AgentChat |
| 多Agent系统（2） | 相关知识 | CodeExecutorAgent |
| 多Agent系统（2） | 相关知识 | RoundRobinGroupChat |
| 多Agent系统（2） | 相关知识 | SelectorGroupChat |
| 多Agent系统（2） | 相关知识 | DockerCommandLineCodeExecutor |
| AutoGen Studio | 有示例代码 | 代码/AutoGen_Studio/autogen_studio_start.ps1 |
| AutoGen Studio | 有示例代码 | 代码/AutoGen_Studio/model_info.json |
| AutoGen Studio | 有示例代码 | 代码/AutoGen_Studio/selector_prompt.md |
| AutoGen短视频自动生成工具 | 有示例代码 | 代码/autogen_generate_video/短视频生成主程序.py |
| AutoGen短视频自动生成工具 | 有示例代码 | 代码/autogen_generate_video/工具函数.py |
| AutoGen短视频自动生成工具 | 应用于 | YouTube Shorts风格视频生成 |
| 多智能体协同代码生成 | 有示例代码 | 代码/autogen_code/文献搜集示例.py |
| 多智能体协同代码生成 | 有示例代码 | 代码/autogen_code/股价变动分析示例.py |
| 多智能体协同代码生成 | 有示例代码 | 代码/autogen_code/数据可视化示例.py |
| 多智能体协同代码生成 | 有示例代码 | 代码/autogen_code/数据分析示例.py |
| 多智能体协同代码生成 | 应用于 | 股价变动分析 |
| 多智能体协同代码生成 | 应用于 | 数据可视化 |
| 多智能体协同代码生成 | 应用于 | 数据分析 |
| 多Agent系统（2） | 被考察于 | AutoGen Studio 和 AgentChat 的区别是什么 |
| 多Agent系统（2） | 被考察于 | CodeExecutorAgent 为什么需要 Docker |
| 多Agent系统（2） | 被考察于 | RoundRobinGroupChat 适合什么协作流程 |
