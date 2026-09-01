---
type: Concept
title: 分组标签与代码标签
description: group-tab 的跨页面同步机制、code-tab 的多语言代码示例用法，以及 sessionStorage 状态持久化原理
tags: [sphinx, tabs, group-tab, code-tab, sessionstorage, sync]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:28:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# 分组标签与代码标签

## group-tab：跨页面标签同步

`.. group-tab::` 是 `.. tab::` 的子类，增加了跨页面选中状态同步功能。当用户在一个页面选择某个分组标签后，同一浏览器会话中其他页面的同名分组标签也会自动选中。

### 使用场景

最典型的场景是多语言/多操作系统文档：用户选择"Python"或"Linux"后，整个文档站点保持一致选择。

```rst
.. tabs::

   .. group-tab:: Linux

      .. code-block:: bash

         sudo apt install python3

   .. group-tab:: macOS

      .. code-block:: bash

         brew install python

   .. group-tab:: Windows

      .. code-block:: bat

         choco install python
```

### 同步原理

1. **确定性 ID**：组名通过 `base64.b64encode(group_name.encode()).decode()` 编码为 tab_id，确保同名标签在所有页面具有相同的 `name` 属性
2. **点击持久化**：点击 group-tab 时，将组名存入 `sessionStorage['sphinx-tabs-last-selected']`
3. **页面加载恢复**：DOMContentLoaded 时检查 sessionStorage，调用 `selectNamedTabs()` 选中同名标签
4. **实时同步**：点击时调用 `selectNamedTabs(name, this.id)` 同步当前页所有同名标签

### sessionStorage vs localStorage

使用 sessionStorage 而非 localStorage 意味着：
- 同一标签页内导航保持选择
- 关闭标签页后重置
- 不同标签页/窗口独立

## code-tab：多语言代码标签页

`.. code-tab::` 继承自 group-tab，专为多语言代码示例设计。它自动：
- 识别 Pygments lexer 并应用语法高亮
- 用 lexer 正式名称作为标签标题（可自定义）
- 继承跨页同步能力

### 基本用法

```rst
.. tabs::

   .. code-tab:: python

      def hello():
          print("Hello, World!")

   .. code-tab:: javascript

      function hello() {
          console.log("Hello, World!");
      }

   .. code-tab:: r

      hello <- function() {
          cat("Hello, World!\n")
      }
```

### 自定义标签名

第二个参数可覆盖自动检测的语言名称：

```rst
.. code-tab:: python3 Python 3

   print("Hello from Python 3")
```

### 带行号和高亮

支持所有 code-block 选项：

```rst
.. code-tab:: python
   :linenos:
   :emphasize-lines: 2

   def fibonacci(n):
       if n <= 1:        # 高亮此行
           return n
       return fibonacci(n-1) + fibonacci(n-2)
```

### Lexer 名称映射

code-tab 内置完整的 Pygments lexer 映射表（`LEXER_MAP`），通过遍历 `pygments.lexers.get_all_lexers()` 构建。常见别名映射：

| 短名 | 正式名称 |
|------|---------|
| `py`, `python` | Python |
| `js`, `javascript` | JavaScript |
| `rb`, `ruby` | Ruby |
| `sh`, `bash` | Bash |
| `md`, `markdown` | Markdown |

如果指定了未知 lexer，抛出 `ValueError: Lexer not implemented: {name}`。

## 普通 tab 与 group-tab/code-tab 的选择

| 场景 | 推荐指令 | 原因 |
|------|---------|------|
| 页面内独立标签切换 | `tab` | 不需要跨页同步，避免 sessionStorage 干扰 |
| 多页面统一语言/OS选择 | `group-tab` | 用户偏好记忆 |
| 多语言代码示例 | `code-tab` | 自动语法高亮+跨页同步 |

## 相关概念

- [四个指令详解](02-directives.md)
- [配置项参考](04-configuration.md)
- [多语言代码示例](../examples/code-tabs.md)
- [分组同步配置示例](../examples/group-tabs-sync.md)
