---
type: Concept
title: "选举与投票机制"
description: "Jupyter使用排序复选制(STV)进行选举，通过Apache STeVe计票工具实现，确保多候选人选举中的比例代表性和广泛共识。"
tags: [elections, voting, stv, ranked-choice, apache-steve, process-votes]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: elections
    resource: /references/elections-papers-source.md
    title: "选举与学术论文信源"
  - id: ec
    resource: /references/executive-council-source.md
    title: "执行委员会信源"
---

## 选举制度概述

Jupyter 的选举（尤其是 EC 选举）使用**排序复选制**（Ranked Choice Voting / Single Transferable Vote, STV），这是一种比例代表制投票方法，确保获胜者获得更广泛的社区支持，而非仅靠简单多数胜选。

## 选举流程（以 EC 选举为例）

```
1. EC 发出提名通知
       │
       ▼
2. UoC 成员提名候选人（可自荐）
       │
       ▼
3. EC 确认候选人资格和接受提名
       │
       ▼
4. 候选人撰写兴趣陈述、资质、经验
       │
       ▼
5. 通过 Google Forms 收集排序投票
       │
       ▼
6. process-votes.py 转换选票格式
       │
       ▼
7. Apache STeVe stv_tool.py 计票
       │
       ▼
8. 公布选举结果
```

## 投票数据格式

选票从 Google Forms 导出为 CSV 文件（`votes.csv`）：

- **第一行**：表头，候选人姓名在方括号中（如 `[Candidate Name]`）
- **后续行**：数字优先级排名（1=最高偏好，数字越大偏好越低）
- 未排名的候选人为空字符串
- 同一候选人不可有相同排名
- 排名可跳过（不影响转换）

示例：
```csv
[John Appleton],[Nancy Bass],[Carla Chang]
1,2,3
1,3,2
,1,2
```

## 计票工具链

### process-votes.py

仓库提供了 Python 脚本 `docs/elections/process-votes.py` 来将 Google Forms CSV 转换为 Apache STeVe 格式：

**输入**：`votes.csv`（Google Forms 导出）

**输出**：
1. `board_nominations.ini` - 候选人字母映射（最多26位候选人）
   ```ini
   [nominees]
   a: John Appleton
   b: Nancy Bass
   c: Carla Chang
   ```

2. `votedata.txt` - 投票数据，每行代表一票，格式为：
   ```
   [日期 时间] 随机哈希 偏好字母串
   ```
   例如：`[2022/11/30 14:28:14] d2327769... cadbfgeih`
   （偏好串按偏好降序排列，如 `abc` = 最偏好 A，其次 B，其次 C）

日期和随机哈希由脚本自动生成，用于满足 STeVe 验证器的格式要求，不代表实际投票时间或选民身份。

### Apache STeVe stv_tool.py

使用 Apache 软件基金会的 STeVe 计票脚本：

```bash
/path/to/steve/monitoring/stv_tool.py -s <席位数> votedata.txt
# 详细输出加 -v 参数
/path/to/steve/monitoring/stv_tool.py -s 2 -v votedata.txt
```

## STV 计票原理

可转移单票制（STV）的核心机制：

1. 选民按偏好排序候选人
2. 达到当选门槛（quota）的候选人当选
3.  surplus votes（超过当选门槛的多余选票）按比例转移给选民的下一偏好
4. 无人达到门槛时，淘汰得票最少的候选人，其选票转移
5. 重复直到所有席位填满

这种制度的好处：
- 避免"票仓分裂"（类似 FPTP 的 spoiler effect）
- 允许选民表达真实偏好而不必"策略性投票"
- 确保少数群体也能获得代表权

## 适用范围

排序复选制/STV 用于：
- EC 选举（UoC 和 EC 分别投票选举各自席位）
- Distinguished Contributors 选举
- 各机构内部有多选项的正式决策

简单二元决策（批准/否决）使用简单多数制。

## 反常识要点

- **不使用电子投票系统**：Jupyter 用 Google Forms + Python 脚本 + Apache STeVe 的组合来计票，而非依赖第三方选举平台。这保持了流程的透明性和可审计性。
- **随机哈希不代表选民身份**：votedata.txt 中的哈希是脚本生成的随机值，不包含可识别选民的信息，这是为了保护选民匿名性。
- **排名可跳过**：选民不需要对所有候选人排名，可以只排名自己支持的候选人，这不会导致选票无效。

## 相关概念

- [执行委员会（EC）](03-executive-council.md)
- [理事会联盟（UoC）与选举人团](08-union-of-councils.md)
- [决策制定流程](09-decision-making.md)
- [杰出贡献者制度](12-distinguished-contributors.md)
