---
type: Example
title: MyST 文档格式化示例
description: 使用 mdformat-myst 格式化包含各种 MyST 语法的 Markdown 文档。
tags: [example, formatting, myst, cli, directive]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:58:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-plugin
    resource: /references/source-plugin.md
    title: mdformat-myst 插件核心实现
---

## 格式化包含 MyST 语法的文档

创建一个包含 MyST 角色、指令、数学公式和注释的 Markdown 文件 `example.md`：

````markdown
# MyST 示例文档

这是一个包含{math}`E=mc^2`行内公式的段落。

% 这是一行MyST注释
% 这是第二行注释

(section-target)=

## 数学公式

$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$ (eq:sum-formula)

块中断分隔：

+++

```{note} 注意
---
class: warning
---
这是一个注意指令，选项YAML会被自动格式化。
```

{abbr}`HTML (HyperText Markup Language)` 是缩写角色。

价格从 \$100 降到 \$50（美元符号已转义）。
````

运行格式化命令：

```bash
mdformat example.md
```

格式化后，插件会自动：

1. 规范化指令选项 YAML 的缩进（2空格 mapping 缩进，4空格 sequence 缩进）
2. 转义普通文本中可能误解析为 MyST 语法的字符
3. 规范化数学公式和角色的格式
4. 正确处理多行注释的 `%` 前缀

## 与 mdformat 其他插件协同

mdformat-myst 自动启用 tables、front_matters、footnote、GFM 等插件，因此你的 MyST 文档中可以同时使用：

- GFM 表格
- YAML front matter
- 脚注
- MyST 角色和指令
- 数学公式

```markdown
---
title: 综合示例
author: 作者
---

# 章节一

| 列1 | 列2 |
|-----|-----|
| A   | B   |

正文[^1]。

[^1]: 这是脚注内容。
```

## 检查格式化结果

使用 `--check` 参数检查文件是否已格式化（不修改文件）：

```bash
mdformat --check example.md
```

退出码 0 表示已格式化，非 0 表示需要格式化。

## 相关概念

- [MyST 语法支持](../concepts/02-myst-syntax-support.md)
- [指令选项 YAML 格式化](../concepts/03-directive-formatting.md)
- [插件架构](../concepts/01-plugin-architecture.md)
