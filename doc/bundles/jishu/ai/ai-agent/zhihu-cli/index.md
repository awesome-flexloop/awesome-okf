---
okf_version: "0.2"
type: bundle
title: "zhihu-cli——知乎数据开放平台官方命令行工具"
description: "知乎数据开放平台 Zhihu CLI 完整知识包：平台定位、三种接入方式（API/Skill/MCP）、安全设计、四大核心能力（搜索/热榜/直答/个人数据）、五种实战玩法、Agent 生态集成。105 条事实，14 项 P0 核验，3 条勘误。"
tags: ["知乎开放平台", "Zhihu CLI", "AI Agent", "MCP", "Skill", "搜索", "热榜", "直答", "个人数据", "命令行工具"]
generated: 2026-09-04
verified: 2026-09-04
status: verified
stale_after: "2026-12-31"
sources:
  - "S1: 腾讯云开发者社区"
  - "S2: 觉醒AI博客"
  - "S3: 知乎官方开放平台 (developer.zhihu.com)"
  - "S4: 知乎问题页"
  - "S5: 老狼知乎专栏"
  - "S6: 老狼知乎回答"
---

# zhihu-cli

> **官方平台**：[知乎数据开放平台](https://developer.zhihu.com) [F-048]
> **产品阶段**：邀测阶段（截至 2026 年 9 月）[F-005]
> **免费额度**：5000 次/天（邀测阶段，2026 年 Q3 扩容至此）[F-006] [E-002]
> **当前版本**：v0.5.0 [F-009]
> **P0 核验**：14 项，3 ✅ 11 ⚠️ 0 ❌（详见 [verification.md](references/verification.md)）
> **事实基数**：105 条（F-001 ~ F-105）

## 项目一句话

Zhihu CLI 是知乎数据开放平台给 AI Agent 提供的官方命令行工具 [F-001]，将**公共内容 + 个人数据**同时交到 AI 手中 [F-004]——支持搜索、热榜、直答、个人数据四大能力，可通过 API、Skill+CLI、MCP 三种方式接入 [E-001]。

## 核心价值

```mermaid
graph TD
    A[Zhihu CLI] --> B[公共内容]
    A --> C[个人数据]
    B --> B1[知乎搜索]
    B --> B2[全网搜索]
    B --> B3[知乎热榜]
    B --> B4[知乎直答]
    C --> C1[我的创作]
    C --> C2[我的关注]
    C --> C3[我的收藏]
```

社区观点认为，Zhihu CLI 最大价值在于**公共内容 + 个人数据同时交到 AI 手中** [F-004]，这是其他搜索类工具不具备的独特优势 [F-084]。

## 知识结构

```
zhihu-cli/
├── index.md                          ← 你在这里
├── log.md                            ← 变更日志
├── concepts/                         ← 概念层（6 篇）
│   ├── index.md
│   ├── 00-platform-overview.md       ← 平台与产品介绍
│   ├── 01-access-architecture.md     ← 接入方式与技术架构
│   ├── 02-security-credentials.md    ← 安全设计与凭证管理
│   ├── 03-core-capabilities.md       ← 核心能力与命令
│   ├── 04-practical-playbooks.md     ← 实战玩法与创意应用
│   └── 05-ecosystem-integration.md   ← 生态集成与兼容性
├── examples/                         ← 操作层（3 篇）
│   ├── index.md
│   ├── 01-setup-installation.md      ← 注册与安装
│   ├── 02-core-commands.md           ← 核心命令使用
│   └── 03-agent-integration.md       ← Agent 接入配置
└── references/                       ← 参考层（3 篇）
    ├── index.md
    ├── article-source.md             ← F-001~F-105 事实登记
    └── verification.md               ← P0 核验报告
```

## 分层导航

### 概念层（6 篇）

| 文档 | 核心内容 | 知识层级 |
|------|----------|----------|
| [00 平台与产品介绍](concepts/00-platform-overview.md) | 平台定位、六大产品、内容分级、邀测信息 | 事实层 |
| [01 接入方式与技术架构](concepts/01-access-architecture.md) | 三种接入方式、调用链路、输出约定 | 机制层 |
| [02 安全设计与凭证管理](concepts/02-security-credentials.md) | 四道校验、Keychain 存储、鉴权机制 | 机制层 |
| [03 核心能力与命令](concepts/03-core-capabilities.md) | 搜索/热榜/直答/个人数据详解 | 事实+机制 |
| [04 实战玩法与创意应用](concepts/04-practical-playbooks.md) | 五种实战玩法 + 创意方向 | 应用层 |
| [05 生态集成与兼容性](concepts/05-ecosystem-integration.md) | Agent 支持、平台兼容、第三方生态 | 应用层 |

### 操作层（3 篇）

| 文档 | 核心内容 |
|------|----------|
| [01 注册与安装](examples/01-setup-installation.md) | 开放平台注册、CLI 安装、Access Secret 配置、Windows 避坑 |
| [02 核心命令使用](examples/02-core-commands.md) | search/hot/answer/me 四大命令实战示例 |
| [03 Agent 接入配置](examples/03-agent-integration.md) | Claude Code Skill/MCP 接入配置流程 |

### 信源层（3 篇）

| 文档 | 内容 | 条目数 |
|------|------|--------|
| [事实登记](references/article-source.md) | F-001~F-105 完整事实底账 | 105 条 |
| [核验报告](references/verification.md) | 14 项 P0 核验 + 3 条勘误 + 时效边界 | - |
| [参考索引](references/index.md) | 外部信源与参考资源导航 | - |

## 信任与生命周期

| 项目 | 状态 |
|------|------|
| **事实基数** | 105 条（F-001~F-105） |
| **P0 核验** | 14 项：3 ✅ 确认 / 11 ⚠️ 部分确认 / 0 ❌ 错误 |
| **勘误项** | 3 条（E-001~E-003） |
| **厂商自述数据** | 8 项（无法独立核验） |
| **status** | verified |
| **stale_after** | 2026-12-31 |

## 时效性提示

⏰ 本知识包信息具有时效性，以下内容可能随时间变化：

- **免费额度**：5000 次/天（2026 年 9 月时点），2026 年 5 月为 1000 次/天 [E-002]
- **产品阶段**：邀测阶段，正式发布时间未定 [F-005]
- **版本号**：v0.5.0，产品快速迭代中 [F-009]
- **接入方式**：API + Skill + MCP 三种，可能新增 [E-001]

**建议**：关键数据以官方最新公告为准（<https://developer.zhihu.com>）。

## 已知边界

1. 平台六大产品中"工具""社区数据""知识库"的具体边界尚不清晰 [P0-014]
2. X-Request-Timestamp 时间戳校验机制待官方文档确认 [P0-006]
3. 全网搜索的百亿索引、600ms 延迟等数据为厂商自述，无独立第三方实测 [P0-002][P0-003]
4. 安全审计 P2/安全为作者评估结论，非官方审计报告 [P0-009]
5. 老狼创作数据存在 9年/430篇 vs 15年/49万字 两种口径（统计维度不同）[P0-010]
6. uv 安装方式为社区推荐，未见官方明确推荐 [P0-011]

---

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
