---
type: concept
title: "数据处理与转换"
bundle: /datawhale/handy-n8n
description: "n8n 数据结构（对象数组 json/binary）、Expressions 表达式、Code 节点（JS/Python 双模式）、内置变量与外部库引入"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c03/n8n-code.md
related:
  - /datawhale/handy-n8n/concepts/workflow-design
  - /datawhale/handy-n8n/concepts/advanced-practice
  - /datawhale/handy-n8n/references/c03-basic-concepts
tags: [data, expressions, code, javascript, python]
status: stable
---

# 数据处理与转换

## 核心理解

n8n 作为低代码平台，数据处理能力分为三个层次：**可视化节点**（Edit Fields、Split Out 等拖拽操作）→ **表达式**（嵌入节点配置的轻量 JavaScript）→ **Code 节点**（完整的 JavaScript/Python 编程环境）。这三层递进让用户在无代码体验和可编程能力之间平滑过渡。

## 数据结构基础

n8n 节点间传递的数据是**对象数组**，每个数组项包含：

```json
[
  {
    "json": { "key": "value" },
    "binary": {
      "file": {
        "data": "base64...",
        "mimeType": "image/png",
        "fileName": "example.png"
      }
    }
  }
]
```

- `json`：文本数据，是最常用的数据载体
- `binary`：二进制数据（图片、文件），Base64 编码，建议设置 mimeType/fileExtension/fileName
- n8n 自动对数组逐项处理，类似数据库表的行级处理

## Expressions 表达式

表达式是 n8n 中**最常用的代码形式**，实现在所有节点中，用于动态生成配置参数。

### 语法
- 使用 `{{ }}` 包裹，基于 [tournament](https://github.com/n8n-io/tournament) 模板引擎
- 只允许 **JavaScript** 代码
- 可引用前序节点输出、工作流元信息、环境变量

```javascript
// 引用前序节点输出
{{ $json.name }}

// 生成随机数组
{{ Array.from({ length: 10 }, (_) => Math.floor(Math.random() * 100)) }}

// 日期计算（单行链式调用）
{{ DateTime.fromISO('2025-03-13').diff(DateTime.fromISO('2025-02-13'), 'months').toObject() }}
```

### 限制
表达式只允许**单个语句**，不允许：
- 变量赋值（`let x = ...`）
- 函数定义（`function example() {...}`）
- 多语句执行

复杂逻辑应使用 Code 节点。

## Code 节点

Code 节点提供完整的编程环境，支持 JavaScript 和 Python 两种语言。

### 运行模式

1. **Run Once for All Items**（默认）：所有输入数据作为数组传递，代码只执行一次
2. **Run Once for Each Item**：每个输入数据项分别执行一次代码

### 语言差异

| 特性 | JavaScript | Python |
|------|-----------|--------|
| 执行引擎 | 原生 Node.js | pyodide（WebAssembly） |
| 性能 | 高 | 较低（WASM 开销） |
| 外部库 | 需配置 `NODE_FUNCTION_ALLOW_EXTERNAL` | pyodide 内置库，首次 import 自动下载 |
| 调试输出 | `console.log()` | `print()` |

Python 代码需 n8n 1.102.0 以上版本才能正常使用部分 pyodide 库。

### 安全限制
Code 节点**不允许**：
- 读写系统文件
- 发起 HTTP 请求（需通过 HTTP Request 节点）

### 内置变量

| JavaScript | Python | 描述 |
|-----------|--------|------|
| `$input.item` | `_input.item` | 当前输入数据项 |
| `$input.all()` | `_input.all()` | 所有输入数据 |
| `$input.first()` | `_input.first()` | 第一个数据项 |
| `$json` | `_json` | 当前项的 json 字段快捷访问 |
| `$("<node-name>").all()` | `_("<node-name>").all()` | 获取指定节点的全部输出 |
| `$now` | `_now` | 当前时间（DateTime.now()） |

### 返回数据格式

Code 节点必须返回数组，每项包含 `json` 字段。新版本自动补全，以下两种写法等效：

```javascript
// 完整写法
return [{ json: { name: "John" } }];

// 简写（自动包装）
return { name: "John" };
```

### 外部库引入

**JavaScript**：通过环境变量白名单允许：
```bash
export NODE_FUNCTION_ALLOW_EXTERNAL=moment,lodash
```

**Python**：pyodide 内置 numpy、pandas、beautifulsoup4 等，首次 import 自动下载。完整列表见 [pyodide packages](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)。

## 数据处理节点

### Edit Fields（Set）
变量赋值节点，修改或添加数据字段：
- Manual Mapping：手动映射字段名和值
- JSON Output：使用 JSON 表达式批量输出

### Split Out
将数组字段拆分为多个数据项：
- 输入 `{ "number": [81, 61, 53], "field1": "test" }`
- 按 `number` 拆分后得到 3 项，每项可选择性保留 `field1`

### Merge
合并多个上游节点的数据：
- Append：追加所有数据项
- Combine：按规则匹配合并
- SQL Query：使用 SQL 合并
- Choose Branch：选择某个输入

## 在 handy-n8n 中的位置

C03 的"n8n 中的代码"子文档系统讲解表达式和 Code 节点，配套 `n8n_code_node.json` 工作流演示 JS/Python 双语 Code 节点。数据处理节点（Edit Fields/Split Out）在"n8n 核心节点"子文档中讲解。数据结构（对象数组）在"n8n 平台介绍"中首次引入。

这三层数据处理能力是 n8n 作为低代码平台"逃生舱"设计的核心体现——简单场景用可视化节点，动态配置用表达式，复杂逻辑用 Code 节点。

## 延伸阅读

- [工作流设计](workflow-design.md)——触发器和核心节点的编排
- [高级实战](advanced-practice.md)——当 Code 节点也不够用时，开发自定义节点
- [C03 n8n 基本概念](../references/c03-basic-concepts.md)——完整信源
