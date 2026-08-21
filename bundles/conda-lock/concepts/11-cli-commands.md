---
okf_version: "0.2"
type: "concept"
title: "CLI 命令体系"
sources:
  - "conda_lock/conda_lock.py"
  - "conda_lock/click_helpers.py"
---

# CLI 命令体系

conda-lock 的命令行界面基于 Click 框架构建，使用自定义 `OrderedGroup` 命令组使 `lock` 成为默认子命令。CLI 提供四个核心命令：`lock`（锁定/默认）、`install`（安装）、`render`（渲染）、`render-lock-spec`（输出锁定规格）。增量更新通过 `lock --update` 选项实现，而非独立子命令。

## OrderedGroup：默认命令机制

```python
# conda_lock/click_helpers.py

class OrderedGroup(click.Group):
    """自定义 Click 命令组，支持默认子命令和命令顺序控制。"""

    def __init__(self, *args, **kwargs):
        self._order = []
        super().__init__(*args, **kwargs)

    def list_commands(self, ctx):
        """按注册顺序返回命令列表（而非字母序）。"""
        return self._order

    def add_command(self, cmd, name=None):
        """注册命令时记录顺序。"""
        self._order.append(name or cmd.name)
        super().add_command(cmd, name)

    def get_command(self, ctx, cmd_name):
        """命令查找。如果 cmd_name 不匹配任何已知子命令，
        且命令组配置了 invoke_without_command=True，
        则将参数传给默认子命令（第一个注册的命令，即 lock）。"""
        cmd = super().get_command(ctx, cmd_name)
        if cmd is None and not ctx.resilient_parsing:
            # 将未匹配的输入视为默认命令的参数
            ctx.default_command = self._order[0] if self._order else None
        return cmd
```

[F-001]

主入口使用 `invoke_without_command=True`，使得直接运行 `conda-lock`（不带子命令）时默认执行 `lock`：

```python
@click.group(cls=OrderedGroup, invoke_without_command=True)
@click.pass_context
def main(ctx, **kwargs):
    if ctx.invoked_subcommand is None:
        ctx.invoke(lock, **kwargs)
```

[F-002]

这意味着：
- `conda-lock` ≡ `conda-lock lock`
- `conda-lock -f environment.yml -p linux-64` ≡ `conda-lock lock -f environment.yml -p linux-64`

## lock 命令

`lock` 是最核心的命令，从环境规格文件生成锁文件。

```python
@main.command()
@click.argument("environment_files", nargs=-1, type=click.Path(exists=True))
@click.option("--file", "-f", "file", multiple=True, type=click.Path(exists=True),
              help="Environment files to lock")
@click.option("--platform", "-p", multiple=True,
              help="Target platforms (e.g. linux-64, osx-arm64, win-64)")
@click.option("--channel", "-c", multiple=True,
              help="Additional conda channels")
@click.option("--dev-dependencies/--no-dev-dependencies", default=False,
              help="Include dev dependencies")
@click.option("--extras", multiple=True,
              help="Additional dependency categories to include")
@click.option("--kind", "-k", default="lock",
              type=click.Choice(["lock", "explicit", "env"]),
              help="Output kind")
@click.option("--lockfile", default="conda-lock.yml",
              help="Output lockfile path")
@click.option("--virtual-package-spec", type=click.Path(exists=True),
              help="Virtual packages specification YAML")
@click.option("--update/--no-update", default=False,
              help="Update existing lock file incrementally")
@click.option("--filter-categories", multiple=True,
              help="Filter to specific categories")
@click.option("--conda", default="conda",
              help="Conda executable to use (conda/mamba/micromamba)
@click.option("--mamba", is_flag=True, default=False,
              help="Use mamba as solver (shorthand for --conda mamba)")
@click.option("--check-input-hash", is_flag=True, default=False,
              help="Check if input has changed before locking")
def lock(file, platform, channel, dev_dependencies, extras, kind,
         lockfile, virtual_package_spec, update, filter_categories,
         conda, mamba, check_input_hash, environment_files):
    """Generate conda lock file from environment specification(s)."""
```

[F-003]

主要选项说明：

| 选项 | 缩写 | 说明 |
|------|------|------|
| `--file` | `-f` | 输入环境文件，可多次指定多文件聚合 |
| `--platform` | `-p` | 目标平台，可多次指定（覆盖 environment.yml 中的 platforms） |
| `--channel` | `-c` | 额外 conda 通道 |
| `--dev-dependencies` | — | 包含 dev 类别依赖 |
| `--extras` | — | 包含自定义 category，可多次指定 |
| `--kind` | `-k` | 输出格式：lock(YAML)/explicit(URL列表)/env(environment.yml) |
| `--lockfile` | — | 输出锁文件路径（默认 conda-lock.yml） |
| `--virtual-package-spec` | — | 自定义虚拟包 YAML 文件 |
| `--update` | — | 增量更新模式：基于已有锁文件更新，可指定包名如 `--update numpy` |
| `--filter-categories` | — | 仅锁定指定类别 |
| `--conda` | — | 指定求解器可执行文件 |
| `--mamba` | — | 使用 mamba（--conda mamba 的简写） |
| `--check-input-hash` | — | 仅在输入哈希变化时重新锁定 |

### 位置参数 vs --file 选项

`environment_files` 位置参数和 `--file/-f` 选项都可以指定输入文件，两者合并使用。这意味着以下写法等价：

```bash
conda-lock lock environment.yml
conda-lock lock -f environment.yml
conda-lock lock environment.yml -f pyproject.toml
```

## install 命令

```python
@main.command()
@click.argument("lockfile", type=click.Path(exists=True), default="conda-lock.yml")
@click.option("--prefix", type=click.Path(), help="Installation prefix path")
@click.option("--name", "-n", help="Environment name")
@click.option("--dev/--no-dev", default=False, help="Include dev dependencies")
@click.option("--extras", multiple=True, help="Additional categories")
@click.option("--conda", default=None, help="Conda executable")
@click.option("--mamba", is_flag=True, help="Use mamba")
def install(lockfile, prefix, name, dev, extras, conda, mamba):
    """Install environment from a lock file."""
```

[F-004]

安装流程：
1. 解析锁文件（`parse_conda_lock_file()`）
2. 根据 `--dev`/`--extras` 过滤类别
3. 创建环境（`conda create` 或 `conda install`）
4. 从锁文件的 URL 列表安装 conda 包
5. 使用 pip 安装 pip 包（按 lockfile 中的 pip 包）

`--prefix` 和 `--name` 二选一：`--name` 使用 conda 默认环境目录，`--prefix` 指定完整路径。

## render 命令

```python
@main.command()
@click.argument("lockfile", type=click.Path(exists=True), default="conda-lock.yml")
@click.option("--kind", "-k", default="explicit",
              type=click.Choice(["explicit", "env"]),
              help="Output format")
@click.option("--dev-dependencies/--no-dev-dependencies", default=False,
              help="Include dev dependencies")
@click.option("--extras", multiple=True, help="Additional categories")
@click.option("--platform", "-p", multiple=True,
              help="Platforms to render (default: all)")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def render(lockfile, kind, dev_dependencies, extras, platform, output):
    """Render a lock file to explicit or environment file format."""
```

[F-005]

> **注意**：`render` 命令使用 `--dev-dependencies/--no-dev-dependencies` 标志（与 `lock` 命令一致），而 `install` 命令使用 `--dev/--no-dev` 标志。

渲染输出两种格式：
- **explicit**：`@EXPLICIT` 格式的 URL 列表，每行一个包下载 URL，conda 可以直接 `conda create --file` 使用。每个平台生成一个文件（如 `conda-linux-64.lock`）。
- **env**：固定版本的 environment.yml，所有包都有精确版本号。

## render-lock-spec 命令

`render-lock-spec` 命令用于输出 `LockSpecification` 的结构化表示（通常为 JSON/YAML 格式），便于调试和检查解析后的锁定规格。

```python
@main.command()
@click.argument("environment_files", nargs=-1, type=click.Path(exists=True))
@click.option("--file", "-f", multiple=True, type=click.Path(exists=True))
@click.option("--platform", "-p", multiple=True)
@click.option("--channel", "-c", multiple=True)
@click.option("--dev-dependencies/--no-dev-dependencies", default=False)
@click.option("--extras", multiple=True)
def render_lock_spec(environment_files, file, platform, channel,
                     dev_dependencies, extras):
    """Render the lock specification to a structured format."""
```

[F-006]

## 增量更新：lock --update

conda-lock 没有独立的 `update` 子命令。增量更新是通过 `lock` 命令的 `--update` 选项实现的：

```bash
# 更新所有包到最新兼容版本
conda-lock lock --update -f environment.yml

# 更新指定包
conda-lock lock --update numpy --update pandas -f environment.yml

# 更新特定平台
conda-lock lock --update -f environment.yml -p linux-64
```

增量更新的工作流程：
1. 读取现有锁文件（`parse_conda_lock_file()`）
2. 通过 `fake_conda_environment()` 构造假环境 + pinning 机制约束更新范围
3. 使用 `update_specs_for_arch()` 进行增量求解（conda install --dry-run）
4. 计算内容哈希，写回锁文件

## 命令调用链

```
conda-lock
    │
    ├─ (无子命令) ──→ lock (默认)
    │
    ├─ lock ──→ make_lock_spec() ──→ solve_conda() + solve_pypi()
    │       ├─ (--update) → parse_conda_lock_file() → update_specs_for_arch()
    │       └─ compute_content_hashes() ──→ write_conda_lock_file()
    │
    ├─ install ──→ parse_conda_lock_file() ──→ 类别过滤(--dev/--extras)
    │            ──→ conda create/install (从锁文件URL)
    │            ──→ pip install (pip包)
    │
    ├─ render ──→ parse_conda_lock_file() ──→ 类别过滤(--dev-dependencies/--extras)
    │           ──→ 格式转换 (explicit/env)
    │           ──→ 输出文件
    │
    └─ render-lock-spec ──→ make_lock_spec() ──→ 输出结构化 LockSpecification
```

[F-007]

## 全局约定

- **平台标识**：使用 conda 的平台命名（`linux-64`/`linux-aarch64`/`osx-64`/`osx-arm64`/`win-64`/`linux-ppc64le`）
- **默认平台**：不指定 `--platform` 时使用当前运行平台
- **默认锁文件**：`conda-lock.yml` 在当前目录
- **类别控制**：`lock` 和 `render` 命令使用 `--dev-dependencies/--no-dev-dependencies` 标志；`install` 命令使用 `--dev/--no-dev` 标志；`--extras` 在所有命令中通用，可叠加自定义类别
- **求解器选择**：默认 conda，`--mamba` 标志切换到 mamba，`--conda micromamba` 切换到 micromamba

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [Conda 求解器](08-conda-solver.md)
- [锁文件 v1/v2 格式](06-lockfile-formats.md)
- [依赖类别与传播](14-categories-and-deps.md)
- [内容哈希机制](12-content-hash.md)
- [基础锁定工作流](../examples/basic-lock-workflow.md)
