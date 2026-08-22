# KaTeX 核心洞察与知识地图

> I阶段产出：核心洞察四元组 + 知识地图设计

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

- F-049（Options类不可变，所有修改通过 having*/with* 方法返回新实例）、F-050（Style类8种不可变样式实例，通过sup/sub/fracNum/fracDen/cramp/text方法转换）
- **陈述**：渲染阶段的 Options 和 Style 对象采用不可变（immutable）设计，每次样式/颜色/字号/字体的变化都通过 `.havingStyle()`、`.withColor()`、`.havingCrampedStyle()` 等方法创建新 Options 实例传入子节点，而非修改共享状态。
- **证据**：F-049（Options类所有having*/with*方法调用extend()返回new Options）、F-050（Style类sup/sub/fracNum/fracDen/cramp/text方法返回styles数组中的预创建实例）
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

---

## 知识地图

### 学习路径

```
入门（2篇）
  ├─ 00-introduction.md      → KaTeX 是什么、解决什么问题、版本信息
  └─ 01-getting-started.md   → 安装、CDN、第一个示例、API快速参考

核心架构（6篇）
  ├─ 02-architecture-overview.md → 整体架构、消化管模型、数据流总览
  ├─ 03-lexer.md                 → 词法分析、Token、正则分词、catcodes
  ├─ 04-macro-expander.md        → 宏展开机制、Token栈、参数消费、展开计数
  ├─ 05-parser.md                → 解析器、模式切换、atom解析、函数调度
  ├─ 06-render-pipeline.md       → 渲染管线、buildTree、buildHTML、buildMathML
  └─ 07-dom-tree.md              → 虚拟DOM树、Span/Anchor/SvgNode、toNode/toMarkup

扩展机制（5篇）
  ├─ 08-function-registry.md     → 函数注册、FunctionSpec、handler、builders
  ├─ 09-macro-system.md          → 宏系统、Namespace、分组作用域、自定义宏
  ├─ 10-settings-options.md      → 配置系统、Settings/Options区别、Style不可变性
  ├─ 11-style-system.md          → TeX样式模型、8种Style、字号映射、tight spacing
  └─ 12-font-metrics.md          → 字体度量、fontMetrics、Unicode支持

扩展模块（2篇）
  ├─ 13-auto-render.md           → auto-render扩展、分隔符、DOM扫描
  └─ 14-contrib-extensions.md    → copy-tex、mhchem、render-a11y-string等
```

### 概念文档与事实映射

| 文档 | 覆盖事实 |
|------|---------|
| 00-introduction | F-001~F-010 |
| 01-getting-started | F-019~F-027（公共API） |
| 02-architecture-overview | F-028~F-042、F-051~F-056（三层模型+管线） |
| 03-lexer | F-028~F-031、F-029（正则） |
| 04-macro-expander | F-032~F-035、F-073~F-076 |
| 05-parser | F-036~F-043 |
| 06-render-pipeline | F-051~F-056、F-020~F-024 |
| 07-dom-tree | F-057~F-059、F-027 |
| 08-function-registry | F-046~F-048、F-012~F-013 |
| 09-macro-system | F-032~F-035、F-073~F-076、F-026 |
| 10-settings-options | F-044~F-045、F-049 |
| 11-style-system | F-050、F-060、F-061~F-063 |
| 12-font-metrics | F-064、F-016~F-018 |
| 13-auto-render | F-065~F-067 |
| 14-contrib-extensions | F-068~F-070 |

### 示例文档规划

| 示例 | 内容 |
|------|------|
| basic-render.md | render()/renderToString() 基本用法、displayMode/inlineMode |
| custom-macros.md | 通过 settings.macros 和 __defineMacro 添加自定义宏 |
| custom-extension.md | 使用 __defineFunction 添加自定义LaTeX命令的完整示例 |
| auto-render-usage.md | auto-render扩展的配置和使用 |
| error-handling.md | throwOnError、errorColor、strict模式的错误处理 |
