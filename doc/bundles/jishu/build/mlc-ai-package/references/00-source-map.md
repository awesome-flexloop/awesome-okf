---
type: reference
title: 源码与模块索引
description: 仓库文件地图——每个路径的职责、关键函数与对应概念文档
tags:
  - mlc-ai
  - reference
  - source-map
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/"
---

# 源码与模块索引

## 仓库根

| 路径 | 职责 | 相关概念 |
|---|---|---|
| `README.md` | 四个发行物的总览、包布局、触发语义 | [简介](../concepts/00-introduction.md)、[仓库布局](../concepts/01-repo-layout-and-release-model.md) |
| `.gitmodules` | 唯一子模块 `3rdparty/tlcpack` | [仓库布局](../concepts/01-repo-layout-and-release-model.md) |
| `docker/bash.sh` | 以 `--rm --pid=host` 在镜像内执行命令，按镜像名判断是否加 `--gpus all` | [nightly 流水线](../concepts/12-nightly-and-stable-wheels.md) |
| `docker/Dockerfile.package-*` | 13 个构建环境镜像（cpu/cu117…cu130/rocm56…rocm62） | [nightly 流水线](../concepts/12-nightly-and-stable-wheels.md) |
| `docker/install/**` | 镜像内安装脚本（conda、cmake、cuda、rocm、rust、vulkan、patchelf 等） | 同上 |
| `.github/actions/detect-env-vars/action.yml` | 按可用 CPU 数设 `CMAKE_BUILD_PARALLEL_LEVEL` | [CI 工作流](../concepts/13-ci-workflows-and-caching.md) |

## `packages/mlc-llvm-static/`

### 顶层文件

| 路径 | 职责 |
|---|---|
| `README.md` | 使用说明、构建、发布、验证、打包细节、许可 |
| `DEPENDENCIES.md` | 依赖审计：矩阵、下游要求、静态闭包、元数据需求 |
| `pyproject.toml` | scikit-build-core 配置、`py3` 标签、sdist 排除、pytest testpaths |
| `CMakeLists.txt` | `LANGUAGES NONE` + 源码构建闸门 + staging + install |
| `version.py` | 版本与上游钉扎（单一源） |

### `scripts/`

| 文件 | 关键函数 | 职责 |
|---|---|---|
| `prepare_llvm.py` | `source_tree`、`configure`、`build_dependencies`、`build_llvm`、`validate_prefix`、`relocate_pkgconfig`、`cached_prefix`、`write_version_module`、`main` | 下载/校验/编译上游，staging 并自检 |
| `split_sdk.py` | `read_components`、`closure`、`partitions`、`cmake_value`、`distribution_options`、`record_build`、`filter_headers`、`profile_cmake`、`split_sdk` | 一次构建切两个 payload |
| `build_wheels.py` | `stage_payloads`、`stage`、`build`、`load_llvm_config` | 编排：编译→分片→对拍→构建→压缩→校验 |
| `compact_coff.py` | `coff_contents`、`compact_coff` | Windows 归档符号裁剪 + 结构比对 |
| `compress_wheel.py` | `compress_wheel`、`compress_deflate` | 7-Zip / zipfile 重压缩 + 完整性校验 |
| `packaging_tools.py` | `seven_zip` | 钉扎 7-Zip 26.05，单文件提取 |
| `verify_wheel.py` | `verify_system_library_paths`、`verify_linux_abi`、`exported_symbols`、`dynamic_sdk_dependencies`、`main` | 安装后完整自检 |
| `verify_split_wheels.py` | `targets`、`main` | 四态安装矩阵 |
| `cache_key.py` | （脚本） | 编译配方指纹 |
| `stamp_version.py` | `stamp_version` | 版本后缀与两包互钉 |
| `sdk_build_options.cmake` | — | 段粒度钩子（`-ffunction-sections` / `/Gw`） |
| `cibuildwheel_run.sh` | — | 通过 uv 跑 cibuildwheel 3.3.1 |

### `python/mlc_llvm_static/`

| 文件 | 关键内容 |
|---|---|
| `__init__.py` | `get_prefix`/`get_cmake_dir`/`get_include_dir`/`get_library_dir`/`get_llvm_config`/`metadata`；Windows launcher 定位 |
| `_llvm_config.py` | `Configuration`（`ordered_libraries`、`query`）、`ConfigurationError`、`sdk_prefix`、`main`；同时作为安装进 SDK 的 `bin/llvm-config.py` |
| `config.py` | `--prefix/--cmake-dir/--include-dir/--library-dir/--llvm-config` CLI |
| `_version.py` | 构建期生成（不入库） |

### 其他目录

| 路径 | 职责 |
|---|---|
| `extra-targets/pyproject.toml` | add-on 分发：`wheel.packages = []`、`dependencies = ["mlc-llvm-static==..."]` |
| `extra-targets/CMakeLists.txt` | 把 `MLC_LLVM_STATIC_EXTRA_PAYLOAD` 装进包 |
| `extra-targets/README.md` | add-on 的范围声明 |
| `verify/CMakeLists.txt` | 四组断言（版本/静态性/前缀内/可选依赖关闭）+ 导出控制 |
| `verify/main.cpp` | `mlc_llvm_probe()`：IR 解析 → O2 → bitcode → JIT → 返回 42 |
| `verify/dependencies.cpp` | zlib/zstd 往返 + 压缩 ELF DWARF 解析 |
| `verify/targets/CMakeLists.txt` | 跨目标探针构建（含 profile 头展开） |
| `verify/targets/targets.cpp` | 逐 triple 生成目标文件并校验架构/格式 |
| `verify/exports.lds` / `exports.macos` | 版本脚本与导出列表 |
| `tests/python/` | 10 个测试文件（见[验证体系](../concepts/14-verification-strategy.md)） |

## `packages/mlc-z3-static/`

| 路径 | 职责 |
|---|---|
| `README.md` | 使用、构建、发布、测试、许可、升级 |
| `pyproject.toml` | cibuildwheel 配置、`wheel.exclude`、sdist 排除 |
| `CMakeLists.txt` | `LANGUAGES NONE` + 五个 env 传递 + install |
| `version.py` | `Z3_VERSION` / `Z3_COMMIT` / `Z3_ARCHIVE_SHA256` |
| `scripts/prepare_z3.py` | `download_source_archive`、`safe_extract`、`cmake_generator_platform`、`cmake_configure_command`、`build_and_install`、`relativize_cmake_export(s)`、`validate_stage`、`write_license`、`write_metadata`、`main` |
| `scripts/z3_build_options.cmake` | Z3 段粒度钩子 |
| `scripts/copy_wheel.py` | 原样复制（不做 auditwheel） |
| `scripts/wheel_manylinux_2_28.sh` / `wheel_macos.sh` / `wheel_windows.ps1` | 本机发布构建 |
| `scripts/cibuildwheel_run.sh` | uv + cibuildwheel 3.3.1 |
| `python/mlc_z3_static/` | `__init__.py`（路径 API）、`config.py`（CLI） |
| `example_project/` | uv 管理的完整消费方（CMake + Python） |
| `tests/python/` | `test_config.py`、`test_cmake_consumer.py` |

## `packages/mlc-doxygen-bin/`

| 路径 | 职责 |
|---|---|
| `README.md` | 运行时范围、构建依赖、ARM64 限制、许可 |
| `pyproject.toml` | `[project.scripts] doxygen`、cibuildwheel（含 `before-all`） |
| `CMakeLists.txt` | `LANGUAGES NONE` + staging + install |
| `version.py` | `DOXYGEN_VERSION` / 派生 tag / SHA-256 |
| `scripts/prepare_doxygen.py` | `find_program`（brew 优先）、`cmake_generator_platform`、`cmake_configure_command`、`build_and_install`、`copy_runtime`、`write_license`、`write_metadata`、`main` |
| `scripts/install_manylinux_build_tools.sh` | 在 manylinux 内装 Bison、构建 Flex 2.6.4 |
| `scripts/wheel_macos.sh` | 自动前置 Homebrew 的 flex/bison 目录 |
| `python/mlc_doxygen_bin/` | `__init__.py`（`get_executable_path`/`metadata`）、`cli.py`（透传）、`__main__.py` |
| `tests/python/` | `test_cli.py`（三条通路 + 生成 HTML）、`test_version.py` |

## `packages/mlc-ai/`

| 路径 | 职责 |
|---|---|
| `README.md` | nightly/stable 语义、workflow 表 |
| `scripts/sync_package.py` | `checkout_source`（递归子模块）、`name_with_gpu`、`run_version_py`、`main` |
| `scripts/build_mlc_ai_wheel_manylinux.sh` | TVM 的容器内构建 + auditwheel |
| `scripts/build_mlc_llm_wheel_manylinux.sh` | MLC-LLM 的容器内构建 |
| `scripts/manylinux_build_common.sh` | `parse_gpu_args`、`cuda_archs_for` |
| `scripts/build_mlc_ai_lib_osx.sh` / `build_mlc_llm_lib_osx.sh` | macOS 库构建 |
| `scripts/build_mlc_ai_lib_win.bat` / `build_mlc_llm_lib_win.bat` | Windows 库构建 |
| `scripts/wheel_upload.py` | 删同名 + 指数退避上传 |
| `scripts/wheel_prune_and_sync.py` | 分组、保留、改页面、删资产 |
| `scripts/update_site.py` | 站点内容替换（`skip_list` 保护 `wheels.html` 等） |
| `scripts/cleanup_workspace.sh` | 容器内 root 清理残留 |
| `conda/build.sh`、`conda/tvm-unity/build-environment.yaml` | conda 构建环境 |
| `3rdparty/tlcpack/` | conda recipes 子模块 |

## `.github/workflows/`

| 文件 | 触发 | 作用 |
|---|---|---|
| `mlc_llvm_static_wheel.yml` | PR（路径过滤）/ 手动 | 五平台构建 + 分发校验 + PyPI 发布 |
| `mlc_z3_static_wheel.yml` | 同上 | 六平台 wheel + sdist + 发布 |
| `mlc_doxygen_bin_wheel.yml` | 同上 | 五平台 wheel + sdist + 发布 |
| `wheel_manylinux.yaml` | PR / 手动 / 每日 | mlc-ai 与 mlc-llm 的 Linux 多 GPU 构建 |
| `wheel_win.yaml` | PR / 手动 / 每日 | Windows 构建（conda 环境） |
| `wheel_applesiliconmac.yaml` | PR / 手动 / 每日 | macOS arm64 构建 |
| `prune_nightly.yaml` | 手动 / 每日 | 清理 nightly + 刷新索引页 |
| `build_docker_package.yaml` | 手动 | 构建并推送 6 个打包镜像 |
| `build_docker_ci.yaml` | 手动 | 构建 CI 镜像（cpu / cu128） |

## 阅读顺序建议

1. `README.md`（根）→ 建立四个发行物的心智模型。
2. `packages/mlc-llvm-static/README.md` → 最完整的包，读它的约束段。
3. `scripts/build_wheels.py`（136 行）→ 抓住编排主流程。
4. `scripts/split_sdk.py` → 理解分片与派发。
5. `python/mlc_llvm_static/_llvm_config.py` → 理解消费侧契约。
6. `verify/CMakeLists.txt` + `scripts/verify_wheel.py` → 理解验收标准。
7. 其余两个包 → 与 LLVM 包对照阅读，差异点即设计要点。

## 延伸阅读

- 环境变量全表：[环境变量与输入参数](01-env-vars-and-inputs.md)
- 依赖取舍：[依赖审计要点](02-dependency-audit.md)
