---
type: example
title: 从源码构建 LLVM SDK
description: 用 build_wheels.py 编译 All-target SDK 并产出两个 wheel 的完整步骤
tags:
  - mlc-ai
  - llvm
  - build
  - example
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/build_wheels.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/prepare_llvm.py"
---

# 从源码构建 LLVM SDK

## 前置条件

| 项 | 要求 |
|---|---|
| 机器 | 该包 README 建议**用远程构建机**，本地编译是小时级 |
| Python | 3.10+（`tarfile.data_filter` 需要 3.12+ 或受维护的 3.10/3.11） |
| CMake | ≥ 3.31 |
| 生成器 | Ninja |
| 磁盘 | 预留数十 GB（源码 + 对象 + SDK） |
| 工具 | 7-Zip（打包期）、Windows 另需 LLVM 的 `llvm-objcopy` |

## 最简命令

```bash
cd packages/mlc-llvm-static

MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD=1 CMAKE_BUILD_PARALLEL_LEVEL=8 \
  python scripts/build_wheels.py --output wheelhouse

python scripts/verify_split_wheels.py wheelhouse
```

第一条命令会：编译一份 All-target SDK → 切成两个 payload → 构建两个 wheel → 重压缩 → 体积与所有权检查。第二条做四态安装验证，需要 C++ 编译器。

**必须显式设 `MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD=1`**，否则 `CMakeLists.txt` 会直接 `FATAL_ERROR`（F-032）。

## 可用覆盖项

| 环境变量 | 作用 |
|---|---|
| `MLC_LLVM_STATIC_SOURCE_CACHE` | 可复用的源码归档缓存目录 |
| `MLC_LLVM_STATIC_LLVM_SOURCE_DIR` | 用已有 LLVM 源码树（开发用） |
| `MLC_LLVM_STATIC_ZLIB_SOURCE_DIR` | 用已有 zlib 源码树 |
| `MLC_LLVM_STATIC_ZSTD_SOURCE_DIR` | 用已有 zstd 源码树 |
| `MLC_LLVM_STATIC_BUILD_WORK` | 源码解压与 LLVM 对象的目录（建议指向本地盘，避免慢速共享盘） |
| `MLC_LLVM_STATIC_PREFIX` | 重新打包一份既有的 All-target SDK（不编译） |
| `MLC_LLVM_STATIC_OBJCOPY` | `llvm-objcopy` 路径（Windows 必需） |
| `MLC_LLVM_STATIC_7ZIP` | 7-Zip 路径（离线或自定义） |
| `MLC_LLVM_STATIC_TARGETS` | 传给 `LLVM_TARGETS_TO_BUILD`，默认 `all` |
| `MLC_LLVM_STATIC_USE_CACHE` | 为 `1` 时读写 `.sdk-cache/all-sdk.zip` |
| `MLC_LLVM_STATIC_CLEAN_BUILD` | 为 `1` 时分片前删除源码构建树 |
| `CMAKE_BUILD_PARALLEL_LEVEL` | 并行度 |

源码覆盖项不享受 SHA-256 钉扎，但会被记入 `staticlib.json` 的 `source_overrides` 字段。

## 分步执行（便于排错）

`build_wheels.py` 有两条入口：

```bash
# 只 staging：编译 + 分片 + 生成 base/extra 元数据，不构建 wheel
python scripts/build_wheels.py --stage-native /tmp/stage/mlc_llvm_static \
  --work-root /tmp/llvm-build

# 完整构建：staging + 两个 wheel + 压缩 + 校验
python scripts/build_wheels.py --output wheelhouse --work-root /tmp/llvm-build
```

CMake 集成走的是第一条（`CMakeLists.txt` 的 `--stage-native`），因为 scikit-build-core 只需要 staging 目录。

若只想验证编译结果：

```bash
python - <<'PY'
from pathlib import Path
import runpy, sys
sys.path.insert(0, "scripts")
from prepare_llvm import validate_prefix
print(validate_prefix(Path("/tmp/stage/mlc_llvm_static/static")))
PY
```

## 各阶段耗时与观察点

| 阶段 | 观察点 |
|---|---|
| 下载源码 | 三份归档（LLVM、zlib、zstd）落到缓存目录，SHA 校验通过 |
| 编译 zlib/zstd | 很快；注意 zlib 只构建 `zlibstatic` 目标 |
| 首次 configure | 只为拿组件图，不编译 |
| 二次 configure | 带上 Base/Extra/Reference 导出集 |
| 编译 LLVM | 主要耗时；并行度由 `CMAKE_BUILD_PARALLEL_LEVEL` 控制 |
| 三个 install 目标 | `install-base/extra/reference-distribution` |
| ORC 运行时（仅 Linux） | 额外一次 compiler-rt 构建 |
| COFF 裁剪（仅 Windows） | 每个 `.lib` 前后解析比对 |
| 分片 | 文件移动 + 头文件三分 + 注入 profile 逻辑 |
| 上游对拍 | 逐组件比对 Python 前端与 `llvm-config` 输出 |
| 构建 wheel | 两次 `python -m build --wheel --no-isolation` |
| retag + 重压缩 | 7-Zip 3-pass，两个 wheel 并行 |
| 体积/所有权检查 | ≥100 MB 或文件重叠即失败 |

## 常见失败与处理

### `FATAL_ERROR: Install an mlc-llvm-static wheel...`

没设 `MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD=1`，也没设 `MLC_LLVM_STATIC_PREFIX`。

### `Source extraction requires a Python with tarfile.data_filter`

Python 版本过旧。用 3.12+，或 3.10/3.11 的受维护补丁版本。

### `A cached/supplied SDK must include the All-target build graph and split CMake exports`

传入的 `MLC_LLVM_STATIC_PREFIX` 不是 All-target 构建，或缺 `share/mlc-llvm-static/build.json`。分片要求一次含全部后端的构建。

### `Split SDKs require an All-target build containing the native backend`

`LLVM_TARGETS_TO_BUILD` 里没有本机后端，或目标数少于 2。检查是否误设了 `MLC_LLVM_STATIC_TARGETS`。

### `Python llvm-config differs from upstream for <profile>/<component>`

打包期对拍失败：前端算出的库序列与上游 `llvm-config` 不一致。通常是改了 `partitions()` 或 `record_build()` 后没同步前端。

### `Wheels have overlapping file ownership`

分片漏移或多移了文件。检查 `extra_libraries` 集合与 `lib/` 下的实际归档。

### `<wheel>: N bytes exceeds the SDK's 100 MB wheel budget`

超出预算。可考虑的合规手段：确认 Windows 上用了 clang-cl（不是 MSVC）、确认 `compact_coff` 真的执行了、确认 7-Zip 可达（而不是退化为 Python zipfile）。

### `Windows wheel packaging requires llvm-objcopy`

设 `MLC_LLVM_STATIC_OBJCOPY` 指向 LLVM 的 `llvm-objcopy`（不能用 GNU binutils 的 `objcopy`）。

### `MLC_LLVM_STATIC_7ZIP` 相关

Linux/macOS 会自动下载钉扎的 7-Zip；若网络受限，手工提供可执行文件路径。

## 用缓存加速二次构建

```bash
MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD=1 \
MLC_LLVM_STATIC_USE_CACHE=1 \
CMAKE_BUILD_PARALLEL_LEVEL=8 \
  python scripts/build_wheels.py --output wheelhouse
```

行为：

- `prepare_llvm.py` 的 `cached_prefix()` 从 `.sdk-cache/all-sdk.zip` 恢复 raw SDK；
- `build_wheels.py` 在恢复后仍会执行 `compact_coff` 与 `split_sdk`，即"重新打包但不重编译"；
- 恢复时只接受 `mlc_llvm_static/static/`、`mlc_llvm_static/licenses/`、`mlc_llvm_static/staticlib.json` 三类路径，并恢复权限位。

缓存键由 `cache_key.py` 计算，CI 用它做 `actions/cache` 的 key（见 [CI 工作流](../concepts/13-ci-workflows-and-caching.md)）。

## 只重打包（不编译）

```bash
MLC_LLVM_STATIC_PREFIX=/path/to/raw/mlc_llvm_static/static \
  python scripts/build_wheels.py --output wheelhouse
```

约束：`MLC_LLVM_STATIC_PREFIX` 的父目录必须含 `licenses/` 与 `staticlib.json`。`prepare_llvm.py` 会：

1. `validate_prefix()` 校验哈希；
2. 复制到 staging；
3. `relocate_pkgconfig()` 重写 `.pc`；
4. 更新 `staticlib.json` 中 `.pc` 文件的哈希后再次校验。

这条路径用于"同一份 SDK 换版本号重发"或"改打包逻辑后重出 wheel"。

## 验证产物

```bash
# 两个 wheel 都在
ls -lh wheelhouse/*.whl

# 体积接近但不超过 100 MB
python - <<'PY'
from pathlib import Path
for p in sorted(Path("wheelhouse").glob("*.whl")):
    print(f"{p.name}: {p.stat().st_size/1e6:.1f} MB")
PY

# 四态安装矩阵
python scripts/verify_split_wheels.py wheelhouse

# 单跑安装后验证（在已装 wheel 的环境里）
python scripts/verify_wheel.py
```

## 自检方式

```bash
# 1) 编译选项与预期一致
grep -c "LLVM_ENABLE_RTTI=OFF\|LLVM_ENABLE_LTO=OFF\|BUILD_SHARED_LIBS=OFF" \
  scripts/prepare_llvm.py

# 2) 缓存键可复算
python scripts/cache_key.py

# 3) 分片算法单测
pytest tests/python/test_profiles.py -q
```

## 陷阱

- **不要在同一 work-root 里混跑不同 `MLC_LLVM_STATIC_TARGETS`**：缓存键会变，但磁盘目录可能残留。
- **`MLC_LLVM_STATIC_CLEAN_BUILD=1` 会删除 `work/source-build`**：只在该目录确实是本脚本管理时才删（代码有 `resolve()` 比较）。
- **`--no-isolation` 要求环境里已有 `build`**：本地构建前先 `pip install build scikit-build-core cmake ninja wheel`。
- **Windows 上必须先初始化 MSVC 环境**：CI 用 `ilammy/msvc-dev-cmd`；本地请在 "x64 Native Tools" 提示符下运行。
- **不要在 macOS 上期待 x86_64 产物**：默认本机架构；要交叉需另配工具链。

## 延伸阅读

- 构建配方的每一项理由：[LLVM SDK 构建配方](../concepts/05-llvm-sdk-build-recipe.md)
- 分片与所有权：[SDK 分片](../concepts/06-split-sdk-partitioning.md)
- 体积控制：[Windows COFF 裁剪与 wheel 重压缩](../concepts/09-windows-coff-and-wheel-recompression.md)
