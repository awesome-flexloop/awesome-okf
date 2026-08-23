# Bundle Update Log

## 2026-08-23

* **Update（R 阶段）**：系统采集 KaTeX 官网 17 个公开页面（首页、Users、Versions、Node、Browser、API、CLI、Auto-render、Extensions & Libraries、Options、Security、Handling Errors、Font、Supported Functions、Support Table、Common Issues、Migration），在 `spec/facts.md` 追加官网事实 W-001~W-152，每页至少 3 条可溯源事实，均标注来源 URL。
* **Fix（事实复核）**：在 `spec/facts.md` 新增"事实复核/修正"小节（修正-1~修正-12），以官网为准复核并记录 `strict` 默认值（`"warn"` 非 `false`）、`trust` 默认 `false`、`globalGroup` 默认 `false`、Auto-render 默认 delimiters（8 条不含 `$...$`）与 ignoredTags 默认值、CLI 18 个选项、官网版本标注不一致（Versions 页 0.16.47 vs CDN 0.18.4）等偏差，不静默覆盖源码事实。
* **Update（I 阶段）**：更新 `spec/insights.md`，在原有 5 个源码架构洞察基础上补充洞察 6-9（三层安全防御纵深、持久宏有状态设计、版本标注不一致、官网与源码双信源分层），输出覆盖 24 篇概念、8 篇示例、2 篇 references 和官网 17 页映射的完整知识地图与四条学习路径。
* **Add（references）**：新增 `references/katex-website.md`，登记官网 17 个页面的稳定 ID、URL、标题、用途与引用提示；更新 `references/katex-source.md` 补充 v0.18.4 源码路径与官网关联说明。
* **Add（concepts 15-23）**：新增 9 篇官网导向概念文档——15-installation-and-runtime（浏览器/Node/Deno、ESM/CJS、CSS 字体路径、Browserslist 构建）、16-command-line（CLI 18 选项与 Options 映射）、17-fonts-and-units（字体加载策略、katex-swap.css、单位换算、1.21em 缩放）、18-security-and-errors（trust/maxSize/maxExpand 三层防御、HTML 消毒、ParseError、错误消息转义）、19-supported-functions（官网 14 个 H2 分类）、20-support-table（字母序支持表、Detexify）、21-common-issues（DOCTYPE、智能引号、align vs aligned、MathJax 差异、CSS 排障）、22-migration（v0.13-v0.18 迁移要点）、23-ecosystem-and-versions（Users、Versions、第三方库索引）。
* **Update（concepts 00-14）**：更新 00-introduction（融合首页卖点、Users/Versions）、01-getting-started（Browser/Node/API、CDN、String.raw、持久宏）、10-settings-options（以官网为准修正默认值、补充 trust context/macro 函数/globalGroup）、11-style-system（补充 Font 页用户视角）、12-font-metrics（融合 Font 页字体格式/Browserslist/Sass）、13-auto-render（修正 delimiters/ignoredTags 默认值、宏持久化）、14-contrib-extensions（聚焦官方 5 扩展，第三方库移至 23）；保留 02-09 源码架构深度内容不变。
* **Add（examples）**：新增 3 篇示例——node-ssr（Node/Deno renderToString、CSS 引入、HTML 组装、缓存）、security-trust（不可信输入、trust 函数、消毒白名单、持久宏隔离）、cli-render（npx katex、stdin/stdout、--input/--output/--display-mode/--macro/--macro-file/--no-throw-on-error）。
* **Update（examples）**：更新 basic-render、custom-macros（共享 macros 对象、\gdef 持久化、宏安全边界）、custom-extension（对照官网/源码检查 builder 与 MathML 要求）、auto-render-usage（默认 delimiters、$$ 先于 $、preProcess、动态内容）、error-handling（throwOnError/errorColor、strict、ParseError、trust）使其与官网 API/Error/Security 表述一致。
* **Add（索引与日志）**：新增 `concepts/index.md`、`examples/index.md`、`references/index.md`（子目录索引无 frontmatter）；更新根 `index.md`（补齐 24 篇概念与 8 篇示例导航、四条学习路径、9 条核心洞察、声明 `okf_version: "0.2"`）；新增本 `log.md`。

## 2026-08-22

* **Creation**：建立 KaTeX v0.18.4 源码级知识包脚手架（concepts/examples/references/spec 四目录），遵循 OKF v0.2 规范。
* **Add（R 阶段）**：深度阅读 KaTeX v0.18.4 源码核心模块（Lexer、Token、MacroExpander、Parser、Settings、Options、Style、buildTree、buildHTML、buildMathML、domTree、defineFunction、defineEnvironment、macros、metrics、contrib/auto-render 等），提取 76 条源码事实（F-001~F-076），覆盖项目信息、目录结构、公共 API、核心模块、渲染管线、字体度量、扩展模块、样式 CSS、宏系统。
* **Add（I 阶段）**：提炼 5 个源码架构洞察（TeX 消化管隐喻、注册表驱动架构、不可变 Options 传递、HTML+MathML 双输出、虚拟 DOM 双输出），设计知识地图。
* **Add（E 阶段）**：生成 15 篇源码概念文档（00-introduction 至 14-contrib-extensions）、5 篇示例（basic-render、custom-macros、custom-extension、auto-render-usage、error-handling）、1 篇源码信源登记（references/katex-source.md）及根 index.md。
