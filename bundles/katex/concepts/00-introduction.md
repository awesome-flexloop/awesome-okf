---
type: Concept
title: KaTeX 简介
description: KaTeX 是一个快速的 Web 数学排版库，将 LaTeX 数学表达式渲染为 HTML+MathML，支持服务端渲染和浏览器端渲染。
tags: [katex, introduction, math, latex]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-02-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 什么是 KaTeX

KaTeX（/ˈkeɪtɛk/，发音类似 "Kay-Tek"）是一个用于 Web 的数学公式排版库。它将 LaTeX 语法书写的数学表达式解析并渲染为浏览器可显示的 HTML 和 MathML 标记，实现接近印刷级质量的数学公式展示。

KaTeX 的核心特点：

- **速度快**：采用同步渲染模型，不需要布局回流即可完成公式排版
- **无依赖**：运行时仅依赖 commander（CLI用），浏览器端使用零依赖
- **输出质量高**：输出结果同时包含 HTML（视觉呈现）和 MathML（语义标记），兼顾视觉效果与无障碍访问
- **服务端渲染支持**：同一套代码既可在浏览器中操作真实 DOM，也可在 Node.js 中生成 HTML 字符串
- **可扩展**：通过 `__defineFunction`、`__defineMacro`、`__defineSymbol` 等 API 支持自定义命令扩展

## 版本与许可

- 当前稳定版本：**0.18.4**
- 许可证：**MIT License**（可自由商用）
- 包管理器：项目本身使用 pnpm 管理依赖，发布到 npm 供所有包管理器使用
- 仓库：[https://github.com/KaTeX/KaTeX](https://github.com/KaTeX/KaTeX)
- 官网：[https://katex.org](https://katex.org)

## KaTeX 能做什么

KaTeX 支持大部分 LaTeX 数学模式命令，包括：

- 基础数学运算：分数、上下标、根号、求和、积分
- 矩阵与表格：`matrix`、`pmatrix`、`array` 等
- 运算符：希腊字母、二元运算符、关系运算符、箭头
- 排版控制：字体切换、颜色、间距、字号
- 文本嵌入：`\text{}` 命令在数学模式中插入普通文本
- 自定义宏：通过配置或扩展 API 添加新命令

KaTeX **不支持** LaTeX 的全部功能（如 TikZ 绘图、复杂页面布局），它专注于数学模式的排版。

## 在项目中的位置

KaTeX 的源码结构清晰地划分为几个层次：

1. **词法层（Lexer/Token）**：将输入字符串切分为 Token 流
2. **宏展开层（MacroExpander）**：展开用户定义的和内置的宏
3. **解析层（Parser）**：将 Token 流解析为抽象语法树（ParseNode 树）
4. **构建层（buildHTML/buildMathML）**：将解析树转换为虚拟 DOM 树
5. **输出层**：虚拟 DOM 序列化为 HTML 字符串或真实 DOM 节点

理解这个分层架构是掌握 KaTeX 的关键。详见 [架构总览](/concepts/02-architecture-overview.md)。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [配置系统](/concepts/10-settings-options.md)
