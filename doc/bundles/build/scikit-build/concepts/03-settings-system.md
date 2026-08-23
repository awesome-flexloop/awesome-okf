---
type: concept
title: 配置系统详解
description: scikit-build-core 的三源配置合并机制——环境变量、config-settings、TOML 配置的优先级与合并规则
tags:
  - scikit-build
  - build
  - configuration
  - settings
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/settings/skbuild_model.py"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/settings/sources.py"
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/settings/skbuild_read_settings.py"
---

# 配置系统详解

scikit-build-core 的配置系统是其核心设计之一。它通过 `SourceChain` 组合三个配置源，支持条件覆盖、版本门控和严格验证。

## 配置数据模型

所有配置通过 `ScikitBuildSettings` dataclass 表示，包含嵌套子配置：

```
ScikitBuildSettings
├── cmake: CMakeSettings        # CMake 相关配置
├── ninja: NinjaSettings        # Ninja 相关配置
├── wheel: WheelSettings        # Wheel 打包配置
├── sdist: SDistSettings        # SDist 打包配置
├── editable: EditableSettings  # 可编辑安装配置
├── build: BuildSettings        # 构建参数
├── install: InstallSettings    # 安装参数
├── logging: LoggingSettings    # 日志配置
├── metadata: dict[str, Any]    # 动态元数据
└── overrides: list             # 条件覆盖列表
```

每个子配置也是 dataclass，字段有明确的类型注解和默认值。完整字段列表见[配置项速查](../references/config-entry-points.md)。

## 三个配置源

配置系统通过 `Source` 协议抽象了统一的键值查询接口。三个内置实现：

### 1. TOMLSource：pyproject.toml 静态配置

从 `[tool.scikit-build]` 表读取嵌套配置。这是最常用的配置方式。

```toml
[tool.scikit-build]
cmake.build-type = "Release"
wheel.py-api = "cp39"

[tool.scikit-build.cmake.define]
CMAKE_PREFIX_PATH = "/opt/foo"
BUILD_TESTS = "OFF"
```

### 2. ConfSource：PEP 517 config-settings

构建前端通过 `--config-settings`（或 `-C`）传递的命令行参数。

```bash
python -m build -Ccmake.build-type=Debug -Cbuild.verbose=true
pip install . -Ccmake.define.BUILD_TESTS=ON
```

键名使用点分格式（`cmake.build-type`），list 值可通过重复键名传入。

### 3. EnvSource：环境变量

以 `SKBUILD_` 为前缀的环境变量，字段路径映射为**大写+下划线**格式。

```bash
export SKBUILD_CMAKE_BUILD_TYPE=Debug
export SKBUILD_BUILD_VERBOSE=true
export SKBUILD_CMAKE_DEFINE="BUILD_TESTS=ON;CMAKE_PREFIX_PATH=/opt/foo"
```

列表值以 `;` 分隔，dict 值以 `key=value;key=value` 格式编码。

## 配置优先级链

三个配置源通过 `SourceChain` 按优先级组合：

```
环境变量 (SKBUILD_*)  ← 最高优先级
    ↓
config-settings (-C)  ← 中优先级
    ↓
pyproject.toml        ← 最低优先级（静态默认值）
```

查询时，`SourceChain` 从高优先级源开始遍历，第一个包含该键的源返回值。

## 合并语义：标量 vs Dict

配置合并的关键细节——**dict 类型字段跨源合并，标量和列表字段替换**：

### 标量和列表：取最高优先级源

```toml
# pyproject.toml
[tool.scikit-build]
cmake.build-type = "Release"
cmake.args = ["-DFOO=1"]
```

```bash
# 环境变量覆盖
export SKBUILD_CMAKE_BUILD_TYPE=Debug
# 结果：build-type=Debug, cmake.args=["-DFOO=1"]（环境变量未设，保留 TOML 值）
```

```bash
# 环境变量覆盖列表
export SKBUILD_CMAKE_ARGS="-DBAR=2"
# 结果：cmake.args=["-DBAR=2"]（整个列表被替换，不是追加！）
```

### Dict 字段：跨源合并（键值叠加）

`cmake.define`、`wheel.force-include` 等 dict 字段是**合并**关系：

```toml
# pyproject.toml
[tool.scikit-build.cmake.define]
A = "1"
B = "2"
```

```bash
# 环境变量补充
export SKBUILD_CMAKE_DEFINE="C=3;D=4"
# 结果：cmake.define = {A: "1", B: "2", C: "3", D: "4"}（四个键都有）
```

```bash
# config-settings 覆盖单个键
python -m build -Ccmake.define.A=overridden
# 结果：cmake.define = {A: "overridden", B: "2", C: "3", D: "4"}
```

这种合并语义在多场景配置（CI 注入、平台特定、基础配置）中非常有用。

## 值类型编码

CMake 定义值（`cmake.define`）通过 `CMakeSettingsDefine` 类处理类型转换：

| Python 值 | CMake 缓存值 |
|-----------|-------------|
| `True` / `true` | `"TRUE"` |
| `False` / `false` | `"FALSE"` |
| `[1, 2, 3]` | `"1;2;3"`（内部分号自动转义） |
| `"hello"` | `"hello"` |
| `"/path/to/dir"` | `"/path/to/dir"`（Path 类型） |

## 条件覆盖（Overrides）

Overrides 允许根据环境条件动态修改配置：

```toml
[[tool.scikit-build.overrides]]
if.system = "darwin"
cmake.args = ["-DCMAKE_OSX_DEPLOYMENT_TARGET=10.15"]

[[tool.scikit-build.overrides]]
if.platform_python_implementation = "CPython"
if.platform_python_version = ">=3.12"
wheel.py-api = "cp312"

[[tool.scikit-build.overrides]]
if.any.system = "windows"
if.any.platform_machine = "ARM64"
cmake.define.CROSS_COMPILING = "ON"
```

- `if.xxx = value` 是 AND 条件（所有满足才匹配）
- `if.any.xxx = value` 是 OR 条件（任一满足即匹配）
- 多个 override 块按顺序匹配，后面的覆盖前面的

支持的条件字段：`system`、`sys_platform`、`platform_machine`、`platform_python_implementation`、`python_version`、`platform_in_virtualenv`、`ci`、`arch` 等。

## override-only 字段

以下字段只能在 overrides 或通过 config-settings/环境变量设置，不能在静态 `[tool.scikit-build]` 中直接设置：

| 字段 | 原因 |
|------|------|
| `cmake.toolchain-file` | 工具链路径是环境相关的 |
| `wheel.tags` | 标签必须与构建环境匹配 |
| `fail` | 条件失败控制 |

## 严格模式验证

默认 `strict-config = true`，SettingsReader 在 `validate_may_exit()` 中检查：

1. **未识别选项**：配置中出现未知键名时报错退出
2. **override-only 违规**：在静态配置中设置 override-only 字段报错
3. **类型验证**：字段值类型不匹配时报错
4. **minimum-version 合规**：使用新版本特性但 minimum-version 过低时警告/迁移

设为 `false` 可以忽略未知选项（兼容旧配置），但不推荐。

## 动态配置插件

通过 entry-point group `scikit-build-core.config.default` 和 `scikit-build-core.config.override` 可以注册配置提供者插件，在 TOML 解析后动态修改配置。设置环境变量 `SKBUILD_NO_ENTRYPOINT_CONFIG=1` 可禁用。

## minimum-version 自动迁移

设置 `minimum-version` 后，SettingsReader 自动处理旧字段名迁移：

| 旧字段 (<0.5) | 新字段 (>=0.5) |
|--------------|---------------|
| `cmake.minimum_version` | `cmake.version` |
| `cmake.verbose` | `build.verbose` |
| `logging="FINE"` | `logging.level="DEBUG"` |

使用 `minimum-version = "build-system.requires"` 可自动从 build-system.requires 提取版本约束，避免版本号硬编码。

## 延伸阅读

- [版本门控与向后兼容](12-version-gating.md)——深入理解 minimum-version 机制
- [配置项速查](../references/config-entry-points.md)——完整字段参考
- [构建流程](05-build-flow.md)——配置如何驱动实际构建
