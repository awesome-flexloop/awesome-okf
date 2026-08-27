---
type: Concept
title: mdformat 插件架构与 mdformat-myst 组成
description: 解析 mdformat 插件机制以及 mdformat-myst 如何通过组合扩展实现 MyST 支持。
tags: [plugin, architecture, mdformat, markdown-it, extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-plugin
    resource: /references/source-plugin.md
    title: mdformat-myst 插件核心实现
---

## mdformat 插件机制

mdformat 基于 [markdown-it-py](https://github.com/executablebooks/markdown-it-py) 解析器构建，采用插件化架构扩展语法支持。每个 mdformat 插件通过 Python entry points 注册为 `mdformat.parser_extension` 组下的一个模块。

插件模块需要实现以下标准接口：

| 接口 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `update_mdit(mdit)` | 函数 | 是 | 配置 markdown-it 解析器实例 |
| `RENDERERS` | 字典 | 否 | Token 类型到渲染函数的映射 |
| `POSTPROCESSORS` | 字典 | 否 | 后处理器映射 |
| `add_cli_argument_group(group)` | 函数 | 否 | 添加 CLI 参数 |

插件入口点在 `pyproject.toml` 中配置：

```toml
[tool.flit.entrypoints."mdformat.parser_extension"]
myst = "mdformat_myst.plugin"
```

## update_mdit 的角色

`update_mdit(mdit: MarkdownIt) -> None` 是插件的核心入口函数，在 markdown-it 解析器初始化时被调用。该函数接收一个 `MarkdownIt` 实例，可以：

- 调用 `mdit.use(plugin)` 加载 markdown-it 语法插件
- 调用 `mdit.add_render_rule()` 添加或覆盖渲染规则
- 修改 `mdit.options` 配置解析器行为
- 向 `mdit.options["parser_extension"]` 添加其他 mdformat 插件依赖

## mdformat-myst 的组合式设计

mdformat-myst 并非独立实现 MyST 语法解析，而是通过 `update_mdit` 一次性加载 6 个底层扩展：

### mdformat 内置扩展

这些扩展通过 `mdformat.plugins.PARSER_EXTENSIONS` 字典获取并添加到解析器：

1. **tables**：表格语法支持（来自 mdformat-gfm）
2. **front_matters**：YAML front matter 支持（来自 mdformat-front-matters）
3. **footnote**：脚注语法支持（来自 mdformat-footnote）

添加方式是检查扩展是否已存在于 `mdit.options["parser_extension"]`，若不存在则追加并调用其 `update_mdit(mdit)` 方法。

### mdit-py-plugins 扩展

这些扩展通过 `mdit.use()` 直接加载 markdown-it-py 插件：

4. **myst_role_plugin**：MyST 角色语法（`{role}`content``）
5. **myst_block_plugin**：MyST 块级语法（行注释 `%`、块中断 `+++`、目标 `(target)=`）
6. **dollarmath_plugin**：美元数学公式语法（`$inline$`、`$$block$$`）

## RENDERERS 与 POSTPROCESSORS

加载扩展后，markdown-it 解析器能识别 MyST 语法生成的 token，但需要对应的渲染函数才能正确输出格式化后的 Markdown 文本。

`RENDERERS` 字典将 markdown-it 生成的 token 类型映射到自定义渲染函数。`POSTPROCESSORS` 字典则在渲染完成后对特定节点（如 paragraph、text）的输出进行二次处理（转义特殊字符）。

## HTML 渲染桩

在 `update_mdit` 的最后，插件将 `fence` 和 `code_block` 的 HTML 渲染规则替换为返回空字符串的 `render_fence_html` 函数。这是因为 MyST 指令被解析为 code fence，插件对 fence 渲染做了修改，导致 CommonMark AST 验证失败。通过覆盖 HTML 渲染为空，可以绕过 mdformat 的 AST 一致性检查。

## 插件依赖关系图

```
mdformat-myst
├── mdformat (核心引擎)
├── mdformat-gfm (tables)
├── mdformat-front-matters (YAML front matter)
├── mdformat-footnote (脚注)
├── mdit-py-plugins
│   ├── myst_role_plugin (角色)
│   ├── myst_block_plugin (块语法)
│   └── dollarmath_plugin (数学)
└── ruamel.yaml (指令选项格式化)
```

## 相关概念

- [MyST 语法支持](02-myst-syntax-support.md)
- [指令选项 YAML 格式化](03-directive-formatting.md)
- [转义机制与后处理器](04-escaping-and-postprocessors.md)
