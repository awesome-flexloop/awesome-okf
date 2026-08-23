---
type: Concept
title: 解析器与渲染器
description: create_md_parser 工厂函数、DocutilsRenderer/SphinxRenderer 的工作机制
tags: [myst, sphinx, parser, renderer, markdown-it, docutils, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 解析器与渲染器

MyST-Parser 的核心由两部分组成：markdown-it-py 解析器配置（`create_md_parser`）和 Token 到 docutils AST 的渲染器（`DocutilsRenderer`/`SphinxRenderer`）。

## create_md_parser 工厂函数

`create_md_parser(config, renderer)` 是解析器的工厂函数，接收 `MdParserConfig` 和渲染器类，返回配置好的 `MarkdownIt` 实例。

### 解析器创建流程

```python
def create_md_parser(config, renderer):
    # 1. 模式选择
    if config.commonmark_only:
        md = MarkdownIt("commonmark", renderer_cls=renderer).use(wordcount_plugin)
        return md
    if config.gfm_only:
        md = MarkdownIt("commonmark", renderer_cls=renderer).use(gfm_plugin).use(wordcount_plugin)
        return md

    # 2. 默认模式：CommonMark 基础 + MyST 核心插件
    md = (MarkdownIt("commonmark", renderer_cls=renderer)
        .enable("table")
        .use(front_matter_plugin)    # YAML frontmatter
        .use(myst_block_plugin)      # MyST 块级语法（指令、注释）
        .use(myst_role_plugin)       # MyST 角色语法 {role}`text`
        .use(footnote_plugin)        # 脚注
        .use(wordcount_plugin)       # 字数统计
    )

    # 3. 按 enable_extensions 按需加载扩展插件
    if "dollarmath" in config.enable_extensions:
        md.use(dollarmath_plugin, ...)
    if "colon_fence" in config.enable_extensions:
        md.block.ruler.before("fence", "colon_fence", colon_fence_rule, ...)
    # ... 其他扩展

    return md
```

### 插件注册的两种方式

1. **`.use(plugin_func, **options)`**：标准 markdown-it-py 插件注册，用于大部分扩展
2. **`.block.ruler.before()`/`.after()`**：直接在规则链中插入自定义规则，用于 colon_fence 等需要精确位置的扩展

## DocutilsRenderer 基类

`DocutilsRenderer` 实现 markdown-it-py 的 `RendererProtocol` 接口，负责将 Token 流转换为 docutils 节点树。

### 核心机制

**自动方法发现**：`__init__` 中自动收集所有 `render_*` 方法构建规则表：

```python
self.rules = {
    k: v for k, v in inspect.getmembers(self, predicate=inspect.ismethod)
    if k.startswith("render_") and k != "render_children"
}
```

**渲染状态**：`setup_render(options, env)` 初始化每次渲染的状态：

| 属性 | 类型 | 说明 |
|------|------|------|
| `md_config` | MdParserConfig | 解析配置 |
| `document` | nodes.document | docutils 文档根节点 |
| `current_node` | nodes.Element | 当前节点（新节点追加到此处） |
| `reporter` | Reporter | 警告/错误报告器 |
| `_level_to_section` | dict | 标题级别到 section 节点的映射 |
| `_heading_slugs` | dict | 标题 slug 注册表 |

### Token 到节点的渲染流程

```python
def _render_tokens(self, tokens):
    # 1. 行号转换：0-based → 1-based
    for token in tokens:
        token.map = [token.map[0] + 1, token.map[1] + 1]

    # 2. 嵌套渲染：遍历 Token 树
    for token in tokens:
        # 处理 opening token
        if token.nesting == 1:  # open tag
            self.rules``[token.type](token)``
        # 处理 self-closing token
        elif token.nesting == 0:
            self.rules``[token.type](token)``
        # 处理 closing token
        elif token.nesting == -1:
            # 关闭当前节点，返回父节点
            pass
```

### 上下文管理器

渲染器使用 `current_node_context()` 上下文管理器管理节点栈：

```python
@contextmanager
def current_node_context(self, node):
    prev_node = self.current_node
    self.current_node = node
    yield
    self.current_node = prev_node
```

## SphinxRenderer 子类

`SphinxRenderer` 继承 `DocutilsRenderer`，添加 Sphinx 特有的渲染能力。

### 额外功能

1. **跨文档链接**：`render_link_project()` 处理 ```[text](./doc.md#anchor)``` 形式的文档间引用，生成 `addnodes.pending_xref` 节点
2. **下载引用**：处理 `{download}` 角色，生成 `addnodes.download_reference` 节点
3. **Sphinx 环境访问**：`sphinx_env` 属性直接返回 `BuildEnvironment`（不返回 None）
4. **相对路径处理**：`_handle_relative_docs()` 处理 include 指令的相对路径

## 两个解析器类

### MystParser（Sphinx 环境）

```python
class MystParser(SphinxParser):
    supported = ("md", "markdown", "myst")

    def parse(self, inputstring, document):
        config = document.settings.env.myst_config  # 全局配置
        topmatter = read_topmatter(inputstring)     # 读取 frontmatter
        if topmatter:
            config = merge_file_level(config, topmatter, warning)  # 合并文件级配置
        parser = create_md_parser(config, SphinxRenderer)
        parser.options["document"] = document
        parser.render(inputstring)
```

### Parser（Docutils 独立环境）

```python
class Parser(RstParser):
    supported = ("md", "markdown", "myst")

    def parse(self, inputstring, document):
        config = create_myst_config(document.settings)  # 从 settings 创建配置
        # ... 同样读取 frontmatter 并合并
        parser = create_md_parser(config, DocutilsRenderer)  # 使用基类渲染器
        parser.options["document"] = document
        parser.render(inputstring)
```

## 解析器选择逻辑

| 使用场景 | 解析器类 | 渲染器类 | 配置来源 |
|---------|---------|---------|---------|
| Sphinx build | MystParser(SphinxParser) | SphinxRenderer | app.env.myst_config |
| myst-docutils-html CLI | Parser(RstParser) | DocutilsRenderer | CLI 参数/frontmatter |
| myst-docutils-demo CLI | Parser(RstParser) | DocutilsRenderer | CLI 参数 |
| RST include | sphinx_.py 中的 Parser 别名 | SphinxRenderer | Sphinx 配置 |

## 相关概念

- [三阶段解析管线](/concepts/03-architecture-pipeline.md)
- [配置系统](/concepts/04-config-system.md)
- [指令与角色](/concepts/07-directives-and-roles.md)
- [Sphinx 集成机制](/concepts/11-sphinx-integration.md)
