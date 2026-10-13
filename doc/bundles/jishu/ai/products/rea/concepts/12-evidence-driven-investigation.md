---
type: Concept
title: "REA 三类证据驱动调查"
description: "用原生算术、Electron 导出与浏览器请求解释指令、静态图、运行时窗口各自能支持的结论"
sources:
  - id: site
    resource: ../references/official-site-source.md
  - id: facts
    resource: ../references/facts.md
generated: {by: "process:seven-concepts-e", at: "2026-10-12"}
status: draft
---

# REA 三类证据驱动调查

官网指南 W05~W08 从具体问题进入分析：DX-Ball 怎样计算声像、Notes 怎样导出 CSV、点击网页按钮发起什么请求。三者分别依靠指令与数据、跨进程静态关系、运行时观察。工具结果应附目标身份、范围和源码位置，助手的解释再从这些证据推导。

## 原生算术

DX-Ball 1.07 的函数 `0x406400` 最初伪代码只显露 `__ftol()`。检查输入指令可见 `[EBP+8]` 整数参数；检查调用者可见砖块横坐标转为 `20 + 30 * tile_x`；读取引用数据得到 1.5625、500.0 与 scale（F-153~F-155）。

恢复的浮点路径依次乘 1.5625、减 500、乘 scale，最后转整数。scale=1 时，x=0/320/640 在转换前对应 -500/0/500。函数名来自维护源码，不应把可读名称当成 stripped 目标已存在的符号。

```powershell
npx -y rea-agents@latest function "D:/analysis/DX-Ball.exe" 0x406400 --provider ghidra --json
```

此地址仅适用于案例目标版本；换程序或版本须重新定位。拿到结果后保留指令、caller、引用常量及未解析项。不能用一个算术公式代替 x87 精度、转换和 ABI 的验证，更不能宣称已经恢复整游戏。

## Electron 文件路径

Notes 的按钮调用 `notes.exportCsv()`；preload 将它映射为 `ipcRenderer.invoke("notes:export")`；主进程 handler 调用 `toCsv`，写入 `app.getPath("downloads")/notes.csv`（F-141~F-143）。

静态图中的字面通道有一个唯一 handler，能帮助跟随路径。判断依据应落在具体代码：通道文本、调用位置、handler 和文件写入参数。若字段是动态计算、存在多个 handler 或路径由运行时注入，回答中应保留未解析状态。

Notion 展示了这一边界：动态 `__electronApi` 与 `channel=null` 的 trace 仅得 partial 图，17 节点、16 边、零 terminal；完整剪贴板路线由额外 wrapper 阅读补齐，不是工具自动获得的完整配对图（F-156~F-159）。SQLite 的 MessageChannel port handoff 也只获得源码解释，未捕获真实 SQL 会话。

## 浏览器观察窗口

先由用户启动独立浏览器调试实例，再发现目标。下面要求已有 `127.0.0.1:9222` 调试端点；`TARGET_ID` 必须换成发现结果中目标页面的 ID：

```powershell
npx -y rea-agents@latest list-browser-targets http://127.0.0.1:9222 --json
npx -y rea-agents@latest inspect-web-page http://127.0.0.1:9222 TARGET_ID --observation-ms 10000 --include-accessibility-text --include-json-body-shapes --json
```

观察开始后用户再点击 Export notes。上游 Notes 记录为 GET notes.json、HTTP 200、application/json、`notes[]` 结构，随后前端构建 Blob 下载（F-144/F-145）。REA 记录请求；点击由独立控制器完成。attach 之前的请求不在观察窗口内。

需要解释请求与导出关系时，再读取脚本：

```powershell
npx -y rea-agents@latest inspect-web-page http://127.0.0.1:9222 TARGET_ID --include-script-sources --json
```

请求响应形状不能独立证明下载内容正确。须核对 `fetch("./notes.json")`、字段到 CSV 的转换和 Blob 构造；浏览器导出与 Electron 主进程写文件也不能混为一个实验。

## 从结果到结论

| 证据 | 可支持 | 仍需补充 |
|---|---|---|
| 指令、caller、数据字节 | 已定位函数的计算解释 | ABI、边界输入、编译器与应用集成 |
| 静态模块与 IPC 图 | 代码中的潜在路径 | 动态通道、实际按钮执行与错误传播 |
| 有界网络记录 | 窗口内所选页面的请求 | 窗口前行为、下载结果、其他进程 |
| 提取 helper harness | 给定输入的函数行为 | 原应用环境、共享状态与系统 API |

每一步提出能被证据回答的问题；若未解析项影响结论，就缩小声明或补新的调查。unknowns 数量少、返回字段齐全、图中无歧义都不是独立可靠性证明。

本轮分析命令未经本机执行。上游指南使用 REA 4.1.0；本页命令形态对照固定 6.4.0，历史运行记录与当前接口核验分开保存。

## 相关概念

- [Notes 首次调查](../examples/notes-first-investigation.md)
- [五项 showcase](../examples/showcase-cases-example.md)
- [重建与验证](13-reconstruction-verification.md)
