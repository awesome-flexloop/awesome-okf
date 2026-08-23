---
type: Fact
title: KaTeX 事实清单
description: KaTeX 源码事实（F-001~F-076）与官网事实（W-001~W-152）的编号清单，含双信源交叉验证与修正记录
tags: [katex, facts, source-code, website, verification]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T20:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T20:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web
    resource: /references/katex-website.md
    title: KaTeX 官网信源
---

# KaTeX 源码事实清单

> R阶段产出：编号事实清单 F-001~F-050，零推测纯客观描述

## 项目基本信息

- F-001: KaTeX 版本为 0.18.4（package.json 第3行）
- F-002: package.json 中 `name` 字段为 `"katex"`，`description` 为 `"Fast math typesetting for the web."`
- F-003: 许可证为 MIT（package.json 第57行）
- F-004: 包管理器为 pnpm@11.4.0（package.json 第58行）
- F-005: 唯一运行时依赖为 `commander: ^8.3.0`（package.json 第167-169行）
- F-006: 入口文件为 `dist/katex.js`（CJS）和 `dist/katex.mjs`（ESM），类型定义为 `types/katex.d.ts`
- F-007: CLI 入口为 `cli.js`（package.json 第138行 bin 字段）
- F-008: 源码使用 TypeScript 编写，构建工具链包含 rollup@^2.79.2 + webpack@^5.74.0 + babel
- F-009: 测试框架为 jest@^30.2.0，测试匹配模式为 `**/test/*-spec.ts`
- F-010: 官网为 https://katex.org，仓库为 https://github.com/KaTeX/KaTeX.git

## 目录结构

- F-011: 源码主目录为 `src/`，包含约 50+ 个 .ts 文件
- F-012: `src/functions/` 目录包含 43 个 .ts 文件（含 utils/ 子目录）
- F-013: `src/environments/` 目录包含 2 个文件：array.ts 和 cd.ts
- F-014: `contrib/` 目录包含 5 个扩展：auto-render、copy-tex、mathtex-script-type、mhchem、render-a11y-string
- F-015: `docs/` 目录包含 14 个 .md 文件：api.md、autorender.md、browser.md、cli.md.template、error.md、font.md、issues.md、libs.md、migration.md、node.md、options.md、security.md、support_table.md、supported.md
- F-016: `fonts/` 目录包含约 50+ 个字体文件（.ttf/.woff/.woff2），涵盖 KaTeX_AMS、KaTeX_Caligraphic、KaTeX_Fraktur、KaTeX_Main、KaTeX_Math、KaTeX_SansSerif、KaTeX_Script、KaTeX_Size1-4、KaTeX_Typewriter 系列
- F-017: `test/` 目录包含测试文件，使用 jest + jsdom 环境
- F-018: `src/metrics/` 目录包含脚本文件：extract_tfms.py、extract_ttfs.py、format_json.py、parse_tfm.py、mapping.pl

## 公共 API（katex.ts）

- F-019: 默认导出对象包含属性：version、render、renderToString、ParseError、SETTINGS_SCHEMA、__parse、__renderToDomTree、__renderToHTMLTree、__setFontMetrics、__defineSymbol、__defineFunction、__defineMacro、__domTree
- F-020: `render(expression: string, baseNode: Node, options?: SettingsOptions): void` 将 LaTeX 渲染到指定 DOM 节点
- F-021: `renderToString(expression: string, options?: SettingsOptions): string` 将 LaTeX 渲染为 HTML 标记字符串
- F-022: `__parse(expression: string, options?: SettingsOptions): AnyParseNode[]` 返回解析树（标注为不推荐公开使用）
- F-023: `__renderToDomTree(expression: string, options: SettingsOptions): DomSpan` 返回内部 DOM 树（HTML+MathML）
- F-024: `__renderToHTMLTree(expression: string, options: SettingsOptions): DomSpan` 返回内部 DOM 树（仅HTML，无MathML）
- F-025: `__defineSymbol`、`__defineFunction`、`__defineMacro` 为默认导出对象上的扩展 API 方法
- F-026: `__setFontMetrics` 为默认导出对象上的方法
- F-027: `__domTree` 暴露 DOM 树节点类型：Span、Anchor、SymbolNode、SvgNode、PathNode、LineNode

## 核心模块

- F-028: Lexer 类位于 src/Lexer.ts，实现词法分析，核心方法为 `lex(): Token`
- F-029: Lexer 使用正则表达式 tokenRegex 进行分词，支持：空白字符、控制词（\[a-zA-Z@]+）、控制符号（\[^\uD800-\uDFFF]）、Unicode 代理对、组合变音符号、\verb/\verb* 命令
- F-030: Lexer 维护 catcodes（分类码）映射，默认 `%` 为14（注释符），`~` 为13（活动字符）
- F-031: Token 类位于 src/Token.ts，包含属性：text（string）、loc（SourceLocation|null）、noexpand（boolean|null）、treatAsRelax（boolean|null）
- F-032: MacroExpander 类位于 src/MacroExpander.ts，类名为 "gullet"（遵循 TeX 术语：mouth→gullet→stomach）
- F-033: MacroExpander 核心方法：expandNextToken()（递归展开直到非可展开token）、expandOnce()（单次展开）、consumeArg()（消费参数）、beginGroup()/endGroup()（分组嵌套）
- F-034: MacroExpander 内部维护 stack: Token[]（逆序存储）和 macros: Namespace<MacroDefinition>
- F-035: MacroExpander 默认展开上限 maxExpand 为 1000（Settings 中定义）
- F-036: Parser 类位于 src/Parser.ts，起始模式为 "math"，核心方法为 `parse(): AnyParseNode[]`
- F-037: Parser 维护属性：mode（"math"|"text"）、gullet（MacroExpander实例）、settings、leftrightDepth、nextToken
- F-038: Parser.parseExpression() 循环解析 atom 直到遇到终止符（}、\endgroup、\end、\right、& 或 breakOnTokenText）
- F-039: Parser.parseAtom() 先调用 parseGroup() 解析基础组，然后处理上下标（^、_、'、Unicode上下标）、limit控制（\limits、\nolimits）
- F-040: Parser.parseGroup() 处理花括号组 {…}、\begingroup…\endgroup 组、函数调用和符号
- F-041: Parser.parseFunction() 查询 functions 注册表，验证模式允许性后调用 parseArguments() 和 callFunction()
- F-042: Parser 支持的参数类型（ArgType）：color、size、url、raw、original、hbox、primitive、math、text
- F-043: Parser 通过 handleInfixNodes() 将 \over 等中缀运算符重写为 \frac 等命令
- F-044: Settings 类位于 src/Settings.ts，通过 SETTINGS_SCHEMA 定义支持的选项
- F-045: Settings 选项包括：displayMode（boolean）、output（"htmlAndMathml"|"html"|"mathml"）、leqno、fleqn、throwOnError（默认true）、errorColor（默认#cc0000）、macros（object）、minRuleThickness、colorIsTextColor、strict、trust、maxSize（默认Infinity）、maxExpand（默认1000）、globalGroup
- F-046: defineFunction 位于 src/defineFunction.ts，维护三个全局注册表：_functions（FunctionSpec）、_htmlGroupBuilders（HtmlBuilder）、_mathmlGroupBuilders（MathMLBuilder）
- F-047: FunctionSpec 接口包含字段：type（NodeType）、numArgs、argTypes、allowedInArgument、allowedInText、allowedInMath、numOptionalArgs、infix、primitive、handler
- F-048: defineEnvironment 位于 src/defineEnvironment.ts，维护 _environments 注册表，EnvSpec 包含 type、numArgs、argTypes、allowedInText、numOptionalArgs、handler
- F-049: Options 类位于 src/Options.ts，渲染时携带：style（Style）、color、size（默认6=normalsize）、textSize、phantom、font、fontFamily、fontWeight、fontShape、sizeMultiplier、maxSize、minRuleThickness
- F-050: Style 类位于 src/Style.ts，8种样式通过 id 0-7 标识（display/text/script/scriptscript × cramped/非cramped），提供 sup()、sub()、fracNum()、fracDen()、cramp()、text() 方法进行样式转换

## 渲染管线

- F-051: buildTree() 位于 src/buildTree.ts，接收 parseTree、expression 字符串、Settings，返回 DomSpan
- F-052: buildTree() 根据 settings.output 选择渲染路径：mathml（仅MathML）、html（仅HTML）、htmlAndMathml（默认，二者都有）
- F-053: HTML+MathML 双输出时，MathML 节点放在 HTML 节点之前
- F-054: displayWrap() 在 displayMode 时用 span.katex-display 包裹，支持 leqno（左侧编号）和 fleqn（左对齐）CSS类
- F-055: buildHTML() 位于 src/buildHTML.ts，接收 AnyParseNode[] 和 Options，返回 DomSpan
- F-056: buildMathML() 位于 src/buildMathML.ts，生成 MathML 语义标注节点
- F-057: domTree.ts 定义虚拟 DOM 节点类：Span、Anchor、SymbolNode、SvgNode、PathNode、LineNode、DocumentFragment
- F-058: 虚拟 DOM 节点提供 toNode()（转为真实HTMLElement）和 toMarkup()（序列化为HTML字符串）方法
- F-059: makeSpan() 位于 src/buildCommon.ts，创建 span 节点的工具函数
- F-060: atoms.ts 定义原子类型组：6个 atom（bin、close、inner、open、punct、rel）和5个 non-atom（accent-token、mathord、op-token、spacing、textord）

## 字体与度量

- F-061: 字号映射 sizeStyleMap[11] 对应 \tiny 到 \HUGE 的11个字号，每个字号在 text/script/scriptscript 三种样式下映射到不同的实际大小索引
- F-062: 字号倍数 sizeMultipliers[11] = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.44, 1.728, 2.074, 2.488]
- F-063: Options.BASESIZE = 6 对应 \normalsize（10pt基准）
- F-064: fontMetrics.ts 提供 getGlobalMetrics(size) 获取全局字体度量

## 扩展模块

- F-065: contrib/auto-render 提供 renderMathInElement() 函数，自动扫描 DOM 中的数学分隔符（$...$、$$...$$、\(...\)、\[...\]）并渲染
- F-066: auto-render 使用 splitAtDelimiters.ts 将文本按分隔符分割为 text/math 片段
- F-067: auto-render 支持选项：delimiters、preProcess、ignoredTags、ignoredClasses、errorCallback、displayMode、macros
- F-068: contrib/copy-tex 提供 katex2tex 功能，将 KaTeX 渲染结果复制回 LaTeX 源码
- F-069: contrib/mhchem 为化学方程式扩展
- F-070: contrib/render-a11y-string 生成无障碍字符串表示

## 样式与CSS

- F-071: src/styles/ 包含3个 SCSS 文件：katex.scss（主样式）、fonts.scss（字体声明）、katex-swap.scss
- F-072: 核心 CSS 类名：.katex（根元素）、.katex-display（显示模式包裹）、.katex-error（错误状态）、.mtight（紧密间距）、.size1~.size11（字号）、.reset-sizeN（重置字号）

## 宏系统

- F-073: src/macros.ts 存储内置宏定义
- F-074: src/macros.ts 中的宏定义可通过 Namespace 进行分组作用域管理（beginGroup/endGroup 压栈/出栈）
- F-075: 宏展开支持 #1~#9 参数占位符，## 转义为 #
- F-076: _getExpansion() 支持两种宏定义形式：字符串（简单替换）和函数（动态展开）

---

# KaTeX 官网事实清单

> R阶段官网采集产出：编号 W-001~W-152，按官网 17 个页面组织，每条标注来源 URL；零推断纯客观描述。
> 采集日期：2026-08-23。

## 首页（Home）

来源：https://katex.org/

- W-001: 首页标题为 "KATEX"，副标题为 "The fastest math typesetting library for the web."
- W-002: 首页列出四个特点：Fast（同步渲染、无需重排页面）、Print quality（基于 Donald Knuth 的 TeX 排版）、Self-contained（无依赖、可与网站资源打包）、Server side rendering（在浏览器或环境中产生相同输出，可通过 Node.js 预渲染为纯 HTML）
- W-003: 首页提供三个入口链接：Installation（指向 /docs/browser）、Documentation（指向 /docs/api）、View on GitHub（指向 https://github.com/KaTeX/KaTeX）
- W-004: 首页包含一个交互式表达式输入框，默认展示宏定义示例 `% \f is defined as #1f(#2) using the macro` 及傅里叶变换公式
- W-005: 首页页脚标注 "Created by Emily Eisenberg and Sophie Alpert"

## Users（谁在使用 KaTeX）

来源：https://katex.org/users

- W-006: Users 页面标题为 "Who is Using KaTeX?"，列出多个使用 KaTeX 的项目
- W-007: 列表中包含的项目有 Khan Academy、Dropbox Paper、GitLab、Gatsby、Gitter、Gradescope、Messenger、Observable、Quill、Rocket.Chat、Slab、Slides、StackEdit、TiddlyWiki 等
- W-008: 列表中包含的中文/东亚相关项目有 BearBei 貝貝、Editor.md、namu.wiki、Techambition、zzllrr Mather
- W-009: 每个项目条目包含项目图标和指向项目官网的链接

## Versions（版本）

来源：https://katex.org/versions

- W-010: Versions 页面 "Current version (Stable)" 标注的最新版本为 0.16.47，提供 Documentation 和 Release Notes 链接（Release Notes 指向 https://github.com/KaTeX/KaTeX/releases/tag/v0.16.47）
- W-011: "Past Versions" 表格列出 0.16.46 的文档链接（指向 netlify.app 预览地址）和 Release Notes 链接
- W-012: 页面说明可在 GitHub（https://github.com/KaTeX/KaTeX/releases）找到历史版本
- W-013: （版本标注差异）Versions 页面标注当前稳定版为 0.16.47，而 Node/Browser/Auto-render 等页面的 CDN 链接引用 0.18.4（Auto-render 页面引用 0.18.1）；本 bundle 以源码 v0.18.4 为基准

## Node.js（Node 安装与使用）

来源：https://katex.org/docs/node

- W-014: Node 页面提供四种安装方式：npm（`npm install katex`）、Yarn（`yarn add katex`）、pnpm（`pnpm add katex`）、Deno 2（`deno install katex` 或 `deno install -g npm:katex`）
- W-015: Deno 可直接从 CDN 导入 ESM：`import katex from "https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.mjs"`
- W-016: 从源码构建需要 Git、Node.js 22.13 或更高版本、启用 corepack；构建步骤为 `corepack enable` → `pnpm install` → `pnpm build`
- W-017: 构建时根据 Browserslist config 自动转译代码并只包含目标环境所需字体；可通过 `BROWSERSLIST` 环境变量指定目标环境（如 `BROWSERSLIST="Chrome 68" pnpm build`）
- W-018: 可通过 `USE_(FONT NAME)` 环境变量设为 `"true"` 或 `"false"` 强制包含或排除某种字体格式
- W-019: KaTeX 作为 CommonJS 模块导出，可通过 `require('katex')` 导入；同时条件性导出 ECMAScript 模块，可通过 `import katex from 'katex'` 导入
- W-020: ES 模块包含 ES6 语法，在旧环境中可能需要转译
- W-021: 在 Node 中通过 `renderToString` 生成的 HTML 仍需链接 CSS 文件、提供字体文件并使用 HTML5 doctype；客户端不需要包含 katex.js
- W-022: mhchem 扩展通过修改 katex 模块添加功能，Node 中用法为 `require('katex'); require('katex/contrib/mhchem');`

## Browser（浏览器安装与使用）

来源：https://katex.org/docs/browser

- W-023: Browser 页面声明 KaTeX 支持所有主流浏览器，包括 Chrome、Safari、Firefox、Opera、Edge
- W-024: Starter 模板要求使用 `<!DOCTYPE html>`（HTML5 doctype），否则 KaTeX 可能无法正确渲染
- W-025: CDN  starter 模板通过 jsDelivr 加载 `katex@0.18.4` 的 `katex.min.css`、`katex.min.js` 和 `contrib/auto-render.min.js`，均带 SRI integrity 哈希和 `crossorigin="anonymous"`
- W-026: 直接包含 `katex.js` 时 `katex` 对象作为全局变量可用；同时提供压缩版 `katex.min.js`
- W-027: 脚本默认使用 `defer` 属性延迟加载以加速页面渲染，`katex` 对象在 `DOMContentLoaded` 事件触发后可用
- W-028: 默认字体使用 `font-display: block` 防止 FOUT（Flash of Unstyled Text）；可改用 `katex-swap.css` 或 `katex-swap.min.css` 使用 `font-display: swap` 防止 FOIT（Flash of Invisible Text）
- W-029: 可通过 Web Font Loader 预加载字体，自定义字体族包括 `KaTeX_AMS`、`KaTeX_Caligraphic:n4,n7`、`KaTeX_Fraktur:n4,n7`、`KaTeX_Main:n4,n7,i4,i7`、`KaTeX_Math:i4,i7`、`KaTeX_Script`、`KaTeX_SansSerif:n4,n7,i4`、`KaTeX_Size1-4`、`KaTeX_Typewriter`
- W-030: 支持 AMD 模块加载器（通过 `require([...], katex => {...})`）和 ECMAScript module（通过 `<script type="module">` + `import katex from '...katex.mjs'`）
- W-031: ESM 方式可用 `nomodule` 属性为不支持 ES 模块的旧浏览器提供回退
- W-032: 使用打包工具（webpack、rollup.js 等）时通过 Node 包管理器安装并导入，必须打包样式表或手动引入
- W-033: 自托管方式一：从 GitHub releases 下载预构建的 `katex.tar.gz` 或 `katex.zip`（注意不是 auto-generated "Source code"），解压后包含 katex.js/katex.min.js/katex.mjs、katex.css/katex.min.css/katex-swap.css/katex-swap.min.css、contrib/（5 个扩展各含 .js/.min.js/.mjs）、fonts/（WOFF2/WOFF/TTF）
- W-034: 自托管方式二：通过 npm/yarn/pnpm 安装，文件位于 `node_modules/katex/dist/`；npm 包同时包含未构建的 TypeScript 源码（`src/`、`contrib/`、`katex.ts`），但这些不应直接在 HTML 中引用
- W-035: `fonts/` 目录必须与 CSS 文件位于同级目录（CSS 通过相对 URL 引用字体如 `url("fonts/KaTeX_AMS-Regular.woff2")`），移动或重命名字体会导致渲染失败

## API

来源：https://katex.org/docs/api

- W-036: 浏览器端渲染调用 `katex.render(expression, element, options)`，将 TeX 渲染到指定 DOM 元素
- W-037: 服务端/字符串渲染调用 `katex.renderToString(expression, options)` 返回 HTML 字符串
- W-038: 可使用 `String.raw` 模板标签避免反斜杠转义（但无法转义 `${` 和反引号）
- W-039: `throwOnError: false` 选项将无效输入以 TeX 源码形式红色渲染，hover 文本显示错误消息；未设置时无效 LaTeX 抛出 `katex.ParseError` 异常
- W-040: `render` 和 `renderToString` 的最后一个参数可包含渲染选项对象（指向 /docs/options）
- W-041: 持久宏（Persistent Macros）要求创建一个共享的 `macros` 对象并在每次调用 `render`/`renderToString` 时传入同一对象，不能每次调用创建新对象
- W-042: 当作者使用 `\gdef` 时，KaTeX 将宏定义插入传入的 `macros` 对象，由于该对象在多次调用间持续存在，`\gdef` 宏可在多个 KaTeX 元素间持久化
- W-043: 持久宏安全说明：持久宏可改变 KaTeX 行为（如重定义标准命令），应仅在共同信任的多个元素间使用；可为单条消息创建一个 `macros` 对象，不应跨多用户消息启用

## CLI

来源：https://katex.org/docs/cli

- W-044: CLI 在通过 Node 包管理器安装 KaTeX 后内置，默认从标准输入读取输入；可通过 `npx katex` 或 `./node_modules/.bin/katex` 执行
- W-045: CLI 页面共列出 18 个选项标题（含 `--version` 与 `--help`）：`-V, --version`、`-d, --display-mode`、`-F, --format <type>`、`--leqno`、`--fleqn`、`-t, --no-throw-on-error`、`-c, --error-color <color>`、`-m, --macro <def>`、`--min-rule-thickness <size>`、`-b, --color-is-text-color`、`-S, --strict`、`-T, --trust`、`-s, --max-size <n>`、`-e, --max-expand <n>`、`-f, --macro-file <path>`、`-i, --input <path>`、`-o, --output <path>`、`-h, --help`
- W-046: `-V, --version` 输出版本号
- W-047: `-d, --display-mode` 以显示模式渲染数学（\int、\sum 等变大，数学居中独占一行）
- W-048: `-F, --format <type>` 决定输出标记语言
- W-049: `--leqno` 将显示数学的 tag 渲染在左侧；`--fleqn` 将显示数学左对齐
- W-050: `-t, --no-throw-on-error` 遇到错误时渲染错误（颜色由 --error-color 指定）而非抛出 ParseError
- W-051: `-c, --error-color <color>` 接受 'rgb' 或 'rrggbb' 格式颜色字符串（无 #），指定 -t 选项渲染的错误颜色
- W-052: `-m, --macro <def>` 定义自定义宏，格式为 `'\foo:expansion'`，可多次使用 -m 参数定义多个宏
- W-053: `--min-rule-thickness <size>` 以 em 为单位指定分数线、\sqrt 顶线、array 竖线、\hline、\hdashline、\underline、\overline 及 \fbox/\boxed/\fcolorbox 边框的最小粗细
- W-054: `-b, --color-is-text-color` 使 \color 行为类似 LaTeX 两参数 \textcolor 而非单参数模式切换
- W-055: `-S, --strict` 开启严格/LaTeX 忠实模式，输入使用 LaTeX 不支持的特性时抛出错误
- W-056: `-T, --trust` 信任输入，启用所有 HTML 特性如 \url
- W-057: `-s, --max-size <n>` 非零时将用户指定尺寸（如 \rule{500em}{500em}）上限设为 maxSize ems；为零时元素和间距可任意大
- W-058: `-e, --max-expand <n>` 限制宏展开次数以防止无限宏循环；设为 Infinity 时宏展开器尝试像 LaTeX 一样完全展开
- W-059: `-f, --macro-file <path>` 从指定文件读取宏定义，每行一个
- W-060: `-i, --input <path>` 从指定文件读取 LaTeX 输入
- W-061: `-o, --output <path>` 将 HTML 输出写入指定文件；`-h, --help` 输出使用信息

## Auto-render Extension（自动渲染扩展）

来源：https://katex.org/docs/autorender

- W-062: Auto-render 扩展自动渲染文本中的所有数学，搜索给定元素内所有文本节点中的分隔符，忽略 `<pre>` 等标签，原地渲染数学
- W-063: 该扩展不是 KaTeX 核心的一部分，需通过 `<script>` 标签与 KaTeX 一同引入；CDN 示例引用 `katex@0.18.1`
- W-064: 扩展暴露单个函数 `window.renderMathInElement(elem, options)`，`elem` 为 HTML DOM 元素，函数递归搜索其中文本节点并渲染数学
- W-065: `options` 可包含与 `katex.render` 相同的键，外加五个 auto-render 专用键：`delimiters`、`ignoredTags`、`ignoredClasses`、`errorCallback`、`preProcess`
- W-066: `delimiters` 默认值为 8 条：`$$`（display:true）、`\(`...`\)`（display:false）、`\begin{equation}`...`\end{equation}`（display:true）、`\begin{align}`...`\end{align}`（display:true）、`\begin{alignat}`...`\end{alignat}`（display:true）、`\begin{gather}`...`\end{gather}`（display:true）、`\begin{CD}`...`\end{CD}`（display:true）、`\[`...`\]`（display:true）
- W-067: 若要添加 `$...$` 行内数学支持，必须将 `$` 规则列在 `$$` 之后（因为规则按顺序处理，先列 `$` 会把 `$$` 捕获为空数学表达式）
- W-068: `ignoredTags` 默认值为 `["script", "noscript", "style", "textarea", "pre", "code", "option"]`
- W-069: `ignoredClasses` 默认未设置；`errorCallback` 默认使用 `console.error`；`preProcess` 签名为 `(math: string) => string`，在渲染前处理数学表达式
- W-070: options 对象的 `displayMode` 属性被忽略，显示模式由 delimiters 中对应条目的 `display` 键决定
- W-071: `options.macros` 对象默认为空对象 `{}`，在多次 `katex.render` 调用间传递，连续方程可通过 `\gdef` 建立共享宏
- W-072: 提供 ESM 版本 `contrib/auto-render.mjs`，支持 `nomodule` 回退

## Extensions & Libraries（扩展与库）

来源：https://katex.org/docs/libs

- W-073: 官方 Extensions 列出 4 个：Auto-render（自动渲染文本中的数学）、Copy-tex（选择复制 KaTeX 渲染元素时将 LaTeX 源码复制到剪贴板）、`math/tex` Custom Script Type（自动显示 `type=math/tex` script 标签内的 LaTeX 数学）、mhchem（编写化学方程式）
- W-074: Copy-tex、mathtex-script-type、mhchem 的链接指向 GitHub `contrib/` 目录
- W-075: 第三方 Libraries 按平台/语言分类：AsciiMath（asciimath2tex）、Android（KaTeXView）、Angular2+（ng-katex）、Canvas（canvas-latex）、iOS（KaTeX-iOS、KatexUtils）、Jekyll（JekTex）、React（react-latex、react-katex）、Ruby（katex-ruby）、Rust（katex-rs）、Sphinx（sphinxcontrib-katex）、Vue（vue-katex）、Web-Components（katex-element、katex-expression）、Wechat Mini Program（@rojer/katex-mini）
- W-076: AsciiMath 需先转换为 LaTeX 再调用 KaTeX，asciimath2tex 库面向 KaTeX 设计
- W-077: Ruby 库 katex-ruby 提供服务端渲染及与 Rails、Hanami、Sprockets 等框架集成
- W-078: Rust 库 katex-rs 提供服务端渲染绑定
- W-079: Web Components 类库含 katex-element（自定义元素 `<katex-element>`）和 katex-expression（基于 Stencil）
- W-080: 微信小程序库为 @rojer/katex-mini

## Options（配置选项）

来源：https://katex.org/docs/options

- W-081: `displayMode`：boolean，默认 `false`；`true` 为显示模式（\displaystyle，\int/\sum 变大，居中独占一行，禁用自动换行），`false` 为行内模式（\textstyle，允许在最外层关系符或二元运算符后换行）
- W-082: `output`：string，可选值 `html`、`mathml`、`htmlAndMathml`（默认）；htmlAndMathml 输出 HTML 供视觉渲染并包含 MathML 供无障碍访问
- W-083: `leqno`：boolean，`true` 时显示数学的 \tag 渲染在左侧而非右侧；`fleqn`：boolean，`true` 时显示数学左对齐并带 2em 左边距
- W-084: `throwOnError`：boolean，默认 `true`；`true` 时遇到不支持命令或无效 LaTeX 抛出 ParseError；`false` 时将不支持命令渲染为文本、无效 LaTeX 以源码形式渲染（hover 文本显示错误），颜色由 errorColor 指定
- W-085: `errorColor`：string，格式 `"#XXX"` 或 `"#XXXXXX"`，默认 `#cc0000`；指定 throwOnError 为 false 时不支持命令和无效 LaTeX 的渲染颜色
- W-086: `macros`：object，键值对集合；键为以反斜杠开头的命令名（如 `"\\foo"`）或单字符（如 `"α"`），值为字符串（LaTeX 展开，支持 #1/#2 参数）、函数（接收 MacroExpander 实例返回字符串）或展开对象（含 tokens 和 numArgs，模拟 \def/\let 结果）
- W-087: `macros` 对象在 LaTeX 代码通过 `\gdef`、`\global\let`（或 globalGroup 下的 `\def`/`\newcommand`/`\let`）定义宏时会被修改；传入同一 macros 对象可使连续调用共享状态
- W-088: `minRuleThickness`：number，单位 em，指定分数线等最小粗细；通常值为 0.04，生效取值约 0.05 或 0.06；负值被忽略
- W-089: `colorIsTextColor`：boolean；当前 KaTeX 中 \color 是切换开关（如 `\color{blue} hello`），匹配 LaTeX 行为；设为 true 可恢复旧版（<0.8.0）和 MathJax 的参数式行为（`\color{blue}{hello}`）
- W-090: `maxSize`：number，用户指定尺寸上限（单位 em）；默认 `Infinity`，元素和间距可任意大
- W-091: `maxExpand`：number，宏展开次数上限，防止无限宏循环；`\edef` 展开计入所有展开 token；设为 Infinity 时完全展开；默认 `1000`
- W-092: `strict`：boolean 或 string 或 function，默认 `"warn"`；`false`/`"ignore"` 允许便利但非 (Xe)LaTeX 支持的特性；`true`/`"error"` 为 LaTeX 忠实模式，对违规抛出错误；`"warn"`（默认）通过 console.warn 警告；自定义函数签名为 `handler(errorCode, errorMsg, token)`，可返回 `"ignore"`/`"error"`/`"warn"`
- W-093: strict 的 errorCode 列表（会抛错类）：`"unknownSymbol"`（未知 Unicode 符号）、`"unicodeTextInMathMode"`（数学模式中使用 Unicode 文本字符）、`"mathVsTextUnits"`（数学/文本命令与单位/模式不匹配）、`"commentAtEnd"`（无终止换行的 % 注释）、`"htmlExtension"`（\html 前缀命令）
- W-094: strict 第二类 errorCode（不抛错但影响行为）：`"newLineInDisplayMode"`（显示模式中使用 \\ 或 \newline，严格模式下不产生换行）
- W-095: `trust`：boolean 或 function，默认 `false`；`false` 时阻止 \includegraphics 等可能产生不良行为的命令并以 errorColor 渲染；`true` 时允许所有此类命令；自定义函数签名为 `handler(context)`
- W-096: trust context 列表：`{command: "\\url", url, protocol}`、`{command: "\\href", url, protocol}`、`{command: "\\includegraphics", url, protocol}`、`{command: "\\htmlClass", class}`、`{command: "\\htmlId", id}`、`{command: "\\htmlStyle", style}`、`{command: "\\htmlData", attributes}`；protocol 为小写字符串如 "http"/"https"，相对 URL 为 "_relative"
- W-097: trust 示例包括禁止特定命令、允许特定命令、允许多个命令、允许特定协议、允许多个协议、允许所有但禁止特定协议、命令+协议组合
- W-098: `globalGroup`：boolean，默认 `false`；`true` 时在全局组中运行 KaTeX 代码，顶层 `\def`/`\newcommand` 定义的宏加入 macros 参数可在后续渲染调用中使用
- W-099: 默认行为下 LaTeX 中 `\begin{equation}` 和 `$$` 等构造创建局部组，阻止 `\gdef` 以外的定义在块外可见；globalGroup 选项改变此行为
- W-100: 函数型宏值接收的 `MacroExpander` 为内部 API，可能发生非向后兼容的变更；参考 `src/defineMacro.js`
- W-101: 展开对象示例：模拟 `\let\realint=\int` 可写为 `{"\\realint": {tokens: [{text: "\\int", noexpand: true}], numArgs: 0}}`

## Security（安全）

来源：https://katex.org/docs/security

- W-102: Security 页面声明 KaTeX 生成的 HTML 应可防止 `<script>` 或其他代码注入攻击
- W-103: 页面建议对 HTML 进行消毒，但需相当宽松的白名单（包含部分 SVG 和 MathML）以支持全部 KaTeX 功能
- W-104: `maxSize` 可防止超大宽高视觉攻击；`maxExpand` 可防止无限宏循环攻击；`trust` 可控制可能加载外部资源或改变 HTML 属性的命令（如 \includegraphics、\htmlClass）
- W-105: KaTeX 抛出的错误消息可能包含未转义的 LaTeX 源码
- W-106: 漏洞报告流程：私下通过 GitHub security advisory 或邮件 katex-security@mit.edu 报告；评估后发布修复和安全公告；修复发布前不公开披露

## Handling Errors（错误处理）

来源：https://katex.org/docs/error

- W-107: 若 KaTeX 遇到错误且 `throwOnError` 未设为 `false`，`render` 和 `renderToString` 抛出 `katex.ParseError` 类型异常
- W-108: 错误消息包含部分 LaTeX 源码，渲染到 HTML 前需转义；示例代码将 `&`、`<`、`>` 替换为 `&amp;`、`&lt;`、`&gt;`
- W-109: 未转义的不可信 LaTeX 源码或异常消息可能导致 `<script>` 注入攻击
- W-110: `e instanceof katex.ParseError` 可判断是否为 KaTeX 解析错误；其他错误应重新抛出
- W-111: 设 `throwOnError` 为 `false` 可使用内置行为：将 LaTeX 源码以 hover 文本显示错误的形式渲染

## Font（字体）

来源：https://katex.org/docs/font

- W-112: 字体属性通过修改 `src/styles/fonts.scss` 文件中的变量控制
- W-113: 默认 KaTeX 数学以周围上下文 1.21 倍字体大小渲染，使上下标更易读；可通过 CSS 控制（如 `.katex { font-size: 1.1em; }`）
- W-114: KaTeX 支持所有 TeX 单位，包括 cm、in 等绝对单位；绝对单位相对于默认 TeX 字号 10pt 缩放，`\kern1cm` 等价于 `\kern2.845275em`
- W-115: 相对单位和绝对单位均相对于 10pt 字体的 LaTeX 统一缩放；因浏览器默认字号较大，KaTeX 中 1cm kern 通常比浏览器单位的 1cm 显得更大
- W-116: KaTeX 提供三种字体格式：ttf（支持非常旧的浏览器和本地安装）、woff（现代浏览器广泛支持）、woff2（现代浏览器，更小更快）
- W-117: 构建时根据 Browserslist config 自动只包含目标环境所需字体；可通过 `USE_(FONT NAME)` 环境变量强制包含/排除
- W-118: 使用 Sass 时可通过 `@use 'node_modules/katex/src/styles/katex' with ($use-ttf: false; $use-woff: false; $use-woff2: true;)` 覆盖字体格式变量
- W-119: 默认构建期望字体位于 `katex.min.css` 同级的 `fonts` 目录；可通过修改 `webpack.common.js` 中 `sassVariables` 字符串添加 `$font-folder: "${fontLocation}";\n` 或替换 `src/styles/fonts.scss` 中的值改变位置，支持相对/绝对路径，修改后需 `pnpm build` 重新构建
- W-120: Sass 方式可通过 `@use '...katex' with ($font-folder: "path/to/fonts")` 覆盖字体目录

## Supported Functions（支持的函数）

来源：https://katex.org/docs/supported

- W-121: Supported Functions 页面是 KaTeX 支持的 TeX 函数列表，按逻辑分组排序
- W-122: 页面说明存在一个按字母排序的类似 Support Table 页面，同时列出支持和不支持的函数
- W-123: 页面包含 14 个 H2 分类：Accents、Delimiters、Environments、HTML、Letters and Unicode、Layout、Logic and Set Theory、Macros、Operators、Relations、Special Notation、Style/Color/Size/Font、Symbols and Punctuation、Units
- W-124: HTML 章节说明"raw HTML"特性对不可信输入有潜在危险，默认禁用，尝试使用时命令名以红色渲染（可通过 errorColor 配置）；完全信任输入需传 `trust: true`，也可通过 trust 选项仅启用部分命令或 URL
- W-125: HTML extension（\html 前缀）命令是非标准的，需要放宽 strict 选项中的 `htmlExtension` 设置
- W-126: Accents 章节列出 `\tilde`、`\widetilde`、`\hat`、`\widehat`、`\vec`、`\bar`、`\dot`、`\ddot`、`\dddot`、`\ddddot`、`\acute`、`\grave`、`\breve`、`\check`、`\mathring`、`\overgroup`、`\undergroup` 等重音命令
- W-127: Delimiter Sizing 支持 `\left`/`\right`/`\middle` 和 `\big`/`\Big`/`\bigg`/`\Bigg` 及其 l/m/r 变体
- W-128: Letters and Unicode 章节说明在 strict 为 false 或 "warn"（默认）时 KaTeX 在文本和数学模式下接受所有 Unicode 字母；未识别字符按文本模式处理；任何字符可通过 `\char"HHHH` 写入
- W-129: Environments 章节包含 matrix、pmatrix、bmatrix、Bmatrix、vmatrix、Vmatrix、array、aligned、gathered、cases 等环境

## Support Table（支持表）

来源：https://katex.org/docs/support_table

- W-130: Support Table 页面是按字母排序的 TeX 函数列表，包含 KaTeX 支持和不支持的函数
- W-131: 页面说明存在按类型排序的类似页面 Supported Functions；若知道字符形状但不知名称，可使用 Detexify（https://detexify.kirelabs.org/classify.html）
- W-132: 表格包含三列：Symbol/Function、Rendered、Source or Comment
- W-133: 表格以 `\gdef\VERT{|}` 开头定义竖线符号，条目覆盖 `!`、`\!`、`#`、`\%`、`&`、`\&`、`'`、`(`、`)`、`\(`...`\)`、`\ `、`\,`、`\:`、`\;`、`_`、`\_` 等符号及命令

## Common Issues（常见问题）

来源：https://katex.org/docs/issues

- W-134: 必须在 HTML 文件顶部包含 `<!DOCTYPE html>`，否则浏览器进入 quirks mode 导致 KaTeX 渲染错误；该要求在 `<iframe>` 中同样需要（iframe 不继承父文档 doctype）
- W-135: Jekyll 和 GitHub Pages 等 Markdown 预处理器的"smart quotes"特性将 `'` 转为 `’`，影响含撇号的数学（如 `f'`）；可通过定义单字符宏 `{"’", "'"}` 解决
- W-136: KaTeX 遵循 LaTeX 对 aligned 和 matrix 环境的渲染（与 MathJax 不同），垂直布局中分数行间距可能比 MathJax 用户习惯的小；可用 `\\[0.1em]` 代替标准行分隔距离调整
- W-137: KaTeX 不支持 `align` 环境（因为 LaTeX 不在数学模式中支持 align），应使用数学模式中的 `aligned` 环境
- W-138: MathJax 默认将 \color 定义为类似 \textcolor；设置 KaTeX 的 `colorIsTextColor` 选项为 true 可获得此行为；KaTeX 默认行为匹配启用 color.js 扩展的 MathJax
- W-139: MathJax 的 `\class`、`\cssId`、`\style` 在 KaTeX 中对应为 `\htmlClass`、`\htmlId`、`\htmlStyle`
- W-140: 部分符号通过宏而非 `\DeclareMathSymbol` 定义，展开时可能行为不同，可能展开为多个 token 并受 `\expandafter` 和 `\noexpand` 影响
- W-141: 排障代码片段可检测 katex.css 是否正确加载：通过 `.katex-version::after` 内容显示版本，未加载时显示 "The KaTeX stylesheet is not loaded!"；CSS 版本应与 `katex.version` 中的 JS 版本匹配
- W-142: CSS 自定义示例：`.katex-display { overflow: auto hidden }` 使显示公式水平可滚动；`.katex-display > .katex { white-space: normal }` 允许显示公式换行（与 LaTeX 不同）

## Migration Guide（迁移指南）

来源：https://katex.org/docs/migration

- W-143: v0.18.0：KaTeX 内部 CSS 类名加 `katex-` 前缀；迁移表列出 20 个重命名类，如 `.accent`→`.katex-accent`、`.base`→`.katex-base`、`.root`→`.katex-root`、`.rule`→`.katex-rule`、`.tag`→`.katex-tag`、`.underline`→`.katex-underline`、`.vbox`→`.katex-vbox` 等
- W-144: v0.17.0：`__defineFunction` 内部 API 变更，属性不再包裹在 `props` 中，需将 props 成员移到定义对象顶层
- W-145: v0.16.0：copy-tex 扩展不再拥有（也不需要）CSS 文件，需移除 `copy-tex.css` 的导入
- W-146: v0.15.0：`\relax` 现在实现为函数，会停止展开和解析；`\kern2\relax em` 不再工作
- W-147: v0.14.0：支持条件导出和 ESM 的模块加载器中 `import katex from 'katex'` 将导入 ESM；contrib 路径从 `katex/dist/contrib/[name].js` 改为 `katex/contrib/[name]`，`katex/dist/katex.mjs` 改为 `katex`
- W-148: v0.13.0 宏参数变更：解析宏参数时 token 不再展开；`\frac\foo\foo`（其中 \foo 定义为 12）将解析为 `\frac{12}{12}` 而非 `\frac{1}{2}12`；可用 `\expandafter` 在解析前展开参数
- W-149: v0.13.0 `\def` 不再接受花括号包裹的控制序列（`\def{\foo}{}` 需改为 `\def\foo{}`），也不再接受未用花括号包裹的替换文本（`\def\foo1` 需改为 `\def\foo{1}`）
- W-150: v0.13.0 `\newline` 和 `\cr` 不再接受可选尺寸参数，垂直间距应使用 `\\`
- W-151: v0.13.0 `\cfrac`、`\color`、`\textcolor`、`\colorbox`、`\fcolorbox` 不再允许作为原始命令（如无可选参数的 `\sqrt` 和上下标）的参数；`\sqrt\textcolor{red}{x}` 需改为 `\sqrt{\textcolor{red}{x}}`
- W-152: Migration 页面覆盖 v0.13.0 至 v0.18.0 共 6 个版本段

---

## 事实复核/修正

> 官网事实与源码事实出现差异时，在本节并列记录来源和结论，不静默覆盖。

### 修正-1：strict 默认值

- 现有源码事实 F-045 将 `strict` 列为 Settings 选项，但未标注默认值。
- 官网 Options 页面（https://katex.org/docs/options）明确标注：`strict` 默认值为 `"warn"`。
- CLI 页面 `-S, --strict` 为布尔开关（传入即开启 true/error 模式），与 Options 默认值 `"warn"` 不冲突——CLI 标志不传时对应 Options 默认 `"warn"`，传 `-S` 时设为 `true`。
- **结论**：以官网为准，`strict` 默认值为 `"warn"`；后续文档不得写为 `false`。

### 修正-2：maxExpand 默认值

- 现有源码事实 F-035 记录 maxExpand 默认 1000，F-045 同。
- 官网 Options 页面（https://katex.org/docs/options）明确标注：`maxExpand` 默认值为 `1000`。
- **结论**：源码事实与官网一致，无需修正。PRD 背景中"maxExpand 默认值为 Infinity"的表述与官网实际页面不符（官网仅说明可设为 Infinity，非默认值）。

### 修正-3：trust 默认值

- 现有源码事实 F-045 将 `trust` 列为选项，但未标注默认值。
- 官网 Options 页面明确标注：`trust` 默认值为 `false`。
- **结论**：以官网为准，`trust` 默认 `false`。

### 修正-4：globalGroup 默认值

- 现有源码事实 F-045 列出 `globalGroup` 选项，但未标注默认值。
- 官网 Options 页面明确标注：`globalGroup` 默认值为 `false`。
- **结论**：以官网为准，`globalGroup` 默认 `false`。

### 修正-5：throwOnError 默认值

- 现有源码事实 F-045 标注 `throwOnError` 默认 true。
- 官网 Options 页面明确标注：`throwOnError` 默认 `true`。
- **结论**：一致，无需修正。

### 修正-6：errorColor 默认值

- 现有源码事实 F-045 标注 `errorColor` 默认 #cc0000。
- 官网 Options 页面明确标注：`errorColor` 默认 `#cc0000`。
- **结论**：一致，无需修正。

### 修正-7：maxSize 默认值

- 现有源码事实 F-045 标注 `maxSize` 默认 Infinity。
- 官网 Options 页面明确标注：`maxSize` 默认 `Infinity`。
- **结论**：一致，无需修正。

### 修正-8：官网版本号标注不一致

- Versions 页面（https://katex.org/versions）标注当前稳定版为 0.16.47。
- Node/Browser/Font 页面 CDN 链接引用 `katex@0.18.4`；Auto-render 页面 CDN 链接引用 `katex@0.18.1`。
- 本 bundle 基于源码 v0.18.4，与 CDN 引用版本一致；Versions 页面版本标注差异记录在案，后续文档以 v0.18.4 为基准。

### 修正-9：Auto-render 默认 delimiters

- 现有源码事实 F-065 记录 auto-render 扫描 `$...$`、`$$...$$`、`\(...\)`、`\[...\]` 分隔符。
- 官网 Auto-render 页面列出的默认 delimiters 共 8 条，包含 `$$`、`\(...\)`、`\begin{equation}`、`\begin{align}`、`\begin{alignat}`、`\begin{gather}`、`\begin{CD}`、`\[`；默认**不包含** `$...$` 行内分隔符。
- **结论**：以官网为准修正默认 delimiters 列表；`$...$` 需用户手动添加且必须排在 `$$` 之后。

### 修正-10：Auto-render 默认 ignoredTags

- 现有源码事实 F-067 列出 ignoredTags 选项但未给出默认值。
- 官网 Auto-render 页面明确标注默认值为 `["script", "noscript", "style", "textarea", "pre", "code", "option"]`。
- **结论**：以官网为准补充默认值。

### 修正-11：CLI 参数数量

- 现有源码事实 F-007 记录 CLI 入口为 cli.js。
- 官网 CLI 页面列出 18 个选项标题（含 version/help）。
- **结论**：补充 CLI 全部选项的完整事实（W-045~W-061）。

### 修正-12：Node 构建要求

- 现有源码事实 F-004 记录包管理器为 pnpm@11.4.0。
- 官网 Node 页面标注从源码构建需要 Node.js 22.13 或更高版本、启用 corepack。
- **结论**：补充构建环境要求事实。
