---
type: Index
title: KaTeX
okf_version: "0.2"
description: KaTeX 是一个快速的 Web 数学排版库，将 LaTeX 数学表达式渲染为 HTML+MathML。本bundle基于源码v0.18.4深度分析并融合官网17页用户文档，覆盖核心架构、渲染管线、扩展机制、安装运行时、CLI、安全、排障迁移和实战示例。
tags: [katex, math, latex, rendering, web]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:40:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:40:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## KaTeX Bundle

本bundle提供 KaTeX v0.18.4 的源码级学习文档，基于七概念方法论（R→I→E→V→C链路）从源码提炼核心知识，并系统融合官网 17 个公开页面的用户文档，形成"会用 + 懂原理 + 能扩展 + 可排障"的完整中文学习路径。共收录 24 篇概念文档、8 篇实战示例和 2 篇信源登记。

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

### 安装与运行

| 文档 | 内容 |
|------|------|
| [安装与运行时](/concepts/15-installation-and-runtime.md) | 浏览器CDN/自托管、Node/npm/pnpm/Deno、ESM/CJS、CSS与字体路径、源码构建 |
| [命令行接口](/concepts/16-command-line.md) | CLI输入输出、18个选项、与Settings映射、宏文件 |
| [字体与单位](/concepts/17-fonts-and-units.md) | font-display策略、TeX单位换算、字体自托管、1.21em缩放 |

### 安全与参考

| 文档 | 内容 |
|------|------|
| [安全与错误处理](/concepts/18-security-and-errors.md) | maxSize/maxExpand/trust三层防御、HTML消毒、ParseError、错误消息转义 |
| [支持的函数](/concepts/19-supported-functions.md) | 官网14个分类的TeX函数体系、HTML扩展安全要求 |
| [支持表](/concepts/20-support-table.md) | 字母序支持表、Detexify手写识别、源码溯源 |
| [常见问题](/concepts/21-common-issues.md) | DOCTYPE/quirks mode、智能引号、align vs aligned、MathJax差异、CSS排障 |
| [版本迁移](/concepts/22-migration.md) | v0.13-v0.18迁移要点：CSS类名前缀、API变更、路径调整 |
| [生态与版本](/concepts/23-ecosystem-and-versions.md) | Users列表、版本说明、第三方库索引（React/Vue/Angular/移动端等） |

### 示例

| 文档 | 内容 |
|------|------|
| [基础渲染示例](/examples/basic-render.md) | render/renderToString用法、行内/显示模式、常见公式（分数/积分/矩阵/希腊字母） |
| [自定义宏示例](/examples/custom-macros.md) | settings.macros别名、带参数宏、函数宏、全局宏注册、物理/数学宏集合 |
| [自定义扩展示例](/examples/custom-extension.md) | __defineFunction添加新命令、\circled/\eval/\checkbox实战 |
| [自动渲染使用示例](/examples/auto-render-usage.md) | 分隔符配置、忽略元素、preProcess预处理、动态内容/AJAX处理、Markdown结合 |
| [错误处理示例](/examples/error-handling.md) | throwOnError/errorColor、strict模式、ParseError、trust安全、安全封装函数 |
| [Node.js 服务端渲染示例](/examples/node-ssr.md) | Node.js（CJS/ESM）与 Deno 中 renderToString、CSS/字体引入、HTML 页面组装、mhchem 扩展、预渲染缓存 |
| [安全与信任配置示例](/examples/security-trust.md) | 不可信输入配置、trust 函数策略、maxSize/maxExpand 防御、错误消息 HTML 转义、输出消毒白名单、持久宏隔离 |
| [命令行渲染示例](/examples/cli-render.md) | npx katex 从 stdin 到 stdout、--input/--output/--display-mode/--macro/--macro-file/--no-throw-on-error、批量处理 |

### 参考信源

| 文档 | 内容 |
|------|------|
| [KaTeX 源码信源](/references/katex-source.md) | v0.18.4 源码核心文件索引，含官网页面对应关系 |
| [KaTeX 官网信源](/references/katex-website.md) | 官网 17 个页面登记：稳定 ID、URL、标题、用途与引用提示 |

## 学习路径推荐

### 路径1：使用 KaTeX（集成与渲染）

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

### 路径2：理解 KaTeX 架构（读源码）

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

### 路径3：扩展 KaTeX（自定义命令）

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

### 路径4：升级排障与生态选型

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

## 核心洞察（源码学习与官网融合关键发现）

1. **TeX消化管隐喻**：Lexer(mouth)→MacroExpander(gullet)→Parser(stomach)三层分离，不是过度设计，而是处理宏动态改变语法的必要架构
2. **注册表驱动架构**：核心引擎仅~2000行（空壳），43个函数文件通过defineFunction插件式注册，学习KaTeX应先掌握注册表机制而非逐个读函数
3. **不可变Options传递**：Options所有with*/having*方法返回新实例，避免子树污染父节点状态，是CSS继承在JS中的正确实现
4. **HTML+MathML双输出**：MathML在前供屏幕阅读器，HTML在后供视觉呈现，自定义函数必须同时提供htmlBuilder和mathmlBuilder
5. **虚拟DOM双输出**：虚拟节点通过toNode()输出真实DOM、toMarkup()输出HTML字符串，是SSR和浏览器渲染统一的基础
6. **三层安全防御纵深**：maxSize 防超大宽高视觉攻击、maxExpand（默认1000）防无限宏循环 DoS、trust（默认false）控制外部资源/HTML 属性命令；处理不可信输入须三者配合并对输出做 HTML 消毒
7. **持久宏的有状态设计**：render/renderToString 表面是无状态纯函数，但共享 macros 对象会被 \gdef 修改实现宏持久化；多用户/多消息场景必须为每条消息创建独立 macros 对象
8. **官网与源码双信源分层**：官网说明"怎么用"和默认值（如 strict 默认 "warn"、trust 默认 false），源码揭示"内部如何工作"；部分默认值源码未显式标注，必须双信源交叉验证
9. **版本标注不一致**：官网 Versions 页标注 0.16.47，而文档页 CDN 引用 0.18.4；本 bundle 以源码 package.json 的 v0.18.4 为权威基准

## 版本信息

- **KaTeX版本**：0.18.4
- **文档生成日期**：2026-08-23
- **许可证**：MIT
- **官方仓库**：https://github.com/KaTeX/KaTeX
- **官方网站**：https://katex.org

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
