---
type: concept
title: "支持的 MyST 语法与安全模型"
description: "详解 jupyterlab-myst 支持的 MyST Markdown 语法特性（directives、roles、任务列表、内联表达式）以及 JupyterLab 信任安全模型"
tags: [jupyterlab-myst, myst-syntax, directives, roles, security, trust, sanitizer]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/parse-pipeline-src.md"
    facts: [F-022, F-054, F-055]
  - path: "/references/execution-components-src.md"
    facts: [F-036, F-043]
  - path: "/references/cell-widget-src.md"
    facts: [F-021]
---

# 支持的 MyST 语法与安全模型

jupyterlab-myst 在 JupyterLab 中支持丰富的 MyST Markdown 语法，同时遵循 JupyterLab 的安全模型保护用户免受恶意内容侵害。

## 支持的 Directives

Directives 是 MyST 中的块级扩展语法，使用 `{directive_name}` 标记：

### card（卡片）

来源：myst-ext-card

```markdown
```{card} 卡片标题
卡片内容，可以包含 **Markdown** 格式。
```
```

渲染为带边框的卡片容器，适合突出显示重要信息。

### grid（网格布局）

来源：myst-ext-grid（包含 grid-item）

```markdown
::::{grid} 2
:::{grid-item}
第一列内容
:::
:::{grid-item}
第二列内容
:::
::::
```

创建多列网格布局，支持响应式列数。

### proof（证明/定理环境）

来源：myst-ext-proof

```markdown
```{proof} 定理名称
证明内容...
```
```

支持的 proof 类型包括：theorem、lemma、proof、definition、remark、corollary、proposition 等。

### exercise（练习环境）

来源：myst-ext-exercise

````markdown
```{exercise} 练习 1
:label: ex-1
练习内容...
```

```{solution} ex-1
:label: sol-1
解答内容...
```
````

支持 exercise 和 solution 配对，带编号和交叉引用。

### tab（标签页）

来源：myst-ext-tabs

````markdown
::::{tab-set}
:::{tab-item} Python
```python
print("Hello")
```
:::
:::{tab-item} R
```r
print("Hello")
```
:::
::::
````

创建可切换的标签页，支持同步选择（sync-tab）。

## 支持的标准 MyST 特性

除了上述显式注册的 directives，转换管道还支持：

| 特性 | 处理插件 | 说明 |
|------|---------|------|
| 数学公式 | mathPlugin | LaTeX 公式（`$...$` 和 `$$...$$`），支持宏定义 |
| 脚注 | footnotesPlugin | `[^1]` 标记的脚注 |
| 交叉引用 | enumerateTargetsPlugin + resolveReferencesPlugin | `{ref}` role、标题自动编号引用 |
| 引用/citation | addCiteChildrenPlugin | `{cite}` 引用，支持 bibtex |
| 缩写词 | abbreviationPlugin | frontmatter 中定义的 abbreviations |
| 术语表 | glossaryPlugin | 术语定义和引用 |
| 外部链接转换 | linksPlugin + transformers | DOI、GitHub、RRID、Wiki 自动链接 |
| 内联 HTML | reconstructHtmlTransform | 原始 HTML 的安全处理 |

### 自动链接转换器

- **WikiTransformer**：`[[WikiLink]]` → 维基百科链接
- **GithubTransformer**：`#123`、`@user` → GitHub issue/PR/用户链接
- **DOITransformer**：`doi:10.xxxx/yyyy` → https://doi.org/链接
- **RRIDTransformer**：`RRID:XXX` → 研究资源标识符链接

## 任务列表

```markdown
- [x] 已完成项
- [ ] 待办项
```

任务列表在 jupyterlab-myst 中是交互式的：
- 渲染为可点击的复选框
- 点击复选框直接编辑 Markdown 源码（更新 `[ ]`/`[x]`）
- 通过 TaskItemControllerProvider 回调通知 MySTMarkdownCell 更新源码
- 使用正则替换定位到对应行：`/^(\s*(?:-|\*)\s*)(\[[\s|x]\])/`

## Inline Expression（内联表达式）

```markdown
当前共有 {eval}`len(df)` 条数据，
正确率 {eval}`accuracy:.1%`。
```

- 代码单元格执行后自动求值
- 结果显示在文本中（支持 text/plain、text/html、image/png 等多种 MIME 类型）
- 错误结果显示错误信息
- 结果持久化到 .ipynb metadata 中

## Frontmatter

Markdown 单元格开头的 YAML 块作为文档 frontmatter：

```markdown
---
title: "文档标题"
authors:
  - name: "作者名"
    affiliations: "机构"
date: 2024-01-01
---
```

- 第一个 Markdown 单元格中的 YAML 块被解析为 frontmatter
- 渲染为 FrontmatterBlock（标题、作者、日期等元数据块）
- 支持 math 宏定义（frontmatter.math）
- 支持 abbreviations 缩写词定义
- mime-renderer 插件自动设置 hideFrontMatter=false，确保 frontmatter 在 Markdown Viewer 中可见

## 图片和附件

- Markdown 中的图片（`![](path)`）通过 imageUrlSourceTransform 处理
- 使用 JupyterLab 的 IRenderMime.IResolver 解析相对路径
- 单元格附件（attachment:filename）通过 AttachmentsResolver 解析
- 支持 JupyterLab 内核输出的图片 MIME 类型

## 安全模型

### JupyterLab Trust 模型

jupyterlab-myst 严格遵循 JupyterLab 的 Notebook 信任机制：

1. **不受信任的 Notebook**：
   - inline expression 的结果（MIME bundle）不渲染
   - HTML 输出经过 sanitizer 清洗
   - 防止打开来自不可信来源的 Notebook 时执行恶意脚本

2. **信任建立方式**：
   - 用户执行任何代码单元格 → Notebook 自动标记为受信任
   - 用户手动标记为受信任
   - 受信任位置的 Notebook（如 Jupyter 目录）

3. **Trust 传播路径**：
   ```
   cell.model.trusted = true
     → MySTWidget.trusted = value
       → UserExpressionsProvider.trusted = value
         → InlineExpression 组件渲染/不渲染结果
   ```

### Sanitizer（HTML 清洗）

- SanitizerProvider 将 JupyterLab 的 ISanitizer 注入 React 上下文
- 渲染 HTML 内容时通过 sanitizer 清洗，移除 `<script>`、`onclick` 等危险元素和属性
- 基于 JupyterLab 内置的 sanitizer（通常是 DOMPurify 或类似库）

### MIME Renderer 安全标记

```ts
const mystMarkdownRendererFactory = {
  safe: true,  // 标记为安全渲染器
  mimeTypes: ['text/markdown'],
  defaultRank: 50,
};
```

`safe: true` 标记告诉 JupyterLab 此渲染器产生的内容是安全的，即使在不受信任的 Notebook 中也可以渲染 Markdown 结构本身（但 inline expression 结果仍受 trust 控制）。

### 外部链接

- 外部链接正常打开（target="_blank"）
- 内部链接通过 JupyterLab ILinkHandler 处理
- Wiki/GitHub/DOI/RRID 链接自动转换为标准 HTTPS 链接

## Python 端 Notary

jupyterlab_myst Python 包包含 notary.py，提供与 Notebook 信任相关的工具。其作用可能是：
- 标记包含 inline expression 的 Notebook 为受信任
- 在服务端验证 Notebook 中 user_expressions metadata 的完整性

（注：Python 端代码主要作为 Jupyter Server 扩展的配置入口，核心功能在 TypeScript 端实现。）

## 与 JupyterLab 内置 Markdown 渲染器的对比

| 特性 | JupyterLab 内置 | jupyterlab-myst |
|------|----------------|-----------------|
| 标准 Markdown | ✅ | ✅ |
| GFM 表格 | ✅ | ✅ |
| 数学公式 | ✅ | ✅ |
| 代码块高亮 | ✅ | ✅ |
| MyST directives | ❌ | ✅ |
| 交叉引用 | ❌ | ✅ |
| 脚注 | 有限 | ✅ |
| 任务列表 | 只读 | ✅ 可交互 |
| Inline expression | ❌ | ✅ |
| Frontmatter 渲染 | 隐藏 | ✅ 可见 |
| DOI/GitHub 自动链接 | ❌ | ✅ |
| 网格布局 | ❌ | ✅ |
| 标签页 | ❌ | ✅ |

## 相关概念

- [01-myst-rendering-pipeline.md](/concepts/01-myst-rendering-pipeline.md)：解析管道和支持的 directives
- [03-inline-expressions.md](/concepts/03-inline-expressions.md)：内联表达式安全机制
- [04-myst-widget-react.md](/concepts/04-myst-widget-react.md)：SanitizerProvider 安全清洗
- [01-using-jupyterlab-myst.md](/examples/01-using-jupyterlab-myst.md)：使用示例
