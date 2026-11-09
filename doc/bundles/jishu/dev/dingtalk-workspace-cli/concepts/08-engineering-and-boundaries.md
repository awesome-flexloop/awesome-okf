---
okf_version: "0.2"
type: Concept
title: "工程与边界：为什么这套 CLI 能长期维护，以及它不适合谁"
description: "从 59 个内部包、11 层测试、69 篇文档与九道合入门禁看 dws 的工程化程度，并给出选型矩阵、已知缺口与升级策略"
sources:
  - id: repo
    resource: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
  - id: ci
    resource: "docs/ci-pr-gates.md"
  - id: readme
    resource: "README.md"
facts: [F-001, F-002, F-005, F-006, F-007, F-008, F-029, F-061, F-063, F-064, F-065, F-066, F-067, F-068, F-069]
---

# 08 · 工程与边界

> 核心判断：dws 的「可维护」不是靠文档承诺，而是靠**九道合入门禁 + 生成物差异守护 + 分层测试**把约束变成机器可执行的检查。

## 1. 仓库结构（可核验的规模）

| 维度 | 数量 | 含义 |
|------|------|------|
| 内部包 | 59 个一级包（`internal/`） | 按职责拆分，含 `tui`、`i18n`、`audit` 等横切能力（F-006、F-064） |
| 测试分层 | 11 个目录（`test/`） | unit / contract / integration / mock_mcp / smoke / cli / skill_* 系列 |
| 文档 | 69 篇（`docs/`） | 架构、域模型、参考手册、RFC、迁移方案、CI 门禁 |
| 工作流 | 16 个（`.github/workflows/`） | CI、发布、镜像、E2E、AI 行为检查 |

（F-006、F-007、F-008）

## 2. 九道合入门禁

`docs/ci-pr-gates.md` 明确列出九个必需检查（F-065）：

| 门禁 | 守什么 |
|------|--------|
| `Lint` | 版本/风险分级、格式、`go vet`、Actionlint |
| `Test` | 按层选择的 race/单元/发布脚本测试 + 跨平台编译 |
| `Coverage` | 整体不回归，**变更代码 100% 覆盖** |
| `Policy` | 仓库策略与 fail-closed 的 CHANGELOG 契约 |
| `Edition` | 版本形态契约测试 |
| `Interface Integrity` | CLI / Schema / Skill / 稳定版兼容性 |
| `AI Behavior` | AI 生成 PR 的独立策略（不检出、不执行 PR 代码） |
| `CLI Smoke` | 每个公开顶层命令的离线 help |
| `Mock MCP` | HTTP 与 stdio 两种 MCP 生命周期的冒烟 |

（F-065）

三个细节值得单独看：

1. **`Interface Integrity` 把「命令面」当公共 API 管理**，改名、删参数、改 Schema 都会触发兼容性检查。
2. **`AI Behavior` 用 `pull_request_target` 且不执行 PR 代码**，避免自动化审查本身成为攻击面（F-066）。
3. **`Policy` 的 CHANGELOG 检查是 fail-closed**：缺失即失败，而不是警告（F-067）。

> **洞察**：静态命令面之所以敢「每版重生成」，靠的不是生成器聪明，而是门禁足够严——没有这九道门，十倍展开的生成物会在几个版本内失控。

## 3. 测试分层与现场验证的边界

| 层 | 目录 | 验证什么 |
|----|------|---------|
| 单元 | `test/unit` | 纯函数与局部逻辑 |
| 契约 | `test/contract` | Spec/Schema/旗标回退链 |
| 集成 | `test/integration` | 多组件协作 |
| Mock MCP | `test/mock_mcp` | 不依赖真实服务的 MCP 生命周期 |
| 冒烟 | `test/smoke` | 公开命令可启动、help 可用 |
| CLI | `test/cli` | 端到端命令行为 |
| 技能 | `test/skill_e2e`、`skill_scripts`、`skill_static` | 技能内容、脚本与静态结构 |

（F-007）

**重要边界**：本束所有运行时描述均来自文档，**未执行** `dws`，因此「测试覆盖到什么程度」是仓库自述，不构成本次核验结论（见 [verification.md](../references/verification.md)）。

## 4. 生成物治理

```text
端点数据 → 生成器 → 提交的 Go 代码 → git diff --exit-code
```

（F-029）

这条机制配合 `Interface Integrity` 门禁，形成「源头变更必须显式提交生成物」的闭环。实践含义：**不要手改生成文件**；改源头、重生成、把差异一起进 PR。

## 5. 升级与降级

```bash
dws upgrade
dws upgrade --rollback
```

（F-061）

- 自升级保留可回滚版本，适合灰度；
- `DWS_NO_SKILLS` 可关闭「升级时联动更新技能」，避免技能目录被意外改写；
- 升级前建议先 `dws schema --all --compact` 存一份基线，升级后 diff 观察契约变化。

## 6. 选型矩阵

| 角色 | 建议 | 理由 |
|------|------|------|
| 个人开发者 | 用 `multi` 技能 + 浏览器登录 | 上下文占用小，权限最小 |
| 团队自动化 | 设备码登录 + `json` 输出 + 退出码分流 | 无浏览器依赖，失败可分类 |
| Agent 平台 | Schema 分级查询 + Skill 流程 + dry-run 确认 | 确定性与安全兼得 |
| 合规敏感组织 | 加审计留存策略 + 域名白名单收紧 | 机制可用，但需自建合规方案 |
| 需要「今天上线的新接口」 | 评估版本时差 | 静态管线需同步端点数据并发布 |

## 7. 已知缺口（不要在文档里回避）

| 缺口 | 影响 | 缓解 |
|------|------|------|
| Windows 不支持 `auth export/import` | 换机需重新登录 | 使用设备码流程快速重登（F-037） |
| 静态命令面存在版本时差 | 新接口可能晚于服务端可用 | 关注版本说明；必要时用 `dws api` 临时兜底（F-058） |
| 20 服务域与 13 产品快照口径不一 | 引用数字易错 | 引用时标注来源与快照（冲突 C-1） |
| 本束未做运行时实测 | 行为细节以官方为准 | 读 [verification.md](../references/verification.md) 的未核验清单 |

## 8. 三条可迁移的工程原则

1. **把接口当产品**：命令面进版本库、进 CI、做兼容性检查。
2. **把安全写进元数据**：副作用声明前置，预览与确认自动派生，而不是逐命令补丁。
3. **把文档当生成物**：help、Schema、技能说明从同一注册表派生，拒绝第二份真相。

这三条与具体语言无关，适用于任何「内部能力 → 外部工具面」的封装工程。

## 延伸

- 架构起源：[02-static-endpoint-pipeline.md](02-static-endpoint-pipeline.md)
- 完整示例：[examples/02-agent-workflow.md](../examples/02-agent-workflow.md)
- 信源与核验：[references/facts.md](../references/facts.md)、[references/verification.md](../references/verification.md)