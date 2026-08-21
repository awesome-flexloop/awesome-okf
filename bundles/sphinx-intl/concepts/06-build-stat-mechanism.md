---
type: concept
title: "编译与统计机制"
description: "sphinx-intl build 的 MO 增量编译逻辑、stat 的翻译进度统计原理、mtime 时间戳判断"
tags: [build, mo-compilation, stat, statistics, mtime, incremental]
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

# 编译与统计机制

本章解析 `sphinx-intl build`（PO→MO 编译）和 `sphinx-intl stat`（翻译统计）两个命令的内部实现。这两个命令相比 update 简单很多，但各自有值得了解的设计细节。

## build：MO 增量编译

`sphinx-intl build` 命令负责将文本格式的 PO 文件编译为二进制格式的 MO 文件。虽然 Sphinx 本身也能自动编译 MO，但使用 sphinx-intl build 可以预先编译好，避免构建文档时的额外开销。

### 编译流程 [F-048]

```python
def build(locale_dir, output_dir, languages):
    for lang in languages:
        lang_dir = os.path.join(locale_dir, lang)
        for dirpath, dirnames, filenames in os.walk(lang_dir):
            dirpath_output = os.path.join(
                output_dir, os.path.relpath(dirpath, locale_dir)
            )
            for filename in filenames:
                base, ext = os.path.splitext(filename)
                if ext != ".po":
                    continue
                mo_file = os.path.join(dirpath_output, base + ".mo")
                po_file = os.path.join(dirpath, filename)

                if os.path.exists(mo_file) and os.path.getmtime(
                    mo_file
                ) > os.path.getmtime(po_file):
                    continue
                click.echo(f"Build: {mo_file}")
                cat = c.load_po(po_file)
                c.write_mo(mo_file, cat)
```

### 增量编译：mtime 判断 [F-049]

build 命令最关键的设计是**基于文件修改时间（mtime）的增量编译**：

```python
if os.path.exists(mo_file) and os.path.getmtime(mo_file) > os.path.getmtime(po_file):
    continue  # 跳过，MO 已是最新
```

判断逻辑：
1. MO 文件不存在 → 需要编译
2. MO 文件存在但 PO 文件更新（po.mtime > mo.mtime）→ 需要重新编译
3. MO 文件存在且 MO 更新或时间相同 → 跳过

这避免了对未修改的 PO 文件重复编译，在大型项目中可以节省大量时间。

**注意**：mtime 比较使用 `>`（严格大于），而非 `>=`。如果 MO 和 PO 的 mtime 完全相同（极端情况），也会触发编译——这是保守策略，宁可多编译一次也不漏掉更新。

### output_dir 处理 [F-050]

```python
if not output_dir or (
    os.path.exists(output_dir) and os.path.samefile(locale_dir, output_dir)
):
    output_dir = locale_dir
```

- 如果未指定 `--output-dir`（`-o`），MO 文件输出到与 PO 相同的目录
- 如果指定了 output_dir 且与 locale_dir 是同一文件系统路径，也回退到 locale_dir
- 如果指定了不同的 output_dir，MO 文件输出到该目录下，保持相对目录结构

**output_dir 路径映射**：
```
PO: <locale_dir>/<lang>/LC_MESSAGES/index.po
MO: <output_dir>/<lang>/LC_MESSAGES/index.mo
```

使用 `os.path.relpath(dirpath, locale_dir)` 保持子目录结构。

### 为什么 MO 文件是必需的？

GNU gettext 运行时查找翻译的流程是：
1. 根据 locale 目录和语言代码定位到 `LC_MESSAGES` 目录
2. 加载 `.mo` 二进制文件（不是 `.po` 文本文件）
3. 使用哈希表在 MO 文件中 O(1) 查找 msgid 对应的 msgstr

MO 格式的优势：
- **加载速度快**：二进制格式，无需解析文本
- **查找效率高**：内置哈希表索引，O(1) 查找
- **体积更小**：二进制存储比文本 PO 更紧凑

虽然 Sphinx 在构建时如果找不到 MO 文件会自动从 PO 编译，但预先编译可以避免构建时的性能开销。

## stat：翻译进度统计

`sphinx-intl stat` 命令提供翻译完成度的快速概览。

### 统计流程 [F-051]

```python
def stat(locale_dir, languages):
    result = {}
    for lang in languages:
        lang_dir = os.path.join(locale_dir, lang)
        for dirpath, dirnames, filenames in os.walk(lang_dir):
            for filename in filenames:
                po_file = os.path.join(dirpath, filename)
                base, ext = os.path.splitext(po_file)
                if ext != ".po":
                    continue
                cat = c.load_po(po_file)
                r = result[po_file.replace("\\", "/")] = {
                    "translated": len(c.translated_entries(cat)),
                    "fuzzy": len(c.fuzzy_entries(cat)),
                    "untranslated": len(c.untranslated_entries(cat)),
                }
                click.echo(
                    "{}: {} translated, {} fuzzy, {} untranslated.".format(
                        po_file, r["translated"], r["fuzzy"], r["untranslated"],
                    )
                )
    return result
```

### 三类消息统计

stat 使用 catalog.py 的三个过滤函数统计：

| 类别 | 过滤函数 | 条件 | 含义 |
|------|---------|------|------|
| translated | `translated_entries(cat)` | `m.id and m.string` | 已翻译（有翻译字符串）|
| fuzzy | `fuzzy_entries(cat)` | `m.id and m.fuzzy` | 模糊标记（需审校）|
| untranslated | `untranslated_entries(cat)` | `m.id and not m.string` | 未翻译（翻译字符串为空）|

### 输出格式

每个 PO 文件输出一行：

```
locale/ja/LC_MESSAGES/index.po: 42 translated, 3 fuzzy, 5 untranslated.
locale/ja/LC_MESSAGES/install.po: 28 translated, 0 fuzzy, 2 untranslated.
```

同时返回一个字典，可以被程序调用：

```python
{
    "locale/ja/LC_MESSAGES/index.po": {
        "translated": 42,
        "fuzzy": 3,
        "untranslated": 5
    },
    ...
}
```

注意返回字典中的 key 做了路径标准化：`po_file.replace("\\", "/")`，将 Windows 反斜杠路径统一为正斜杠格式 [F-052]。

### 进度计算

基于三类计数可以计算翻译完成度：

```
完成率 = translated / (translated + fuzzy + untranslated) × 100%
```

fuzzy 条目的处理取决于团队策略：
- 有些团队将 fuzzy 视为"未完成"（需要审校）
- 有些团队将 fuzzy 视为"有参考翻译"（比完全未翻译好）

sphinx-intl 不做判断，只是如实报告三类计数。

## build 和 stat 的设计对比

| 特性 | build | stat |
|------|-------|------|
| 是否修改文件 | 是（写入 MO） | 否（只读） |
| 是否需要所有语言目录 | 是 | 是 |
| 增量逻辑 | mtime 比较跳过已编译 | 无（每次都重新统计）|
| 多进程支持 | 否（单进程顺序处理） | 否（单进程顺序处理）|
| 返回值 | None | dict（统计结果）|
| 输出 | "Build: <mo_file>" | "<file>: N translated, ..." |

### 为什么 build 不像 update 一样支持多进程？

1. **编译 MO 很快**：Babel 写入 MO 是简单的二进制序列化，比 PO 文本合并快得多
2. **I/O 密集为主**：编译主要是磁盘读写，多进程对 I/O 密集任务加速有限
3. **文件数量通常不多**：即使大型项目，PO 文件数量也通常在几十到几百，单进程足够快
4. **增量编译大幅减少工作量**：大部分文件在日常使用中会被 mtime 检查跳过

## 语言目录发现

build 和 stat 都使用同一个语言目录发现逻辑——通过 `get_lang_dirs()` 函数自动发现语言目录。

```python
def get_lang_dirs(path):
    dirs = [
        relpath(d, path)
        for d in glob(path + "/[a-z]*")
        if os.path.isdir(d) and not d.endswith("pot")
    ]
    return (tuple(dirs),)
```

匹配规则 [F-053]：
- 使用 glob 模式 `<path>/[a-z]*`：匹配以小写字母开头的目录
- 排除目录（`os.path.isdir`）
- 排除以 `pot` 结尾的目录（即 `pot/` POT 模板目录）
- 返回值包装在单元素元组中：`(('de', 'ja'),)`——这是为了与 `-l` 选项的多值格式保持一致（`-l` 可多次使用，每次返回一个 tuple）

**语言目录名必须小写字母开头**——这是 sphinx-intl 的一个隐式约定。如果语言代码以数字或大写字母开头（一般不会），可能无法被自动发现，需要通过 `-l` 显式指定。

## 相关概念

- [更新机制：多进程合并与 Fuzzy](05-update-mechanism.md)
- [目录文件操作：Catalog 模块](04-catalog-operations.md)
- [翻译工作流原理](03-translation-workflow.md)
