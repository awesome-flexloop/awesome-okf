---
type: concept
title: ScholarClaw 项目概览与定位
description: "零依赖学术搜索 skill 包的定位：远端 SaaS 的薄客户端、TS 客户端 + Shell 脚本双层调用面、配置体系、安装方式与运行时依赖。"
tags: [scholarclaw, overview, academic-search, skill, configuration]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: ScholarClaw 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: ScholarClaw 架构洞察
---

# ScholarClaw 项目概览与定位

ScholarClaw 是有道出品的学术搜索 skill 包（版本 1.4.1，`package.json` 与 `SKILL.md` frontmatter 一致）（F-sc-057、F-sc-043），面向论文检索、文献调研、学术问答等场景。理解它的第一把钥匙是：**本地仓库里没有任何搜索逻辑**——没有模型、没有索引、没有检索代码，全部计算都发生在远端 SaaS `https://scholarclaw.youdao.com`，本地只是一个协议适配层（F-sc-001）。

## 一、定位：以 Markdown 契约 + Shell 脚本为主体的 skill 包

常见预期是"这类项目应该是个 SDK"，但 ScholarClaw 的真实形态是"skill 包"：

- `SKILL.md` 是面向 LLM 的运行时契约（触发条件、SSE 事件、时序参数），而非 README 式说明（F-sc-043~F-sc-048，详见 [/concepts/03-skill-contract.md](/concepts/03-skill-contract.md)）；
- shell 脚本是主交付物：`install.sh` 把脚本安装为 `sc-*` 系统别名，SKILL.md 教 LLM 调用的也是 shell 命令（F-sc-042）；
- TypeScript 客户端（`server/index.ts`）是路由与类型的**权威参照**，但 `package.json` 的 `main` 直接指向 `.ts` 源文件、dependencies 为空——TS 侧不被构建运行（F-sc-057）。

## 二、双层调用面总览

同一组后端 API 存在三套平行入口，最终汇聚到同一个远端服务：

| 调用面 | 载体 | 覆盖范围 | 说明 |
|--------|------|---------|------|
| TypeScript 客户端 | `server/index.ts` 的 `ScholarClawClient` | 9 组共 20 个方法 | 统一 `request()` 通道，JSON 编码（F-sc-008~F-sc-019） |
| Shell 脚本 | `scripts/` 下 16 个 `.sh`（1 公共库 + 15 功能脚本） | 全部路由的 curl 直调 | 主交付物（F-sc-029） |
| npm 命令别名 | `package.json` 14 个 npm scripts + `lobsterai` 元数据块 | 桥接进宿主工具的命令生态 | skillType=`api`、14 个 supportedCommands（F-sc-058、F-sc-059） |

选型建议：LLM/智能体场景走 SKILL.md 契约调 shell 命令；需要类型安全的程序化调用可参考 TS 客户端，但需自行承担"该层未经构建验证"的风险。详见 [/concepts/01-server-client.md](/concepts/01-server-client.md) 与 [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)。

## 三、配置体系

### 配置接口与默认值

`ScholarClawConfig` 接口含 5 个字段，默认值如下（F-sc-001）：

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `serverUrl` | `https://scholarclaw.youdao.com` | 服务端地址 |
| `apiKey` | `''` | 认证密钥 |
| `timeout` | `30000` | 超时（毫秒） |
| `maxRetries` | `3` | 最大重试次数 |
| `debug` | `false` | 调试开关 |

### 配置文件位置与合并优先级

- 配置文件路径为 `~/.scholarclaw/config.json`（F-sc-002）；安装时 `install.sh` 还会生成 `scholarclaw.env`（F-sc-042）。
- 合并链为：默认值 ← 配置文件 ← OpenClaw 配置 ← 环境变量 ← 显式 overrides，后者覆盖前者（F-sc-003）。SKILL.md 面向使用者的声明为：环境变量 > OpenClaw 配置 > 配置文件 > 默认值（F-sc-050）。
- 校验规则三条：`serverUrl` 必填、必须是合法 URL、`timeout` 小于 1000 时输出警告（F-sc-004）。

### 关键常量

搜索引擎常量 `SEARCH_ENGINES` 共 9 项：`ARXIV`、`PUBMED`、`GOOGLE`、`KUAKE`、`BOCHA`、`CACHE`、`NIPS`、`THECVF`、`MLR_PRESS`（F-sc-005）；搜索模式 `SEARCH_MODES` 为 `simple`、`ai`，排序选项 `SORT_OPTIONS` 为 `relevance`、`date`、`citation_count`（F-sc-006）；任务状态常量 `BLOG_STATUSES`/`BENCHMARK_STATUSES` 均为 `pending`、`running`、`completed`、`failed` 四值（F-sc-007）。注意引擎清单与状态枚举存在源码间不一致，见 [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)。

## 四、安装、打包与运行时依赖

- **安装**：`install.sh` 落盘到 `~/.scholarclaw`，生成 `scholarclaw.env`、写入 `aliases.sh` 的 `sc-*` 命令别名，并分发 `scholarclaw` 快速启动脚本（F-sc-042）。
- **打包**：`package.sh` 构建 `dist/` 目录并生成 tar.gz、zip 归档及对应 sha256 校验文件（F-sc-041）。
- **运行时依赖**：仅两项——`curl`（必需）、`jq`（可选）；`package.json` 的 dependencies 为空，devDependencies 只有 `@types/node ^20` 与 `typescript ^5`，engines 要求 node>=`16.0.0`（F-sc-051、F-sc-057）。jq 可选意味着输出格式不稳定：有 jq 时是美化 JSON，无 jq 时是原始紧凑 JSON，下游脚本化解析时不能假设格式。
- **构建配置**：`tsconfig.json` 声明 target=`ES2020`、strict=`true`、outDir=`./dist`，但无配套构建脚本（F-sc-060）。

## 五、SKILL.md 与 README 的角色

- `SKILL.md` frontmatter：`name: scholarclaw`、`version: 1.4.1`、`official: false`；正文声明触发条件（学术场景替代 web-search）、分场景响应时间期望表、能力清单（7 项）（F-sc-043~F-sc-045、F-sc-049）。
- `README.md` 含功能介绍、引擎表（9 引擎）、API 参考表、环境变量表、Script Reference 表等章节（F-sc-061）。

## 学习路径建议

1. 先读本篇建立全局视图；
2. 再读 [/concepts/01-server-client.md](/concepts/01-server-client.md)（API 面权威参照）与 [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)（实际调用层）；
3. 进阶读 [/concepts/03-skill-contract.md](/concepts/03-skill-contract.md)（LLM 时序契约）与 [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)（防御性集成思维）。

## 相关概念

- [/concepts/01-server-client.md](/concepts/01-server-client.md)
- [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)
- [/concepts/03-skill-contract.md](/concepts/03-skill-contract.md)
- [/concepts/04-evolution-inconsistency.md](/concepts/04-evolution-inconsistency.md)
