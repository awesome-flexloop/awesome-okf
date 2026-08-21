---
okf_version: "0.2"
type: reference
title: "CLI 入口点 (conda_lock.py)"
sources:
  - "conda_lock/conda_lock.py"
  - "conda_lock/click_helpers.py"
---

# CLI 入口点 (conda_lock.py)

conda-lock 使用 Click 框架构建命令行界面，采用 `OrderedGroup` 自定义命令组，使 `lock` 成为默认子命令。CLI 入口模块定义了四个核心命令：`lock`（默认/锁定）、`install`（安装）、`render`（渲染）、`render-lock-spec`（输出锁定规格）。增量更新通过 `lock --update` 选项实现，而非独立子命令。

## Click OrderedGroup 与默认命令

```python
# conda_lock/click_helpers.py

import click

class OrderedGroup(click.Group):
    """自定义命令组，保持命令注册顺序，并将第一个命令作为默认命令。"""

    def __init__(self, *args, **kwargs):
        self._order = []
        super().__init__(*args, **kwargs)

    def get_command(self, ctx, cmd_name):
        # 如果输入不匹配任何已知命令，且存在默认命令，
        # 则将其作为默认命令（lock）的参数处理
        ctx.default_command = self._order[0] if self._order else None
        return super().get_command(ctx, cmd_name)

    def list_commands(self, ctx):
        return self._order

    def add_command(self, cmd, name=None):
        self._order.append(name or cmd.name)
        super().add_command(cmd, name)
```

**设计要点**：
- `OrderedGroup` 维护命令注册顺序列表 `_order`，`list_commands()` 按注册顺序返回，确保帮助信息中命令顺序可控。
- 当用户直接运行 `conda-lock` 而不指定子命令时，`lock`（第一个注册的命令）作为默认命令执行。这通过 Click 的 `invoke_without_command=True` 和自定义命令解析实现。

## CLI 主入口与命令注册

```python
# conda_lock/conda_lock.py

import click
from .click_helpers import OrderedGroup

@click.group(cls=OrderedGroup, invoke_without_command=True)
@click.pass_context
def main(ctx, **kwargs):
    """conda-lock: Generate fully reproducible conda lock files."""
    if ctx.invoked_subcommand is None:
        # 无子命令时默认执行 lock
        ctx.invoke(lock, **kwargs)

@main.command()
@click.argument("environment_files", nargs=-1, type=click.Path())
@click.option("--platform", "-p", multiple=True, help="Target platforms")
@click.option("--channel", "-c", multiple=True, help="Channels to use")
@click.option("--dev-dependencies/--no-dev-dependencies", default=False)
@click.option("--extras", multiple=True, help="Additional categories to include")
@click.option("--kind", "-k", default="lock",
              type=click.Choice(["lock", "explicit", "env"]))
@click.option("--lockfile", default="conda-lock.yml")
@click.option("--virtual-package-spec", type=click.Path(),
              help="Virtual package specification YAML")
@click.option("--update/--no-update", default=False)
@click.option("--filter-categories", multiple=True)
def lock(environment_files, platform, channel, dev_dependencies, extras,
         kind, lockfile, virtual_package_spec, update, filter_categories):
    """Generate conda lock file from environment specification(s)."""
    # ... 锁定逻辑入口

@main.command()
@click.argument("lockfile", type=click.Path(), default="conda-lock.yml")
@click.option("--prefix", type=click.Path(), help="Installation prefix")
@click.option("--name", "-n", help="Environment name")
@click.option("--dev/--no-dev", default=False)
@click.option("--extras", multiple=True)
def install(lockfile, prefix, name, dev, extras):
    """Install environment from a lock file."""
    # ... 安装逻辑入口

@main.command()
@click.argument("lockfile", type=click.Path(), default="conda-lock.yml")
@click.option("--kind", "-k", default="explicit",
              type=click.Choice(["explicit", "env"]))
@click.option("--dev-dependencies/--no-dev-dependencies", default=False)
@click.option("--extras", multiple=True)
@click.option("--platform", "-p", multiple=True)
def render(lockfile, kind, dev_dependencies, extras, platform):
    """Render a lock file to explicit or environment file format."""
    # ... 渲染逻辑入口

@main.command()
@click.argument("environment_files", nargs=-1, type=click.Path())
@click.option("--file", "-f", multiple=True, type=click.Path())
@click.option("--platform", "-p", multiple=True)
@click.option("--channel", "-c", multiple=True)
@click.option("--dev-dependencies/--no-dev-dependencies", default=False)
@click.option("--extras", multiple=True)
def render_lock_spec(environment_files, file, platform, channel,
                     dev_dependencies, extras):
    """Render the lock specification to a structured format."""
    # ... 输出锁定规格逻辑入口
```

**关键设计**：
- **默认子命令机制**：通过 `invoke_without_command=True` + `ctx.invoked_subcommand is None` 判断，无子命令时自动调用 `lock`。结合 `OrderedGroup` 中 lock 为首个注册命令，实现 `conda-lock` 等同于 `conda-lock lock`。
- **多源文件支持**：`environment_files` 接受可变数量的输入文件（nargs=-1），支持同时传入多个 environment.yml/pyproject.toml 进行聚合锁定。
- **跨平台选项**：`--platform/-p` 接受多次指定，实现多平台锁文件生成，与 CONDA_SUBDIR 机制协同。
- **kind 选项**：`lock` 命令的 `--kind` 参数控制输出格式（lock YAML / explicit URL 列表 / environment.yml），与 `render` 命令的输出选项一致。
- **依赖类别控制**：`lock` 和 `render` 命令使用 `--dev-dependencies/--no-dev-dependencies` 标志，`install` 命令使用 `--dev/--no-dev` 标志；`--extras` 在所有命令中通用，用于指定自定义 category。类别过滤在 `make_lock_spec()` 的 `filtered_categories` 参数中实现，而非 `LockSpecification.with_categories()` 方法。

## 命令调用链

```
用户输入 → Click 解析 → OrderedGroup.get_command()
  ├─ lock (默认) → src_parser.make_lock_spec(filtered_categories=...)
  │                → conda_solver.solve_conda()
  │                → pypi_solver.solve_pypi() → content_hash.compute_content_hashes()
  │                → lockfile.write_conda_lock_file()
  │       └─ (--update) → lockfile.parse_conda_lock_file()
  │                       → conda_solver.update_specs_for_arch()
  │                       → 重新求解 → lockfile.write_conda_lock_file()
  ├─ install → lockfile.parse_conda_lock_file() → invoke_conda 执行安装
  │            (--dev/--no-dev 标志控制类别过滤)
  ├─ render  → lockfile.parse_conda_lock_file() → 格式转换输出
  │            (--dev-dependencies/--no-dev-dependencies 标志控制类别过滤)
  └─ render-lock-spec → src_parser.make_lock_spec() → 输出结构化锁定规格
```
