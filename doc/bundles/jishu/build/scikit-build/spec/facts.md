# scikit-build-core 源码事实清单

> R阶段产出：编号事实清单 F-001 ~ F-090，每条事实指向具体源码路径，无推断性表述。

## 项目元数据

F-001: 包名为 `scikit_build_core`，定义于 `pyproject.toml` 的 `[project]` 表的 `name` 字段
F-002: 构建后端为 `hatchling.build`，定义于 `pyproject.toml` 的 `[build-system]` 表的 `build-backend` 字段
F-003: `build-system.requires` 包含 `hatchling >=1.24` 和 `hatch-vcs >=0.4`
F-004: 运行时依赖包含 `packaging >=23.2`、`pathspec >=0.12.0`，Python <3.11 时额外依赖 `exceptiongroup >=1.0`、`tomli >=1.2.2`、`typing-extensions >=4`
F-005: 可选依赖组 `wheels` 包含 `cmake`（Windows 排除 4.4.0）和 `ninja`
F-006: CLI 入口点 `scikit-build` 和 `scikit-build-core` 均指向 `scikit_build_core.__main__:main`
F-007: `__version__` 从 `._version` 模块导入，定义于 `src/scikit_build_core/__init__.py` 第11行
F-008: `__all__` 在 `src/scikit_build_core/__init__.py` 中仅导出 `["__version__"]`
F-009: 支持 Python 3.9 ~ 3.15 及 Free Threading Python 4（classifiers 声明）
F-010: 许可证为 Apache-2.0，作者为 Henry Schreiner

## 包结构

F-011: 源码位于 `src/scikit_build_core/` 目录下
F-012: 子模块包含：`_compat/`、`_vendor/`、`ast/`、`build/`、`builder/`、`file_api/`、`hatch/`、`init/`、`metadata/`、`resources/`、`settings/`、`setuptools/`、`utils/`
F-013: 顶层模块文件包含：`__init__.py`、`__main__.py`、`_check_extra.py`、`_logging.py`、`_reproducible.py`、`_shutil.py`、`_variants.py`、`cmake.py`、`errors.py`、`format.py`、`program_search.py`
F-014: `_compat/` 子模块包含：`builtins.py`、`tomllib.py`、`typing.py`、`importlib/`（含 `__init__.py` 和 `metadata.py`）、`setuptools/`（含 `__init__.py` 和 `errors.py`）
F-015: `_vendor/` 目录下 vendored 了 `pyproject_metadata` 包
F-016: `resources/` 目录下包含 CMake FindPython 模块、项目模板（abi3/c/cython/fortran/nanobind/pybind11/swig）、`_editable_redirect.py`、`known_wheels.toml`、`scikit-build.schema.json`
F-017: `resources/templates/` 下的模板按语言分目录：abi3、abi3t、c、common、cython、fortran、nanobind、pybind11、swig

## PEP 517 入口点（build/__init__.py）

F-018: `build_wheel(wheel_directory, config_settings=None, metadata_directory=None)` 函数定义于 `src/scikit_build_core/build/__init__.py` 第45-58行，调用 `_build_wheel_impl(..., editable=False)`
F-019: `build_editable(wheel_directory, config_settings=None, metadata_directory=None)` 函数定义于同文件第61-74行，调用 `_build_wheel_impl(..., editable=True)`
F-020: `build_sdist(sdist_directory, config_settings=None)` 函数定义于同文件第124-131行，委托给 `build/sdist.py` 的 `build_sdist` 函数
F-021: `get_requires_for_build_sdist(config_settings=None)` 函数定义于同文件第134-150行，通过 `GetRequires.from_config_settings` 获取依赖
F-022: `get_requires_for_build_wheel(config_settings=None)` 定义于同文件第173-176行，调用 `_get_requires_for_build_wheel(config_settings, state="wheel")`
F-023: `get_requires_for_build_editable(config_settings=None)` 定义于同文件第179-182行，调用 `_get_requires_for_build_wheel(config_settings, state="editable")`
F-024: `prepare_metadata_for_build_wheel` 和 `prepare_metadata_for_build_editable` 仅在 `_has_safe_metadata()` 返回 True 时条件定义（第93-121行）
F-025: `_exit_on_failed_live_process()` 上下文管理器将 `FailedLiveProcessError` 转换为 `SystemExit(1)`
F-026: `_has_safe_metadata()` 检查 pyproject.toml 中是否存在 `if.failed` 或 `if.any.failed` 覆盖条件

## CMake 集成（cmake.py）

F-027: `CMake` 类是一个 frozen dataclass，定义于 `src/scikit_build_core/cmake.py` 第66-98行，包含 `version: Version` 和 `cmake_path: Path` 两个字段
F-028: `CMake.default_search(cls, *, version, module=True, env=None)` 类方法搜索 CMake 可执行文件，支持从 `CMAKE_EXECUTABLE` 环境变量或系统路径查找
F-029: `CMake.__fspath__()` 返回 `os.fspath(self.cmake_path)`
F-030: `CMaker` 类是一个 dataclass，定义于同文件第101-399行
F-031: `CMaker` 字段包括：`cmake: CMake`、`source_dir: Path`、`build_dir: Path`、`build_type: str`、`module_dirs: list[Path]`、`prefix_dirs: list[Path]`、`prefix_roots: dict[str, list[Path]]`、`fresh: bool`、`init_cache_file: Path`、`env: dict[str, str]`、`single_config: bool`、`file_api: Index | None`
F-032: `CMaker.__post_init__()` 创建构建目录、处理 stale 缓存检测、写入 `.skbuild-info.json` 信息文件
F-033: `CMaker.init_cache(cache_settings)` 方法写入 `CMakeInit.txt` 初始缓存文件，支持 bool/Path/str 值类型和 CMAKE_MODULE_PATH/CMAKE_PREFIX_PATH 设置
F-034: `CMaker.configure(*, defines, cmake_args, toolchain)` 执行 cmake 配置，计算参数、选择生成器、运行 cmake 命令、解析 file-api 响应
F-035: `CMaker.build(build_args=(), *, targets, verbose, build_type)` 执行 cmake --build，支持多目标构建
F-036: `CMaker.install(prefix, *, strip, components, targets, build_type)` 执行 cmake --install，支持 component 安装和 strip
F-037: `_compute_cmake_args` 生成 `-S`、`-B`、`--toolchain`、`-C`（init cache）、`-D` 定义等命令行参数
F-038: `single_config` 字段在非 Windows 平台默认为 True（Ninja/Makefiles），Windows 默认为 False

## 配置系统（settings/）

F-039: `ScikitBuildSettings` dataclass 定义于 `src/scikit_build_core/settings/skbuild_model.py` 第824-945行
F-040: `ScikitBuildSettings` 嵌套子配置包括：`cmake: CMakeSettings`、`ninja: NinjaSettings`、`logging: LoggingSettings`、`sdist: SDistSettings`、`wheel: WheelSettings`、`backport: BackportSettings`、`editable: EditableSettings`、`build: BuildSettings`、`install: InstallSettings`、`generate: list[GenerateSettings]`、`messages: MessagesSettings`、`search: SearchSettings`
F-041: `CMakeSettings` 字段包括：`version: SpecifierSet | None`、`args: list[str]`、`define: dict[str, CMakeSettingsDefine]`、`build_type: str | list[str]`（默认 "Release"）、`source_dir: Path`、`toolchain_file: Path | None`（override_only）、`fresh: bool`、`python_hints: bool`
F-042: `NinjaSettings` 字段包括：`version: SpecifierSet`（默认 ">=1.5"）、`make_fallback: bool`（默认 True）
F-043: `WheelSettings` 字段包括：`packages: list[str] | dict[str, str] | None`、`py_api: str`（默认 ""）、`install_dir: str`、`license_files: list[str] | None`、`cmake: bool`（默认 True）、`platlib: bool | None`、`exclude: list[str]`、`build_tag: str`、`tags: list[str] | None`（override_only）、`force_include: dict[str, str]`、`reproducible: bool`
F-044: `SDistSettings` 字段包括：`include: list[str]`、`exclude: list[str]`、`inclusion_mode: "classic" | "default" | "manual" | "explicit" | None`、`reproducible: bool`（默认 True）、`cmake: bool`（默认 False）、`force_include: dict[str, str]`、`resolve_symlinks: "all" | "external" | "none" | "classic" | None`
F-045: `EditableSettings` 字段包括：`mode: "redirect" | "inplace"`（默认 "redirect"）、`verbose: bool`（默认 True）、`rebuild: bool`（默认 False）、`rebuild_dir: str`
F-046: `EditableSettings.rebuild_enabled` 属性返回 `self.rebuild or bool(self.rebuild_dir)`
F-047: `BuildSettings` 字段包括：`tool_args: list[str]`、`targets: list[str]`、`verbose: bool`、`requires: list[str]`
F-048: `InstallSettings` 字段包括：`components: list[str]`、`targets: list[str]`、`strip: bool | None`
F-049: `GenerateSettings` 字段包括：`path: Path`、`template: str`、`template_path: Path | None`、`location: "install" | "build" | "source"`（默认 "install"）
F-050: `CMakeSettingsDefine` 是 `str` 的子类，`__new__` 方法将 bool 转为 "TRUE"/"FALSE"，list 转为 ";" 分隔字符串（转义分号）
F-051: `EnvValue` 类支持三种配置形式：纯字符串（default）、`{env=..., default=..., force=...}` 表、`resolve(env)` 方法解析最终值
F-052: `ScikitBuildSettings.strict_config: bool` 默认为 True
F-053: `ScikitBuildSettings.minimum_version: Version | None` 控制向后兼容行为
F-054: `ScikitBuildSettings.build_dir: str` 默认为空字符串（使用临时目录）
F-055: 标记为 `override_only=True` 的字段包括：`cmake.toolchain_file`、`wheel.tags`、`variant`、`variant_name`、`variant_label`、`null_variant`、`fail`，不能在静态 `[tool.scikit-build]` 表中设置

## 配置源系统（settings/sources.py）

F-056: `Source` Protocol 定义于 `src/scikit_build_core/settings/sources.py` 第282-328行，包含 `has_item`、`get_item`、`convert`、`unrecognized_options`、`all_option_names` 方法
F-057: `EnvSource(prefix, *, env)` 类实现 Source 接口，从环境变量读取配置，前缀为 `SKBUILD`，字段路径映射为大写下划线形式（如 `cmake.args` → `SKBUILD_CMAKE_ARGS`）
F-058: `EnvSource` 中列表值以 `;` 分隔编码，字典值以 `key=value;key=value` 编码
F-059: `ConfSource(*prefixes, settings, verify=True)` 类实现 Source 接口，从 PEP 517 config-settings 读取配置，使用点分键名（如 `cmake.build-type`）
F-060: `TOMLSource(*prefixes, settings)` 类实现 Source 接口，从嵌套 TOML 映射读取配置，支持 dataclass 递归转换
F-061: `SourceChain(*sources, prefixes=())` 类组合多个 Source，按优先级顺序查询，`convert_target(target)` 方法构建 dataclass 实例
F-062: `SourceChain.convert_target` 中 dict 类型字段合并而非替换：后续源的 dict 键值补充到高优先级源的 dict 中
F-063: 配置优先级：环境变量 > config-settings > pyproject.toml（TOMLSource）

## SettingsReader（settings/skbuild_read_settings.py）

F-064: `SettingsReader` 类定义于 `src/scikit_build_core/settings/skbuild_read_settings.py` 第263-693行
F-065: `SettingsReader.__init__` 接收参数：`pyproject: dict`、`config_settings: Mapping`、`state: Literal["sdist","wheel","editable","metadata_wheel","metadata_editable"]`、`extra_settings`、`verify_conf`、`env`、`retry`
F-066: `SettingsReader` 处理 overrides（条件覆盖）、minimum-version 向后兼容、auto-cmake-version（从 CMakeLists.txt 读取 cmake_minimum_required）、entry-point config providers
F-067: `SettingsReader.from_file(pyproject_path, ...)` 类方法从文件读取 pyproject.toml 并构造 SettingsReader
F-068: `SettingsReader.validate_may_exit()` 检查未识别选项并在 strict_config 模式下退出，验证 override-only 字段、metadata provider 配置、generate 模板设置
F-069: `SettingsReader.settings` 属性为解析后的 `ScikitBuildSettings` 实例
F-070: 入口点配置通过 `scikit-build-core.config.default` 和 `scikit-build-core.config.override` entry-point groups 加载，可通过 `SKBUILD_NO_ENTRYPOINT_CONFIG` 环境变量禁用

## 程序搜索（program_search.py）

F-071: `Program` NamedTuple 包含 `path: Path` 和 `version: Version | None` 两个字段
F-072: `get_cmake_programs(*, module=True)` 生成器依次查找：pip 安装的 cmake 模块、系统 PATH 中的 cmake/cmake3
F-073: `get_ninja_programs(*, module=True)` 生成器依次查找：pip 安装的 ninja 模块、系统 PATH 中的 ninja-build/ninja/samu
F-074: `get_make_programs()` 查找系统 PATH 中的 gmake/make
F-075: `best_program(programs, *, version)` 选择第一个版本匹配 SpecifierSet 的程序
F-076: CMake 版本通过 `cmake -E capabilities` JSON 输出获取，失败时回退到 `cmake --version`
F-077: `compute_timeout(executable)` 根据 CI/Windows/Rosetta/Apple Silicon 调整超时时间（基础 5 秒）

## 构建器（builder/）

F-078: `Builder` 类定义于 `src/scikit_build_core/builder/builder.py`
F-079: `get_archs(env, cmake_args)` 函数解析 macOS ARCHFLAGS 环境变量和 CMAKE_SYSTEM_PROCESSOR 参数，返回架构列表
F-080: `archs_to_tags(archs)` 将 `["arm64", "x86_64"]` 转换为 `["universal2"]`
F-081: `builder/sysconfig.py` 提供 `get_python_include_dir`、`get_python_library`、`get_soabi`、`get_platform`、`get_numpy_include_dir` 等函数
F-082: `builder/generator.py` 中的 `parse_generator` 解析 cmake 参数中的生成器设置，`set_environment_for_gen` 设置生成器环境变量
F-083: `builder/get_requires.py` 中的 `GetRequires` 类计算构建所需的 cmake/ninja/variants/dynamic_metadata 依赖

## CMake File API（file_api/）

F-084: `file_api/query.py` 中的 `stateless_query(build_dir)` 在构建目录写入无状态 CMake File API 查询
F-085: `file_api/reply.py` 中的 `load_reply_dir(query_dir)` 读取并解析 CMake File API 回复
F-086: `file_api/model/` 包含 typed dataclass 模型：`Index`、`CodeModel`、`Cache`、`CMakeFiles`、`Directory`、`Toolchains`、`cache.py`、`cmakefiles.py`、`codemodel.py`、`common.py`、`directory.py`、`index.py`、`toolchains.py`

## Editable 安装（build/_editable.py）

F-087: `editable_redirect(...)` 函数生成 redirect 模式的 editable 安装重定向脚本，从 `resources/_editable_redirect.py` 模板读取并追加 install() 调用
F-088: 两种 editable 模式：`redirect`（默认，使用 .pth 文件 + sys.meta_path 重定向器）和 `inplace`（简单 .pth 文件指向源码目录）
F-089: redirect 模式下 `editable.rebuild = true` 时，导入时触发 CMake 重构建
F-090: `editable.rebuild_dir` 设置时自动启用 rebuild-on-import，编译产物安装到指定的独立目录

## 错误类型（errors.py）

F-091: 错误类包括 `CMakeConfigError`、`CMakeNotFoundError`、`FailedLiveProcessError`，均定义于 `src/scikit_build_core/errors.py`

## 插件/扩展接口

F-092: Hatch 插件入口点 `hatch.scikit-build` 指向 `scikit_build_core.hatch.hooks`
F-093: setuptools 兼容层通过 `distutils.commands.build_cmake` 和 `distutils.setup_keywords.*` 入口点提供
F-094: dynamic-metadata 插件入口点包括：`scikit_build_core.metadata.regex`、`scikit_build_core.metadata.template`、`scikit_build_core.metadata.setuptools_scm`、`scikit_build_core.metadata.fancy_pypi_readme`
F-095: `validate_pyproject.tool_schema.scikit-build` 入口点指向 `scikit_build_core.settings.skbuild_schema:get_skbuild_schema`，提供 JSON Schema 验证

## 元数据处理（build/metadata.py）

F-096: `get_standard_metadata()` 函数使用 vendored `pyproject_metadata` 解析 `[project]` 表
F-097: 动态元数据插件通过 `builder/_load_provider.py` 加载

## 日志（_logging.py）

F-098: `_logging.py` 提供基于 rich 的彩色输出和结构化日志，包含 `logger`、`rich_print`、`rich_warning`、`rich_error`
