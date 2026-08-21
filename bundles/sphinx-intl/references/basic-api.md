---
type: reference
title: "basic.py 核心业务逻辑 API 参考"
description: "sphinx-intl update/build/stat 核心函数、数据类和多进程处理机制的源码信源"
tags: [core-logic, update, build, stat, multiprocessing, api-reference]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: basic-py
    resource: "sphinx_intl/basic.py"
    title: "sphinx-intl core business logic module"
---

# basic.py 核心业务逻辑 API 参考

本文件记录 `sphinx_intl/basic.py` 中定义的核心数据类和业务函数。

## 数据类

### UpdateItem（frozen dataclass）

单文件更新任务描述符，不可变。

```python
@dataclasses.dataclass(frozen=True)
class UpdateItem:
    po_file: str        # 目标 PO 文件路径
    pot_file: str       # 源 POT 文件路径
    lang: str           # 目标语言代码
    line_width: int     # PO 文件最大行宽
    ignore_obsolete: bool  # 是否移除过时消息
```

### UpdateResult（frozen dataclass）

单文件更新结果。

```python
@dataclasses.dataclass(frozen=True)
class UpdateResult:
    po_file: str                # PO 文件路径
    status: str                 # 状态: "create" | "update" | "notchanged"
    added: Optional[int] = 0    # 新增消息数（仅update状态）
    deleted: Optional[int] = 0  # 删除消息数（仅update状态）
```

## 工具函数

### get_lang_dirs(path)

获取指定路径下的语言目录列表。

- **参数**: `path` (str) — locale 目录路径
- **返回**: `tuple` — 包装在单元素元组中的语言目录名元组
- **匹配规则**: `glob(path + "/[a-z]*")`，排除以 `pot` 结尾的目录
- **注意**: commands.py 中也有同名函数，basic.py 中的是独立副本

## 内部函数

### _update_single_file(update_item: UpdateItem) -> UpdateResult

处理单个 PO 文件的更新/创建，支持多进程调用。

**逻辑流程**:

1. 加载 POT 文件（`c.load_po(update_item.pot_file)`）
2. 如果 PO 文件已存在：
   - 加载现有 PO 文件
   - 记录更新前的 msgid 集合
   - 调用 `c.update_with_fuzzy(cat, cat_pot)` 合并新消息
   - 比较更新前后 msgid 集合
   - 如果有变化：写入 PO 文件，返回 `("update", added, deleted)`
   - 如果无变化：返回 `("notchanged",)`
3. 如果 PO 文件不存在（新文件）：
   - 设置 `cat_pot.locale = lang`
   - 写入新 PO 文件
   - 返回 `("create",)`

## 公开函数

### update(locale_dir, pot_dir, languages, line_width=76, ignore_obsolete=False, jobs=0)

从 POT 文件批量更新/创建 PO 文件，支持多进程并行。

- **参数**:
  - `locale_dir` (str): locale 目录路径
  - `pot_dir` (str): POT 文件目录路径
  - `languages` (tuple): 目标语言代码元组
  - `line_width` (int): PO 文件最大行宽，默认 76
  - `ignore_obsolete` (bool): 是否移除过时 `#~` 消息，默认 False
  - `jobs` (int): 并行进程数，0 表示使用所有 CPU
- **返回**: `dict` — `{'create': int, 'update': int, 'notchanged': int}` 统计
- **行为**:
  1. 遍历 `pot_dir` 下所有 `.pot` 文件
  2. 为每个 (pot_file, language) 组合构建 UpdateItem
  3. PO 文件路径规则: `<locale_dir>/<lang>/LC_MESSAGES/<basename>.po`
  4. 使用 `multiprocessing.Pool(processes=jobs or None)` 并行处理
  5. 实时输出每个文件的处理结果

### build(locale_dir, output_dir, languages)

将 PO 文件编译为 MO 文件。

- **参数**:
  - `locale_dir` (str): locale 目录路径
  - `output_dir` (str): MO 输出目录路径
  - `languages` (tuple): 目标语言代码元组
- **返回**: `None`
- **行为**:
  1. 遍历每个语言目录下的 `.po` 文件
  2. 构建对应 MO 文件路径: `<output_dir>/<relpath>/<base>.mo`
  3. **增量编译**: 如果 MO 文件存在且 mtime 晚于 PO 文件则跳过
  4. 调用 `c.load_po()` + `c.write_mo()` 编译

### stat(locale_dir, languages)

打印所有 PO 文件的翻译统计信息。

- **参数**:
  - `locale_dir` (str): locale 目录路径
  - `languages` (tuple): 目标语言代码元组
- **返回**: `dict` — `{po_file_path: {'translated': int, 'fuzzy': int, 'untranslated': int}}`
- **行为**:
  1. 遍历每个语言目录下的 `.po` 文件
  2. 使用 `c.translated_entries()`、`c.fuzzy_entries()`、`c.untranslated_entries()` 统计
  3. 实时输出: `<po_file>: N translated, N fuzzy, N untranslated.`
