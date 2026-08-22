---
type: Index
title: Examples 索引
description: jupyter-renderers 示例教程索引
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# Examples 示例教程

| 编号 | 文档 | 类型 | 难度 | 核心知识点 |
|------|------|------|------|-----------|
| 01 | [开发自定义 MIME 渲染器](01-custom-mime-renderer.md) | HowTo | ⭐⭐ | MIME 渲染器四要素、CSS样式、Python打包、预构建扩展 |
| 02 | [自定义 LaTeX 排版器](02-custom-latex-typesetter.md) | HowTo | ⭐⭐⭐ | ILatexTypesetter、JupyterFrontEndPlugin、异步加载、disabledExtensions互斥 |

## 前置知识

- 阅读 [Concepts 02 - MIME 渲染器模式](../concepts/02-mime-renderer-pattern.md) 理解四要素模式
- 阅读 [Concepts 03 - 扩展类型](../concepts/03-extension-types.md) 理解 MIME 渲染器 vs 应用扩展的区别
- 阅读 [Concepts 08 - Python 打包](../concepts/08-python-packaging.md) 理解预构建扩展打包机制
- 参考 [References - IRenderMime API](../references/rendermime-interfaces-api.md) 查阅接口定义
