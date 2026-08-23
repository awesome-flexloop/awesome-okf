---
type: Reference
title: KaTeX 官网信源
description: KaTeX 官网 17 个公开页面登记，含稳定 ID、URL、标题、用途与引用提示
tags: [katex, website, reference]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T21:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T21:00:00+08:00 }
status: stable
stale_after: 2027-02-23
sources:
  - id: katex-website
    resource: https://katex.org
    title: KaTeX Official Website
---

## KaTeX 官网页面索引

本文档登记 KaTeX 官网（https://katex.org）17 个公开页面的稳定 ID、URL、标题、页面用途和引用提示，作为 Wiki 中所有官网事实溯源的信源目标。后续概念文档与示例的 `sources.resource` 可通过 `/references/katex-website.md#<id>` 引用本文件，或直接引用对应 URL。

> 采集日期：2026-08-23。官网版本标注存在不一致：Versions 页面标注当前稳定版为 0.16.47，而 Node/Browser/Font 等文档页 CDN 链接引用 0.18.4，Auto-render 页面引用 0.18.1。本 bundle 以源码 v0.18.4 为基准，详见 [事实清单修正-8](/spec/facts.md#修正-8官网版本号标注不一致)。

### 页面清单

| ID | URL | 标题 | 页面用途 | 引用提示 |
|----|-----|------|---------|---------|
| web-home | https://katex.org/ | Home | KaTeX 首页，展示产品定位（最快的 Web 数学排版库）、四大特点（Fast/Print quality/Self-contained/Server side rendering）、交互式演示和入口链接 | 用于 00-introduction 的产品定位与特点描述；首页演示中的宏定义示例可用于宏系统说明 |
| web-users | https://katex.org/users | Who is Using KaTeX? | 列出使用 KaTeX 的知名项目（Khan Academy、Dropbox Paper、GitLab、Gatsby、Slab 等），含项目图标和官网链接 | 用于 00-introduction 和 23-ecosystem-and-versions 的生态展示；条目随官网变化，引用时标注采集日期 |
| web-versions | https://katex.org/versions | Versions | 版本索引页，标注当前稳定版（0.16.47）和历史版本，提供 Documentation 与 Release Notes 链接 | 用于版本说明；注意该页版本标注滞后于文档页 CDN 版本号，以源码 package.json 为权威基准 |
| web-node | https://katex.org/docs/node | Node.js | Node.js 安装与使用指南：npm/yarn/pnpm/Deno 安装、从源码构建（Node 22.13+、corepack、pnpm）、CJS/ESM 导入、CSS/字体要求、mhchem 扩展用法 | 用于 01-getting-started、15-installation-and-runtime；Deno CDN 导入示例和构建环境要求以此页为准 |
| web-browser | https://katex.org/docs/browser | Browser | 浏览器安装与使用指南：CDN starter 模板（含 SRI）、全局变量/ESM/AMD 加载方式、字体加载策略（font-display: block/swap）、自托管方式、打包工具集成、字体目录要求 | 用于 01-getting-started、15-installation-and-runtime、17-fonts-and-units；CDN 版本为 0.18.4，字体目录必须与 CSS 同级 |
| web-api | https://katex.org/docs/api | API | 公共 API 文档：katex.render()、katex.renderToString()、String.raw 用法、throwOnError 行为、持久宏（Persistent Macros）机制与安全说明 | 用于 01-getting-started、09-macro-system；持久宏安全警告（不应跨多用户消息启用）必须保留 |
| web-cli | https://katex.org/docs/cli | CLI | CLI 参考：18 个选项（含 --version/--help），涵盖 display-mode、format、macro、macro-file、trust、strict、max-size、max-expand、input/output 等 | 用于 16-command-line 和 examples/cli-render；CLI 选项与 Options 页面的映射关系需对照说明 |
| web-autorender | https://katex.org/docs/autorender | Auto-render Extension | 自动渲染扩展文档：renderMathInElement() 用法、5 个专用选项（delimiters/ignoredTags/ignoredClasses/errorCallback/preProcess）、默认 delimiters（8 条，不含 $...$）、ESM 版本 | 用于 13-auto-render 和 examples/auto-render-usage；CDN 引用版本为 0.18.1；$...$ 需手动添加且必须排在 $$ 之后 |
| web-libs | https://katex.org/docs/libs | Extensions & Libraries | 官方扩展（4 个：auto-render/copy-tex/mathtex-script-type/mhchem）与第三方库索引（按平台分类：React/Vue/Angular/Android/iOS/Rust/Ruby 等） | 用于 14-contrib-extensions 和 23-ecosystem-and-versions；官方扩展指向 GitHub contrib/ 目录 |
| web-options | https://katex.org/docs/options | Options | 全部配置选项参考：displayMode/output/leqno/fleqn/throwOnError/errorColor/macros/minRuleThickness/colorIsTextColor/maxSize/maxExpand/strict/trust/globalGroup 的类型、默认值和用法 | 用于 10-settings-options、04-macro-expander；默认值权威来源：strict="warn"、trust=false、globalGroup=false、maxExpand=1000、throwOnError=true、errorColor="#cc0000"、maxSize=Infinity |
| web-security | https://katex.org/docs/security | Security | 安全指南：HTML 注入防护、maxSize/maxExpand/trust 三层防御、HTML 消毒建议（白名单需含 SVG 和 MathML）、错误消息风险、漏洞报告流程 | 用于 18-security-and-errors 和 examples/security-trust；安全建议不得弱化，消毒白名单说明必须保留 |
| web-error | https://katex.org/docs/error | Handling Errors | 错误处理指南：ParseError 异常类型、throwOnError=false 行为、错误消息中 LaTeX 源码的 HTML 转义要求、e instanceof katex.ParseError 判断方式 | 用于 18-security-and-errors 和 examples/error-handling；转义示例（& < >）必须保留 |
| web-font | https://katex.org/docs/font | Font | 字体与排版文档：字体属性配置（fonts.scss 变量）、1.21em 默认缩放、TeX 单位换算（cm/in 相对 10pt 缩放）、三种字体格式（ttf/woff/woff2）、Browserslist 构建、Sass 变量覆盖、字体目录配置 | 用于 12-font-metrics 和 17-fonts-and-units；Sass @use 变量覆盖语法以此页为准 |
| web-supported | https://katex.org/docs/supported | Supported Functions | 按类型分组的 TeX 函数支持列表，14 个 H2 分类：Accents/Delimiters/Environments/HTML/Letters and Unicode/Layout/Logic and Set Theory/Macros/Operators/Relations/Special Notation/Style/Color/Size/Font/Symbols and Punctuation/Units | 用于 19-supported-functions；HTML 扩展需 trust 和 strict 放宽的说明必须保留 |
| web-support-table | https://katex.org/docs/support_table | Support Table | 按字母排序的 TeX 函数支持表，三列：Symbol/Function、Rendered、Source or Comment；含 Detexify 链接 | 用于 20-support-table；与 Supported Functions 页互补（一个按类型、一个按字母） |
| web-issues | https://katex.org/docs/issues | Common Issues | 常见问题：DOCTYPE/quirks mode、智能引号、aligned/matrix 间距、align vs aligned、MathJax 差异（color/class/cssId/style）、CSS 版本检测、CSS 自定义示例 | 用于 21-common-issues；DOCTYPE 要求在 iframe 中同样适用 |
| web-migration | https://katex.org/docs/migration | Migration Guide | 版本迁移指南，覆盖 v0.13.0 至 v0.18.0 共 6 个版本段：CSS 类名前缀、__defineFunction 变更、contrib 路径、\relax 行为、宏参数行为等 | 用于 22-migration；v0.18.0 的 20 个 CSS 类名重命名必须完整记录 |

### 按文档映射

以下表格说明各官网页面对应的概念文档，便于交叉引用：

| 概念文档 | 引用的官网页面 ID |
|---------|-----------------|
| 00-introduction | web-home、web-users、web-versions |
| 01-getting-started | web-api、web-browser、web-node |
| 10-settings-options | web-options |
| 12-font-metrics | web-font |
| 13-auto-render | web-autorender |
| 14-contrib-extensions | web-libs |
| 15-installation-and-runtime | web-node、web-browser |
| 16-command-line | web-cli |
| 17-fonts-and-units | web-font、web-browser |
| 18-security-and-errors | web-security、web-error |
| 19-supported-functions | web-supported |
| 20-support-table | web-support-table |
| 21-common-issues | web-issues |
| 22-migration | web-migration |
| 23-ecosystem-and-versions | web-users、web-versions、web-libs |

### 引用规范

1. **稳定 ID 优先**：文档 `sources` 中引用官网页面时，优先使用本文件定义的稳定 ID（如 `/references/katex-website.md#web-options`），而非直接硬编码 URL。
2. **URL 直引**：需要直接可点击链接时，可在正文使用 Markdown 链接指向官网 URL，但 `sources.resource` 仍应指向本文件对应锚点。
3. **版本标注**：引用 CDN 链接或版本号时，必须注明该 bundle 基于 v0.18.4，官网 Versions 页面标注差异参见 [facts.md 修正-8](/spec/facts.md#修正-8官网版本号标注不一致)。
4. **默认值溯源**：配置选项默认值以 web-options 页面为权威来源；源码中未显式标注默认值的选项（strict/trust/globalGroup）不得仅凭源码推断。
