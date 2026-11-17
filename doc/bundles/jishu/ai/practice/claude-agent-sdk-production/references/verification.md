---
okf_version: "0.2"
type: reference
title: P0 权威核验报告（Claude Agent SDK 生产级智能体构建指南）
description: 对博文 F-001 至 F-087 中 P0 级声明的 Anthropic 官方文档、PyPI 与 npm 核验记录，含勘误 E-1~E-4 与核验边界
tags: [verification, p0, claude-agent-sdk, anthropic, security]
generated:
  by: process:blog-article-to-okf-wiki R→I→E→V
  at: "2026-11-10T15:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-10T15:00:00+08:00"
status: stable
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://stackademic.com/blog/building-production-ai-agents-with-anthropic-s-claude-agent-sdk
  - id: anthropic-news-sonnet-4-5
    url: https://www.anthropic.com/news/claude-sonnet-4-5
  - id: anthropic-engineering-agent-sdk
    url: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
  - id: agent-sdk-overview
    url: https://code.claude.com/docs/en/agent-sdk/overview
  - id: agent-sdk-quickstart
    url: https://code.claude.com/docs/en/agent-sdk/quickstart
  - id: agent-sdk-permissions
    url: https://code.claude.com/docs/en/agent-sdk/permissions
  - id: agent-sdk-hooks
    url: https://code.claude.com/docs/en/agent-sdk/hooks
  - id: pypi-claude-agent-sdk
    url: https://pypi.org/project/claude-agent-sdk/
  - id: npm-claude-agent-sdk
    url: https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk
  - id: claude-code-model-config
    url: https://code.claude.com/docs/en/model-config
---

# P0 权威核验报告

> 核验时间：2026-11-10
> 核验方式：博文声明逐项回到 Anthropic 官方新闻、官方工程文章、Agent SDK overview/quickstart/permissions/hooks、PyPI 项目页与 npm registry
> 信源距离预判：**第三方技术媒体编译 + 快速上手解读**，非厂商自宣、非作者一手实测
> 页面日期：2026-09-26；正文事件时点：2025-09-29（见 E-1）

---

## 核验总览

**11 个 P0 声明集群：✅8 / ⚠️3 / ❌0。无核心声明失败，bundle 状态 `stable`。**

| # | F 编号 | 博文声明 | 权威来源 | 结果 | 处置 |
|---|--------|---------|---------|------|------|
| 1 | F-003~F-008、F-081 | SDK 于 2025-09-29 随 Sonnet 4.5 发布；由 Claude Code SDK 更名；此前六个月持续更新 Claude Code | Anthropic 官方新闻 + 官方工程文章（2025-09-29） | ✅ | 直接采用；更名与日期一致 |
| 2 | F-009~F-014 | 六项能力：agent loop、内置工具、权限、上下文管理、子代理、记忆 | Agent SDK overview Capabilities 表 | ✅ | 直接采用；补齐 Hooks/MCP/Plugins |
| 3 | F-015~F-018 | 官方能力表；Python/TS；运行 Claude Code 二进制；四种接入方式 | Agent SDK overview | ✅ | 直接采用；补入官方对比表 |
| 4 | F-019~F-026 | npm/pip 安装、Python 3.10+、Node 18.14+、二进制打包 | 官方 quickstart + PyPI + npm | ✅ | 直接采用；补源码分发例外 |
| 5 | F-027~F-029 | 版本、engines、`.env` 不自动加载 | npm registry + PyPI + quickstart | ✅ | 采用 2026-11-10 快照 |
| 6 | F-030 | 第三方不得提供 claude.ai 登录/速率限制 | Agent SDK overview NOTE | ✅ | 补入正文“认证边界” |
| 7 | F-031~F-035、F-043~F-045 | 最小 agent：`query()` + `ClaudeAgentOptions`、消息流、`acceptEdits` | 官方 quickstart | ✅ | 代码片段采用；标注未实测 |
| 8 | F-036~F-042 | 七项配置：allowed_tools、permission_mode、model、cwd、max_turns、system_prompt、mcp_servers | 官方 quickstart + PyPI README + 权限页 | ⚠️ | 六项通过；`model` 的 Sonnet 4.5 建议过期（E-2） |
| 9 | F-046~F-057、F-076~F-080 | Hooks/PreToolUse、六步评估、六种模式、allow/deny 语义、审计盲区 | Agent SDK permissions + hooks + PyPI README | ✅ | 直接采用；补 `bypassPermissions` 警告 |
| 10 | F-058~F-067 | Sonnet 4.5 推荐、$3/$15、付费计划功能、Agent SDK 全开发者可用 | Anthropic 官方新闻 + 官方 model-config | ⚠️ | 定价/可用性通过；推荐范围转述偏窄（F-058），当前模型阵容已更新（F-066） |
| 11 | F-068~F-075 | 沙箱、日志、只读起步、边界测试、SDK vs raw API | 博文原文；官方文档交叉 | ⚠️ | 方法论建议标注；Darktrace 仅博文单源（E-4） |

---

## 勘误台账

### E-1（⚠️ 日期型）：页面日期与正文事件时点冲突

| 口径 | 内容 |
|---|---|
| 页面标注 | 2026-09-26（Saturday, September 26, 2026） |
| 正文事件 | “Anthropic released the Claude Agent SDK on September 29, 2025” |
| 官方锚点 | 官方新闻与工程文章均为 2025-09-29 |
| 差异 | 页面日期比正文事件晚约 12 个月；正文未提 Sonnet 5.5 / Opus 5.5 等后续模型 |
| 判定 | 转载或页面日期标注异常；内容时点按 2025-09-29 处理 |
| 正文处置 | 知识包按 2025-09 口径呈现；index“阅读须知”第 1 条明示 |

### E-2（⚠️ 时效型）：`claude-sonnet-4-5` 已非最新

| 口径 | 内容 |
|---|---|
| 博文 | “model: Specify the Claude model (use claude-sonnet-4-5 for latest)” |
| 2026-11-10 官方 | Anthropic API 的 `sonnet` 别名解析为 Sonnet 5.5；`opus` 为 Opus 5.5；`haiku` 为 Haiku 5.5；Fable 5.2 为单独可选模型（F-066） |
| 判定 | 博文写作时的最新模型，当前已过期 |
| 正文处置 | 配置表保留博文原值并标注“已过期”；选型指向 [claude-model-selection](../../claude-model-selection/index.md) |

### E-3（⚠️ 精度型）：Python SDK 自带 CLI 的例外

| 口径 | 内容 |
|---|---|
| 博文 | “The Python SDK includes the CLI automatically — no separate installation required.” |
| 官方 quickstart | 两个 SDK 通常打包二进制；pip 安装到源码分发（例如 ARM64 Windows）时不含二进制，需另装 Claude Code（F-026） |
| 判定 | 主路径正确，遗漏源码分发例外 |
| 正文处置 | 01 篇写明“多数平台附带、源码分发例外” |

### E-4（⚠️ 单源型）：Darktrace 研究未能独立定位

| 口径 | 内容 |
|---|---|
| 博文 | “Recent research from Darktrace showed agents hacking their own test environments.” |
| 核验 | 核验环境浏览器工具不可用，未定位到 Darktrace 原始研究；无官方或独立报道可交叉 |
| 判定 | 仅博文单源，不作为硬事实 |
| 正文处置 | 03 篇威胁模型中以“测试环境攻击”呈现，标注为文章引用；不写具体数字与结论 |

### 附：引文范围注记（F-058）

博文写 “Anthropic recommends Sonnet 4.5 for all agent use cases”；官方原文为 “We recommend upgrading to Claude Sonnet 4.5 for all uses.” 博文把 “all uses” 收窄为 “all agent use cases”，属转述范围差异，不构成事实错误，但引用时以官方原文为准。

---

## 机械核验记录

| 项 | 结果 | 说明 |
|---|---|---|
| 双份 F 编号 | ✅ | spec `facts.md` 与 `references/article-source.md` 均为 F-001~F-087，集合一致、连续无跳号 |
| UTF-8 | ✅ | 全部新增/修改 .md 以 UTF-8 无 BOM 写入 |
| 相对链接 | ✅ | index/concepts/references 间链接逐一 `Test-Path` |
| toctree | ✅ | 根 index 收 concepts/index、references/index、log；子目录 index 收全部内容文件 |
| 计数同步 | ✅ | practice 31 束/29 目录、ai 294 束、jishu 532 束、总索引 727 束（以 `check-bundles-index.py` 地面真值为准） |
| frontmatter | ✅ | okf_version/type/title/description/tags/generated/verified/status/stale_after/sources 齐备 |
| 代码实测 | ❌ 未做 | 代码片段未在本库环境执行，正文显著标注 |
| Darktrace 原始研究 | ⚠️ 未定位 | 浏览器工具超时；标“仅博文单源” |

---

## 核验边界

1. `platform.claude.com` 在核验环境返回 “App unavailable in region”，平台侧细节以 `code.claude.com` 文档与官方新闻为准。
2. 浏览器工具在本次核验中超时，Darktrace 研究未独立定位；不影响 SDK 核心事实。
3. 价格为 2025-09-29 官方发布口径；2026-11-10 未重新核对 Sonnet 4.5 现价，正文只把它作为文章时点事实。
4. 代码片段只做语法与 API 形状核对，未执行；不能声称“实测通过”。
5. 版本号（npm 0.3.322 / PyPI 0.2.180）为 2026-11-10 查询快照，迭代后需复核。

---

## 结论

核心声明（发布时间、更名、能力、安装、权限模型、hooks、定价与可用性）均有官方源支撑。三项 ⚠️ 分别为日期异常、模型时效与 Darktrace 单源，均已在正文与 index 明示，不影响 `stable` 状态。`stale_after` 设为 2027-01-31，到期前应复核模型阵容与 SDK 版本。
