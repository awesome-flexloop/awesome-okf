---
okf_version: "0.2"
type: Reference
title: "Univer 博文 P0 权威核验报告"
description: "对博文 24 项 P0/P1 声明的官方交叉核验：17✅ / 7⚠️ / 0❌，含勘误四张清单与博文未覆盖的官方边界"
tags: [univer, verification, p0-check, fact-check, errata, license-boundary]
generated: { by: "blog-article-to-okf-wiki:R/V", at: "2026-11-20T09:40:00+08:00" }
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

# P0 权威核验报告

> 核验时间：2026-11-20。信源：GitHub REST API（仓库元数据时点快照）、`dev` 分支 README.md、官方安装文档、官方功能对比页、`dream-num/skills` 仓库与其 `univer-cli/SKILL.md`（均为项目一手材料）。
> 博文信源距离：**第三方开源推介号（Github喵）转述**，非项目方发布；其中对比与选型段属作者观点，不构成官方结论。

## 核验总览

| 级别 | 数量 | 结论分布 |
|------|------|---------|
| P0（数字/日期/命令/许可/授权） | 16 | ✅ 12 / ⚠️ 4 / ❌ 0 |
| P1（能力声明/架构/兼容列表） | 8 | ✅ 5 / ⚠️ 3 / ❌ 0 |
| 合计 | **24** | **✅ 17 / ⚠️ 7 / ❌ 0** |

**总体评估**：博文技术准确度高——安装命令、初始化代码、报价单公式、三层命令模型、事件名、插件分层、Node/Chrome/React 版本、授权边界均与官方材料逐字或同向一致，且"开源版够用于嵌表格、文件导入导出要付费"这一主结论成立。**7 项 ⚠️ 全部是动态时点数、命令写法演进、示例完整性或观点口径**，无一项构成核心声明造假。故 bundle 状态为 **stable**，但下列勘误须在正文落实。

> **「人和 AI agent 共用一套 API」不是作者发挥**：官方 description 逐字为 "…for people and AI agents"，README 亦写明 "Agents can use the same open-source APIs; your application supplies the model and tool orchestration."（F-058/F-072）。这是官方定位，也是本知识包归入 AI 产品域的依据。

## 勘误四张清单

### ① 日期/版本表

| 博文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| TypeScript / Apache-2.0（F-003） | GitHub API `language=TypeScript`、`license.spdx_id=Apache-2.0`（F-056） | ✅ 一致 |
| Luckysheet 已归档、官方称升级成 Univer（F-002） | `dream-num/Luckysheet` `archived=true`，description "Luckysheet upgraded to Univer"，homepage 指向 univer 仓库（F-059） | ✅ 一致 |
| 开发 Node.js ≥22.18 / Headless ≥18.17（F-049） | README "Headless Univer supports Node.js `>=18.17.0`. Developing this monorepo requires Node.js `>=22.18`."（F-069） | ✅ 逐字一致 |
| Chrome 88 编译、缺 `Intl.Segmenter` 补 polyfill（F-050/F-051） | README "compiled with a Chrome 88 target"；polyfill 建议 `@formatjs/intl-segmenter`（F-069） | ✅ 一致 |
| React 18 / 19 都支持（F-012） | README：视图层基于 React 18，支持 18 与 19，**另对 React 16.9+/17 提供最小兼容支持**（F-069） | ✅ 博文为不穷尽列举，正文按官方补全 |

### ② 成效数字溯源表

| 博文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| 标题「Github 26k star」（F-001） | 2026-11-20 GitHub API 实测 **30,434**（Fork 2,755 / issues 198 / subscribers 849，F-057）。博文 2026-11-19 发布，两者相隔一天 | ⚠️ **时效/口径差异，非造假**。Star 为动态数字，但一天内不可能增长约 4.4k，判为博文采用了滞后快照；正文统一采用官方现值并标注时点，禁止写死 26k |
| 「十几行代码就够了」（F-011） | 官方 Quick start = 安装 1 行 + HTML 容器 1 行 + TypeScript 约 14 行（F-064） | ✅ 口径成立；但不含业务数据接入与生命周期等待，正文注明"最小可运行示例" |
| 「十几分钟就能看到效果」（F-055） | 无官方数据 | ➖ 作者体验，正文标为观点、不量化 |

### ③ 口径对照表

| 博文声明（F） | 官方口径 | 结论 |
|--------------|---------|------|
| 「接 OpenClaw、DeepSeek Harness 的也有现成集成」（F-031） | 官方生态表列 **5 个**仓库：Univer CLI、DeepSeek Harness、WorkBuddy（Developer preview）、OpenClaw、Univer SDK Skills（F-070） | ⚠️ 博文漏列 WorkBuddy 与 SDK Skills，属不穷尽列举；正文按官方补全 |
| 「CLI 能处理 Excel、Word、PPT 文件」（F-031） | `univer-cli` SKILL.md 定义五类 Unit：Sheet / Doc / Slide / **Base** / **Board**（F-071） | ⚠️ 博文为简化表述；正文补全五类 |
| 「跟集成 OnlyOffice 比，不用另起一套文档服务器」（F-053） | 开源子集确实纯前端；但官方 Server SDK 正是承载协同、历史与文件转换的后端组件（F-060/F-062） | ⚠️ **仅对开源子集成立**。正文限定为「开源核心不需要服务端；启用商业协同时仍需 Server SDK」 |
| 「跟 Handsontable、AG Grid 比」（F-052） | 官方 SDK 对比页对象为 SpreadJS / Handsontable / ONLYOFFICE / Syncfusion（未含 AG Grid，F-072） | ⚠️ 对比对象为作者自选；正文标注为作者观点，不写成官方评测 |
| 「开源版基本够了」（F-045） | 官方 compare 页：开源版仅含前端编辑器、不含服务端组件，**且开源版公式引擎性能低于商业版**（F-072） | ⚠️ 结论方向成立但博文未披露性能差异；正文在选型页补上这一边界 |

### ④ 引文逐字 / 命令逐字核对表

| 博文引用（F） | 官方原文核对 | 结论 |
|--------------|-------------|------|
| `pnpm add @univerjs/presets @univerjs/preset-sheets-core`（F-008） | README Quick start 逐字一致（F-064） | ✅ |
| `createUniver({ ... UniverSheetsCorePreset({ container: 'app' }) ... })` + `univerAPI.createWorkbook({})`（F-010） | README 逐字一致，另要求 `<div id="app" style="height: 100vh"></div>`（F-064） | ✅ |
| 报价单 `setValues` 四行、`setValue(4)`、`onCalculationResultApplied()`、D4=200、`workbook.save()`（F-014~F-019） | README 报价单示例逐字一致；官方另有 `.catch(console.error)`，并明确恢复须 `createWorkbook(JSON.parse(saved))` **而非创建空白 workbook**（F-067） | ✅ 逐字一致，博文省略 catch 与恢复分支 |
| 「要等生命周期进入 Steady、公式引擎就绪后再改」（F-015） | 官方示例在 `setValues` 前有**完整 `await new Promise` 等待代码**：检查 `getCurrentLifecycleStage() >= LifecycleStages.Steady`，否则监听 `LifeCycleChanged` 直到 Steady（F-066） | ⚠️ **博文把关键等待逻辑压成一句注释**。照抄博文代码在新 workbook 上可能因公式控制器未就绪而取不到重算结果；examples 必须补回官方等待段 |
| `npx skills add dream-num/skills -s univer-cli -g`（F-028） | 官方现行：`npx skills add dream-num/skills --skill build-with-univer`（skills 仓库 README）、`--skill univer-integrate`（安装文档）；`-s` 简写未见于官方现行文档；`univer-cli` skill 自身安装为 `npm install -g univer-cli` + `univer doctor`（F-070/F-071） | ⚠️ **实体真实、写法已演进**。`skills/univer-cli` 目录确实存在但标注 `hidden: true`；官方并提示旧教程引用 `dream-num/univer-sdk-skills` 应改用 `dream-num/skills`。正文给出官方现行命令，博文写法登记为历史/简写口径 |
| `git clone ... pnpm install pnpm dev`（F-048） | README Local development 逐字一致（F-072） | ✅ |
| `BeforeCommandExecute` / `CommandExecuted`（F-025） | README 逐字："`BeforeCommandExecute` can inspect and cancel an execution; `CommandExecuted` reports executions to listeners"（F-068） | ✅ |
| Command / Mutation / Operation 三类定义（F-035~F-037） | README 三类定义逐字同向（F-068） | ✅ |

## 博文未覆盖、但选型必须知道的官方边界

以下为 R 阶段官方核验新增事实（F-060~F-072），博文未提及，本知识包在 concepts 中补齐：

1. **三 SDK 分层**：Web SDK / Server SDK / AI SDK，Apache-2.0 仅覆盖 Web SDK 核心（F-060/F-061）。
2. **开源版公式引擎性能低于商业版**；开源版不含服务端组件（F-072）。
3. **版本纪律**：所有 `@univerjs/*` 须同版本，商业包须匹配 release line；另有 API Stability Policy（F-065）。
4. **两种集成模式**：preset mode 与 plugin mode；plugin mode 默认不含 Facade API（F-072）。
5. **React/Rxjs 为 peerDependencies**（不阻止 Vue/Angular 使用）；**mobile support 仍为 experimental**（F-072）。
6. **快照 ≠ 文件**：`workbook.save()` 是内部 JSON 快照，与 XLSX 导入导出分属两条能力，后者走 Server SDK 的 Exchange（OOXML↔Unit 映射，F-067/F-072）。
7. **agent 治理的官方形态**：AI SDK 建立在 Headless 之上，Worktree 隔离草稿 + readback 自检 + viewer 预览 + 人工 merge，且官方明确 "Command success is not correctness evidence"（F-071/F-072）。

## 核验方法与局限

1. **方法**：GitHub REST API 取仓库不可伪造元数据（创建时间/Star/语言/许可证/归档状态）；jsDelivr 镜像取 `dev` 分支 README 全文逐段比对命令、参数与表述；官方 compare 页与 installation 文档核对授权边界与运行时；GitHub Contents API 核对 `dream-num/skills` 下 skill 实体清单。
2. **局限**：① **未实际安装运行 Univer**，所有代码级结论以官方 README 示例为准，examples 属「官方可照做流程」而非本知识包实机验证；② 商业版能力、水印具体表现与授权价格未核验（需商务/法务确认）；③ 官方 compare 页信息更新于 2026-10，功能矩阵可能继续变动；④ Star 等动态数字为 2026-11-20 时点快照。
3. **复核安排**：`stale_after: 2026-12-31` 前复核 Star 量级、skills 仓库命令写法演进、开源/商业功能矩阵变动、CLI 是否结束 Developer preview。
