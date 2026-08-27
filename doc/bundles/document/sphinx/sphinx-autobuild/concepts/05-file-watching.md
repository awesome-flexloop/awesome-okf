---
type: Concept
title: 文件监听与过滤
description: IgnoreFilter 路径过滤机制、watchfiles 异步监听、默认忽略目录清单、调试模式用法
tags: [sphinx-autobuild, file-watching, ignore-filter, watchfiles, glob, regex]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-source
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild 源码信源登记
---

# 文件监听与过滤

## 文件监听机制

sphinx-autobuild 使用 [`watchfiles`](https://github.com/samuelcolvin/watchfiles) 库进行文件系统变化检测。`watchfiles` 是一个基于 Rust（通过 `watchfiles` Rust 核心库）的高性能文件监听库，在 Python 层提供了简洁的异步 API。

核心监听代码位于 `RebuildServer.watch()` 方法：

```python
async def watch(self) -> None:
    async for changes in watchfiles.awatch(
        *self.paths,
        watch_filter=lambda _, path: not self.ignore(path),
    ):
        changed_paths = [Path(path).resolve() for (_, path) in changes]
        with ProcessPoolExecutor() as pool:
            fut = pool.submit(self.change_callback, changed_paths=changed_paths)
            await asyncio.wrap_future(fut)
        self.flag.set()
```

### watchfiles.awatch() 特性

- **异步迭代器**：`async for changes in watchfiles.awatch(...)` 以异步方式迭代变化事件批次
- **多路径监听**：通过 `*self.paths` 传入多个监听目录（源目录 + `--watch` 指定的额外目录）
- **过滤回调**：`watch_filter` 参数接收一个回调函数 `(change_type, path) -> bool`，返回 `True` 表示保留该变化，`False` 表示忽略
- **变化事件格式**：每个 `changes` 是一个 `set` 的 `(Change, path)` 元组，`Change` 是枚举类型（added/modified/deleted）

### 监听路径

默认监听路径包括：

1. **源文件目录**（`src_dir`）：Sphinx 文档源文件目录
2. **额外监听目录**（`--watch DIR`）：用户通过 `--watch` 选项添加的目录，常用于监听主题源码、扩展源码等

## IgnoreFilter 类

`IgnoreFilter` 位于 `sphinx_autobuild/filter.py`，决定哪些文件变化应该被忽略。它是一个可调用对象，实现了双模式匹配。

### 初始化

```python
class IgnoreFilter:
    def __init__(self, regular, regex_based):
        normalised_paths = [Path(p).resolve().as_posix() for p in regular]
        self.regular_patterns = list(dict.fromkeys(normalised_paths))
        self.regex_based_patterns = [*map(re.compile, dict.fromkeys(regex_based))]
```

参数：

| 参数 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `regular` | `list[str]` | 默认忽略目录 + `--ignore` | glob 模式或目录路径列表 |
| `regex_based` | `list[str]` | `--re-ignore` | 正则表达式字符串列表 |

初始化时的关键处理：

1. **路径归一化**：所有路径通过 `Path(p).resolve().as_posix()` 转换为绝对路径的正斜杠格式，确保跨平台一致性
2. **去重**：使用 `dict.fromkeys()`（Python 3.7+ 保持插入顺序的字典）去除重复模式
3. **正则预编译**：正则表达式在初始化时一次性编译为 `re.Pattern` 对象，避免每次调用时重复编译

### 匹配逻辑

```python
def __call__(self, filename: str, /):
    normalised_path = Path(filename).resolve().as_posix()
    
    # 调试输出
    if os.getenv("SPHINX_AUTOBUILD_DEBUG") not in {None, "", "0"}:
        print(f"SPHINX_AUTOBUILD_DEBUG: {normalised_path!r} has changed; ignores are {self}")
    
    # 1. 路径前缀/glob 匹配
    for pattern in self.regular_patterns:
        if normalised_path.startswith(f"{pattern}/"):
            return True
        if fnmatch.fnmatch(normalised_path, pattern):
            return True
    
    # 2. 正则表达式匹配
    for regex in self.regex_based_patterns:
        if regex.search(normalised_path):
            return True
    
    return False
```

#### 两层匹配机制

**第一层：路径前缀 + glob 匹配（regular_patterns）**

- **前缀匹配**：`normalised_path.startswith(f"{pattern}/")` —— 如果路径以某个忽略目录开头（加 `/` 防止前缀误匹配，如 `/foo` 匹配 `/foo/bar` 但不匹配 `/foobar`）
- **glob 匹配**：`fnmatch.fnmatch(normalised_path, pattern)` —— 使用标准库 fnmatch 进行通配符匹配（`*`、`?`、`[seq]`）

**第二层：正则表达式匹配（regex_based_patterns）**

- `regex.search(normalised_path)` —— 在归一化路径中搜索正则匹配项（注意是 `search` 而非 `match`，即不需要从开头匹配）

#### 返回值语义

- 返回 `True`：文件应该被**忽略**（不触发重建）
- 返回 `False`：文件应该被**监听**（触发重建）

注意这个语义与直觉可能相反：`watch_filter=lambda _, path: not self.ignore(path)` 中使用了 `not`，因为 `watchfiles` 的过滤器返回 `True` 表示"保留这个事件"。

### __repr__ 调试表示

```python
def __repr__(self):
    return (
        f"IgnoreFilter(regular={self.regular_patterns!r}, "
        f"regex_based={self.regex_based_patterns!r})"
    )
```

在调试模式下，每次文件变化都会打印当前的 IgnoreFilter 配置，帮助排查过滤规则。

## 默认忽略目录

sphinx-autobuild 在 `__main__.py` 的 `main()` 函数中构建了一个全面的默认忽略列表：

```python
ignore_dirs = [
    ".git", ".hg", ".svn",                    # 版本控制
    ".idea", ".vscode",                       # IDE 配置
    ".mypy_cache", ".ruff_cache",             # 类型检查/Linter 缓存
    ".pytest_cache", ".pytype",               # 测试/类型检查缓存
    ".nox", ".tox",                           # 测试环境管理
    ".venv", "venv",                          # Python 虚拟环境
    "node_modules",                           # Node.js 依赖
    out_dir,                                  # Sphinx 输出目录（必须忽略！）
    args.warnings_file,                       # warnings 文件（构建时写入）
    args.doctree_dir,                         # doctree 缓存目录
    *args.ignore,                             # 用户通过 --ignore 添加的
]
ignore_dirs = list(filter(None, ignore_dirs))  # 移除 None 值
```

### 为什么输出目录必须被忽略？

Sphinx 构建会写入 `out_dir`（如 `docs/_build/html/`），如果不忽略输出目录，构建写入的 HTML 文件会触发 watchfiles 检测到变化，从而导致无限循环：构建→写入文件→检测变化→再次构建→...

这是文档预览工具中一个经典的问题，sphinx-autobuild 通过默认将输出目录加入忽略列表来避免。

### doctree 和 warnings 文件

Sphinx 使用 `-d` 选项指定的 doctree 目录（默认 `_build/.doctrees`）存储解析后的文档树缓存，构建时会写入；`-w` 选项指定的 warnings 文件也在构建时写入。这两个目录/文件同样会在构建时被修改，如果不忽略会导致不必要的重建。

## 调试模式

设置环境变量 `SPHINX_AUTOBUILD_DEBUG` 为非空非零值可以启用调试输出：

```bash
# Linux/macOS
SPHINX_AUTOBUILD_DEBUG=1 sphinx-autobuild docs docs/_build/html

# Windows PowerShell
$env:SPHINX_AUTOBUILD_DEBUG = "1"
sphinx-autobuild docs docs/_build/html
```

启用后，每次文件变化都会打印类似：

```
SPHINX_AUTOBUILD_DEBUG: '/home/user/project/docs/index.rst' has changed; ignores are IgnoreFilter(regular=[...], regex_based=[...])
```

这对于排查"为什么我的文件修改没有触发重建"或"为什么忽略规则没有生效"非常有用。

调试模式的判断条件是：

```python
if os.getenv("SPHINX_AUTOBUILD_DEBUG") not in {None, "", "0"}:
```

即以下值会**禁用**调试：未设置、空字符串、`"0"`；其他任何值（`"1"`、`"y"`、`"true"`、`"whatever"`）都会启用调试。

## 配置忽略规则的最佳实践

### 添加自定义忽略

```bash
# 忽略所有 .tmp 文件
sphinx-autobuild --re-ignore '\.tmp$' docs docs/_build/html

# 忽略 build 目录
sphinx-autobuild --ignore 'build' docs docs/_build/html

# 多个忽略规则
sphinx-autobuild \
  --re-ignore '\.log$' \
  --re-ignore '\.tmp$' \
  --ignore 'draft' \
  docs docs/_build/html
```

### 监听额外目录

```bash
# 同时监听主题源码目录
sphinx-autobuild --watch path/to/theme docs docs/_build/html

# 监听多个额外目录
sphinx-autobuild \
  --watch ../my-theme/src \
  --watch ../my-extension/sphinx_ext \
  docs docs/_build/html
```

主题开发时建议同时使用 `-a`（全量重建）选项，因为 Sphinx 增量构建可能无法正确检测主题静态文件的变化。

## 相关概念

- [架构概览](02-architecture-overview.md)
- [服务器与热重载](06-server-and-hotreload.md)
- [构建系统](04-builder-system.md)
- [主题开发工作流](../examples/theme-development.md)
- [sphinx-autobuild 源码信源登记](../references/sphinx-autobuild-source.md)
