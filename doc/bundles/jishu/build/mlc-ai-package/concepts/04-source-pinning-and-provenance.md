---
type: concept
title: 上游源码钉扎与供应链校验
description: SOURCES 三元组、镜像回退、安全解压、许可证强制与工具链钉扎
tags:
  - mlc-ai
  - supply-chain
  - sha256
  - reproducibility
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/prepare_llvm.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/scripts/prepare_z3.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/scripts/prepare_doxygen.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/packaging_tools.py"
---

# 上游源码钉扎与供应链校验

## 钉扎的数据结构

`prepare_llvm.py` 把三个上游源写成一个字典（F-040）：

```python
SOURCES = {
    "llvm": {
        "version": LLVM_VERSION,
        "url": f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{LLVM_VERSION}/llvm-project-{LLVM_VERSION}.src.tar.xz",
        "sha256": _VERSION["LLVM_ARCHIVE_SHA256"],
    },
    "zlib": {
        "version": "1.3.1",
        "url": "https://github.com/madler/zlib/releases/download/v1.3.1/zlib-1.3.1.tar.gz",
        "mirrors": ["https://zlib.net/fossils/zlib-1.3.1.tar.gz"],
        "sha256": "9a93b2b7dfdac77ceba5a558a580e74667dd6fede4585b91eefb60f03b72df23",
    },
    "zstd": {
        "version": "1.5.7",
        "url": "https://github.com/facebook/zstd/releases/download/v1.5.7/zstd-1.5.7.tar.gz",
        "sha256": "eb33e51f49a15e023950cd7825ca74a4a2b43db8354825ac24fc1b7ee09e6fa3",
    },
}
```

三点值得注意：

1. **LLVM 的 SHA 来自 `version.py`**，与包版本同源；zlib/zstd 的 SHA 内联在这里。这意味着升级 LLVM 只改 `version.py`，升级压缩库要改脚本——但两者的 SHA 都在 `cache_key.py` 的指纹覆盖范围内（F-136）。
2. **只有 zlib 有镜像**：GitHub release 与 zlib.net fossils 双源。LLVM 与 zstd 只走 GitHub。
3. **`version` 字段不是装饰**：它进入缓存键，也进入 `staticlib.json` 的 `sources` 记录。

## 下载与校验的完整状态机

`source_tree()` 的流程可以画成：

```text
指定了 MLC_LLVM_STATIC_<NAME>_SOURCE_DIR？
├─ 是 → 校验该目录含预期 CMakeLists.txt → 直接返回（开发用，不校验 SHA）
└─ 否 → 缓存目录下已有归档且 SHA 匹配？
        ├─ 是 → 检查解压戳记 .mlc-source-sha256
        │       ├─ 匹配 → 复用已解压源码树
        │       └─ 不匹配 → 重新解压
        └─ 否 → 逐个候选 URL 下载到 <name>.part
                ├─ SHA 匹配 → 原子 replace 到正式文件名 → 解压
                └─ 全部失败 → RuntimeError（附带每个 URL 的错误）
```

关键细节：

- **写 `.part` 再 `replace`**：避免半截文件被当成完整归档。`prepare_z3.py` 用的是 `archive.with_suffix(".tmp")`，同构。
- **解压戳记是文件内容**：`stamp.read_text() == spec["sha256"]`，不是 mtime。这样即使缓存被复制到别处，戳记仍然可信。
- **校验失败会删除缓存归档**：`prepare_z3.py` 的 `verify_archive()` 打印期望值与实际值后 `path.unlink()`，防止"坏文件永久占据缓存位"。

## 安全解压：三处实现，一条原则

LLVM 用标准库的 data filter（F-045）：

```python
if not hasattr(tarfile, "data_filter"):
    raise RuntimeError("Source extraction requires a Python with tarfile.data_filter (3.12+ or a maintained 3.10/3.11)")
with tarfile.open(archive) as stream:
    stream.extractall(temporary, filter="data")
```

Z3/Doxygen 则**先逐条检查再解压**（F-046）：

```python
base = extract_dir.resolve()
with tarfile.open(archive, "r:gz") as tar:
    members = tar.getmembers()
    for member in members:
        target = (extract_dir / member.name).resolve()
        if target != base and base not in target.parents:
            raise RuntimeError(f"Refusing to extract path outside destination: {member.name}")
    extract_kwargs = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
    tar.extractall(extract_dir, **extract_kwargs)
```

两处叠加了同一个原则：**归档是外部输入，路径与链接必须被约束**。区别是 LLVM 侧強制要求 `data_filter` 存在（否则拒绝构建），Z3/Doxygen 侧允许旧 Python 但保留显式路径检查。

解压后还有一个结构断言：解压目录下必须**恰好有一个**顶层目录（`len(roots) != 1` 即抛错）。这防止上游打包布局变化时静默取到错误路径。

## 许可证：ship 不出错的硬门禁

三个包都把"许可证文件是否存在"做成构建失败条件，而不是警告：

| 包 | 源文件 | wheel 内目标名 | 缺失时 |
|---|---|---|---|
| llvm | `llvm/LICENSE.TXT`、`compiler-rt/LICENSE.TXT`、zlib `README`、zstd `LICENSE` | `licenses/LLVM.txt` 等四份 | `copy2` 抛 `FileNotFoundError` |
| z3 | `LICENSE.txt` | `licenses/LICENSE-Z3.txt` | 显式 `RuntimeError`（F-052） |
| doxygen | `LICENSE` | `licenses/LICENSE-Doxygen.txt` | 显式 `RuntimeError`（F-053） |

Z3/Doxygen 的注释说明了动机：许可证必须来自**经过 SHA-256 校验的上游源码归档**，而不是仓库里另抄一份。这样 sdist 与 wheel 的许可证来源可追溯。

Doxygen 还多一层：打包代码本身是 MIT，捆绑的 Doxygen 是 GPL-2.0-only，因此 wheel 元数据写 `MIT AND GPL-2.0-only`（F-158）。

## 打包工具也要钉扎

7-Zip 是压缩环节的外部依赖。`packaging_tools.py` 把它变成可校验的制品（F-054、F-055）：

```python
SEVEN_ZIP_VERSION = "26.05"
SEVEN_ZIP = {
    ("Linux", "x86_64"): ("7z2605-linux-x64.tar.xz", "7zzs", "22cf82..."),
    ("Linux", "aarch64"): ("7z2605-linux-arm64.tar.xz", "7zzs", "0b71f6..."),
    ("Darwin", "universal"): ("7z2605-mac.tar.xz", "7zz", "12ef68..."),
}
```

行为要点：

- **Windows 不下载**：直接 `shutil.which("7z")` / `7zz`，缺失即抛错并提示设置 `MLC_LLVM_STATIC_7ZIP`。
- **只提取单个常规文件**：`source.getmember(member)` 后校验 `entry.isfile()`，再逐块复制。注释写明「do not extract arbitrary paths/links」——即使归档被投毒，也无法借此写出任意文件。
- **SHA 不符即抛错**，不像源码归档那样回退镜像（这里没有镜像列表）。

同理，`llvm-objcopy` 也不是随便找一个（F-094）：

```python
version = subprocess.check_output([executable, "--version"], text=True).strip()
if "LLVM" not in version:
    raise RuntimeError("MLC_LLVM_STATIC_OBJCOPY must be LLVM's llvm-objcopy")
```

因为 GNU binutils 的 `objcopy` 名字相同但行为不同，只能靠版本字符串区分。

## 开发用覆盖：三个 SOURCE_DIR

三个包都提供"用本地源码树替代下载"的开关：

| 环境变量 | 校验内容 |
|---|---|
| `MLC_LLVM_STATIC_LLVM_SOURCE_DIR` | 含 `llvm/CMakeLists.txt` |
| `MLC_LLVM_STATIC_ZLIB_SOURCE_DIR` | 含 `CMakeLists.txt` |
| `MLC_LLVM_STATIC_ZSTD_SOURCE_DIR` | 含 `build/cmake/CMakeLists.txt` |
| `MLC_Z3_STATIC_SOURCE_DIR` | 含 `CMakeLists.txt` |
| `MLC_DOXYGEN_BIN_SOURCE_DIR` | 含 `CMakeLists.txt` |

`prepare_llvm.py` 会把这些覆盖记入 `staticlib.json` 的 `source_overrides` 字段（`details.update({... "source_overrides": [...]})`），这是必要的诚实标注：**源码覆盖不享受钉扎保证**，产物元数据要能看出这一点。

## 与缓存键的联动

`cache_key.py` 把 `SOURCES` 里的 `version` + `sha256` 与 `DEFAULT_TARGETS` 一起哈希（F-136）。因此：

- 改 `LLVM_ARCHIVE_SHA256` → 缓存键变化 → 重新编译；
- 改镜像 URL → **不影响**缓存键（URL 不在 recipe 里，只有 version/sha256）→ 复用已有 SDK，这是合理的；
- 改 `prepare_llvm.py` 的 `configure`/`install`/`build_dependencies`/`build_llvm` 函数体 → 缓存键变化。

最后一条依赖 `inspect.getsource`。这意味着**注释与空行改动也会让缓存失效**——是保守但安全的取舍。

## 自检方式

```bash
# 1) 三个上游 SHA 都能在脚本或 version.py 中找到
grep -rn "sha256" packages/mlc-llvm-static/version.py \
  packages/mlc-llvm-static/scripts/prepare_llvm.py | head

# 2) 解压路径约束仍在
grep -n "Refusing to extract path outside" packages/mlc-z3-static/scripts/prepare_z3.py \
  packages/mlc-doxygen-bin/scripts/prepare_doxygen.py

# 3) 7-Zip 钉扎版本与 SHA 表
python -c "import sys; sys.path.insert(0,'packages/mlc-llvm-static/scripts'); import packaging_tools; print(packaging_tools.SEVEN_ZIP_VERSION, len(packaging_tools.SEVEN_ZIP))"

# 4) 缓存键包含源码文本（改一行注释后键应变化）
python packages/mlc-llvm-static/scripts/cache_key.py
```

## 陷阱

- **`SOURCE_DIR` 覆盖不做 SHA 校验**：这是开发便利，不是发布路径。发布构建里不要设这些变量。
- **`tarfile.data_filter` 需要 Python 3.12+/受维护的 3.10/3.11**：CI 用 3.11 并在 `manylinux` 容器里另装 Python，注意容器内解释器版本。
- **镜像列表只对 zlib 存在**：不要假设 LLVM 下载失败会自动重试其他来源。
- **许可证缺失是硬失败**：如果上游改了许可证文件名，构建会红；这是有意的，不要改成 warning。

## 延伸阅读

- 版本字段定义：[单一版本源与版本戳记](02-single-version-source.md)
- 依赖策略与取舍：[依赖审计要点](../references/02-dependency-audit.md)
- 构建配方：[LLVM SDK 构建配方](05-llvm-sdk-build-recipe.md)
