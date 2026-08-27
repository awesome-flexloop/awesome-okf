---
type: Concept
title: 路径处理与跨平台兼容
description: rediraffe的路径标准化机制——Windows/POSIX路径转换、dirhtml目录URL处理、增量构建JSON记录、冲突检测
tags: [sphinxext-rediraffe, path, cross-platform, dirhtml, incremental-build, json-record]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# 路径处理与跨平台兼容

rediraffe 需要在多种路径格式之间转换——用户配置中的路径、Sphinx源文件路径、构建输出路径、URL路径——同时保证在 Windows、Linux、macOS 上行为一致。

## 路径处理流程

重定向路径的转换经过以下步骤：

```
用户配置路径（.rst/.md）
    │
    ├─ 1. PureWindowsPath 标准化
    │     （统一处理反斜杠/正斜杠/混合斜杠）
    │
    ├─ 2. remove_suffix 移除源文件后缀
    │     （.rst/.rst.txt/.md等）
    │
    ├─ 3. 添加 .html 后缀
    │
    ├─ 4. dirhtml特殊处理（可选）
    │     非index文件：page.html → page/index.html
    │
    ├─ 5. 拼接 outdir 得到绝对路径
    │
    ├─ 6. 冲突检测（源已存在/目标不存在）
    │
    └─ 7. relpath 计算相对URL
          → PureWindowsPath → PurePosixPath → 正斜杠URL
```

## 跨平台路径标准化

### Windows路径问题

在Windows上，路径分隔符是反斜杠（`\`），但URL必须使用正斜杠（`/`）。Sphinx项目可能在Windows上开发、在Linux上构建（CI/CD），路径格式不一致。

rediraffe 使用 `PureWindowsPath` 做第一层标准化：

```python
src_redirect_from = Path(PureWindowsPath(src_redirect_from))
src_redirect_to = Path(PureWindowsPath(src_redirect_to))
```

`PureWindowsPath` 能正确处理：
- 正斜杠：`docs/folder1/f1.rst`
- 反斜杠：`docs\\folder1\\f1.rst`
- 混合斜杠：`docs\\folder1/f1.rst`
- Windows盘符：`C:\\docs\\page.rst`（但重定向路径通常是相对路径）

这三种格式在测试中都有覆盖：
- `test-backslashes`：反斜杠路径
- `test-mixed_slashes`：混合斜杠路径
- `test-nested`：正斜杠路径

### POSIX输出转换

计算相对URL后，使用 `PurePosixPath` 确保输出正斜杠：

```python
rel_url=str(
    PurePosixPath(
        PureWindowsPath(
            relpath(build_redirect_to, build_redirect_from.parent)
        )
    )
)
```

`relpath()` 在Windows上返回反斜杠路径，经 `PureWindowsPath` 解析后再用 `PurePosixPath` 转换为正斜杠，最终写入HTML中的URL始终是正斜杠格式。

### 点号文件名处理

文件名中包含点号（如 `a.b.c.rst`）需要特殊处理。`remove_suffix` 只移除**已知的源文件后缀**：

```python
def remove_suffix(docname: str, suffixes: list[str]) -> str:
    for suffix in suffixes:
        if docname.endswith(suffix):
            return docname[: -len(suffix)]
    return docname
```

这确保 `docs/a.b.c.rst` 被正确转换为 `docs/a.b.c.html`，而不是被错误地截断为 `docs/a.b.html`。测试用例 `test-dot-in-filename` 验证了这一点。

## dirhtml 目录URL处理

DirectoryHTMLBuilder（`-b dirhtml`）将页面输出为目录结构：

```
html构建器输出：          dirhtml构建器输出：
├── page.html             ├── page/
└── index.html            │   └── index.html
                          └── index.html
```

rediraffe 针对 dirhtml 做特殊路径转换：

```python
if type(app.builder) is DirectoryHTMLBuilder:
    if redirect_from_name != 'index':
        redirect_from = src_redirect_from.parent / redirect_from_name / 'index.html'
    if redirect_to_name != 'index':
        redirect_to = src_redirect_to.parent / redirect_to_name / 'index.html'
```

关键规则：
- 名为 `index` 的文件不变：`index.rst` → `index.html`
- 非index文件转为目录：`page.rst` → `page/index.html`
- 源和目标都需要独立判断（源可能是普通页，目标可能是index）

### dirhtml相对URL差异

由于目录层级不同，dirhtml的 `rel_url` 会包含更多 `../`：

**配置**：`another.rst → index.rst`

| 构建器 | from_url | to_url | rel_url |
|--------|----------|--------|---------|
| html | `another.html` | `index.html` | `index.html` |
| dirhtml | `another/index.html` | `index.html` | `../index.html` |

测试验证：`test_jinja` 在dirhtml下断言 `rel_url: ../index.html`。

## 源文件后缀处理

Sphinx支持多种源文件后缀（通过 `source_suffix` 配置），默认是 `.rst`，但也可以配置为：

```python
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
    '.rst.txt': 'restructuredtext',
}
```

`remove_suffix` 函数遍历配置的后缀列表，只移除匹配的后缀：

```python
redirect_from_name = remove_suffix(src_redirect_from.name, app.config.source_suffix)
```

注意 `app.config.source_suffix` 在旧版Sphinx中是列表，在新版中是dict。rediraffe 传入的是后缀列表/字典键，`endswith` 对两种类型都能工作（dict迭代时返回key）。

## 冲突与错误检测

在写入重定向文件之前，`build_redirects` 执行多项检测：

### 1. 源文件已存在（冲突）

```python
if build_redirect_from.exists():
    logger.warning(
        '%s %s redirects to %s but %s already exists!',
        yellow('(broken)'), redirect_from, redirect_to, build_redirect_from
    )
    app.statuscode = 1
    continue
```

当重定向源位置已经有一个HTML文件时（即该页面实际被Sphinx构建出来了），rediraffe不会覆盖它，而是报告警告。这种情况通常发生在配置错误（把一个存在的页面配置为重定向源）。

**例外：增量更新**

```python
if (build_redirect_from.exists()
    and src_redirect_from.as_posix() in redirect_record):
    if redirect_record[src_redirect_from.as_posix()] == src_redirect_to.as_posix():
        continue  # 目标未变，跳过
    build_redirect_from.unlink()  # 目标变了，删除旧文件重写
```

如果重定向文件已存在于JSON记录中且目标相同，跳过；如果目标变了，删除旧文件后重新生成。

### 2. 目标文件不存在

```python
if not build_redirect_to.exists():
    logger.warning(
        '%s %s redirects to %s but %s does not exist!',
        yellow('(broken)'), redirect_from, redirect_to, build_redirect_to
    )
    app.statuscode = 1
    continue
```

当重定向目标页面不存在时，报告警告。可能原因：
- 目标路径拼写错误
- 目标页面被排除在构建之外（`exclude_patterns`）
- 链式重定向的最终叶子页面不存在

### 3. 错误状态码

所有检测到的问题都会设置 `app.statuscode = 1`，导致 `sphinx-build` 命令以非零退出码结束，可以在CI中检测到。

## 增量构建JSON记录

### _rediraffe_redirected.json 格式

rediraffe 使用 `_rediraffe_redirected.json` 文件记录已生成的重定向：

```json
{
  "old-page.rst": "new-page.rst",
  "legacy/intro.rst": "guide/introduction.rst"
}
```

key是源文件路径（POSIX格式），value是目标文件路径（POSIX格式）。

### 增量构建流程

```python
# 读取上次记录
redirect_json_file = Path(app.outdir) / REDIRECT_JSON_NAME
if redirect_json_file.exists():
    redirect_record = json.loads(redirect_json_file.read_bytes())
else:
    redirect_record = {}

# ... 生成重定向 ...

# 更新记录
redirect_record[src_redirect_from.as_posix()] = src_redirect_to.as_posix()

# 写入记录
redirect_json_file.write_text(json.dumps(redirect_record), encoding='utf8')
```

增量构建的好处：
1. **跳过未变更的重定向**：如果重定向关系未变且HTML已存在，不重复写入
2. **检测变更**：如果目标变了，删除旧文件重写
3. **清理旧重定向**：不在新配置中的重定向源不会被自动删除（JSON记录只追加/更新），如果需要清理需手动删除JSON文件

### 强制重新生成

如果需要强制重新生成所有重定向文件：

```bash
# 方法1：删除JSON记录文件和输出目录
rm -rf _build/html/_rediraffe_redirected.json
sphinx-build -b html . _build/html

# 方法2：完全清理构建目录
make clean && make html
```

## 从已删除目录重定向

rediraffe 支持从已不存在的目录重定向。例如，如果原来有 `deletedfolder/another.rst` 页面，整个目录被删除了，可以配置：

```python
rediraffe_redirects = {
    'deletedfolder/another.rst': 'index.rst',
    'deletedfolder/deletedfolder2/another.rst': 'index.rst',
}
```

关键代码：
```python
build_redirect_from.parent.mkdir(parents=True, exist_ok=True)
```

写入重定向文件前，会自动创建所有必需的父目录，即使源目录在文件系统中已被删除。测试用例 `test-redirect_from_deleted_folder` 验证了此功能。

## 路径相关测试覆盖

| 测试用例 | 覆盖场景 |
|---------|---------|
| `test-nested` | 嵌套目录正斜杠路径 |
| `test-backslashes` | Windows反斜杠路径 |
| `test-mixed_slashes` | 混合斜杠路径 |
| `test-dot_in_filename` | 文件名含点号 |
| `test-dirhtml_user_index_files` | dirhtml用户自定义index文件 |
| `test-redirect_from_deleted_folder` | 已删除目录的重定向 |

## 相关概念

- [架构概览](02-architecture-overview.md)
- [Builder体系详解](05-builders.md)
- [Jinja2模板系统](06-jinja-templates.md)
- [基础重定向示例](../examples/basic-redirects.md)
