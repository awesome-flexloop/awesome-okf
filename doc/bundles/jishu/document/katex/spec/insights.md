---
type: Spec
title: KaTeX 核心洞察与知识地图
description: 从源码架构与官网文档双信源提炼的核心洞察四元组，以及覆盖 00-23 概念文档、8 个示例和官网 17 页的完整知识地图
tags: [katex, architecture, insights, knowledge-map]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T20:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T20:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: facts
    resource: /spec/facts.md
    title: KaTeX 事实清单（源码 F-001~F-076 + 官网 W-001~W-152）
---

# KaTeX 核心洞察与知识地图

> I阶段产出：核心洞察四元组 + 知识地图设计。洞察 1-5 为源码架构洞察（保留原有分析），洞察 6-9 为官网用户视角与事实偏差修正洞察。

## 核心洞察（四元组）

### 洞察1：TeX 消化管隐喻的架构映射

- **陈述**：KaTeX 的核心处理管线严格遵循 TeX 的 "mouth→gullet→stomach" 消化管模型，Lexer 是 mouth（口/词法分析）、MacroExpander 是 gullet（食道/宏展开）、Parser 是 stomach（胃/语法解析），三者职责分离且通过 Token 流串联。
- **证据**：F-028（Lexer.lex()）、F-032（MacroExpander 注释直接称 gullet）、F-036（Parser 构造函数创建 gullet）、F-038~F-042（Parser 通过 fetch()→gullet.expandNextToken() 获取已展开token）
- **反常识**：一般编译器实现常将词法分析和宏展开混在 Parser 中，但 KaTeX 刻意模仿 TeX 原始设计将宏展开独立为 gullet 层——这不是过度设计，而是处理 TeX 动态语法（宏可改变语法结构）的必要架构。
- **行动**：理解 KaTeX 必须先理解这个三层模型，不要跳过 MacroExpander 直接看 Parser；自定义扩展时需明确自己在mouth/gullet/stomach哪一层工作（defineSymbol在mouth层，defineMacro在gullet层，defineFunction在stomach层）。

### 洞察2：注册表驱动的可扩展架构

- **陈述**：KaTeX 的所有 LaTeX 命令（\frac、\sqrt、\color 等）都通过 defineFunction/defineMacro/defineEnvironment 注册到全局表中，核心 Parser/Build 引擎本身是一个不包含任何具体命令的"空壳"，命令实现全部以插件形式存在。
- **证据**：F-046（_functions/_htmlGroupBuilders/_mathmlGroupBuilders三个全局表）、F-047（FunctionSpec 接口）、F-012（src/functions/目录43个文件）、F-013（environments/目录2个文件）、F-025~F-027（__defineFunction/__defineMacro/__defineSymbol 公开扩展API）
- **反常识**：核心引擎仅约2000行代码（Lexer+Parser+MacroExpander+Settings+Options+Style+buildTree），而具体命令实现占了代码量的大部分（43个函数文件×平均~100行 ≈ 4000+行）。这意味着学习KaTeX不应该先读函数实现，而应该先掌握注册表机制和核心引擎接口。
- **行动**：添加自定义LaTeX命令时，按照"注册handler→注册htmlBuilder→注册mathmlBuilder"三步进行；参考现有函数文件（如 genfrac.ts 处理分数族、op.ts 处理算符族）作为模板。

### 洞察3：不可变 Options + Style 传递的渲染状态模型

- **陈述**：渲染阶段的 Options 和 Style 对象采用不可变（immutable）设计，每次样式/颜色/字号/字体的变化都通过 `.havingStyle()`、`.withColor()`、`.havingCrampedStyle()` 等方法创建新 Options 实例传入子节点，而非修改共享状态。
- **证据**：F-049（Options类不可变，所有修改通过 having*/with* 方法返回新实例）、F-050（Style类8种不可变样式实例，通过sup/sub/fracNum/fracDen/cramp/text方法转换）
- **反常识**：这种设计看起来"低效"（频繁创建对象），但实际上 Style 只有8种预创建实例（0-7），Options 的 extend 是浅拷贝，而且不可变性彻底避免了子树渲染污染父节点状态的问题——这是CSS继承模型在JavaScript中的正确实现方式。
- **行动**：编写自定义 htmlBuilder/mathmlBuilder 时，必须通过 options.having*() 创建新的 Options 对象传递给子节点的 buildGroup/buildExpression 调用，绝不能直接修改 options 的属性。

### 洞察4：HTML+MathML 双输出无障碍设计

- **陈述**：KaTeX 默认输出同时包含 MathML（语义标记，屏幕阅读器可读）和 HTML（视觉呈现），MathML 节点放在 HTML 节点之前，且通过 CSS 让视觉上只看到 HTML 渲染结果。
- **证据**：F-052（output默认值为htmlAndMathml）、F-053（MathML在HTML之前）、F-051（buildTree双分支）
- **反常识**：很多数学渲染库（如MathJax早期版本）只输出HTML或只输出MathML，但KaTeX选择同时输出二者——这增加了代码复杂度（需要写两套builder：htmlBuilder和mathmlBuilder），但获得了"开箱即用的无障碍访问"能力，且MathML的语义信息对搜索引擎和辅助技术至关重要。
- **行动**：自定义函数扩展时，必须同时提供 htmlBuilder 和 mathmlBuilder，缺少mathmlBuilder会导致屏幕阅读器无法识别自定义命令。

### 洞察5：虚拟DOM中间层的双输出能力

- **陈述**：KaTeX 不直接操作浏览器DOM或拼接HTML字符串，而是先构建一层虚拟DOM树（domTree.ts中的Span/Anchor/SvgNode等），再通过 toNode() 和 toMarkup() 分别输出为真实DOM和HTML字符串。
- **证据**：F-057（domTree.ts定义虚拟节点类）、F-058（toNode/toMarkup双方法）、F-020~F-021（render和renderToString分别走toNode和toMarkup路径）
- **反常识**：这个虚拟DOM层比React的虚拟DOM简单得多（没有diff算法），但它的价值不在于性能优化，而在于同一份虚拟树可以同时服务于DOM渲染和服务端字符串渲染——这是KaTeX能同时支持浏览器端render()和SSR端renderToString()的架构基础。
- **行动**：理解 domTree 节点类型是编写自定义 builder 的前提；buildHTML 返回的是虚拟节点树而非真实DOM。

### 洞察6：三层安全防御纵深——源码能力与官网安全指引的互补

- **陈述**：KaTeX 在源码层面提供了 maxSize、maxExpand、trust 三个独立的安全配置项，官网 Security 页面进一步将其组织为"防御纵深"模型——maxSize 防超大宽高视觉攻击、maxExpand 防无限宏循环 DoS、trust 控制可能加载外部资源或改变 HTML 属性的命令（如 \includegraphics、\htmlClass），并明确建议对输出 HTML 进行消毒。源码定义了"能配置什么"，官网定义了"应该怎么安全地用"。
- **证据**：F-045（Settings 包含 maxSize/maxExpand/trust 选项）、W-090（maxSize 默认 Infinity）、W-091（maxExpand 默认 1000，设为 Infinity 时完全展开）、W-095（trust 默认 false，自定义函数接收 context）、W-096（trust context 覆盖 \url/\href/\includegraphics/\htmlClass/\htmlId/\htmlStyle/\htmlData 七类命令）、W-104（三层防护说明）、W-102~W-103（HTML 消毒建议，需宽松白名单含 SVG 和 MathML）、W-105（错误消息可能含未转义 LaTeX 源码）、W-109（未转义源码可导致 script 注入）
- **反常识/差异**：源码中 maxSize 默认值是 Infinity（不限制），看起来"不安全"，但官网明确将其列为安全防线之一——默认不限制是为了功能完整性，安全责任转移给部署者。这与"安全默认"的常见直觉相反，体现了 KaTeX "库不假设部署场景"的设计哲学：渲染库提供闸门，是否落闸由集成方决定。
- **行动**：处理不可信输入时必须同时设置 maxSize 合理上限、保持 maxExpand 默认值 1000、trust=false，并对输出做 HTML 消毒（白名单需包含部分 SVG 和 MathML）；catch ParseError 后，错误消息中的 LaTeX 源码必须经 HTML 转义（& < >）再显示。

### 洞察7：持久宏的有状态设计——API 简洁性与安全边界的张力

- **陈述**：KaTeX 的 render/renderToString 表面上是无状态纯函数，但通过传入共享的 macros 对象实现了有状态的宏持久化——\gdef/\global\let（或 globalGroup 下的 \def/\newcommand/\let）会修改该对象，使宏定义在多次调用间存活。官网 API 页面明确警告持久宏只能在共同信任的多个元素间使用，globalGroup 选项进一步控制顶层 \def 的作用域（默认 false 时局部组阻止定义外泄）。
- **证据**：W-041~W-043（持久宏要求共享同一 macros 对象，\gdef 插入该对象，安全说明：不应跨多用户消息启用）、W-086~W-087（macros 值支持字符串/函数/展开对象三种形式，对象在 \gdef/\global\let 时被修改）、W-098~W-099（globalGroup 默认 false，默认行为下 \begin{equation}/$$ 创建局部组阻止 \gdef 以外定义外泄）、F-045（Settings 包含 macros 和 globalGroup）、F-073~F-074（macros.ts 内置宏与 Namespace 分组作用域 beginGroup/endGroup）
- **反常识/差异**：纯函数 API 通常假设无副作用，但 KaTeX 刻意通过可变参数对象模拟 TeX 的 \gdef 全局语义。官网文档对此的安全警告（"不应跨多用户消息启用"）在源码类型定义中完全不可见——TypeScript 类型签名上 macros 只是普通 object，看不出其会被变异。这种"文档承载安全契约、类型不表达副作用"的分工在渲染库中常见但容易踩坑。
- **行动**：同信任域的多个 KaTeX 元素可共享一个 macros 对象实现连续方程宏复用；多用户/多消息场景必须为每条消息创建独立 macros 对象；globalGroup=true 时需理解其改变了顶层 \def 的可见性语义；阅读源码时注意 macros 对象是输入输出双向参数。

### 洞察8：版本标注不一致——信源交叉验证的必要性

- **陈述**：官网 Versions 页面标注当前稳定版为 0.16.47，而 Node/Browser/Font 页面的 CDN 链接引用 katex@0.18.4，Auto-render 页面 CDN 引用 katex@0.18.1；源码 package.json 确认版本为 0.18.4。官网文档自身存在版本标注不一致，Versions 页面更新滞后于文档页面中的 CDN 链接。
- **证据**：W-010（Versions 页"Current version (Stable)"标注 0.16.47）、W-011（Past Versions 表格列出 0.16.46）、W-013（版本标注差异说明，本 bundle 以源码 v0.18.4 为基准）、W-025（Browser 页 CDN 引用 katex@0.18.4）、W-015（Node 页 Deno CDN 导入 katex@0.18.4）、W-063（Auto-render 页 CDN 引用 katex@0.18.1）、F-001（源码 package.json 版本 0.18.4）、修正-8
- **反常识/差异**：通常认为官网"最新版本"页面是最权威的，但 KaTeX 官网的 Versions 页面反而落后于文档内容页中的 CDN 版本号——这说明官网不同页面可能由不同发布流程维护，版本标注不是原子更新。源码 package.json 才是版本的最终权威信源，而非官网版本索引页。
- **行动**：引用 KaTeX 版本时以 package.json 为权威基准；复制 CDN 链接时需逐页核对版本一致性（注意 auto-render 可能与核心不同步）；本 bundle 统一以 v0.18.4 为基准，版本差异在 facts.md 修正-8 中记录在案，后续文档不得混用版本号。

### 洞察9：官网与源码的双信源分层——用户文档与架构文档互补而非替代

- **陈述**：官网文档面向使用者（安装、API、选项默认值、安全、CLI），源码事实面向架构理解（Lexer、MacroExpander、Parser、buildTree、虚拟 DOM）。二者存在明确分层：官网说明"怎么用"和"默认值是什么"，源码揭示"内部如何工作"。部分配置默认值在源码类型定义中未显式声明（strict、trust、globalGroup），必须由官网 Options 页面提供权威值——单读任一信源都不完整。
- **证据**：F-045（Settings 选项列表列出 strict/trust/globalGroup 但未标注默认值）、W-092（strict 默认 "warn"，支持 false/"ignore"/true/"error"/"warn"/自定义函数）、W-095（trust 默认 false）、W-098（globalGroup 默认 false）、修正-1（strict 默认值以官网为准，非 false）、修正-3（trust 默认 false）、修正-4（globalGroup 默认 false）、F-035（maxExpand 默认 1000 源码与官网 W-091 一致）、W-016（源码构建需 Node 22.13+、corepack，补充了源码事实中缺失的构建环境要求）
- **反常识/差异**：源码常被视为"最终真相"，但 KaTeX 源码中 Settings 选项的默认值并未全部在 TypeScript 类型或 schema 中以人类可读方式标注——SETTINGS_SCHEMA 定义了选项的类型和约束，但部分默认值（如 strict 的 "warn"）需要查阅官网文档或运行时 defaults 才能确认。这意味着"源码即文档"在配置契约层面不成立，必须官网与源码双信源交叉验证。
- **行动**：编写概念文档时，配置选项默认值以官网 Options 页面为准，内部架构机制以源码为准；facts.md 中的"事实复核/修正"小节（修正-1~修正-12）是双信源交叉验证的正式记录，后续 E 阶段文档必须引用修正后的结论，不得回退到修正前的错误默认值。

---

## 知识地图

### 文档全清单（00-23 概念文档 + 8 示例 + 2 references）

#### 概念文档（24 篇）

| 编号 | 文档 | 状态 | 内容概要 |
|------|------|------|---------|
| 00 | [00-introduction.md](../concepts/00-introduction.md) | 更新 | KaTeX 是什么、核心特点、版本许可、能力边界；融合首页卖点与 Users/Versions 入口 |
| 01 | [01-getting-started.md](../concepts/01-getting-started.md) | 更新 | 安装、CDN、核心 API（render/renderToString）、String.raw、错误处理、持久宏说明 |
| 02 | [02-architecture-overview.md](../concepts/02-architecture-overview.md) | 保留 | 三层消化管模型（Lexer→MacroExpander→Parser）、注册表驱动设计、双输出无障碍 |
| 03 | [03-lexer.md](../concepts/03-lexer.md) | 保留 | 正则分词、Token结构、catcodes、\verb特殊处理 |
| 04 | [04-macro-expander.md](../concepts/04-macro-expander.md) | 保留 | Token栈、展开循环、参数消费、Namespace分组作用域 |
| 05 | [05-parser.md](../concepts/05-parser.md) | 保留 | 递归下降解析、atom/上下标处理、函数调度、模式切换 |
| 06 | [06-render-pipeline.md](../concepts/06-render-pipeline.md) | 保留 | buildTree/buildHTML/buildMathML、HTML+MathML双输出、displayWrap |
| 07 | [07-dom-tree.md](../concepts/07-dom-tree.md) | 保留 | Span/Anchor/SymbolNode/SvgNode、toNode/toMarkup双输出 |
| 08 | [08-function-registry.md](../concepts/08-function-registry.md) | 保留 | defineFunction三要素（handler/htmlBuilder/mathmlBuilder）、FunctionSpec、参数类型 |
| 09 | [09-macro-system.md](../concepts/09-macro-system.md) | 保留 | 内置宏、自定义宏（settings.macros/__defineMacro）、\newcommand/\def |
| 10 | [10-settings-options.md](../concepts/10-settings-options.md) | 更新 | Settings/Options双层配置、strict/trust/globalGroup默认值修正、trust context、macro函数、不可变状态传递 |
| 11 | [11-style-system.md](../concepts/11-style-system.md) | 更新 | 8种TeX样式、字号映射、tight spacing；补充官网Font页用户视角说明 |
| 12 | [12-font-metrics.md](../concepts/12-font-metrics.md) | 更新 | 字体族组织、fontMetrics、Unicode；融合Font页字体格式/Browserslist/Sass变量 |
| 13 | [13-auto-render.md](../concepts/13-auto-render.md) | 更新 | renderMathInElement()、默认delimiters修正（8条不含$...$）、ignoredTags默认值、preProcess、宏持久化 |
| 14 | [14-contrib-extensions.md](../concepts/14-contrib-extensions.md) | 更新 | 官方5扩展（auto-render/copy-tex/mathtex-script-type/mhchem/render-a11y-string）；第三方库移至23 |
| 15 | 15-installation-and-runtime.md | 新增 | 浏览器CDN/自托管、Node/npm/pnpm/yarn/Deno、ESM/CJS、CSS/字体路径、Bundler、Browserslist/USE_FONT构建 |
| 16 | 16-command-line.md | 新增 | CLI输入/输出、18个选项（含--version/--help）、与Options映射、宏文件、常见用法 |
| 17 | 17-fonts-and-units.md | 新增 | 字体加载策略、katex-swap.css、FOUT/FOIT、TeX单位换算、绝对长度缩放、字体自托管、1.21em默认缩放 |
| 18 | 18-security-and-errors.md | 新增 | trust控制命令、maxSize/maxExpand防护、HTML消毒白名单、ParseError、错误消息转义、安全封装 |
| 19 | 19-supported-functions.md | 新增 | 按官网14个H2分类整理支持函数（Accents/Delimiters/Environments/HTML/Layout等） |
| 20 | 20-support-table.md | 新增 | 字母序支持表用途、支持/不支持条目阅读方式、Detexify、源码/宏定义溯源 |
| 21 | 21-common-issues.md | 新增 | DOCTYPE/quirks mode、智能引号、aligned/matrix间距、align vs aligned、color差异、MathJax命名映射、CSS排障 |
| 22 | 22-migration.md | 新增 | v0.13-v0.18迁移要点：CSS类名前缀、__defineFunction、contrib路径、\relax、宏参数行为 |
| 23 | 23-ecosystem-and-versions.md | 新增 | Users列表、Versions版本说明、官方扩展入口、第三方库索引（React/Vue/Angular/Android/iOS/Rust/Ruby/小程序等） |

#### 示例文档（8 篇）

| 文档 | 状态 | 内容 |
|------|------|------|
| [basic-render.md](../examples/basic-render.md) | 更新 | render/renderToString、行内/显示模式、常见公式；与官网API表述一致 |
| [custom-macros.md](../examples/custom-macros.md) | 更新 | settings.macros别名、带参数宏、函数宏、共享macros对象、\gdef持久化、宏安全边界 |
| [custom-extension.md](../examples/custom-extension.md) | 更新 | __defineFunction添加命令、builder、MathML无障碍要求；对照官网/源码检查 |
| [auto-render-usage.md](../examples/auto-render-usage.md) | 更新 | 默认delimiters、$$先于$规则、ignoredTags/ignoredClasses、preProcess、动态内容、宏持久化 |
| [error-handling.md](../examples/error-handling.md) | 更新 | throwOnError/errorColor、strict模式、ParseError、trust安全、安全封装函数 |
| node-ssr.md | 新增 | Node.js/ESM/CJS中renderToString、CSS引入、HTML注入注意事项 |
| security-trust.md | 新增 | 不可信输入配置、trust函数、错误处理、HTML消毒、持久宏隔离 |
| cli-render.md | 新增 | npx katex从stdin到stdout、--input/--output/--display-mode/--macro/--macro-file/--no-throw-on-error |

#### References（2 篇）

| 文档 | 状态 | 内容 |
|------|------|------|
| [katex-source.md](../references/katex-source.md) | 更新 | v0.18.4 源码核心文件索引，补充官网关联说明 |
| katex-website.md | 新增 | 官网17个页面登记：ID、URL、标题、用途、引用提示 |

### 概念文档与事实映射

| 文档 | 源码事实 | 官网事实 |
|------|---------|---------|
| 00-introduction | F-001~F-010 | W-001~W-005（首页）、W-006~W-009（Users）、W-010~W-013（Versions） |
| 01-getting-started | F-019~F-027（公共API） | W-036~W-043（API）、W-023~W-031（Browser） |
| 02-architecture-overview | F-028~F-042、F-051~F-056 | W-002（Fast/SSR特点） |
| 03-lexer | F-028~F-031 | — |
| 04-macro-expander | F-032~F-035、F-073~F-076 | W-091（maxExpand）、W-100（MacroExpander内部API） |
| 05-parser | F-036~F-043 | — |
| 06-render-pipeline | F-051~F-056、F-020~F-024 | W-082（output选项） |
| 07-dom-tree | F-057~F-059、F-027 | — |
| 08-function-registry | F-046~F-048、F-012~F-013 | W-100（defineMacro参考） |
| 09-macro-system | F-032~F-035、F-073~F-076、F-026 | W-041~W-043、W-086~W-087、W-101 |
| 10-settings-options | F-044~F-045、F-049 | W-081~W-101（Options全页） |
| 11-style-system | F-050、F-060、F-061~F-063 | W-113（1.21em缩放）、W-114~W-115（单位） |
| 12-font-metrics | F-064、F-016~F-018 | W-112、W-116~W-120（Font全页） |
| 13-auto-render | F-065~F-067 | W-062~W-072（Auto-render全页） |
| 14-contrib-extensions | F-068~F-070 | W-073~W-074（Extensions）、W-124~W-125（HTML扩展） |
| 15-installation-and-runtime | F-004~F-008 | W-014~W-022（Node）、W-023~W-035（Browser）、W-116~W-119（构建字体） |
| 16-command-line | F-007 | W-044~W-061（CLI全页） |
| 17-fonts-and-units | F-061~F-063 | W-112~W-120（Font全页）、W-028（font-display） |
| 18-security-and-errors | F-045（安全相关选项） | W-102~W-106（Security）、W-107~W-111（Error） |
| 19-supported-functions | F-012（函数目录） | W-121~W-129（Supported Functions） |
| 20-support-table | — | W-130~W-133（Support Table） |
| 21-common-issues | — | W-134~W-142（Common Issues） |
| 22-migration | F-001（版本基准） | W-143~W-152（Migration全页） |
| 23-ecosystem-and-versions | F-010 | W-006~W-013（Users/Versions）、W-073~W-080（Extensions & Libraries） |

### 官网 17 页面映射表

| # | 官网页面 | URL | 映射文档 |
|---|---------|-----|---------|
| 1 | 首页（Home） | https://katex.org/ | 00-introduction |
| 2 | Users | https://katex.org/users | 00-introduction、23-ecosystem-and-versions |
| 3 | Versions | https://katex.org/versions | 00-introduction、23-ecosystem-and-versions |
| 4 | Node.js | https://katex.org/docs/node | 01-getting-started、15-installation-and-runtime |
| 5 | Browser | https://katex.org/docs/browser | 01-getting-started、15-installation-and-runtime |
| 6 | API | https://katex.org/docs/api | 01-getting-started、09-macro-system |
| 7 | CLI | https://katex.org/docs/cli | 16-command-line、examples/cli-render |
| 8 | Auto-render | https://katex.org/docs/autorender | 13-auto-render、examples/auto-render-usage |
| 9 | Extensions & Libraries | https://katex.org/docs/libs | 14-contrib-extensions、23-ecosystem-and-versions |
| 10 | Options | https://katex.org/docs/options | 10-settings-options、04-macro-expander |
| 11 | Security | https://katex.org/docs/security | 18-security-and-errors、examples/security-trust |
| 12 | Handling Errors | https://katex.org/docs/error | 18-security-and-errors、examples/error-handling |
| 13 | Font | https://katex.org/docs/font | 12-font-metrics、17-fonts-and-units |
| 14 | Supported Functions | https://katex.org/docs/supported | 19-supported-functions |
| 15 | Support Table | https://katex.org/docs/support_table | 20-support-table |
| 16 | Common Issues | https://katex.org/docs/issues | 21-common-issues |
| 17 | Migration | https://katex.org/docs/migration | 22-migration |

### 学习路径

#### 路径1：使用 KaTeX（不读源码）

```
00-introduction → 01-getting-started → 15-installation-and-runtime
                         ↓
              examples/basic-render
                         ↓
              10-settings-options（配置选项）
                         ↓
    ┌────────────────────┼────────────────────┐
    ↓                    ↓                    ↓
18-security-and-   13-auto-render      16-command-line
errors             → examples/          → examples/cli-render
→ examples/          auto-render-usage
  error-handling
→ examples/
  security-trust
```

目标读者：前端/Node.js 开发者，只需在项目中集成和使用 KaTeX。
覆盖官网页面：首页、Node、Browser、API、Options、Security、Error、Auto-render、CLI。

#### 路径2：理解 KaTeX 架构（读源码）

```
00-introduction → 02-architecture-overview
                      ↓
        ┌─────────┬───┴───┬──────────┐
        ↓         ↓       ↓          ↓
     03-lexer  04-macro  05-parser  06-render-pipeline
                  ↓                        ↓
            09-macro-system            07-dom-tree
                                        ↓
                               10-settings-options
                                        ↓
                                  11-style-system
                                        ↓
                                   12-font-metrics
```

目标读者：希望深入理解 TeX 排版引擎实现、编译器架构的工程师。
覆盖源码事实：F-028~F-064，三层消化管模型、注册表、虚拟 DOM、不可变状态。

#### 路径3：扩展 KaTeX（自定义命令）

```
08-function-registry → examples/custom-extension
       ↑                      ↓
09-macro-system      （了解虚拟DOM）→ 07-dom-tree
       ↑                      ↓
examples/custom-macros    （了解Options）→ 10-settings-options
       ↑                      ↓
14-contrib-extensions   （无障碍要求）→ 06-render-pipeline
                              ↓
                     examples/security-trust
```

目标读者：需要添加自定义 LaTeX 命令、宏或贡献扩展的开发者。
覆盖：defineFunction/defineMacro、FunctionSpec、htmlBuilder/mathmlBuilder、MathML 无障碍、安全考量。

#### 路径4：升级排障与生态选型

```
21-common-issues（常见问题排查）
       ↓
22-migration（版本迁移 v0.13→v0.18）
       ↓
19-supported-functions → 20-support-table（查支持范围）
       ↓
23-ecosystem-and-versions（第三方库选型：React/Vue/Angular/小程序等）
       ↓
17-fonts-and-units（字体/单位/渲染异常排障）
```

目标读者：维护已有 KaTeX 集成、准备升级、排查渲染问题或选择生态库的开发者。
覆盖官网页面：Common Issues、Migration、Supported Functions、Support Table、Users/Versions/Libs、Font。
