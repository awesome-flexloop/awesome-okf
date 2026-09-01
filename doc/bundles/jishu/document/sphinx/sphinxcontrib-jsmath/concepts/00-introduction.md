---
type: Concept
title: sphinxcontrib-jsmath 简介
description: sphinxcontrib-jsmath 是什么、jsMath 渲染器的工作原理、与其他数学渲染方案的对比
tags: [sphinxcontrib-jsmath, introduction, sphinx, math, jsmath, html]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-source
    resource: /references/jsmath-source.md
    title: sphinxcontrib-jsmath 源码信源登记
---

# sphinxcontrib-jsmath 简介

## 什么是 sphinxcontrib-jsmath

**sphinxcontrib-jsmath** 是 Sphinx 官方维护的一个扩展，它通过 [jsMath](http://www.math.union.edu/~dpvc/jsmath/) JavaScript 库在 HTML 输出中渲染数学公式。jsMath 是早期的浏览器端数学公式渲染方案，它使用 TeX 字体在网页中显示数学符号，无需安装额外软件即可在浏览器中查看数学公式。

这个扩展是 Sphinx 内置数学渲染能力的"外置化"产物——在 2019 年之前，jsMath 渲染器直接内置在 Sphinx 核心中。从 Sphinx 1.8 开始，官方将各种 HTML math renderer 拆分为独立的 `sphinxcontrib-*` 包，sphinxcontrib-jsmath 就是从 Sphinx 核心中拆分出来的第一个（参见 CHANGES.rst 中 "copied from sphinx package" 的记录）。

## 核心定位

sphinxcontrib-jsmath 在 Sphinx 数学渲染生态中扮演"轻量级浏览器端渲染"角色：

- **不依赖服务端渲染**：数学公式以原始 TeX/LaTeX 源码嵌入 HTML，由浏览器端 jsMath 脚本渲染
- **不依赖 MathJax/KaTeX CDN**：使用自托管的 jsMath 脚本和字体文件
- **极简实现**：整个扩展仅 88 行 Python 代码（核心模块 `__init__.py`），无运行时依赖
- **按需加载**：文档中无数学公式时，jsMath 脚本不会被引入页面

## 与其他数学渲染方案对比

Sphinx 支持多种 HTML 数学渲染方案，sphinxcontrib-jsmath 是其中之一：

| 渲染器 | 包名 | 渲染方式 | 依赖 | 特点 |
|--------|------|---------|------|------|
| **jsMath** | sphinxcontrib-jsmath | 浏览器端 JS + TeX 字体 | 需自托管 jsMath 脚本和字体 | 轻量、无外部CDN依赖、渲染效果较旧 |
| **MathJax** | 内置（sphinx.ext.mathjax） | 浏览器端 JS | 默认从 CDN 加载 MathJax | 渲染质量高、功能全面、需网络或本地部署 |
| **KaTeX** | 第三方扩展 | 浏览器端 JS | KaTeX 库 | 渲染速度极快、功能子集 |
| **imgmath** | 内置（sphinx.ext.imgmath） | 服务端生成图片 | LaTeX + dvipng/dvisvgm | 输出为图片、无JS依赖、需要LaTeX环境 |
| **MathJax v3** | sphinxcontrib-mathjax（未来） | 浏览器端 JS | MathJax v3 | MathJax 最新版本 |

## jsMath 的工作原理

jsMath 的渲染流程：

1. Sphinx 构建时，数学公式以原始 LaTeX 源码嵌入 HTML（包裹在 `<span class="math">` 或 `<div class="math">` 中）
2. 页面加载时，jsMath.js 脚本扫描页面中所有 `class="math"` 的元素
3. jsMath 解析 LaTeX 源码，使用 TeX 字体在浏览器中排版数学公式
4. 最终用户看到排版精美的数学公式

```
rst 源文件:  .. math:: E = mc^2
                    ↓ Sphinx 构建
HTML 输出:   <div class="math notranslate nohighlight">E = mc^2</div>
                    ↓ 浏览器加载 jsmath.js
页面显示:    渲染后的 "E = mc²" 数学公式
```

## 为什么了解这个扩展

即使你不使用 jsMath（大多数现代项目使用 MathJax），学习 sphinxcontrib-jsmath 仍有重要价值：

1. **最小 Sphinx 扩展示范**：88 行代码完整实现了一个 math renderer 扩展，是学习 Sphinx 扩展开发的绝佳起点
2. **理解 HTML 访问者模式**：展示了如何通过 visitor 方法拦截 docutils 节点输出
3. **理解事件驱动的资源加载**：`env-updated` 事件 + 条件检查实现按需资源加载
4. **Sphinx 架构知识**：理解 `add_html_math_renderer` API 和 MathDomain 协作机制

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [扩展注册与 setup 函数](02-setup-and-registration.md)
- [数学节点访问者](03-math-node-visitors.md)
- [智能JS加载机制](04-smart-js-loading.md)
- [源码信源登记](../references/jsmath-source.md)
