---
okf_version: "0.2"
type: "concept"
title: "Context 全局配置与 condarc"
sources:
  - "conda/base/context.py"
  - "conda/common/configuration.py"
  - "conda/base/constants.py"
---

# Context 全局配置与 condarc

## 概述

`context` 是 conda 的全局配置单例对象，它聚合了所有配置文件（condarc）、环境变量和命令行参数，形成一个统一的全局状态对象，被 conda 的各个模块共享使用 [F-022]。context 在整个 conda 代码库中扮演"配置总线"的角色——几乎所有模块都从 context 读取配置参数，而非直接访问配置文件或环境变量。

## context 单例对象

context 对象在 `conda/base/context.py` 模块顶层直接实例化，导入即获得全局唯一实例：

```python
# conda/base/context.py
from frozendict import frozendict
from functools import cache, cached_property
from ..auxlib.decorators import memoizedproperty
```

context 使用三种缓存机制确保配置访问的性能和不可变性 [F-023]：

- **`frozendict`**：来自第三方 `frozendict` 库，用于存储不可变的字典配置，防止运行时意外修改配置值；
- **`cached_property`**：Python 标准库的缓存属性装饰器，用于计算成本较高的配置属性；
- **`memoizedproperty`**：auxlib 提供的记忆化属性装饰器，功能类似 cached_property。

context 的初始化在 CLI 入口 `main_subshell()` 中完成，采用两阶段初始化：先用 `pre_parser` 解析已知参数（如 `--no-plugins`）创建初步 context，再用完整 parser 解析后二次初始化 [F-017]。

## 配置文件搜索路径

condarc 配置文件的搜索路径分为多个层级 [F-024][F-028]：

**系统级路径**（由 `SEARCH_PATH` 常量定义，Unix 和 Windows 不同）：

| 平台 | 路径 |
|------|------|
| Unix | `/etc/conda/.condarc`, `/etc/conda/condarc`, `/etc/conda/condarc.d/`, `/var/lib/conda/.condarc` 等 |
| Windows | `C:/ProgramData/conda/.condarc`, `C:/ProgramData/conda/condarc`, `C:/ProgramData/conda/condarc.d` |

**安装级路径**：`$CONDA_ROOT/.condarc`（即 conda 安装目录下）。

**用户级路径**：
- `~/.condarc`（`user_rc_path`，最常用的用户配置文件位置）[F-024]
- `~/.config/conda/.condarc`（XDG 规范路径）
- `~/.conda/.condarc`

**环境级路径**：`$CONDA_PREFIX/.condarc`（激活环境中的配置）。

**特殊路径**：`$CONDARC` 环境变量指定的路径。

此外，两个关键路径变量 [F-024]：

```python
user_rc_path = abspath(expanduser(f"~/{DEFAULT_CONDARC_FILENAME}"))  # ~/.condarc
sys_rc_path = join(sys.prefix, DEFAULT_CONDARC_FILENAME)              # sys.prefix/.condarc
```

配置按搜索路径顺序加载，后加载的配置覆盖先加载的，命令行参数优先级最高，环境变量次之，配置文件最低。

## 平台映射

context 内部维护平台名称映射表 `_platform_map` [F-025]，将 Python `sys.platform` 值映射为 conda 内部使用的平台标识：

```python
_platform_map = {
    "freebsd13": "freebsd",
    "linux2": "linux",
    "linux": "linux",
    "darwin": "osx",
    "win32": "win",
    "zos": "zos",
}
```

这用于将 Python 报告的平台名统一为 conda 通道子目录（subdir）使用的命名约定，如 `linux-64`、`osx-arm64`、`win-64` 等。

## Configuration 框架与 ParameterLoader

`conda/common/configuration.py` 提供了一个通用的配置管理框架，核心类包括 [F-026]：

### Configuration 类

`Configuration` 是配置框架的顶层类，负责：
- 从多个来源（YAML 文件、环境变量、命令行）加载原始参数；
- 按优先级合并参数值；
- 执行类型验证和自定义验证；
- 支持参数别名。

Configuration 支持延迟求值（lazy eval），配置值在首次访问时才会被解析和合并。

### ParameterLoader

`ParameterLoader` 是参数描述符，用于在 Configuration 子类中声明配置参数。每个参数通过 ParameterLoader 绑定名称、类型、默认值、验证函数等元信息。

### 参数类型体系

框架提供四种参数类型，分别处理不同形态的配置值 [F-026]：

| 参数类型 | 用途 | YAML 示例 |
|----------|------|-----------|
| `PrimitiveParameter` | 标量值（字符串、布尔值、数字） | `always_copy: true` |
| `SequenceParameter` | 序列值（列表/元组） | `channels: [conda-forge, defaults]` |
| `MapParameter` | 键值对映射 | `channel_alias: {https://conda.anaconda.org: ...}` |
| `YamlRawParameter` | 原始 YAML 数据（支持注释和标志） | 任意嵌套 YAML 结构 |

这些参数类型在处理 condarc YAML 文件时，`YamlRawParameter` 负责解析 ruamel.yaml 的 `CommentedMap`/`CommentedSeq` 对象，提取 YAML 注释中的优先级标志（`!top`、`!bottom`、`!final`）。

### 原始参数来源

框架定义了三种 `RawParameter` 子类，分别对应三种配置来源：

- **`YamlRawParameter`**：从 YAML 配置文件加载，使用 ruamel.yaml 解析，保留注释信息，`make_raw_parameters_from_file()` 方法带 `@cache` 装饰器缓存文件解析结果；
- **`EnvRawParameter`**：从环境变量加载，以 `CONDA_` 为前缀扫描环境变量（如 `CONDA_CHANNELS`），支持 `!important` 优先级标记；
- **`ArgParseRawParameter`**：从 argparse 命令行参数加载。

## 配置错误体系

配置框架定义了完整的错误类层次 [F-027]：

```
ConfigurationError (基类，继承自 CondaError)
├── ConfigurationLoadError    # 配置文件加载失败（YAML 语法错误等）
├── ValidationError           # 参数验证失败
│   ├── MultipleKeysError     # 同一参数使用了多个别名
│   ├── InvalidTypeError      # 参数类型错误
│   └── CustomValidationError # 自定义验证失败
└── MultiValidationError      # 多个验证错误聚合（继承 CondaMultiError）
```

- `ConfigurationLoadError` 在 YAML 文件解析失败时抛出，包含文件路径和错误位置（行号、列号）；
- `ValidationError` 携带参数名、参数值、来源和错误消息；
- `MultipleKeysError` 在 YAML 文件中同时使用了互斥的别名键时抛出（如同时使用 `channels` 和 `channels` 的旧名）；
- `MultiValidationError` 通过 `raise_errors()` 函数统一抛出——单个错误直接 raise，多个错误包装为 MultiValidationError。

## 常量与枚举

`conda/base/constants.py` 定义了 conda 运行时使用的关键常量和枚举 [F-028][F-029]：

**核心常量**：

```python
APP_NAME = "conda"
REPODATA_FN = "repodata.json"           # 仓库元数据文件名
PREFIX_MAGIC_FILE = "conda-meta/history" # 环境标识文件
ROOT_ENV_NAME = "base"                  # 根环境名称
DEFAULTS_CHANNEL_NAME = "defaults"      # 默认通道名称
DEFAULT_SOLVER = "libmamba"             # 默认求解器
CLASSIC_SOLVER = "classic"              # 经典求解器名称
KNOWN_SUBDIRS = ("noarch", "linux-64", "osx-arm64", "win-64", ...)  # 所有已知平台子目录
```

`DEFAULT_CHANNELS` 在 Unix 上为 `pkgs/main` 和 `pkgs/r`，在 Windows 上额外包含 `pkgs/msys2`。

**关键枚举类型**：

| 枚举 | 值 | 用途 |
|------|-----|------|
| `ChannelPriority` | strict/flexible/disabled | 通道优先级策略 |
| `DepsModifier` | not_set/no_deps/only_deps | 依赖处理标志 |
| `UpdateModifier` | freeze_installed/update_deps/update_specs/update_all/... | 更新策略 |
| `SafetyChecks` | disabled/warn/enabled | 安全检查级别 |
| `SatSolverChoice` | pycosat/pycryptosat/pysat | SAT 求解器选择 |
| `PathConflict` | clobber/warn/prevent | 路径冲突处理 |

## frozendict 不可变配置

frozendict 在 conda 配置系统中被广泛使用，其核心作用有两点：

1. **防止意外修改**：配置加载后即为不可变对象，避免运行时某个模块意外修改全局配置导致难以追踪的 bug；
2. **缓存安全**：`@cache` 和 `@cached_property` 装饰器要求返回值可哈希，frozendict 是可哈希的不可变映射，适合作为缓存键或缓存值。

在 `common/configuration.py` 中，`deepfreeze()` 函数用于将嵌套的数据结构（dict、list）递归转换为 frozendict 和 tuple，确保整个配置树不可变。Enum 类型被特殊注册为保持原样不冻结。

## 相关概念

- [Index 索引与 SubdirData](./08-index-and-repodata.md)：context 提供 channels、subdirs、repodata_fn 等配置给 Index 使用
- [Solver 求解器与 SAT 算法](./09-solver-and-resolve.md)：context 提供 solver、channel_priority 等求解器相关配置
