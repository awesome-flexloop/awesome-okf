---
type: Concept
title: 三阶段解析管线
description: MyST-Parser 的 Markdown→Token→AST→输出三阶段解析管线架构详解
tags: [myst, sphinx, architecture, pipeline, parsing, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 三阶段解析管线

MyST-Parser 采用清晰的三阶段管线架构，将 Markdown 文本逐步转换为最终输出。每个阶段职责单一，通过数据结构（Token 流、AST）传递结果。

## 阶段一：Markdown 解析（markdown-it-py）

第一阶段由 `create_md_parser()` 工厂函数配置的 `MarkdownIt` 实例完成。输入是 MyST Markdown 文本，输出是 markdown-it Token 流。

### 解析器配置流程

1. **模式选择**：
   - `commonmark_only=True`：仅启用 wordcount 插件，严格 CommonMark
   - `gfm_only=True`：启用 gfm_plugin（含 tasklist）+ wordcount
   - 默认模式：CommonMark + table + 基础 MyST 插件

2. **基础插件加载**（默认模式）：
   - `front_matter_plugin`：解析 YAML frontmatter
   - `myst_block_plugin`：MyST 块级语法（指令、注释等）
   - `myst_role_plugin`：MyST 角色语法（`{role}`text``）
   - `footnote_plugin`：脚注支持
   - `wordcount_plugin`：字数统计

3. **扩展插件按需加载**：根据 `enable_extensions` 配置加载 18 个可选扩展

### Token 结构

markdown-it Token 包含：
- `type`：Token 类型（如 `heading_open`、`paragraph_open`、`inline`、`fence`）
- `tag`：HTML 标签名（如 `h1`、`p`、`code`）
- `attrs`：属性列表
- `map`：行号映射 `[start_line, end_line]`（0-based）
- `children`：子 Token（inline 内容）
- `content`：文本内容
- `markup`：标记符号（如 `#`、``` ```、`:::`）

## 阶段二：Token 渲染（DocutilsRenderer / SphinxRenderer）

第二阶段由渲染器将 Token 流转换为 docutils AST（doctree）。核心是 `DocutilsRenderer` 类及其 Sphinx 扩展 `SphinxRenderer`。

### 渲染机制

1. **自动方法发现**：`__init__` 中通过 `inspect.getmembers()` 自动发现所有 `render_*` 方法构建规则映射表
2. **Token 分发**：遍历 Token 列表，按 token.type 调用对应的 `render_*` 方法
3. **节点构建**：每个 `render_*` 方法创建 docutils 节点（`nodes.paragraph`、`nodes.section` 等）并追加到 `current_node`

### 关键渲染方法

| Token 类型 | 渲染方法 | 生成的 docutils 节点 |
|-----------|---------|---------------------|
| heading_open/close | render_heading | nodes.section + nodes.title |
| paragraph_open/close | render_paragraph | nodes.paragraph |
| fence/code_block | render_fence/render_code_block | nodes.literal_block（可能带 Pygments 高亮） |
| inline | render_inline | 递归渲染子 Token |
| link_open/close | render_link | nodes.reference / addnodes.pending_xref |
| image | render_image | nodes.image |
| myst_role | render_myst_role | 通过 docutils 角色系统生成节点 |
| myst_directive | 处理指令 | 通过 Mock 层调用 docutils 指令 |

### 行号处理

渲染前将 Token 的 `map` 行号从 0-based 转换为 1-based（`token.map = [token.map[0] + 1, token.map[1] + 1]`），并传播给子 Token。

## 阶段三：Sphinx 后处理（Post-Transforms）

第三阶段在 Sphinx 环境中执行 Post-Transform，完成引用解析和最终调整。

### 注册的 Transforms

| Transform | 阶段 | 优先级 | 功能 |
|-----------|------|--------|------|
| UnreferencedFootnotesDetector | Transform | 默认 | 检测未引用脚注（替换 Sphinx 内置版本） |
| SortFootnotes | Transform | 默认 | 排序脚注 |
| CollectFootnotes | Transform | 默认 | 收集脚注到文档末尾 |
| AddSlugIds | Transform | 默认 | 添加 slug 锚点 ID |
| PrioritiseExplicitIds | Transform | 默认 | 优先使用显式 ID |
| ResolveAnchorIds | Transform | 默认 | 解析锚点 ID |
| MystReferenceResolver | Post-Transform | 9 | 解析 MyST 交叉引用（高于默认 ReferencesResolver 的 10） |

### MystReferenceResolver 解析流程

对于每个 `pending_xref` 节点（`reftype == "myst"`）：

1. 如果 `refdomain == "doc"`：调用 `resolve_myst_ref_doc()` 解析文档引用
2. 否则调用 `resolve_myst_ref_any()` 依次尝试：
   - std:ref 标签引用
   - std:doc 文档引用
   - std domain objects
   - 其他 domain 的 resolve_any_xref
3. 本地未找到 → 尝试 intersphinx（`_resolve_myst_ref_intersphinx()`）
4. Intersphinx 未找到 → 尝试本地锚点回退
5. 全部失败 → 发出警告并降级为外部链接

## 配置如何参与管线

- **builder-inited 事件**：`create_myst_config(app)` 从 `app.config` 读取所有 `myst_*` 配置，创建 `MdParserConfig` 存入 `app.env.myst_config`
- **parse() 方法**：从 `document.settings.env.myst_config` 获取全局配置，读取文件 frontmatter 合并，创建解析器
- **渲染器初始化**：通过 `parser.options["document"] = document` 将 document 传入渲染器，`setup_render()` 从中提取 `md_config`

## 渲染器类层次

```
RendererProtocol (markdown-it-py)
    └── DocutilsRenderer (mdit_to_docutils/base.py)
        └── SphinxRenderer (mdit_to_docutils/sphinx_.py)
```

- `DocutilsRenderer`：不依赖 Sphinx，生成标准 docutils 节点，用于 CLI 工具
- `SphinxRenderer`：继承 DocutilsRenderer，添加 Sphinx 特有功能（pending_xref、download_reference、跨文档链接等）

## 相关概念

- [解析器与渲染器](/concepts/06-parser-and-renderer.md)
- [配置系统](/concepts/04-config-system.md)
- [指令与角色](/concepts/07-directives-and-roles.md)
- [交叉引用](/concepts/08-cross-references.md)
- [Sphinx 集成机制](/concepts/11-sphinx-integration.md)
