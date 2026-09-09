---
okf_version: "0.2"
type: Tutorial
title: Runbook 与 Playbook 写作教程
description: 从零掌握 IT 运维场景下 runbook 和 playbook 的结构化写作方法：runbook 的 8 组件模板 + 9 条设计原则 + 四级自动化路径；playbook 的角色-沟通框架 + 事件类型专属化。
tags: [runbook, playbook, 运维, ITIL, SRE, NIST 800-61, 事件响应, 自动化成熟度, 写作指南]
generated: { by: "reference_agent/trae-research-agent", at: "2026-09-09T10:00:00+08:00" }
status: stable
stale_after: 2029-09-09
sources:
  - id: s11
    title: Stew.so 9 Best Practices for Writing On-Call Runbooks（2025-12-04）
    url: https://stew.so/blog/runbook-best-practices
  - id: s12
    title: Docsio Runbook Template: 8 Essential Components（2026-04-12）
    url: https://docs.io/templates/runbook
  - id: s13
    title: DevOps AI Toolkit Runbook Automation Maturity Model（2026-06-14）
    url: https://devops-ai-toolkit.io/runbook-automation
  - id: s14
    title: NIST SP 800-61 Rev. 3 Computer Security Incident Handling Guide（2025-04-03）
    url: https://csrc.nist.gov/pubs/sp/800/61/r3/final
  - id: s15
    title: CISA Federal Incident Response Playbook
    url: https://www.cisa.gov/incident-response-playbook
  - id: s16
    title: Upstat.io Runbook Version Management Best Practices（2025-10-07）
    url: https://upstat.io/blog/runbook-version-management
  - id: s17
    title: Valydex NIST SP 800-61 Rev. 3 Key Changes（2026-02-21）
    url: https://valydex.com/nist-sp-800-61-rev-3
  - id: s18
    title: Tomoda Hinata Idempotent Containment in Incident Response（2026-06-28）
    url: https://hinata.dev/posts/idempotent-containment
  - id: s19
    title: CalmOps Agentic DevOps: The Road to Autonomous Operations（2026-05-22）
    url: https://calmops.io/agentic-devops
  - id: s20
    title: 腾讯云 LLM + Runbook 智能运维架构实践（2025-12-13）
    url: https://cloud.tencent.com/developer/article/llm-runbook-ops
---

```{note}
本教程面向 IT 运维工程师、SRE 团队负责人及技术写作者。前置阅读建议：[概念 04：runbook / playbook / SOP 辨析](../concepts/04-runbook-playbook-sop.md) 与 [事实清单 facts.md](../facts.md)。
```

# Runbook 与 Playbook 写作教程

> **一句话摘要**：Runbook 是把已知故障的修复步骤写下来，供凌晨被告警叫醒的人照做；Playbook 是在大型事件中协调多人多部门的沟通框架。前者重"步骤清晰"，后者重"角色明确"。两者分工：runbook 处理可预测的技术故障，playbook 处理不可预测的大型事件。

## 一、选型：什么场景写 runbook，什么场景写 playbook

| 维度 | Runbook | Playbook |
|------|---------|----------|
| 问题性质 | 已知故障模式，有明确根因与修复步骤 | 新型/复合型事件，根因不清晰，需多方协作探索 |
| 执行者 | 单个人（On-Call 工程师） | 多角色团队（IC、技术、沟通、法务、管理层） |
| 核心结构 | 步骤 + 命令 + 验证 | 角色 + 沟通节奏 + 决策权限 |
| 时效要求 | 秒～分钟级（MTTR 导向） | 小时～天级（协调导向） |
| 典型场景 | 数据库宕机、磁盘满、服务重启 | 数据泄露、大规模舆情、并购整合 |

> **原则**：能用 runbook 解决的问题，不要写 playbook；只有涉及多角色协调、根因不明、无法预定义路径的场景才用 playbook。

## 二、Runbook 写作：8 组件模板

### 2.1 模板骨架

```markdown
# [Task ID]：[简明故障描述]

## 触发条件（When to run）
- 告警来源：[告警平台/渠道]
- 告警链接：[直链到告警详情]
- 严重度：[P0/P1/P2/P3]
- 手动触发判定：[什么情况下手动启动]

## 前置条件（Prerequisites）
- 所需权限：[例如 kubectl edit、生产数据库 write 权限]
- 环境准备：[例如切换到生产集群、备份当前状态]
- 工具依赖：[例如 ansible、kubectl、curl]

## 诊断步骤（Diagnostic）
> 如果根因不明，按以下顺序排查（最常见原因排最前）：
1. [步骤描述] —— 命令：`[可直接粘贴的命令]`
2. [步骤描述] —— 命令：`[命令]`
   - 预期输出：[正常情况下的输出示例]
   - 异常则进入：[跳转到下一步或 escalation 路径]

## 修复步骤（Remediation）
> 已知根因后的修复操作：
1. [步骤描述]（Why：[说明这一步的目的是什么]）
   - 命令：`[可直接粘贴]`
2. [步骤描述]
   - 命令：`[可直接粘贴]`

## 验证步骤（Verification）
- [ ] 执行：`[验证命令]`，预期输出：[...]
- [ ] 检查：[URL/监控面板链接]，确认指标恢复正常
- [ ] 等待：[X 分钟] 后告警自动消除

## 升级路径（Escalation）
- 若 [X 分钟] 内未恢复 → 通知 [角色/联系人]
- 若 [Y 条件] → 升级到 [P0 响应通道]
- IC 联系方式：[Slack/电话]

## 回滚指引（Rollback）
- 如修复后出现问题，执行：
  1. `[回滚命令]`
  2. 验证：`[回滚验证命令]`

## 备注
- 变更记录：[Git log 链接或 PR 编号]
- 上次验证日期：[YYYY-MM-DD]
```

### 2.2 Stew.so 9 条设计原则（写前必过）

| # | 原则 | 检查方式 |
|---|------|---------|
| 1 | **写 3am 读者**——假定读者凌晨、睡眠不足、有压力 | 请同事在正常状态下读一遍，看是否有需要"想一下"的步骤 |
| 2 | **最常见原因排最前** | 按过去 6 个月同类告警的频次排序，不按计划性排 |
| 3 | **包含 Why**——每个关键步骤说明意图 | 检查步骤前是否有"（Why：…）"标注 |
| 4 | **命令可直接粘贴执行**，非截图 | 粘贴到终端测试，确保无多余空格或特殊字符 |
| 5 | **写验证步骤**——告诉读者如何知道修好了 | 验证步骤不可省略；缺少验证 = 没有结束信号 |
| 6 | **明确升级触发条件**——何时停止自行处理 | 设定具体时间点或条件，不用"严重时"等模糊词 |
| 7 | **告警直链到对应 runbook** | 告警平台配置 webhook 或直接链接到文档 |
| 8 | **Git 版本控制** | 所有变更走 PR，禁止直接 push |
| 9 | **定期评审** | 季度评审会 + 90 天无触发告警自动归档（F-039） |

### 2.3 4 类 Runbook 的分场景写法

| 类型 | 用途 | 写法要点 |
|------|------|---------|
| **Diagnostic**（诊断） | 定位根因，如查日志定位故障组件 | 重点在排查树：每个分支给出判断标准与下一步 |
| **Remediation**（修复） | 修复已知故障，如重启服务 | 重点在命令准确性与验证步骤 |
| **Deployment**（发布/回滚） | 滚动升级、灰度发布、紧急回滚 | 重点在回滚路径，每一步都要有反向操作 |
| **Maintenance**（计划性运维） | 磁盘清理、证书更新、备份验证 | 重点在频率与前置检查，避免遗漏 |

> **关键规则**：每个 runbook 只对应一个故障模式。多个场景混合的 runbook 是 SOP debt 的典型来源（F-035）。

## 三、Playbook 写作：角色-沟通框架

### 3.1 与 Runbook 的根本区别

Playbook 不需要写"第 1 步做什么，第 2 步做什么"——因为事件本身不可预测。Playbook 的结构化输入是：

1. **角色分工（RACI）**：谁负责决策、谁负责执行、谁负责沟通
2. **沟通节奏**：什么时间向谁报告，用什么渠道
3. **决策权限**：哪些动作可以自主决定，哪些必须升级
4. **事件类型专属**：不同事件类型（数据泄露、服务大面积宕机、合规检查）有专属 playbook，不能用一套通用模板

### 3.2 CISA 联邦 IR Playbook 4 阶段模板

```markdown
# [事件类型] Incident Response Playbook

## 阶段 1：Preparation（准备）
- 资源清单：[关键系统、联系人、工具访问权限]
- 角色定义（RACI）：
  | 角色 | 职责 | 联系人 |
  |------|------|--------|
  | IC（Incident Commander） | 总体协调、决策升级 | [姓名/Slack] |
  | Technical Lead | 技术分析与修复 | [姓名] |
  | Comms Lead | 对内/对外沟通 | [姓名] |
  | Legal Lead | 合规与法务评估 | [姓名] |
  | Exec Sponsor | 高层决策授权 | [姓名] |
  | BC Lead | 业务连续性保障 | [姓名] |

## 阶段 2：Detection & Analysis（检测与分析）
- 告警来源：[SIEM/SOAR/用户报告]
- 初判 checklist：[3-5 个快速定性问题]
- 严重度分级标准（incident declaration criteria）：
  | 级别 | 判定标准 | 响应节奏 |
  |------|---------|---------|
  | P0 | 核心服务中断 / 数据泄露 | 5 分钟内 IC 到位，15 分钟全员启动 |
  | P1 | 非核心服务降级 | 15 分钟内 IC 到位 |
  | P2 | 局部影响，有 workaround | 1 小时内响应 |
  | P3 | 信息确认中，暂不影响服务 | 正常工作时间处理 |

## 阶段 3：Containment / Eradication & Recovery（封禁/清除/恢复）
- 封禁策略（idempotent containment）：
  - 可重复执行的操作：[软封禁、降级、限流]
  - 需人工确认的操作：[防火墙封禁、实例终止] ← 禁止自动执行
  - 执行前必须 dry-run 验证影响范围
- 清除步骤：[根据事件类型定制]
- 恢复验证：[业务指标恢复标准]

## 阶段 4：Post-Incident（事后复盘）
- 强制复盘时间：事件关闭后 48 小时内
- 复盘文档模板：[时间线 / 根因 / 响应得失 / playbook 修订项]
- 修订触发条件：发现 playbook 中未覆盖的协调盲点
```

### 3.3 版本管理（5 条实践）

| 实践 | 做法 |
|------|------|
| Git 管理 | 所有变更走 PR，禁止直接 push 到主分支 |
| 语义化版本 | Major=架构变更、Minor=向后兼容增强、Patch=修复错误 |
| 双日期追踪 | Last Updated（上次修改）+ Last Validated（上次验证生效）分开记录 |
| 季度评审会 | 每季度集中 review 所有 in-use playbook |
| 90 天无触发归档 | 超过 90 天未被引用/触发的 playbook 自动进入归档队列 |

## 四、自动化成熟度路径：从文档到 AI 可执行

### 4.1 四级分层与推进策略

```
Level 1  Documentation      ← 纯文本步骤，MTTR 基线
    ↓  把文字转为可执行命令
Level 2  Script Collection   ← 脚本集合，复制粘贴式
    ↓  引入编排平台
Level 3  Orchestrated Workflows ← Ansible AWX / Rundeck 等平台编排
    ↓  AI 解析 + 策略约束
Level 4  AI-Executable Automation  ← 机器可读结构化触发器，LLM 驱动
```

> **行业数据**：从 Level 1 推进到 Level 3+，MTTR 可降低 40–60%（F-036）。

### 4.2 安全护栏：不可跳过的阶段

| 阶段 | 允许 AI 做的事 | 不允许 AI 做的事 | 护栏 |
|------|-------------|---------------|------|
| Shadow Mode | 并行观察、输出修复建议 | 执行任何操作 | 人审批输出，AI 不执行 |
| 试点 | 在 Top-10 告警类型中自动修复 | 破坏性操作（终止实例、删库） | 限定范围，policy-as-code 校验 |
| 全面自治 | 所有非破坏性操作自动执行 | 无需人工确认的不可逆操作 | black box recorder（操作日志不可篡改） |

### 4.3 腾讯云 LLM + Runbook 架构参考

```
告警触发 → LLM 分析（读懂告警、判断场景、选择流程）
         → 生成修复计划（调用对应 runbook）
         → Runbook/脚本执行（"干"的部分）
         → 结果反馈给 LLM
         → LLM 再决策（是否需要升级或继续）
         → 闭环
```

> 该架构已在生产环境落地，MTTR 平均降低约 50%（F-043）。核心思想：**LLM 负责"想"，Runbook 负责"干"**。

## 五、Runbook vs Playbook 对照速查

| 维度 | Runbook | Playbook |
|------|---------|----------|
| 写作对象 | 已知故障模式 | 不可预测的大型事件 |
| 核心结构 | 步骤 + 命令 + 验证 | 角色 + 沟通节奏 + 决策权限 |
| 读者状态 | 单个人，凌晨告警 | 多角色团队，协同响应 |
| 自动化路径 | L1→L2→L3→L4 渐进推进 | 不适合全自动，重在协调框架 |
| 验收标准 | MTTR 降低 | 响应时间 / 协调盲点减少 |
| 失败模式 | 命令过时 / 路径过长 | 角色不清 / 升级路径缺失 |

## 六、写前自检清单

在发布 runbook 或 playbook 前，逐项检查：

**Runbook 自检（Stew.so 9 条简化版）**：
- [ ] 命令可直接粘贴，不是截图
- [ ] 每个步骤有 Why 说明
- [ ] 验证步骤存在且可执行
- [ ] 升级条件明确（时间或触发条件）
- [ ] 最常见问题排最前
- [ ] 告警平台已配置直链
- [ ] Git 版本控制已启用
- [ ] 上次验证日期已填写

**Playbook 自检**：
- [ ] RACI 角色矩阵完整（6 个关键角色至少 3 个有明确 owner）
- [ ] 事件类型专属（不是一套用所有场景）
- [ ] 严重度分级标准清晰（P0-P3 对应不同响应节奏）
- [ ] 封禁操作含 dry-run 要求
- [ ] 复盘时间窗口已设定（48 小时内）
- [ ] 修订触发条件已定义

## 参考

- [F-033～F-036](../facts.md#九、IT-运维专项：Runbook-设计原则) — Runbook 设计原则与四级自动化
- [F-037～F-041](../facts.md#十、IT-运维专项：Playbook-与事件响应框架) — NIST / CISA 事件响应框架
- [F-042～F-043](../facts.md#十一、IT-运维前沿：Agentic-DevOps-与-AI-可执行-Runbook) — Agentic DevOps 路径
- [概念 04：runbook / playbook / SOP 辨析](../concepts/04-runbook-playbook-sop.md)
- [洞察 6/7/8](../insights.md) — 本教程背后的设计哲学
