---
type: concept
title: "更新机制：多进程合并与 Fuzzy"
description: "sphinx-intl update 的多进程并行架构、UpdateItem/UpdateResult 数据类、单文件更新逻辑与 fuzzy 标记处理"
tags: [update, multiprocessing, parallel, fuzzy, dataclass, merge]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: basic-api
    resource: /references/basic-api.md
    title: "basic.py 核心业务逻辑 API 参考"
  - id: catalog-api
    resource: /references/catalog-api.md
    title: "catalog.py PO/POT/MO 文件操作 API 参考"
---

# 更新机制：多进程合并与 Fuzzy

`sphinx-intl update` 是最复杂的子命令，实现了从 POT 到 PO 的智能更新，并支持多进程并行处理。本章深入解析其内部机制。

## 数据类设计

basic.py 使用 Python `@dataclasses.dataclass(frozen=True)` 定义了两个不可变数据类来描述更新任务和结果。

### UpdateItem — 更新任务描述符 [F-039]

```python
@dataclasses.dataclass(frozen=True)
class UpdateItem:
    po_file: str           # 目标 PO 文件路径
    pot_file: str          # 源 POT 文件路径
    lang: str              # 目标语言代码
    line_width: int        # PO 文件最大行宽
    ignore_obsolete: bool  # 是否移除过时消息
```

`frozen=True` 使 UpdateItem 成为不可变对象，可以安全地在多进程间传递。每个 UpdateItem 代表一个 (POT文件, 语言) 组合的更新任务。

### UpdateResult — 更新结果 [F-040]

```python
@dataclasses.dataclass(frozen=True)
class UpdateResult:
    po_file: str                    # PO 文件路径
    status: str                     # 状态: "create" | "update" | "notchanged"
    added: Optional[int] = 0        # 新增消息数
    deleted: Optional[int] = 0      # 删除消息数
```

三种状态含义：
- `"create"`：PO 文件不存在，从 POT 创建了新文件
- `"update"`：PO 文件存在，有消息增删，已写入更新
- `"notchanged"`：PO 文件存在，msgid 集合无变化，跳过写入

## 多进程并行架构

update 函数使用 Python 标准库 `multiprocessing.Pool` 实现并行处理 [F-041]。

### 任务构建阶段 [F-042]

```python
to_translate = []
for dirpath, dirnames, filenames in os.walk(pot_dir):
    for filename in filenames:
        pot_file = os.path.join(dirpath, filename)
        base, ext = os.path.splitext(pot_file)
        if ext != ".pot":
            continue
        basename = relpath(base, pot_dir)
        for lang in languages:
            po_dir = os.path.join(locale_dir, lang, "LC_MESSAGES")
            po_file = os.path.join(po_dir, basename + ".po")
            to_translate.append(
                UpdateItem(po_file, pot_file, lang, line_width, ignore_obsolete)
            )
```

构建阶段做以下事情：
1. 递归遍历 `pot_dir` 下所有 `.pot` 文件
2. 对每个 POT 文件和每个目标语言，计算对应的 PO 文件路径
3. PO 文件路径规则：`<locale_dir>/<lang>/LC_MESSAGES/<相对路径>/<文件名>.po`
4. 为每个组合创建一个 UpdateItem，加入任务列表

### 并行执行阶段 [F-043]

```python
with mp.Pool(processes=jobs or None) as pool:
    for result in pool.imap_unordered(_update_single_file, to_translate):
        status[result.status] += 1
        if result.status == "update":
            click.echo(f"Update: {result.po_file} +{result.added}, -{result.deleted}")
        elif result.status == "create":
            click.echo(f"Create: {result.po_file}")
        else:
            click.echo(f"Not Changed: {result.po_file}")
```

关键设计选择：
- `mp.Pool(processes=jobs or None)`：`jobs=0` 时 `processes=None`，使用 `os.cpu_count()` 个进程
- `pool.imap_unordered()`：无序迭代结果——谁先处理完就返回谁，比有序的 `imap` 更快
- 主线程负责结果收集和进度输出，子进程只执行 `_update_single_file`
- `with` 语句确保 Pool 正确清理

### 为什么选 multiprocessing 而非 threading？

PO 文件读写和 Babel 目录操作是 CPU 密集型（解析/生成文本），Python GIL 会限制多线程的 CPU 并行性。使用多进程可以真正利用多核 CPU，对于有大量文档的项目（如 Python 官方文档有上百个 POT 文件）并行加速效果显著。

## 单文件更新逻辑：_update_single_file

`_update_single_file` 是多进程池中的工作函数，处理单个 PO 文件的创建或更新 [F-044]。

### 新文件创建分支 [F-045]

```python
else:  # new po file
    cat_pot.locale = update_item.lang
    c.dump_po(
        update_item.po_file,
        cat_pot,
        width=update_item.line_width,
        ignore_obsolete=update_item.ignore_obsolete,
    )
    return UpdateResult(update_item.po_file, "create")
```

当 PO 文件不存在时：
1. 将 POT Catalog 对象的 locale 设置为目标语言
2. 直接将 POT 内容写入新的 PO 文件（msgstr 全为空）
3. 返回 `"create"` 状态

### 已有文件更新分支 [F-046]

```python
if os.path.exists(update_item.po_file):
    cat = c.load_po(update_item.po_file)
    msgids_before = {m.id for m in cat if m.id}
    c.update_with_fuzzy(cat, cat_pot)
    msgids_after = {m.id for m in cat if m.id}
    if msgids_before != msgids_after:
        added = msgids_after - msgids_before
        deleted = msgids_before - msgids_after
        c.dump_po(update_item.po_file, cat, ...)
        return UpdateResult(update_item.po_file, "update", len(added), len(deleted))
    else:
        return UpdateResult(update_item.po_file, "notchanged")
```

更新逻辑的核心是**基于 msgid 集合差异的智能更新**：

1. 加载现有 PO 文件
2. 记录更新前的 msgid 集合
3. 调用 `update_with_fuzzy`（即 Babel 的 `catalog.update()`）合并 POT 变更
4. 记录更新后的 msgid 集合
5. 比较前后集合差异：
   - **有差异**：写入更新后的 PO 文件，返回 `"update"` 状态和增删计数
   - **无差异**：不写入文件，返回 `"notchanged"` 状态

### 为什么基于 msgid 集合判断而非总是写入？

1. **性能优化**：如果只是行号注释（`#:`）变化而 msgid 没变，不写入文件可避免磁盘 I/O 和不必要的版本控制 diff
2. **幂等性**：多次运行 update 不会产生无意义的文件修改
3. **增量友好**：只在有实际翻译内容变化时才更新文件，便于版本控制和翻译人员识别变更

但注意：Babel 的 `catalog.update()` 也会更新位置注释（`#:` 行号），即使 msgid 没变。sphinx-intl 的判断方式是**只看 msgid 集合**，位置注释的变化不会触发写入——这意味着如果只是源文件行号变了而内容没变，PO 文件不会被重写。

## --no-obsolete 选项

`--no-obsolete` 选项控制是否在写入时移除 obsolete 条目 [F-047]。

在 gettext 工作流中，当 POT 中删除了一条消息，PO 中对应的条目不会被直接删除，而是被标记为 obsolete（以 `#~` 前缀）：

```po
#~ msgid "Old string that was removed"
#~ msgstr "已删除的旧字符串"
```

- **不使用 `--no-obsolete`（默认）**：保留 obsolete 条目，翻译人员可以看到历史翻译
- **使用 `--no-obsolete`**：在 dump_po 时传入 `ignore_obsolete=True`，彻底移除 obsolete 条目

obsolete 条目的保留策略取决于团队工作流：保留有利于复用旧翻译（如果消息后来又加回来），删除则保持 PO 文件整洁。

## 并行安全考虑

多进程编程需要考虑数据隔离和竞态条件。sphinx-intl 的设计天然避免了这些问题：

1. **进程隔离**：每个子进程独立加载和处理自己的文件，不共享内存状态
2. **无共享写入**：每个 UpdateItem 指向不同的 PO 文件，不同进程不会写入同一文件
3. **只读共享**：POT 文件只被读取，不被修改，多进程读取同一文件是安全的
4. **目录创建安全**：`os.makedirs(exist_ok=True)` 在多进程下也是安全的（exist_ok=True 保证目录已存在时不报错）

## 完整更新流程概览

```
sphinx-intl update -p _build/gettext -l ja -l de -j 4
│
├─ 参数校验
│   ├─ pot_dir 存在？→ 否则报错
│   └─ languages 非空？→ 否则报错
│
├─ 任务构建（主线程）
│   ├─ os.walk(pot_dir) 遍历所有 .pot 文件
│   ├─ 为每个 (pot, lang) 组合创建 UpdateItem
│   └─ 收集到 to_translate 列表
│
├─ 并行处理（4个子进程）
│   ├─ 子进程1: _update_single_file(item1) → UpdateResult
│   ├─ 子进程2: _update_single_file(item2) → UpdateResult
│   ├─ 子进程3: _update_single_file(item3) → UpdateResult
│   └─ 子进程4: _update_single_file(item4) → UpdateResult
│       │
│       ├─ 加载 POT
│       ├─ PO 存在？
│       │   ├─ 是 → 加载 PO → merge fuzzy → 检查变化 → 写入/跳过
│       │   └─ 否 → 设置 locale → 写入新 PO
│       └─ 返回 UpdateResult
│
└─ 结果汇总（主线程）
    ├─ 实时输出每个文件的状态
    └─ 返回 {'create': N, 'update': N, 'notchanged': N}
```

## 相关概念

- [翻译工作流原理](03-translation-workflow.md)
- [目录文件操作：Catalog 模块](04-catalog-operations.md)
- [编译与统计机制](06-build-stat-mechanism.md)
- [basic.py API 参考](/references/basic-api.md)
