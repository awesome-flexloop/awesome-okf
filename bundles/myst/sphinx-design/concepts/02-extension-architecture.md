---
type: concept
title: 扩展架构与两阶段渲染
description: sphinx-design 的组件注册机制、SdDirective 基类、两阶段渲染架构与 Marker-Class Stash/Graft 模式
tags:
- sphinx
- extension
- architecture
- post-transform
- directive
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/extension.py
- sphinx_design/shared.py
- sphinx_design/config.py
---

# 扩展架构与两阶段渲染

## 整体架构

sphinx-design 的架构可以分为三层：

```
┌─────────────────────────────────────────────────────┐
│  配置层 (config.py)                                  │
│  SdConfig dataclass → sd_* Sphinx 配置值            │
│  类型验证 + 默认值回退 + TOML 兼容                    │
├─────────────────────────────────────────────────────┤
│  组件层 (各模块)                                     │
│  SdDirective 子类 → run_with_defaults() → AST节点   │
│  SphinxRole 子类 → run() → 行内节点                 │
│  SphinxPostTransform 子类 → HTML 结构特化            │
├─────────────────────────────────────────────────────┤
│  渲染层                                              │
│  自定义 Node Visitor → HTML/LaTeX/Text 输出         │
│  sphinx-design.min.css → 样式                       │
│  design-tabs.js → Tab 交互增强                      │
└─────────────────────────────────────────────────────┘
```

## 入口与初始化流程

`setup_extension(app)` 是扩展的主入口，执行顺序如下：

1. **配置注册**：`setup_sd_config(app)` 遍历 `SdConfig` 的所有 dataclass 字段，通过 `app.add_config_value()` 注册为 `sd_*` 前缀配置值，同时连接 `config-inited`（priority=400，验证/回退无效值）和 `builder-inited`（挂载配置到 env）事件。

2. **静态资源注册**：连接 `builder-inited` 事件到 `add_static_assets`，该函数仅在 HTML 格式时注册 CSS 和 JS 文件。

3. **容器 visitor 覆盖**：覆盖 `nodes.container` 的 HTML visitor（`override=True`），当节点 `is_div=True` 时输出不带 `container` 类的 `<div>`，避免与 Bootstrap CSS 冲突。

4. **PassthroughTextElement 注册**：为所有输出格式注册空 visitor，用于引用节点在段落外正确渲染。

5. **组件注册**（在 `capture_directives` 上下文管理器内）：
   - `div` 指令 + `AddFirstTitleCss` transform
   - 徽章与按钮（badges_buttons）
   - 卡片（cards）
   - 网格（grids）
   - 下拉折叠（dropdown）
   - 图标（icons）
   - 标签页（tabs）
   - 文章信息（article_info）

6. **自定义指令注册**：连接 `config-inited` 事件到 `setup_custom_directives`，根据 `sd_custom_directives` 配置创建用户自定义指令。

## SdDirective 基类

所有 sphinx-design 的指令都继承自 `SdDirective`（继承 `SphinxDirective`），它提供两个核心能力：

### 1. 模板方法模式

`SdDirective.run()` 被 `@final` 标记为不可重写，它实现了统一的前置处理逻辑：

```python
@final
def run(self) -> list[nodes.Node]:
    # 1. 查找自定义指令配置
    if data := get_sd_config(self.env).custom_directives.get(self.name):
        # 2. 应用默认参数
        if (not self.arguments) and (argument := data.get("argument")):
            self.arguments = [str(argument)]
        # 3. 应用默认选项
        for key, value in data.get("options", {}).items():
            if key not in self.options and key in self.option_spec:
                try:
                    self.options[key] = self.option_spec``[key](str(value.md)``)
                except Exception:
                    LOGGER.warning(...)
    # 4. 调用子类实现
    return self.run_with_defaults()
```

子类只需实现 `run_with_defaults()` 方法，无需关心自定义指令的默认值处理。

### 2. 组件工厂

`create_component(name, classes, **attributes)` 是创建组件容器节点的工厂函数：

```python
def create_component(name, classes=(), **attributes):
    return nodes.container(
        is_div=True,           # 标记为 div 而非默认 container
        design_component=name, # 组件类型标记
        classes=list(classes),
        **attributes
    )
```

`is_component(node, name)` 函数通过检查 `design_component` 属性来判断节点类型，这在 PostTransform 和子元素验证中广泛使用。

## 两阶段渲染架构

sphinx-design 的交互组件（dropdown、tab）采用两阶段渲染策略，这是其架构的核心设计：

### 阶段一：指令解析（所有输出格式通用）

在指令的 `run_with_defaults()` 方法中，生成**语义化的通用 AST**：

```
dropdown 指令:
  container(design_component="dropdown", has_title=True, ...)
    ├── rubric (标题文本, sd-summary-title 类)
    └── ... (内容节点)

tab-item 指令:
  container(design_component="tab-item", selected=True, ...)
    ├── rubric (标签文本, sd-tab-label 类, sync_id 属性)
    └── container(design_component="tab-content", sd-tab-content 类)
         └── ... (内容节点)
```

这种结构在非 HTML 格式中会降级为"标题+内容"的线性渲染（rubric 在 docutils 中默认渲染为粗体标题），保证 LaTeX/PDF/man 等输出可读。

### 阶段二：Post-Transform HTML 特化（仅 HTML）

SphinxPostTransform 在构建后期（doctree 解析完成后）遍历文档树，将通用 AST 转换为 HTML 专用结构：

**DropdownHtmlTransform**（priority=199）：
```html
<details class="sd-sphinx-override sd-dropdown sd-card">
  <summary class="sd-summary-title sd-card-header">
    <span class="sd-summary-icon">SVG图标</span>
    <span class="sd-summary-text">标题文本</span>
    <span class="sd-summary-state-marker">chevron SVG</span>
  </summary>
  <div class="sd-summary-content sd-card-body">
    ...内容
  </div>
</details>
```

**TabSetHtmlTransform**（priority=200）：
```html
<div class="sd-tab-set">
  <input type="radio" id="sd-tab-item-0" name="sd-tab-set-0" checked="checked">
  <label for="sd-tab-item-0" data-sync-group="code" data-sync-id="python">Python</label>
  <div class="sd-tab-content" id="sd-tab-item-0-content">...内容</div>
  
  <input type="radio" id="sd-tab-item-1" name="sd-tab-set-0">
  <label for="sd-tab-item-1" data-sync-group="code" data-sync-id="javascript">JavaScript</label>
  <div class="sd-tab-content" id="sd-tab-item-1-content">...内容</div>
</div>
```

关键特点：
- 使用原生 `<details>/<summary>` 实现 dropdown，零 JavaScript
- Tab 使用 CSS `:checked` 伪类 + hidden radio input 实现切换，仅同步需要 JS
- PostTransform 优先级确保嵌套组件正确处理（dropdown 199 < tab 200，tab 在 dropdown 之后转换）
- 注入 ARIA 属性（`aria-controls`）增强可访问性

## Marker-Class Stash/Graft 模式

这是 sphinx-design 解决 Sphinx 交叉引用富文本丢失问题的精巧模式，用于 `button-ref` 和 `bdg-ref` 组件。

### 问题背景

Sphinx 的标准域交叉引用解析器（std-domain resolver）在处理显式标题的 ref/doc 引用时，会调用 `node.astext()` 重建引用节点内容，这会将所有内联标记（emphasis、strong、图标等）扁平化为纯文本。例如：

```rst
.. button-ref:: target

   **粗体** :fas:`rocket` 带图标
```

解析后按钮内的富文本会变成纯文本 "粗体 rocket 带图标"，丢失加粗和图标。

### 解决方案：两个 PostTransform + Marker Class

**Stash 阶段**（高优先级，在 resolver 之前运行）：

1. 遍历所有 `pending_xref` 节点，找到带 `sd-btn` 类的 button-ref
2. 生成唯一 marker class：`sd-button-ref-content-{index}`
3. 深拷贝富文本内容到 `document.sd_button_ref_content` dict（瞬态 Python 属性，不序列化）
4. 将 marker class 添加到 pending_xref 的 classes 中
5. Badge tooltip 使用相同机制（priority=5），存储 tooltip 字符串而非节点

**Resolver 运行**：Sphinx 内置的 ReferencesResolver（priority=10）和 myst-parser 的 resolver（priority=9）执行交叉引用解析，将 pending_xref 替换为 nodes.reference。由于 class 属性会被 docutils 的 `replace_self` 复制到替换节点，marker class 得以保留。

**Graft 阶段**（低优先级，在 resolver 之后运行）：

1. 遍历文档中所有 Element，查找带有 marker class 的节点
2. 如果是已解析的 `nodes.reference`，用暂存的富文本内容替换其子节点
3. 移除 marker class
4. 清空暂存 dict（避免内存泄漏）

```
时间线:
  priority 5   BadgeRefTooltipStash     → 暂存 tooltip 到 marker class
  priority 8   ButtonRefContentStash    → 暂存富文本到 marker class
  priority 9   myst-parser resolver     → 解析 myst 类型引用
  priority 10  ReferencesResolver       → 解析 std 域引用（扁平化内容）
  priority 11  ButtonRefContentGraft    → 恢复富文本内容
  priority 12  BadgeRefTooltipGraft     → 恢复 tooltip 到 reftitle
```

### 为什么用 class 作为关联 key？

docutils 的 `update_basic_atts` 在节点替换时只复制"基本"属性：ids、classes、names。自定义节点属性（如 `sd_tooltip`）不会被复制。class 是少数被可靠复制的属性之一，因此被巧妙用作暂存数据与已解析节点之间的关联桥梁。

## 配置系统

`SdConfig` dataclass 是配置的中心化声明：

```python
@dc.dataclass
class SdConfig:
    custom_directives: dict[str, Any] = dc.field(default_factory=dict, ...)
    fontawesome_source: str = dc.field(default="none", ...)
    fontawesome_cdn_url: str = dc.field(default="https://cdnjs...", ...)
    fontawesome_version: str = dc.field(default="as-named", ...)
    fontawesome_latex: bool | str = dc.field(default=False, ...)
    tabs_storage_prefix: str = dc.field(default="sphinx-design-tab-id-", ...)
```

验证策略：
- **无效值不阻断构建**：发出警告后回退到默认值
- **映射类型逐条验证**：`custom_directives` 中单个无效条目被丢弃，不影响其他条目
- **两层缓存**：`config-inited` 验证并修正值 → `builder-inited` 挂载到 `env.sd_config` → `get_sd_config(env)` 懒加载获取

## capture_directives 上下文管理器

为了支持 `sd_custom_directives` 的 inherit 目标验证，`capture_directives(app)` 通过 monkey-patch `app.add_directive` 拦截所有指令注册：

```python
@contextmanager
def capture_directives(app):
    directive_map = {}
    add_directive = app.add_directive
    def _add_directive(name, directive, **kwargs):
        directive_map[name] = directive  # 捕获指令类
        add_directive(name, directive, **kwargs)
    app.add_directive = _add_directive
    yield directive_map
    app.add_directive = add_directive  # 恢复原方法
```

退出上下文后 `directive_map` 包含所有 sphinx-design 注册的指令名→类映射，供 `setup_custom_directives` 验证 inherit 目标和选项键。

## 相关概念

- [配置与自定义指令](/concepts/09-configuration.md) — 配置项详解与自定义指令用法
- [徽章与按钮](/concepts/07-badges-buttons.md) — 徽章/按钮指令与角色详解（含 Stash/Graft 实例）
- [标签页组件](/concepts/06-dropdown-tabs.md) — Tab 两阶段渲染与 JS 同步机制
