---
type: concept
title: "目录文件操作：Catalog 模块"
description: "catalog.py 对 Babel 库的封装——PO/POT/MO 读写、两阶段 charset 探测、条目过滤"
tags: [catalog, babel, po, pot, mo, file-io, charset]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: catalog-api
    resource: /references/catalog-api.md
    title: "catalog.py PO/POT/MO 文件操作 API 参考"
---

# 目录文件操作：Catalog 模块

`sphinx_intl/catalog.py` 是 sphinx-intl 的文件 I/O 层，提供 PO/POT/MO 文件的读写和条目过滤功能。它是对 Babel 库 `babel.messages.pofile` 和 `babel.messages.mofile` 模块的轻量封装，增加了编码探测和目录自动创建等便利功能。

## 模块定位

```
commands.py → basic.py → catalog.py → babel.messages.pofile/mofile
   CLI层      业务逻辑层    文件I/O层     底层实现（Babel库）
```

catalog.py 不包含业务逻辑，只负责：
1. 文件读写（PO/POT/MO）
2. 编码处理（charset 探测）
3. 条目过滤（translated/fuzzy/untranslated）
4. 目录合并（update_with_fuzzy）

所有业务函数（update/build/stat）都通过 catalog.py 操作翻译文件。

## PO/POT 文件读取：load_po

```python
def load_po(filename, **kwargs):
```

`load_po` 读取 PO 或 POT 文件并返回 Babel 的 `Catalog` 对象。它实现了一个巧妙的**两阶段 charset 探测**机制。

### 为什么需要两阶段读取？

PO 文件的编码信息存储在文件头部的 `Content-Type` 头中：

```po
"Content-Type: text/plain; charset=UTF-8\n"
```

但要读取这个头部，需要先打开文件——这就产生了"鸡生蛋"问题：不知道编码就无法正确解析文件，但编码信息又在文件中。

### 两阶段读取方案 [F-033]

**第一阶段：探测编码**
```python
with open(filename, "rb") as f:
    cat = pofile.read_po(f)
charset = cat.charset or "utf-8"
```
以二进制模式打开文件，让 Babel 尝试解析。Babel 的 `read_po` 在不指定 charset 时能以容错方式读取头部信息，从中提取 charset 声明。

**第二阶段：使用正确编码重读**
```python
with open(filename, "rb") as f:
    return pofile.read_po(f, charset=charset, **kwargs)
```
用探测到的 charset 再次以二进制模式打开文件，这次 Babel 使用正确的编码解析所有字符串。

默认 charset 为 `utf-8`，如果头部没有声明编码则使用 UTF-8。

**关键细节**：两次都使用 binary mode（`"rb"`）打开文件，而不是文本模式。这是因为 Babel 的 `read_po` 期望接收字节流并自行处理编码转换，传入文本流可能导致双重编码问题。

## PO 文件写入：dump_po

```python
def dump_po(filename, catalog, **kwargs):
```

将 Babel `Catalog` 对象写入 PO 文件。

### 自动创建目录 [F-034]

```python
dirname = os.path.dirname(filename)
os.makedirs(dirname, exist_ok=True)
```

写入前自动确保目标目录存在，调用者不需要手动创建 `LC_MESSAGES` 等子目录。这就是为什么 `sphinx-intl update` 可以自动创建完整的目录结构。

### line_width → width 兼容处理 [F-035]

```python
if "line_width" in kwargs:
    kwargs["width"] = kwargs["line_width"]
    del kwargs["line_width"]
```

早期版本使用 `line_width` 参数名，Babel 库使用 `width`。这里做了兼容转换，保持向后兼容。

### 二进制写入

```python
with open(filename, "wb") as f:
    pofile.write_po(f, catalog, **kwargs)
```

同样使用 binary mode（`"wb"`），让 Babel 自行处理编码输出。

## MO 文件写入：write_mo

```python
def write_mo(filename, catalog, **kwargs):
```

将 Catalog 对象编译写入 MO 二进制文件。

同样自动创建目录（`os.makedirs(dirname, exist_ok=True)`），使用 binary mode 写入。

注意：catalog.py 中**没有 `load_mo` 函数**——MO 是编译输出格式，sphinx-intl 不需要读取 MO 文件，MO 文件由 Sphinx 运行时加载。

## 条目过滤函数

catalog.py 提供三个简单但常用的条目过滤函数，用于 `stat` 命令统计翻译进度。

### translated_entries(catalog) [F-036]

```python
def translated_entries(catalog):
    return [m for m in catalog if m.id and m.string]
```

返回所有已翻译的消息条目。条件：消息 ID 非空且翻译字符串非空。

Babel 的 Catalog 对象是可迭代的，每次迭代返回一个 `Message` 对象。

### fuzzy_entries(catalog) [F-037]

```python
def fuzzy_entries(catalog):
    return [m for m in catalog if m.id and m.fuzzy]
```

返回所有标记为 fuzzy（模糊）的消息条目。Fuzzy 标记表示该翻译需要人工审校——通常由 `update_with_fuzzy` 自动添加到新增/变更的消息上。

### untranslated_entries(catalog) [F-038]

```python
def untranslated_entries(catalog):
    return [m for m in catalog if m.id and not m.string]
```

返回所有未翻译的消息条目。条件：消息 ID 非空且翻译字符串为空。

### 三类条目的关系

一个消息条目属于且仅属于以下三种状态之一（对于有 m.id 的消息）：

| 状态 | 条件 | 含义 |
|------|------|------|
| translated | `m.id and m.string and not m.fuzzy` | 已完成翻译 |
| fuzzy | `m.id and m.fuzzy` | 翻译存在但需审校 |
| untranslated | `m.id and not m.string` | 尚未翻译 |

注意：fuzzy 条目的 `m.string` 通常也非空（可能是机器翻译或旧翻译），所以 fuzzy 检查应优先于 translated。catalog.py 的三个过滤函数是**独立查询**而非互斥分类，fuzzy 条目可能同时满足 translated 的条件（`m.string` 非空）。

## 目录合并：update_with_fuzzy

```python
def update_with_fuzzy(catalog, catalog_source):
    catalog.update(catalog_source)
```

这个函数名有一定误导性——它本身不直接处理 fuzzy 标记，而是调用 Babel 的 `catalog.update()` 方法。Babel 的 update 方法在合并新消息时会自动将新增/变更的消息标记为 fuzzy。

### Babel catalog.update() 的行为

当使用 POT 模板更新 PO 时，Babel 的 update 方法执行以下操作：

1. **匹配消息**：通过 msgid 匹配现有消息和模板消息
2. **新增消息**：模板中有但 PO 中没有的消息，添加到 PO 并标记为 fuzzy
3. **变更消息**：msgid 发生变化的消息（Babel 通过相似度匹配），保留旧翻译但标记为 fuzzy
4. **过时消息**：PO 中有但模板中没有的消息，标记为 obsolete（不删除）
5. **位置更新**：更新 `#:` 注释中的文件位置信息
6. **保留翻译**：msgid 完全匹配的已有翻译保持不变，不标记 fuzzy

fuzzy 标记的作用是提醒翻译人员：这些条目可能需要重新审校。翻译人员确认翻译正确后，需要手动移除 `#, fuzzy` 标记。

## Babel Catalog 对象

sphinx-intl 通过 catalog.py 返回的核心数据结构是 Babel 的 `babel.support.Catalog` 对象（在新版本 Babel 中为 `babel.messages.catalog.Catalog`）。以下是 Catalog 的关键属性和方法（由 Babel 库提供）：

| 属性/方法 | 说明 |
|----------|------|
| `catalog.charset` | 文件编码（如 'UTF-8'）|
| `catalog.locale` | 语言区域（Locale 对象）|
| `catalog[msgid]` | 通过 msgid 索引获取 Message 对象 |
| `catalog.update(template)` | 用模板更新目录 |
| `for m in catalog` | 迭代所有 Message 对象 |

### Message 对象

| 属性 | 说明 |
|------|------|
| `m.id` | 消息 ID（原始字符串），可以是 str 或 (str, str) 元组（复数形式）|
| `m.string` | 翻译字符串 |
| `m.fuzzy` | 是否为 fuzzy 标记 |
| `m.locations` | 来源位置列表 `[(filename, lineno), ...]` |
| `m.comments` | 翻译者注释 |
| `m.flags` | 标志集合（如 {'fuzzy', 'python-format'}）|

## 设计特点总结

1. **薄封装**：catalog.py 只有约 80 行代码，是 Babel 库的极薄封装层
2. **二进制 I/O**：所有文件操作都使用 binary mode，交由 Babel 处理编码
3. **两阶段编码探测**：巧妙解决"编码信息在文件中"的鸡生蛋问题
4. **目录自动创建**：写入时自动 `os.makedirs(exist_ok=True)`，简化调用方代码
5. **函数式过滤**：三个过滤函数都是简单的列表推导，无副作用

## 相关概念

- [翻译工作流原理](03-translation-workflow.md)
- [更新机制：多进程合并与 Fuzzy](05-update-mechanism.md)
- [编译与统计机制](06-build-stat-mechanism.md)
- [catalog.py API 参考](../references/catalog-api.md)
