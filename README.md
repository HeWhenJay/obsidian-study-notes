# Obsidian AI 学习笔记库

这是一个面向 AI 应用开发学习者的中文 Obsidian 笔记库，重点整理 AI Agent、RAG、LangChain、LangGraph、GraphRAG、多 Agent 系统、MCP、A2A、Agent Skills、AutoGen、CrewAI 等方向的课程笔记、技术图解、代码示例和知识关系标记。

如果你正在找系统化的 AI Agent 学习笔记、RAG 优化笔记、LangChain 实战笔记、GraphRAG 原理和实践记录，这个仓库可以作为学习路线、复习资料和项目实践参考。

## 适合谁

- 正在入门大模型应用开发，希望从 Prompt、RAG、Agent 工程逐步建立知识体系的人。
- 想系统学习 AI Agent、LangChain、LangGraph、AutoGen、CrewAI、MCP/A2A 的开发者。
- 需要整理 RAG 优化方法的人，包括查询改写、索引优化、检索优化、RAG-Fusion、重排序、上下文压缩、GraphRAG 和 RAG 效果评估。
- 准备 AI Agent 开发实习、RAG 项目、企业知识库问答、智能客服、多 Agent 协作项目的人。
- 使用 Obsidian 管理学习资料，希望参考中文技术笔记结构和关系标记写法的人。

## 当前内容

### AI Agent 相关

入口笔记：`AI Agent相关/AI Agent.md`

已整理内容：

- AI Agent 全景：Agent 基础概念、常见模式、应用场景和技术路线。
- 多 Agent 系统：多智能体协作、任务分工、AutoGen、CrewAI、Agent 小镇等方向。
- LangChain：Model I/O、LCEL、RAG、工具调用、中间件和 `create_agent`。
- LangGraph：状态图、节点、边、reducer、工具调用、interrupt、checkpoint、持久化和多 Agent 交接。
- MCP、A2A 与 Agent Skills：工具协议、智能体通信、技能文件结构和工程化实践。

### RAG 相关

入口笔记：`RAG相关/RAG.md`

已整理内容：

- Pre-Retrieval 预检索优化：查询优化、索引优化、检索优化。
- Post-Retrieval 后检索优化：重排序、RAG-Fusion、上下文压缩和过滤。
- GraphRAG：知识图谱、实体关系抽取、社区检测、Community Report、Local/Global/DRIFT Search。
- RAG 效果评估：检索评估、响应评估、常用指标和评估工具。

### 附件图解

`Attachments/` 中保存了大量配套图解，覆盖：

- AI Agent 架构与开发框架对比。
- RAG 查询、索引、检索、重排序和评估流程。
- LangGraph 状态图、工具节点、checkpoint、interrupt、多 Agent 交接。
- MCP、A2A、Agent Skills、AutoGen、CrewAI 等工具链实践。

## 推荐阅读顺序

1. `AI Agent相关/AI Agent.md`
2. `AI Agent相关/AI Agent全景/AI Agent总结.md`
3. `RAG相关/RAG.md`
4. `RAG相关/Pre-Retrieval预检索/Pre-Retrieval预检索优化.md`
5. `RAG相关/Post-Retrieval后检索/Post-Retrieval后检索优化.md`
6. `RAG相关/GraphRAG/GraphRAG介绍.md`
7. `AI Agent相关/LangChain/LangChain总结.md`
8. `AI Agent相关/LangGraph/LangGraph总结.md`
9. `AI Agent相关/MCP、A2A与Agent Skills/MCP、A2A与Agent Skills总结.md`
10. `AI Agent相关/多Agent系统/多Agent系统总结.md`

## 笔记特点

- 使用中文解释核心概念，保留关键英文术语，适合反复复习。
- 每个主题尽量包含背景、核心思路、方法、代码索引、易错点和总结。
- 保留 Obsidian 双链，方便在图谱视图中串联 AI Agent、RAG、LangChain、LangGraph、GraphRAG 等知识点。
- 多数专题含 `## 关系标记`，用“主体、关系、客体”的形式记录知识关联。
- 结合课程材料、官方文档和本地实践代码，不只是概念摘要。

## 关键词

AI Agent 学习笔记、RAG 学习笔记、LangChain 中文笔记、LangGraph 中文笔记、GraphRAG 笔记、MCP 学习笔记、A2A 协议、Agent Skills、AutoGen 笔记、CrewAI 笔记、多智能体系统、检索增强生成、知识库问答、大模型应用开发、Obsidian 学习笔记。

## 使用方式

推荐用 Obsidian 打开本仓库根目录：

```bash
git clone https://github.com/HeWhenJay/obsidian-study-notes.git
```

然后在 Obsidian 中选择该目录作为 vault，即可查看双链、附件图片和知识图谱。

## 说明

这些笔记主要用于个人学习、复习和项目实践沉淀。内容会持续补充和修订，适合参考学习路线、概念理解和工程实践思路；具体 API、框架版本和模型能力请以官方文档为准。
