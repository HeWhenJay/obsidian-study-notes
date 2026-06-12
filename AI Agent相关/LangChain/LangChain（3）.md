## 背景介绍

本节对应 `LangChain03` 资料中的 RAG 部分，也补充课程已有 [[RAG相关/RAG]] 笔记。主题是如何用 LangChain 串起文档加载、切分、嵌入、向量存储、检索和生成。

本节保存的示例代码位于：

- `代码/rag/doc_and_llm.py`
- `代码/rag/rag_with_webpage.py`
- `代码/rag/人事管理流程.docx`

课程 PPT 里把 RAG 分成两段：索引阶段和问答阶段。LangChain 的价值是给每个阶段提供统一组件，让数据从原始文件变成 `Document`，再变成向量和检索器，最后进入 Prompt。

## 英文术语中文名

| 英文术语 | 中文名 | 说明 |
| --- | --- | --- |
| RAG | 检索增强生成 | 先检索相关知识，再让模型基于上下文回答 |
| Document | 文档对象 | 包含 `page_content` 和 `metadata` |
| Document Loader | 文档加载器 | 从 TXT、PDF、HTML、Word、Markdown 等来源加载数据 |
| Text Splitter | 文本切分器 | 把长文档切成适合检索的块 |
| Embeddings | 嵌入模型包装器 | 把文本映射为向量 |
| Vector Store | 向量存储 | 存储向量和元数据，支持相似度查询 |
| Retriever | 检索器 | 以统一接口返回相关文档 |
| Chroma | 向量数据库 | 课程代码使用的向量存储 |
| FAISS | 向量索引库 | 常见本地向量检索方案 |
| BM25Retriever | 关键词检索器 | 基于词项匹配，适合补足语义检索 |
| EnsembleRetriever | 集成检索器 | 融合多个检索器结果 |
| create_stuff_documents_chain | Stuff 文档链 | 把多个文档拼进上下文后交给模型 |
| create_retrieval_chain | 检索问答链 | 组合检索器和文档处理链 |

## RAG 的两阶段

RAG 不只是“向量库 + 大模型”。更准确的流程是：

```text
索引阶段：加载 -> 切分 -> 元数据 -> 嵌入 -> 入库
问答阶段：问题 -> 检索 -> 组装上下文 -> 生成答案 -> 引用/校验
```

| 阶段 | 主要问题 | LangChain 组件 |
| --- | --- | --- |
| 加载 | 数据从哪里来 | `TextLoader`、`PyPDFLoader`、`WebBaseLoader`、`Docx2txtLoader` |
| 切分 | 文本块多大、重叠多少 | `RecursiveCharacterTextSplitter`、`MarkdownHeaderTextSplitter` |
| 表示 | 文档和元数据如何流转 | `Document` |
| 嵌入 | 文本如何转向量 | `DashScopeEmbeddings`、OpenAI/HuggingFace embeddings |
| 存储 | 向量放哪里 | `Chroma`、`FAISS` 等 |
| 检索 | 如何找相关片段 | `as_retriever()`、BM25、混合检索 |
| 生成 | 如何让模型只基于上下文回答 | `ChatPromptTemplate`、LCEL、文档链 |

## Document 对象

LangChain 的 RAG 数据流核心是 `Document`。它通常包含两个字段：

| 字段 | 含义 | 用途 |
| --- | --- | --- |
| `page_content` | 文档正文 | 被切分、嵌入、检索和注入 Prompt |
| `metadata` | 来源、页码、标题、文件名等元数据 | 做过滤、引用、溯源和权限控制 |

`代码/rag/doc_and_llm.py` 先用注释模拟了宠物文档，再切到真实 Word 文档 `人事管理流程.docx`。这个例子适合理解：加载器的目标不是直接给模型文本，而是先转成标准 `Document` 列表。

## 文档加载和切分

课程列出的常见加载器：

| 文档类型 | 加载器 |
| --- | --- |
| TXT | `TextLoader` |
| PDF | `PyPDFLoader` |
| CSV | `CSVLoader` |
| JSON | `JSONLoader` |
| HTML | `UnstructuredHTMLLoader` / `WebBaseLoader` |
| Markdown | `UnstructuredMarkdownLoader` |
| 目录 | `DirectoryLoader` |
| Word | `Docx2txtLoader` / `UnstructuredWordDocumentLoader` |

切分器重点看三个：

| 切分器 | 适合场景 |
| --- | --- |
| `CharacterTextSplitter` | 简单按字符或分隔符切分 |
| `RecursiveCharacterTextSplitter` | 默认优先，尽量保持自然段、句子等结构 |
| `MarkdownHeaderTextSplitter` | Markdown 笔记、技术文档、章节结构清晰的材料 |

`doc_and_llm.py` 使用 `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`。这里的 `chunk_size` 和 `chunk_overlap` 不是固定答案，需要结合文档结构、模型上下文窗口、检索召回和回答质量调参。

## 嵌入和向量存储

PPT 把嵌入模型包装器放在三类模型包装器之一：

| 模型包装器 | 输入 | 输出 | 用途 |
| --- | --- | --- | --- |
| LLM | 字符串 | 字符串 | 旧式文本补全，课程不重点使用 |
| Chat Model | 消息列表 | AI 消息 | 聊天、Agent、结构化交互 |
| Embedding Model | 文本 | 向量 | RAG 检索、相似度搜索 |

`doc_and_llm.py` 用 `DashScopeEmbeddings` 生成向量，再用 `Chroma.from_documents` 建向量库。随后调用 `vector_store.as_retriever()` 得到检索器。

要注意：向量库只解决“语义相似”问题，不等于最终答案可靠。还需要元数据过滤、混合检索、重排序、上下文压缩和回答校验，这些内容与 [[RAG相关/Pre-Retrieval预检索优化/Pre-Retrieval预检索优化]]、[[RAG相关/Post-Retrieval后检索优化/Post-Retrieval后检索优化]] 相关。

## 检索策略

课程 PPT 中列出了几种检索器：

| 检索器 | 特点 |
| --- | --- |
| `FAISS.from_texts(...).as_retriever()` | 本地向量检索，适合快速原型 |
| `Chroma.from_documents(...).as_retriever()` | 课程代码使用，适合文档向量检索 |
| `BM25Retriever.from_texts(...)` | 关键词匹配强，适合专有名词、编号、精确词 |
| `EnsembleRetriever` | 融合语义检索和关键词检索 |

如果用户问题中有精确实体、编号、岗位名、数据库字段，只做 embedding 检索容易漏召回。此时可把 BM25 和向量检索做混合检索，再接重排序。

## 两种 RAG 写法

课程代码里有两种写法。

第一种是手写 LCEL：

```text
{"question": RunnablePassthrough(), "context": retriever}
| prompt_template
| client
```

这种写法透明，适合理解数据如何流动。

第二种是预制链：

```text
create_stuff_documents_chain
create_retrieval_chain
```

`代码/rag/rag_with_webpage.py` 用 `WebBaseLoader` 加载网页，用 `RecursiveCharacterTextSplitter` 切分，用 `Chroma` 建库，再组合 `create_stuff_documents_chain` 和 `create_retrieval_chain` 完成网页问答。

学习时建议先掌握手写 LCEL，再使用预制链。否则调试时很难判断问题出在加载、切分、检索还是 Prompt。

## 与已有 RAG 笔记连接

这节是 LangChain 版的 RAG 实践入口，已有 RAG 优化笔记更偏方法论：

| 方向 | 关联笔记 |
| --- | --- |
| 查询改写、Multi-Query、分解查询 | [[RAG相关/Pre-Retrieval预检索/查询优化/Multi-Query多路召回-痛点分析]] |
| 索引增强、摘要索引、父子块 | [[RAG相关/Pre-Retrieval预检索优化/Pre-Retrieval预检索优化]] |
| RAG-Fusion 和重排序 | [[RAG相关/Post-Retrieval后检索/RAG-Fusion-痛点分析]] |
| GraphRAG | [[RAG相关/GraphRAG/GraphRAG介绍]] |

课程的 `doc_and_llm.py` 是基础可运行流程，后续优化应从上述方向逐步加组件，而不是一开始就堆复杂架构。

## 安全和可靠性

官方 RAG 教程特别提醒 indirect prompt injection：外部文档可能包含“忽略系统提示”“泄露密钥”等恶意内容。做生产 RAG 时至少要注意：

| 风险 | 处理方式 |
| --- | --- |
| 文档中含恶意指令 | Prompt 中明确区分“资料内容”和“系统指令”，并做安全过滤 |
| 检索结果来源不可信 | 保留 metadata，输出引用来源 |
| 上下文过长 | 做压缩、重排序或摘要 |
| 权限越权 | 按用户权限过滤 metadata，再检索 |
| 回答幻觉 | 要求仅基于上下文回答，不足则说明无法确定 |

## 易错点

| 易错点 | 正确理解 |
| --- | --- |
| 文档加载后直接喂给模型 | 应先切分、加元数据、嵌入、检索 |
| chunk 越大越好 | 过大会稀释相关信息，过小会丢上下文 |
| 向量检索能解决所有召回 | 精确词和专有名词常需要 BM25 或 metadata 过滤 |
| 检索器返回结果就一定正确 | 还要重排序、去重、压缩和引用校验 |
| `create_retrieval_chain` 是黑盒 | 它只是组合检索器和文档处理链，核心流程仍要理解 |

## 补充资料

- [Build a RAG agent with LangChain](https://docs.langchain.com/oss/python/langchain/rag)
- [LangChain integrations](https://docs.langchain.com/oss/python/integrations/providers/overview)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| LangChain（3） | 属于技能 | [[AI Agent]] |
| LangChain（3） | 相关知识 | [[LangChain总结]] |
| LangChain（3） | 相关知识 | [[RAG相关/RAG]] |
| LangChain（3） | 前置知识 | [[LangChain（2）]] |
| LangChain（3） | 有示例代码 | 代码/rag/doc_and_llm.py |
| LangChain（3） | 有示例代码 | 代码/rag/rag_with_webpage.py |
| LangChain RAG | 应用于 | 企业知识库问答 |
| Retriever | 相关知识 | [[RAG相关/Pre-Retrieval预检索优化/Pre-Retrieval预检索优化]] |
| RAG 生成 | 相关知识 | [[RAG相关/Post-Retrieval后检索优化/Post-Retrieval后检索优化]] |
| LangChain RAG | 被考察于 | 如何解释 RAG 从文档加载到生成回答的完整链路 |

相关：[[LangChain（1）]] [[LangChain（2）]] [[LangChain（4）]] [[LangChain总结]] [[RAG相关/RAG]]
