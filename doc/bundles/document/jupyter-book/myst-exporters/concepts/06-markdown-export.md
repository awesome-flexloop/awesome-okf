---
type: concept
title: "Markdown 导出"
description: "myst-to-md 将 MDAST 转换回 MyST Markdown 的序列化器，支持角色/指令语法、YAML frontmatter 和脚注/术语表"
tags: [myst-exporters, markdown, myst, serializer, mdast]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-md/src/index.ts"
    facts: [F-019, F-020]
  - path: "myst-to-md/src/types.ts"
    facts: []
---

# Markdown 导出

Markdown 导出由 `myst-to-md` 包提供，将 MDAST 序列化回 MyST 风格的 Markdown。这个导出器的主要用途是：
1. **Markdown 规范化**：将不同来源的 Markdown 统一为标准格式
2. **格式转换闭环**：MyST→MDAST→MyST，支持文档的程序化修改后重新输出
3. **简化输出**：为不支持 HTML/LaTeX 的目标环境生成简化的 Markdown

## MdSerializer 架构

与 TexSerializer 类似，MdSerializer 使用字符串拼接模式：

```typescript
class MdSerializer implements State {
  file: VFile;
  options: Options;
  mdast: Root;
  indent: string;      // 当前缩进（列表嵌套时递增）
  set: MdStateData;    // 需放在文末的集合（footnotes/glossary/abbreviations）
  value: string;       // 输出内容
  handlers: Record<string, MdastToMystHandler>;
}
```

### 核心方法

| 方法 | 说明 |
|------|------|
| `renderChildren(node, opts?)` | 遍历子节点，按 type 查 handler 表分发 |
| `write(value)` | 追加字符串到输出 |
| `text(value)` | 转义特殊 Markdown 字符后写入 |
| `trim()` | 去除末尾空白 |
| `ensureNewLine()` | 确保以换行结尾 |
| `addBlock()` | 块级元素前确保有空行，后有换行 |
| `closeBlock()` | 块结束处理（换行）|
| `newline()` | 添加空行 |

## 输出结构

### Frontmatter

如果 MDAST 的第一个节点是 YAML frontmatter（类型 `yaml`），会输出为：

```markdown
---
key: value
---
```

否则不输出 frontmatter。frontmatter 内容来自 myst-parser 解析的原始 YAML 或后续 transform 填充的 frontmatter 数据。

### 正文

正文按标准 MyST Markdown 语法输出：

| MyST 节点 | Markdown 输出 | 说明 |
|----------|-------------|------|
| heading | `# Title` | 按 depth 输出对应数量的 # |
| paragraph | 普通文本 | 段落之间空行分隔 |
| strong | `**bold**` | 粗体 |
| emphasis | `*italic*` | 斜体 |
| inlineCode | `` `code` `` | 行内代码 |
| code | ```` ```lang\ncode\n``` ```` | 代码块，带语言标识 |
| list (unordered) | `- item` | 无序列表（使用 `-`） |
| list (ordered) | `1. item` | 有序列表 |
| blockquote | `> quote` | 引用 |
| thematicBreak | `---` | 水平线 |
| link | `[text](url)` | 链接 |
| image | `![alt](path)` | 图片 |
| footnoteReference | `[^key]` | 脚注引用 |
| crossReference | `[](#target)` | 交叉引用 |
| container/admonition | ````{note}\nContent\n``` ```` | 指令块 |
| math/display | `$$\nformula\n$$` | 块级数学 |
| math/inline | `$formula$` | 行内数学 |
| role/abbr | `{abbr}`short` `` | 角色语法 |
| directive | ````{directive}\n:option: val\nContent\n``` ```` | 指令语法 |

### 文末集合

MdSerializer 的 `set` 对象跟踪需要放在文档末尾的内容：

- **footnotes**：`[^key]: footnote text`，按引用顺序输出在文末
- **glossary**：术语表定义（如果有 glossary directive）
- **abbreviations**：缩写定义

这些内容在文档最后通过空行分隔后追加。

## MyST 语法特性

### 角色（Roles）

行内语义标记使用角色语法：

```markdown
这是 {math}`E=mc^2` 公式。
这是 {abbr}`HTML (HyperText Markup Language)` 缩写。
```

### 指令（Directives）

块级扩展语法使用代码围栏加指令名：

````markdown
```{note}
这是一个提示框。
```
````

带选项的指令：

````markdown
```{figure} images/pic.png
:width: 300px
:align: center

图片标题文字。
```
````

### 交叉引用

MyST 的自动标题引用使用 `{doc}`、`{ref}` 等角色，Markdown 导出保留 `[](#id)` 或 `[text](#id)` 格式。

## 转义规则

`text()` 方法对 Markdown 特殊字符进行转义：

- `*` → `\*`（防止意外的 emphasis）
- `_` → `\_`（同上）
- `` ` `` → `` \` ``（防止意外 code）
- `[` → `\[`、`]` → `\]`（防止意外链接）
- `#` → `\#`（防止意外标题）
- `>` → `\>`（防止意外引用）
- `|` → `\|`（表格分隔符）
- `$` → `\$`（数学公式分隔符）

在链接文本、代码块等上下文中不转义。

## 使用方式

```typescript
import { unified } from 'unified';
import mystParse from 'myst-parser';
import { mystToMdPlugin } from 'myst-to-md';

const file = unified()
  .use(mystParse)
  .use(mystToMdPlugin)
  .processSync('# Hello\n\n**Bold** text.');

console.log(file.result);
// # Hello
//
// **Bold** text.
```

## 限制

Markdown 导出不支持：
- 复杂表格合并单元格（输出标准 Markdown 表格）
- 自定义 CSS 样式（无对应 Markdown 语法）
- 交互元素（如 collapsible admonition 展开状态）
- 精确的排版控制（如分页、页面边距）

这些场景应使用 HTML/DOCX/PDF 等格式。

## 相关概念

- [00-exporter-architecture](00-exporter-architecture.md)：统一导出架构
- [01-html-export](01-html-export.md)：HTML 导出（富文本格式）
- [01-multi-format-export](../examples/01-multi-format-export.md)：多格式到处示例
