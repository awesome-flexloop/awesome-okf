---
okf_version: "0.2"
type: Concept
title: "嵌入表格与 Facade API：从十几行代码到业务数据打通"
description: "Sheets Core preset 嵌入、Facade API 三层对象、生命周期 Steady 前置、JSON 快照恢复与 Headless 同构架构"
tags: [univer, facade-api, preset, headless, snapshot, lifecycle]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-20T10:10:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/7WCDC4R7mxqFRHMP0Zf9hA
  - id: official-readme
    url: https://github.com/dream-num/univer/blob/dev/README.md
  - id: official-installation
    url: https://docs.univer.ai/guides/sheets/getting-started/installation
---

# 嵌入表格与 Facade API：从十几行代码到业务数据打通

> 概念层（How）。可照做代码见 [examples/00](../examples/00-embed-sheets-core.md) 与 [examples/01](../examples/01-quotation-with-lifecycle.md)。

## 四层结构：为什么两行安装命令就能出编辑器

Univer 把「组装编辑器」的成本收进 **preset**（预配置插件包）：

```
容器 DOM  →  createUniver + Preset  →  univerAPI（Facade）  →  workbook / sheet / range
```

1. **容器**：页面放 `<div id="app" style="height: 100vh"></div>`（F-064）。
2. **安装**：`pnpm add @univerjs/presets @univerjs/preset-sheets-core`（F-008，官方逐字一致）。
3. **初始化**：`createUniver({ locale, locales, presets: [UniverSheetsCorePreset({ container: 'app' })] })` 返回 `univerAPI`，再 `univerAPI.createWorkbook({})`（F-010）。
4. **Facade API**：应用侧唯一入口，按 `getActiveWorkbook() → getActiveSheet() → getRange()` 逐层取对象（F-013）。

官方还提示两条容易被略过的工程约束（F-065）：

- 组件框架下要**保留 `createUniver` 返回的 `univer` 实例**，卸载时调 `univer.dispose()`，否则残留渲染与事件监听；
- 所有 `@univerjs/*` 包**必须同版本**，商业包须匹配 release line；另有 API Stability Policy 约束扩展点依赖。

集成方式不止 preset 一种：官方另有 **plugin mode**，可精细控制插件选择、注册顺序与懒加载，但**默认不含 Facade API**，需自行引入 facade 包（F-072）。深定制选 plugin mode，快速上手选 preset mode。

## ⚠️ 生命周期 Steady：博文压成注释的那段代码

博文报价单示例写了一句注释「新建的 workbook 要等生命周期进入 Steady、公式引擎就绪后再改」（F-015），但**代码段没有等待逻辑**。官方 README 的同一示例在 `setValues` 之前有完整的 `await new Promise(...)`：先查 `getCurrentLifecycleStage() >= LifecycleStages.Steady`，未就绪则监听 `LifeCycleChanged` 直到进入 Steady（F-066）。

这不是风格差异，而是**可复现性差异**：新建 workbook 后立刻写公式，公式控制器可能尚未注册，`onCalculationResultApplied()` 的时序与结果都不可靠。照抄博文代码容易得到"示例跑不通"的结论，却误以为是 SDK 的问题。本知识包在 [examples/01](../examples/01-quotation-with-lifecycle.md) 补回官方等待段。

## 你的代码和用户改的是同一张表

Facade API 的关键价值不是"能读写单元格"，而是**应用代码、用户操作、AI agent 走同一个内容模型**（F-016/F-023/F-067）。官方在 `setValue(4)` 上方逐字注明 "An application control or agent can make the same edit."：

- 写入 `=B2*C2`、`=B3*C3`、`=SUM(D2:D3)`，把 B2 从 2 改成 4，合计自动重算为 **200**（F-014/F-016/F-017）；
- `onCalculationResultApplied().then(...)` 等待计算落地后读 `D4`，官方另有 `.catch(console.error)`（F-067）；
- `workbook.save()` 返回**含 workbook 与已注册插件数据的 JSON 快照**，持久化由应用决定（数据库 / localStorage 均可，F-018）；
- 恢复时须在初始化后 `univerAPI.createWorkbook(JSON.parse(saved))`，**而不是先创建空白 workbook 再灌数据**（F-019/F-067）。

> **边界**：快照是 Univer 内部 Unit 数据，不等于 Excel 文件。XLSX 导入导出走 Server SDK 的 Exchange（F-072），属商业能力。详见 [01-授权边界](01-three-sdk-layers-and-license-boundary.md)。

## Headless：同一份代码，不挂编辑器

Web SDK 的内容模型、命令系统与公式引擎可在 **Node.js 中不带 UI 复用**，官方称 Headless 模式（F-020/F-021）。浏览器编辑器、Node Headless 任务与合适合成的 Worker 共享对应插件与计算逻辑（官方称 isomorphic architecture，F-068）。

适用场景：后端批量生成报价单、服务端校验用户填写的数据、agent 在后台读写内容。运行时门槛与浏览器端不同——Headless 只要 Node.js `>=18.17.0`，而开发 monorepo 需要 `>=22.18`（F-049/F-069）。

## 运行时兼容（官方逐字）

| 项 | 值 |
|----|-----|
| Headless Node.js | `>=18.17.0` |
| 开发 monorepo | `>=22.18` |
| 编译目标 | Chrome 88；Edge≥88 / Firefox≥90 / Chrome≥88 / Safari≥14.1 / Electron≥12 |
| polyfill | 依赖 `Intl.Segmenter`，老环境建议 `@formatjs/intl-segmenter` |
| 视图层 | React 18 构建，支持 18/19，对 16.9+/17 提供最小兼容；React/Rxjs 为 peerDependencies，**不阻止 Vue/Angular** |
| 移动端 | Sheets mobile support 仍为 **experimental** |

（F-012/F-050/F-051/F-069/F-072）

## 阅读下一篇

- [03 · 命令系统与插件架构](03-command-system-and-plugin-architecture.md)——撤销为什么不会乱
- [examples/01 · 报价单完整示例](../examples/01-quotation-with-lifecycle.md)——含官方生命周期等待段
