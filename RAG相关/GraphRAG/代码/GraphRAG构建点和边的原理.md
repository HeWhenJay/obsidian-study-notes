# GraphRAG 构建点和边的原理详解

## 概述

GraphRAG（Graph Retrieval-Augmented Generation）通过大语言模型（LLM）从文本中提取实体（节点/点）和关系（边），构建知识图谱。这个项目使用的是微软的GraphRAG框架。

## 核心流程

### 1. 文本分块（Chunking）

**配置**（settings.yaml）：
```yaml
chunks:
  size: 1200          # 每个文本块的大小
  overlap: 100        # 文本块之间的重叠部分
  group_by_columns: [id]
```

- 将输入文档分割成大小为1200字符的文本块
- 相邻文本块之间有100字符的重叠，确保上下文连贯性
- 这些文本块是后续实体提取的基本单位

### 2. 实体和关系提取（Extract Graph）

这是构建点和边的核心步骤。

#### 配置参数

```yaml
extract_graph:
  model_id: default_chat_model
  prompt: "prompts/extract_graph.txt"
  entity_types: [organization,person,geo,event]  # 定义要提取的实体类型
  max_gleanings: 1  # 最大补充提取次数
```

#### 提取过程

**步骤1：识别实体（构建"点"）**

LLM会从每个文本块中识别以下类型的实体：
- **organization**（组织）：公司、机构、团体等
- **person**（人物）：人名、角色等
- **geo**（地理位置）：国家、城市、地点等
- **event**（事件）：重要事件、活动等

每个实体包含：
- `entity_name`：实体名称（大写）
- `entity_type`：实体类型
- `entity_description`：实体的详细描述

**格式示例**：
```
("entity"<|>PROJECT GUTENBERG<|>ORGANIZATION<|>Project Gutenberg is a volunteer effort to digitize and archive cultural works)
```

**步骤2：识别关系（构建"边"）**

从识别出的实体中，找出所有明确相关的实体对，提取关系信息：
- `source_entity`：源实体名称
- `target_entity`：目标实体名称
- `relationship_description`：关系描述
- `relationship_strength`：关系强度（1-10的数值评分）

**格式示例**：
```
("relationship"<|>CHARLES DICKENS<|>A CHRISTMAS CAROL<|>Charles Dickens wrote A Christmas Carol<|>9)
```

#### Prompt工程

系统使用精心设计的prompt（`prompts/extract_graph.txt`）来指导LLM：

1. **明确的任务定义**：识别特定类型的实体和它们之间的关系
2. **结构化输出格式**：使用特殊分隔符（`<|>`和`##`）
3. **Few-shot示例**：提供3个详细的示例来指导LLM
4. **完成标记**：使用`<|COMPLETE|>`标记提取完成

### 3. 实际提取示例

从缓存文件可以看到实际的提取结果：

**提取的实体（点）**：
```
PROJECT GUTENBERG (ORGANIZATION)
CHARLES DICKENS (PERSON)
ARTHUR RACKHAM (PERSON)
J. B. LIPPINCOTT COMPANY (ORGANIZATION)
PHILADELPHIA (GEO)
NEW YORK (GEO)
A CHRISTMAS CAROL (EVENT)
```

**提取的关系（边）**：
```
CHARLES DICKENS -> A CHRISTMAS CAROL (wrote, strength: 9)
PROJECT GUTENBERG -> CHARLES DICKENS (provides works by, strength: 8)
J. B. LIPPINCOTT COMPANY -> PHILADELPHIA (published in, strength: 8)
ARTHUR RACKHAM -> A CHRISTMAS CAROL (illustrated, strength: 6)
```

### 4. 描述总结（Summarize Descriptions）

```yaml
summarize_descriptions:
  model_id: default_chat_model
  prompt: "prompts/summarize_descriptions.txt"
  max_length: 500
```

当同一个实体在多个文本块中出现时，会有多个描述。这一步将：
- 合并同一实体的多个描述
- 生成统一的、不超过500字符的综合描述
- 提高实体信息的一致性和完整性

### 5. 图谱最终化（Finalize Graph）

这一步会：
- **去重**：合并相同的实体和关系
- **标准化**：统一实体名称的大小写和格式
- **权重计算**：聚合关系强度
- **图结构优化**：构建最终的图谱结构

### 6. 社区检测（Create Communities）

```yaml
cluster_graph:
  max_cluster_size: 10
```

使用图聚类算法（如Leiden算法）将图谱划分为社区：
- 识别紧密连接的实体群组
- 每个社区代表一个主题或概念集群
- 用于后续的层次化检索

## 输出文件

构建完成后，生成以下文件：

1. **entities.parquet**：所有实体（点）的信息
   - id, name, type, description, text_unit_ids等

2. **relationships.parquet**：所有关系（边）的信息
   - source, target, description, weight等

3. **graph.graphml**：完整的图谱结构（GraphML格式）
   - 可用Gephi、Cytoscape等工具可视化

4. **communities.parquet**：社区检测结果
   - 实体的社区归属信息

5. **community_reports.parquet**：社区摘要报告
   - 每个社区的综合描述

## 技术特点

### 1. 基于LLM的提取
- **优势**：理解复杂语义，提取隐含关系
- **灵活性**：可以通过修改prompt调整提取策略
- **准确性**：使用few-shot learning提高提取质量

### 2. 增量式处理
- 逐个文本块处理，适合大规模文档
- 使用缓存机制（cache/extract_graph/）避免重复计算
- 支持断点续传

### 3. 多轮提取（Gleanings）
```yaml
max_gleanings: 1
```
- 第一轮提取后，可以再次询问LLM是否有遗漏的实体和关系
- 提高提取的完整性

### 4. 并发处理
```yaml
concurrent_requests: 25
async_mode: threaded
```
- 支持并发调用LLM API
- 大幅提升处理速度

## 工作流程总结

```
输入文档 (input/book.txt)
    ↓
文本分块 (chunks: 1200字符, overlap: 100)
    ↓
并行提取 (18个文本块)
    ↓
LLM提取实体和关系 (使用prompt模板)
    ↓
描述总结 (合并重复实体的描述)
    ↓
图谱最终化 (去重、标准化)
    ↓
社区检测 (识别实体群组)
    ↓
生成报告 (社区摘要)
    ↓
输出文件 (entities.parquet, relationships.parquet, graph.graphml等)
```

## 查询方式

构建完图谱后，支持三种查询方式：

1. **Local Search**：基于实体和关系的局部搜索
2. **Global Search**：基于社区报告的全局搜索
3. **DRIFT Search**：动态检索和过滤

## 增量更新：添加新内容怎么办？

### 当前状态（重要！）

**简短回答：目前需要重新运行索引，但不会完全重建。**

### 缓存机制

GraphRAG使用了智能缓存系统（`cache/`目录），当你添加新内容后重新运行 `graphrag index` 时：

#### ✅ 不会重复处理的部分（从缓存读取）：
1. **已有文档的分块**：旧文档不会重新分块
2. **已提取的实体和关系**：已处理的文本块不会重新调用LLM
3. **已生成的描述**：已有实体的描述不会重新生成

#### ⚠️ 需要重新计算的部分：
1. **图结构重建**：需要将新旧节点和边合并成完整图谱
2. **社区检测**：需要重新运行Leiden算法识别社区
3. **社区报告**：受影响的社区需要重新生成摘要

### 实际操作

```bash
# 1. 将新文档添加到input目录
cp new_document.txt input/

# 2. 重新运行索引（会利用缓存）
graphrag index --root D:\graghrag

# 结果：
# - 只处理新文档（约几分钟）
# - 旧文档从缓存读取（几秒钟）
# - 重建图结构和社区（取决于规模）
```

### 性能对比

假设原有10个文档，添加1个新文档：

| 操作 | 完全重建 | 使用缓存 |
|------|---------|---------|
| 文本分块 | 11个文档 | 1个新文档 |
| LLM提取 | 11个文档 | 1个新文档 |
| 图构建 | 全部 | 全部 |
| 社区检测 | 全部 | 全部 |
| **总时间** | ~100% | ~20-30% |

### 冲突处理

**问题**：如果新文档说"天空是红色的"，但旧文档说"天空是蓝色的"，会怎样？

**答案**：GraphRAG会同时保留两种信息：
- 创建两个独立的声明节点
- 在查询时，LLM会综合考虑所有信息
- 如果大部分文档说"蓝色"，查询结果会倾向"蓝色"，但会提及存在"红色"的说法

这类似于人类处理矛盾信息的方式：保留所有观点，根据权重和上下文做出判断。

### 未来功能（规划中）

Microsoft正在开发 `graphrag update` 命令，将支持：

1. **智能增量更新**：
   - 只将新实体添加到现有社区
   - 只重新计算受影响的社区
   - 设置阈值决定何时需要完全重建

2. **更高效的处理**：
   - 避免不必要的社区重新计算
   - 只对变化的社区重新生成摘要
   - 支持删除和编辑操作

3. **时间序列分析**：
   - 支持"过去24小时发生了什么"类型的查询
   - 追踪实体和关系的变化历史

### 最佳实践建议

#### 1. 小批量更新
```bash
# 不推荐：一次添加100个文档
# 推荐：分批添加，每次10-20个文档
```

#### 2. 定期清理缓存
```bash
# 如果发现结果异常，清理缓存重建
rm -rf cache/
graphrag index --root D:\graghrag
```

#### 3. 监控缓存大小
```bash
# 缓存会持续增长，定期检查
du -sh cache/
```

#### 4. 版本控制
```bash
# 重要更新前备份output目录
cp -r output/ output_backup_20260521/
```

### 实际示例

假设你的《圣诞颂歌》项目想添加《雾都孤儿》：

```bash
# 1. 下载新书
wget https://www.gutenberg.org/files/730/730-0.txt -O input/oliver_twist.txt

# 2. 重新索引
graphrag index --root D:\graghrag

# 3. 观察日志
# - 会看到"reading from cache"（读取缓存）
# - 只有oliver_twist.txt会显示"extract graph progress"
# - 最后会重新计算社区和报告

# 4. 查询测试
graphrag query --root D:\graghrag --method global \
  --query "比较这两个故事中的主角性格"
```

### 技术细节

缓存文件命名规则：
```
cache/extract_graph/chat_<hash>_v2
```
- `hash`：基于文本内容的SHA256哈希
- `v2`：缓存版本号
- 相同内容的文本块会生成相同的hash，从而复用缓存

## 总结

GraphRAG通过以下方式构建点和边：

**点（实体）的构建**：
- 使用LLM从文本中识别预定义类型的实体
- 提取实体的名称、类型和详细描述
- 合并和去重相同的实体

**边（关系）的构建**：
- 识别实体之间的明确关系
- 提取关系描述和强度评分
- 聚合和标准化关系信息

**增量更新策略**：
- 利用缓存机制避免重复处理旧内容
- 只对新文档进行LLM提取（节省时间和成本）
- 重建图结构和社区以整合新旧信息
- 智能处理冲突信息，保留多元观点

整个过程高度自动化，核心依赖于精心设计的prompt和强大的LLM能力，能够从非结构化文本中构建出结构化的知识图谱。虽然添加新内容需要重新运行索引命令，但通过缓存机制可以大幅减少处理时间（通常只需原时间的20-30%）。
