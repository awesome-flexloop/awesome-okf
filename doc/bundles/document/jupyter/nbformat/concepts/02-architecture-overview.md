---
type: "concept"
title: "架构总览"
description: "nbformat的分层架构、模块依赖关系、核心数据流与版本路由机制"
tags: [architecture, modules, data-flow, layered-design]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: init-api
    resource: /references/init-api.md
    title: "包入口公共API"
  - id: notebooknode
    resource: /references/notebooknode-source.md
    title: "NotebookNode源码"
  - id: validator
    resource: /references/validator-source.md
    title: "验证器源码"
---

# 架构总览

nbformat 采用**轻量分层架构**，核心分为4层：

```
┌─────────────────────────────────────────────────────┐
│                   公共API层                          │
│  __init__.py: read/write/reads/writes/validate/     │
│  convert/NO_CONVERT/NBFormatError                    │
├─────────────────────────────────────────────────────┤
│                   核心服务层                          │
│  reader.py / converter.py / validator.py / sign.py  │
├─────────────────────────────────────────────────────┤
│                   对象模型层                          │
│  notebooknode.py(NotebookNode) / _struct.py(Struct) │
│  sentinel.py / warnings.py / _imports.py            │
├─────────────────────────────────────────────────────┤
│                   版本实现层                          │
│  v1/  v2/  v3/  v4/  (含JSON Schema文件)             │
│  每个版本: nbbase.py + nbjson.py + rwbase.py         │
│           + convert.py + schema.json                 │
└─────────────────────────────────────────────────────┘
```

## 模块清单与职责

### 公共API层（`__init__.py`）

唯一对外导出的入口，提供统一的 `read`/`write`/`reads`/`writes`/`validate`/`convert` 函数和版本路由表 `versions`。所有公共API内部委托给核心服务层和版本实现层。

### 核心服务层

| 模块 | 职责 |
|------|------|
| `reader.py` | JSON解析（`parse_json`）、版本检测（`get_version`）、分版本读取（`reads`→版本模块的`to_notebook_json`） |
| `converter.py` | 版本转换：递归逐步升级/降级，确保每步版本号发生变化 |
| `validator.py` | Schema验证器管理（缓存+双后端）、normalize归一化、better_validation_error增强错误信息 |
| `sign.py` | Notebook信任签名：HMAC计算、SQLite/内存存储、NotebookNotary门面类、jupyter-trust CLI |
| `json_compat.py` | 双验证器适配器：JsonSchemaValidator(jsonschema)和FastJsonSchemaValidator(fastjsonschema) |

### 对象模型层

| 模块 | 职责 |
|------|------|
| `notebooknode.py` | `NotebookNode(Struct)`：自动转换嵌套dict、优化的`__deepcopy__`、`from_dict()`递归转换 |
| `_struct.py` | `Struct(dict)`：属性访问、类成员保护、`_allownew`开关、merge冲突解决 |
| `sentinel.py` | `Sentinel`类：创建唯一哨兵值（如NO_CONVERT），带有用repr |
| `warnings.py` | `MissingIDFieldWarning`和`DuplicateCellId`两个FutureWarning子类 |
| `_imports.py` | `import_item()`：通过点分字符串动态导入对象（如`import_item("nbformat.v4")`） |
| `corpus/words.py` | `generate_corpus_id()`：生成8位十六进制随机cell ID（`uuid4().hex[:8]`）|
| `current.py` | 已废弃的旧API，导入时发出DeprecationWarning |

### 版本实现层（v1-v4）

每个版本目录包含：

| 文件 | 职责 |
|------|------|
| `__init__.py` | 导出该版本的公共API（upgrades/downgrade/reads/writes/new_*等） |
| `nbbase.py` | 该版本的Notebook/Cell/Output工厂函数和版本常量（nbformat, nbformat_minor, nbformat_schema） |
| `nbjson.py` | JSON读写实现（JSONReader/JSONWriter），委托给rwbase |
| `rwbase.py` | 读写基类（NotebookReader/NotebookWriter）+ split_lines/rejoin_lines/strip_transient工具 |
| `convert.py` | upgrade/downgrade函数（v4↔v3，v3↔v2等） |
| `*.schema.json` | 对应minor版本的JSON Schema文件 |

v2额外有`nbpy.py`和`nbxml.py`（Python和XML格式支持，已废弃）。

## 核心数据流

### 读取流程（read）

```
read(fp, as_version)
  → reads(s, as_version)
    → reader.reads(s)              # JSON解析+版本检测→版本模块to_notebook_json
      → parse_json(s)              # json.loads
      → get_version(nb_dict)       # 读取nbformat/nbformat_minor
      → versions[major].to_notebook_json(nb_dict, minor)
        → from_dict(d)             # 递归转NotebookNode
        → rejoin_lines(nb)         # 行列表→字符串
        → strip_transient(nb)      # 移除临时字段
    → convert(nb, as_version)      # 按需版本转换（逐步递归）
    → validate(nb)                 # Schema验证（失败仅日志记录）
  → 返回 NotebookNode
```

[F-020]

### 写入流程（write）

```
write(nb, fp, version)
  → writes(nb, version)
    → convert(nb, version)         # 按需版本转换
    → validate(nb)                 # Schema验证
    → versions[version].writes_json(nb)
      → deepcopy(nb)               # 不修改原对象
      → split_lines(nb)            # 多行字符串→行列表（VCS友好）
      → strip_transient(nb)        # 移除临时字段
      → json.dumps(indent=1, sort_keys=True)
  → 写入文件（确保末尾换行）
```

[F-021]

## 版本路由机制

`versions`字典是所有版本相关操作的核心路由表：

```python
versions = {1: v1, 2: v2, 3: v3, 4: v4}
```

读取时：`versions[major].to_notebook_json(nb_dict, minor=minor)`
写入时：`versions[version].writes_json(nb, **kwargs)`
转换时：升级用`versions[step_version].upgrade(nb)`，降级用`versions[version].downgrade(nb)`

每个版本模块必须提供统一接口，新增版本只需在versions字典中注册即可，无需修改公共API [F-022]。

## 关键设计特点

1. **版本模块化**：每个版本独立目录，通过统一接口契约隔离
2. **读写对称**：read/write、reads/writes配对设计，文件路径和文件对象均支持
3. **验证宽容**：验证失败不抛异常（仅日志），通过`capture_validation_error`可选捕获
4. **深拷贝优化**：NotebookNode.__deepcopy__绕过Python通用深拷贝慢路径
5. **双验证后端**：fastjsonschema默认（快），jsonschema用于需要error_tree的场景
6. **行拆分VCS友好**：写入时split_lines将多行字符串拆分为列表，Git diff更可读

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [NotebookNode与Struct](03-notebook-node.md)
- [读写API](04-read-write-api.md)
