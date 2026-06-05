## 简介

Faithfulness（忠实度）、Answer Relevancy / Response Relevancy（答案/响应相关性）、Context Recall（上下文召回率）、Context Precision（上下文精度）这四类指标之间存在协同关系。RAG 的整体性能是检索器和生成器共同作用的结果，不能只看单一指标。

- 检索器是生成器的基础：Context Recall 和 Context Precision 直接决定输入给生成器的上下文质量。
- 理想状态：高召回率 + 高精度。检索器既能找全相关信息，又尽量少引入无关信息。
- 现实权衡：在大规模数据集中，召回率和精度往往难以兼得。提高召回率可能引入更多噪声，追求更高精度又可能漏掉部分关键信息。

当 Context Recall 和 Context Precision 一高一低、难以单独判断检索效果时，可以引入 F1 分数做综合评估。F1 是精度和召回率的调和平均值：

```text
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

## 典型痛点和权衡策略

很多业务场景，如技术文档问答或客服，倾向于优先保证信息不遗漏。因此，“高召回率 + 中等精度”常常是可接受甚至更符合业务目标的选择。

- 生成器依赖高质量输入：Faithfulness 和 Answer Relevancy 的表现很大程度上取决于检索器提供的上下文。
- 如果上下文不完整（低 Context Recall），生成器可能因缺乏信息而无法给出完整或准确的答案，影响 Answer Relevancy，甚至可能被迫猜测，影响 Faithfulness。
- 如果上下文充满噪声（低 Context Precision），生成器可能难以聚焦关键信息，导致答案冗余、偏题，影响 Answer Relevancy；也可能错误地依据无关信息，影响 Faithfulness。

## 关系标记

| 主体             | 关系   | 客体                |
| -------------- | ---- | ----------------- |
| RAG应用效果评估痛点分析  | 属于技能 | [[RAG相关/RAG]]     |
| RAG应用效果评估痛点分析  | 前置知识 | [[RAG效果评估量化]]     |
| RAG应用效果评估痛点分析  | 相关知识 | [[RAG检索评估]]       |
| RAG应用效果评估痛点分析  | 相关知识 | [[RAG响应评估]]       |
| RAG应用效果评估痛点分析  | 相关知识 | [[RAG评估指标总结]]     |
| Context Recall | 相关知识 | Context Precision |
| Faithfulness   | 相关知识 | Answer Relevancy  |
| RAG应用效果评估痛点分析  | 应用于  | 技术文档问答项目          |
| RAG应用效果评估痛点分析  | 应用于  | 智能客服项目            |
