---
type: Reference
title: "验证器Validator源码"
description: "validator.py和json_compat.py源码解析，包括双验证器后端(fastjsonschema/jsonschema)、Schema缓存、normalize归一化、iter_validate迭代器"
tags: [validator, jsonschema, fastjsonschema, schema, normalize, validation-error]
sources:
  - id: validator-py
    resource: "../../../../../external/libs/jupyter/nbformat/nbformat/validator.py"
    title: "nbformat/validator.py"
  - id: json-compat-py
    resource: "../../../../../external/libs/jupyter/nbformat/nbformat/json_compat.py"
    title: "nbformat/json_compat.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
---

# 验证器Validator源码

## 双验证器后端（`json_compat.py`）

nbformat 支持两个JSON Schema验证后端：

| 后端 | 类名 | 默认 | 特点 |
|------|------|------|------|
| fastjsonschema | `FastJsonSchemaValidator` | ✅ 默认 | 编译为Python代码，验证速度快；不支持error_tree |
| jsonschema | `JsonSchemaValidator` | 备选 | 纯Python实现，支持ErrorTree用于元数据错误定位 |

通过环境变量 `NBFORMAT_VALIDATOR` 切换，默认值为 `fastjsonschema`。

### 适配器类层次

- `JsonSchemaValidator`：包装 `jsonschema.Draft4Validator`，提供 `validate()`/`iter_errors()`/`error_tree()`
- `FastJsonSchemaValidator(JsonSchemaValidator)`：包装 `fastjsonschema.compile()`，`error_tree()` 抛 NotImplementedError

## 验证器缓存（`validator.py`）

```python
validators: dict[tuple[str, int | None, int | None, bool], Any] = {}
```

缓存键为 `(validator_name, version, version_minor, relax_add_props)` 四元组，避免重复加载和编译JSON Schema。

### get_validator() 核心逻辑

1. 版本号默认取 `current_nbformat`/`current_nbformat_minor`
2. 通过 `import_item("nbformat.v%s" % version)` 动态导入版本模块
3. 调用 `_get_schema_json()` 加载对应的JSON Schema文件
4. 对未来版本（`version_minor > current_minor`）自动relax：`_relax_additional_properties()` + `_allow_undefined()`
5. `relax_add_props=True` 时也调用 `_relax_additional_properties()`
6. 创建验证器实例并缓存

## normalize() 归一化函数

`normalize(nbdict, version=None, version_minor=None, *, relax_add_props=False, strip_invalid_metadata=False)` 执行：

1. **Cell ID修复**（v4.5+）：对缺少 `id` 字段的cell发出 `MissingIDFieldWarning` 并自动生成ID；对重复ID自动修复并发出 `DuplicateCellId` 警告
2. **无效元数据剥离**（`strip_invalid_metadata=True`）：使用jsonschema的error_tree定位metadata中不符合schema的键并移除

## validate() 公共API

```python
def validate(nbdict=None, ref=None, version=None, version_minor=None,
             relax_add_props=False, nbjson=None) -> None
```

- `ref` 参数可针对子schema验证（如 `"code_cell"`/`"markdown_cell"`）
- 内部调用 `_validate()` → `iter_validate()` → `_get_errors()`
- 遇到第一个错误即抛出 `ValidationError`

## iter_validate() 生成器

返回所有验证错误的迭代器，错误通过 `better_validation_error()` 增强：
- 对 `oneOf` 失败（cell类型不匹配），根据 `cell_type`/`output_type` 直接验证对应子schema，给出更精确的错误信息
- 使用 `NotebookValidationError` 截断输出，避免在错误日志中dump整个notebook

## 相关信源

- [包入口公共API](init-api.md)
- [v4格式规范](../concepts/09-v4-format.md)
