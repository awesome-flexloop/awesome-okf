---
type: Example
title: "REA 首次调查 Notes CSV 导出"
description: "从按钮沿 preload、IPC 与主进程定位文件路径，并独立检查 CSV formatter 的引号转义"
sources:
  - id: site
    resource: ../references/official-site-source.md
  - id: facts
    resource: ../references/facts.md
generated: {by: "process:seven-concepts-e", at: "2026-10-12"}
status: draft
---

# REA 首次调查 Notes CSV 导出

官网六文件 Notes fixture 包括 package.json、HTML 和四个 JS 文件。它把导出行为拆成渲染器、preload、主进程与 formatter，适合练习“定位代码，再检验预测”（F-141~F-143）。本轮不安装或启动 Electron。

## 输入与静态检查

准备 Node.js/npm、已授权的示例目录。官网 [Notes ZIP](https://rea.tools/examples/notes-example.zip) 包含完整目录；解压到独立位置，先读 package.json，不执行应用启动脚本。以下路径须换成实际目录：

```powershell
npx -y rea-agents@latest analyze-javascript-application "D:/analysis/notes-example" --json
```

问助手：“Export notes 后 CSV 写到哪里，有哪些字段？回答附文件与行号。”上游 4.1.0 结果中，`normalized_result.summary.ipc` 记录一个字面通道、一个 renderer transmission 与一个 main handler，唯一配对且无歧义。6.4.0 的输出布局可能不同，不能把历史字段形状当作永不变更的接口。

## 跟随导出

1. `renderer.js` 的 click listener 调用 `window.notes.exportCsv()`。
2. `preload.js` 通过 contextBridge 暴露 API，调用 `ipcRenderer.invoke("notes:export")`。
3. `main.js` 的 `ipcMain.handle("notes:export", ...)` 调用 `toCsv(notes)`，写入 downloads 下的 notes.csv。
4. `csv.js` 决定 id/title 两列及标题转义。

```javascript
ipcMain.handle("notes:export", () => {
  const destination = path.join(app.getPath("downloads"), "notes.csv");
  writeFileSync(destination, toCsv(notes), "utf8");
  return destination;
});
```

这是带上下文依赖的源码摘录，不是单独可运行脚本。静态代码说明目标路径的构造方式，尚未证明当前机器执行后真的写出了文件。继续追问文件无法写入时，沿同步异常、invoke 返回与页面 async handler 阅读错误传播，不能凭“唯一配对”断言错误处理完整。

## 检查 formatter

在解压目录中仅执行下面的 Node 脚本。代码使用已读 csv.js，不加载 Electron，也不调用 writeFileSync；本轮另在固定源码副本执行了相同算法核验，详见验证记录。

```javascript
const assert = require("node:assert/strict");
const { toCsv } = require("./csv.js");
const output = toCsv([{ id: 1, title: 'Hello, "REA"' }]);
assert.equal(output, 'id,title\n1,"Hello, ""REA"""\n');
assert.equal(toCsv([]), "id,title\n");
assert.equal(toCsv([{ id: 2, title: "A,B" }]), 'id,title\n2,"A,B"\n');
process.stdout.write(output);
```

预期输出：

```text
id,title
1,"Hello, ""REA"""
```

标题整个放进双引号字段，内部引号写成两个，末尾保留换行。上游 formatter 仅转义 title；不要从这几个测试推断任意 id、恶意数据或表格软件安全性。

## 浏览器版本区别

官网另有 Notes Web：请求 notes.json 后前端构建 CSV Blob 并触发下载（F-144）。Electron 示例由主进程写文件，Web 示例由浏览器下载，二者共享教学问题但路径不同。REA 的被动窗口由用户或独立控制器触发点击，不能把网络记录写成 REA 自动导出。

验收时分别记录：代码中的路径、formatter 的实际输出、是否启动过应用以及是否验证过文件落地。本例只完成前两层，后两层未执行。

## 相关概念

- [安装边界](../concepts/11-official-site-getting-started.md)
- [三类调查](../concepts/12-evidence-driven-investigation.md)
- [验证记录](../references/official-site-verification.md)
