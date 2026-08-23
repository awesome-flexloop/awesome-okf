---
type: Concept
title: 高级模式与 API 集成
description: Python API 集成、自定义 Jinja2 扩展、LazyDict 延迟字典、Phase 上下文管理、符号链接处理、文件权限同步、外部数据高级用法
tags: [copier, advanced, api, python-api, extensions, lazydict, symlinks, permissions]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-source
    resource: /references/copier-source.md
---

# 高级模式与 API 集成

除了 CLI 用法，Copier 还提供 Python API、扩展机制和高级配置选项，支持将 Copier 集成到其他工具和自动化流程中。[^copier-source]

## Python API

### 便捷函数

`copier` 包导出三个主要入口函数：

```python
from copier import run_copy, run_recopy, run_update

# 从零创建项目
run_copy(
    src_path="gh:user/template",
    dst_path="./my-project",
    data={"project_name": "demo"},
    vcs_ref="v2.0.0",
    defaults=True,
    overwrite=True,
    unsafe=False,
    quiet=False,
)

# 重新复制（保留答案）
run_recopy(
    dst_path="./my-project",
    defaults=True,
    overwrite=True,
    skip_answered=True,
)

# 智能更新
run_update(
    dst_path="./my-project",
    conflict="inline",
    context_lines=3,
    skip_answered=True,
)
```

### Worker 类直接使用

对于更精细的控制，直接使用 `Worker` 类：

```python
from pathlib import Path
from copier._main import Worker

with Worker(
    src_path="./template",
    dst_path=Path("./output"),
    data={"name": "test"},
    defaults=True,
    overwrite=True,
    exclude=["*.tmp", "~*"],
    skip_if_exists=[".env"],
    templates_suffix=".jinja",
    conflict="inline",
    context_lines=5,
    pretend=False,
    quiet=True,
) as worker:
    worker.run_copy()
    # 或 worker.run_update() / worker.run_recopy()
```

### 参数映射（CLI → API）

| CLI 选项 | API 参数 | 类型 |
|----------|---------|------|
| `-d K=V` | `data={"K": "V"}` | dict |
| `--data-file` | 通过 `data` 手动合并 YAML | dict |
| `-r/--vcs-ref` | `vcs_ref="v1.0.0"` | str \| VcsRef |
| `-l/--defaults` | `defaults=True` | bool |
| `-w/--overwrite` | `overwrite=True` | bool |
| `-f/--force` | `defaults=True, overwrite=True` | bool×2 |
| `-n/--pretend` | `pretend=True` | bool |
| `-q/--quiet` | `quiet=True` | bool |
| `-x/--exclude` | `exclude=["pattern"]` | Sequence[str] |
| `-s/--skip` | `skip_if_exists=["pattern"]` | Sequence[str] |
| `-T/--skip-tasks` | `skip_tasks=True` | bool |
| `--trust/--UNSAFE` | `unsafe=True` | bool |
| `-A/--skip-answered` | `skip_answered=True` | bool |
| `--ask` | `ask=["pattern"]` | Sequence[str] |
| `-o/--conflict` | `conflict="inline"` | Literal |
| `-c/--context-lines` | `context_lines=3` | int |
| `-C/--no-cleanup` | `cleanup_on_error=False` | bool |
| `-a/--answers-file` | `answers_file=Path(...)` | RelativePath |

### VcsRef 特殊值

```python
from copier import VcsRef

# 使用已有项目的当前模板版本
run_update("./project", vcs_ref=VcsRef.CURRENT)
```

### get_update_data()

`get_update_data()` 函数用于检查更新可用性（CLI `check-update` 底层使用）：

```python
from copier._main import get_update_data

update_available, current, latest = get_update_data(
    dst_path="./my-project",
    use_prereleases=False,
)

if update_available:
    print(f"Update from {current} to {latest}")
```

## 类型系统

### Phase 枚举与上下文

`Phase` 枚举用于追踪当前执行阶段，可在模板中通过 `{{ _copier_phase }}` 访问：

```python
from copier import Phase

# 当前可用阶段
Phase.PROMPT    # "prompt"    - 交互式问卷
Phase.TASKS     # "tasks"     - 执行任务
Phase.MIGRATE   # "migrate"   - 执行迁移
Phase.RENDER    # "render"    - 渲染文件
Phase.UNDEFINED # "undefined" - 外部数据加载等
```

使用 `Phase.use()` 上下文管理器设置当前阶段：
```python
with Phase.use(Phase.RENDER):
    # 此上下文中 Phase.current() 返回 Phase.RENDER
    print(Phase.current())  # Phase.RENDER
```

阶段信息存储在 `ContextVar`（`_phase`）中，支持 asyncio 协程安全的上下文传播。

### Operation 类型

`Operation = Literal["copy", "update"]`，通过 `_operation` ContextVar 和 `@as_operation` 装饰器管理：

```python
from copier._main import as_operation

@as_operation("copy")
def my_copy_function():
    # 在此函数内 _operation.get() 返回 "copy"
    ...
```

### LazyDict：延迟求值字典

`LazyDict` 是 Copier 实现的一个特殊字典，值在首次访问时才求值：

```python
from copier._types import LazyDict

def expensive_computation():
    print("Computing...")
    return {"key": "value"}

lazy = LazyDict({"data": expensive_computation})
# 此时 expensive_computation 尚未调用
result = lazy["data"]  # 打印 "Computing..."，返回 {"key": "value"}
result = lazy["data"]  # 第二次访问直接返回缓存值
```

在 Copier 中用于：
- `_render_context()` 中的 `_copier_conf`：配置值延迟计算，避免不必要的属性访问
- `_external_data()`：外部数据文件延迟加载，避免循环依赖
- Jinja2 渲染上下文中的动态值

LazyDict 实现了 `MutableMapping` 接口，支持 `__getitem__`、`__setitem__`、`__delitem__`、`__iter__`、`__len__`。赋值时将值包装为 lambda，删除时清除缓存。

## 自定义 Jinja2 扩展

模板可以通过 `_jinja_extensions` 指定自定义 Jinja2 扩展：

```yaml
_jinja_extensions:
  - "copier_templates_extensions.TemplateExtensionLoader"
  - "jinja2_jsonschema.JsonSchemaExtension"
  - "myapp.jinja_ext.MyCustomExtension"
```

**注意**：自定义扩展属于不安全特性，需要 `--trust` 授权。扩展在加载失败时抛出 `ExtensionNotFoundError`。

Copier 默认加载的扩展：
- `jinja2_ansible_filters.AnsibleCoreFiltersExtension`：Ansible 过滤器集
- `copier._jinja_ext.YieldExtension`：yield 标签扩展

### 内置扩展：YieldExtension

`YieldExtension` 允许在路径模板中使用 `{% yield %}` 标签生成多个文件：

```jinja
{# 文件名：{{ item }}.py.jinja #}
{% for item in modules %}{% yield item %}{% endfor %}
```

在 Worker 的 `_render_parts()` 方法中，遇到 yield 标签时迭代 `yield_iterable`，为每个值生成一个路径+上下文对。

### 自定义全局函数

除了扩展，Copier 还在 Jinja2 环境中注册了：
- `pathjoin(*parts, mode="posix")`：跨平台路径拼接
- `to_json` 过滤器的增强版本（支持 Pydantic dataclass、LazyDict、PurePath）

### 自定义 undefined 行为

```yaml
_envops:
  undefined: "jinja2.StrictUndefined"
```

- `jinja2.Undefined`（默认）：未定义变量渲染为空字符串，不报错
- `jinja2.StrictUndefined`：引用未定义变量抛出 `UndefinedError`，适合在 CI/CD 中早期发现模板错误

## 错误处理

### 异常层次

```
CopierError (基类)
├── UserMessageError (退出码 1)
│   ├── UnsupportedVersionError
│   ├── ExtensionNotFoundError
│   ├── InteractiveSessionError
│   └── TaskError (同时继承 CalledProcessError)
├── ConfigFileError
│   ├── InvalidConfigFileError
│   └── MultipleConfigFilesError
├── PathError
│   ├── PathNotAbsoluteError
│   ├── PathNotRelativeError
│   └── ForbiddenPathError
├── UnsafeTemplateError (退出码 4)
├── CopierAnswersInterrupt (同时继承 KeyboardInterrupt)
├── YieldTagInFileError
└── MultipleYieldTagsError
```

警告层次：
```
CopierWarning (基类)
├── UnknownCopierVersionWarning
├── OldTemplateWarning
├── DirtyLocalWarning
├── ShallowCloneWarning
├── MissingSettingsWarning
└── MissingFileWarning
```

### CopierAnswersInterrupt：Ctrl+C 恢复

用户按 Ctrl+C 时，Copier 抛出 `CopierAnswersInterrupt`（继承 KeyboardInterrupt），携带已收集的部分答案：

```python
from copier.errors import CopierAnswersInterrupt
from copier._main import Worker

try:
    with Worker(src_path="tpl", dst_path="out") as worker:
        worker.run_copy()
except CopierAnswersInterrupt as e:
    # e.answers: 已收集的答案（AnswersMap）
    # e.last_question: 中断时的问题
    # e.template: 当前模板
    print(f"Interrupted at question: {e.last_question.var_name}")
    # 可以保存部分答案
```

## 文件权限与跨平台

### 可执行位同步

Copier 智能处理跨平台文件权限问题：

1. **Git index 优先**：模板的 `git ls-files --stage` 记录的文件模式（100755/100644）是可执行位的权威来源
2. **权限合并**：从 Git index 获取可执行位（0o111），从文件系统获取读写位（~0o111），合并后作为源文件权限
3. **Windows 兼容**：Windows 上 `os.stat()` 不报告可执行位，但 Git index 模式会被保留
4. **Git index 同步**：当 `core.fileMode=false`（Windows 默认），`chmod` 对 Git 不可见，Copier 通过 `git update-index --cacheinfo` 显式更新 index 中的模式

为什么使用 `--cacheinfo` 而非 `--chmod`：`--chmod` 会重新暂存工作区内容，在 update 流程中会覆盖用于冲突重建的原始 blob SHA。`--cacheinfo` 仅修改现有 blob 的模式位，不重新读取工作区。

### 符号链接处理

```yaml
_preserve_symlinks: true
```

启用后，模板中的符号链接在输出中保留为符号链接（而非复制目标内容）。这对于包含相对符号链接的模板很有用。

## 工具函数

`_tools.py` 提供了多个实用工具：

```python
from copier._tools import (
    copier_version,      # 获取 Copier 版本号
    OS,                  # 操作系统信息命名空间
    Style,               # 输出样式（OK/WARNING/DANGER/IGNORE）
    printf,              # 格式化状态输出
    cast_to_bool,        # 字符串转布尔（yes/no/true/false/1/0）
    normalize_git_path,  # 规范化 Git 路径
    scantree,            # 递归目录扫描
    handle_remove_readonly,  # Windows 只读文件删除处理
)
```

## 嵌入到其他工具

Copier 的 Python API 适合嵌入到：

- **项目初始化工具**：CLI 包装器添加组织特定的默认值和验证
- **CI/CD 管道**：在流水线中自动生成/更新项目
- **IDE 插件**：在 VS Code 等 IDE 中提供新建项目向导
- **模板管理平台**：多模板管理和版本控制界面

示例：自定义 CLI 包装器

```python
import typer
from copier import run_copy

app = typer.Typer()

@app.command()
def create(
    name: str = typer.Option(..., help="项目名称"),
    template: str = typer.Option("gh:myorg/python-template", help="模板 URL"),
):
    """从组织模板创建新项目。"""
    run_copy(
        src_path=template,
        dst_path=f"./{name}",
        data={"project_name": name, "org_name": "MyOrg"},
        defaults=True,
        overwrite=True,
        vcs_ref="stable",  # 使用 stable 分支
    )
    typer.echo(f"项目 {name} 创建成功！")

if __name__ == "__main__":
    app()
```

## 相关概念

- [CLI 命令参考](08-cli-reference.md)
- [Worker 与生命周期](05-worker-and-lifecycle.md)
- [Jinja2 模板渲染](04-jinja2-templating.md)
- [安全与信任机制](09-security-and-safety.md)
- [Python API 使用示例](/examples/python-api-usage.md)
- [Copier 源码信源登记](/references/copier-source.md)

[^copier-source]: Copier 源码信源，见 [copier-source.md](/references/copier-source.md)。
