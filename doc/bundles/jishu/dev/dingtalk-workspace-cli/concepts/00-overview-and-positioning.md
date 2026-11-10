---
okf_version: "0.2"
type: Concept
title: "定位与全景：一个把接口契约当交付物的钉钉工作区 CLI"
description: "dws 是什么、为什么要把 MCP 能力编译成静态命令面、双表面（CLI + Schema）如何同源，以及 20 个服务域的全景划分"
sources:
  - id: repo
    resource: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
  - id: readme
    resource: "README.md"
  - id: architecture
    resource: "docs/architecture.md"
facts: [F-001, F-003, F-004, F-009, F-010, F-011, F-012, F-013, F-014]
---

# 00 · 定位与全景

> 核心判断：dws 不是「把钉钉 API 包一层脚本」，而是把**接口契约**本身做成可版本化、可 diff、可审计的交付物，并让人类 CLI 与 AI Agent 读同一份真相（F-010、F-025）。

## 1. 一句话定位

钉钉工作区命令行工具（`dws`），用一条命令覆盖通讯录、群聊、日程、待办、审批、考勤、文档、表格、云盘、邮件、会议纪要等 20 个服务域，同时面向两类消费者：**人**（Cobra 命令行）与 **Agent**（机器可读 Schema）（F-009、F-013）。

版本坐标固定为本束核验时的 `1.0.68-beta.1`（2026-11-06，HEAD `c631e4fb`，F-003、F-004）。

## 2. 它要解决的真实问题

直接让 Agent 连 MCP 端点会暴露三个工程问题：

| 问题 | 动态 MCP 的现状 | dws 的处置 |
|------|----------------|-----------|
| 不可 diff | `tools/list` 是运行时结果，接口一变，行为静默漂移，CI 抓不到 | 命令面在构建期静态展开，生成物进版本库，用 `git diff --exit-code` 守护（F-012、F-029） |
| 不可审计 | Agent 自主决定调什么工具，人类无法预读意图 | 每个叶命令带 effect / risk / confirmation 元数据，写操作默认要确认（F-021、F-048） |
| 不确定 | 同一意图可能命中多个工具，模型选择不稳定 | 命令名即语义（`dws <product> <resource> <verb>`），Schema 限定可选项（F-015、F-032） |

用一句话概括：**把「调用什么」从运行时的概率选择，提前到构建期的确定声明。**

## 3. 双表面：同一注册表，两种读者

```text
        internal/syncdata（端点数据，唯一来源）
                    │
                    ▼
        CommandRegistry（叶 Spec 注册表）
           │                    │
           ▼                    ▼
    Cobra 命令树           Schema 输出器
   （给人：help/补全）    （给机器：参数/约束/风险）
```

- 人类表面：`dws chat message send --help`，看示例、看必填项。
- 机器表面：`dws schema <path>`，看结构化参数、约束、效果与风险（F-030、F-031）。
- 关键约束：两套表面**不得各写一份**；Schema 必须从 registry 派生（F-023、F-025）。

> **洞察**：很多 CLI 把「帮助文档」当附属品，dws 把它当**主产品**——因为 Agent 的第一读者不是人，而是推理时的上下文窗口。Schema 的质量直接决定 Agent 调用的成功率。

## 4. 能力面全景（20 个服务域）

按业务对象而非 API 分组，可以分成四簇：

| 簇 | 服务域 | 典型用途 |
|----|--------|---------|
| 沟通与协作 | `contact`、`chat`、`ding`、`live` | 找人、发群消息、DING 提醒、直播 |
| 日程与事务 | `calendar`、`todo`、`oa`、`attendance`、`report` | 排会、待办、审批、考勤、日志汇报 |
| 内容与文档 | `doc`、`sheet`、`aitable`、`wiki`、`drive`、`whiteboard`、`minutes`、`mail` | 写文档、改表格、建多维表、知识库、云盘、白板、纪要、邮件 |
| 平台与开发 | `devdoc`、`aisearch`、`api`、`dev` | 开放平台文档、AI 搜索、原始 API 直连、本地开发桥接 |

数字口径需要区分（见 [verification.md](../references/verification.md) 冲突 C-1）：

- **20** 是 README 列举的服务域全集（F-013）；
- **13 个产品 / 180 条命令**是 `pre` 环境命令索引快照（F-014）。

不要用一个数字覆盖另一个，二者维度不同。

## 5. 三个「不适用」

1. **追求零学习成本的终端用户**：dws 仍是命令行，图形客户端更合适。
2. **需要离线操作内部系统的场景**：dws 的价值在钉钉云端能力，不替代内网工具。
3. **只想一次性调某个未支持接口**：直接走 `dws api`（F-058），但那样会绕过安全元数据，不适合作为长期集成方案。

## 6. 读完本束你应该能回答

- 为什么静态命令面比动态 MCP 发现更适合 Agent？（→ 02）
- 一条命令背后有哪些契约字段？（→ 01）
- 登录态、多组织、密钥存在哪里？（→ 04）
- 怎样让 Agent 安全地写数据？（→ 06、07）

## 延伸

- 架构细节：[01-command-contract-model.md](01-command-contract-model.md) → [02-static-endpoint-pipeline.md](02-static-endpoint-pipeline.md)
- 上手实践：[examples/00-install-and-first-login.md](../examples/00-install-and-first-login.md)
- 事实出处：[references/facts.md](../references/facts.md)