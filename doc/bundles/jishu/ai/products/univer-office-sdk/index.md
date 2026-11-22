---
okf_version: "0.2"
type: bundle
title: "Univer：人与 AI agent 共用的嵌入式 Office SDK"
description: "Univer 表格/文档引擎 SDK 的授权边界、Facade API、命令系统与 agent 治理教程——源自微信博文经 GitHub API 与官方 README/安装文档/对比页逐项核验，含 72 条编号事实、24 项 P0 核验与 3 个可迁移模式（官方流程重组，未实机运行）"
tags: [univer, office-sdk, spreadsheet, apache-2.0, ai-agent, headless, facade-api, command-system, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-11-20T10:30:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-20T10:45:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/7WCDC4R7mxqFRHMP0Zf9hA
  - id: github-api
    url: https://api.github.com/repos/dream-num/univer
  - id: official-readme
    url: https://github.com/dream-num/univer/blob/dev/README.md
  - id: official-compare
    url: https://univer.ai/compare/
  - id: official-installation
    url: https://docs.univer.ai/guides/sheets/getting-started/installation
  - id: official-skills
    url: https://github.com/dream-num/skills
---

# Univer：人与 AI agent 共用的嵌入式 Office SDK

> **类型**：技术教程 / 选型（含可照做 `examples/`，操作可复现性两问皆"是"）
> **信源**：微信公众号「Github喵」《Github 26k star，网页里嵌一个 Excel》（2026-11-19 14:30，四川）→ 2026-11-20 经 GitHub REST API、`dev` 分支 README、官方安装文档与功能对比页逐项核验
> **核验结论**：24 项 P0/P1 声明 **17✅ / 7⚠️ / 0❌**，核心声明无造假；7 项差异全部落在动态时点数、命令写法演进、示例完整性与观点口径
> **数据时点**：Star / 版本 / 功能矩阵均为 2026-11-20 快照；`stale_after: 2026-12-31`

## 本文概要

[Univer](https://github.com/dream-num/univer) 是一套 TypeScript、Apache-2.0 许可的**嵌入式 Office SDK**：用 preset 十几行代码就能在自己的网页里放一个带公式引擎的表格编辑器，数据、权限与持久化都由应用侧掌握。它脱胎于已归档的 [Luckysheet](https://github.com/dream-num/Luckysheet)，但为重写而非同库延续。官方仓库自述定位逐字为 "Build your own AI office … **for people and AI agents**"——也就是说，本教程把 agent 治理列为一级主题，不是跟随推介文的主线发挥，而是跟随官方定位。

真正需要学到的不是"怎么嵌一个表格"，而是**三层边界**：① Apache-2.0 只覆盖 Web SDK 核心，文件导入导出 / 协同 / 历史走 Server SDK 与商业授权；② `workbook.save()` 是内部 JSON 快照，不等于 XLSX 导出；③ 当人和 agent 共用同一套写入 API 时，治理点必须下沉到命令层，而不是 UI 层。

## 阅读路径

**先建立概念（约 20 分钟）**

1. [00 · 身份、谱系与信源距离](concepts/00-identity-and-provenance.md)——项目身份、Luckysheet 谱系、Star 时点勘误、二手内容的信源距离
2. [01 · 三 SDK 分层与授权边界（洞察层）](concepts/01-three-sdk-layers-and-license-boundary.md)——洞察四元组：为什么"开源版够用"必须加限定词
3. [02 · 嵌入表格与 Facade API](concepts/02-embed-and-facade-api.md)——preset 嵌入、Facade 三层对象、Steady 生命周期、Headless 同构
4. [03 · 命令系统与插件架构](concepts/03-command-system-and-plugin-architecture.md)——Command / Mutation / Operation、撤销合成、changesets + OT
5. [04 · AI agent 治理与生态](concepts/04-agent-governance-and-ecosystem.md)——执行前/执行后事件闸门、Worktree 审阅流程、五个生态集成
6. [05 · 选型矩阵与三个可迁移模式（萃取层）](concepts/05-selection-and-transferable-patterns.md)——P-1 授权边界前置 / P-2 命令层治理 / P-3 快照优先

**再动手实操**

7. [00 · 十几行代码嵌一个表格编辑器](examples/00-embed-sheets-core.md)——preset 安装、容器、初始化、dispose、版本纪律
8. [01 · 报价单、生命周期等待与快照恢复](examples/01-quotation-with-lifecycle.md)——补回博文省略的 Steady 等待段、公式重算读回、快照恢复
9. [02 · agent 命令闸门、CLI 工作区与本地开发](examples/02-agent-command-guard.md)——闸门示意（⚠️ 非官方）、官方现行 skills 命令、源码本地开发

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 归属 | `dream-num/univer`（Organization），创建于 2022-09-29，默认分支 `dev` |
| 语言 / 许可 | TypeScript / **Apache-2.0**（仅覆盖 Web SDK 核心） |
| 社区数据 | Star **30,434**、Fork 2,755、issues 198（**2026-11-20 时点**，非博文标题的 26k） |
| 三个 SDK | Web SDK（开源核心）/ Server SDK（协同·历史·文件转换）/ AI SDK（Headless 之上的 agent 能力） |
| 快速安装 | `pnpm add @univerjs/presets @univerjs/preset-sheets-core` |
| 运行时要求 | 开发 monorepo Node.js ≥ 22.18；Headless ≥ 18.17；Chrome 88 编译目标，`Intl.Segmenter` 需 polyfill |
| 视图层 | React 18 构建，支持 18/19，对 React 16.9+/17 有最小兼容；React/Rxjs 为 peerDependencies（不排斥 Vue/Angular） |
| 命令模型 | Command / Mutation / Operation 三类；`BeforeCommandExecute` 可检查并取消，`CommandExecuted` 用于审计 |
| 持久化 | `workbook.save()` → 含插件数据的 JSON 快照；恢复须 `createWorkbook(JSON.parse(saved))` |
| 文件互通 | XLSX / DOCX / PPTX 导入导出走 Server SDK Exchange（OOXML ↔ Unit 映射），属商业授权范围 |
| 官方生态 | Univer CLI、DeepSeek Harness、WorkBuddy（Developer preview）、OpenClaw、Univer SDK Skills（共 5 个） |

## ⚠️ 阅读前必知的七条口径勘误

1. **Star 数**：博文标题「26k」为滞后快照；本包统一采用官方现值 **30,434（2026-11-20）**，所有动态数字引用须带时点。
2. **"十几行代码"的完整性**：官方 Quick start 确为十几行，但报价单示例在 `setValues` 前有**完整的 `await` 等待 Steady / 公式引擎就绪代码**，博文把它压成一句注释。照抄博文代码可能取不到重算结果——[examples/01](examples/01-quotation-with-lifecycle.md) 已补回官方等待段。
3. **CLI 命令写法已演进**：博文 `npx skills add dream-num/skills -s univer-cli -g` 中的 `univer-cli` skill **真实存在**（标注 `hidden: true`），但官方现行主推 `--skill build-with-univer` / `--skill univer-integrate`，`-s` 简写未见于现行文档。属「实体真实、写法演进」，不是虚构。
4. **"不用另起文档服务器"只对开源子集成立**：纯前端编辑确实不需要服务端，但启用协同、历史、文件转换时仍需 Server SDK。
5. **"开源版基本够了"漏了一个边界**：官方对比页明确开源版**不含服务端组件，且公式引擎性能低于商业版**。结论方向成立，但选型时应披露。
6. **对比对象系作者自选**：官方 SDK 对比页对象为 SpreadJS / Handsontable / ONLYOFFICE / Syncfusion，**未含 AG Grid**；博文与 Handsontable / AG Grid / OnlyOffice 的比较属作者观点，不是官方评测。
7. **生态与 CLI 能力为不穷尽列举**：官方生态表为 5 个（博文漏列 WorkBuddy 与 SDK Skills）；`univer-cli` 定义五类 Unit：Sheet / Doc / Slide / **Base** / **Board**（博文只说 Excel/Word/PPT）。

## 采用提示与已知边界

- **授权边界前置**：需求若是「产品里放一个能算公式的表格、数据自己存」，开源核心可闭环；若是「上传下载 Excel / 多人协同 / 复杂图表与透视表」，即进入商业授权范围。立项文档里写清这两句，比记任何产品名都重要（[concepts/05](concepts/05-selection-and-transferable-patterns.md)）。
- **快照 ≠ 文件导出**：`workbook.save()` 是内部 JSON 快照，与 XLSX 导入导出分属两条能力。把"能保存"当"能导出 Excel"交付，是本类 SDK 最常见的需求事故。
- **agent 治理**：官方逐字提示 "Command success is not correctness evidence"——命令执行成功不等于结果正确，须读回自检；草稿在 Worktree 隔离，人工显式 merge（[concepts/04](concepts/04-agent-governance-and-ecosystem.md)）。
- **版本纪律**：所有 `@univerjs/*` 须同版本，商业包须匹配 release line；plugin mode 默认不含 Facade API；mobile support 仍为 experimental。
- **未核验项**：商业授权价格、水印具体表现、试用限制细节未核验，需商务/法务确认；官方对比页信息更新于 2026-10，功能矩阵会变。
- **实机边界**：本知识包**未实际安装运行 Univer**，`examples/` 均为官方 README / 安装文档可照做流程的重组与标注；闸门示意代码为**非官方模板**，已显著标注。
- **复核安排**：`stale_after: 2026-12-31` 前复核 Star 量级、skills 命令写法、开源/商业功能矩阵、CLI Developer preview 状态。

## 信源与可信度

- [博文事实清单 F-001~F-072](references/article-source.md)：72 条编号事实（博文 55 + 官方核验补充 17），双份登记之一；另一份在 `.trae/specs/univer-office-sdk-okf-wiki/facts.md`。
- [P0 权威核验报告](references/verification.md)：24 项核验、勘误四张清单、博文未覆盖的官方边界、核验方法与局限。
- 信源距离：第三方开源推介号 → 已升级为 GitHub API 与项目一手文档交叉核验；博文观点段（选型对比、体验判断）保留观点标签，不升格为官方结论。

## 主题关联

- [wigolo](../wigolo/index.md)：同为「微信博文 → 官方核验 → OKF 教程」范式，可对照看单源推介文的信源距离处理
- [craft-anything](../craft-anything/index.md)：同属 AI 产品域的近期博文转化束，可对照看 F 编号台账与勘误清单写法
- [skills-manager](../skills-manager/index.md)：Agent Skill 的安装与管理，和本包 CLI / skills 集成章节相邻
- [agent-reach](../agent-reach/index.md)：Agent 触达与工具接入生态，和「人和 agent 共用一套 API」的治理问题相邻

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
