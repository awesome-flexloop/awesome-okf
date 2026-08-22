---
type: Concept
title: 三阶段转换流水线架构
description: rst-to-myst 的核心架构：RST→docutils AST→markdown-it tokens→MyST Markdown 三阶段转换。
tags: [pipeline, architecture, ast, tokens, rendering, conversion-flow]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-parser
    resource: /references/source-parser.md
    title: rst-to-myst RST 解析器模块
  - id: src-markdownit
    resource: /references/source-markdownit.md
    title: rst-to-myst MarkdownIt 渲染器
  - id: src-mdformat-render
    resource: /references/source-mdformat-render.md
    title: rst-to-myst mdformat 渲染集成
---

## 为什么需要多阶段转换

直接进行 RST→Markdown 文本替换看似简单，但存在以下问题：
- RST 语法复杂，上下文相关，正则替换难以正确处理嵌套结构
- 需要理解指令和角色的语义才能正确映射
- 输出需要格式化（缩进、空行、列表紧密度等）

rst-to-myst 采用三阶段流水线，每个阶段有明确的输入输出和职责边界，中间结果可检查、可调试。

## 流水线总览

```
输入 RST 文本
    │
    ▼
┌─────────────────────────────┐
│  阶段1: RST 解析             │
│  to_docutils_ast()          │
│  LosslessRSTParser          │
│  输出: docutils AST         │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  阶段2: Token 生成          │
│  MarkdownItRenderer         │
│  docutils NodeVisitor       │
│  输出: markdown-it tokens   │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  阶段3: Markdown 渲染       │
│  from_tokens()              │
│  mdformat MDRenderer        │
│  输出: MyST Markdown 文本   │
└─────────────────────────────┘
```

## 阶段 1：RST 解析

**入口函数**：`to_docutils_ast()`
**核心类**：`LosslessRSTParser`（继承 `docutils.parsers.rst.Parser`）
**输出**：`docutils.nodes.document` 对象 + 警告流

此阶段的关键设计是"无损解析"：
- 不执行指令的 `run()` 方法（保留指令原始结构）
- 使用自定义 `InlinerMyst` 和状态类
- 应用一组自定义 Transform 修正 AST

解析完成后按顺序应用以下 Transform：
1. `PropagateTargets` - 传播空的内部目标
2. `FrontMatter` - 提取开头的 field_list 为 FrontMatterNode
3. `AnonymousHyperlinks` - 链接匿名引用到目标
4. `Footnotes` - 为自动编号脚注分配编号
5. `StripFootnoteLabel` - 移除脚注的 label 子节点
6. `ResolveListItems` - 为列表项传播 bullet/prefix 属性

## 阶段 2：Token 生成

**入口类**：`MarkdownItRenderer`（继承 `nodes.GenericNodeVisitor`）
**核心方法**：`to_tokens()`, `add_token()`, `visit_*()/depart_*()`
**输出**：`RenderOutput(tokens, env)` NamedTuple

此阶段使用 Visitor 模式遍历 docutils AST：
- `document.walkabout(self)` 触发每个节点的 visit/depart 方法
- `add_token()` 方法自动管理 inline 容器和嵌套计数
- 遇到未实现的节点类型输出警告（不崩溃）
- Front matter tokens 在遍历完成后前置到 token 流开头

Token 流遵循 markdown-it 规范，使用 open/close 对表示嵌套结构。

## 阶段 3：Markdown 渲染

**入口函数**：`from_tokens()`
**核心类**：`mdformat.renderer.MDRenderer`
**输出**：格式化的 MyST Markdown 文本字符串

此阶段使用 mdformat 的渲染引擎：
- 加载 myst/tables/frontmatter/deflist 扩展 + AdditionalRenderers
- 自定义渲染器处理：front matter、替换、指令、未处理文本
- 设置 `finalize=False` 禁用 mdformat 默认的引用过滤
- 手动输出所有引用定义（不仅是使用过的）

渲染后调用 `get_myst_extensions()` 扫描 tokens 推断所需 MyST 扩展。

## 调试方法

每个阶段的结果都可以单独检查：

```bash
# 检查阶段1输出（docutils AST）
rst2myst ast input.rst

# 检查阶段2输出（markdown-it tokens）
rst2myst tokens input.rst

# 检查阶段3输出（最终 Markdown）
rst2myst stream input.rst
```

当转换结果不符合预期时，通过对比三个阶段的输出可以快速定位问题发生在哪个阶段。

## 最终输出

`rst_to_myst()` 函数串联三个阶段，返回 `ConvertedOutput`：
- `text`：最终 MyST Markdown 文本（末尾带换行）
- `tokens`：markdown-it token 列表（可用于进一步处理）
- `env`：渲染环境（包含 references、duplicate_refs 等）
- `warning_stream`：警告输出流
- `extensions`：推断的 MyST 扩展需求集合

## 相关概念

- [LosslessRSTParser 与自定义 Transform](/concepts/04-lossless-parser.md)
- [MarkdownItRenderer 与 AST→Token 遍历](/concepts/06-token-rendering.md)
- [mdformat 渲染集成与自定义渲染器](/concepts/07-mdformat-integration.md)
