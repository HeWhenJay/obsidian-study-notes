## Ragas

### 简介

Ragas 是常用的 RAG 自动化评估库，适合在已有测试集后，对整个 RAG 管道（RAG Pipeline）做离线量化评估。它的核心价值是提供一组面向检索质量和生成质量的指标，帮助定位问题来自检索器还是生成器。

Ragas 的评估通常需要把 RAG 运行过程中的关键信息整理成数据集，例如用户问题、模型回答、检索上下文和参考答案。评估器本身常使用 LLM 或 embedding 模型进行打分，因此评估结果会受到评估模型、提示词、数据集质量和版本 API 的影响。

Ragas 支持 LangChain 和 LlamaIndex 等框架集成。

### 常见评估指标

- 检索质量：Context Precision（上下文精度）、Context Recall（上下文召回率）。
- 生成质量：Faithfulness（忠实度）、Answer Relevancy / Response Relevancy（答案/响应相关性）。

Ragas 的 Context Precision 更偏向检索排序质量：它关注相关上下文是否排在更靠前的位置，而不是简单计算“上下文中相关信息数量 / 上下文总信息数量”。后者可以作为业务上的简化理解，但不能完全等同于 Ragas 的实现。

### 使用步骤

1. 准备评估数据集。常见字段包括 question / user_input、answer / response、contexts / retrieved_contexts、ground_truth / reference，具体字段名要以当前安装的 Ragas 版本为准。
2. 构造评估器并选择指标。代码展示：[[评估器代码]]
3. 执行评估，得到各指标分数；如有需要，再导出为 CSV 或表格用于对比不同版本的 RAG 效果。

## TruLens

### 简介

TruLens 更偏向 RAG/LLM 应用的可观测性、调试和在线追踪，常用于开发阶段记录调用链，并通过反馈函数观察应用质量。

TruLens 的 RAG Triad 通常包含三类评估：Context Relevance（上下文相关性）、Groundedness（回答是否有上下文依据）和 Answer Relevance（答案是否回答问题）。它与 Ragas 都能做评估，但 TruLens 更强调过程追踪和迭代调试。

TruLens 同样支持 LangChain 和 LlamaIndex。

## 关系标记

| 主体 | 关系 | 客体 |
| --- | --- | --- |
| RAG常用评估工具 | 属于技能 | [[RAG相关/RAG]] |
| RAG常用评估工具 | 前置知识 | [[RAG效果评估量化]] |
| RAG常用评估工具 | 有示例代码 | [[评估器代码]] |
| RAG常用评估工具 | 相关知识 | [[RAG评估指标总结]] |
| Ragas | 相关知识 | [[RAG检索评估]] |
| Ragas | 相关知识 | [[RAG响应评估]] |
| TruLens | 相关知识 | [[RAG响应评估]] |
| RAG常用评估工具 | 应用于 | RAG离线评估项目 |
