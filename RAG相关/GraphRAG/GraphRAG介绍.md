## 简介
GraphRAG是传统RAG的一种扩展，它通过引入知识图谱（Knowledge Graph），增强信息检索能力和生成质量。

## 核心思想/技术
利用知识图谱中的结构化关系，辅助LLM更精准的理解查询意图，并在海量数据中找出最相关的信息进行生成。

1. 构建或使用已有的知识图谱：将实体与实体之间的关系以图的形式表现。
2. 图检索（Graph-based Retrieval）：根据用户问题，在知识图谱中查找相关的实体和关系。
3. 图增强生成（Graph-enhanced Generation）：结合图中检索到的路径或子图信息，生成更准确、连贯的回答。

这样的方法不仅依赖文本文档，还利用了实体之间的语义关联，提高回答的准确性和深度。

## 基本概念
- Document(文档)：系统中的输入文档，需放入项目文件夹提前准备好的input文件夹下。GraphRAG默认支持纯文本、CSV(Comma-Separated Values，即逗号分隔值)和JSON等输入格式；CSV中的每一行通常会被当作一个文档处理。
- TextUnit(文本块)：GraphRAG索引流程中由Document切分得到的文本块，用于后续实体、关系和声明抽取。
- Entity(实体)：从TextUnit中提取出的实体，通常是人物、地点、组织、事件，或者通过配置/提示词调优得到的自定义实体类型。
- Relationship(关系)：实体与实体之间的边，由索引流程从TextUnit中抽取或归纳得到。
- Claim(声明)：从文本块抽出的一个结构化事实判断，通常描述“某个实体对某个实体做了某种行为/发生了某种情况”，常带有时间范围和状态。Claim抽取是可选流程，并非默认一定开启。
- Covariate(协变量)：GraphRAG里输出表的通用容器名。默认情况下GraphRAG的协变量类型就是Claim(声明)。在GraphRAG这里，它更像是“附着在实体/关系/文本块旁边的补充结构化信息”。它不一定是图的主边，但可以在检索、社区报告、局部查询时作为额外证据进入上下文。
- Community Report(社区报告)：GraphRAG先从文本中抽取实体和关系构建图，再通过社区检测把连接紧密的实体聚成社区；Community Report就是LLM对某个社区生成的一份结构化总结，方便检索时快速理解该社区的主题和关键发现。
- Node(节点)：在GraphRAG输出图语境下，通常就是知识图谱里的节点，也就是Entity实体。

## 使用说明
### 创建并激活conda环境
使用conda单独管理GraphRAG运行环境：

`conda create -n graphrag python=3.11 -y`

`conda activate graphrag`

GraphRAG通常通过pip安装，但应安装在已经激活的conda环境中：

`python -m pip install --upgrade pip`

`python -m pip install graphrag`

检查GraphRAG命令是否可用：

`graphrag --help`

每次重新打开终端后，都需要先激活环境：

`conda activate graphrag`

### 前提准备
在已经激活的conda环境中，提前准备GraphRAG需要的文件夹：
在当前项目下创建一个自定义文件夹 `ragtest`，后续操作均在此目录下进行。

`mkdir ragtest`

`cd ragtest`

`mkdir input`


需要进行RAG的文本需要提前放入自定义文件夹下的input文件夹中，对于当前示例而言就是`ragtest/input` 文件夹

### 初始化
在已激活的conda环境中，执行以下命令初始化GraphRAG索引结构：

`graphrag init --root ./`

### 设置参数
编辑 `.env` 和 `settings.yaml` 文件，作用是设置APIkey、调用的模型名称等

### 优化提示词
运行以下命令对提示词进行调优（适合中文）：

`graphrag prompt-tune --root ./ --language Chinese --output prompts`

作用是可以让大模型更好的提取文档中的实体与关系。

### 构建索引
最后构建完整的知识图谱索引：

`graphrag index --root ./`

## 关系标记
| 主体               | 关系   | 客体               |
| ---------------- | ---- | ---------------- |
| GraphRAG         | 属于技能 | RAG              |
| GraphRAG         | 前置知识 | RAG              |
| GraphRAG         | 前置知识 | 知识图谱             |
| GraphRAG         | 相关知识 | Document         |
| GraphRAG         | 相关知识 | TextUnit         |
| GraphRAG         | 相关知识 | Entity           |
| GraphRAG         | 相关知识 | Relationship     |
| GraphRAG         | 相关知识 | Claim            |
| GraphRAG         | 相关知识 | Covariate        |
| GraphRAG         | 相关知识 | Community Report |
| GraphRAG         | 相关知识 | Node             |
| TextUnit         | 相关知识 | Document         |
| Entity           | 相关知识 | Relationship     |
| Claim            | 相关知识 | Covariate        |
| Community Report | 相关知识 | Entity           |
| Community Report | 相关知识 | Relationship     |
