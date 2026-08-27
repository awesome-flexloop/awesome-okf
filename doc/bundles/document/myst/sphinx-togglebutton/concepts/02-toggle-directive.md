---
type: Concept
title: toggle 指令详解
description: ".. toggle:: 指令的语法、选项、DOM 结构及其与 admonition 折叠的区别"
tags:
- sphinx
- toggle
- directive
- admonition
- dom
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T03:06:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: togglebutton-source
  resource: /references/togglebutton-source.md
  title: sphinx-togglebutton 源码路径映射
---

# toggle 指令详解

`.. toggle::` 指令是 sphinx-togglebutton 提供的显式折叠指令，用于将任意 RST 内容包装为可折叠区域。

## 指令语法

```rst
.. toggle:: [可选标题文本]
   :show:
   :id: <自定义ID>

   折叠内容……
```

### 参数

| 参数 | 必需 | 说明 |
|------|------|------|
| 可选标题文本 | 否 | 折叠区域的摘要文本（注意：此参数当前不显示为标题，仅作占位） |

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:show:` | flag | 默认展开内容（无此选项则默认折叠） |
| `:id:` | string | 为折叠容器指定自定义 HTML id |

## 工作原理

### Python 端输出

Toggle 指令在 Python 端生成一个 `<div class="toggle">` 容器（若有 `:show:` 则为 `<div class="toggle toggle-shown">`），内容通过 `nested_parse` 解析为子节点。Python 端不做任何隐藏处理，内容完整输出到 HTML。

### JS 端处理

前端 JavaScript 在 `DOMContentLoaded` 时执行：

1. **非 admonition 的 `.toggle` 元素**：JS 将其包装为 `<details class="toggle-details">` 结构，前面插入 `<summary>` 元素包含 chevron 图标和提示文本
2. **`.admonition.dropdown` 元素**：在 `.admonition-title` 内插入 `<button class="toggle-button">`，标题栏整体可点击

### 两种折叠模式对比

| 特性 | admonition dropdown | toggle 指令（非 admonition） |
|------|---------------------|---------------------------|
| DOM 策略 | CSS 类 `toggle-hidden` 切换 | 原生 `<details>/<summary>` |
| 触发方式 | `:class: dropdown` | `.. toggle::` 指令 |
| 点击区域 | 整个标题栏 | summary 区域 |
| 无 JS 降级 | 内容始终可见 | 内容始终可见（details 默认为 open） |
| 无障碍 | ARIA 属性 | 原生 details 无障碍支持 |
| 适用场景 | 提示框、警告框 | 任意内容块（图片、代码、表格组合） |

## 使用示例

### 折叠答案区域

```rst
以下是一道思考题：

什么是 Python 的 GIL？

.. toggle::
    :show:

    **答案**：GIL（Global Interpreter Lock，全局解释器锁）是 CPython 中的
    一个互斥锁，确保同一时刻只有一个线程执行 Python 字节码。
```

### 折叠代码示例

```rst
.. toggle::

    点击展开完整代码：

    .. code-block:: python

        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
```

### 带自定义 ID

```rst
.. toggle::
    :id: my-special-toggle

    这个折叠区域可以通过 #my-special-toggle 锚定。
```

## 相关概念

- [快速开始](01-getting-started.md)
- [配置项参考](03-configuration.md)
- [基础使用示例](../examples/basic-usage.md)
