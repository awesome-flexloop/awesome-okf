---
okf_version: "0.2"
type: Example
title: "实操 1：十几行代码嵌一个表格编辑器"
description: "Sheets Core preset 完整嵌入流程（官方 Quick start 逐字）、容器与 CSS、组件卸载 dispose、版本一致性纪律"
tags: [univer, quickstart, preset, example, vite]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-20T10:30:00+08:00" }
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

# 实操 1：十几行代码嵌一个表格编辑器

> **可复现性声明**：本页命令与代码取自官方 `dev` 分支 README「Quick start」并逐字核对（F-008/F-010/F-064），属"官方可照做流程"。**本知识包未实机安装运行**，运行前请以官方文档当前版本为准。

## 前置

- 使用打包器的浏览器应用（官方以 Vite 为例）；
- 版本号：**所有 `@univerjs/*` 包必须保持同版本**，商业包须匹配对应 release line（F-065）；
- 组件框架：视图层基于 React 18（支持 18/19），React 与 Rxjs 为 peerDependencies，**不阻止在 Vue / Angular 中使用**（F-012/F-069/F-072）。

## 步骤 1 · 安装

```bash
pnpm add @univerjs/presets @univerjs/preset-sheets-core
```

（F-008；官方 README 逐字一致）

## 步骤 2 · 准备容器

```html
<div id="app" style="height: 100vh"></div>
```

（F-009/F-064；官方示例带 `height: 100vh`，容器高度为 0 是常见的"编辑器没显示"原因）

## 步骤 3 · 初始化

```ts
import { UniverSheetsCorePreset } from '@univerjs/preset-sheets-core'
import UniverPresetSheetsCoreEnUS from '@univerjs/preset-sheets-core/locales/en-US'
import { createUniver, LocaleType, mergeLocales } from '@univerjs/presets'
import '@univerjs/preset-sheets-core/lib/index.css'

const { univerAPI } = createUniver({
  locale: LocaleType.EN_US,
  locales: {
    [LocaleType.EN_US]: mergeLocales(UniverPresetSheetsCoreEnUS),
  },
  presets: [
    UniverSheetsCorePreset({
      container: 'app',
    }),
  ],
})

univerAPI.createWorkbook({})
```

（F-010；官方 Quick start 逐字一致）

页面此时就是一个可编辑表格：工具栏、公式栏、合并单元格、冻结窗格、筛选排序、数据验证、条件格式、批注均在开源范围内（F-007/F-063）。官方明示该示例 **"needs no commercial Univer license or Server SDK"**（F-064）。

## 步骤 4 · 组件卸载时释放

官方要求保留 `createUniver` 返回的 `univer` 实例，并在组件卸载时调用 `dispose()`（F-012/F-065）：

```ts
const univer = createUniver({ /* 同上 */ })
// 组件 unmount 时
univer.dispose()
```

> 注意：官方示例解构的是 `univerAPI`（便于后续操作内容），但生命周期管理需要 `univer` 实例本身。只保留 `univerAPI` 而丢弃实例，会导致无法正确释放。

## 常见偏差对照

| 现象 | 原因 | 处理 |
|------|------|------|
| 页面空白 | 容器无高度 | 给容器显式高度（官方 `height: 100vh`） |
| 插件冲突 / 功能异常 | 同时引入 preset 与 preset 已含的插件，或版本不一致 | 二选一；统一 `@univerjs/*` 版本（F-065/F-072） |
| 需要精细控制插件顺序或懒加载 | preset 同步加载 | 改用 **plugin mode**；注意它默认不含 Facade API，需自行引入 facade 包（F-072） |
| 移动端表现异常 | Sheets mobile support 仍为 experimental；Core preset 只注册桌面 UI | 按官方文档显式组装 mobile 插件，勿在桌面 preset 初始化后追加（F-072） |

## 下一步

- [实操 2 · 报价单与生命周期等待](01-quotation-with-lifecycle.md)——把业务数据接进这张表
- [概念 02 · 嵌入与 Facade API](../concepts/02-embed-and-facade-api.md)
