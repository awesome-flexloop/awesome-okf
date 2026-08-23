---
type: concept
title: "Inline Expression 内联表达式执行"
description: "详解 jupyterlab-myst 的内联表达式机制：利用 Jupyter 内核协议的 user_expressions 字段、metadata 持久化、信任模型和执行流程"
tags: [jupyterlab-myst, inline-expression, user-expressions, kernel, metadata, trust]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/execution-components-src.md"
    facts: [F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037]
---

# Inline Expression 内联表达式执行

Inline Expression（内联表达式）是 MyST Markdown 中的特殊语法，允许在 Markdown 文本中嵌入 Python 表达式，执行结果动态显示在文本中。jupyterlab-myst 在 JupyterLab 中实现了这一功能：当代码单元格执行后，Markdown 单元格中的内联表达式自动在当前内核命名空间中求值并显示结果。

## MyST 语法

在 MyST Markdown 中，内联表达式使用 `{eval}` role 或反引号语法：

```markdown
数据集中共有 {eval}`len(df)` 行记录，
均值为 {eval}`df['value'].mean():.2f`。
```

解析后，这些表达式在 MDAST 中表示为 `inlineExpression` 类型节点，其 `value` 属性为表达式文本字符串。

## 内核协议机制

jupyterlab-myst 巧妙利用了 Jupyter 内核协议的 `user_expressions` 字段，而非常规的代码执行请求。

### execute_request 协议

Jupyter 的 execute_request 消息包含两个关键字段：

```json
{
  "header": { "msg_type": "execute_request" },
  "content": {
    "code": "",
    "silent": false,
    "user_expressions": {
      "0": "len(df)",
      "1": "df['value'].mean()"
    }
  }
}
```

- `code`：要执行的代码（jupyterlab-myst 设为空字符串，不执行代码）
- `user_expressions`：命名字典，内核执行完 code 后对每个表达式在用户命名空间中求值

### 为什么不用常规 code 执行？

如果发送 code = `print(len(df))`，结果会作为 stdout 输出到代码单元格的输出区域，产生副作用。而 `user_expressions` 的结果直接在 execute_reply 中返回，不产生任何输出，非常适合获取表达式的求值结果。

### execute_reply 响应

内核返回的 execute_reply 中包含 `user_expressions` 结果：

**成功结果**：
```json
{
  "content": {
    "status": "ok",
    "user_expressions": {
      "0": {
        "status": "ok",
        "data": { "text/plain": "100" },
        "metadata": {}
      }
    }
  }
}
```

**错误结果**：
```json
{
  "content": {
    "status": "ok",
    "user_expressions": {
      "0": {
        "status": "error",
        "ename": "NameError",
        "evalue": "name 'df' is not defined",
        "traceback": ["..."]
      }
    }
  }
}
```

注意：外层 status 是 "ok"（表示请求成功处理），内层每个表达式有自己的 status（"ok" 或 "error"）。

## 执行流程

### 触发时机

Inline expression 的求值在**代码单元格执行后**自动触发：

```
用户按 Shift+Enter 执行代码单元格
    │
    ▼
NotebookActions.executed 信号触发
    │
    ▼
notebookCellExecuted(notebook, cell, tracker)
    │
    ├─ 1. 检查执行的是否为代码单元格（MarkdownCell 跳过）
    ├─ 2. 通过 tracker 找到 NotebookPanel
    ├─ 3. 获取 SessionContext（内核连接）
    ├─ 4. await cell.updateFragmentMDAST()（更新被执行单元格的 fragment）
    ├─ 5. await executeUserExpressions(cell, ctx)
    │      └─ 向所有 Markdown 单元格发送表达式求值请求
    ├─ 6. 将结果写入 cell metadata['user_expressions']
    └─ 7. cell.model.trusted = true
```

> **注意**：当前实现中，`notebookCellExecuted` 在代码单元格执行后触发，但它只处理被执行的那个 cell 参数。实际上，从源码看 `notebookCellExecuted` 接收 `cell` 参数后先检查 `isMySTMarkdownCell(cell)`，如果不是 MarkdownCell 就直接 return。这意味着 inline expression 的求值发生在 Markdown 单元格自身"被执行"时（JupyterLab 中双击 Markdown 单元格进入编辑模式后 Shift+Enter 也会触发 executed 信号）。

### executeUserExpressions 实现

```ts
export async function executeUserExpressions(cell, sessionContext) {
  const kernel = sessionContext.session?.kernel;
  if (!kernel) throw new Error('Session has no kernel.');

  // 1. 从 MDAST 提取所有 inlineExpression 节点
  const mdast = cell.mystModel?.mdast ?? {};
  const expressions = selectAll('inlineExpression', mdast)
    .map(node => node.value);

  if (expressions.length === 0) return [];

  // 2. 构建编号字典
  const userExpressions = {};
  expressions.forEach((expr, index) => {
    userExpressions[`${index}`] = expr;
  });

  // 3. 发送内核请求
  const future = kernel.requestExecute({
    code: '',
    user_expressions: userExpressions
  }, false);

  // 4. 处理响应
  return new Promise((resolve, reject) => {
    future.onReply = (msg) => {
      if (msg.content.status !== 'ok') {
        return reject('Kernel response was not OK');
      }

      const results = [];
      for (const key in msg.content.user_expressions) {
        const expr = expressions[parseInt(key)];
        const result = msg.content.user_expressions[key];
        results.push({ expression: expr, result });
      }
      resolve(results);
    };
  });
}
```

## Metadata 持久化

表达式结果存储在单元格 metadata 中，随 .ipynb 文件持久化：

```json
{
  "cell_type": "markdown",
  "metadata": {
    "user_expressions": [
      {
        "expression": "len(df)",
        "result": {
          "status": "ok",
          "data": { "text/plain": "100" },
          "metadata": {}
        }
      }
    ]
  },
  "source": ["数据集中共有 {eval}`len(df)` 行记录"]
}
```

这意味着：
- 保存 Notebook 后重新打开，表达式结果仍然可见（不需要重新执行）
- 但只有受信任的 Notebook 才会渲染这些结果
- 重新执行代码单元格后，结果自动刷新

### Metadata 操作函数

```ts
// 读取（兼容 JL 3.6 和 4.x）
getUserExpressions(cell): IUserExpressionMetadata[] | undefined

// 写入
setUserExpressions(cell, expressions: IUserExpressionMetadata[]): void

// 删除
deleteUserExpressions(cell): void
```

JupyterLab 3.6 使用 `model.metadata.get()` / `model.metadata.set()` 模式（Yjs Map API），4.x 使用 `model.getMetadata()` / `model.setMetadata()`。两个版本通过检测 model 是否有 setMetadata 方法来兼容。

## 信任模型

jupyterlab-myst 遵循 JupyterLab 的信任（trust）安全模型：

1. **打开不受信任的 Notebook**：inline expression 的结果不会渲染（即使 metadata 中有数据），防止恶意 Notebook 通过伪造的 MIME bundle 注入 HTML/JS。
2. **执行代码单元格后**：`cell.model.trusted = true`，用户主动执行代码隐式信任该 Notebook，表达式结果开始显示。
3. **MySTWidget.trusted 属性**：通过 UserExpressionsProvider 传递给 InlineExpression 组件。
4. **InlineExpression 组件**：只有 `trusted === true` 且有 result 时才使用 rendermime 渲染 result.data（MIME bundle）。

信任状态变化时（onModelTrustedChanged），自动恢复 expressions 并触发重渲染。

## 结果渲染

InlineExpression 组件的渲染逻辑：
1. 使用 useUserExpressions() 获取 { expressions, rendermime, trusted }
2. 通过表达式文本匹配到对应的 IUserExpressionMetadata
3. 如果 trusted=true 且 result.status='ok'：
   - 使用 rendermime.createRenderer(mimeType) 创建输出渲染器
   - 将 result.data（MIME bundle）渲染到 DOM
   - 支持 text/plain、text/html、image/png 等所有 Jupyter MIME 类型
4. 如果 result.status='error'：显示错误信息（ename + evalue）
5. 如果未执行且没有 result：显示原始表达式文本或占位符

## 与 myst-execute 的对比

| 特性 | myst-execute | jupyterlab-myst inline expression |
|------|-------------|----------------------------------|
| 执行时机 | 构建时（myst build） | 运行时（JupyterLab 中 Shift+Enter） |
| 执行位置 | Node.js 连接本地内核 | 浏览器通过 WebSocket 连接内核 |
| 结果存储 | 构建缓存（JSON 文件） | Notebook metadata（.ipynb 文件） |
| 交互性 | 无（静态输出） | 有（重新执行代码后自动刷新） |
| 安全模型 | 构建时执行，信任本地环境 | JupyterLab trust model |

## 相关概念

- [00-architecture-plugins.md](/concepts/00-architecture-plugins.md)：插件架构（executor 插件）
- [01-myst-rendering-pipeline.md](/concepts/01-myst-rendering-pipeline.md)：解析管道（inlineExpression 节点）
- [02-myst-markdown-cell.md](/concepts/02-myst-markdown-cell.md)：单元格生命周期（metadata 变更处理）
- [01-using-jupyterlab-myst.md](/examples/01-using-jupyterlab-myst.md)：使用示例
