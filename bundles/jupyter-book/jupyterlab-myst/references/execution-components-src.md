---
type: reference
title: "Inline Expression 执行与 React 组件源码"
description: "src/actions.ts 用户表达式执行、src/userExpressions.ts metadata 管理、src/mime.tsx MIME 渲染器、src/components/ 和 src/providers/ React 组件"
source_path: "external/libs/ai/jupyter-book/jupyterlab-myst/src/actions.ts"
key_exports:
  - executeUserExpressions
  - notebookCellExecuted
  - metadataSection
  - IExpressionResult
  - IUserExpressionMetadata
  - RenderedMySTMarkdown
  - mystMarkdownRendererFactory
  - InlineExpression
  - UserExpressionsProvider
  - TaskItemControllerProvider
  - SanitizerProvider
  - renderers
facts: [F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045]
---

# Inline Expression 执行与 React 组件源码

## Inline Expression 执行

### src/userExpressions.ts

定义 inline expression 的类型系统和 metadata 操作：

```ts
// metadata 存储键名
export const metadataSection = 'user_expressions';

// 结果类型
interface IExpressionOutput { status: 'ok'; data: PartialJSONObject; metadata: PartialJSONObject; }
interface IExpressionError { status: 'error'; traceback: string[]; ename: string; evalue: string; }
type IExpressionResult = IExpressionError | IExpressionOutput;

// metadata 中的条目
interface IUserExpressionMetadata {
  expression: string;  // 原始表达式文本
  result: IExpressionResult;
}
```

三个 metadata 操作函数（兼容 JL 3.6/4.x）：
- `getUserExpressions(cell)` → IUserExpressionMetadata[] | undefined
- `setUserExpressions(cell, expressions)` → void
- `deleteUserExpressions(cell)` → void

### src/actions.ts

**executeUserExpressions(cell, sessionContext)**：
1. 获取 sessionContext.session?.kernel，无 kernel 则抛错
2. 从 cell.mystModel.mdast 使用 `selectAll('inlineExpression', mdast)` 提取所有表达式节点
3. 构建 user_expressions 字典：`{ '0': expr0, '1': expr1, ... }`
4. 发送 `kernel.requestExecute({ code: '', user_expressions }, false)`
5. future.onReply 中解析 execute_reply 的 user_expressions 结果
6. 返回 IUserExpressionMetadata[]（每个含 expression 文本和 result）

**notebookCellExecuted(notebook, cell, tracker)**（代码单元格执行后的回调）：
1. 通过 tracker 找到包含 notebook 的 NotebookPanel
2. 获取 sessionContext
3. 如果不是 MarkdownCell 则跳过
4. await cell.updateFragmentMDAST()
5. await executeUserExpressions(cell, ctx)
6. 有结果 → setUserExpressions(cell, expressions)
7. 无结果 → deleteUserExpressions(cell)
8. cell.model.trusted = true

## MIME 渲染器（src/mime.tsx）

### RenderedMySTMarkdown

继承 MySTWidget，实现 IRenderMime.IRenderer：
- constructor：添加 CSS class 'jp-RenderedMySTMarkdown'
- renderModel(model)：从 model.data['text/markdown'] 获取文本 → markdownParse → processArticleMDAST → 创建 MySTModel → this.model = mystModel → 等待 renderPromise

### mystMarkdownRendererFactory

```ts
export const mystMarkdownRendererFactory: IRenderMime.IRendererFactory = {
  safe: true,
  mimeTypes: ['text/markdown'],
  defaultRank: 50,
  createRenderer: options => new RenderedMySTMarkdown(options)
};
```

## React 组件（src/components/）

### components/inlineExpression.tsx

InlineExpression 组件：
- 使用 useUserExpressions() 获取 expressions、rendermime、trusted
- 根据表达式字符串匹配对应的 IUserExpressionMetadata
- 只有 trusted=true 且有 result 时才渲染
- 使用 rendermime.createRenderer(mimeType) 创建输出渲染器
- 将 result.data（MIME bundle）渲染到 DOM
- result.status === 'error' 时显示错误信息

### components/listItem.tsx

自定义 listItem 渲染器，处理任务列表项（- [ ] / - [x]）：
- 渲染复选框
- 使用 TaskItemControllerProvider 的 controller 回调通知 checkbox 变化
- 传递行号信息用于定位源码中的对应行

### components/index.tsx

导出所有组件。

## Provider（src/providers/）

### providers/userExpressions.tsx

UserExpressionsProvider + useUserExpressions() Hook：
- Context 值：{ expressions?, rendermime?, trusted? }

### providers/taskItem.tsx

TaskItemControllerProvider：
- controller: (change: ITaskItemChange) => void
- ITaskItemChange: { line: number; checked: boolean }
- 用于任务列表复选框交互

### providers/sanitizer.tsx

SanitizerProvider：
- 将 JupyterLab 的 ISanitizer 注入 React 上下文
- 渲染 HTML 输出时进行安全清洗

### providers/index.tsx

导出所有 Provider。

## renderers.tsx

注册自定义 myst-to-react 渲染器映射：
- 覆盖 listItem 渲染器以支持任务列表
- 覆盖 inlineExpression 渲染器
- 其他节点使用 myst-to-react 默认渲染器
