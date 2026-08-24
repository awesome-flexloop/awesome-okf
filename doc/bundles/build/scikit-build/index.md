---
okf_version: "0.2"
---

# scikit-build-core 知识库

本知识包是基于 CMake 的 Python 包构建后端 [scikit-build-core](https://scikit-build-core.readthedocs.io/) 的系统化中文教程，基于源码深度阅读生成，覆盖从 PEP 517 接口到 CMake 集成、配置系统、editable 安装的完整知识体系。scikit-build-core 是一个符合 PEP 517 标准的独立构建后端，将 CMake 作为一等公民，通过 Init-Cache 文件与 CMake 通信、通过 CMake File API 程序化读取构建结果，提供三源配置合并（环境变量/config-settings/TOML）、条件覆盖、minimum-version 渐进式功能门控、redirect/inplace 双模式 editable 安装（含 rebuild-on-import）等特性。所有内容均溯源至 scikit-build-core 源码（`external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/` 目录核心模块），遵循 [OKF v0.2 规范](../../meta/okf-spec/index.md)。

## 入门基础（concepts/）

* [scikit-build-core 简介](concepts/00-introduction.md) — 项目定位、解决的问题、与 setuptools/meson-python/cmake-build-extension 的对比、适用场景判断。
* [PEP 517 构建后端接口](concepts/01-pep517-build-backend.md) — PEP 517 钩子函数（build_wheel/build_sdist/build_editable/get_requires/prepare_metadata）、config-settings 传递、构建生命周期、兼容前端列表。
* [快速开始](concepts/02-quickstart.md) — 从零创建 C 扩展包：pyproject.toml + CMakeLists.txt + C 源码最简示例、`scikit-build-core init` 命令、pybind11 快速配置。

## 核心概念（concepts/）

* [配置系统详解](concepts/03-settings-system.md) — ScikitBuildSettings 数据模型、三源配置（EnvSource/ConfSource/TOMLSource）与 SourceChain 优先级链、dict 合并语义 vs 标量替换、CMakeSettingsDefine 类型编码、条件覆盖（overrides）、override-only 字段、strict-config 严格验证。
* [CMake 集成机制](concepts/04-cmake-integration.md) — CMake 类（可执行文件定位与版本检测）、CMaker 类（configure/build/install 生命周期）、CMakeInit.txt 初始缓存文件（SKBUILD_* 变量）、单配置/多配置生成器差异、跨平台编译器配置。
* [构建流程](concepts/05-build-flow.md) — build_wheel 十阶段流程：配置解析→程序搜索→构建目录准备→CMake Configure→Build→Install→Python 包收集→Editable 处理→元数据生成→打包、架构检测（universal2/ARCHFLAGS）、SDist 构建差异、可重现构建。
* [Wheel 与 SDist 打包](concepts/06-wheel-and-sdist.md) — platlib vs purelib 安装目录、Python 包发现（packages 配置/自动发现）、install-dir CMake 安装目标、文件排除与强制包含、PEP 639 许可证文件、wheel 标签（py-api/abi3/tags）、sdist inclusion-mode 文件选择策略、符号链接处理。
* [程序搜索与依赖管理](concepts/07-program-discovery.md) — Program 数据结构、CMake/Ninja/Make 分层搜索顺序（pip 模块→PATH→环境变量）、版本匹配（best_program/SpecifierSet）、超时处理（CI/Windows/Rosetta）、GetRequires 动态依赖计算。

## 高级主题（concepts/）

* [可编辑安装](concepts/08-editable-installs.md) — redirect vs inplace 双模式对比、redirect 模式原理（.pth + sys.meta_path finder）、rebuild-on-import 自动重编译、rebuild-dir 独立构建目录（不污染源码树）、verbose 日志、模式选择决策树。
* [CMake File API](concepts/09-cmake-file-api.md) — CMake File API 原理（stateless query + JSON reply）、typed dataclass 模型（CodeModel/Target/InstallRule/Artifact）、构建产物发现与安装验证、错误诊断信息、跨平台路径处理。
* [动态元数据](concepts/10-dynamic-metadata.md) — PEP 621 dynamic 字段、内置 provider（regex 版本提取/setuptools_scm/template/fancy-pypi-readme）、元数据提供者接口、动态字段与构建阶段依赖关系。
* [插件与兼容层](concepts/11-plugins-and-compat.md) — Hatch 构建插件配置、setuptools 兼容层（build_cmake 命令/distutils entry-points）、配置提供者插件（scikit-build-core.config.default/override）、CMake 工具提供者、JSON Schema 验证。
* [版本门控与向后兼容](concepts/12-version-gating.md) — minimum-version 机制、字段自动迁移（cmake.minimum_version → cmake.version 等）、默认值版本门控、功能启用版本检查、strict-mode 差异、`"build-system.requires"` 自动同步最佳实践。

## 实战示例（examples/）

* [基础 C 扩展](examples/basic-c-extension.md) — 最简 C 扩展模块（add/greet 函数）：pyproject.toml + CMakeLists.txt + C 源码完整代码、Development.Module vs Development 区别、WITH_SOABI 作用、多源文件/头文件/链接库配置、abi3 稳定 ABI。
* [pybind11 C++ 模块](examples/pybind11-module.md) — pybind11_add_module 配置、C++ 类/函数/STL 容器绑定示例、C++ 标准设置、编译选项、abi3 稳定 ABI、nanobind 替代方案、Debug/ASAN 调试构建。
* [Editable 开发工作流](examples/editable-workflow.md) — C++ 扩展开发完整工作流：redirect + rebuild + rebuild-dir 推荐配置、修改 C++→直接测试（rebuild-on-import 自动检测）、Python 源码即时生效、多包开发、inplace 模式、CI 禁用 editable、常见问题排查。

## 信源登记簿（references/）

* [scikit-build-core 源码信源](references/skbuild-core-source.md) — 源码目录结构索引、项目基本信息（Apache-2.0/Python 3.9+）、CLI 入口点、完整 entry-points 清单（build_backend/console_scripts/hatch/metadata/cmake/validate_pyproject）、核心模块路径。
* [配置项速查](references/config-entry-points.md) — pyproject.toml [tool.scikit-build] 全量配置项：cmake/ninja/wheel/sdist/editable/build/install/logging 子表字段类型与默认值、配置优先级（env > config-settings > TOML）、override-only 字段列表、overrides 条件字段。

## 信任与生命周期说明

* **status 判定依据**：全部 18 个内容文档（13 个概念 + 3 个示例 + 2 个信源参考）均 `status: stable`。内容基于对 scikit-build-core 源码（`scikit_build_core/` 目录，核心模块 build/settings/cmake/builder/file_api/program_search 等）的逐模块阅读与事实提取，经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2026-12-01`。scikit-build-core 0.10+ API 相对稳定，核心类（CMaker/SettingsReader/SourceChain/CMake）自 0.5 以来的架构变化主要集中在配置迁移和 minimum-version 门控；该日期作为针对未来大版本升级（如 1.0）的保守重新评估节点。
* **核验链路**：`generated: true` 标记各文档由源码→OKF 工作流生成；`verified: false` 标记 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 18 个内容文档（13 个概念 + 3 个示例 + 2 个信源参考），另含 spec/ 目录下的 facts.md 与 insights.md（R/I 阶段中间产出）和根 index.md。

```{toctree}
:hidden:

concepts/00-introduction
concepts/01-pep517-build-backend
concepts/02-quickstart
concepts/03-settings-system
concepts/04-cmake-integration
concepts/05-build-flow
concepts/06-wheel-and-sdist
concepts/07-program-discovery
concepts/08-editable-installs
concepts/09-cmake-file-api
concepts/10-dynamic-metadata
concepts/11-plugins-and-compat
concepts/12-version-gating
examples/basic-c-extension
examples/editable-workflow
examples/pybind11-module
references/config-entry-points
references/skbuild-core-source
spec/facts
spec/insights
```
