## 背景介绍

本节对应 `LangGraphV1.x/adv` 目录，主题是进阶控制流：图可视化、条件分支、并行 MapReduce（映射归约）、递归限制、`Command`（命令式跳转对象）、运行配置、checkpoint（状态检查点）、子图和 `interrupt`（中断等待）人机协作。

第一节解决“图怎么搭起来”，本节解决“图如何在复杂流程中可控地跳转、并行、暂停、恢复和可视化”。这也是 LangGraph 相比普通 Agent 封装最核心的工程价值。

## 英文术语中文名

代码标识符保留英文，正文里优先按下面的中文名理解：

| 英文术语 | 中文名 | 说明 |
| --- | --- | --- |
| Visualization | 图可视化 | 把图结构画出来，便于检查控制流 |
| Graphviz | 图绘制工具 | 常用的图结构渲染工具 |
| Mermaid | 文本绘图语法 | 用文本描述流程图、时序图等 |
| conditional edge | 条件边 | 根据状态选择下一条边 |
| Command | 命令式跳转对象 | 在节点返回值里同时表达状态更新和下一跳 |
| Send | 并行分发指令 | 从路由函数派发多个并行任务 |
| MapReduce | 映射归约 | 先拆分并行处理，再合并结果的模式 |
| reducer | 状态合并器 | 合并多个分支或节点返回的状态更新 |
| recursion_limit | 递归步数上限 | 防止循环图无限执行 |
| GraphRecursionError | 图递归超限错误 | 图执行超过递归上限时抛出的异常 |
| checkpoint | 状态检查点 | 某一步执行后的状态快照 |
| checkpointer | 检查点保存器 | 保存和读取状态检查点的组件 |
| thread | 执行线程 / 会话线程 | 一组可恢复的执行历史 |
| interrupt | 中断等待 | 暂停图执行，等待外部输入后恢复 |
| human-in-the-loop | 人在回路 / 人机协作 | 让人参与审核、确认或补充信息 |
| subgraph | 子图 | 被父图调用或嵌套的一段图流程 |

## 课程脉络

`adv` 目录可以按功能分成六组：

| 代码 | 主题 | 学习重点 |
| --- | --- | --- |
| `Visualization.py` | 图可视化 | Graphviz、Mermaid、`get_graph().draw_mermaid_png()` |
| `示例3.3_条件分支.py`、`Command.py` | 条件路由和命令式跳转 | 路由函数、`Command(update=..., goto=...)`（命令式跳转对象） |
| `Map-reduce.py`、`Map-reduce2.py`、`示例4_如何创建用于并行执行的MapReduce分支.py` | 并行分支 | `Send`（并行分发指令）、并行执行、结果 reducer（状态合并器） |
| `loop/示例5.1_设置递归限制.py` | 循环保护 | `recursion_limit`、`GraphRecursionError` |
| `subgraphs/` | 子图 | 父图、子图、状态传递、跨图跳转 |
| `interr/` | 人机协作 | `interrupt()`（中断等待）、`Command(resume=...)`、checkpointer（检查点保存器）、人工审核工具调用 |

![[LangGraph可视化图2.png]]

这类图不是为了好看，而是为了确认控制流是否符合设计。复杂 Agent 出错时，先看图结构，再看执行轨迹。

## 条件分支

`示例3.3_条件分支.py` 延续基础图的条件边思路：路由函数读取 state，再返回节点名。适合“判断后走某条边”的场景。

常见模式：

| 判断条件 | 下一步 |
| --- | --- |
| 模型返回工具调用 | 进入工具节点 |
| 模型没有工具调用 | 结束 |
| 人工审核通过 | 执行动作 |
| 人工审核拒绝 | 回到生成节点 |
| 错误次数超过上限 | 进入兜底节点 |

条件边适合静态图结构：所有可能节点和边都提前声明，只是运行时选择哪一条。

## Command（命令式跳转对象）：状态更新和跳转合并

`Command.py` 展示了命令式控制流：

```text
return Command(
    update={"foo": value},
    goto=goto,
)
```

`Command`（命令式跳转对象）的价值是把“更新状态”和“跳到下一个节点”合成一个返回值。它适合节点内部已经知道下一步目标的情况，尤其是交接、人工审核、异常修复这类流程。

| 方式 | 特点 | 适合场景 |
| --- | --- | --- |
| 条件边 | 路由逻辑在边上 | 图结构清晰，路由规则集中 |
| `Command(goto=...)` | 节点返回中直接决定跳转 | 交接、动态跳转、同时更新状态和控制流 |

注意：`Command` 不是让图变成随意跳转的脚本。节点可能跳到哪些目标，最好用 `Command[Literal["node_b", "node_c"]]` 约束，方便静态理解和调试。

## Send（并行分发指令）和 MapReduce（映射归约）并行分支

`Map-reduce.py` 和 `Map-reduce2.py` 讲的是 `Send`。

`Send`（并行分发指令）可以从一个路由函数返回多个并行任务：

```text
return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]
```

`Map-reduce.py` 是同质节点并行：多个 subject 都发给同一个 `generate_joke` 节点。`Map-reduce2.py` 是异质节点并行：不同输入发给不同节点，例如一个生成笑话，一个生成悲伤故事。

![[LangGraph示例4.png]]

并行分支要特别关注 reducer（状态合并器）。多个分支同时写回同一个字段时，如果没有 reducer，后写入的更新可能覆盖先写入的更新。课程中用：

```text
jokes: Annotated[list[str], operator.add]
```

把多个分支的结果合并成列表。

## 递归限制

`loop/示例5.1_设置递归限制.py` 演示循环图的保护机制。只要图里存在循环，就要考虑终止条件。

两个关键点：

| 机制 | 作用 |
| --- | --- |
| 业务终止条件 | 例如任务完成、工具无调用、审核通过 |
| `recursion_limit` | 防止图无限循环 |

如果循环超过限制，LangGraph 会抛出类似 `GraphRecursionError` 的异常。复习时不要把它当成“报错处理技巧”，而要理解为 Agent 控制流设计的安全边界。

## 配置和 checkpoint（状态检查点）

`Configuration.py` 和 `Checkpoints.py` 连接到后续持久化主题。

运行配置常见写法：

```text
config = {"configurable": {"thread_id": "1"}}
```

`thread_id` 对 checkpoint（状态检查点）很关键。官方持久化文档说明：checkpointer（检查点保存器）使用 `thread_id` 作为保存和恢复 checkpoint 的主键；没有它，就无法把一次中断后的恢复请求定位回同一条执行线程。补充资料见：[LangGraph persistence threads](https://langchain-ai.github.io/langgraph/cloud/concepts/threads/)。

可以这样记：

| 概念 | 含义 |
| --- | --- |
| checkpoint（状态检查点） | 某一步图执行后的状态快照 |
| checkpointer（检查点保存器） | 保存和读取 checkpoint 的组件 |
| thread（执行线程） | 一组按 `thread_id` 关联的执行历史 |
| `thread_id` | 恢复同一会话或同一任务的指针 |

## interrupt（中断等待）：让图暂停等待外部输入

`adv/interr/interrupt_demo.py`、`interrupt_hitl.py`、`interrrput_demo2.py` 和 `agent中使用interrup.py` 讲的是人机协作。

`interrupt()`（中断等待）的作用是：在节点内部暂停执行，把问题或待审核内容返回给外部调用方。随后外部调用方用：

```text
Command(resume=...)
```

把人的输入传回图中。

官方 human-in-the-loop（人在回路 / 人机协作）文档强调几个点：

1. `interrupt()` 暂停图执行，并把值暴露给调用方。
2. 恢复时必须使用同一个 `thread_id`。
3. `Command(resume=...)` 的值会成为节点内 `interrupt()` 的返回值。
4. 被中断节点恢复时会从节点函数开头重新执行，因此中断前的副作用要谨慎设计。
5. 人机协作场景需要 checkpointer（检查点保存器）。

补充资料见：[LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)。

![[LangGraph如何使用interrupt等待用户输入.png]]

## 人工审核工具调用

`adv/interr/审查工具使用.py` 是本节最实用的例子：模型想调用天气工具前，先进入人工审核节点。

流程可以理解为：

```text
call_llm -> human_review_node -> run_tool -> call_llm
```

人工审核节点可以做三类决策：

| 动作 | 含义 |
| --- | --- |
| continue | 允许原工具调用继续执行 |
| update | 修改工具调用参数后再执行 |
| feedback | 不执行工具，给模型一条反馈，让模型重新生成 |

![[LangGraph如何审查工具调用.png]]

这类设计很适合高风险工具调用，例如发邮件、下单、删除数据、提交简历、支付、更新数据库。核心不是“让人多点一次确认”，而是把审核结果结构化写回状态和控制流。

## 子图

`subgraphs/Subgraphs.py` 和 `示例7_如何将控制流和状态更新与命令结合.py` 展示父图和子图。

子图适合把一段复杂流程封装起来，例如：

- 搜索和引用生成子图。
- 数据清洗子图。
- 审核修订子图。
- 多 Agent 协作子图。

关键是边界设计：子图需要明确接收哪些 state 字段，返回哪些字段。否则图嵌套会让上下文变得难以追踪。

## 复习重点

1. 条件边适合预先声明的分支，`Command`（命令式跳转对象）适合节点内决定跳转并同时更新状态。
2. `Send`（并行分发指令）用于生成多个并行分支；多个分支写同一字段时必须设计 reducer（状态合并器）。
3. 任何循环图都要有业务终止条件，并用 `recursion_limit` 兜底。
4. checkpointer（检查点保存器）保存状态快照，`thread_id` 是恢复同一执行线程的关键。
5. `interrupt()`（中断等待）让节点暂停等待外部输入，`Command(resume=...)` 恢复执行。
6. 被中断节点恢复时会重新执行节点函数，因此中断前不要放不可重复的副作用。
7. 人工审核工具调用可以用 `continue`、`update`、`feedback` 三类动作建模。

## 补充资料

- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangGraph persistence threads](https://langchain-ai.github.io/langgraph/cloud/concepts/threads/)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangGraph（2） | 属于技能 | [[AI Agent相关/AI Agent]] |
| LangGraph（2） | 前置知识 | [[LangGraph（1）]] |
| LangGraph（2） | 相关知识 | Command（命令式跳转对象） |
| LangGraph（2） | 相关知识 | Send（并行分发指令） |
| LangGraph（2） | 相关知识 | MapReduce（映射归约） |
| LangGraph（2） | 相关知识 | interrupt（中断等待） |
| LangGraph（2） | 相关知识 | checkpointer（检查点保存器） |
| LangGraph（2） | 相关知识 | thread_id |
| LangGraph（2） | 相关知识 | [[LangGraph总结]] |
| LangGraph控制流 | 有示例代码 | 代码/LangGraphV1.x/adv/Command.py |
| LangGraph并行分支 | 有示例代码 | 代码/LangGraphV1.x/adv/Map-reduce.py |
| LangGraph并行分支 | 有示例代码 | 代码/LangGraphV1.x/adv/Map-reduce2.py |
| LangGraph并行分支 | 有示例代码 | 代码/LangGraphV1.x/adv/示例4_如何创建用于并行执行的MapReduce分支.py |
| LangGraph人机协作 | 有示例代码 | 代码/LangGraphV1.x/adv/interr/interrupt_demo.py |
| LangGraph人机协作 | 有示例代码 | 代码/LangGraphV1.x/adv/interr/interrupt_hitl.py |
| LangGraph工具审核 | 有示例代码 | 代码/LangGraphV1.x/adv/interr/审查工具使用.py |
| LangGraph（2） | 被考察于 | Command（命令式跳转对象）和条件边有什么区别 |
| LangGraph（2） | 被考察于 | interrupt（中断等待）为什么需要 checkpointer（检查点保存器）和 thread_id |
| LangGraph（2） | 应用于 | 高风险工具调用人工审核 |
