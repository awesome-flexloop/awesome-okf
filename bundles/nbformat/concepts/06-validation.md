---
type: "concept"
title: "验证体系"
description: "JSON Schema验证机制、双后端(fastjsonschema/jsonschema)、Schema缓存、normalize归一化、错误增强"
tags: [validation, jsonschema, fastjsonschema, schema, normalize, validation-error]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: validator
    resource: /references/validator-source.md
    title: "验证器源码"
---

# 验证体系

nbformat 使用 JSON Schema 验证 Notebook 结构合法性，支持双验证后端，具备验证器缓存、归一化修复和增强错误信息能力。

## 双验证后端

| 后端 | 默认 | 速度 | Error Tree | 适用场景 |
|------|------|------|-----------|---------|
| fastjsonschema | ✅ | 快（编译为Python代码） | ❌ 不支持 | 默认验证路径 |
| jsonschema | 备选 | 较慢（纯Python） | ✅ 支持 | 需要error_tree的元数据剥离场景 |

通过环境变量 `NBFORMAT_VALIDATOR` 切换：
- `NBFORMAT_VALIDATOR=fastjsonschema`（默认）
- `NBFORMAT_VALIDATOR=jsonschema`

[F-060]

### 适配器类

**JsonSchemaValidator**（jsonschema后端）：
- 包装 `jsonschema.Draft4Validator`
- 提供 `validate(data)`、`iter_errors(data, schema=None)`、`error_tree(errors)`
- 支持 `evolve(schema=...)` 动态调整schema

**FastJsonSchemaValidator**（fastjsonschema后端）：
- 通过 `fastjsonschema.compile(schema)` 编译为Python验证函数
- `error_tree()` 抛 `NotImplementedError`（fastjsonschema异常不含足够信息）
- 验证失败时将 `JsonSchemaException` 转为 `ValidationError`

[F-061]

## get_validator() — 验证器获取与缓存

```python
def get_validator(version=None, version_minor=None, relax_add_props=False, name=None):
```

验证器按 `(validator_name, version, version_minor, relax_add_props)` 四元组缓存：

```python
validators: dict[tuple[str, int|None, int|None, bool], Any] = {}
```

[F-062]

### Schema加载流程

1. 通过 `import_item("nbformat.v%s" % version)` 动态导入版本模块
2. 根据 `(version, version_minor)` 在 `nbformat_schema` 字典中查找schema文件名
3. 加载对应的 `.schema.json` 文件
4. 未来版本（minor > 当前）自动relax：
   - `_relax_additional_properties()`：将所有 `additionalProperties: false` 改为 `true`
   - `_allow_undefined()`：在cell/output的oneOf中添加unrecognized类型
5. `relax_add_props=True` 时也relax additionalProperties
6. 创建验证器实例并缓存

[F-063]

## validate() — 公共验证API

```python
def validate(nbdict=None, ref=None, version=None, version_minor=None,
             relax_add_props=False, nbjson=None) -> None:
```

验证失败抛出 `ValidationError`。参数说明：

| 参数 | 说明 |
|------|------|
| `nbdict` | 要验证的Notebook dict/NotebookNode |
| `ref` | 子schema引用，如 `"code_cell"`/`"markdown_cell"`/`"stream"` |
| `version`/`version_minor` | 指定版本，默认从Notebook自动检测 |
| `relax_add_props` | 是否允许额外属性（忽略未知字段） |
| `nbjson` | 废弃参数，向后兼容 |

[F-064]

### 验证流程

```
validate(nbdict)
  → _validate(nbdict, ...)
    1. 检测版本（get_version或ref指定）
    2. _normalize() — 归一化修复
    3. iter_validate() → _get_errors()
       a. 获取缓存的验证器
       b. validator.iter_errors(nbdict) 获取错误迭代器
       c. 首个错误非None时：若当前后端不是jsonschema，
          切换到jsonschema后端获取更好的错误信息
       d. 对每个错误调用 better_validation_error() 增强
    4. 遇到第一个错误即抛出
```

[F-065]

## isvalid() — 布尔检查

```python
from nbformat.validator import isvalid
result = isvalid(nb)  # True/False
```

- 内部调用 `_validate(nb, repair_duplicate_cell_ids=False)`
- 捕获ValidationError返回False，否则返回True
- 使用deepcopy保护原始Notebook不被修改，验证后断言Notebook未被篡改

[F-066]

## normalize() — 归一化修复

```python
def normalize(nbdict, version=None, version_minor=None, *,
              relax_add_props=False, strip_invalid_metadata=False):
    return (changes_count, normalized_notebook)
```

normalize 在验证前自动修复常见问题，返回 `(修改次数, 修复后的Notebook深拷贝)`。

### 修复操作

**Cell ID修复**（v4.5+）：
- 缺少 `id` 字段：发出 `MissingIDFieldWarning`（FutureWarning），自动生成ID
- 重复ID：发出 `DuplicateCellId`（FutureWarning），自动生成新ID修复

**无效元数据剥离**（`strip_invalid_metadata=True`）：
- 使用jsonschema的 `error_tree` 定位metadata中不符合schema的键
- 移除notebook级和cell级metadata中的无效键
- 仅在jsonschema后端下可用（需要error_tree支持）

[F-067]

### normalize与validate的关系

公共 `validate()` 总是调用 `_normalize()`（使用默认参数：修复重复ID，不剥离metadata），这意味着验证过程会对Notebook进行副作用修改（生成缺失cell ID）。纯检查场景使用 `isvalid()`（`repair_duplicate_cell_ids=False`）。

## better_validation_error() — 错误信息增强

JSON Schema的 `oneOf` 错误信息通常不友好（只说"不匹配任何schema"），`better_validation_error()` 针对cell/output类型进行改进：

1. 检测错误是否在 `oneOf` 关键字上
2. 如果是cell类型错误，根据 `cell_type` 字段直接验证对应子schema（如`code_cell`）
3. 如果是output类型错误，根据 `output_type` 直接验证
4. 递归增强子错误，合并relative_path
5. 返回 `NotebookValidationError`（截断输出，避免dump整个Notebook）

[F-068]

### NotebookValidationError

`NotebookValidationError(ValidationError)` 自定义 `__str__` 方法：
- 使用 `_truncate_obj()` 截断错误实例（cell列表显示为"...N cells..."，长字符串截断为64字符，dict/list截断为16项）
- 格式化输出包含：错误消息、失败的验证器和位置、截断后的实例内容

[F-069]

## iter_validate() — 迭代所有错误

```python
def iter_validate(nbdict=None, ref=None, version=None, ...):
```

返回所有 `ValidationError` 的生成器，不抛出异常。适合收集全部验证错误而非遇错即停的场景。

## 未来兼容性设计

当验证来自更高minor版本的Notebook时（如用nbformat 5.9读取v4.8的Notebook），验证器自动进入**宽容模式**：
- `additionalProperties: false` 全部改为 `true`
- cell和output的oneOf添加unrecognized类型
- 前向兼容保证：新版本引入的新字段不会导致旧版本nbformat无法读取

[F-070]

## 相关概念

- [版本系统与转换](05-version-system.md)
- [v4格式详解](09-v4-format.md)
- [Notebook构造API](07-notebook-construction.md)
