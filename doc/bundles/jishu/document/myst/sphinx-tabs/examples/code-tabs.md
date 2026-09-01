---
type: Example
title: 多语言代码标签页
description: 使用 code-tab 指令创建多语言代码示例，包括自定义标签名、行号高亮和跨页同步
tags: [sphinx, tabs, code-tab, example, multilingual, syntax-highlighting]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:36:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# 多语言代码标签页

## 三语言 Hello World

```rst
.. tabs::

   .. code-tab:: python

      print("Hello, World!")

   .. code-tab:: javascript

      console.log("Hello, World!");

   .. code-tab:: r

      cat("Hello, World!\n")
```

每个标签显示语言全称（Python / JavaScript / R），自动语法高亮。由于继承自 group-tab，用户选择 Python 后，其他页面的 code-tab 也会自动切换到 Python。

## 带行号和高亮行

```rst
.. tabs::

   .. code-tab:: python
      :linenos:
      :emphasize-lines: 2

      def greet(name):
          message = f"Hello, {name}!"  # 高亮此行
          return message

      print(greet("World"))

   .. code-tab:: javascript
      :linenos:
      :emphasize-lines: 2

      function greet(name) {
          const message = `Hello, ${name}!`;  // 高亮此行
          return message;
      }

      console.log(greet("World"));
```

## 自定义标签名称

第二个参数可以覆盖自动检测的语言名：

```rst
.. tabs::

   .. code-tab:: python3 Python 3

      # Python 3.10+ 特性
      def greet(name: str) -> str:
          return f"Hello, {name}!"

   .. code-tab:: py Python 2 (兼容)

      # Python 2.7 兼容写法
      def greet(name):
          return "Hello, %s!" % name
```

## 数据处理多语言对比

```rst
.. tabs::

   .. code-tab:: python

      import pandas as pd

      df = pd.read_csv("data.csv")
      summary = df.groupby("category")["value"].mean()
      print(summary)

   .. code-tab:: r

      library(dplyr)

      df <- read.csv("data.csv")
      summary <- df %>%
        group_by(category) %>%
        summarise(mean_value = mean(value))
      print(summary)

   .. code-tab:: julia

      using DataFrames, CSV

      df = CSV.read("data.csv", DataFrame)
      summary = combine(groupby(df, :category), :value => mean)
      println(summary)
```

## 常见 Lexer 短名

| 短名 | 显示名称 |
|------|---------|
| `python`, `py` | Python |
| `javascript`, `js` | JavaScript |
| `typescript`, `ts` | TypeScript |
| `r` | R |
| `julia` | Julia |
| `bash`, `sh` | Bash |
| `java` | Java |
| `cpp`, `c++` | C++ |
| `rust`, `rs` | Rust |
| `go` | Go |

## 相关示例

- [基础标签页](basic-tabs.md)
- [分组标签同步](group-tabs-sync.md)

## 相关概念

- [分组标签与代码标签](../concepts/03-group-and-code-tabs.md)
- [快速开始](../concepts/01-getting-started.md)
