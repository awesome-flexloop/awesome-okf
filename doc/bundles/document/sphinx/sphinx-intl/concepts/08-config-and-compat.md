---
type: concept
title: "配置读取与 Python 兼容层"
description: "sphinx-intl 如何读取 Sphinx conf.py 配置、Tags 类实现、Python 2/3 兼容层设计"
tags: [config, conf.py, tags, compatibility, pycompat, execfile]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: commands-api
    resource: /references/commands-api.md
    title: "commands.py CLI 入口 API 参考"
---

# 配置读取与 Python 兼容层

本章解析 sphinx-intl 读取 Sphinx `conf.py` 配置的机制、Tags 类的实现，以及 Python 兼容层（pycompat.py）的设计。这些是 sphinx-intl 与 Sphinx 生态对接的关键"胶水代码"。

## conf.py 配置读取

sphinx-intl 的一个便利特性是自动读取 Sphinx 的 `conf.py` 文件来获取 `locale_dirs` 配置，免去用户每次手动指定 `-d` 参数的麻烦。

### read_config 函数 [F-060]

```python
def read_config(path, passed_tags):
    tags = Tags()
    passed_tags = sum(passed_tags, ())  # 展平嵌套 tuple
    for tag in passed_tags:
        tags.add(tag)

    namespace = {
        "__file__": os.path.abspath(path),
        "tags": tags,
    }

    olddir = os.getcwd()
    try:
        if not os.path.isfile(path):
            msg = "'%s' is not found (or specify --locale-dir option)." % path
            raise click.BadParameter(msg)
        os.chdir(os.path.dirname(path) or ".")
        execfile_(os.path.basename(path), namespace)
    finally:
        os.chdir(olddir)

    return namespace
```

### 执行 conf.py 的关键设计

**1. 模拟 Sphinx 执行环境**

Sphinx 的 conf.py 不是普通的配置文件——它是一个 Python 脚本，执行时依赖特定的命名空间。sphinx-intl 注入两个关键变量：

- `__file__`：conf.py 文件的绝对路径。conf.py 中可能使用 `__file__` 来计算相对路径
- `tags`：一个 Tags 对象，用于支持 `only` 指令和条件配置（与 `sphinx-build -t <tag>` 一致）

**2. 工作目录切换** [F-061]

```python
os.chdir(os.path.dirname(path) or ".")
try:
    execfile_(os.path.basename(path), namespace)
finally:
    os.chdir(olddir)
```

conf.py 的执行目录切换到 conf.py 所在目录。这是因为 Sphinx 在执行 conf.py 时也是在 conf.py 所在目录执行的，conf.py 中可能使用相对路径引用其他文件（如 `sys.path.insert(0, os.path.abspath('.'))`）。

使用 `try/finally` 确保无论执行成功还是失败，工作目录都会恢复。

**3. execfile_ 而非 exec**

不直接使用 Python 内置的 `exec()`，而是通过 pycompat.py 的 `execfile_()` 函数执行。这是为了兼容 Python 2 语法的 conf.py 文件（详见下文）。

### 获取 locale_dirs 配置

main 函数在 read_config 返回的 namespace 中查找 `locale_dirs`：

```python
cfg = read_config(ctx.config, tag)
locale_dirs = cfg.get("locale_dirs", ["locales"])
ctx.locale_dir = os.path.join(os.path.dirname(ctx.config), locale_dirs[0])
```

- 默认为 `['locales']`（Sphinx 的默认 locale 目录名）
- 取列表第一个目录作为 locale_dir
- 拼接为相对于 conf.py 的绝对路径

### -t/--tag 选项的作用

`-t/--tag` 选项传递标签给 conf.py，与 `sphinx-build -t <tag>` 功能一致。这在 conf.py 中使用条件配置时非常有用：

```python
# conf.py
if tags.has('draft'):
    exclude_patterns = ['draft/*.rst']
else:
    exclude_patterns = []
```

通过 `-t draft` 可以启用 draft 模式的配置。

## Tags 类：sphinx_util.py

sphinx_util.py 中定义了一个 Tags 类，这是从 Sphinx 源码中移植过来的精简版本 [F-062]。

```python
class Tags:
    def __init__(self, tags: list[str] = None) -> None:
        self.tags = dict.fromkeys(tags or [], True)

    def has(self, tag: str) -> bool:
        return tag in self.tags

    __contains__ = has  # 支持 `tag in tags` 语法

    def __iter__(self) -> Iterator[str]:
        return iter(self.tags)

    def add(self, tag: str) -> None:
        self.tags[tag] = True

    def remove(self, tag: str) -> None:
        self.tags.pop(tag, None)
```

### 为什么本地移植 Tags？

1. **减少耦合**：不依赖 Sphinx 内部 API（`sphinx.util.tags.Tags`），避免 Sphinx 版本升级导致 API 变化
2. **最小依赖**：Tags 类非常简单（约 15 行代码），不值得为此导入整个 Sphinx 包
3. **兼容性保证**：自己控制实现，确保在各种 Sphinx 版本下行为一致

实际上，commands.py 顶部同时导入了 Sphinx 的 Tags 和本地 Tags：

```python
from sphinx.util.tags import Tags  # Sphinx 的 Tags
```

但 sphinx_util.py 也定义了一份 Tags。在 read_config 中实际使用的 Tags 类来源需要注意——代码中 `tags = Tags()` 直接引用了从 Sphinx 导入的 Tags，而 sphinx_util.py 的 Tags 是冗余移植，可能为未来解耦做准备。

## Python 兼容层：pycompat.py

pycompat.py 提供 Python 2/3 兼容功能，核心是 `execfile_()` 函数。

### execfile_：安全执行 conf.py [F-063]

```python
def execfile_(filepath: str, _globals: Any, open: Callable = open) -> None:
    with open(filepath, "rb") as f:
        source = f.read()

    filepath_enc = filepath.encode(fs_encoding)
    try:
        code = compile(source, filepath_enc, "exec")
    except SyntaxError:
        # 可能是 Python 2 语法，尝试用 2to3 转换
        source = convert_with_2to3(filepath)
        code = compile(source, filepath_enc, "exec")
        warnings.warn(
            "Support for evaluating Python 2 syntax is deprecated "
            "and will be removed in sphinx-intl 4.0. "
            "Convert %s to Python 3 syntax.",
            source=filepath,
        )
    exec(code, _globals)
```

### 智能语法降级处理

execfile_ 实现了优雅的 Python 2 兼容：

1. **先尝试 Python 3 编译**：读取文件后直接 `compile(source, ..., "exec")`
2. **如果 SyntaxError**：假设文件使用 Python 2 语法，调用 `convert_with_2to3()` 转换
3. **编译转换后的代码**并发出 DeprecationWarning
4. **执行编译后的 code object**

这种"先尝试、失败再降级"的策略比一开始就做 2to3 转换更高效——绝大多数 conf.py 已经是 Python 3 语法。

### convert_with_2to3：Python 2→3 自动转换 [F-064]

```python
def convert_with_2to3(filepath: str) -> str:
    from lib2to3.refactor import RefactoringTool, get_fixers_from_package
    from lib2to3.pgen2.parse import ParseError

    fixers = get_fixers_from_package("lib2to3.fixes")
    refactoring_tool = RefactoringTool(fixers)
    source = refactoring_tool._read_python_source(filepath)[0]
    try:
        tree = refactoring_tool.refactor_string(source, "conf.py")
    except ParseError as err:
        lineno, offset = err.context[1]
        raise SyntaxError(err.msg, (filepath, lineno, offset, err.value))
    return str(tree)
```

使用标准库 `lib2to3` 模块自动将 Python 2 语法转换为 Python 3。处理的转换包括：`print` 语句→函数、`xrange`→`range`、`except Exception, e`→`except Exception as e` 等。

> **注意**：`lib2to3` 在 Python 3.13+ 中已被标记为废弃（PEP 594），未来版本可能移除。这也是 Python 2 兼容功能计划在 sphinx-intl 4.0 中移除的原因。

### relpath：跨平台相对路径 [F-065]

```python
def relpath(path: str, start: str = os.curdir) -> str:
    try:
        return os.path.relpath(path, start)
    except ValueError:
        return path
```

对 `os.path.relpath` 的安全包装。在 Windows 上当 path 和 start 在不同驱动器上时（如 `D:\foo` 和 `C:\bar`），`os.path.relpath` 会抛出 `ValueError`。relpath 在这种情况下回退到返回原始路径，避免崩溃。

### fs_encoding：文件系统编码 [F-066]

```python
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
```

用于将文件路径编码为字节串（`filepath.encode(fs_encoding)`），这在 compile() 函数中作为 filename 参数使用，影响错误 traceback 中的路径显示。

## 配置自动检测总结

sphinx-intl 启动时的配置自动检测流程：

```
sphinx-intl <command>
│
├─ 1. 查找 conf.py
│   ├─ -c 显式指定？→ 使用指定路径
│   └─ 自动查找：./conf.py → ./source/conf.py
│
├─ 2. 读取配置（如果找到 conf.py）
│   ├─ 创建 Tags 对象，添加 -t 标签
│   ├─ 切换到 conf.py 目录
│   ├─ execfile_ 执行 conf.py（Python 3 优先，2→3 降级）
│   ├─ 恢复工作目录
│   └─ 从 namespace 获取 locale_dirs（默认 ['locales']）
│
├─ 3. 查找 POT 目录
│   └─ 依次检查：_build/gettext → build/gettext → _build/locale → build/locale
│
├─ 4. 查找 Transifex 项目名
│   └─ 解析 .tx/config 中的 [project.resource] 格式
│
└─ 5. 通过 ctx.default_map 注入子命令默认值
    ├─ update: locale_dir, pot_dir
    ├─ build: locale_dir
    ├─ stat: locale_dir
    └─ update-txconfig-resources: locale_dir, pot_dir, transifex_project_name
```

这种多层自动检测让用户在标准 Sphinx 项目中几乎不需要指定任何路径参数——直接在项目根目录运行 `sphinx-intl update` 就能正确工作。

## 相关概念

- [CLI 命令体系详解](02-cli-commands.md)
- [Transifex 平台集成](07-transifex-integration.md)
- [commands.py API 参考](../references/commands-api.md)
