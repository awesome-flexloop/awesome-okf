---
okf_version: "0.2"
type: Example
title: "实操 2：报价单、生命周期等待与快照恢复"
description: "官方报价单示例完整版——补齐博文省略的 Steady 生命周期等待段、公式重算读回、JSON 快照持久化与恢复"
tags: [univer, facade-api, formula, lifecycle, snapshot, example]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-20T10:35:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/7WCDC4R7mxqFRHMP0Zf9hA
  - id: official-readme
    url: https://github.com/dream-num/univer/blob/dev/README.md
---

# 实操 2：报价单、生命周期等待与快照恢复

> **可复现性声明**：本页为官方 README「Connect your application to editable content」示例的完整重组（F-066/F-067）。博文把**生命周期等待段压成一句注释**，本页按官方补齐。**本知识包未实机运行**。

## 为什么这一页值得单独写

博文代码开头只有一行注释：「新建的 workbook 要等生命周期进入 Steady、公式引擎就绪后再改」（F-015）。官方示例在写入数据前有完整的 `await` 等待逻辑（F-066）。缺了它，在新建 workbook 后立即写公式，可能因公式控制器尚未注册而取不到重算结果——这是"照抄博文跑不通"的高发点。

## 步骤 1 · 等待公式控制器就绪（官方原文补齐）

```ts
// Wait for formula controllers before editing a newly created workbook.
await new Promise<void>((resolve) => {
  if (univerAPI.getCurrentLifecycleStage() >= univerAPI.Enum.LifecycleStages.Steady) {
    resolve()
    return
  }
  const listener = univerAPI.addEvent(univerAPI.Event.LifeCycleChanged, ({ stage }) => {
    if (stage === univerAPI.Enum.LifecycleStages.Steady) {
      listener.dispose()
      resolve()
    }
  })
})
```

（F-066；`univerAPI` 来自 [实操 1](00-embed-sheets-core.md) 的 `createUniver` 返回值）

## 步骤 2 · 写入报价单数据与公式

```ts
const workbook = univerAPI.getActiveWorkbook()!
const sheet = workbook.getActiveSheet()

sheet.getRange('A1:D4').setValues([
  ['Item', 'Quantity', 'Unit price', 'Amount'],
  ['Seats', 2, 25, '=B2*C2'],
  ['Support', 1, 100, '=B3*C3'],
  ['Total', '', '', '=SUM(D2:D3)'],
])
```

（F-014/F-067，官方逐字一致）

## 步骤 3 · 应用代码或 agent 改一个格子，读回重算结果

```ts
// An application control or agent can make the same edit.
sheet.getRange('B2').setValue(4)

univerAPI.getFormula().onCalculationResultApplied().then(() => {
  console.log(sheet.getRange('D4').getValue()) // 200
  localStorage.setItem('quotation', JSON.stringify(workbook.save()))
}).catch(console.error)
```

（F-016/F-017/F-018/F-067）

- 座位数 2→4 后合计自动重算为 **200**；
- 官方示例带 `.catch(console.error)`，博文省略；
- `workbook.save()` 返回**含 workbook 与已注册插件数据的 JSON 快照**，持久化位置由应用决定（数据库 / localStorage 均可）。

> 这一句是"人和 agent 共用同一张表"的落点（F-023）：改值的可以是界面控件，也可以是 agent，走的都是 Facade API。

## 步骤 4 · 下次加载时恢复快照

官方明确要求：初始化后**用快照创建 workbook，而不是先建空白 workbook 再灌数据**（F-019/F-067）：

```ts
const saved = localStorage.getItem('quotation')
if (saved) {
  univerAPI.createWorkbook(JSON.parse(saved))
}
```

## 边界检查（写完别漏）

| 检查项 | 结论 |
|--------|------|
| 快照能当 Excel 文件导出吗？ | **不能**。快照是内部 Unit 数据；XLSX 导入导出走 Server SDK 的 Exchange，属单独授权能力（F-067/F-072） |
| 这条链路需要商业许可吗？ | **不需要**。官方明示该 workflow uses only open-source packages（F-067） |
| 依赖版本 | 所有 `@univerjs/*` 同版本（F-065） |
| 计算时序 | 必须等 `Steady` + `onCalculationResultApplied()`，不能靠固定延时 |

## 延伸

- [实操 3 · agent 命令闸门与 CLI](02-agent-command-guard.md)
- [概念 02 · 嵌入与 Facade API](../concepts/02-embed-and-facade-api.md)
- [概念 01 · 授权边界](../concepts/01-three-sdk-layers-and-license-boundary.md)
