---
type: "concept"
title: "v4格式详解"
description: "v4 Notebook JSON格式完整规范：顶层结构、cell类型、output类型、metadata、JSON Schema约束"
tags: [v4, format, schema, json, cell, output, metadata]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: v4-nbbase
    resource: /references/v4-nbbase-source.md
    title: "v4构造API"
  - id: validator
    resource: /references/validator-source.md
    title: "验证器源码"
---

# v4格式详解

v4 是当前默认Notebook格式（nbformat=4, nbformat_minor=5），本文档详细说明其JSON结构。

## 顶层结构

一个v4.5 Notebook的JSON结构如下：

```json
{
  "nbformat": 4,
  "nbformat_minor": 5,
  "metadata": { ... },
  "cells": [ ... ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `nbformat` | int | ✅ | 主版本号，必须为4 |
| `nbformat_minor` | int | ✅ | 次版本号，0-5 |
| `metadata` | object | ✅ | Notebook元数据（kernelspec, language_info等） |
| `cells` | array | ✅ | Cell数组（取代v3的worksheets） |

[F-100]

## Cell类型

v4有4种cell类型，由 `cell_type` 字段区分。

### Code Cell

```json
{
  "id": "a1b2c3d4",
  "cell_type": "code",
  "metadata": { ... },
  "execution_count": 1,
  "source": "print('hello')\n",
  "outputs": [ ... ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string (v4.5+) | Cell唯一ID，8-64字符 |
| `cell_type` | `"code"` | 固定值 |
| `metadata` | object | Cell元数据（tags, collapsed等） |
| `execution_count` | int/null | 执行计数，null=未执行 |
| `source` | string/array | 代码内容 |
| `outputs` | array | 输出对象列表 |

[F-101]

### Markdown Cell

```json
{
  "id": "e5f6g7h8",
  "cell_type": "markdown",
  "metadata": { ... },
  "source": "# Title\n\nSome **markdown** text."
}
```

无 `execution_count` 和 `outputs`。

### Raw Cell

```json
{
  "id": "i9j0k1l2",
  "cell_type": "raw",
  "metadata": { ... },
  "source": "Some raw text."
}
```

不被内核解释，直接透传（常用于nbconvert配置）。

### Cell ID要求（v4.5+）

- 每个cell必须有 `id` 字段
- ID由8-64个字符组成，允许：`[a-zA-Z0-9_-]`
- ID在Notebook范围内必须唯一
- 缺失ID会触发 `MissingIDFieldWarning` 并自动生成
- 重复ID会触发 `DuplicateCellId` 警告并自动修复

[F-102]

## Output类型

Code cell的 `outputs` 数组包含4种输出类型，由 `output_type` 字段区分。

### execute_result（执行结果）

```json
{
  "output_type": "execute_result",
  "execution_count": 1,
  "metadata": { ... },
  "data": {
    "text/plain": "2",
    "text/html": "<b>2</b>"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `output_type` | `"execute_result"` | 固定值 |
| `execution_count` | int/null | 对应的执行计数 |
| `metadata` | object | 输出元数据 |
| `data` | object | MIME类型→内容的映射（mime bundle） |

[F-103]

### display_data（显示数据）

```json
{
  "output_type": "display_data",
  "metadata": { ... },
  "data": {
    "image/png": "iVBORw0KGgo...",
    "text/plain": "<Figure size 640x480 with 1 Axes>"
  }
}
```

与execute_result结构类似，但无 `execution_count`。用于显式的`display()`调用或富媒体输出。

### stream（流输出）

```json
{
  "output_type": "stream",
  "name": "stdout",
  "text": "Hello World\n"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `"stdout"/"stderr"` | 流名称 |
| `text` | string/array | 文本内容（多行时为行列表） |

### error（错误输出）

```json
{
  "output_type": "error",
  "ename": "ZeroDivisionError",
  "evalue": "division by zero",
  "traceback": [
    "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
    "\u001b[0;31mZeroDivisionError\u001b[0m: division by zero"
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ename` | string | 异常类型名 |
| `evalue` | string | 异常消息 |
| `traceback` | array[string] | 带ANSI颜色码的traceback行列表 |

[F-104]

## MIME Bundle

`data` 字段是一个MIME bundle：键为MIME类型字符串，值为该类型表示的数据。

### 常见MIME类型

| MIME类型 | 内容 | 数据格式 |
|----------|------|---------|
| `text/plain` | 纯文本表示 | string |
| `text/html` | HTML表示 | string |
| `text/markdown` | Markdown表示 | string |
| `text/latex` | LaTeX表示 | string |
| `application/json` | JSON数据 | JSON object/array（非字符串） |
| `application/javascript` | JavaScript代码 | string |
| `image/png` | PNG图片 | base64编码字符串 |
| `image/jpeg` | JPEG图片 | base64编码字符串 |
| `image/svg+xml` | SVG矢量图 | string（XML文本） |

[F-105]

### 二进制数据处理

图片等二进制数据以base64编码存储在JSON字符串中。`BytesEncoder` 在写入时处理bytes→ASCII的转换。

### 行拆分格式

对于文本类型MIME（`text/*`、`application/javascript`、`image/svg+xml`），写入时多行内容拆分为行列表：

```json
{
  "data": {
    "text/plain": ["line1\n", "line2\n", "line3\n"]
  }
}
```

读取时通过 `rejoin_lines()` 重新合并为字符串。

## Metadata

Metadata是一个自由格式的NotebookNode（dict子类），不同工具使用不同的键。常见字段：

### Notebook-level metadata

```json
{
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3 (ipykernel)",
      "name": "python3",
      "language": "python"
    },
    "language_info": {
      "name": "python",
      "version": "3.10.0",
      "mimetype": "text/x-python",
      "codemirror_mode": { "name": "ipython", "version": 3 },
      "pygments_lexer": "ipython3",
      "nbconvert_exporter": "python",
      "file_extension": ".py"
    },
    "authors": [ { "name": "Author Name" } ]
  }
}
```

[F-106]

### Cell-level metadata

```json
{
  "metadata": {
    "tags": ["hide-input", "parameters"],
    "collapsed": false,
    "autoscroll": "auto",
    "jupyter": { "source_hidden": false, "outputs_hidden": false }
  }
}
```

- `tags`：标签数组，用于nbconvert参数化、条件渲染等
- `collapsed`：输入是否折叠（v4中标记为deprecated，建议用`jupyter.source_hidden`）
- `trusted`：运行时信任标记，不持久化（被strip_transient移除）

[F-107]

## JSON Schema

v4的JSON Schema文件位于 `nbformat/v4/nbformat.v4.schema.json`（以及v4.0-v4.5各自的schema文件）。

### Schema版本映射

| (major, minor) | Schema文件 |
|----------------|-----------|
| (4, 0) | nbformat.v4.0.schema.json |
| (4, 1) | nbformat.v4.1.schema.json |
| (4, 2) | nbformat.v4.2.schema.json |
| (4, 3) | nbformat.v4.3.schema.json |
| (4, 4) | nbformat.v4.4.schema.json |
| (4, 5) | nbformat.v4.5.schema.json |
| (None, None) | nbformat.v4.schema.json（最新） |

[F-108]

### Schema主要约束

1. 顶层必须有 `nbformat=4`，`cells`为array
2. cell通过`oneOf`约束：根据`cell_type`匹配code/markdown/raw三种schema
3. output通过`oneOf`约束：根据`output_type`匹配4种输出schema
4. code cell必须有`execution_count`（int或null）和`outputs`数组
5. data字段是MIME类型自由字典（`additionalProperties: true`）
6. v4.5 schema额外要求每个cell有唯一的`id`字段

[F-109]

## v4次版本变更记录

| minor | 变更 |
|-------|------|
| 0 | 初始v4格式：扁平cells、mime bundle、4种output类型 |
| 1 | metadata中增加可选字段 |
| 2 | 放宽output data约束 |
| 3 | 增加cell attachments支持 |
| 4 | 进一步放宽metadata约束 |
| 5 | 强制cell ID（id字段），8-64字符，唯一 |

[F-110]

## 相关概念

- [版本系统与转换](05-version-system.md)
- [验证体系](06-validation.md)
- [Notebook构造API](07-notebook-construction.md)
