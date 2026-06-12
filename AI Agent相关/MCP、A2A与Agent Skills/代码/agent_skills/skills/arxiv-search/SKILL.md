---
name: arxiv-search
description: 在 arXiv 预印本库中搜索物理学、数学、计算机科学、定量生物学及相关领域的论文。

---

# arXiv 搜索技能

此技能可访问 arXiv，这是一个免费的学术论文分发服务和开放获取的学术论文库，涵盖物理学、数学、计算机科学、定量生物学、定量金融、统计学、电气工程、系统科学和经济学等领域。
## ⚠️ 强制执行规则（Agent 必读）

1. **严禁委派**：不要调用 `task` 工具来处理此请求，必须由当前的 Agent 实例直接处理。
2. **工具链要求**：你必须按照以下顺序操作：
   - 第一步：使用 `read_file` 确认脚本路径。
   - 第二步：使用 `execute` 工具运行命令行。
## 何时使用此技能

以下情况可使用此技能：

- 查找期刊发表前的预印本和最新研究论文
- 搜索计算生物学、生物信息学或系统生物学领域的论文
- 获取与生物学相关的数学或统计方法论
- 查找应用于生物学问题的机器学习论文
- 获取可能尚未被 PubMed 收录的最新研究成果

## 如何使用此技能

此技能提供了一个 Python 脚本，用于搜索 arXiv 并返回格式化的结果。

### 基本用法

**注意：** 始终使用技能目录的绝对路径（如上系统提示符所示）。
你必须使用 `execute` 工具运行以下 bash 命令：

```bash
python [YOUR_SKILLS_DIR]/arxiv-search/arxiv_search.py "您的搜索查询" [--max-papers N]

```

将 `[YOUR_SKILLS_DIR]` 替换为系统提示符中技能目录的绝对路径（例如，`/Users/xiaoxia/Desktop/agent_skills/skills` 或完整的绝对路径）。

**参数：**

- `query`（必需）：搜索查询字符串（例如，“神经网络蛋白质结构”、“单细胞RNA测序”）
- `--max-papers`（可选）：要检索的最大论文数量（默认值：10）

### 示例

搜索机器学习论文：

```bash

python ~/.deepagents/agent/skills/arxiv-search/arxiv_search.py "deep learning drug discovery" --max-papers 5

```

搜索计算生物学论文：

```bash
python ~/.deepagents/agent/skills/arxiv-search/arxiv_search.py "protein folded prediction"

```

搜索生物信息学方法：

```bash
python ~/.deepagents/agent/skills/arxiv-search/arxiv_search.py "genome assembly algorithms"

```

## 输出格式

该脚本返回格式化的结果，包含：

- **Title**：论文标题
- **Summary**：摘要/概要文本

每篇论文为了便于阅读，各部分之间以空行分隔。

## 功能

- **相关性排序**：结果按与查询的相关性排序
- **快速检索**：无需身份验证即可直接访问 API
- **简洁界面**：输出清晰易懂
- **无需 API 密钥**：免费访问 arXiv 数据库

## 说明

- arXiv 尤其适用于：
- 计算机科学（cs.LG、cs.AI、cs.CV）
- 定量生物学（q-bio）
- 统计学（stat.ML）
- 物理学和数学
- 论文为预印本，可能未经同行评审
- 结果包含近期上传的论文和较早的论文
- 最适合生物学领域的计算/理论研究