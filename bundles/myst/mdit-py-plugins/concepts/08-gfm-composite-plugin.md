---
type: Concept
title: GFM 组合插件
description: gfm_plugin组合多个插件和配置一键启用GitHub Flavored Markdown风格，以及插件组合模式
tags:
- mdit-py-plugins
- gfm
- composite-plugin
- github
- version-compat
difficulty: 高级
estimated_time: 10分钟
prerequisites:
- 02-using-plugins
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: mdit-py-plugins-source
  resource: /references/plugin-source-mapping.md
  title: mdit-py-plugins 源码路径映射
---

# GFM 组合插件

gfm_plugin 是一个"元插件"——它本身不定义任何解析规则，而是组合其他插件和配置来模拟 GitHub Flavored Markdown 渲染效果。

## 启用内容

```python
from mdit_py_plugins.gfm import gfm_plugin

md = MarkdownIt().use(gfm_plugin)
```

执行以下操作：

1. **启用内置规则**：
   - `md.enable("table")` — GFM表格
   - `md.enable("strikethrough")` — 删除线

2. **设置GFM选项**（markdown-it-py >= 4.1.0）：
   - `options["tasklists"] = True` — 任务列表
   - `options["alerts"] = True` — GitHub告警块（> [!NOTE]）
   - `options["strikethrough_single_tilde"] = True` — 单~删除线

3. **加载插件**：
   - `md.use(gfm_autolink_plugin)` — GFM自动链接（URL文本自动转链接）
   - `md.use(footnote_plugin, inline=False)` — 脚注（不含行内脚注）

4. **可选**：
   - `dollarmath=True` → `md.use(dollarmath_plugin, allow_blank_lines=False)`
   - `front_matter=True` → `md.use(front_matter_plugin)`

## 版本兼容检查

gfm_plugin 在调用时检查 markdown-it-py 版本：

```python
_MIN_VERSION = (4, 1, 0)
if _parse_version(_mdit_version) < _MIN_VERSION:
    raise RuntimeError(f"requires markdown-it-py >= 4.1.0 (installed: {_mdit_version})")
```

这是因为 tasklists 和 alerts 选项是 markdown-it-py 4.1.0 新增的内置功能。

## 插件组合模式

gfm_plugin 展示了插件的可组合性：

```python
def composite_plugin(md, option1=False, option2=False):
    # 1. 启用内置规则
    md.enable("some_rule")
    
    # 2. 设置选项
    md.options["key"] = value
    
    # 3. 加载子插件
    md.use(child_plugin1)
    md.use(child_plugin2, child_option=True)
    
    # 4. 可选加载
    if option1:
        md.use(optional_plugin)
```

关键点：
- 插件可以 `use()` 其他插件（形成依赖链）
- 可以 `enable()`/`disable()` 内置规则
- 可以修改 `md.options`
- 可以进行版本检查
- 使用 `@lru_cache` 缓存版本解析结果

## 与 gfm_like 预设的区别

markdown-it-py 内置的 `"gfm-like"` 预设：
- 启用table、strikethrough
- 设置linkify=True
- 不包含脚注、自动链接插件、tasklists(4.1+)、alerts(4.1+)

gfm_plugin：
- 更接近现代 GitHub 渲染
- 包含脚注、自动链接
- 使用 markdown-it-py 4.1.0+ 的内置tasklists/alerts
- 可选dollarmath和front_matter
- 要求markdown-it-py >= 4.1.0
