---
type: Reference
title: KaTeX 源码信源
description: KaTeX v0.18.4 源码仓库与核心文件索引
tags: [katex, source, reference]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-02-22
sources:
  - id: katex-repo
    resource: https://github.com/KaTeX/KaTeX
    title: KaTeX GitHub Repository
---

## KaTeX 源码索引

本文档登记 KaTeX v0.18.4 源码中各核心模块的文件路径，作为 Wiki 中所有事实溯源的信源目标。

### 入口与配置

| 文件 | 路径（相对仓库根） | 职责 |
|------|-------------------|------|
| 主入口 | `katex.ts` | 公共API导出：render/renderToString/ParseError/扩展API |
| 配置 | `src/Settings.ts` | Settings类、SETTINGS_SCHEMA、Strict/Trust处理 |
| CLI | `cli.js` | 命令行接口入口 |
| 包定义 | `package.json` | 版本、依赖、脚本、导出配置 |

### 词法与解析

| 文件 | 路径 | 职责 |
|------|------|------|
| 词法分析器 | `src/Lexer.ts` | Lexer类、正则分词、catcode管理、注释处理 |
| Token定义 | `src/Token.ts` | Token类、SourceLocation、LexerInterface |
| 宏展开器 | `src/MacroExpander.ts` | MacroExpander类（gullet）、Token栈、宏展开循环、参数消费 |
| 命名空间 | `src/Namespace.ts` | 分组作用域管理（beginGroup/endGroup） |
| 解析器 | `src/Parser.ts` | Parser类（stomach）、模式切换、atom解析、函数调度、参数解析 |
| 源码位置 | `src/SourceLocation.ts` | 输入位置范围记录 |
| 解析错误 | `src/ParseError.ts` | ParseError异常类 |

### 注册系统

| 文件 | 路径 | 职责 |
|------|------|------|
| 函数注册 | `src/defineFunction.ts` | defineFunction()、_functions/_htmlGroupBuilders/_mathmlGroupBuilders全局表 |
| 宏注册 | `src/defineMacro.ts` | MacroDefinition类型、MacroContextInterface |
| 环境注册 | `src/defineEnvironment.ts` | defineEnvironment()、_environments全局表 |
| 符号表 | `src/symbols.ts` | 内置符号注册表（math/text模式） |
| 函数索引 | `src/functions.ts` | 函数模块汇总导出 |
| 宏定义 | `src/macros.ts` | 内置宏定义 |
| 环境索引 | `src/environments.ts` | 环境模块汇总导出 |
| 函数实现 | `src/functions/*.ts` | 43个LaTeX命令的handler+builder实现 |
| 环境实现 | `src/environments/*.ts` | array/cd环境实现 |

### 渲染

| 文件 | 路径 | 职责 |
|------|------|------|
| 构建入口 | `src/buildTree.ts` | buildTree()/buildHTMLTree()、输出格式选择、display包装 |
| HTML构建 | `src/buildHTML.ts` | buildHTML()、分组构建、表达式构建 |
| MathML构建 | `src/buildMathML.ts` | buildMathML()、语义标注生成 |
| 构建通用 | `src/buildCommon.ts` | makeSpan/makeAnchor等工具函数、度量计算 |
| 虚拟DOM | `src/domTree.ts` | Span/Anchor/SymbolNode/SvgNode/PathNode/LineNode虚拟节点 |
| MathML树 | `src/mathMLTree.ts` | MathML虚拟节点 |
| 树抽象 | `src/tree.ts` | DocumentFragment/VirtualNode基类 |
| 解析节点 | `src/parseNode.ts` | 解析节点类型工具 |
| 解析树 | `src/parseTree.ts` | parseTree()入口函数 |
| 节点类型 | `src/types/nodes.ts` | AnyParseNode联合类型与各节点类型定义 |

### 样式与字体

| 文件 | 路径 | 职责 |
|------|------|------|
| 样式 | `src/Style.ts` | Style类、8种样式实例（display/text/script/scriptscript × cramped） |
| 渲染选项 | `src/Options.ts` | Options类、字号映射、不可变with*/having*方法 |
| 字体度量 | `src/fontMetrics.ts` | getGlobalMetrics()、字体度量数据接口 |
| 分隔符 | `src/delimiter.ts` | 分隔符尺寸与渲染 |
| 可延伸符 | `src/stretchy.ts` | 可延伸符号（如括号、箭头）处理 |
| 单位 | `src/units.ts` | validUnit()、CSS单位转换、makeEm() |
| 间距数据 | `src/spacingData.ts` | TeX间距规则数据 |
| 符号定义 | `src/symbols.ts` | 符号分组（bin/rel/open/close/punct/inner/ord） |
| 原子类型 | `src/atoms.ts` | atom/non-atom常量、isAtom类型守卫 |
| 字体类型 | `src/types/fonts.ts` | MathFont/TextFont/FontWeight/FontShape类型 |

### 工具

| 文件 | 路径 | 职责 |
|------|------|------|
| 工具函数 | `src/utils.ts` | escape/hyphenate/protocolFromUrl等 |
| SVG几何 | `src/svgGeometry.ts` | SVG路径数据（弧形/花括号等） |
| Unicode脚本 | `src/unicodeScripts.ts` | supportedCodepoint()、scriptFromCodepoint() |
| Unicode重音 | `src/unicodeAccents.js` | Unicode组合重音映射 |
| Unicode符号 | `src/unicodeSymbols.js` | Unicode符号规范化映射 |
| Unicode上下标 | `src/unicodeSupOrSub.ts` | Unicode上下标字符处理 |
| 宽字符 | `src/wide-character.ts` | 全角/宽字符处理 |

### 样式表

| 文件 | 路径 | 职责 |
|------|------|------|
| 主样式 | `src/styles/katex.scss` | KaTeX核心CSS样式 |
| 字体样式 | `src/styles/fonts.scss` | @font-face字体声明 |
| 交换样式 | `src/styles/katex-swap.scss` | 字体加载优化样式 |

### 扩展模块（contrib/）

| 文件 | 路径 | 职责 |
|------|------|------|
| 自动渲染 | `contrib/auto-render/auto-render.ts` | renderMathInElement()、DOM扫描渲染 |
| 分隔符分割 | `contrib/auto-render/splitAtDelimiters.ts` | 数学分隔符识别与文本分割 |
| 复制TeX | `contrib/copy-tex/copy-tex.ts` | 复制时输出LaTeX源码 |
| 化学扩展 | `contrib/mhchem/mhchem.js` | mhchem化学方程式支持 |
| 无障碍字符串 | `contrib/render-a11y-string/render-a11y-string.ts` | 生成无障碍文本表示 |
| 脚本类型 | `contrib/mathtex-script-type/mathtex-script-type.js` | script[type=math/tex]自动渲染 |
