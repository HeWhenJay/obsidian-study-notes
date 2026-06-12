## 简介

GraphRAG 是一种把知识图谱、社区检测和 RAG 结合起来的检索增强生成方法。它不是简单地“把向量库换成图数据库”，而是在索引阶段从文本中抽取实体、关系和可选声明，构建图结构，再围绕社区生成层级化报告；查询阶段根据问题类型选择本地搜索、全局搜索或 DRIFT 搜索。

传统 RAG 的核心是语义相似度：文档切块、嵌入成向量，查询时找相似文本块，再拼接给大模型。它适合事实型、局部型问答，但对跨文档、跨实体、需要总体洞察的问题容易漏信息。GraphRAG 的价值在于补上“关系结构”和“全局主题”的视角。

## 适用场景

GraphRAG 更适合这些问题：

| 问题类型 | 示例 | 为什么适合 GraphRAG |
| --- | --- | --- |
| 全局总结 | 这批市场趋势报告里主要有哪几个竞争阵营？ | 需要跨多个社区报告综合 |
| 关系推理 | 爱因斯坦妻子的国籍是什么？ | 问题依赖实体之间的关系链 |
| 主题/阵营发现 | 文档集中有哪些主要人物、组织、事件线？ | 社区检测能把紧密相关实体聚成主题 |
| 长文档深度分析 | 这个故事的核心主题和关键冲突是什么？ | 全局搜索可利用高层社区摘要 |
| 跨块/跨文档证据整合 | 某个事件的前因后果是什么？ | 图结构能连接分散文本块 |

不适合把 GraphRAG 当作所有 RAG 的默认替代。若问题只是“某个条款是多少”“某个字段在哪里”，普通向量检索、BM25、元数据过滤和重排序通常更轻、更便宜。

## 知识图谱基础

知识图谱（Knowledge Graph，KG）也称语义网络，用图结构表示现实世界中的实体及其关系：

| 组成 | 含义 | GraphRAG 中的对应 |
| --- | --- | --- |
| Node / 节点 | 实体、概念、人物、地点、事件 | Entity |
| Edge / 边 | 两个节点之间的关系 | Relationship |
| 属性 | 实体或关系的描述、权重、来源 | description、weight、text_unit_ids |
| 子图 | 与某个问题相关的一组节点和边 | Local Search 上下文 |
| 社区 | 图中连接密集的一组实体 | Community |

知识图谱的关键不是“画图好看”，而是让系统知道实体之间如何连接，从而支持跨片段、跨文档的关系推理。

## 核心概念

| 概念 | 说明 |
| --- | --- |
| Document（文档） | 输入文档。GraphRAG 默认可处理 text、csv、json 等，课程示例使用 `input/book.txt`。 |
| TextUnit（文本块） | Document 切分后的片段，是实体、关系和声明抽取的基本单位。 |
| Entity（实体） | 从 TextUnit 中抽取的人物、组织、地点、事件或自定义实体类型。 |
| Relationship（关系） | 实体之间的边，包含 source、target、description、weight 等信息。 |
| Claim（声明） | 可选抽取结果，用于表达事实、主张、状态或事件。课程配置中 `extract_claims.enabled: false`，所以不是默认必有。 |
| Covariate（协变量） | GraphRAG 输出表里的补充结构化信息容器。默认协变量常对应 Claim。 |
| Community（社区） | 图中连接密集的实体群组，代表主题、故事线或概念集合。 |
| Community Report（社区报告） | LLM 对社区生成的结构化摘要，是 Global Search 的核心材料。 |
| Leiden 算法 | 社区检测算法，用于把图划分为层级社区。 |
| GraphML | 图结构导出格式，可用 Gephi、Cytoscape 等工具可视化。 |

## 工作流总览

GraphRAG 分为两个主要阶段：

```text
索引阶段：Document -> TextUnit -> Entity / Relationship / Claim -> Graph -> Community -> Community Report
查询阶段：Question -> Local / Global / DRIFT Search -> Answer
```

索引阶段负责把非结构化文本转成结构化图和摘要；查询阶段负责按问题类型选择合适的检索上下文。

## 索引阶段

### 1. 文本切分

课程 PPT 用“300 token、100 token overlap”讲解原理；实际配套 `settings.yaml` 中是：

```yaml
chunks:
  size: 1200
  overlap: 100
  group_by_columns: [id]
```

切分的目的不是简单减少长度，而是让后续 LLM 能在有限上下文里稳定抽取实体和关系。重叠用于减少边界处实体/关系丢失。

### 2. 提取实体和关系

课程配置：

```yaml
extract_graph:
  model_id: default_chat_model
  prompt: "prompts/extract_graph.txt"
  entity_types: [organization,person,geo,event]
  max_gleanings: 1
```

LLM 会从每个 TextUnit 中抽取：

| 输出 | 说明 |
| --- | --- |
| 实体 | 名称、类型、描述 |
| 关系 | 源实体、目标实体、关系描述、关系强度 |
| 描述 | 对实体和关系的简短说明，后续会合并和总结 |

`max_gleanings` 表示补充抽取次数。第一轮抽取后，GraphRAG 可继续询问模型是否还有遗漏实体和关系，以提高召回。

### 3. 构建知识图谱

GraphRAG 会将实体作为节点，关系作为边，合并成全局图谱。这个过程包含：

| 操作 | 作用 |
| --- | --- |
| 去重 | 合并重复实体和重复关系 |
| 标准化 | 统一实体名称、类型、格式 |
| 权重聚合 | 汇总关系强度 |
| 来源追踪 | 保留实体/关系来自哪些 TextUnit |

配套资料 `代码/GraphRAG构建点和边的原理.md` 记录了点边构建细节和实际输出示例。

### 4. 社区检测

构建知识图谱后，GraphRAG 使用 Leiden 社区检测算法识别实体社区。

社区层级可按 C0、C1、C2、C3 理解：

| 层级 | 含义 | 适合回答 |
| --- | --- | --- |
| C0 / C1 | 更高层、更概括的社区 | 全局主题、阵营、趋势 |
| C2 / C3 | 更低层、更具体的社区 | 某个实体、事件、关系细节 |

需要纠正一个常见误解：社区不是“文档目录”。社区来自实体关系图的连接密度，同一文档的内容可能分属不同社区，不同文档的实体也可能被聚到同一社区。

### 5. 社区报告

每个社区会生成 Community Report。它是 GraphRAG 做全局回答的关键，不只是图谱的附属说明。

报告通常包含：

| 内容 | 作用 |
| --- | --- |
| 社区主题 | 概括这一组实体的核心含义 |
| 关键实体 | 标明社区中重要节点 |
| 关键关系 | 解释实体间重要连接 |
| 发现/结论 | 支持后续全局问答的摘要证据 |

课程 PPT 将社区报告分为细节级、中等粒度、全局级摘要，可以理解为从低层社区到高层社区的层级总结。

## 查询阶段

GraphRAG 查询不是只有一种“图检索”。课程和官方文档都强调了 local、global、DRIFT 这些不同方法。

### Local Search（本地搜索）

Local Search 将图中与问题相关的实体、关系、协变量和原始文本块组合起来生成答案。

适合：

| 适合问题 | 示例 |
| --- | --- |
| 具体实体属性 | 洋甘菊的治疗特性是什么？ |
| 某个人物/组织/地点相关事实 | 某个角色和其他角色是什么关系？ |
| 需要原文证据的细节问答 | 某个事件在哪里发生？ |

它常使用较低层社区和更细粒度的实体关系信息，例如 C2/C3。

### Global Search（全局搜索）

Global Search 面向高层次问题，通过 map-reduce 搜索社区报告。

流程：

```text
Map：并行处理社区报告，生成中间响应和重要性分数
Reduce：按分数排序、合并高价值响应，生成全局答案
```

适合：

| 适合问题 | 示例 |
| --- | --- |
| 全局主题 | 这个故事的主题是什么？ |
| 阵营/趋势/冲突分析 | 报告里主要有哪些竞争阵营？ |
| 文档集整体总结 | 这一批材料的核心发现是什么？ |

需要纠正一个常见误解：Global Search 不是“把所有原文塞给模型”，而是优先利用社区报告做 map-reduce 汇总。

### DRIFT Search

DRIFT Search 可以理解为对 Local Search 的扩展：它利用社区信息扩大本地搜索的起点，使检索能覆盖更多事实类型，适合不完全匹配固定模板的复杂查询。

适合：

| 适合问题 | 说明 |
| --- | --- |
| 既有具体实体又要更多背景 | 先定位实体，再拓展相关社区 |
| 关系链不明确的问题 | 通过社区和实体邻域扩展搜索范围 |
| 比 local 更开放，但又不需要纯 global 的问题 | 在局部事实和社区摘要之间折中 |

## 实践配置

课程实践使用《圣诞颂歌》文本：

- 原始文本来源：[Project Gutenberg - A Christmas Carol](https://www.gutenberg.org/cache/epub/24022/pg24022.txt)
- 本地输入：`input/book.txt`
- 配套说明：`代码/README.md`
- 配置文件：`代码/settings.yaml`
- Prompt 目录：`代码/prompts/`

课程命令：

```bash
conda create -n graphrag python=3.11 -y
conda activate graphrag
pip install graphrag
graphrag init --root D:\graghrag
graphrag index --root D:\graghrag
graphrag query --root D:\graghrag --method local --query "这个故事的主题是什么?"
graphrag query --root D:\graghrag --method global --query "这个故事主题是什么?"
graphrag query --root D:\graghrag --method drift --query "这个故事主题是什么?"
```

配套配置使用 DashScope 兼容 OpenAI 接口：

| 配置项 | 课程值 |
| --- | --- |
| chat model | `qwen-coder-plus` |
| embedding model | `text-embedding-v1` |
| api_base | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| API Key 环境变量 | `GRAPHRAG_API_KEY` |
| vector store | LanceDB |
| output dir | `output` |
| cache dir | `cache` |

课程 README 提醒：`qwen-max` 在该环境下可能触发 `TypeError: Object of type ModelMetaclass is not JSON serializable`，示例改用 `qwen-coder-plus`。这更像是当时依赖和模型兼容问题，复现时应优先检查当前 GraphRAG 版本、provider 配置和模型 JSON 输出能力。

## 输出文件

索引完成后常见输出：

| 文件 | 含义 |
| --- | --- |
| `documents.parquet` | 输入文档记录 |
| `text_units.parquet` | 切分后的文本块 |
| `entities.parquet` | 实体节点 |
| `relationships.parquet` | 实体关系边 |
| `communities.parquet` | 社区检测结果 |
| `community_reports.parquet` | 社区报告 |
| `graph.graphml` | 可视化图结构文件 |
| `stats.json` | 索引统计 |
| `output/lancedb/` | 向量索引数据 |

配套 `代码/parquet.py` 用于读取 parquet 输出；`graph.graphml` 可导入 Gephi 可视化。课程还给了 Gephi 下载入口：[Gephi download](https://gephi.org/users/download/)。

## Gephi 可视化

GraphRAG 官网和课程都推荐用 Gephi 查看 `graph.graphml`：

1. 安装 Gephi。
2. 导入 `output/graph.graphml`。
3. 根据节点度、社区、边权重调整布局和颜色。

可视化的目标是辅助理解图结构，不是 GraphRAG 查询必须步骤。生产查询依赖的是索引文件、社区报告和检索流程。

## 增量更新

配套资料指出：添加新文档后重新运行 `graphrag index` 会利用 `cache/`，但不等于完全增量图更新。

| 部分 | 是否可复用 |
| --- | --- |
| 已处理文本块的 LLM 抽取 | 通常可从 cache 读取 |
| 新文档的分块和抽取 | 需要新增处理 |
| 图结构合并 | 需要重新构建 |
| 社区检测 | 需要重新运行 |
| 社区报告 | 受影响社区需要重新生成 |

因此可以说“有缓存加速”，但不要说“GraphRAG 原生支持完全无代价增量更新”。

## 纠错总结

| 容易写错 | 更准确的说法 |
| --- | --- |
| GraphRAG = 知识图谱 + RAG | 还包括社区检测、社区报告和多种查询策略 |
| GraphRAG 只用于图数据库检索 | Microsoft GraphRAG 的核心索引输出包含 parquet、LanceDB、GraphML 等，不必先上 Neo4j |
| Claim 是默认必开 | Claim / Covariate 是可选流程，课程配置里 `extract_claims.enabled: false` |
| 社区就是文档章节 | 社区来自图结构聚类，不等同于文档目录 |
| Global Search 检索原文块 | Global Search 主要 map-reduce 社区报告 |
| Local Search 适合全局总结 | Local Search 更适合具体实体和局部事实 |
| DRIFT 等同 Local | DRIFT 以社区信息扩展 Local 起点，适合更开放的复杂查询 |
| 只要问题复杂就必须 GraphRAG | 需要权衡构图成本、LLM 抽取成本和普通 RAG 优化方案 |

## 与其他 RAG 优化的关系

| 技术 | 侧重点 | 与 GraphRAG 的关系 |
| --- | --- | --- |
| Multi-Query | 扩展查询表达 | 可作为查询优化补充 |
| 父子索引 | 同时保留小块召回和大块上下文 | 可用于普通 RAG，也可与图索引思路结合 |
| 元数据过滤 | 先按结构字段筛选 | GraphRAG 中 metadata / text_unit_ids 也很重要 |
| RAG-Fusion | 多路召回后融合排序 | 可补足 local/global 之外的召回策略 |
| GraphRAG | 关系结构和全局社区报告 | 更适合跨实体、跨文档和整体洞察 |

## 代码索引

| 资料 | 说明 |
| --- | --- |
| `代码/README.md` | 课程实践命令和模型配置说明 |
| `代码/settings.yaml` | GraphRAG 项目配置 |
| `代码/settings配置示例.png` | settings 中模型配置截图 |
| `代码/GraphRAG构建点和边的原理.md` | 点边构建流程、输出文件和增量说明 |
| `代码/parquet.py` | parquet 输出查看脚本 |
| `代码/prompts/extract_graph.txt` | 实体和关系抽取 Prompt |
| `代码/prompts/community_report_text.txt` | 社区报告文本 Prompt |
| `代码/prompts/local_search_system_prompt.txt` | Local Search Prompt |
| `代码/prompts/global_search_map_system_prompt.txt` | Global Search Map Prompt |
| `代码/prompts/global_search_reduce_system_prompt.txt` | Global Search Reduce Prompt |
| `代码/prompts/drift_search_system_prompt.txt` | DRIFT Search Prompt |

## 补充资料

- [Microsoft GraphRAG documentation](https://microsoft.github.io/graphrag/)
- [GraphRAG indexing architecture](https://microsoft.github.io/graphrag/index/architecture/)
- [GraphRAG query overview](https://microsoft.github.io/graphrag/query/overview/)
- [Gephi download](https://gephi.org/users/download/)

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| GraphRAG | 属于技能 | [[RAG]] |
| GraphRAG | 前置知识 | RAG |
| GraphRAG | 前置知识 | 知识图谱 |
| GraphRAG | 相关知识 | [[Pre-Retrieval预检索优化]] |
| GraphRAG | 相关知识 | [[Post-Retrieval后检索优化]] |
| GraphRAG | 相关知识 | Entity |
| GraphRAG | 相关知识 | Relationship |
| GraphRAG | 相关知识 | Community Report |
| GraphRAG | 相关知识 | Local Search |
| GraphRAG | 相关知识 | Global Search |
| GraphRAG | 相关知识 | DRIFT Search |
| GraphRAG | 有示例代码 | 代码/settings.yaml |
| GraphRAG | 有示例代码 | 代码/GraphRAG构建点和边的原理.md |
| GraphRAG | 有示例代码 | 代码/prompts/extract_graph.txt |
| GraphRAG | 被考察于 | GraphRAG 适合解决哪些传统 RAG 不擅长的问题 |
| Global Search | 应用于 | 全局主题总结 |
| Local Search | 应用于 | 实体细节问答 |
| DRIFT Search | 应用于 | 开放复杂查询 |
| Community Report | 相关知识 | Leiden 社区检测 |

相关：[[RAG]] [[Pre-Retrieval预检索优化]] [[Post-Retrieval后检索优化]]
