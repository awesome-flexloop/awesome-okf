---
type: "concept"
title: "读写API"
description: "read/write/reads/writes四个核心API的用法、参数、版本控制、验证行为和文件/字符串双模式"
tags: [read, write, reads, writes, api, io, serialization]
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

# 读写API

nbformat 提供4个核心读写函数，构成公共I/O层。它们自动处理版本检测、版本转换和Schema验证。

## API总览

| 函数 | 输入 | 输出 | 说明 |
|------|------|------|------|
| `read(fp, as_version, **kwargs)` | 文件路径/文件对象 | NotebookNode | 从文件读取 |
| `reads(s, as_version, **kwargs)` | JSON字符串 | NotebookNode | 从字符串读取 |
| `write(nb, fp, version=NO_CONVERT, **kwargs)` | NotebookNode + 文件路径/对象 | None | 写入文件 |
| `writes(nb, version=NO_CONVERT, **kwargs)` | NotebookNode | JSON字符串 | 序列化为字符串 |

[F-040]

## read() / reads() — 读取Notebook

### 签名

```python
def reads(s, as_version, capture_validation_error=None, **kwargs):
def read(fp, as_version, capture_validation_error=None, **kwargs):
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `s` / `fp` | str / file-like | JSON字符串（reads）或文件路径/文件对象（read） |
| `as_version` | int 或 `NO_CONVERT` | 目标版本号，传 `nbformat.NO_CONVERT` 保持原始版本 |
| `capture_validation_error` | dict | 可选，验证错误写入此字典的 `"ValidationError"` 键 |

### 读取流程详解

```
reads(s, as_version)
  1. nb = reader.reads(s)           # 底层读取（无转换）
     a. parse_json(s) → json.loads()
     b. get_version(nb_dict) → (major, minor)
     c. versions[major].to_notebook_json(nb_dict, minor=minor)
        - from_dict() 递归转NotebookNode
        - rejoin_lines() 合并行列表
        - strip_transient() 移除临时字段
  2. if as_version is not NO_CONVERT:
       nb = convert(nb, as_version)  # 递归版本转换
  3. try: validate(nb)               # Schema验证
     except ValidationError as e:
       get_logger().error(...)       # 仅日志记录，不抛出
       if capture_validation_error:
         capture_validation_error["ValidationError"] = e
  4. return nb
```

[F-041]

### read() 的文件/路径双模式

`read()` 内部通过 `try: buf = fp.read()` 检测输入类型：
- 如果 `fp` 有 `read()` 方法（文件对象），直接读取
- 如果没有（路径字符串），用 `open(fp, encoding="utf8")` 打开后调用 `reads()`

```python
# 文件路径
nb = nbformat.read("notebook.ipynb", as_version=4)

# 文件对象
with open("notebook.ipynb", encoding="utf8") as f:
    nb = nbformat.read(f, as_version=4)
```

[F-042]

## write() / writes() — 写入Notebook

### 签名

```python
def writes(nb, version=NO_CONVERT, capture_validation_error=None, **kwargs):
def write(nb, fp, version=NO_CONVERT, capture_validation_error=None, **kwargs):
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `nb` | NotebookNode | 要写入的Notebook |
| `fp` | file-like / str | 文件对象或路径字符串（仅write） |
| `version` | int 或 `NO_CONVERT` | 目标版本，默认 `NO_CONVERT`（保持notebook自身版本） |

### 写入流程详解

```
writes(nb, version)
  1. if version is not NO_CONVERT:
       nb = convert(nb, version)
     else:
       version, _ = reader.get_version(nb)
  2. try: validate(nb)
     except ValidationError:  # 仅日志记录
  3. return versions[version].writes_json(nb, **kwargs)
     a. deepcopy(nb)              # 不修改原对象
     b. split_lines(nb)           # 多行字符串→行列表
     c. strip_transient(nb)       # 移除临时字段
     d. json.dumps(nb, indent=1, sort_keys=True,
                   separators=(",",": "), cls=BytesEncoder)
```

[F-043]

### JSON输出格式

写入时JSON序列化使用固定参数：
- `indent=1`：1空格缩进（易读且文件不大）
- `sort_keys=True`：键排序（VCS diff稳定）
- `separators=(",",": ")`：紧凑分隔符
- `ensure_ascii=False`：允许Unicode直接输出
- `cls=BytesEncoder`：bytes类型通过ASCII解码处理（base64图片数据）

[F-044]

### write() 的换行保证

```python
if not s.endswith("\n"):
    fp.write("\n")
```

write() 确保输出文件末尾始终有换行符，符合POSIX文本文件惯例 [F-045]。

## NO_CONVERT 哨兵

`NO_CONVERT` 是一个 `Sentinel` 单例：

```python
NO_CONVERT = Sentinel("NO_CONVERT", __name__, """...""")
```

- 传给 `read/reads` 的 `as_version`：读取后不转换版本，返回原始版本的Notebook
- 传给 `write/writes` 的 `version`：使用Notebook自身的版本号写入

身份比较用 `is` 运算符：`if as_version is not NO_CONVERT` [F-046]。

## 验证行为

读写时验证失败**不抛出异常**，仅通过traitlets logger记录ERROR级别日志。这保证了即使Notebook不完全符合Schema，也能被正常读写（容错设计）。

如需捕获验证错误：

```python
errors = {}
nb = nbformat.read("file.ipynb", as_version=4, capture_validation_error=errors)
if "ValidationError" in errors:
    # 处理验证错误
    print(errors["ValidationError"])
```

[F-047]

## split_lines / rejoin_lines — VCS友好机制

JSON格式中，多行字符串默认存储为单个字符串，导致Git diff中整段代码显示为一行变更。nbformat在写入时将这些字段拆分为行列表：

```python
# 写入后JSON中的source字段
"source": [
 "print('hello')\n",
 "print('world')\n"
]

# 读取后内存中
cell.source == "print('hello')\nprint('world')\n"
```

拆分范围：
- 所有cell的`source`字段
- stream输出的`text`字段
- mime bundle中`text/*`类型的数据
- `application/javascript`和`image/svg+xml`

JSON类型（`application/json`、`*+json`）不拆分，保持JSON结构完整性 [F-048]。

## strip_transient — 临时字段清理

读写时均调用`strip_transient()`移除不应持久化的字段：

- `nb.metadata.orig_nbformat` / `orig_nbformat_minor`（转换时的原始版本标记）
- `nb.metadata.signature`（HMAC签名，不应写入文件）
- 所有cell的`metadata.trusted`（运行时信任状态）

[F-049]

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
- [版本系统与转换](05-version-system.md)
