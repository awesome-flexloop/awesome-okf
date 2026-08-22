---
type: Index
title: KaTeX
description: KaTeX 是一个快速的 Web 数学排版库，将 LaTeX 数学表达式渲染为 HTML+MathML。本bundle基于源码v0.18.4深度分析，覆盖核心架构、渲染管线、扩展机制和实战示例。
tags: [katex, math, latex, rendering, web]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:40:00+08:00 }
status: stable
stale_after: 2027-08-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## KaTeX Bundle

本bundle提供 KaTeX v0.18.4 的源码级学习文档，基于七概念方法论（R→I→E→V→C链路）从源码提炼核心知识，覆盖从入门使用到源码扩展的完整学习路径。

## 快速导航

### 入门

| 文档 | 内容 |
|------|------|
| [KaTeX 简介](/concepts/00-introduction.md) | KaTeX 是什么、核心特点、版本许可、能力边界 |
| [快速开始](/concepts/01-getting-started.md) | 安装、CDN、核心API（render/renderToString）、配置选项、第一个示例 |

### 核心架构

| 文档 | 内容 |
|------|------|
| [架构总览](/concepts/02-architecture-overview.md) | 三层消化管模型（Lexer→MacroExpander→Parser）、注册表驱动设计、双输出无障碍 |
| [词法分析器（Lexer）](/concepts/03-lexer.md) | 正则分词、Token结构、catcodes、\verb特殊处理 |
| [宏展开器（MacroExpander）](/concepts/04-macro-expander.md) | Token栈、展开循环、参数消费、Namespace分组作用域 |
| [解析器（Parser）](/concepts/05-parser.md) | 递归下降解析、atom/上下标处理、函数调度、模式切换 |
| [渲染管线](/concepts/06-render-pipeline.md) | buildTree/buildHTML/buildMathML、HTML+MathML双输出、displayWrap |
| [虚拟DOM树](/concepts/07-dom-tree.md) | Span/Anchor/SymbolNode/SvgNode、toNode/toMarkup双输出 |

### 扩展机制

| 文档 | 内容 |
|------|------|
| [函数注册表](/concepts/08-function-registry.md) | defineFunction三要素（handler/htmlBuilder/mathmlBuilder）、FunctionSpec、参数类型 |
| [宏系统](/concepts/09-macro-system.md) | 内置宏、自定义宏（settings.macros/__defineMacro）、\newcommand/\def |
| [配置系统](/concepts/10-settings-options.md) | Settings/Options双层配置、strict/trust模式、不可变状态传递 |
| [样式系统](/concepts/11-style-system.md) | 8种TeX样式、sup/sub/fracNum/fracDen转换、数学原子类、间距规则 |
| [字体与度量](/concepts/12-font-metrics.md) | 字体族组织、fontMetrics、Unicode支持、字号系统 |

### 扩展模块

| 文档 | 内容 |
|------|------|
| [自动渲染扩展](/concepts/13-auto-render.md) | auto-render扩展、renderMathInElement()、分隔符配置 |
| [贡献扩展模块](/concepts/14-contrib-extensions.md) | copy-tex、mhchem、render-a11y-string、mathtex-script-type |

### 示例

| 文档 | 内容 |
|------|------|
| [基础渲染示例](/examples/basic-render.md) | render/renderToString用法、行内/显示模式、常见公式（分数/积分/矩阵/希腊字母） |
| [自定义宏示例](/examples/custom-macros.md) | settings.macros别名、带参数宏、函数宏、全局宏注册、物理/数学宏集合 |
| [自定义扩展示例](/examples/custom-extension.md) | __defineFunction添加新命令、\circled/\eval/\checkbox实战 |
| [自动渲染使用示例](/examples/auto-render-usage.md) | 分隔符配置、忽略元素、preProcess预处理、动态内容/AJAX处理、Markdown结合 |
| [错误处理示例](/examples/error-handling.md) | throwOnError/errorColor、strict模式、ParseError、trust安全、安全封装函数 |

### 参考信源

| 文档 | 内容 |
|------|------|
| [KaTeX 源码信源](/references/katex-source.md) | 源码仓库核心文件索引（入口/词法解析/注册系统/渲染/样式字体/扩展模块） |

## 学习路径推荐

### 路径1：使用KaTeX（不读源码）

```
00-introduction → 01-getting-started → examples/basic-render
                                         ↓
                                  examples/error-handling
                                         ↓
                            (如需自动渲染) → 13-auto-render → examples/auto-render-usage
                            (如需自定义宏) → examples/custom-macros
```

### 路径2：理解KaTeX架构（读源码）

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

### 路径3：扩展KaTeX（自定义命令）

```
08-function-registry → examples/custom-extension
       ↑                      ↓
09-macro-system      （了解虚拟DOM）→ 07-dom-tree
       ↑                      ↓
examples/custom-macros    （了解Options）→ 10-settings-options
```

## 核心洞察（源码学习关键发现）

1. **TeX消化管隐喻**：Lexer(mouth)→MacroExpander(gullet)→Parser(stomach)三层分离，不是过度设计，而是处理宏动态改变语法的必要架构
2. **注册表驱动架构**：核心引擎仅~2000行（空壳），43个函数文件通过defineFunction插件式注册，学习KaTeX应先掌握注册表机制而非逐个读函数
3. **不可变Options传递**：Options所有with*/having*方法返回新实例，避免子树污染父节点状态，是CSS继承在JS中的正确实现
4. **HTML+MathML双输出**：MathML在前供屏幕阅读器，HTML在后供视觉呈现，自定义函数必须同时提供htmlBuilder和mathmlBuilder
5. **虚拟DOM双输出**：虚拟节点通过toNode()输出真实DOM、toMarkup()输出HTML字符串，是SSR和浏览器渲染统一的基础

## 版本信息

- **KaTeX版本**：0.18.4
- **文档生成日期**：2026-08-22
- **许可证**：MIT
- **官方仓库**：https://github.com/KaTeX/KaTeX
- **官方网站**：https://katex.org
