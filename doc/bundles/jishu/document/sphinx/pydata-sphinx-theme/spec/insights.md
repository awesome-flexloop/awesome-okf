---
type: spec
title: "pydata-sphinx-theme 架构洞察"
---

# pydata-sphinx-theme 架构洞察

> I 阶段产出：基于事实清单提炼的核心洞察四元组。每条洞察都指回 `spec/facts.md` 的事实编号。

## 洞察 I-001：主题即应用——事件管线才是主题的真正骨架

- **陈述**：pydata-sphinx-theme 不是一个"HTML + CSS 皮肤"，而是一个在 Sphinx 构建生命周期中运行的应用：`setup()` 连接 11 个回调，横跨 `builder-inited`、`html-page-context`、`build-finished` 三个阶段，负责配置迁移、导航计算、模板过滤、静态资源改写、Pygments 双主题生成与 logo 复制。
- **证据**：F-009~F-014（setup 接线）、F-015~F-024（配置更新）、F-039~F-044（模板与资产注入）、F-060~F-064（logo/Pygments）。
- **反常识**：多数人以为换主题只是换一套模板；实际上这个主题一半以上的 Python 代码在"改构建结果"——删除重复 CSS、重写 `pygments.css`、修正 canonical URL、过滤空模板。主题的能力边界由 Sphinx 事件决定，而不是由 CSS 决定。
- **行动**：排查主题问题时先判断问题发生在哪个事件阶段；自定义主题时优先复用 `html-page-context` 注入上下文，而不是复制模板或写大量 CSS 覆盖。

## 洞察 I-002：渐进披露不是样式，而是服务端计算出来的导航数据结构

- **陈述**：侧栏的层级、展开状态、当前页高亮和 `aria-current` 并非由前端 JS 在浏览器里推断，而是 `toctree.py` 在构建期把 Sphinx 的 toctree 解析成带 `current/active` 类的 HTML，并插入 `<details>/<summary>` 折叠控件；前端只负责滚动与开关。
- **证据**：F-045~F-054（LinkInfo、祖先定位、`<details>` 注入、缓存与标记迁移）、F-075（仅页内 TOC 高亮由 IntersectionObserver 负责）。
- **反常识**：为了性能，主题会对"同一祖先、同一输出目录、同一展开层级"的侧栏做缓存，然后在命中时"搬运"当前页标记。也就是说，侧栏 HTML 是可共享的，页面差异只是几个类名和 `open` 属性。
- **行动**：遇到"侧栏高亮错页/展开错层"时，先检查 `show_nav_level`、`collapse_navigation` 与 builder 类型（`dirhtml` 不缓存），而不是去改 JS。

## 洞察 I-003：双主题不是两套站点，而是同一份 HTML 上的运行时可切换状态

- **陈述**：light/dark 由 `<html data-theme="...">` 驱动：CSS 变量按 `html[data-theme="light"]` 与 `html[data-theme="dark"]` 分别定义，Pygments 在构建结束时把两套高亮规则写进同一个 `pygments.css`，JS 只切换 `data-theme` 并记住用户选择。
- **证据**：F-033~F-035（首屏内联脚本防闪烁）、F-063~F-067（双前缀 CSS、颜色/字体变量）、F-069（主题切换与持久化）、F-078~F-080（HTML 转换层）。
- **反常识**：主题没有为暗色模式生成第二份页面，也没有依赖 `prefers-color-scheme` 媒体查询来决定高亮色；它用 `light-dark()` 与 `data-theme` 选择器把"模式"降维成一个 DOM 属性，因此可以做到用户手动覆盖系统偏好且即时生效。
- **行动**：自定义配色时使用 `html[data-theme] { --pst-color-primary: light-dark(...) }`；需要模式专属图片时用 `only-light` / `only-dark` / `dark-light` 类，而不是写两页内容。

## 洞察 I-004：导航与页内目录是两套不同的算法，各自为性能优化

- **陈述**：顶部导航只遍历 `root_doc` 的 toctree 条目并自行拼 HTML（不解析完整 TocTree），侧栏则从"当前顶层祖先"解析子树并用 BeautifulSoup 改写成 Bootstrap 结构；页内 TOC 又是第三种处理，直接改写 Sphinx 生成的 `context["toc"]`。
- **证据**：F-046~F-048（顶部导航的轻量遍历 vs 侧栏的祖先子树）、F-049~F-053（三套 HTML 改写路径）、F-054（对齐类计算）。
- **反常识**：同一个页面上的三个目录（顶部、左侧、右侧）来自三条完全不同的代码路径，因此它们的配置项、缓存策略和 bug 面也互不相同；"导航不显示"不等于"toctree 写错了"。
- **行动**：按区域定位问题：顶部看 `root_doc` + `header_links_before_dropdown`，左侧看 `show_nav_level` / `navigation_depth` / `html_sidebars`，右侧看 `secondary_sidebar_items` / `show_toc_level`。

## 洞察 I-005：可插拔性来自"模板即组件 + 空渲染即移除"

- **陈述**：页面的每个区域都配置为模板名列表；`_update_and_remove_templates` 会为无后缀名称补 `.html`，逐个渲染，并把渲染结果为空白（或仅空白字符）的模板从列表中剔除。于是"组件是否存在"由组件自身的渲染结果决定，而不是由中心化的开关表决定。
- **证据**：F-039~F-040（区段列表、补后缀、空渲染剔除）、F-037（23 个组件）、F-027~F-029（默认组件组合）、F-055~F-057（次级侧栏的按页字典）。
- **反常识**：这意味着任何模板都可以被放进任何区域，只要它在当前上下文能渲染出内容；同时也意味着"模板找不到/变量缺失"会静默变成"该区域为空"，而不是显式报错。`templates_skip_empty_check` 是为此留下的性能与可观测性逃生口。
- **行动**：新增组件时先保证在目标区段能独立渲染；调试"组件消失"时直接渲染该模板并检查空白输出，而不是只查 `html_theme_options`。

## 洞察 I-006：可访问性是构建期语义 + 运行期交互的共同产物

- **陈述**：主题在构建期补齐 `aria-level`、`aria-current`、skip link、`<dialog>` 语义与可滚动容器的 `tabIndex`，在运行期维护焦点、Escape 关闭、抽屉焦点与 TOC 高亮；并用 Playwright + Axe-core 做自动化回归。
- **证据**：F-034（noscript）、F-049~F-052（`aria-current`）、F-070（快捷键）、F-075~F-077（焦点与 tabIndex）、F-078~F-079（翻译器补语义）、F-086~F-088（测试与局限）。
- **反常识**：主题明确声明自动化测试只能覆盖约 30–40% 的可访问性问题；因此"CI 绿"不等于"可访问"，人工键盘与读屏测试仍是必要环节。
- **行动**：自定义布局后至少手动验证键盘 Tab 顺序、Escape 关闭、焦点可见性与屏幕阅读器标签；不要把 Axe 通过当作验收终点。
