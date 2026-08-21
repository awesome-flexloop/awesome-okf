---
type: "example"
title: "读取、验证与转换"
description: "读取现有Notebook文件、验证结构合法性、跨版本转换、处理验证错误、捕获ValidationError"
tags: [read, validate, convert, version, validation-error, normalize]
sources:
  - id: init-api
    resource: /references/init-api.md
    title: "包入口公共API"
  - id: validator
    resource: /references/validator-source.md
    title: "验证器源码"
---

# 读取、验证与转换

## 示例目标

演示如何读取Notebook、验证其结构、进行版本转换、处理验证错误和归一化修复。

## 完整代码

```python
"""
读取Notebook、验证、版本转换和错误处理示例。
"""
import json
import nbformat as nbf
from nbformat.validator import validate, isvalid, normalize, iter_validate
from nbformat.reader import get_version, reads as reader_reads

# ── 1. 基本读取 ──────────────────────────────────────────

# 读取并自动转换为v4
nb = nbf.read("example_notebook.ipynb", as_version=4)
major, minor = get_version(nb)
print(f"读取成功: nbformat v{major}.{minor}")
print(f"单元数: {len(nb.cells)}")

# 读取时不转换版本（保持原始版本）
nb_raw = nbf.read("example_notebook.ipynb", as_version=nbf.NO_CONVERT)
major_raw, minor_raw = get_version(nb_raw)
print(f"NO_CONVERT读取: v{major_raw}.{minor_raw}")

# ── 2. 从JSON字符串读取 ──────────────────────────────────

with open("example_notebook.ipynb", encoding="utf-8") as f:
    json_str = f.read()

nb2 = nbf.reads(json_str, as_version=4)
print(f"从字符串读取: {len(nb2.cells)} 个单元")

# ── 3. 验证Notebook ──────────────────────────────────────

# 3a. 基本验证（失败抛ValidationError）
try:
    validate(nb)
    print("✅ Notebook验证通过")
except nbf.ValidationError as e:
    print(f"❌ 验证失败: {e.message}")
    print(f"   路径: {'/'.join(str(p) for p in e.absolute_path)}")

# 3b. isvalid: 返回bool，不抛异常
if isvalid(nb):
    print("✅ isvalid: Notebook有效")
else:
    print("❌ isvalid: Notebook无效")

# 3c. 捕获验证错误（读取时）
errors = {}
nb3 = nbf.read("example_notebook.ipynb", as_version=4, capture_validation_error=errors)
if "ValidationError" in errors:
    print(f"⚠️ 读取时发现验证错误: {errors['ValidationError']}")
else:
    print("✅ 读取时无验证错误")

# 3d. iter_validate: 收集所有错误
all_errors = list(iter_validate(nb))
if all_errors:
    print(f"发现 {len(all_errors)} 个验证错误:")
    for err in all_errors:
        print(f"  - {err.message}")
else:
    print("✅ iter_validate: 无错误")

# ── 4. 故意构造无效Notebook并验证 ────────────────────────

invalid_nb = nbf.v4.new_notebook()
# 缺少cell_type字段（无效）
invalid_nb.cells.append(nbf.from_dict({"source": "bad cell", "metadata": {}}))

try:
    validate(invalid_nb)
    print("✅ 无效Notebook意外通过验证")
except nbf.ValidationError as e:
    print(f"❌ 预期的验证失败: {e.message[:100]}")

print(f"isvalid结果: {isvalid(invalid_nb)}")

# ── 5. normalize归一化 ───────────────────────────────────

# 创建一个缺少cell ID的Notebook（模拟v4.4及以下）
nb_no_id = nbf.v4.new_notebook()
cell = nbf.v4.new_code_cell("print(1)")
del cell["id"]  # 移除ID
nb_no_id.cells.append(cell)

import warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    changes, normalized = normalize(nb_no_id)
    id_warnings = [x for x in w if "id" in str(x.message).lower()]
    print(f"normalize修改次数: {changes}")
    print(f"ID相关警告数: {len(id_warnings)}")
    if id_warnings:
        print(f"  警告: {id_warnings[0].message}")
    print(f"修复后cell ID: {normalized.cells[0].id}")

# ── 6. 版本转换 ──────────────────────────────────────────

# v4 → v3
nb_v3 = nbf.convert(nb, 3)
v3_major, v3_minor = get_version(nb_v3)
print(f"\n转换到v3: v{v3_major}.{v3_minor}")
print(f"v3中worksheets数: {len(nb_v3.worksheets)}")
print(f"v3第一个worksheet中的cell数: {len(nb_v3.worksheets[0].cells)}")

# 检查v3特有的字段（input而非source）
v3_cell = nb_v3.worksheets[0].cells[1]  # 第一个code cell
if hasattr(v3_cell, 'input'):
    print(f"v3 code cell使用'input'字段: {v3_cell.input[:30]}...")

# v3 → v4（回转）
nb_v4_back = nbf.convert(nb_v3, 4)
print(f"回转到v4: v{get_version(nb_v4_back)[0]}.{get_version(nb_v4_back)[1]}")
print(f"回转后cell数: {len(nb_v4_back.cells)}")

# ── 7. 序列化检查 ────────────────────────────────────────

# writes → reads 往返一致性
json_str = nbf.writes(nb)
nb_roundtrip = nbf.reads(json_str, as_version=4)
print(f"\nJSON往返: 原始{len(nb.cells)}cell → 往返后{len(nb_roundtrip.cells)}cell")

# 验证写入的JSON格式
json_obj = json.loads(json_str)
print(f"JSON顶层键: {sorted(json_obj.keys())}")
print(f"nbformat={json_obj['nbformat']}, nbformat_minor={json_obj['nbformat_minor']}")
```

## 预期输出

```
读取成功: nbformat v4.5
单元数: 7
NO_CONVERT读取: v4.5
从字符串读取: 7 个单元
✅ Notebook验证通过
✅ isvalid: Notebook有效
✅ 读取时无验证错误
✅ iter_validate: 无错误
❌ 预期的验证失败: ...
isvalid结果: False
normalize修改次数: 1
ID相关警告数: 1
  警告: Cell is missing an `id` field. See ...
修复后cell ID: a1b2c3d4

转换到v3: v3.0
v3中worksheets数: 1
v3第一个worksheet中的cell数: 7
v3 code cell使用'input'字段: import math
import random...
回转到v4: v4.5
回转后cell数: 7

JSON往返: 原始7cell → 往返后7cell
JSON顶层键: ['cells', 'metadata', 'nbformat', 'nbformat_minor']
nbformat=4, nbformat_minor=5
```

## 关键要点

- `read()` 需要 `as_version` 参数；传入 `NO_CONVERT` 保持原始版本
- `validate()` 失败抛 `ValidationError`，`isvalid()` 返回bool
- `capture_validation_error` 参数在读写时捕获验证错误而非抛异常
- `iter_validate()` 返回所有错误的迭代器，适合批量检查
- `normalize()` 自动修复常见问题（如缺失cell ID），返回修改次数
- `convert()` 在版本间转换，跨版本递归逐步转换（如v2→v3→v4）
- v4→v3时，`cells` 扁平数组包装到 `worksheets`，`source` 重命名为 `input`
- `writes()`/`reads()` 往返后结构等价

## 相关概念

- [读写API](../concepts/04-read-write-api.md)
- [验证体系](../concepts/06-validation.md)
- [版本系统与转换](../concepts/05-version-system.md)
