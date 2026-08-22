---
type: reference
title: "扩展指令源码：Include/Embed/Mermaid/TOC/Raw等"
description: "myst-directives中include、embed、mermaid、toc、raw、image、iframe、aside、dropdown、div、bibliography、glossary、index等扩展指令的实现参考"
tags: [reference, directives, include, embed, mermaid, toc, raw, image, iframe]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/include.ts"
    facts: [F-S025]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/embed.ts"
    facts: [F-S026]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/mermaid.ts"
    facts: [F-S024]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/toc.ts"
    facts: [F-S029]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/raw.ts"
    facts: [F-S036]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/image.ts"
    facts: [F-S019]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/iframe.ts"
    facts: [F-S035]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/aside.ts"
    facts: [F-S033]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/dropdown.ts"
    facts: [F-S034]
---

# 扩展指令源码参考

本文档提供 myst-directives 中扩展指令的实现细节参考。

## Include 指令

[include.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/include.ts#L1-L190)

### 别名与选项

- 别名：literalinclude
- 核心选项：literal(Boolean)、lang/language/code(String)
- 行过滤选项：start-line、end-line、start-at、end-at、start-after、end-before、lines
- 代码块选项：继承 CODE_DIRECTIVE_OPTIONS（caption/linenos/emphasize-lines/filename 等）

### 行过滤互斥检查

```ts
ensureOnlyOneOf(data, vfile, ['start-at', 'start-line', 'start-after', 'lines']);
ensureOnlyOneOf(data, vfile, ['end-at', 'end-line', 'end-before', 'lines']);
```

同时使用多个 start 或多个 end 选项产生警告。

### lines 格式解析

parseLinesString() 支持格式：
- 单行：`1` → 1
- 范围：`1-5` → [1, 5]
- 开放范围：`20-` → [20]（从第20行到末尾）
- 组合：`1,3,5-10,20-` → [1, 3, [5,10], [20]]

### 自动语言推断

```ts
function extToLanguage(ext?: string): string | undefined {
  return {
    ts: 'typescript', js: 'javascript', mjs: 'javascript',
    tex: 'latex', py: 'python', md: 'markdown', yml: 'yaml',
  }[ext ?? ''] ?? ext;
}
```

### 输出

```ts
const include: Include = {
  type: 'include',
  file,           // 文件路径（相对）
  literal,        // 是否作为代码块
  lang,           // 语言（literal模式下）
  caption,        // 标题（literal模式下）
  filter: {       // 行过滤器
    startAt, startAfter, endAt, endBefore, lines
  },
  ...opts,        // 代码块选项
};
```

## Embed 指令

[embed.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/embed.ts#L1-L40)

```ts
run(data) {
  const arg = (data.arg as string).startsWith('#') ? argString.substring(1) : argString;
  const { label } = normalizeLabel(arg) || {};
  return [{
    type: 'embed',
    source: { label },           // 通过label引用目标节点
    'remove-input': data.options?.['remove-input'],
    'remove-output': data.options?.['remove-output'],
  }];
}
```

支持 # 前缀（`:::{embed}#my-figure` 等价于 `:::{embed}my-figure`）。

## Mermaid 指令

[mermaid.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/mermaid.ts#L1-L21)

```ts
run(data) {
  return [addCommonDirectiveOptions(data, {
    type: 'mermaid',
    value: data.body as string,   // Mermaid DSL 文本
  })];
}
```

无特殊选项，仅支持通用选项（class/label）。

## TOC 指令

[toc.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/toc.ts#L1-L61)

### 别名

tableofcontents、table-of-contents、toctree、contents

### 上下文（context/kind）

| 上下文 | 默认来源 | 说明 |
|--------|----------|------|
| project | 默认（非 contents） | 整个项目所有页面 |
| children | - | 当前页面的子页面 |
| page | - | 当前页面内的标题 |
| section | contents 别名默认 | 当前章节内的标题 |

无效 context 产生错误并回退到 'project'。

### 输出

```ts
const toc = {
  type: 'toc',
  kind: context,      // project/children/page/section
  depth,              // 层级深度
  children,           // 可选标题（heading 或 paragraph）
};
```

## Raw 指令

[raw.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/raw.ts#L1-L74)

三个 raw 相关指令：

| 指令 | 参数 | 输出字段 |
|------|------|----------|
| raw | latex/tex/typst/typ/无 | lang + tex/typst + value |
| raw:latex (raw:tex) | 无 | lang:'tex' + tex |
| raw:typst (raw:typ) | 无 | lang:'typst' + typst |

```ts
// raw 指令
const tex = ['tex', 'latex'].includes(lang) ? `\n${value}\n` : undefined;
const typst = ['typst', 'typ'].includes(lang) ? `\n${value}\n` : undefined;
return [{ type: 'raw', lang, tex, typst, value }];
```

raw:latex 和 raw:typst 是格式特定的快捷方式，无需指定参数。

## Image 指令

[image.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/image.ts#L1-L58)

- arg：图片路径（必填，String）
- 选项：width(w)、height(h)、alt、align（默认center）、title
- alt 可从 body 文本自动提取（toText）
- 输出：image 节点（不包裹 container）

与 figure 的区别：image 是行内/独立图片，不带标题和编号；figure 是带 caption 的容器。

## Iframe 指令

[iframe.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/iframe.ts#L1-L65)

- arg：URL（必填）
- 选项：width、align、title（可访问性）、placeholder（静态导出占位图）
- 无 body：直接输出 iframe 节点
- 有 body：包裹在 container(kind:'figure') 中，body 作为 caption
- placeholder 生成 image(placeholder:true) 子节点

## Aside 指令

[aside.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/aside.ts#L1-L37)

- 别名：margin、sidebar、topic
- arg：可选标题（作为 admonitionTitle 放在最前面）
- body：MyST 内容（必填）
- kind：aside/margin 时为 undefined，sidebar/topic 时为指令名

```ts
const children = [...data.body];
if (data.arg) children.unshift({ type: 'admonitionTitle', children: data.arg });
return [{ type: 'aside', kind, children }];
```

## Dropdown 指令

[dropdown.ts](file:///d:/spaces/SpecWeave/external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/dropdown.ts#L1-L44)

- arg：标题（myst）→ 放入 summary 子节点
- body：MyST 内容（必填）
- 选项：open（Boolean，初始展开状态）
- 输出：details HTML 元素节点

```ts
const children = [];
if (data.arg) children.push({ type: 'summary', children: data.arg });
children.push(...data.body);
return [{ type: 'details', open: data.options?.open, children }];
```

## 其他简单指令

| 指令 | 输出 | 说明 |
|------|------|------|
| div | div | body为myst内容的通用块容器 |
| bibliography | bibliography | filter选项过滤引用 |
| glossary | glossary | body为myst内容的术语表容器 |
| index | mystTarget + indexEntries | 索引条目定义（single/pair/triple/see/seealso） |
| show-index (genindex) | genindex | 显示生成的索引 |
| blockquote | blockquote | 块引用 |
| anywidget (widget) | 交互式小部件 | Jupyter 小部件嵌入 |
| mdast | - | 直接嵌入 MDAST 节点 |
| mystdemo | - | 指令演示用途 |
