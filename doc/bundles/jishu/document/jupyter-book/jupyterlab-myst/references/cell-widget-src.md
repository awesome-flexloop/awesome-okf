---
type: reference
title: "MySTMarkdownCell 与 MySTWidget 源码"
description: "src/MySTMarkdownCell.tsx 和 src/widget.tsx 核心组件实现"
source_path: "external/libs/ai/jupyter-book/jupyterlab-myst/src/MySTMarkdownCell.tsx"
key_classes:
  - MySTMarkdownCell
  - MySTWidget
  - MySTModel
facts: [F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021]
tags: [jupyterlab-myst, reference]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/jupyterlab-myst/src/"
    facts: []
---

# MySTMarkdownCell 与 MySTWidget 源码

## MySTMarkdownCell（src/MySTMarkdownCell.tsx）

继承自 `@jupyterlab/cells` 的 `MarkdownCell`，是 Notebook 中每个 Markdown 单元格的 UI 实现。

### 关键属性
- `_notebookRendermime`：Notebook 级别的 IRenderMimeRegistry，用于创建 widget 输出渲染器
- `_attachmentsResolver`：AttachmentsResolver，处理单元格附件（图片等资源）
- `_mystWidget`：MySTWidget 实例，MyST 内容的 React 渲染容器
- `_mystModel`：MySTModel 实例，包含 mdast/references/expressions/frontmatter
- `_fragmentMDAST`：该单元格单独解析的 MDAST 片段
- `_metadataJustChanged`：boolean 标志位，用于区分 metadata 变更和内容变更

### 构造函数逻辑
1. 调用 super(options)
2. 创建 AttachmentsResolver（parent 指向 notebook rendermime.resolver）
3. 创建 MySTModel 和 MySTWidget
4. 连接 taskItemChanged 信号到 setTaskItem 方法
5. HACK：替换默认的 `_renderer` 为 text/plain 渲染器（不使用 rendermime 的输出渲染）
6. HACK：覆写 onTrustedChanged 回调
7. HACK：重建 ActivityMonitor（timeout=100ms，先处理 metadata 变更再决定是否重渲染）
8. HACK：覆写 _handleRendered 回调为 onRenderedChanged
9. 调用 restoreExpressionsFromMetadata() 从 metadata 恢复表达式结果

### 关键方法

**onRenderedChanged()**：处理渲染/编辑模式切换
- rendered=false → showEditor()
- rendered=true → 如果有 placeholder 则 updateFragmentMDAST()；否则 render()

**render()**：
1. updateFragmentMDAST() — 解析本单元格 Markdown
2. renderNotebook(parent) — 全局聚合处理所有 MyST 单元格
3. 等待 _mystWidget.renderPromise
4. inputArea.renderInput(_mystWidget) — 将 MySTWidget 挂载到输入区域

**updateFragmentMDAST()**：
1. markdownParse(source) — myst-parser 解析
2. processCellMDAST(resolver, fragmentMDAST) — 图片 URL 转换
3. 设置 fragmentMDAST.type = 'block'
4. 存储到 _fragmentMDAST

**setTaskItem()**：复选框点击回调
- 按行替换 `[ ]` / `[x]` 文本
- 更新 cell.model.sharedModel.setSource()

**onMetadataChanged()**：监听 metadata 变更
- 设置 _metadataJustChanged = true
- 如果 key 是 'user_expressions'，调用 restoreExpressionsFromMetadata()
- 其他 key 走 super.onMetadataChanged()

## MySTWidget（src/widget.tsx）

继承自 VDomRenderer<IMySTModel>，使用 React 渲染 MyST 内容。

### MySTModel
继承 VDomModel，四个可观察属性（setter 中调用 stateChanged.emit()）：
- `references: References` — 引用解析结果
- `mdast: any` — 处理后的 MDAST 节点
- `expressions: IUserExpressionMetadata[]` — inline expression 结果
- `frontmatter: Frontmatter` — 文档 frontmatter

### render() 方法的 Provider 嵌套

```tsx
<TaskItemControllerProvider controller={this._taskItemController}>
  <ThemeProvider
    theme={getJupyterTheme()}
    Link={linkFactory(this._resolver, this._linkHandler)}
    renderers={renderers}
    setTheme={setTheme}
  >
    <SanitizerProvider sanitizer={this._sanitizer}>
      <UserExpressionsProvider
        expressions={expressions}
        rendermime={this._rendermime}
        trusted={this._trusted}
      >
        <TabStateProvider>
          <ArticleProvider
            kind={SourceFileKind.Article}
            references={references}
            frontmatter={frontmatter}
          >
            {frontmatter && <FrontmatterBlock frontmatter={frontmatter} />}
            <MyST ast={mdast} />
          </ArticleProvider>
        </TabStateProvider>
      </UserExpressionsProvider>
    </SanitizerProvider>
  </ThemeProvider>
</TaskItemControllerProvider>
```

### 主题检测
```ts
function getJupyterTheme(): Theme {
  return document.body.dataset.jpThemeLight === 'false' ? Theme.dark : Theme.light;
}
```

### 外部依赖
- @myst-theme/frontmatter: FrontmatterBlock
- @myst-theme/providers: ArticleProvider, TabStateProvider, ThemeProvider, Theme
- myst-to-react: MyST（核心 MDAST 渲染组件）
