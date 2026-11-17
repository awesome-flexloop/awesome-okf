---
okf_version: "0.2"
type: Reference
title: "Microsoft Agent Framework 核验报告（P0 对账与口径说明）"
description: "对 GA 日期、版本号、包名、Harness 压缩条件、CodeAct 基准、Copilot SDK 1.0 时间线等 P0 声明的逐项核验与差异说明"
tags: [核验, P0, 勘误, 版本, 时效]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T14:42:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T14:42:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: build2026
    resource: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/
  - id: learn
    resource: https://learn.microsoft.com/zh-cn/agent-framework/
  - id: github
    resource: https://github.com/microsoft/agent-framework
  - id: releases
    resource: https://api.github.com/repos/microsoft/agent-framework/releases
---

# 核验报告

## 核验方法

- 官方文档与 README 作为一手信源；博文声明逐条对照文档。
- 日期/版本用 GitHub Releases API 交叉核对（`published_at`，UTC）。
- 包名与安装命令对照 README、Learn 页面与仓库 `python/packages/` 目录。
- 厂商自述的成效数字（CodeAct 基准）单独标注，不升级为独立事实。

## P0 逐项结论

| # | 待核验声明 | 博文口径 | 核验结果 | 结论 |
|---|-----------|---------|---------|------|
| 1 | MAF 1.0 GA 日期 | 2026-04-02 | Releases：`python-1.0.0` 2026-04-02 16:16 UTC；`dotnet-1.0.0` 2026-04-02 16:43 UTC | ✅ 一致（F-002） |
| 2 | 由 AutoGen 与 Semantic Kernel 收敛而来 | 是 | Learn 概述：同一团队的直接继承者，合并两者能力 | ✅ 一致（F-003） |
| 3 | .NET 与 Python 概念/API 一致 | 是 | Learn 概述与 README 均如此表述；Go 另为预览 | ✅ 一致（F-005/F-012） |
| 4 | Python 安装包 | `agent-framework` | README、Learn 均确认；另有 `agent-framework-foundry` 子集包 | ✅ 一致（F-006） |
| 5 | .NET 安装包 | 未在博文展开 | README：`Microsoft.Agents.AI`；Foundry 需 `Microsoft.Agents.AI.Foundry` | ✅ 补齐（F-007） |
| 6 | Harness 单方法创建 | `chatClient.AsHarnessAgent(...)` / `create_harness_agent(...)` | Learn Harness 页与 get-started 第 6 步一致 | ✅ 一致（F-035/F-100） |
| 7 | 自动上下文压缩 | 博文称“监视 token 用量并中途压缩” | Learn 能力矩阵：.NET/Python 需提供令牌限制或自定义策略才启用；Go 需显式组合 provider | ⚠️ 口径需限定（F-037） |
| 8 | FileMemoryProvider 存储路径 | `agent-file-memory/{session}/` | 博文独有细节，Learn 未给路径模板 | ⚠️ 单源（F-040） |
| 9 | Shell 执行仅 .NET | 是 | Learn 工具页与 Harness 页均将 Shell 执行标为 .NET only / 沙箱 `ShellExecutor` | ✅ 一致（F-040/F-045） |
| 10 | 后台代理实验性 | 博文列为能力，未标实验 | Learn：实验阶段；Go 无打包提供程序 | ⚠️ 博文未标注（F-068/F-069） |
| 11 | CodeAct 包名与形态 | `agent-framework-hyperlight`（alpha），Hyperlight micro-VM | 仓库存在 `python/packages/hyperlight`；README：`pip install agent-framework-hyperlight --pre`；`HyperlightCodeActProvider` 存在 | ✅ 一致（F-104/F-106/F-107） |
| 12 | CodeAct 基准 52.4% / 63.9% | 27.81s/6,890 → 13.23s/2,489 | 未在 Learn 或仓库文档中找到独立复现或原始测例说明 | ⚠️ 厂商自述、单源（F-105） |
| 13 | GitHub Copilot SDK 集成 1.0 | Build 2026 宣布“reaching 1.0” | Releases：`python-github-copilot-1.0.0` 发布于 2026-07-23，晚于博文 | ⚠️ 宣布与包发布有时差（F-108） |
| 14 | Handoff 编排 1.0 | 是 | Learn 编排页列 handoff 模式；博文给出 .NET/Python 代码 | ✅ 一致（F-109/F-110/F-080） |
| 15 | Foundry 托管代理 GA | 博文描述为生产归宿 | Learn 托管页：Foundry 托管代理已正式发布；Python 自托管包仍为预发布 | ✅ 一致（F-086） |
| 16 | 自托管 .NET 包状态 | 博文未提 | Learn：.NET 托管包为预发行版（prerelease） | ✅ 补齐（F-086） |
| 17 | 当前最新版本 | 博文写于 2026-06 | Releases：`python-1.21.0`（2026-10-08）、`dotnet-1.21.0`（2026-09-11） | ✅ 已更新（F-008） |
| 18 | Go 支持状态 | 博文只提 .NET 与 Python | Learn 概述：Go 公共预览，需 Go 1.26+，CodeAct/声明性代理/功能工作流未实现 | ⚠️ 文档后增（F-005/F-120） |

## 差异与勘误

### 1. 压缩并非无条件“自动”

博文将“自动上下文压缩”列为 Harness 开箱能力，容易被读成默认开启。Learn 能力矩阵明确：在 .NET 与 Python 中，只有提供令牌限制或自定义压缩策略时才启用；Go 需要显式组合 provider。本知识包在正文采用文档口径，并把博文表述标注为“公告口径”。（F-037）

### 2. CodeAct 基准为厂商自述单源

52.4% 时间下降与 63.9% token 下降来自博文中的一张对比表，未给出测例代码版本、硬件、模型与统计方法；仓库有 benchmark 示例但未在文档中给出同一组数字。正文按“厂商自述、单次代表性工作负载”呈现，不作为普遍性能结论。（F-105）

### 3. Copilot SDK “1.0”的时间差

博文（2026-06-03）称 GitHub Copilot SDK 集成“reaching 1.0”；独立包 `python-github-copilot-1.0.0` 的 Release 时间为 2026-07-23。两者不矛盾（发布宣告早于独立包 tag），但读者若按日期核对会看到差异。正文以“Build 2026 宣布、后续包发布”表述。（F-108）

### 4. Go 支持是文档后增，不是博文错误

博文写“same concepts and APIs across .NET and Python”，在其发布时点成立；2026-10 的 Learn 文档新增 Go 公共预览。正文将 Go 单列为“预览与能力边界”，避免用博文否定后续文档。（F-005/F-120）

### 5. Harness 文件记忆路径为博文单源

`agent-file-memory/{session}/` 只出现在博文；Learn 只说明“会话级文件记忆默认启用”。正文标注为“博文给出的默认路径”，不当作稳定 API 契约。（F-040）

## 单源声明

- CodeAct 基准数字（F-105）：仅博文单源。
- Harness 文件记忆路径模板（F-040）：仅博文单源。
- BUILD session 编号与标题（F-111）：仅博文单源（build.microsoft.com 页面未逐一核对）。
- Foundry 托管代理“缩容到零/文件系统保留/每会话 VM 隔离”细节（F-087）：博文单源；Learn 托管页只做能力概述。

## 结论

核心事实（GA 日期、收敛关系、包名、Harness 创建方式、托管 GA 状态、工作流与编排模式）均有官方文档或 Releases 交叉支持。未发现需要把 bundle 标为 `flagged` 的核心声明失败；两项厂商自述数据已显式标注，四项细节标为单源。bundle 状态定为 `stable`，`stale_after: 2027-05-31`。

## 第二轮：源码核验（commit 098214127）

### 方法

- 信源：本地检出 `D:\spaces\SpecWeave\external\dao\action\agent-framework`，commit `098214127`。
- 符号核验：`Select-String` 检索 `^class` / `^def` / `^    def`，逐项确认类名与方法名存在。
- 版本核验：读取 `python/packages/core/pyproject.toml` 与 `dotnet/nuget/nuget-package.props`。
- 计数核验：`Get-ChildItem ... | Measure-Object` 独立计数，不采信目测。
- 未执行测试套件；结论为静态阅读 + 符号检索。

### 逐项结论

| # | 声明 | 源码核验 | 结论 |
|---|------|---------|------|
| 1 | Python core 版本 | `1.25.0` | ✅（F-124） |
| 2 | .NET 版本 | `VersionPrefix 1.28.0` | ✅（F-125） |
| 3 | Python 包数 | 44 个目录 | ✅ 脚本计数（F-123） |
| 4 | .NET 项目数 | 38 个目录 | ✅ 脚本计数（F-126） |
| 5 | core 顶层 py 文件 | 24 个 | ✅ 脚本计数（F-128） |
| 6 | Harness 循环上限 | `DEFAULT_MAX_ITERATIONS = 10` | ✅（F-141） |
| 7 | 后台代理等待 | `DEFAULT_BACKGROUND_AGENTS_WAIT_TIMEOUT_SECONDS = 300` | ✅（F-142） |
| 8 | FIDES 仅 Python | `dotnet/src` 检索 `IntegrityLabel|Fides|FIDES` 零命中 | ✅（F-155） |
| 9 | 检查点协议 | `save` / `load` / `list_checkpoints` | ✅（F-151） |
| 10 | Go 独立仓库 | `go/` 仅 README 指向 agent-framework-go | ✅（F-127） |

### 新增口径差异

#### 1. Shell 并非“仅 .NET”（文档滞后）

文档 F-040 写“Shell 执行（仅 .NET）”。源码 `_harness/_agent.py` 从 `agent_framework_tools.shell` 导入 `ShellExecutor`，并接受 `shell_executor` 参数（F-145）；该包版本 `1.0.0b261106`，为预发布（F-146）。

正确表述：**Python Harness 已有 Shell 能力，但依赖预发布包，不在稳定安装面内。** 正文写“截至该 commit 可用（预发布）”，不把文档旧结论当永久事实（F-163）。

#### 2. 源码 1.25.0 领先 Release 1.21.0

F-008 记录最新 Release 为 `python-1.21.0`；源码为 `1.25.0`（F-124、F-164）。两者不矛盾，但**不能把源码行为直接写成已发布行为**。本知识包在源码篇统一标注“main 快照”。

#### 3. “自动压缩”需要策略/预算（源码确认）

源码提供 `disable_compaction`、`before_compaction_strategy`、`after_compaction_strategy`、`max_context_window_tokens` 与 9 种策略（F-136、F-139）。这确认了第一轮的判断：压缩是“可配置能力”，不是无条件默认行为（F-037）。

### 残余风险（源码轮）

1. 未运行 Python/.NET 测试；默认值与类关系可能随版本变化。
2. 计数为目录/文件级，不等于 API 数或发布包数。
3. 未读 Go 仓库源码；Go 结论仅来自主仓 README 与文档。
4. 本地检出为 env-bound，复现需同一 commit。

