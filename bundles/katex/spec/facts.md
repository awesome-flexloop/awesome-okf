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
- F-018: `src/metrics/` 目录包含 Python 脚本（extract_tfms.py、extract_ttfs.py、format_json.py、parse_tfm.py、mapping.pl）用于字体度量提取

## 公共 API（katex.ts）

- F-019: 默认导出对象包含属性：version、render、renderToString、ParseError、SETTINGS_SCHEMA、__parse、__renderToDomTree、__renderToHTMLTree、__setFontMetrics、__defineSymbol、__defineFunction、__defineMacro、__domTree
- F-020: `render(expression: string, baseNode: Node, options?: SettingsOptions): void` 将 LaTeX 渲染到指定 DOM 节点
- F-021: `renderToString(expression: string, options?: SettingsOptions): string` 将 LaTeX 渲染为 HTML 标记字符串
- F-022: `__parse(expression: string, options?: SettingsOptions): AnyParseNode[]` 返回解析树（标注为不推荐公开使用）
- F-023: `__renderToDomTree(expression: string, options: SettingsOptions): DomSpan` 返回内部 DOM 树（HTML+MathML）
- F-024: `__renderToHTMLTree(expression: string, options: SettingsOptions): DomSpan` 返回内部 DOM 树（仅HTML，无MathML）
- F-025: `__defineSymbol`、`__defineFunction`、`__defineMacro` 为扩展 API，用于添加自定义符号、函数、宏
- F-026: `__setFontMetrics` 用于扩展内部字体度量对象
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
- F-053: HTML+MathML 双输出时，MathML 节点放在 HTML 节点之前（用于无障碍访问，屏幕阅读器读取MathML）
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
