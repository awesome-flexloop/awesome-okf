---
type: concept
title: mlc-doxygen-bin 包
description: 只构建 Doxygen CLI、Flex/Bison 探测、Homebrew 优先与 Windows ARM64 的 iconv 限制
tags:
  - mlc-ai
  - doxygen
  - cli
  - packaging
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/scripts/prepare_doxygen.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/pyproject.toml"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/python/mlc_doxygen_bin/"
---

# mlc-doxygen-bin 包

## 定位

把 Doxygen 的**命令行可执行文件**打包成 Python wheel，让构建系统能用 pip 固定 Doxygen 版本，而不依赖系统包管理器。钉扎 `DOXYGEN_VERSION = "1.18.0"`，tag 由版本派生为 `Release_1_18_0`（F-021）。

范围被刻意收窄（该包 README「Runtime scope」段）：只构建 CLI，不捆绑 `doxywizard`、`doxyindexer`、`doxysearch.cgi`、libclang、Graphviz、LaTeX、Ghostscript、PlantUML。这些仍是"需要时由用户自行提供"的外部依赖。

## 构建裁剪

`prepare_doxygen.py` 的选项表（F-115）：

```python
"-Dbuild_wizard=OFF",       # 不要 GUI
"-Dbuild_app=OFF",          # 不要 GUI 的 app 壳
"-Dbuild_parse=OFF",
"-Dbuild_search=OFF",
"-Dbuild_doc=OFF", "-Dbuild_doc_chm=OFF",
"-Duse_libclang=OFF",
"-Duse_sys_spdlog=OFF", "-Duse_sys_fmt=OFF", "-Duse_sys_sqlite3=OFF",
```

两组含义：

| 组 | 目的 |
|---|---|
| `build_*` | 不构建 Doxygen 自带的其他可执行文件与文档产物 |
| `use_sys_*` / `use_libclang` | 不依赖宿主系统上的 spdlog / fmt / sqlite3 / libclang，改为使用 Doxygen 自带的源码 |

第二组是"自包含"的关键：如果用 `use_sys_*`，wheel 就会隐式依赖构建机的系统库版本，装到别的机器上可能缺库。`use_libclang=OFF` 则去掉一个重量级可选依赖。

Windows 上额外加 `-Dwin_static=ON`，把运行时静态链接，减少对 MSVC 可再发行组件的依赖。

## Flex / Bison：Doxygen 的构建期必需工具

Doxygen 的解析器由 `.l` / `.y` 生成，因此构建期必须有 Flex 与 Bison。`find_program()` 的处理顺序值得记住（F-116）：

```python
def find_program(env_name: str, candidates: tuple[str, ...]) -> str | None:
    configured = os.environ.get(env_name)
    if configured:
        return configured
    if platform.system() == "Darwin":
        brew = shutil.which("brew")
        if brew:
            for candidate in candidates:
                result = subprocess.run([brew, "--prefix", "--installed", candidate], ...)
                if result.returncode == 0:
                    path = Path(result.stdout.strip()) / "bin" / candidate
                    if path.is_file():
                        return str(path)
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None
```

三级优先：

1. **显式环境变量** `FLEX_EXECUTABLE` / `BISON_EXECUTABLE`；
2. **macOS 上的 Homebrew 前缀查询**——Apple 提供的 flex/bison 版本过旧，而 `brew --prefix --installed` 能定位到 Cellar 里的新版，且不依赖 PATH 顺序；
3. **PATH 查找**，候选名含 Windows 的 `win_flex` / `win_bison`。

这一步做得细，是因为 Doxygen 的扫描器很大：该包 README 记载 AlmaLinux 8 的 Flex 2.6.1 在生成 Doxygen 的大型 scanner 时可能失败，因此 manylinux 脚本会从 `install_manylinux_build_tools.sh` 装一个钉扎的 Flex 2.6.4 到 `/usr/local`。

## Windows ARM64：一个被显式拒绝的组合

```python
if windows_target_arch() == "ARM64" and "-DICONV_DIR=" not in extra_args:
    raise RuntimeError(
        "Windows ARM64 needs an ARM64 iconv: Doxygen only bundles x86/x64 iconv libraries. "
        "Pass -DICONV_DIR=<prefix> through MLC_DOXYGEN_BIN_EXTRA_CMAKE_ARGS."
    )
```

背景：Doxygen 需要 iconv，但其 Windows 构建只自带 x86/x64 的 iconv 静态库。本仓库不想把第三方 iconv 拉进构建，因此**不发布 Windows ARM64 wheel**，同时保留一条手动出路（显式给 `-DICONV_DIR=`）。

这是一个"明确不支持 + 明确如何自行构建"的处理方式，比"构建出坏产物"好得多。对照 `mlc-z3-static`：它的矩阵含 `win_arm64`，`mlc-doxygen-bin` 不含——差异就来自这条 iconv 约束。

## macOS 的部署目标

```python
if platform.system() == "Darwin":
    deployment_target = os.environ.get("MACOSX_DEPLOYMENT_TARGET")
    if deployment_target:
        cmd.append(f"-DMACOS_VERSION_MIN={deployment_target}")
        cmd.append(f"-DCMAKE_OSX_DEPLOYMENT_TARGET={deployment_target}")
```

两个变量都要传：`CMAKE_OSX_DEPLOYMENT_TARGET` 给 CMake，`MACOS_VERSION_MIN` 给 Doxygen 自己的构建逻辑（它会在代码里写最低系统版本）。

CI 对 Doxygen 固定 `MACOSX_DEPLOYMENT_TARGET=13.0`，平台标签因此是 `macosx_13_0_arm64` / `macosx_13_0_x86_64`——比 LLVM SDK 与 Z3 用的 `14.0` 更低，这是各自二进制实际能做到的下限，不要互相套用。

CI 还会在 macOS 上先 `brew install flex bison`，并把 `FLEX_EXECUTABLE` / `BISON_EXECUTABLE` 写入 `GITHUB_ENV`；Windows 上用 `choco install winflexbison3` 提供 `win_flex` / `win_bison`。这比依赖 `find_program()` 的自动探测更确定——CI 里显式固定工具路径，本地才靠探测。

## staging 与 wheel 布局

`prepare_doxygen.py` 的 `main()`（F-117 相关）：

```python
stage_dir = build_and_install(source_dir, build_root)
executable = copy_runtime(stage_dir, package_dir)
license_path = write_license(package_dir, source_dir)
write_version_module(package_dir)
write_metadata(package_dir, executable, source_dir, license_path)
```

wheel 内布局：

```text
mlc_doxygen_bin/
├── __init__.py
├── __main__.py
├── cli.py
├── _version.py            ← 生成
├── doxygen.json           ← 生成
├── bin/
│   └── doxygen[.exe]      ← 生成
└── licenses/
    └── LICENSE-Doxygen.txt
```

`copy_runtime()` 在非 Windows 上补 `0o755`：

```python
executable.chmod(executable.stat().st_mode | 0o755)
```

这一位很关键：zip 里不带可执行位，安装后 `doxygen` 会 Permission denied。CMake 侧的 `install(DIRECTORY ... USE_SOURCE_PERMISSIONS)` 则保证 wheel 里保住该位。

## 三条调用通路

`tests/python/test_cli.py` 断言三条入口都能用（F-156）：

| 通路 | 实现 |
|---|---|
| Python API | `mlc_doxygen_bin.get_executable_path()` |
| 模块执行 | `python -m mlc_doxygen_bin`（`__main__.py`） |
| console script | `doxygen`（`[project.scripts]` → `cli:main`） |

`cli.py` 的实现只有几行（F-119）：

```python
def main() -> int:
    cmd = [get_executable_path(), *sys.argv[1:]]
    return subprocess.run(cmd, check=False).returncode
```

三个细节：

- **`check=False` + 返回 returncode**：让 Doxygen 的退出码原样透传（Doxygen 在发现文档警告时会返回非零，这是它的正常语义）。
- **`sys.argv[1:]` 直接透传**：不做参数解析，避免与 Doxygen 自己的选项冲突。
- **返回类型是 `int`**：`console_scripts` 会用返回值作为进程退出码。

`__main__.py` 只有 4 行，`cli.py` 只有 7 行——这是"薄包装"的正确形态。

## 元数据结构

`doxygen.json`（F-118）：

```python
{
    "name": "doxygen",
    "doxygen_version": ..., "doxygen_tag": ...,
    "source_repository": ..., "source_archive_url": ..., "source_archive_sha256": ...,
    "source_dir": ..., "package_version": ...,
    "executable": rel(package_dir, executable),
    "license": license_path,
    "features": {"cli": True, "doxywizard": False, "search_tools": False, "libclang": False},
    "platform": platform.platform(), "python": sys.version.split()[0],
}
```

`features` 是显式的"能力声明"：读者不用猜有没有 GUI、有没有搜索工具。`metadata()` 在文件不存在时返回 `{}` 而非抛错——这让"只装了包体"的场景仍可 import。

## cibuildwheel 与构建工具

```toml
[tool.cibuildwheel.linux]
manylinux-x86_64-image = "manylinux_2_28"
manylinux-aarch64-image = "manylinux_2_28"
before-all = "bash scripts/install_manylinux_build_tools.sh"
repair-wheel-command = "python scripts/copy_wheel.py {wheel} {dest_dir}"
```

`before-all` 是这个包独有的：需要在 cibuildwheel 的构建容器里先装好 Flex/Bison（以及必要时升级 Flex）。`repair-wheel-command` 仍是"原样复制"——wheel 里没有需要 auditwheel 处理的共享库。

## 自检方式

```bash
# 1) 只构建 CLI
grep -n "build_wizard\|build_app\|build_search\|use_libclang" packages/mlc-doxygen-bin/scripts/prepare_doxygen.py

# 2) 三条通路可用
doxygen --version
python -m mlc_doxygen_bin --version
python -c "import mlc_doxygen_bin as d; print(d.get_executable_path())"

# 3) 生成一个最小项目的 HTML
mkdir -p /tmp/doxy-demo && printf '/** @file a.h */\nint f(void);\n' > /tmp/doxy-demo/a.h
cd /tmp/doxy-demo && doxygen -g - && doxygen Doxyfile && ls html/index.html

# 4) ARM64 Windows 的显式拒绝
grep -n "ICONV_DIR" packages/mlc-doxygen-bin/scripts/prepare_doxygen.py
```

## 陷阱

- **不要在 Windows ARM64 上直接构建**：会抛错，除非你提供 ARM64 iconv。
- **`doxygen` 的非零退出码可能是正常的**（有警告时），`cli.py` 因此用 `check=False`。
- **不要把 `doxywizard` 当作可用**：`features` 明确为 false。
- **`MACOSX_DEPLOYMENT_TARGET` 要同时设两个 CMake 变量**：只设一个会导致版本元数据与实际二进制不一致。
- **wheel 里 `bin/doxygen` 的可执行位必须保住**：`USE_SOURCE_PERMISSIONS` 与 `chmod` 二者缺一不可。

## 延伸阅读

- 同构的静态包：[mlc-z3-static 包](10-z3-static-package.md)
- 消费示例：[消费 Z3 与 Doxygen](../examples/02-consume-z3-and-doxygen.md)
- CI 矩阵差异：[CI 工作流与 SDK 缓存](13-ci-workflows-and-caching.md)
