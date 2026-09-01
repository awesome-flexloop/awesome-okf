---
type: spec-facts
title: sphinx-design 源码事实采集
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
sources:
- sphinx_design/__init__.py
- sphinx_design/extension.py
- sphinx_design/shared.py
- sphinx_design/config.py
- sphinx_design/cards.py
- sphinx_design/grids.py
- sphinx_design/dropdown.py
- sphinx_design/tabs.py
- sphinx_design/badges_buttons.py
- sphinx_design/icons.py
- sphinx_design/article_info.py
- sphinx_design/static/design-tabs.js
- pyproject.toml
description: sphinx-design 源码事实清单
tags:
- sphinx-design
- spec
- facts
stale_after: '2027-08-23'
---

# sphinx-design 源码事实采集（零推理）

## F-001 ~ F-010：项目元数据与依赖

- F-001：包名为 `sphinx_design`（下划线），导入名为 `sphinx_design`，Sphinx 扩展名为 `sphinx_design`。
- F-002：项目描述为"A sphinx extension for designing beautiful, view size responsive web components"。
- F-003：作者 Chris Sewell，邮箱 chrisj_sewell@hotmail.com，MIT 许可证。
- F-004：构建系统使用 flit_core >=3.4,<4。
- F-005：要求 Python >=3.11。
- F-006：核心运行时依赖仅 `sphinx>=7.2,<10`，无其他第三方运行时依赖。
- F-007：支持 Python 3.11、3.12、3.13、3.14。
- F-008：`__init__.py` 导出 `setup(app)` 函数，调用 `extension.setup_extension(app)`，返回 `parallel_read_safe: True, parallel_write_safe: True`。
- F-009：版本号通过动态方式获取（`dynamic = ["version"]`）。
- F-010：关键词为 "sphinx", "extension", "material design", "web components"。

## F-011 ~ F-025：配置系统（config.py）

- F-011：所有配置集中声明在 `SdConfig` dataclass 中，字段使用 `@dc.dataclass` 装饰。
- F-012：配置在 Sphinx 中注册为 `sd_` 前缀的扁平配置值（如 `fontawesome_latex` → `sd_fontawesome_latex`）。
- F-013：`SdConfig.custom_directives` 类型为 `dict[str, Any]`，默认空 dict，用于自定义指令继承，validator 为 `validate_custom_directives`。
- F-014：`SdConfig.fontawesome_source` 类型 str，默认 `"none"`，可选值 `"none"` 或 `"cdn"`，控制 FontAwesome CSS 加载方式。
- F-015：`SdConfig.fontawesome_cdn_url` 类型 str，默认 `"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"`。
- F-016：`SdConfig.fontawesome_version` 类型 str，默认 `"as-named"`，可选值 `"as-named", "4", "5", "6"`，控制 FA 类名方案。
- F-017：`SdConfig.fontawesome_latex` 类型 `bool | str`，默认 `False`，接受 bool 或 `"none"/"fontawesome"/"fontawesome5"`。
- F-018：`SdConfig.tabs_storage_prefix` 类型 str，默认 `"sphinx-design-tab-id-"`，localStorage key 前缀，空字符串禁用持久化。
- F-019：`setup_sd_config(app)` 遍历 `SdConfig` 的所有 dataclass 字段，通过 `app.add_config_value(f"sd_{field.name}", default, "env")` 注册。
- F-020：`config-inited` 事件（priority=400）执行 `_validate_config_values`，无效值替换为默认值并发出警告。
- F-021：`builder-inited` 事件执行 `_attach_env_config`，将验证后的 `SdConfig` 实例挂载到 `app.env.sd_config`。
- F-022：`get_sd_config(env)` 函数从 `env.sd_config` 获取配置，若不存在则通过 `SdConfig.from_sphinx(env.config)` 创建并缓存。
- F-023：validator 系统模仿 attrs 库，`instance_of(type)` 检查类型，`one_of(allowed)` 检查枚举值。
- F-024：`fontawesome_latex_mode` 属性将 bool 值归一化为字符串：`True→"fontawesome"`, `False→"none"`。
- F-025：WARNING_TYPE 常量值为 `"design"`，所有警告类型为 `design.<subtype>`。

## F-026 ~ F-040：共享基础设施（shared.py）

- F-026：`SEMANTIC_COLORS` 元组包含 11 种语义色：primary, secondary, success, info, warning, danger, light, muted, dark, white, black。
- F-027：`SdDirective` 继承自 `SphinxDirective`，是所有 sphinx-design 指令的基类。
- F-028：`SdDirective.run()` 被 `@final` 标记，不可重写；它处理自定义指令默认参数/选项后调用 `self.run_with_defaults()`。
- F-029：`SdDirective.run_with_defaults()` 抛出 `NotImplementedError`，子类必须实现。
- F-030：`create_component(name, classes, rawtext="", children=(), **attributes)` 创建 `nodes.container`，设置 `is_div=True`、`design_component=name`、`classes=list(classes)`。
- F-031：`is_component(node, name)` 检查节点的 `design_component` 属性是否等于给定名称。
- F-032：`SKIP_CHILD_TYPES = (nodes.comment, nodes.target, nodes.system_message)`，是组件容器内结构上可忽略的节点类型。
- F-033：`is_ignorable_child(node)` 检查节点是否为 SKIP_CHILD_TYPES 的实例。
- F-034：`make_choice(choices)` 返回一个 lambda，调用 `directives.choice(argument, choices)` 做选项验证。
- F-035：`margin_option(argument)` 验证 margin 为 1 个（全方向）或 4 个（t/b/l/r）整数，0-5 或 "auto"，生成 `sd-m-*` 或 `sd-m{t,b,l,r}-*` CSS 类。
- F-036：`padding_option(argument)` 验证 padding 为 1 个或 4 个整数 0-5，生成 `sd-p-*` 或 `sd-p{t,b,l,r}-*` CSS 类。
- F-037：`text_align(argument)` 验证对齐值为 left/right/center/justify，生成 `sd-text-{value}` CSS 类。
- F-038：`PassthroughTextElement` 继承 `nodes.TextElement`，用于引用节点在段落外正确渲染的占位元素。
- F-039：`setup_custom_directives(app, config, directive_map)` 在 `config-inited` 事件中注册 `sd_custom_directives` 中声明的自定义指令，检查 inherit 目标和 option 键是否合法。
- F-040：自定义指令数据格式为 `{name: {inherit: str, argument?: str, options?: {str: str}}}`。

## F-041 ~ F-055：扩展入口与静态资源（extension.py）

- F-041：`setup_extension(app)` 是扩展的主入口函数。
- F-042：静态文件目录为 `Path(__file__).parent / "static"`，即 `sphinx_design/static/`。
- F-043：`add_static_assets(app)` 仅在 HTML 格式构建时执行，添加 CSS `sphinx-design.min.css` 和 JS `design-tabs.js`。
- F-044：`design-tabs.js` 通过 `app.add_js_file("design-tabs.js", **js_attributes)` 添加，携带 `data-sd-tabs-storage-prefix` 属性。
- F-045：扩展覆盖了 `nodes.container` 的 HTML visitor（`override=True`），用于阻止默认添加 `container` CSS 类。
- F-046：`visit_container` 方法：若节点 `is_div=True`，CSS 类为 `"docutils"`（不加 `container`），否则为 `"docutils container"`；支持 `style` 属性。
- F-047：`PassthroughTextElement` 在所有输出格式（html/latex/text/man/texinfo）中注册为 null visitor（不输出任何内容）。
- F-048：`Div` 指令（指令名 `"div"`）覆盖默认的 `container` 指令，生成不带 `container` CSS 类的 `<div>` 元素。
- F-049：`Div` 指令接受可选参数（CSS 类名），选项包括 `style` 和 `name`，有内容。
- F-050：`capture_directives(app)` 是上下文管理器，通过 monkey-patch `app.add_directive` 捕获所有注册的指令类到 `directive_map`。
- F-051：`AddFirstTitleCss` 是 SphinxTransform（priority=699），检查 docinfo 中是否有 `sd_hide_title` 字段，若有则给第一个 section 的 title 添加 `sd-d-none` CSS 类。
- F-052：扩展按顺序调用各模块的 setup 函数：setup_sd_config → setup_badges_and_buttons → setup_cards → setup_grids → setup_dropdown → setup_icons → setup_tabs → setup_article_info。
- F-053：扩展注册 `div` 指令（override=True）和 `AddFirstTitleCss` transform。
- F-054：`add_static_assets` 通过 `app.config.html_static_path.append(str(STATIC_DIR))` 注册静态目录。
- F-055：静态目录包含两个文件：`sphinx-design.min.css`（预编译压缩 CSS）和 `design-tabs.js`（Tab 同步 JS）。

## F-056 ~ F-075：卡片组件（cards.py）

- F-056：注册两个指令：`card`（CardDirective）和 `card-carousel`（CardCarouselDirective）。
- F-057：`CardDirective.option_spec` 包含：width（auto/25%/50%/75%/100%）、margin、text-align、img-top、img-bottom、img-background、img-alt、link、link-type（url/any/ref/doc）、link-alt、shadow（none/sm/md/lg）、class-card/class-header/class-body/class-title/class-footer/class-img-top/class-img-bottom。
- F-058：卡片标题为可选位置参数（`optional_arguments = 1`），`final_argument_whitespace = True`。
- F-059：卡片内容通过 `^^^`（3个或以上脱字符）分隔 header，通过 `+++`（3个或以上加号）分隔 footer。
- F-060：`REGEX_HEADER = re.compile(r"^\^{3,}\s*$")` 匹配 header 分隔线。
- F-061：`REGEX_FOOTER = re.compile(r"^\+{3,}\s*$")` 匹配 footer 分隔线。
- F-062：`CardContent` 是 NamedTuple，包含 body（必填）、header（可选）、footer（可选），每个为 (offset, StringList) 元组。
- F-063：卡片默认 CSS 类包括 `sd-card`、`sd-sphinx-override`、`sd-shadow-sm`、`sd-mb-3`。
- F-064：width 选项生成 `sd-w-{value}` 类（如 `sd-w-50`）。
- F-065：有 link 选项时添加 `sd-card-hover` 类，链接通过 `sd-stretched-link` + `sd-hide-link-text` 实现整卡可点击。
- F-066：img-background 创建带 `sd-card-img` 类的 image 节点和 `sd-card-img-overlay` 覆盖层，后续内容放入覆盖层。
- F-067：img-top 创建 `sd-card-img-top` 类的 image 节点，img-bottom 创建 `sd-card-img-bottom` 类的 image 节点。
- F-068：header 区域使用 `sd-card-header` 类，body 使用 `sd-card-body` 类，footer 使用 `sd-card-footer` 类，title 使用 `sd-card-title sd-font-weight-bold` 类。
- F-069：`add_card_child_classes(node)` 为直接子段落节点添加 `sd-card-text` 类（不处理嵌套在 admonition/list 等中的段落）。
- F-070：`get_link_target(target, link_type)` 根据 link-type 规范化链接目标：url 用 `directives.uri()` 移除空白；ref 折叠空白并小写化；doc/any 折叠空白保留大小写。
- F-071：link-type 为 url 时生成 `nodes.reference`，为 ref/doc/any 时生成 `addnodes.pending_xref`。
- F-072：`CardCarouselDirective` 需要 1 个必填参数（列数 1-12），生成 `sd-cards-carousel` + `sd-card-cols-{n}` 类的横向滚动容器。
- F-073：`CardDirective.create_card()` 是类方法，`GridItemCardDirective` 复用此方法创建卡片。
- F-074：title 使用 `PassthroughTextElement` 包裹内联文本节点，确保可翻译且不影响结构。
- F-075：卡片链接的 fallback 文本使用 `link-alt` 选项或原始 link 文本。

## F-076 ~ F-090：网格布局（grids.py）

- F-076：注册三个指令：`grid`（GridDirective）、`grid-item`（GridItemDirective）、`grid-item-card`（GridItemCardDirective）。
- F-077：`GridDirective` 接受 0 或 1 个可选参数（列数），有内容。
- F-078：`GridDirective.option_spec`：gutter、margin、padding、outline（flag）、reverse（flag）、class-container、class-row。
- F-079：网格容器使用 `sd-container-fluid` + `sd-sphinx-override` 类，行使用 `sd-row` 类。
- F-080：列数参数通过 `row_columns_option()` 验证，接受 1 个或 4 个（xs/sm/md/lg）值 1-12 或 "auto"，生成 `sd-row-cols-{n}` 和响应式 `sd-row-cols-{size}-{n}` 类。
- F-081：gutter 选项通过 `gutter_option()` 验证，接受 1 个或 4 个值 0-5，生成 `sd-g-{n}` 和响应式类。
- F-082：outline 选项添加 `sd-border-1` 类，reverse 添加 `sd-flex-row-reverse` 类。
- F-083：`GridItemDirective.option_spec`：columns、margin、padding、child-direction（column/row）、child-align（start/end/center/justify/spaced）、outline、class。
- F-084：grid-item 默认使用 `sd-col` + `sd-d-flex-column` 类，columns 选项通过 `item_columns_option()` 生成 `sd-col-{n}` 响应式类。
- F-085：child-direction 生成 `sd-d-flex-{value}` 类（`sd-d-flex-column` 或 `sd-d-flex-row`）。
- F-086：child-align 生成 `sd-align-major-{value}` 类。
- F-087：`GridItemCardDirective` 接受 0 或 1 个可选参数（卡片标题），option_spec 合并了 grid-item 的 columns/margin/padding/class-item 和 CardDirective 的所有卡片选项（除 margin）。
- F-088：`GridItemCardDirective` 默认 width 为 "100%"，margin 设为空列表（避免双重间距），内部调用 `CardDirective.create_card()` 创建卡片。
- F-089：grid-item 使用 `sd-col` + `sd-d-flex-row` 类（与普通 grid-item 默认 column 不同）。
- F-090：`_media_option()` 是列数/间距验证的通用函数，1 个值时自动复制到 4 个断点，生成带 `{prefix}{size}-{value}` 模式的 CSS 类列表。

## F-091 ~ F-105：下拉折叠（dropdown.py）

- F-091：注册 `dropdown` 指令（DropdownDirective）和 `DropdownHtmlTransform` post-transform。
- F-092：注册两个自定义节点：`dropdown_main`（继承 nodes.Element + nodes.General）和 `dropdown_title`（继承 nodes.TextElement + nodes.General）。
- F-093：`dropdown_main` 在 HTML 中渲染为 `<details>` 标签，支持 `open` 属性。
- F-094：`dropdown_title` 在 HTML 中渲染为 `<summary>` 标签。
- F-095：`DropdownDirective` 接受 0 或 1 个可选参数（标题文本），`final_argument_whitespace=True`，有内容。
- F-096：`DropdownDirective.option_spec`：open（flag，默认展开）、color（语义色）、icon（octicon 名称）、chevron（right-down/down-up）、animate（fade-in/fade-in-slide-down）、margin、name、class-container、class-title、class-body。
- F-097：DropdownHtmlTransform 默认 priority=199，仅在 HTML 格式执行。
- F-098：转换后的 HTML 结构为 `<details class="sd-sphinx-override sd-dropdown sd-card"><summary class="sd-summary-title sd-card-header">...<div class="sd-summary-content sd-card-body">...`。
- F-099：默认使用 card 样式（`sd-card` + `sd-card-header` + `sd-card-body`），TODO 标注未来可能添加非 card 选项。
- F-100：状态标记图标使用 octicon：chevron 为 "right-down" 时用 `chevron-right`，为 "down-up" 时用 `chevron-down`。
- F-101：无标题时使用 `kebab-horizontal` octicon 作为默认标题图标。
- F-102：animate 选项添加 `sd-fade-in` 或 `sd-fade-in-slide-down` CSS 类。
- F-103：color 选项为标题添加 `sd-bg-{color}` + `sd-bg-text-{color}` 类。
- F-104：icon 选项在标题前插入自定义 octicon SVG（`sd-summary-icon` 类），chevron 在标题后（`sd-summary-state-marker` 类）。
- F-105：直接子段落节点添加 `sd-card-text` 类（与卡片相同的处理方式）。

## F-106 ~ F-125：标签页（tabs.py）

- F-106：注册三个指令：`tab-set`（TabSetDirective）、`tab-item`（TabItemDirective）、`tab-set-code`（TabSetCodeDirective）。
- F-107：注册 `TabSetHtmlTransform` post-transform（priority=200，仅 HTML）。
- F-108：注册两个自定义节点：`sd_tab_input`（渲染为 `<input type="radio">`）和 `sd_tab_label`（渲染为 `<label>`）。
- F-109：`tab-set` 选项：sync-group（str）、class（class 列表），有内容，子元素应为 `tab-item`。
- F-110：`tab-item` 需要 1 个必填参数（标签文本），选项：selected（flag）、sync（str，同步 ID）、name、class-container/class-label/class-content，有内容。
- F-111：`tab-item` 生成结构：container(tab-item) > rubric(tab-label) + container(tab-content)，允许非 HTML 输出的默认渲染。
- F-112：`tab-set-code` 选项：no-sync（flag）、sync-group、class-set/class-item/class-label/class-content，子元素应为 `literal_block`（代码块）。
- F-113：`tab-set-code` 自动将代码块的语言名（大写）作为标签文本，默认 sync-group 为 "code"，sync_id 为语言名。
- F-114：`TabSetHtmlTransform` 将抽象 AST 转换为 HTML 专用结构：radio input + label + content 的顺序。
- F-115：每个 tab-set 分配唯一 ID `sd-tab-set-{n}`，每个 tab-item 分配 `sd-tab-item-{n}`。
- F-116：第一个 tab-item 默认选中，或第一个有 `selected` 选项的 tab-item；多个 selected 发出警告。
- F-117：radio input 使用 `name={set_id}` 实现互斥选择，`checked` 属性控制选中状态。
- F-118：label 的 `for` 属性指向对应 input 的 ID，`aria-controls` 指向 content panel 的 ID。
- F-119：同步数据通过 `data-sync-id` 和 `data-sync-group` 属性传递给 JavaScript。
- F-120：超链接目标（nodes.target）被保留在重建的 tab-set 前部，确保锚点引用仍然有效。
- F-121：tab-item 的 ids（包括来自前置 hyperlink target 的锚点）传播到 label 节点上。
- F-122：content panel 的 ID 为 `{tab_item_id}-content`，通过 `ids.insert(0, ...)` 前置确保现有锚点不失效。
- F-123：多个 selected tab-item 发出 WARNING_TYPE ".tab" 警告；非 tab-item 子元素被跳过但保留 target 节点。
- F-124：tab-set 验证子元素，非 tab-item 且非 ignorable 的子元素发出警告并跳过（不中断构建）。
- F-125：tab-item 若不在 tab-set 内也发出警告但继续处理。

## F-126 ~ F-150：徽章与按钮（badges_buttons.py）

- F-126：角色名前缀常量：`ROLE_NAME_BADGE_PREFIX = "bdg"`，`ROLE_NAME_LINK_PREFIX = "bdg-link"`，`ROLE_NAME_REF_PREFIX = "bdg-ref"`。
- F-127：指令名常量：`DIRECTIVE_NAME_BUTTON_LINK = "button-link"`，`DIRECTIVE_NAME_BUTTON_REF = "button-ref"`。
- F-128：为每种语义色注册 6 个徽章角色：`bdg-{color}`、`bdg-{color}-line`（轮廓）、`bdg-link-{color}`、`bdg-link-{color}-line`、`bdg-ref-{color}`、`bdg-ref-{color}-line`。
- F-129：另外注册 3 个无色角色：`bdg`、`bdg-link`、`bdg-ref`。
- F-130：徽章自定义节点 `sd_badge` 继承 `nodes.inline + nodes.General`，HTML 渲染为 `<span>`，非 HTML 格式（latex/text/man/texinfo）使用 passthrough（不输出包装器）。
- F-131：徽章 CSS 类由 `create_bdg_classes(color, outline)` 生成：基础类 `sd-sphinx-override sd-badge`，填充色 `sd-bg-{color} sd-bg-text-{color}`，轮廓色 `sd-outline-{color} sd-text-{color}`。
- F-132：徽章支持 tooltip（提示文本），通过 `; tooltip` 语法，分号可用 `\;` 转义。
- F-133：`split_tooltip(text)` 解析最后一个未转义分号后的文本为 tooltip，空 tooltip 视为无 tooltip。
- F-134：`BadgeRole` 生成纯文本徽章（无链接），tooltip 设置到节点的 `tooltip` 属性。
- F-135：`LinkBadgeRole` 继承 `ReferenceRole`，生成外部链接徽章（`nodes.reference`），tooltip 设置为 `reftitle`。
- F-136：`XRefBadgeRole` 继承 `ReferenceRole`，生成内部交叉引用徽章（`addnodes.pending_xref`）。
- F-137：链接/引用徽章的 tooltip 仅在显式 `title <target>` 形式后接受分号，因为 URL 和引用目标中 `;` 是合法字符。
- F-138：`_TooltipRoleMixin` 是处理 tooltip 解析的混入类，兼容 rST（NUL 编码转义）和 MyST（原始反斜杠）两种解析器。
- F-139：`_ButtonDirective` 是按钮基类，需要 1 个必填参数（链接目标），有内容。
- F-140：按钮 option_spec：color（语义色）、outline（flag）、align（left/right/center）、expand（flag，全宽）、click-parent（flag，父元素可点击）、tooltip、shadow（flag）、ref-type（any/ref/doc/myst）、class。
- F-141：按钮基础 CSS 类：`sd-sphinx-override sd-btn sd-text-wrap`；填充色 `sd-btn-{color}`，轮廓色 `sd-btn-outline-{color}`。
- F-142：click-parent 添加 `sd-stretched-link` 类，shadow 添加 `sd-shadow-sm`，expand 添加 `sd-d-grid` 包装器。
- F-143：按钮内容通过 `nodes.inline(translatable=True)` 标记为可翻译，Sphinx 翻译后自动展开。
- F-144：`ButtonLinkDirective` 用 `directives.uri()` 处理外部 URL（移除空白），生成 `nodes.reference`。
- F-145：`ButtonRefDirective` 用 `ws_re.sub(" ", argument).strip()` 折叠空白（保留多词标签），ref-type 为 "ref" 时小写化目标，生成 `addnodes.pending_xref`。
- F-146：`ButtonRefContentStash`（priority=8）在交叉引用解析前暂存 button-ref 的富文本内容，避免 std-domain resolver 将内联标记扁平化为纯文本。
- F-147：`ButtonRefContentGraft`（priority=11）在解析后恢复暂存的富文本内容到已解析的 reference 节点。
- F-148：暂存/恢复通过 marker class 机制实现：给 pending_xref 添加唯一标记类 `sd-button-ref-content-{n}`，内容存储在 `document.sd_button_ref_content` 瞬态属性上。
- F-149：`BadgeRefTooltipStash`（priority=5）和 `BadgeRefTooltipGraft`（priority=12）用相同 marker class 机制传递 bdg-ref 的 tooltip 到解析后的 reference 节点的 `reftitle` 属性。
- F-150：按钮放在 `nodes.paragraph` 容器中（因为 reference 节点需要 TextElement 父元素），段落使用 align 选项的 CSS 类。

## F-151 ~ F-170：图标系统（icons.py）

- F-151：支持三类图标：GitHub Octicon（SVG 内联）、FontAwesome（CSS class）、Material Design Icons（SVG 内联）。
- F-152：Octicon 角色名为 `octicon`；FontAwesome 角色名包括 `fa/fas/fab/far`（v4/v5 兼容）和 `fa-solid/fa-brands/fa-regular`（v6 规范）；Material 角色名为 `material-regular/outlined/round/sharp/twotone`。
- F-153：注册 `_all-octicon` 指令用于自身文档生成，输出所有 octicon 的表格。
- F-154：Octicon 数据从 `compiled/octicons.json` 加载（`@lru_cache(1)` 缓存），Material 数据从 `compiled/material_{style}.json` 加载。
- F-155：`sd_icon` 自定义节点继承 `nodes.inline + nodes.General`，刻意无 Text 子节点，使 `astext()` 返回空字符串，避免 SVG 标记污染目录标签、搜索索引、HTML 页面标题等纯文本上下文。
- F-156：Octicon 语法：`:octicon:`name;height;classes``，height 默认 1em，接受 px/em/rem 单位。
- F-157：`get_octicon(name, height, classes, aria_label)` 根据 height 自动选择 16px 或 24px 原始尺寸，等比缩放宽度，生成 `<svg>` 标记。
- F-158：`HEIGHT_REGEX = re.compile(r"^(?P<value>\d+(\.\d+)?)(?P<unit>px|em|rem)$")` 验证高度格式。
- F-159：无 aria_label 时设置 `aria-hidden="true"`，有 aria_label 时设置 `aria-label` 和 `role="img"`。
- F-160：Octicon CSS 类：`sd-octicon sd-octicon-{name} {user_classes}`。
- F-161：FontAwesome 角色语法：`:fas:`name;classes``，类名由 `sd_fontawesome_version` 配置决定。
- F-162：FA_VERSION_CLASSES 映射：solid → {"4":"fa","5":"fas","6":"fa-solid"}，brands → {"4":"fa","5":"fab","6":"fa-brands"}，regular → {"4":"fa","5":"far","6":"fa-regular"}。
- F-163：`FA_ROLE_STYLES` 映射角色名到语义样式：fa/fas/fa-solid→solid，fab/fa-brands→brands，far/fa-regular→regular。
- F-164：FontAwesome CSS 加载由 `sd_fontawesome_source` 控制：`none`（用户/主题自行提供）或 `cdn`（自动添加 CDN CSS）。
- F-165：FontAwesome LaTeX 支持：`sd_fontawesome_latex="fontawesome5"` 使用 `\faIcon[style]{name}` 命令，`"fontawesome"` 使用 `\faicon{name}`，False/`"none"` 不渲染并发出一次性警告。
- F-166：`add_fontawesome_pkg` 在 `config-inited` 事件添加 LaTeX 包。
- F-167：`add_fontawesome_css` 在 `builder-inited` 事件（仅 HTML）添加 CDN CSS 文件。
- F-168：`fontawesome` 节点在 HTML 中渲染为 `<span class="{classes}">`，LaTeX 中渲染为 `\faIcon` 命令，man/text/texinfo 中发出警告并 SkipNode。
- F-169：Material icon 语法与 Octicon 相同：`:material-regular:`name;height;classes``，CSS 类为 `sd-material-icon sd-material-icon-{name}`，version 标记为 "4.0.0.63c5cb3"。
- F-170：Octicon 默认原始高度 16px，≥1.5em 或 ≥24px 时使用 24px 版本；Material icon 默认原始高度 20px，≥1.5em 或 ≥24px 时使用 24px 版本。

## F-171 ~ F-180：文章信息（article_info.py）

- F-171：注册 `article-info` 指令（ArticleInfoDirective），无内容。
- F-172：`article-info` option_spec：avatar（URI）、avatar-alt、avatar-link（URI）、avatar-outline（语义色）、author（必填 str）、date（必填 str）、read-time（必填 str）、class-container、class-avatar。
- F-173：article-info 生成网格布局：外层 `sd-container-fluid` + 内层 `sd-row sd-row-cols-2 sd-gx-2 sd-gy-1`。
- F-174：头像区域为 `sd-col sd-col-auto sd-d-flex-row sd-align-minor-center`，头像图片使用 `sd-avatar-sm` 类，可选轮廓色 `sd-outline-{color}`。
- F-175：author 字段可选解析内联标记（parse_fields=True），date 和 read-time 字段带 octicon 图标（calendar 和 clock，16px 高度）。
- F-176：信息网格使用响应式列：`sd-row-cols-2 sd-row-cols-xs-2 sd-row-cols-sm-3 sd-row-cols-md-3 sd-row-cols-lg-3`。
- F-177：有 avatar-link 时头像包裹在 `nodes.reference` 中。
- F-178：文本字段通过 `_parse_text()` 方法处理，`parse=True` 时使用 `self.state.inline_text()` 解析内联标记并包裹在 `nodes.paragraph` 中（类 `sd-p-0 sd-m-0`）。
- F-179：每个信息项（author/date/read-time）放在 `sd-col sd-col-auto sd-d-flex-row sd-align-minor-center` 的 grid-item 中。
- F-180：date 图标使用 `sd-pr-2` 类（右侧 padding），read-time 图标同理。

## F-181 ~ F-195：Tab 同步 JavaScript（design-tabs.js）

- F-181：JS 文件 `design-tabs.js` 通过 `DOMContentLoaded` 事件初始化，使用 `@ts-check` 类型检查注释。
- F-182：Tab 选择状态存储在 `window.localStorage`，key 前缀由 script 标签的 `data-sd-tabs-storage-prefix` 属性配置。
- F-183：`storageKeyPrefix` 在脚本执行时通过 `document.currentScript` 捕获，空字符串完全禁用持久化。
- F-184：`create_key(el)` 从 label 元素的 `data-sync-id` 和 `data-sync-group` 属性创建 `[group, id, group--id]` 三元组。
- F-185：`get_label_input(label)` 通过 label 的 `for` 属性或 `previousElementSibling` 获取关联的 radio input。
- F-186：Tab 同步通过 radio input 的 `change` 事件（而非 label click）触发，确保鼠标/键盘/JS 激活都只触发一次。
- F-187：同步时直接设置其他同 key label 关联 input 的 `checked = true`（不触发 click 或 change 事件），保持幂等性。
- F-188：支持 URL 查询参数选择 Tab：`?group=syncId` 格式，在初始化时检查并存储。
- F-189：支持 URL hash 定位 Tab 内容：`select_tab_from_hash()` 处理 hash 指向 tab-label 或 tab-content 内部元素的情况。
- F-190：嵌套 Tab-set 支持：hash 定位时逐级打开所有父级 `.sd-tab-content` 面板。
- F-191：localStorage 访问被 try/catch 包裹，SecurityError 等异常时静默降级（不持久化但 Tab 同步仍工作）。
- F-192：DOM 顺序为 input → label → content（由 TabSetHtmlTransform 保证），JS 依赖此顺序关系。
- F-193：打开目标 Tab 后调用 `target.scrollIntoView()` 重新滚动到目标位置（因为面板可见性改变了页面布局）。
- F-194：全局映射 `sd_id_to_elements` 按 `group--id` key 存储所有关联的 label 元素数组。
- F-195：脚本同时监听 `hashchange` 事件以响应浏览器前进/后退导航。
