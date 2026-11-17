---
type: spec
title: "mlc-ai/package 源码事实清单"
sources:
  - "external/dev/libs/mlc-ai/package/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-z3-static/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-doxygen-bin/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-ai/README.md"
  - "external/dev/libs/mlc-ai/package/.github/workflows/"
---

# mlc-ai/package 源码事实清单

> R 阶段产出：编号事实 F-001 ~ F-100，每条指向仓库内的具体文件或配置项，不做因果推断。
> 仓库根目录：`external/dev/libs/mlc-ai/package`（下称「仓库根」）。

## 一、仓库定位与顶层结构

F-001: 仓库根 README 的标题为 `Packaging Utils`，正文定义为「a set of packaging utils to build packages in the community」。
F-002: 每个包位于 `packages/<package>/`，各自带独立 README 与独立的 GitHub Actions workflow。
F-003: 根 README 的包表列出四个包：`mlc-z3-static`、`mlc-doxygen-bin`、`mlc-llvm-static`、`mlc-ai`。
F-004: 前三者的发布目标是 PyPI，`mlc-ai` 的发布目标是 `mlc.ai/wheels` 索引页（根 README 包表「Published to」列）。
F-005: `docker/` 位于仓库根，存放构建环境镜像；镜像由 `build_docker_package.yaml` 与 `build_docker_ci.yaml` 手动构建。
F-006: 根 README 声明：PR 只在 `packages/<package>/` 内文件或该包 workflow 变更时构建，且仅改动 Markdown 不触发构建；PR 运行从不发布。
F-007: 根 README 声明手动运行（workflow_dispatch）可构建全部平台；PyPI 包仅在勾选 *Publish to PyPI* 时发布，可指定自定义仓库 URL，`version_suffix` 追加如 `.post1` 的后缀。
F-008: 根 README 声明 `mlc-ai` 的 workflow 接收 `tag` 输入以构建稳定版，否则构建 nightly。
F-009: 根 README 声明 `mlc-ai` 的 wheel workflow 按每日计划构建并从 `main` 上传，随后 `prune_nightly.yaml` 清理旧 nightly wheel 并刷新 wheel 索引。
F-010: 根 README 的「Package layout」段规定：`packages/` 下的 PyPI 包遵循同一标准布局，`mlc-ai` 是例外。
F-011: `.gitmodules` 仅登记一个子模块：`3rdparty/tlcpack` → `https://github.com/tlc-pack/tlcpack`。

## 二、标准包布局与版本单一源

F-012: 标准布局的 `pyproject.toml` 使用 scikit-build-core 构建；版本从 `version.py` 读取；含 `test` extra、pytest `testpaths` 与 cibuildwheel 配置。
F-013: 标准布局的 `version.py` 是包版本与上游钉扎值（release、commit、archive SHA-256）的唯一来源；升级只改这一个文件。
F-014: 标准布局的 `CMakeLists.txt` 负责运行 `scripts/prepare_<upstream>.py` 并把其 staging 输出安装进 wheel。
F-015: 标准布局的 `scripts/` 含 `prepare_<upstream>.py`、`stamp_version.py`、`copy_wheel.py`、`cibuildwheel_run.sh` 与三个平台脚本（`wheel_manylinux_2_28.sh`、`wheel_macos.sh`、`wheel_windows.ps1`）。
F-016: 标准布局的 `python/<module>/` 是 Python 包；`_version.py` 在构建期由 `version.py` 生成并被 gitignore。
F-017: 标准布局的 `tests/python/` 是针对已安装 wheel 运行的 pytest 套件。
F-018: 根 README 明确说明：辅助脚本按包复制而非共享，理由是「each package builds from its own sdist」。
F-019: `mlc-llvm-static/version.py` 定义 `__version__ = "23.1.1"`、`LLVM_VERSION = "23.1.1"`、`LLVM_ARCHIVE_SHA256 = "ebe9be46fe8756d58c5b198ffad0fa2a766257add81a4dc52179bfacc7888ee6"`。
F-020: `mlc-z3-static/version.py` 定义 `__version__ = "5.3.1"`、`Z3_VERSION = "5.3.1"`、`Z3_COMMIT = "ac9156f97cb44e56472e1c841f7a2beb1e976b24"`、`Z3_ARCHIVE_SHA256 = "33558971c286653d47b03f97f9f973d0350629c827cacda2583608ba14d74ea6"`，并由版本号派生 `Z3_TAG = f"z3-{Z3_VERSION}"`。
F-021: `mlc-doxygen-bin/version.py` 定义 `__version__ = "1.18.0"`、`DOXYGEN_VERSION = "1.18.0"`、`DOXYGEN_ARCHIVE_SHA256 = "a1deed70a6785bbec95a2b2a9e419dc7f7b223a9d74a8644ae611c8e2dcdd354"`，并由版本号派生 `DOXYGEN_TAG = "Release_" + DOXYGEN_VERSION.replace(".", "_")`。
F-022: `mlc-llvm-static/scripts/stamp_version.py` 用 `packaging.version.Version` 校验版本，要求 `version.base_version == LLVM_VERSION`，只允许叠加 PEP 440 后缀。
F-023: 同脚本同时改写 `pyproject.toml` 与 `extra-targets/pyproject.toml` 中各一处 `mlc-llvm-static(?:-extra-targets)==` 精确版本要求，并校验匹配次数为 1。
F-024: 同脚本在 `GITHUB_OUTPUT` 存在时写入 `version=<value>`，供后续 workflow 步骤消费。
F-025: `prepare_llvm.py` 的 `write_version_module()` 生成运行期 `mlc_llvm_static/_version.py`，内容含 `__version__` 与 `LLVM_VERSION`，并注明「do not edit」。
F-026: `prepare_z3.py`、`prepare_doxygen.py` 各自有同构的 `write_version_module()`，分别额外生成 `Z3_TAG`/`Z3_COMMIT` 与 `DOXYGEN_TAG`。

## 三、scikit-build-core 与内层 CMake 流水线

F-027: `mlc-llvm-static/pyproject.toml` 的 `build-system.requires` 为 `["scikit-build-core>=0.11", "cmake>=3.31", "ninja"]`，`build-backend` 为 `scikit_build_core.build`。
F-028: 同文件设置 `wheel.py-api = "py3"`、`wheel.packages = ["python/mlc_llvm_static"]`、`build-dir = "build/{wheel_tag}"`。
F-029: 同文件用 `[tool.scikit-build.metadata.version]` 的 `scikit_build_core.metadata.regex` provider 从 `version.py` 读取版本。
F-030: 同文件的 `sdist.exclude` 排除 `build`、`dist`、`wheelhouse`、`.sdk-cache`、`extra-targets` 以及包内 `static`/`licenses`/`staticlib.json`/`_version.py`。
F-031: `mlc-llvm-static/CMakeLists.txt` 声明 `project(mlc_llvm_static LANGUAGES NONE)`，即不编译任何 C/C++ 源码，只做 staging 与 install。
F-032: 同文件在两个环境变量都未设置时报 `FATAL_ERROR`：`MLC_LLVM_STATIC_ALLOW_SOURCE_BUILD` 不等于 `1` 且 `MLC_LLVM_STATIC_PREFIX` 为空——默认拒绝隐式源码构建。
F-033: 同文件用 `add_custom_target(stage_mlc_llvm_static ALL ...)` 调 `scripts/build_wheels.py --stage-native ... --work-root ...`。
F-034: 同文件用 `install(DIRECTORY "${stage}/static" "${stage}/licenses" DESTINATION mlc_llvm_static USE_SOURCE_PERMISSIONS)` 与 `install(FILES ...)` 落 wheel 布局。
F-035: `mlc-z3-static/CMakeLists.txt` 与 `mlc-doxygen-bin/CMakeLists.txt` 同构：`LANGUAGES NONE` + `add_custom_target(... ALL)` + `cmake -E env` 传递 `*_PACKAGE_DIR`、`*_BUILD_ROOT`、`*_CMAKE_COMMAND`、`*_CMAKE_GENERATOR`、`*_CMAKE_GENERATOR_PLATFORM`。
F-036: 两个内层构建脚本都优先使用外层传入的 CMake（`MLC_Z3_STATIC_CMAKE_COMMAND` / `MLC_DOXYGEN_BIN_CMAKE_COMMAND`），避免误用 PATH 上的旧 cmake。
F-037: z3 与 doxygen 的 `pyproject.toml` 都配置 `[tool.cibuildwheel]`：`build = "cp311-*"`、`build-frontend = "build"`、`test-extras = ["test"]`、`test-command = "pytest {project}/tests/python -q"`。
F-038: 两者的 `repair-wheel-command` 都指向 `python scripts/copy_wheel.py {wheel} {dest_dir}`；该脚本只做 `shutil.copy2`，不修改 wheel。
F-039: 两个 `cibuildwheel_run.sh` 均通过 `uv tool run --isolated --from "cibuildwheel==3.3.1"` 运行固定版本 cibuildwheel。

## 四、上游源码钉扎与供应链

F-040: `prepare_llvm.py` 的 `SOURCES` 字典登记 llvm / zlib / zstd 三者的 `version`、`url`、`sha256`；zlib 额外登记 `mirrors`。
F-041: llvm 源地址形如 `https://github.com/llvm/llvm-project/releases/download/llvmorg-<VER>/llvm-project-<VER>.src.tar.xz`。
F-042: zlib 钉扎 1.3.1，`sha256 = "9a93b2b7dfdac77ceba5a558a580e74667dd6fede4585b91eefb60f03b72df23"`；zstd 钉扎 1.5.7，`sha256 = "eb33e51f49a15e023950cd7825ca74a4a2b43db8354825ac24fc1b7ee09e6fa3"`。
F-043: `source_tree()` 先查 `MLC_LLVM_STATIC_<NAME>_SOURCE_DIR` 覆盖；否则按 URL 列表（主源 + 镜像）逐个下载到 `.part` 临时文件，校验通过后原子替换。
F-044: 下载缓存目录由 `MLC_LLVM_STATIC_SOURCE_CACHE` 指定，默认 `<work>/sources`；解压目录用 `.mlc-source-sha256` 戳记判断是否可复用。
F-045: 解压调用 `tarfile.extractall(..., filter="data")`，且在没有 `tarfile.data_filter` 时直接抛错（要求 Python 3.12+ 或受维护的 3.10/3.11）。
F-046: `prepare_z3.py` 的 `safe_extract()` 逐条比对 `member.name` 解析后路径必须位于解压根内，越界即抛 `RuntimeError`。
F-047: `prepare_doxygen.py` 有同构的 `safe_extract()` 与 `download_archive()`，并同样在下载后校验 SHA-256。
F-048: `prepare_z3.py` 在归档已存在但校验失败时打印期望值与实际值并删除该文件（`verify_archive`）。
F-049: z3 的归档 URL 由 commit 派生：`https://github.com/Z3Prover/z3/archive/{Z3_COMMIT}.tar.gz`。
F-050: doxygen 的归档 URL 由 tag 派生：`.../releases/download/{DOXYGEN_TAG}/doxygen-{DOXYGEN_VERSION}.src.tar.gz`。
F-051: `prepare_llvm.py` 在源码构建结束时把 LLVM、compiler-rt、zlib、zstd 的许可证分别复制为 `LLVM.txt`、`compiler-rt.txt`、`zlib.txt`、`zstd.txt`。
F-052: `prepare_z3.py` 的 `write_license()` 要求上游 `LICENSE.txt` 存在，否则抛错；目标名为 `LICENSE-Z3.txt`。
F-053: `prepare_doxygen.py` 的 `write_license()` 要求上游 `LICENSE` 存在，否则抛错；目标名为 `LICENSE-Doxygen.txt`。
F-054: `packaging_tools.py` 钉扎 7-Zip `26.05`，为 Linux x86_64 / Linux aarch64 / macOS 三平台登记归档名、成员名与 SHA-256；Windows 使用本机 `7z`/`7zz`。
F-055: `packaging_tools.py` 只从 tar 包中提取登记名对应的单个常规文件，不整体解压（注释：「do not extract arbitrary paths/links」）。

## 五、LLVM SDK 构建配方

F-056: `prepare_llvm.py` 的 `configure()` 固定 `-DCMAKE_BUILD_TYPE=Release`、`-DCMAKE_INSTALL_LIBDIR=lib`、`-DCMAKE_POSITION_INDEPENDENT_CODE=ON`、`-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDLL`，默认生成器为 Ninja。
F-057: `build_llvm()` 的选项包含 `-DBUILD_SHARED_LIBS=OFF`、`-DLLVM_BUILD_LLVM_DYLIB=OFF`、`-DLLVM_BUILD_LLVM_C_DYLIB=OFF`、`-DLLVM_LINK_LLVM_DYLIB=OFF`。
F-058: 同函数设置 `-DLLVM_ENABLE_PIC=ON`、`-DLLVM_ENABLE_LTO=OFF`、`-DLLVM_ENABLE_ASSERTIONS=OFF`、`-DLLVM_ABI_BREAKING_CHECKS=FORCE_OFF`、`-DLLVM_ENABLE_RTTI=OFF`、`-DLLVM_ENABLE_EH=OFF`。
F-059: 同函数以 `FORCE_ON` 打开 zlib 与 zstd，并显式关闭 libxml2、libedit、ffi、Z3 solver、curl、httplib、libpfm、DIA SDK、bindings、ICU、iconv。
F-060: 同函数遍历 `llvm/tools` 下的每个工具目录，生成 `-DLLVM_TOOL_<NAME>_BUILD=ON|OFF`，仅 `llvm-config` 为 ON。
F-061: 同函数连续两次 configure：第一次仅得到组件图，第二次追加 `distribution_options(build)` 把后端库分配到上游的分离导出集。
F-062: `distribution_options()` 输出 `-DLLVM_DISTRIBUTIONS=Base;Extra;Reference`，Base 组件为 `llvm-headers;llvm-libraries;cmake-exports;base-cmake-exports`，Extra 组件为后端库列表加 `extra-cmake-exports`，Reference 组件为 `llvm-config;reference-cmake-exports`。
F-063: 同函数把 `llvm-config` 的 `BuildVariables.inc` 中 `LLVM_SYSTEM_LIBS` 里的静态库绝对路径改写为库名或 `-l<name>`，使重定位后的 SDK 不再保留构建机路径。
F-064: 同函数依次执行 `install-base-distribution`、`install-extra-distribution`、`install-reference-distribution` 三个目标。
F-065: 仅在 Linux 上额外配置并安装 `compiler-rt` 的 ORC 运行时（`-DCOMPILER_RT_BUILD_ORC=ON`，其余 sanitizer/xray/fuzzer/profile 全关），安装到 `lib/clang/<major>/`。
F-066: `build_dependencies()` 只安装 zlib 的 `zlibstatic` 目标与头文件（含构建目录生成的 `zconf.h`），并关闭 zstd 的 CLI、测试、共享库与多线程支持。
F-067: `validate_native_archive()` 校验归档以 `!<arch>\n` 开头、每个成员头 60 字节且以 `` `\n `` 结尾，并拒绝成员载荷为 LTO bitcode 魔数（`BC\xc0\xde` 或 `\xde\xc0\x17\x0b`）。
F-068: `validate_prefix()` 在存在 `base.json` 时按其中 `files` 逐项校验 SHA-256；否则要求 `bin/llvm-config`、`include/llvm/IR/Module.h`、`lib/cmake/llvm/LLVMConfig.cmake` 存在。
F-069: `validate_prefix()` 要求 `bin/` 下只有 `llvm-config` 一个文件、不含任何 `.so`/`.dylib`/`.dll`、且 `llvm-config --prefix` 报告值等于实际前缀（可重定位）。
F-070: `validate_prefix()` 在 Linux 上要求存在 `lib/clang/*/lib/**/liborc_rt*.a`。
F-071: `relocate_pkgconfig()` 把所有 `.pc` 文件的 `prefix=` 重写为 `prefix=${pcfiledir}/../..`。
F-072: `cached_prefix()` 在 `MLC_LLVM_STATIC_USE_CACHE=1` 时从 `.sdk-cache/all-sdk.zip` 恢复，只接受 `mlc_llvm_static/static/`、`mlc_llvm_static/licenses/`、`mlc_llvm_static/staticlib.json` 前缀条目，并恢复文件权限位。

## 六、SDK 分片（split）机制

F-073: `split_sdk.py` 的 `read_components()` 用正则解析 `tools/llvm-config/LibraryDependencies.inc` 的 `{ "name", "lib"|nullptr, true, {...} }` 结构，并要求存在 `all` 与 `core` 两个组件。
F-074: `closure()` 对组件依赖图递归求传递闭包；`partitions()` 把非本机后端的后端组件依赖提升为 base，其余库归为 extra。
F-075: `partitions()` 为 native 概况重建 `native_components`：剔除 `all`/`all-targets` 和非本机后端组件，再补回 `all-targets -> native` 与裁剪后的 `all`。
F-076: `distribution_options()` 要求 `LLVM_NATIVE_ARCH` 出现在 `LLVM_TARGETS_TO_BUILD` 中且目标数不少于 2（注释：「Split SDKs require an All-target build containing the native backend」）。
F-077: `record_build()` 生成 `share/mlc-llvm-static/build.json`，字段含 `components`、`native_components`、`extra_libraries`、`native`、`targets`、`flags`、`host_target`。
F-078: 同函数从 `llvm-config` 取 `--cflags/--cppflags/--cxxflags/--ldflags/--system-libs`，按平台分别用 `shlex.split(posix=...)` 解析，并把前缀替换为 `${prefix}` 占位；同时剔除 `-I` 与 `-L`/`-LIBPATH:` 开头的项。
F-079: `filter_headers()` 为 `include/llvm/Config/*.def` 与 `Targets.h` 各生成两份：base 侧 `mlc-native/`（只保留本机后端行）与 extra 侧 `mlc-all/`（全量），原文件改写为 `__has_include("llvm/Config/mlc-all/<name>")` 派发器，受 `MLC_LLVM_STATIC_NATIVE_ONLY` 控制。
F-080: `profile_cmake()` 在 `LLVMConfig.cmake` 中读 `base.json` 的 `build_id`/`sdk_version`，存在 `extra.json` 时要求两者 `STREQUAL`，否则 `FATAL_ERROR`。
F-081: 同函数实现 `MLC_LLVM_STATIC_PROFILE` 的 `auto|native|all` 三态解析，并据此设置 `LLVM_AVAILABLE_LIBS` 与 `LLVM_TARGETS_TO_BUILD`；引用 `LLVMExtraExports.cmake` 包在 all 分支内，删除对 `LLVMReferenceExports.cmake` 的 include。
F-082: 同函数在 native 档向 `LLVM_DEFINITIONS` 追加 `-DMLC_LLVM_STATIC_NATIVE_ONLY=1`，并写入 `set_property(GLOBAL PROPERTY LLVM_COMPONENT_LIBS ${LLVM_AVAILABLE_LIBS})`。
F-083: `split_sdk()` 先 `copytree` 全量到 base，再把 `extra_libraries` 对应的 `.a`/`.lib` 与 `LLVMExtraExports*.cmake` 移入 extra；缺失 Extra 导出集即抛错。
F-084: 同函数删除 base 的 `bin/` 后只放入 `_llvm_config.py` 的副本（Unix 下同时放可执行的 `llvm-config`），即上游 `llvm-config` 可执行文件不进任何 wheel。
F-085: 同函数以 `metadata` 的规范化 JSON 的 SHA-256 作为 `build_id`，为 native/all 各生成 `base.json` / `extra.json`，`schema_version=2`，并记录 `files` 全量哈希与 `archive_count`。
F-086: 同函数把 native 概况另存为 `staticlib.json` 供 scikit-build-core 打包使用，并复制 `licenses/`。

## 七、打包后处理与体积控制

F-087: `build_wheels.py` 的 `stage_payloads()` 先 `compact_coff(raw)`，再 `split_sdk(...)`，然后以 raw 前缀中的上游 `llvm-config` 为基准，对 native 与 all 两档逐组件比对 `--link-static --libnames` 输出，不一致即抛错。
F-088: `build_wheels.py` 的 `build()` 用 `python -m build --wheel --no-isolation` 分别构建主包与 `extra-targets`，要求恰得 2 个 wheel。
F-089: 同函数在传入 `--platform-tag` 时对每个 wheel 执行 `python -m wheel tags --remove --platform-tag <tag>`。
F-090: 同函数用 `ThreadPoolExecutor(max_workers=2)` 并行重压缩两个 wheel，随后校验每个 wheel 小于 `100,000,000` 字节。
F-091: 同函数以 zip 成员名集合校验两个 wheel 的 `mlc_llvm_static/` 文件所有权不相交，重叠即抛错。
F-092: `compress_wheel.py` 用 7-Zip 参数 `a -tzip -mm=Deflate -mx=9 -mfb=258 -mpass=3 -mmt=2 -scsUTF-8 -bd -bb0 -y` 重压缩，并校验成员名集合、CRC、原始大小、外部属性、时间戳与注释与源一致，且压缩方式只允许 STORE/DEFLATE。
F-093: 同文件在无 7-Zip 时退化为 Python `zipfile` 的 `compresslevel=9` 重写；`compress_wheel()` 注释说明必须在 retag 之后执行，因为 `wheel tags` 会用默认压缩参数重写归档。
F-094: `compact_coff.py` 的 `compact_coff()` 只对 `system == "Windows"` 生效，要求 `MLC_LLVM_STATIC_OBJCOPY` 或 PATH 上的 `llvm-objcopy`，并校验其版本字符串包含 `LLVM`。
F-095: 同文件用 `coff_contents()` 解析 COFF 归档的节表、符号表、重定位与 COMDAT 辅助记录，把「候选可删符号」限定为：无辅助记录的 STATIC 局部标签、以及 section 0 且 value 0 的无引用未定义声明。
F-096: 同文件把以下对象列入保护集不删：COMDAT 键符号（含 PCH 中 STATIC 存储类的键）、`.drectve` 中 `/INCLUDE`、`/EXPORT`、`/ALTERNATENAME` 引用的符号、重定位或 weak 引用指向的符号、公共定义；遇到 `.gfids`/`.giats`/`.gljmp`/`.gehcont` 守卫表直接抛错。
F-097: 同文件在 `objcopy --strip-symbols` 之后重新解析归档，比对节名、节属性、节载荷 SHA-256、公共定义、COMDAT 记录；任何差异即抛错并打印首个差异。
F-098: 同文件把 `packaging: {coff: "unreferenced-symbols-preserve-comdat-v1", llvm_objcopy: <version>}` 写入 `staticlib.json`，使压缩前后的 SDK 无法混用。

## 八、运行期前端与配置

F-099: `mlc_llvm_static/__init__.py` 暴露 `get_prefix`、`get_cmake_prefix_path`、`get_cmake_dir`、`get_include_dir`、`get_library_dir`、`get_llvm_config`、`metadata`，全部基于 `Path(__file__).resolve().parent` 相对定位；`import` 不下载任何文件（模块 docstring）。
F-100: `_windows_launcher()` 通过 `importlib.metadata.distribution("mlc-llvm-static")` 的 `files` 列表定位 `llvm-config.exe`，找不到再回落 `sysconfig.get_path("scripts")`；注释说明不能只查默认 Scripts 目录（漏 `--user` 安装），也不能查 PATH（可能命中另一个 LLVM）。
F-101: `_llvm_config.Configuration.__init__()` 读取 `share/mlc-llvm-static/base.json`，存在 `extra.json` 时校验 `build_id` 与 `sdk_version` 一致，并按 `auto|native|all` 解析 profile。
F-102: `Configuration.ordered_libraries()` 对组件图做后序 DFS 后整体反转，得到静态链接所需顺序；缺组件抛 `ConfigurationError("... unavailable in the ... profile")`，缺归档抛 `missing static archive`。
F-103: `Configuration.query()` 维护 `--version/--prefix/--bindir/--includedir/--libdir/--cmakedir/--obj-root/--host-target/--targets-built/--components/--build-mode/--build-system/--has-rtti/--assertion-mode` 的直出表。
F-104: 同方法对 `--cflags/--cppflags/--cxxflags` 前置 `-I<prefix>/include`，native 档追加 `-DMLC_LLVM_STATIC_NATIVE_ONLY=1`；对 `--ldflags` 前置 `-L<prefix>/lib`（Windows 为 `-LIBPATH:`）。
F-105: 同方法对 `--link-shared` 直接抛 `ConfigurationError("This SDK only provides static LLVM libraries")`；对未知选项抛 `unknown option`。
F-106: 同方法在 `--quote-paths` 时按 `base.json` 的 `system` 选择 `shlex.quote`（Unix）或 `subprocess.list2cmdline`（Windows）渲染路径。
F-107: `mlc_llvm_static/config.py` 提供 `--prefix/--cmake-dir/--include-dir/--library-dir/--llvm-config` 互斥参数，作为 `python -m mlc_llvm_static.config` 的入口。
F-108: `mlc_llvm_static.metadata(profile)` 返回 `base.json` 副本，all 档合并 `extra.json` 的 `files`，并重算 `targets`、`profile`、`archive_count`。

## 九、Z3 与 Doxygen 包

F-109: z3 的 `prepare_z3.py` 固定 `CMAKE_POSITION_INDEPENDENT_CODE=ON`、`CMAKE_CXX_STANDARD=20`、`Z3_BUILD_LIBZ3_SHARED=OFF`，并关闭 Python/.NET/Java/GO/OCaml/Julia 绑定、可执行文件、测试可执行文件、GMP、git describe 与 git hash。
F-110: 同文件在 Windows 上把 `platform.machine()` 映射为 Visual Studio `-A` 平台值（`AMD64`/`X86_64`→`x64`，`ARM64`/`AARCH64`→`ARM64`，`X86`→`Win32`），并可被 `MLC_Z3_STATIC_CMAKE_GENERATOR_PLATFORM` 覆盖。
F-111: 同文件的 `relativize_cmake_export()` 把导出文件中的 `set(_IMPORT_PREFIX "<绝对 staging 路径>")` 替换为四层 `get_filename_component` 相对推导。
F-112: 同文件的 `validate_relocatable_cmake_exports()` 与 `validate_relocatable_pkgconfig()` 在导出文件或 `.pc` 中仍残留绝对 staging 路径时抛错。
F-113: 同文件的 `main_targets_files()` 同时识别 Z3 4.x 的 `Z3Targets.cmake` 与 Z3 5.x 的 `Z3-<kind>-targets.cmake`。
F-114: z3 的 `pyproject.toml` 声明 `wheel.exclude = ["mlc_z3_static/shared/**"]`，用于排除旧版就地构建遗留的共享库输出。
F-115: doxygen 的 `prepare_doxygen.py` 关闭 `build_wizard`、`build_app`、`build_parse`、`build_search`、`build_doc`、`build_doc_chm`、`use_libclang`、`use_sys_spdlog`、`use_sys_fmt`、`use_sys_sqlite3`，Windows 追加 `-Dwin_static=ON`。
F-116: 同文件的 `find_program()` 在 macOS 上优先用 `brew --prefix --installed` 解析 flex/bison，再回落 `shutil.which`；候选名含 `win_flex`、`win_bison`。
F-117: 同文件在 Windows 目标架构为 ARM64 且未通过 `MLC_DOXYGEN_BIN_EXTRA_CMAKE_ARGS` 提供 `-DICONV_DIR=` 时直接抛错（Doxygen 只自带 x86/x64 iconv）。
F-118: doxygen 的 `write_metadata()` 在 `doxygen.json` 中显式记录 `features = {cli: true, doxywizard: false, search_tools: false, libclang: false}`。
F-119: `mlc_doxygen_bin/cli.py` 的 `main()` 以 `subprocess.run([get_executable_path(), *sys.argv[1:]])` 透传参数与退出码；`pyproject.toml` 的 `[project.scripts]` 注册 `doxygen = "mlc_doxygen_bin.cli:main"`。

## 十、nightly 与稳定版 wheel 流水线（mlc-ai 包）

F-120: `packages/mlc-ai/README.md` 说明该目录不遵循标准包布局，存放的是构建期才克隆的上游项目构建脚本。
F-121: `sync_package.py` 在包名不含 `nightly` 时要求环境变量 `MLC_STABLE_BUILD_VER` 非空，否则抛错（注释：CI 的空表达式得到空串而非未设置，故用 `not` 而非 `is None`）。
F-122: 同脚本的 `checkout_source()` 执行 `git checkout -f <tag>` 与 `git submodule update --init --recursive`，注释说明嵌套子模块（mlc-llm → tvm → tvm-ffi）必须递归同步。
F-123: 同脚本的 `name_with_gpu()` 生成 `-cpu`、`-rocm<digits>`、`-cu<digits>` 后缀，并只改写 `pyproject.toml` 中 `name = "..."` 一行一次。
F-124: `wheel_manylinux.yaml` 的 GPU 矩阵为 `none`、`cuda-12.8`、`cuda-13.0`、`rocm-6.1`、`rocm-6.2`，对应镜像 `mlcaidev/package-{cpu,cu128,cu130,rocm61,rocm62}:655adb5`。
F-125: 同 workflow 的 `PKG_KIND` 由 `workflow_dispatch` 且 `tag` 非空判定为 `stable`，其余为 `nightly`；cron 为 `0 6 * * *`。
F-126: 同 workflow 在构建前用 `docker/bash.sh --no-gpu <image> ./scripts/cleanup_workspace.sh` 以 root 清理自托管 runner 上的残留文件。
F-127: 同 workflow 通过 `softprops/action-gh-release@v3` 上传到 tag `v0.9.dev0` 并标记 prerelease，且仅在 `refs/heads/main` 上执行。
F-128: `build_mlc_ai_wheel_manylinux.sh` 先 `pip install --no-deps ./3rdparty/tvm-ffi` 再 `pip wheel --no-deps`，随后 `auditwheel repair`；排除项含 `libtinfo`、`libtvm_ffi`，CUDA 排除 `libcuda/libcudart/libnvrtc/libcublas/libcublasLt`，ROCm 排除 `libamdhip64/libhsa-runtime64/librocm_smi64/librccl/libhipblas/libhipblaslt`。
F-129: 同脚本写入 `config.cmake` 的选项含 `HIDE_PRIVATE_SYMBOLS ON`、`USE_RPC ON`、`USE_VULKAN ON`、`USE_Z3 OFF`，并按 GPU 分支设置 `USE_LLVM`、`USE_CUDA`/`USE_ROCM`、`USE_CUBLAS`/`USE_HIPBLAS`、`USE_NCCL`/`USE_RCCL`、`USE_CUTLASS`。
F-130: `manylinux_build_common.sh` 的 `cuda_archs_for()` 对 12.8/13.0 追加 `120`，仅 13.0 追加 `110`；基础列表为 `80;89;90a`。
F-131: `wheel_prune_and_sync.py` 按 wheel 名分组（`name-version-...`），nightly 归入同一个 `nightly` 组并以 dev 序号排序，稳定版按版本各自成组。
F-132: 同脚本先 `update_wheel_page()` 生成 `<a href=...>` 列表并提交推送到站点仓，再 `delete_assets()`，注释说明顺序不能反（保证页面不指向已删资产）。
F-133: `wheel_upload.py` 上传前删除同名资产，失败按指数退避（上限 600 秒）加随机抖动重试。
F-134: `build_docker_package.yaml` 的构建矩阵为 `cpu`、`rocm61`、`rocm62`、`cu124`、`cu128`、`cu130`，推送镜像标签为 `git log -1 --format='%h'`。
F-135: `docker/Dockerfile.package-cpu` 以 `quay.io/pypa/manylinux_2_28_x86_64` 为基，依次安装 core、cmake、llvm、vulkan sdk、patchelf、conda、Python 3.13、auditwheel、Rust，并设 `AUDITWHEEL_PLAT=manylinux_2_28_x86_64`。

## 十一、CI 缓存、验证与发布

F-136: `cache_key.py` 把三个上游的 `version`+`sha256`、`DEFAULT_TARGETS`、`prepare_llvm` 与 `split_sdk` 若干函数的**源码文本**、`sdk_build_options.cmake` 全文、以及显式 `CC`/`CXX` 一起做 SHA-256，输出 `key=<hash>`。
F-137: `mlc_llvm_static_wheel.yml` 的缓存路径为 `packages/mlc-llvm-static/.sdk-cache`，键为 `llvm-all-sdk-<platform_tag>-<recipe key>`，并在「打包或验证失败」时仍执行保存（`if: always()` 且未命中且 zip 存在）。
F-138: 同 workflow 的 `checks` 作业先 `stamp_version.py --suffix`，再跑 `pytest packages/mlc-llvm-static/tests/python -q`，最后以 Python 内联脚本生成平台矩阵 JSON。
F-139: 平台矩阵含 Linux x86_64（`ubuntu-latest`，`manylinux_2_28_x86_64`）、Linux aarch64（`ubuntu-24.04-arm`）、macOS arm64（`macos-15`，`macosx_14_0_arm64`）、Windows AMD64（`windows-2022`，`clang-cl`）、Windows ARM64（`windows-11-vs2026-arm`，`clang-cl`）。
F-140: Linux 构建在 `quay.io/pypa/manylinux_2_28_*` 容器内执行，并显式 `export PATH="/opt/python/cp311-cp311/bin:$PATH"`。
F-141: 同 workflow 的 `distributions` 作业按「平台矩阵 × 两个 wheel family」构造期望文件名集合，逐一比对下载产物，再跑 `twine check --strict`，并把 wheel 体积表写入 step summary。
F-142: 同 workflow 的发布作业按 `publish_packages` 选择 `mlc-llvm-static`（环境 `pypi`）或 `mlc-llvm-static-extra-targets`（环境 `pypi-extra-targets`），使用 `pypa/gh-action-pypi-publish`、`id-token: write` 与 `actions/attest-build-provenance@v3`。
F-143: `verify_wheel.py` 校验安装后每个 `metadata()["files"]` 条目存在且 SHA-256 匹配，并校验 `python -m mlc_llvm_static.config` 三个查询的返回值。
F-144: 同脚本把 SDK 复制到含空格的临时目录 `relocated SDK with spaces`，用 `python <prefix>/bin/llvm-config.py` 校验 `--version/--prefix/--includedir/--libdir/--cmakedir` 的可重定位性。
F-145: 同脚本校验 `--quote-paths --link-static --system-libs` 输出中的绝对路径均位于重定位后的前缀内（`verify_system_library_paths`），并拒绝任何 `.so/.dll/.dylib`。
F-146: 同脚本以 `cmake` 构建 `verify/` 探针，链接方式覆盖 `cmake` 与 `llvm-config`（Windows 追加 `whole-archive`），并校验：无动态 SDK 依赖、导出符号集合仅为 `mlc_llvm_probe`（macOS 为 `_mlc_llvm_probe`，Windows 额外允许 `__jit_debug_descriptor` 与 `__jit_debug_register_code`）。
F-147: 同脚本调用探针可执行文件，要求 `mlc_llvm_probe()` 返回 42，并通过子进程加载 DLL 以规避 Windows 上已加载 DLL 无法删除的问题。
F-148: `verify_linux_abi()` 用 `readelf --version-info` 检查 GLIBC ≤ 2.28、GLIBCXX ≤ 3.4.24、CXXABI ≤ 1.3.11、GCC ≤ 7.0.0 的 manylinux_2_28 上限。
F-149: `verify/CMakeLists.txt` 要求 `LLVM_PACKAGE_VERSION` 等于 `MLC_LLVM_EXPECTED_VERSION`，并遍历 `LLVM_AVAILABLE_LIBS` 检查每个目标都存在且类型为 `STATIC_LIBRARY` 或 `INTERFACE_LIBRARY`。
F-150: 同文件校验每个导入目标（含 `ZLIB::ZLIB`、`zstd::libzstd_static`）的实际路径位于 `MLC_LLVM_EXPECTED_PREFIX` 内，并断言 libxml2/libedit/ffi/Z3/curl/httplib/DIA 全部为假。
F-151: 同文件在 Linux 上使用 `-z,defs`、`--exclude-libs,ALL` 与 `exports.lds` 版本脚本，在 macOS 上使用 `-exported_symbols_list`。
F-152: `verify/targets/targets.cpp` 依次初始化全部 TargetInfo/Target/TargetMC/AsmPrinter/AsmParser/Disassembler，对每个传入 triple 生成目标文件，并校验 `getArch()` 与二进制格式（ELF/COFF/Mach-O/Wasm）匹配。
F-153: `verify_split_wheels.py` 依次执行：安装 base（`--no-deps`）→ 断言 profile 为 native → 跑 `verify_wheel.py` → 跑 native targets → 安装 extra → `pip check` → 断言 all 与目标集合 → 跑验证 → 显式 `targets("native")` → 卸载 extra → 断言恢复 native → 再跑验证。
F-154: `tests/python/test_profiles.py` 覆盖 profile 选择、跨 build_id/sdk_version 拒绝、依赖顺序与去重、缺归档提前报错、不支持查询报错、header 派发不覆盖另一 wheel 的文件、组件表格式校验、split 后文件所有权不相交。
F-155: z3 的 `tests/python/test_cmake_consumer.py` 构建并链接一个针对 `z3::libz3` 的小型 CMake 消费方，并检查其未链接动态 `libz3`。
F-156: doxygen 的 `tests/python/test_cli.py` 通过可执行文件路径、`python -m mlc_doxygen_bin` 与 `doxygen` console script 三条通路运行，并为一个极小项目生成 HTML。

## 十二、许可与依赖策略

F-157: `mlc-llvm-static` 的 `license` 元数据为 `Apache-2.0 WITH LLVM-exception AND Zlib AND BSD-3-Clause`，wheel 内 `mlc_llvm_static/licenses/` 存放各组件许可。
F-158: `mlc-z3-static` 为 MIT；`mlc-doxygen-bin` 为 `MIT AND GPL-2.0-only`（打包代码 MIT、捆绑的 Doxygen 可执行文件 GPL-2.0-only）。
F-159: `DEPENDENCIES.md` 依赖矩阵列出 zlib/zstd 为必需，libxml2、libedit、libffi、Z3、libcurl、cpp-httplib、libpfm、DIA SDK、ICU/iconv 均为「保持关闭」。
F-160: 同文件说明 `--system-libs` 的上游实现只从 Support 与 WindowsManifest 构造，且不随请求组件变化。
F-161: 同文件指出静态链接只消除共享库依赖，不会自动隐藏符号；下游 DSO 应使用版本脚本/导出列表，Windows ORC 消费方需接受两个 GDB JIT 钩子符号。
F-162: 同文件给出 LLVM 23.1.1 的标准后端清单（AArch64、AMDGPU、ARM、AVR、BPF、Hexagon、Lanai、LoongArch、Mips、MSP430、NVPTX、PowerPC、RISCV、Sparc、SPIRV、SystemZ、VE、WebAssembly、X86、XCore），并声明 ARC/CSKY/DirectX/M68k/Xtensa 为实验性、被排除。
