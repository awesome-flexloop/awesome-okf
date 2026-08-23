---
type: Reference
title: "包入口公共API源码"
description: "nbformat/__init__.py 中的 read/write/reads/writes/validate/convert 等顶层公共API源码片段与说明"
tags: [api, read, write, validate, convert, NO_CONVERT]
sources:
  - id: nbformat-init
    resource: "../../../../../external/libs/jupyter/nbformat/nbformat/__init__.py"
    title: "nbformat/__init__.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 包入口公共API源码

本信源登记 `nbformat/__init__.py` 中导出的全部公共API。

## 版本映射表 `versions`

```python
versions = {
    1: v1,
    2: v2,
    3: v3,
    4: v4,
}
```

`versions` 字典将主版本号（int）映射到对应版本模块（v1/v2/v3/v4），是版本分发的核心路由表。每个版本模块必须提供 `upgrades`/`downgrade`/`reads_json`/`writes_json`/`to_notebook_json` 等标准接口。

## 顶层读写API签名

| 函数 | 签名 | 核心行为 |
|------|------|---------|
| `read(fp, as_version, capture_validation_error=None, **kwargs)` | 读文件 → NotebookNode | 支持文件对象或路径字符串，内部委托给 `reads()` |
| `reads(s, as_version, capture_validation_error=None, **kwargs)` | 读字符串 → NotebookNode | 先 `reader.reads(s)` 解析JSON，再按需 `convert()`，最后 `validate()` |
| `write(nb, fp, version=NO_CONVERT, capture_validation_error=None, **kwargs)` | NotebookNode → 写文件 | 委托给 `writes()` 序列化，确保末尾换行 |
| `writes(nb, version=NO_CONVERT, capture_validation_error=None, **kwargs)` | NotebookNode → JSON字符串 | 按需 `convert()`，`validate()`，再委托 `versions[version].writes_json()` |

## 版本转换哨兵 `NO_CONVERT`

```python
NO_CONVERT = Sentinel(
    "NO_CONVERT",
    __name__,
    """Value to prevent nbformat to convert notebooks to most recent version.""",
)
```

`NO_CONVERT` 是一个 `Sentinel` 单例，传入 `as_version` 或 `version` 参数时跳过自动版本转换，保持notebook原始版本。

## 异常类 `NBFormatError`

```python
class NBFormatError(ValueError):
    pass
```

`NBFormatError` 继承自 `ValueError`，在遇到不支持的nbformat版本时抛出。

## 当前版本常量

- `current_nbformat` = `v4.nbformat` = 4
- `current_nbformat_minor` = `v4.nbformat_minor` = 5

## 相关信源

- [NotebookNode源码](notebooknode-source.md)
- [版本转换converter](converter-source.md)
- [验证器validator](validator-source.md)
