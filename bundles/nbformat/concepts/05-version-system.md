---
type: "concept"
title: "版本系统与转换"
description: "nbformat四个版本(v1-v4)的差异、版本检测、逐步递归转换机制、upgrade/downgrade流程"
tags: [version, convert, upgrade, downgrade, v1, v2, v3, v4, migration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: init-api
    resource: /references/init-api.md
    title: "包入口公共API"
  - id: v4-nbbase
    resource: /references/v4-nbbase-source.md
    title: "v4构造API"
---

# 版本系统与转换

nbformat 支持4个主版本（v1-v4），版本号存储在Notebook JSON的顶层字段 `nbformat`（主版本）和 `nbformat_minor`（次版本）中。

## 版本历史概览

| 版本 | minor | 主要特征 | 状态 |
|------|-------|---------|------|
| v1 | 0 | 原始Python pickle格式，仅基本结构 | 历史遗留 |
| v2 | 0 | 引入JSON格式，增加worksheet概念，支持.py/.xml格式 | 历史遗留 |
| v3 | 0 | 稳定JSON格式，prompt_number、pyout/pyerr输出类型、worksheet分组 | 旧版兼容 |
| v4 | 0-5 | 当前版本：扁平化cells、cell ID、mime bundle输出、execute_result | **当前** |

[F-050]

当前默认版本为 **v4.5**（nbformat=4, nbformat_minor=5）[F-051]。

## 版本检测

```python
from nbformat.reader import get_version

major, minor = get_version(nb)
# major = nb.get("nbformat", 1)   # 默认为1
# minor = nb.get("nbformat_minor", 0)  # 默认为0
```

版本号不存在时，major默认为1，minor默认为0 [F-052]。

## 版本路由表

```python
versions = {1: v1, 2: v2, 3: v3, 4: v4}
```

所有版本相关操作（读取、写入、转换）通过此字典分发到对应版本模块。每个版本模块必须提供：

| 接口 | 说明 |
|------|------|
| `nbformat` / `nbformat_minor` | 版本号常量 |
| `nbformat_schema` | Schema文件映射表 |
| `to_notebook_json(nb_dict, minor)` | dict→NotebookNode |
| `reads_json(s)` / `writes_json(nb)` | JSON序列化/反序列化 |
| `upgrade(nb)` | 升级到下一主版本 |
| `downgrade(nb)` | 降级到上一主版本 |
| `new_notebook()` / `new_code_cell()` 等 | 工厂函数 |

[F-053]

## convert() — 递归逐步转换

```python
def convert(nb, to_version):
```

convert() 使用**逐步递归**策略在版本间转换：

### 升级路径（to_version > 当前版本）

```
v1 → v2 → v3 → v4
```

每步调用 `versions[step_version].upgrade(nb)`，其中 `step_version = version + 1`。

### 降级路径（to_version < 当前版本）

```
v4 → v3 → v2 → v1
```

每步调用 `versions[version].downgrade(nb)`，其中 `step_version = version - 1`。

[F-054]

### 转换验证

每步转换后检查版本号确实发生了变化：

```python
converted = convert_function(nb)
if converted.get("nbformat", 1) == version:
    raise ValueError("Failed to convert notebook from v%d to v%d." % (version, step_version))
```

这防止了upgrade/downgrade函数忘记更新版本号的静默失败 [F-055]。

### 跨版本转换示例

```python
# v2 → v4: 递归路径 v2→v3(upgrade) → v3→v4(upgrade)
nb_v4 = convert(nb_v2, 4)

# v4 → v2: 递归路径 v4→v3(downgrade) → v3→v2(downgrade)
nb_v2 = convert(nb_v4, 2)
```

## v3 ↔ v4 转换要点

v3到v4是最大的格式变革，`v4/convert.py` 中的 `upgrade()`/`downgrade()` 处理以下映射：

### v3 → v4（upgrade）

| v3概念 | v4对应 | 处理方式 |
|--------|--------|---------|
| `worksheets` 数组 | 顶层 `cells` 数组 | 扁平化：所有worksheet中的cells合并到顶层cells |
| `cell.input` | `cell.source` | 重命名字段 |
| `cell.prompt_number` | `cell.execution_count` | 重命名字段 |
| `cell.language` | 移除 | code cell不再有language字段（由kernel metadata决定） |
| `cell.collapsed` | `cell.metadata.collapsed` | 移入metadata |
| heading cell | markdown cell | `### heading` → Markdown标题语法 |
| html cell | markdown cell | 类型转换 |
| `output.prompt_number` | `output.execution_count` | 重命名（pyout→execute_result） |
| `output.type: "pyout"` | `output.output_type: "execute_result"` | 类型重命名 |
| `output.type: "pyerr"` | `output.output_type: "error"` | 类型重命名 |
| `output.stream: "stdout"` | `output.name: "stdout"` | 字段重命名 |
| 输出数据在顶层（`output.png`/`output.text`等） | `output.data` mime bundle dict | 重组为{mime_type: data}结构，mime类型别名映射 |
| （无） | `cell.id` | v4.5+自动生成8位随机ID |

[F-056]

原始版本信息保存在 metadata 中：
- `nb.metadata.orig_nbformat` = 原始主版本
- `nb.metadata.orig_nbformat_minor` = 原始次版本

### v4 → v3（downgrade）

上述映射的反向操作：
- cells → worksheets（包装到单个worksheet中）
- source → input
- execution_count → prompt_number
- 添加language="python"
- data dict中的mime类型拆回顶层字段（`text/html`→`html`等）
- markdown单行标题识别为heading cell
- 移除cell.id和cell.attachments

[F-057]

### MIME类型映射

```python
_mime_map = {
    "text": "text/plain",
    "html": "text/html",
    "svg": "image/svg+xml",
    "png": "image/png",
    "jpeg": "image/jpeg",
    "latex": "text/latex",
    "json": "application/json",
    "javascript": "application/javascript",
}
```

v3使用简短别名（`png`/`html`/`text`），v4使用标准MIME类型作为键名 [F-058]。

## v4 次版本演进

v4内的次版本升级由 `v4/convert.py` 的 `upgrade()` 处理：

- v4.0→v4.5：为所有cell添加`id`字段（`generate_corpus_id()`）
- 之前的minor版本间无数据结构变更（仅schema放宽）

未来次版本的转换代码预留了位置（注释中的 `if from_minor < 3:` 等）。

## current.py — 废弃API

`nbformat.current` 模块是v3时代的遗留API，导入时发出DeprecationWarning，建议使用：
- 顶层 `nbformat.read/write/validate` 进行公共I/O
- `nbformat.vX` 直接使用特定版本的构造API

[F-059]

## 相关概念

- [读写API](04-read-write-api.md)
- [验证体系](06-validation.md)
- [v4格式详解](09-v4-format.md)
