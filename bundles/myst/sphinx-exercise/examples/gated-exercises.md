---
type: Example
title: 门控练习包裹内容
description: 使用 exercise-start/end 和 solution-start/end 门控指令对包裹任意 RST 内容，无需缩进嵌套
tags: [sphinx, exercise, gated, example, wrap, no-indent]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: exercise-source
    resource: /references/exercise-source.md
    title: sphinx-exercise 源码路径映射
---

# 门控练习包裹内容

## 包裹代码块和说明

使用门控指令，练习内容不需要额外缩进：

```rst
.. exercise-start:: 数据分析练习
   :label: ex-data
   :nonumber:

在这个练习中，你将使用 pandas 分析 CSV 数据。

首先导入必要的库：

.. code-block:: python

   import pandas as pd
   import numpy as np

然后读取数据：

.. code-block:: python

   df = pd.read_csv("data.csv")
   print(df.head())

.. exercise-end::
```

## 门控解答

```rst
.. solution-start:: ex-data

解答步骤如下：

.. code-block:: python

   import pandas as pd

   df = pd.read_csv("data.csv")

   # 查看基本统计
   print(df.describe())

   # 分组聚合
   result = df.groupby("category")["value"].agg(["mean", "sum"])
   print(result)

.. note::

   注意处理缺失值。

.. solution-end::
```

## 对比自包含与门控风格

**自包含风格（需要缩进）**：

```rst
.. exercise::

   这里的每一行都需要缩进。

   .. code-block:: python

      # 代码块也要嵌套缩进
      print("hello")
```

**门控风格（无需缩进）**：

```rst
.. exercise-start::

这里不需要额外缩进。

.. code-block:: python

   print("hello")

.. exercise-end::
```

## 包裹表格和列表

门控指令可以自然包含表格等复杂结构：

```rst
.. exercise-start:: 表格分析
   :label: ex-table

请分析下表中的数据并回答问题：

.. list-table:: 销售数据
   :header-rows: 1

   * - 月份
     - 销售额
     - 增长率
   * - 1月
     - 100万
     - +5%
   * - 2月
     - 120万
     - +20%

问题：哪个月增长率最高？

.. exercise-end::

.. solution-start:: ex-table

2月增长率最高，为 +20%。

计算方法：(120 - 100) / 100 = 20%

.. solution-end::
```

## 相关示例

- [基础练习与解答](/examples/basic-exercise.md)
- [教师版/学生版配置](/examples/hide-solutions.md)

## 相关概念

- [门控指令](/concepts/04-gated-directives.md)
- [练习指令详解](/concepts/02-exercise-directive.md)
