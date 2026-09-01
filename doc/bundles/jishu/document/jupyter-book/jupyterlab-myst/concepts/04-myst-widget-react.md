---
type: concept
title: "MySTWidget React 渲染系统"
description: "详解 MySTWidget 的 React Provider 嵌套链、Theme 适配、自定义渲染器、链接处理和任务列表交互"
tags: [jupyterlab-myst, react, myst-to-react, provider, theme, renderers]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/cell-widget-src.md"
    facts: [F-015, F-016, F-017, F-018, F-019, F-020, F-021]
  - path: "/references/execution-components-src.md"
    facts: [F-041, F-042, F-043, F-044, F-045]
---

# MySTWidget React 渲染系统

MySTWidget 是 jupyterlab-myst 的 React 渲染核心，继承自 JupyterLab Lumino 的 VDomRenderer，将 myst-to-react 组件库嵌入到 JupyterLab 的 Widget 体系中。通过多层 React Context Provider 嵌套，将 JupyterLab 的服务（rendermime、sanitizer、linkHandler）桥接到 myst-to-react 的渲染系统。

## VDomRenderer 桥接模式

```ts
export class MySTWidget extends VDomRenderer<IMySTModel> {
  constructor(options: IMySTOptions) {
    super(model);
    this._resolver = options.resolver;
    this._linkHandler = options.linkHandler;
    this._rendermime = options.rendermime;
    this._trusted = options.trusted;
    this._sanitizer = options.sanitizer;
    this.addClass('myst');
  }

  protected render(): React.JSX.Element {
    // 返回 React 元素，VDomRenderer 负责渲染到 DOM
  }
}
```

VDomRenderer 是 JupyterLab AppUtils 提供的桥接类：
- 继承 Lumino Widget，可挂载到 JupyterLab 的 DOM 体系
- 使用 ReactDOM.render 将 render() 返回的 React 元素渲染到 Widget 节点
- 监听 model.stateChanged 信号自动触发重渲染
- 提供 renderPromise 供外部等待渲染完成

## MySTModel：可观察数据模型

```ts
export class MySTModel extends VDomModel implements IMySTModel {
  private _references?: References;
  private _mdast?: any;
  private _expressions?: IUserExpressionMetadata[];
  private _frontmatter?: Frontmatter;

  // 每个 setter 调用 this.stateChanged.emit() 触发重渲染
  set references(value) { this._references = value; this.stateChanged.emit(); }
  set mdast(value) { this._mdast = value; this.stateChanged.emit(); }
  set expressions(value) { this._expressions = value; this.stateChanged.emit(); }
  set frontmatter(value) { this._frontmatter = value; this.stateChanged.emit(); }
}
```

四个属性对应渲染所需的四类数据：
- **mdast**：处理后的 MDAST 节点（分片后的单元格内容）
- **references**：全局引用解析结果（交叉引用、脚注、citation 数据）
- **expressions**：inline expression 执行结果
- **frontmatter**：文档元数据（仅第一个单元格有）

## Provider 嵌套链

MySTWidget.render() 中的 Provider 从外到内：

```
TaskItemControllerProvider
  └─ ThemeProvider
       └─ SanitizerProvider
            └─ UserExpressionsProvider
                 └─ TabStateProvider
                      └─ ArticleProvider
                           ├─ <FrontmatterBlock /> (条件渲染)
                           └─ <MyST ast={mdast} />
```

### 1. TaskItemControllerProvider（最外层）

提供任务列表复选框的交互回调：

```tsx
<TaskItemControllerProvider controller={this._taskItemController}>
```

controller 是一个函数 `(change: ITaskItemChange) => void`，当用户点击复选框时被调用。MySTWidget 在构造函数中创建：

```ts
this._taskItemController = change => this._taskItemChanged.emit(change);
```

通过 Signal 通知 MySTMarkdownCell 更新 Markdown 源码中的 `[ ]` / `[x]`。

### 2. ThemeProvider

来自 @myst-theme/providers，控制 MyST 内容的主题：

```tsx
<ThemeProvider
  theme={getJupyterTheme()}
  Link={linkFactory(this._resolver, this._linkHandler)}
  renderers={renderers}
  setTheme={setTheme}
>
```

- **theme**：通过 `document.body.dataset.jpThemeLight` 检测 JupyterLab 当前主题（light/dark）
- **Link**：自定义链接组件（linkFactory 创建）
- **renderers**：自定义节点渲染器映射
- **setTheme**：空函数（JupyterLab 主题由 JupyterLab 自身控制，不需要 MyST 设置）

### 3. SanitizerProvider

```tsx
<SanitizerProvider sanitizer={this._sanitizer}>
```

将 JupyterLab 的 ISanitizer 注入 React 上下文。渲染 HTML 输出（如 inline expression 的 text/html 结果）时使用此 sanitizer 进行安全清洗，防止 XSS。

### 4. UserExpressionsProvider

```tsx
<UserExpressionsProvider
  expressions={expressions}
  rendermime={this._rendermime}
  trusted={this._trusted}
>
```

将 inline expression 相关数据注入上下文：
- expressions：表达式结果数组
- rendermime：IRenderMimeRegistry（用于创建 MIME 输出渲染器）
- trusted：信任状态（控制是否渲染表达式结果）

### 5. TabStateProvider

来自 @myst-theme/providers，管理 tab 指令（sync-tab）的状态。

### 6. ArticleProvider

```tsx
<ArticleProvider
  kind={SourceFileKind.Article}
  references={references}
  frontmatter={frontmatter}
>
```

提供文档级上下文：文档类型（Article/Notebook）、引用数据、frontmatter。

## FrontmatterBlock

如果 frontmatter 存在（第一个单元格），渲染 FrontmatterBlock 组件（来自 @myst-theme/frontmatter）：

```tsx
{frontmatter && <FrontmatterBlock frontmatter={frontmatter} />}
<MyST ast={mdast} />
```

FrontmatterBlock 显示标题、作者、日期、摘要等元数据。

## 自定义渲染器（renderers）

renderers.tsx 导出 `renderers` 对象，覆盖 myst-to-react 的默认渲染器：

- **listItem**：自定义列表项渲染，支持任务列表复选框
- **inlineExpression**：自定义内联表达式渲染，使用 rendermime 显示表达式结果

其他节点类型使用 myst-to-react 的默认渲染器。

## 链接处理（linkFactory）

```ts
linkFactory(resolver?, linkHandler?) => React.ComponentType<{to: string, children: React.ReactNode}>
```

创建自定义 Link 组件：
- 内部链接（以 `#` 开头或 JupyterLab 可解析的路径）使用 ILinkHandler.handleLink() 导航
- 外部链接正常打开
- 使用 resolver 解析相对 URL（附件、同目录文件）

## RenderedMySTMarkdown：Markdown Viewer 渲染器

RenderedMySTMarkdown 继承 MySTWidget，实现 IRenderMime.IRenderer 接口，用于 JupyterLab Markdown Viewer（打开独立 .md 文件）：

```ts
export class RenderedMySTMarkdown extends MySTWidget implements IRenderMime.IRenderer {
  async renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const mdast = markdownParse(model.data[MIME_TYPE] as string);
    const { references, mdast: mdastNext, frontmatter } =
      await processArticleMDAST(mdast, this.resolver);
    const mystModel = new MySTModel();
    mystModel.references = references;
    mystModel.mdast = mdastNext;
    mystModel.frontmatter = frontmatter;
    mystModel.expressions = this.model?.expressions;  // 保留已有表达式结果
    this.model = mystModel;
    return this.renderPromise || Promise.resolve();
  }
}
```

与 MySTMarkdownCell 中的 MySTWidget 的区别：
- 使用 processArticleMDAST（而非 processNotebookMDAST）处理完整文档
- 不从 fragmentMDAST 聚合，直接解析完整 Markdown 文本
- 不涉及单元格生命周期管理
- 通过 IRenderMime.IRenderer 接口集成到 Markdown Viewer

## CSS 类名

MySTWidget 添加 CSS class `myst`，配合 style/ 目录的样式表：
- `base.css`：基础样式
- `links.css`：链接样式
- `jupyterlab-typography.css`：与 JupyterLab 排版协调
- `preflight.css`：样式重置
- `tailwind.css`：Tailwind CSS 工具类

## 相关概念

- [00-architecture-plugins.md](00-architecture-plugins.md)：插件架构（mime-renderer 插件）
- [01-myst-rendering-pipeline.md](01-myst-rendering-pipeline.md)：解析管道
- [02-myst-markdown-cell.md](02-myst-markdown-cell.md)：单元格生命周期
- [03-inline-expressions.md](03-inline-expressions.md)：内联表达式
