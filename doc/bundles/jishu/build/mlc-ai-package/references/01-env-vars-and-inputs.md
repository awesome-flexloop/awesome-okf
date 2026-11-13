---
type: reference
title: 环境变量与输入参数
description: 全仓环境变量、workflow 输入与命令参数的速查表
tags:
  - mlc-ai
  - reference
  - environment
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/scripts/"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/scripts/"
  - "external/dev/libs/mlc-ai/package/packages/mlc-ai/scripts/"
  - "external/dev/libs/mlc-ai/package/.github/workflows/"
---

# 环境变量与输入参数

## mlc-llvm-static：构建控制

| 变量 | 取值 | 作用 |
|---|---|---|
| `MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD` | `1` | 允许真正编译 LLVM；缺省时 CMake 直接 `FATAL_ERROR` |
| `MLC_LLVM_STATIC_PREFIX` | 路径 | 重打包既有 SDK（不编译）；其父目录须含 `licenses/` 与 `staticlib.json` |
| `MLC_LLVM_STATIC_TARGETS` | 如 `all` | 传给 `LLVM_TARGETS_TO_BUILD`，默认 `all` |
| `MLC_LLVM_STATIC_SOURCE_CACHE` | 路径 | 源码归档缓存目录，默认 `<work>/sources` |
| `MLC_LLVM_STATIC_LLVM_SOURCE_DIR` | 路径 | 用已有 LLVM 源码树 |
| `MLC_LLVM_STATIC_ZLIB_SOURCE_DIR` | 路径 | 用已有 zlib 源码树 |
| `MLC_LLVM_STATIC_ZSTD_SOURCE_DIR` | 路径 | 用已有 zstd 源码树 |
| `MLC_LLVM_STATIC_BUILD_WORK` | 路径 | 源码解压与 LLVM 对象目录，默认 `<work>/source-build` |
| `MLC_LLVM_STATIC_USE_CACHE` | `1` | 读写 `.sdk-cache/all-sdk.zip` |
| `MLC_LLVM_STATIC_CLEAN_BUILD` | `1` | 分片前删除 `work/source-build` |
| `MLC_LLVM_STATIC_OBJCOPY` | 路径 | `llvm-objcopy`（Windows 必需） |
| `MLC_LLVM_STATIC_7ZIP` | 路径 | 7-Zip 可执行文件 |
| `MLC_LLVM_STATIC_PROFILE` | `auto`/`native`/`all` | profile 选择（构建期与运行期共用） |
| `MLC_LLVM_STATIC_SDK_PREFIX` | 路径 | 前端覆盖 SDK 前缀（测试用） |
| `CMAKE_BUILD_PARALLEL_LEVEL` | 整数 | 并行度 |

## mlc-llvm-static：命令参数

```bash
# build_wheels.py
--output <dir>            # 默认 <project>/wheelhouse
--work-root <dir>         # 默认 <project>/build/split-sdk
--stage-native <dir>      # 只 staging（CMake 集成用）
--platform-tag <tag>      # retag（如 manylinux_2_28_x86_64）

# prepare_llvm.py
--output <dir>            # 必需
--work-root <dir>         # 必需

# compress_wheel.py <wheel...>          # 位置参数
# verify_split_wheels.py <wheelhouse>   # 位置参数
# stamp_version.py [version] [--suffix]
# cache_key.py                          # 无参数，输出 key=<hash>
```

## mlc-z3-static

| 变量 | 作用 |
|---|---|
| `MLC_Z3_STATIC_SOURCE_DIR` | 用已有 Z3 源码树 |
| `MLC_Z3_STATIC_PACKAGE_DIR` | staging 目录（CMake 传入） |
| `MLC_Z3_STATIC_BUILD_ROOT` | 内层构建根（CMake 传入） |
| `MLC_Z3_STATIC_CMAKE_COMMAND` | 内层使用的 cmake（CMake 传入） |
| `MLC_Z3_STATIC_CMAKE_GENERATOR` | 内层生成器 |
| `MLC_Z3_STATIC_CMAKE_GENERATOR_PLATFORM` | Windows `-A` 平台 |
| `MLC_Z3_STATIC_BUILD_TYPE` | 默认 `Release` |
| `MLC_Z3_STATIC_EXTRA_CMAKE_ARGS` | 追加 CMake 参数 |
| `MLC_Z3_STATIC_STATIC_EXTRA_CMAKE_ARGS` | 按 kind 追加（`<KIND>` 大写） |
| `CMAKE_BUILD_PARALLEL_LEVEL` | 并行度 |

CLI：

```bash
python -m mlc_z3_static.config [--kind static] \
  [--prefix | --cmake-dir | --include-dir | --library-dir]
```

## mlc-doxygen-bin

| 变量 | 作用 |
|---|---|
| `MLC_DOXYGEN_BIN_SOURCE_DIR` | 用已有 Doxygen 源码树 |
| `MLC_DOXYGEN_BIN_PACKAGE_DIR` | staging 目录 |
| `MLC_DOXYGEN_BIN_BUILD_ROOT` | 内层构建根 |
| `MLC_DOXYGEN_BIN_CMAKE_COMMAND` | 内层 cmake |
| `MLC_DOXYGEN_BIN_CMAKE_GENERATOR` | 内层生成器 |
| `MLC_DOXYGEN_BIN_CMAKE_GENERATOR_PLATFORM` | Windows `-A` 平台 |
| `MLC_DOXYGEN_BIN_BUILD_TYPE` | 默认 `Release` |
| `MLC_DOXYGEN_BIN_EXTRA_CMAKE_ARGS` | 追加 CMake 参数（Windows ARM64 必传 `-DICONV_DIR=`） |
| `FLEX_EXECUTABLE` / `BISON_EXECUTABLE` | 显式指定 flex/bison |
| `CMAKE_BUILD_PARALLEL_LEVEL` | 并行度 |
| `MACOSX_DEPLOYMENT_TARGET` | macOS 最低版本 |

## mlc-ai（nightly / stable）

| 变量 / 参数 | 作用 |
|---|---|
| `MLC_STABLE_BUILD_VER` | 稳定版必须设置的 tag；空或缺失即报错 |
| `--package` | `tvm` / `mlc-llm` |
| `--package-name` | 输出包名（如 `mlc-ai-nightly`、`mlc-ai`） |
| `--revision` | nightly 的检出点，默认 `origin/main`（TVM 用 `origin/mlc`） |
| `--gpu` | `none` / `cuda-12.8` / `cuda-13.0` / `rocm-6.1` / `rocm-6.2` |
| `--skip-checkout` | 用当前检出（nightly 用） |
| `--dry-run` | 只打印不写入（`sync_package.py` / `wheel_prune_and_sync.py` / `update_site.py` / `wheel_upload.py`） |
| `GITHUB_TOKEN` | 上传与清理脚本必需 |
| `AUDITWHEEL_PLAT` | 镜像内设为 `manylinux_2_28_x86_64` |
| `WHEEL_TEST` | `docker/bash.sh` 透传给容器 |
| `CUDA_VISIBLE_DEVICES` | `docker/bash.sh` 透传 |

CLI 参数（`wheel_prune_and_sync.py`）：

```bash
--keep-top <n>       # 每组保留条数，默认 1
--site-path <dir>    # 站点仓路径，默认 mlc-ai.github.io
--repo <owner/name>  # 默认 mlc-ai/package
--dry-run
```

## GitHub Actions workflow 输入

### `mlc_llvm_static_wheel.yml`

| 输入 | 类型 | 默认 | 作用 |
|---|---|---|---|
| `version_suffix` | string | `""` | 追加 PEP 440 后缀 |
| `publish` | boolean | `false` | 是否发布到 PyPI |
| `repository_url` | string | `""` | 自定义 PyPI 兼容仓库 |
| `publish_packages` | choice | `both` | `both` / `mlc-llvm-static` / `mlc-llvm-static-extra-targets` |

### `mlc_z3_static_wheel.yml` / `mlc_doxygen_bin_wheel.yml`

| 输入 | 默认 | 作用 |
|---|---|---|
| `version_suffix` | `""` | 同上 |
| `publish` | `false` | 同上 |
| `repository_url` | `""` | 同上 |

### `wheel_manylinux.yaml` / `wheel_win.yaml` / `wheel_applesiliconmac.yaml`

| 输入 | 默认 | 作用 |
|---|---|---|
| `tag` | `""` | 稳定版 tag；空则 nightly |

## workflow 环境变量（YAML 内定义）

| 变量 | 位置 | 值/来源 |
|---|---|---|
| `PKG_KIND` | mlc-ai 三个 wheel workflow | `stable` 当且仅当手动运行且 `tag` 非空 |
| `MLC_STABLE_BUILD_VER` | 同上 | `inputs.tag` 或空 |
| `CC` / `CXX` | llvm workflow 矩阵 | Windows 为 `clang-cl` |
| `MACOSX_DEPLOYMENT_TARGET` | llvm / z3 workflow | `14.0` |
| `PLATFORM_TAG` | llvm workflow | 来自矩阵 `tag` |
| `PACKAGE_VERSION` | llvm workflow | 来自 `checks` 作业输出 |
| `PLATFORM_MATRIX` | llvm `distributions` 作业 | 来自 `checks` 输出 |
| `CIBW_BUILD` | z3 workflow | 如 `cp311-manylinux_x86_64` |
| `CIBW_ARCHS_*` | z3 workflow | 来自矩阵 `arch` |
| `CIBW_ENVIRONMENT_*` | z3 workflow | 传 `CMAKE_BUILD_PARALLEL_LEVEL` / `MACOSX_DEPLOYMENT_TARGET` |
| `MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD` | llvm workflow | `"1"` |
| `MLC_LLVM_STATIC_USE_CACHE` | llvm workflow | `"1"` |
| `MLC_LLVM_STATIC_CLEAN_BUILD` | llvm workflow | `"1"` |

## 运行期可见的常量（生成物）

| 位置 | 常量 |
|---|---|
| `mlc_llvm_static/_version.py` | `__version__`、`LLVM_VERSION` |
| `mlc_llvm_static.metadata()` | `profile`、`targets`、`archive_count`、`files`、`build`、`host_target`、`flags` |
| `mlc_z3_static/_version.py` | `__version__`、`Z3_VERSION`、`Z3_TAG`、`Z3_COMMIT` |
| `mlc_z3_static.staticlib.json` | `artifacts`、`source_archive_sha256`、`license` |
| `mlc_doxygen_bin/_version.py` | `__version__`、`DOXYGEN_VERSION`、`DOXYGEN_TAG` |
| `mlc_doxygen_bin/doxygen.json` | `features`、`executable`、`license` |

## 优先级与互斥关系

```text
MLC_LLVM_STATIC_PREFIX  ──┐
                          ├─ 任一生效则不编译；二者都空且未允许源码构建 → FATAL_ERROR
ALLOW_SOURCE_BUILD=1    ──┘

MLC_LLVM_STATIC_PROFILE: 显式参数 > 环境变量 > auto（看 extra.json 是否存在）

MLC_LLVM_STATIC_<NAME>_SOURCE_DIR: 一旦设置，跳过下载与 SHA 校验（开发用，不可用于发布）
```

## 延伸阅读

- profile 三态语义：[profile 选择与派发](../concepts/07-profile-selection.md)
- 构建配方：[LLVM SDK 构建配方](../concepts/05-llvm-sdk-build-recipe.md)
- CI 缓存键构成：[CI 工作流与 SDK 缓存](../concepts/13-ci-workflows-and-caching.md)
