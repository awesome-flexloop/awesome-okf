---
type: bundle
title: "企业微信套件 Skill（wecom-unified）"
okf_version: "0.2"
---

# 企业微信套件 Skill（wecom-unified）

`wecom-unified` 是企业微信官方开源的 Skill 套件，把通讯录、文档、在线表格、智能表格、智能文档、在线 PPT、日程、会议、待办、微盘、邮件、消息等能力，封装为 AI 宿主可直接读取的 Markdown 契约与辅助脚本。它的实质内容位于 `skills/wecom-unified/`：1 篇 `SKILL.md` 负责分流，133 篇 reference 提供参数契约，6 个 Python 脚本生成物料，53 个模板文件支撑 PPT 装配。本知识包按 commit `cae8a5befac67d96bfe573b1675c5faab474758e` 冻结这一基线。

理解这套工具的关键，是区分两条交付链：Skill 只提供「怎么调」的知识，真正的接口能力来自独立安装的 `wecom-cli`（npm 包 `@wecom/cli`，版本下限 `1.2.1`）。安装 Skill 成功不代表业务可用；任何命令前都必须通过「版本 → 授权 → 初始化」三步门禁，且输出侧禁止外露 `userid`、`docid` 等内部标识。

本知识包面向三类读者：首次接入的工程师可从概念 00、01 与示例 01 入手；需要稳定路由的 Agent 开发者应重点读 02、03；要落地文档/PPT 物料流水线的读者则看 04、05 与示例 02、03。所有技术断言均登记在 108 条事实中，可逐条复核。

## 概念篇

| 序号 | 文档 | 主题 | 一句话摘要 |
|---|---|---|---|
| 00 | [套件定位与依赖](concepts/00-overview.md) | 边界与依赖 | Skill 与 `wecom-cli` 是两条独立交付链，运行时经 Bash 进程连接 |
| 01 | [前置检查与身份](concepts/01-preflight-and-identity.md) | 门禁与输出 | 三步硬门禁 + `identity whoami` + ID 类字段禁外露 |
| 02 | [意图路由](concepts/02-intent-routing.md) | 分流机制 | 意图 → 14 个业务域 → reference → 构造命令，禁止凭描述拼参数 |
| 03 | [references 分类学](concepts/03-references-taxonomy.md) | 知识组织 | 133 篇扁平文档的两级命名、逐域分布与四个子系列 |
| 04 | [脚本工具链](concepts/04-scripts-toolchain.md) | 工程实现 | 6 个脚本的输入输出、依赖与防护机制 |
| 05 | [PPT 模板系统](concepts/05-ppt-template-system.md) | 设计系统 | 9 套模板的三段式结构、`index.json` 协议与四类校验 |

## 实战示例

| 序号 | 示例 | 场景 | 说明 |
|---|---|---|---|
| 01 | [带前置检查的首次接入](examples/01-quickstart-with-preflight.md) | 环境起步 | 安装、版本门禁、扫码授权、身份确认、只读查询 |
| 02 | [从表格数据到在线 PPT](examples/02-sheet-to-ppt-pipeline.md) | 跨域流水线 | `collect.py` 采集 → pptx 建文档 → 写页传图 → 交付链接 |
| 03 | [本地 PPT 预览与公式重算](examples/03-pptx-preview-and-recalc.md) | 本地物料 | `pptx2image.py` 预览与 `recalc.py` 重算 |

3 篇示例均为基于源码阅读整理的用法演示，**未在本机实跑**，输出仅表示格式，不构成运行结果承诺。

## 信源与证据

- **事实登记**：[references/facts.md](references/facts.md)，共 108 条（F-001～F-108），分六节：仓库结构 18 条、前置检查与路由 26 条、references 分类学 19 条、scripts 工具链 29 条、模板系统 9 条、安装与耦合 7 条。每条含源文件行号与可复跑的核对命令。
- **洞察**：[references/insights.md](references/insights.md)，6 条四元组（陈述 / 证据 / 反常识 / 行动），文末附概念文档知识地图。
- **信源登记**：[references/sources.md](references/sources.md)，记录上游仓库 `git@github.com:WecomTeam/wecom-unified.git`、基线 commit、MIT 许可证、197 个文件的口径、版本标注说明与关键信源文件清单。

## 信任与生命周期说明

- **状态**：已为 `stable`，R（事实）与 I（洞察）、E（概念与示例）阶段均已完成，并于 2026-11-09 通过 V 阶段独立复核（Grep 级实体核验 + F 编号一致性 + 结构/链接检查）。
- **时效**：`stale_after` 为 `2027-11-09`；超过该日期应重新核对上游 commit 与 `wecom-cli` 版本下限。
- **基线**：全部事实与文档对应 commit `cae8a5befac67d96bfe573b1675c5faab474758e`。上游无独立版本号（`SKILL.md` frontmatter 仅 `name`、`description`、`allowed-tools`），升级评审以 commit 为准。
- **示例**：3 篇示例均未实跑，任何命令输出、返回字段与文件列表都是示意，不得作为验收依据。
- **范围**：本包只覆盖 `skills/wecom-unified/` 的契约、脚本与模板；不含 `wecom-cli` 的实现细节与服务端接口的完整字段表。

## 相关企业微信知识包

- [企业微信 5.0.10 版本说明](../wecom-5-0-10-release/index.md)
- [企业微信 5.0.12 版本说明](../wecom-5-0-12-release/index.md)
- [企业微信专题场景](../wecom-topic-scenarios/index.md)
- [wecom-cli 命令行工具](../wecom-cli/index.md)
- [企业微信 AI 机器人 Python SDK](../wecom-aibot-python-sdk/index.md)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```