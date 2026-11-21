---
okf_version: "0.2"
type: Reference
title: "Univer 博文事实清单（信源登记）"
description: "微信公众号《Github 26k star，网页里嵌一个 Excel》的 F 编号事实登记与官方核验状态（F-001~F-072）"
tags: [univer, article-source, fact-registry, blog-article, office-sdk]
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-11-20T09:30:00+08:00" }
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

# 博文事实清单（article-source）

> 本文件是 F 编号事实的**双份登记之一**，另一份在 spec `.trae/specs/univer-office-sdk-okf-wiki/facts.md`，两集合正则比对一致：F-001~F-072 连续无跳号。
> 类型：O=客观事实，V=作者观点/体验，S=厂商自述。核验：✅ 官方一致 ｜ ⚠️ 口径/时效差异（详见 [verification.md](verification.md)）｜ ➖ 无需外部核验。
> 博文：公众号「Github喵」原创，2026-11-19 14:30 四川发布。F-001~F-055 出自博文，F-056~F-072 为 2026-11-20 官方一手核验补充。
> **信源距离**：第三方开源推介号转述（非项目方发布）；经 GitHub REST API、dev 分支 README、官方文档与功能对比页升级为官方一手交叉核验。

## A. 博文元信息（F-001 ~ F-003）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-001 | O | 博文标题《Github 26k star，网页里嵌一个 Excel，十几行代码就够了！》；公众号「Github喵」，原创，2026-11-19 14:30，四川 | ➖ |
| F-002 | O | 推介对象 Univer 是 Luckysheet 团队重写的新一代表格引擎；Luckysheet 已归档，官方说法是升级成 Univer | ✅ F-059 |
| F-003 | O | TypeScript 编写，Apache-2.0 协议 | ✅ F-056 |

## B. 定位与形态（F-004 ~ F-007）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-004 | O | 形态是一套 SDK，把电子表格和文档编辑器嵌进自己的产品，数据和权限都在自己手里 | ✅ F-058/F-061 |
| F-005 | O | 把 AI agent 当成正式用户，人和 AI 调的是同一套 API | ✅ F-058/F-068 |
| F-006 | O | 开源部分的入口是 Sheets Core 这个 preset | ✅ F-064 |
| F-007 | O | 工具栏、公式栏、合并单元格、冻结窗格、筛选排序、数据验证、条件格式、批注，开源版都带 | ✅ F-063 |

## C. 十几行代码嵌入（F-008 ~ F-012）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-008 | O | 安装命令 `pnpm add @univerjs/presets @univerjs/preset-sheets-core` | ✅ F-064 逐字一致 |
| F-009 | O | 页面放一个 id 为 app 的容器，然后初始化 | ✅ F-064 |
| F-010 | O | 初始化代码：`createUniver({ locale, locales: mergeLocales(...), presets: [UniverSheetsCorePreset({ container: 'app' })] })` + `univerAPI.createWorkbook({})` | ✅ F-064 逐字一致 |
| F-011 | O | 跑起来就是一个完整的表格编辑器；标题称「十几行代码就够了」 | ✅ F-064（示例为安装 1 行 + HTML 1 行 + TS 约 14 行） |
| F-012 | O | 视图层基于 React，18 和 19 都支持；放进 Vue 之类框架也行；组件卸载时调 `univer.dispose()` | ✅ F-065/F-069（官方另有 16.9+/17 最小兼容，博文未列） |

## D. Facade API、快照与 Headless（F-013 ~ F-021）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-013 | O | 应用开的口子叫 Facade API，workbook、sheet、range 一层层拿下去 | ✅ F-067 |
| F-014 | O | 报价单示例：`A1:D4` 写入四行，含 `=B2*C2`、`=B3*C3`、`=SUM(D2:D3)` | ✅ F-067 逐字一致 |
| F-015 | O | 代码注释提示「新建的 workbook 要等生命周期进入 Steady、公式引擎就绪后再改」，但博文代码段**未包含等待逻辑** | ⚠️ F-066 官方示例有完整 `await` 等待代码 |
| F-016 | O | 业务代码或 agent 把座位数从 2 改成 4：`sheet.getRange('B2').setValue(4)` | ✅ F-067 |
| F-017 | O | `univerAPI.getFormula().onCalculationResultApplied().then(() => ...)`，合计重算为 200 | ✅ F-067（官方另有 `.catch(console.error)`） |
| F-018 | O | `workbook.save()` 拿到一份 JSON 快照，存数据库还是 localStorage 自己定 | ✅ F-067 |
| F-019 | O | 下次把快照传给 `createWorkbook` 就能原样恢复 | ✅ F-067（官方强调须「替代创建空白 workbook」） |
| F-020 | O | 这套 API 不依赖浏览器；Node.js 里不挂编辑器也能跑，官方叫 Headless 模式 | ✅ F-061 |
| F-021 | O | Headless 的内容模型和公式计算跟浏览器里是同一份代码；可用于后端批量生成报价单、校验用户填的数据 | ✅ F-061/F-068 |

## E. AI agent 与命令事件（F-022 ~ F-031）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-022 | O | Univer 定位是人和 agent 共用的 Office SDK | ✅ F-058 |
| F-023 | O | agent 不用模拟点击、不用自己拼 xlsx，直接调 Facade API 写值、写公式、读结果 | ✅ F-058/F-067 |
| F-024 | O | 模型和工具编排由应用负责，Univer 只管表格这一层 | ✅ F-058 逐字同向 |
| F-025 | O | 表格里每次修改都走命令系统；`univerAPI.Event` 有 `BeforeCommandExecute` 和 `CommandExecuted` 两个事件 | ✅ F-068 |
| F-026 | O | 前一个能在执行前检查甚至直接取消；挂监听可拦下越权改动、改动留记录 | ✅ F-068 |
| F-027 | O | 官方做了 Univer CLI，给 agent 一个本地的 Office 工作区 | ✅ F-070/F-071 |
| F-028 | O | 安装命令 `npx skills add dream-num/skills -s univer-cli -g`；在 Claude Code、Codex 这类 agent 里装 Skill | ⚠️ F-070 官方现行写法不同 |
| F-029 | O | 直接说要一张带公式、数据验证和条件格式的工资表 | ➖ 用法示例 |
| F-030 | O | agent 在隔离的草稿里改完，自己读回来核对一遍，再给一个本地预览链接，合并还是丢掉由你决定 | ✅ F-071/F-072（Worktree + readback + viewer + 人工 merge） |
| F-031 | O | 接 OpenClaw、DeepSeek Harness 的也有现成集成；CLI 能处理 Excel、Word、PPT，文件转换属单独授权 | ✅ F-070/F-072（官方另列 WorkBuddy；CLI 支持五类 Unit 不止三种） |

## F. 命令系统与插件分层（F-032 ~ F-040）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-032 | V | 做过编辑器的都知道，单个功能好写，麻烦在功能之间的牵连 | ➖ 作者判断 |
| F-033 | O | 例：在开着筛选的区域里插入一行，表格内容要变，筛选范围也得跟着变；撤销时两样都得回去 | ✅ F-068 官方同例 |
| F-034 | O | Univer 让插入行 Command 收集各插件交上来的改动，基础行变更与筛选范围变更合成一次执行，撤销记录只记一条 | ✅ F-068 |
| F-035 | O | 动作分三类之一：Command 编排一次业务操作 | ✅ F-068 |
| F-036 | O | Mutation 是真正改内容的变更，能存进快照 | ✅ F-068 |
| F-037 | O | Operation 只改临时状态，比如滚动位置、打开了哪个面板 | ✅ F-068 |
| F-038 | O | 实时协同也建在 Mutation 之上，把变更打包后做 OT 合并 | ✅ F-068（官方称 changesets） |
| F-039 | O | 插件分层：底层 Core、渲染引擎、公式引擎 → 中间 Sheets 产品插件 → 上层筛选/数据验证功能插件，逻辑和界面各拆一个包 | ✅ F-068 |
| F-040 | V | 想加自定义功能，照着官方的筛选插件把结构抄一遍就行 | ✅ F-068 有 walkthrough |

## G. 授权边界（F-041 ~ F-046）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-041 | O | 开源仓库是 Web SDK 核心：Sheets 和 Docs 编辑、公式引擎、渲染引擎、Facade API、Headless 运行；Apache-2.0，商用没问题 | ✅ F-061/F-062 |
| F-042 | O | 不在开源范围：xlsx 导入导出、图表、透视表、实时协同、版本历史、打印和导出 PDF | ✅ F-062/F-072 |
| F-043 | O | 这些属于商业插件和 Server SDK；能免费试用，但有水印和功能限制 | ✅ F-062 逐字同向（Freemium） |
| F-044 | O | 官方在线演示里不少是商业版能力，别看完演示就以为全都开源 | ✅ F-072 |
| F-045 | V | 只放一个能算公式的表格、数据用 JSON 快照存，开源版基本够了 | ✅ F-067 官方明示无需商业许可 |
| F-046 | V | 要让用户上传、下载 Excel，就得把授权预算算进去 | ✅ F-062/F-072 |

## H. 源码与运行时（F-047 ~ F-051）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-047 | O | 仓库自带一个 Sheets 加 Docs 的开发工作台 | ✅ F-072 |
| F-048 | O | `git clone https://github.com/dream-num/univer.git` → `pnpm install` → `pnpm dev` | ✅ F-072 逐字一致 |
| F-049 | O | 本地开发仓库要 Node.js 22.18 以上；只在 Node 里跑 Headless，18.17 以上就够 | ✅ F-069 逐字一致 |
| F-050 | O | 浏览器端按 Chrome 88 编译 | ✅ F-069 |
| F-051 | O | 老环境缺 `Intl.Segmenter` 的补个 polyfill | ✅ F-069 |

## I. 对比与结论（F-052 ~ F-055）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-052 | V | 跟 Handsontable、AG Grid 这类数据表格比，Univer 多了完整的公式引擎和文档模型，更像把 Office 内核嵌进产品 | ➖ 作者观点；官方对比页对象为 SpreadJS/Handsontable/ONLYOFFICE/Syncfusion |
| F-053 | V | 跟集成 OnlyOffice 比，不用另起一套文档服务器，开源部分纯前端就能跑 | ⚠️ 仅开源子集成立；商业协同需 Server SDK |
| F-054 | O | 代价是核心之外的文件导入导出要付费 | ✅ F-062 |
| F-055 | V | 建议先把 Sheets Core 跑起来，十几分钟就能看到效果 | ➖ 作者体验，未实测 |

## J. 官方核验补充（F-056 ~ F-072，2026-11-20）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-056 | O | GitHub API：`dream-num/univer`，id 543101941，owner 类型 Organization，创建 2022-09-29，默认分支 `dev`，TypeScript，`license.spdx_id=Apache-2.0`，`archived=false` | ✅ |
| F-057 | O | 时点快照 2026-11-20：**Star 30,434**、Fork 2,755、open issues 198、subscribers 849；最近 push 2026-11-19 | ✅ 动态数字 |
| F-058 | O | 官方 description 逐字："Build your own AI office with Univer Office SDK. Bring editing, calculation, collaboration, and file processing into your product for people and AI agents."；homepage `https://univer.ai` | ✅ |
| F-059 | O | `dream-num/Luckysheet`：`archived=true`，description "Luckysheet upgraded to Univer"，homepage 指向 univer 仓库，最后 push 2025-08-19 | ✅ F-002 成立 |
| F-060 | O | 官方三 SDK 分层：**Web SDK**（基础：内容模型、编辑、渲染、公式、Facade）、**Server SDK**（协同、编辑历史、Office 文件导入导出）、**AI SDK**（接既有 agent 与工作流） | ✅ |
| F-061 | O | 官方明确本仓库仅以 Apache-2.0 提供 Web SDK 核心：content models/snapshot、plugin & DI、command system、formula & rendering engines、Facade APIs、UI foundation、Sheets/Docs 编辑；含开源 Headless 内容能力 | ✅ |
| F-062 | O | 官方：商业 Web SDK 插件、Server SDK、开源基础之外的 AI SDK 能力**单独分发与授权**；Freemium 评估含 **watermarks and feature limits**；Server SDK 承载 real-time collaboration、revision history、Office file conversion | ✅ |
| F-063 | O | 官方 Open-source capabilities 表：Sheets 编辑与布局（cell styles/merged cells/rich text/freeze panes/floating images/undo-redo）、数据与计算（formulas/defined names/filtering/sorting/data validation/conditional formatting/hyperlinks/comments/find & replace）、Docs | ✅ |
| F-064 | O | 官方 Quick start 安装命令、`<div id="app" style="height: 100vh"></div>` 容器、`createUniver` 示例与博文逐字一致；并明示 "needs no commercial Univer license or Server SDK" | ✅ |
| F-065 | O | 官方：组件框架需保留 `createUniver` 返回的 `univer` 实例并在卸载时 `univer.dispose()`；所有 `@univerjs/*` 须同版本，商业包须匹配 release line，另有 API Stability Policy | ✅ |
| F-066 | O | **官方报价单示例含完整 `await new Promise`（检查 `LifecycleStages.Steady` / 监听 `LifeCycleChanged`）等待代码**，注释为 "Wait for formula controllers before editing a newly created workbook" | ⚠️ 博文仅留注释 |
| F-067 | O | 官方报价单逐字：`setValues` 四行、`setValue(4)` 注 "An application control or agent can make the same edit."、`onCalculationResultApplied().then(...).catch(console.error)`、D4=200、`workbook.save()` 为含插件数据的 JSON 快照、恢复须 `createWorkbook(JSON.parse(saved))` 而非空白 workbook、快照持久化与 XLSX 导入导出分离 | ✅ |
| F-068 | O | 官方架构逐字：Command/Mutation/Operation 三类定义、`IUndoRedoService` 记录 forward+inverse mutations、筛选区插入行合成单条 undo、changesets+OT、History 从 snapshot+changesets 重建、`univerAPI.Event` typed events 与 `univerAPI.Enum`、`BeforeCommandExecute` 可检查并取消、`CommandExecuted` 通知、listeners 返回 disposables、插件 Controllers/Services 与 `@univerjs/design`/`ui`/`icons` 分层、interceptor 扩展点 | ✅ |
| F-069 | O | 官方 Runtime compatibility 逐字：Headless Node.js `>=18.17.0`、开发 monorepo `>=22.18`、Chrome 88 编译目标、浏览器表 Edge≥88/Firefox≥90/Chrome≥88/Safari≥14.1/Electron≥12、`Intl.Segmenter` polyfill 建议 `@formatjs/intl-segmenter`、**React 18 构建且支持 18/19，对 16.9+/17 提供最小兼容** | ✅ |
| F-070 | O | 官方 CLI/生态表五仓库：Univer CLI、Univer Office for DeepSeek Harness、**Univer Office for WorkBuddy（Developer preview）**、Univer Office for OpenClaw、Univer SDK Skills；官方 skills 仓库 README 主推 `npx skills add dream-num/skills --skill build-with-univer`，安装文档用 `--skill univer-integrate`，并提示旧教程的 `dream-num/univer-sdk-skills` 应改用新命令 | ⚠️ 与 F-028 写法差异 |
| F-071 | O | `skills/univer-cli` 目录确实存在，其 SKILL.md 标注 `hidden: true`，安装方式为 `npm install -g univer-cli` + `univer doctor`；CLI 面向 `.univer` 多 Unit 文件、worktree、readback、viewer handoff，支持 Sheet/Doc/Slide/Base/Board 五类 Unit；明确 "Command success is not correctness evidence" | ✅ 概念成立 |
| F-072 | O | 官方 compare 页（信息更新 2026-10）：**开源版仅含前端编辑器、不含服务端组件，且开源版公式引擎性能低于商业版**；图表/透视表部分项标 `v1.3.0+ · Pro`；XLSX 导入导出属 Full Office SDK 列。README 声明 demos "show more than the default open-source setup"。安装文档另有 preset/plugin 两种模式、plugin mode 默认不含 Facade、React/Rxjs 为 peerDependencies（不阻止 Vue/Angular）、mobile support 仍 experimental；本地开发命令与 F-048 一致 | ✅ |

## 双份一致性核对

- 本文件 F 编号集合 = spec `facts.md` 集合 = {F-001 … F-072}，连续无跳号。
- V 阶段补充事实：无（所有核验事实在 R 阶段一次性登记，双份回转完成）。
