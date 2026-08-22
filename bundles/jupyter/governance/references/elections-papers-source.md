---
type: Reference
title: "选举与学术论文文档源码"
description: "Elections 工具和 Academic Papers 流程文档的信源登记。"
tags: [reference, source, elections, voting, stv, academic-papers]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: elections-doc
    resource: https://github.com/jupyter/governance/blob/main/docs/elections/README.md
    title: "docs/elections/README.md"
  - id: papers-doc
    resource: https://github.com/jupyter/governance/blob/main/docs/papers.md
    title: "docs/papers.md"
---

# 选举工具与学术论文信源

**原始文件路径**：
- `docs/elections/README.md` - 选举计票脚本说明
- `docs/elections/process-votes.py` - 选票处理Python脚本
- `docs/papers.md` - 学术论文撰写流程

**内容摘要**：

**选举计票工具**：
- 将 Google Forms 导出的 CSV 选票文件转换为 Apache STeVe 的 `stv_tool.py` 可用格式
- 输出两个文件：`board_nominations.ini`（候选人字母映射）和 `votedata.txt`（投票数据）
- 投票使用可转移单票制（STV, Single Transferable Vote）/ 排序复选制
- CSV格式：第一行表头在方括号中包含候选人姓名；后续行是数字优先级排名
- 计票命令：`/path/to/steve/monitoring/stv_tool.py -s <席位数> votedata.txt`
- Python 3 环境，已知兼容 Python 3.10.8

**学术论文流程**：
- 原则：作者署名包容慷慨、标准明确可审计、流程公开、作者问责
- 作者排序：第一作者为"Project Jupyter"，个人作者按字母顺序排列（类似高能物理领域惯例）
- JOSS论文流程：协调人→开issue公告→在仓库中起草→邮件通知潜在作者→截止后提交
- JOSS作者资格（ICMJE标准）：实质贡献+最终版本批准+对工作准确性负责
- 传统学术论文：要求所有作者积极参与撰写/编辑
- 论文在 GitHub 上公开撰写

**关键事实锚点**：F-033, F-034
