---
type: concept
title: "表格"
description: "table、list-table、csv-table三种表格指令的语法和用法，包括Markdown表格、列表表格和CSV表格"
tags: [myst-syntax, table, list-table, csv-table, csv]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/table.ts"
    facts: [F-S020, F-S021, F-S022]
---

# 表格

MyST 提供三种表格指令：`table`（包裹 Markdown 表格）、`list-table`（列表定义表格）和 `csv-table`（CSV 数据表格）。

## Table 指令

`table` 指令包裹标准 Markdown 表格，提供标题、编号和样式选项：

````markdown
:::{table} 表格标题
:label: tbl-data
:align: center

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A   | B   | C   |
| D   | E   | F   |
:::
````

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| caption | myst | 可选表格标题（解析为 MyST） |

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:class:` | String | CSS 类名。`full-width` 在 LaTeX 中跨双栏 |
| `:align:` | String | 对齐方式：left/center/right |
| `:label:` | String | 交叉引用标签 |

Table 内的 Markdown 表格使用标准 GFM 管道表格语法。有标题时表格自动编号（Table 1、Table 2...）。

## List-Table 指令

`list-table` 使用嵌套列表定义表格，适合表格内容较复杂（包含多行段落、列表等）的场景：

````markdown
:::{list-table} 列表定义的表格
:header-rows: 1

*   - 姓名
    - 年龄
    - 城市
*   - 张三
    - 25
    - 北京
*   - 李四
    - 30
    - 上海
:::
````

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:header-rows:` | Number | 表头行数（默认 0） |
| `:class:` | String | CSS 类名 |
| `:align:` | String | left/center/right |

### 语法规则

list-table 的 body **必须**是两层嵌套的列表：
- 外层列表的每一项是一行
- 内层列表的每一项是一个单元格
- 单元格内可以包含任意 MyST 内容（段落、列表、代码等）

验证逻辑：
1. body 必须有且仅有一个顶层列表
2. 每个列表项必须恰好包含一个子列表
3. 违反规则会产生错误，表格不渲染

```markdown
:::{list-table} 复杂内容表格
:header-rows: 1

*   - 功能
    - 说明
    - 示例
*   - **加粗**
    - 单元格内可以有
      - 嵌套列表
      - 多段内容
    - `code`
:::
```

## CSV-Table 指令

`csv-table` 从 CSV 数据创建表格，适合从外部数据源导入或程序生成的表格：

````markdown
:::{csv-table} CSV数据表格
:header-rows: 1

姓名,年龄,城市
张三,25,北京
李四,30,上海
王五,28,广州
:::
````

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:header:` | String | 补充表头行（独立于 header-rows） |
| `:header-rows:` | Number | body 中的表头行数 |
| `:delim:` | String | 分隔符，默认 `,`；特殊值 `tab`/`space` |
| `:keepspace:` | Boolean | 保留分隔符后的空格 |
| `:quote:` | String | 引号字符（默认 `"`） |
| `:escape:` | String | 转义字符（默认 `"`） |
| `:class:` | String | CSS 类名 |
| `:align:` | String | left/center/right |

### 分隔符选项

```markdown
:::{csv-table} Tab分隔表格
:delim: tab
:header-rows: 1

姓名	年龄	城市
张三	25	北京
:::
```

```markdown
:::{csv-table} 空格分隔表格
:delim: space

A B C
1 2 3
:::
```

### MyST 内容单元格

csv-table 的每个单元格通过 `ctx.parseMyst()` 递归解析，因此单元格内可以使用 MyST 语法：

```markdown
:::{csv-table} 带格式的表格
:header-rows: 1

功能,语法,示例
**加粗**,`**text**`,**粗体**
[链接](https://example.com),`[text](url)`,[示例](https://example.com)
:::
```

### 引号和转义

包含逗号的字段使用引号包裹，引号内的引号用双引号转义：

```markdown
:::{csv-table}
:header-rows: 1

产品,描述
"产品A, 升级版","包含功能1, 功能2, 功能3"
"带""引号""的产品","描述中包含""引号"""
:::
```

## 三种表格对比

| 特征 | table | list-table | csv-table |
|------|-------|-----------|-----------|
| 数据来源 | Markdown 管道表格 | 嵌套列表 | CSV 字符串 |
| 单元格富文本 | ✅ | ✅（最强） | ✅（MyST解析） |
| 程序化生成 | ❌ 手动编写 | ❌ 手动编写 | ✅ 适合导出 |
| 表头支持 | Markdown 语法 | `:header-rows:` | `:header:` + `:header-rows:` |
| 适用场景 | 简单表格 | 复杂内容表格 | 数据导入/导出 |
| 学习成本 | 低 | 中 | 低 |

## 表格标题和编号

三种表格指令在提供标题（arg）时都会：
1. 将标题解析为 caption 节点
2. 包裹在 `container(kind:'table')` 中
3. 自动编号（Table 1、Table 2...）
4. 支持通过 label 交叉引用

```markdown
参见 {ref}`tbl-data` 了解详情。
```

## 相关概念

- [指令与角色基础](00-directive-role-basics.md)
- [图片与图表](03-figures-images.md)
