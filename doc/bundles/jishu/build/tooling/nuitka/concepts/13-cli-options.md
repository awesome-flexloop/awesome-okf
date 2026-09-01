---
okf_version: "0.2"
type: Concept
title: "命令行选项系统"
description: "Nuitka命令行选项——分类选项体系、选项解析、配置文件支持、环境变量、常用选项速查"
tags: ["nuitka", "cli", "options", "configuration", "command-line"]
sources:
  - id: REF-OPT-001
    path: "nuitka/Options.py"
    description: "选项定义与解析"
  - id: REF-OPT-002
    path: "nuitka/OptionSpecs.py"
    description: "选项规范"
prerequisites:
  - "00-introduction"
next: null
related:
  - "../examples/basic-compilation.md"
  - "../examples/standalone-build.md"
  - "../examples/onefile-build.md"
verified: true
status: active
---

# 命令行选项系统

Nuitka提供500+个命令行选项，控制编译的各个方面——从基本的输出配置到优化级别、打包选项、调试信息、平台特定设置。选项系统支持命令行参数、配置文件、环境变量三种配置方式。

## 选项分类

Nuitka的选项按功能分为以下几大类：

### 1. 基本控制

| 选项 | 说明 |
|------|------|
| `<filename>` | 要编译的Python脚本/模块/包路径 |
| `--module` | 编译为Python扩展模块（.pyd/.so） |
| `--package=<pkg>` | 编译为包模式 |
| `--run` | 编译后立即执行（编译+运行） |
| `--output-dir=DIR` | 指定输出目录 |
| `--output-filename=NAME` | 指定输出文件名 |
| `--output-dir=DIR` | 输出目录 |

### 2. 分发模式

| 选项 | 说明 |
|------|------|
| `--standalone` | 启用独立分发模式，收集所有依赖到dist目录 |
| `--onefile` | 启用单文件模式（先standalone再压缩） |
| `--onefile-tempdir-spec=SPEC` | Onefile临时目录策略 |
| `--onefile-compression-level=N` | Onefile压缩级别（1-22） |
| `--onefile-no-compression` | Onefile不压缩（更快启动） |
| `--onefile-windows-splash-screen-image=IMG` | Onefile启动闪屏（Windows） |

### 3. 导入控制

| 选项 | 说明 |
|------|------|
| `--follow-imports` | 跟随所有导入（默认） |
| `--nofollow-imports` | 不跟随任何导入（仅编译主脚本） |
| `--follow-import-to=MOD` | 仅跟随指定模块/包 |
| `--nofollow-import-to=MOD` | 不跟随指定模块/包 |
| `--follow-stdlib` | 也编译标准库模块（默认不编译） |
| `--follow-no-test` | 不跟随test/tests目录（默认） |
| `--include-package=PKG` | 包含整个包（即使没有被导入） |
| `--include-module=MOD` | 包含单个模块 |
| `--prefer-source-code-for-extension` | 有源码时优先编译源码而非使用C扩展 |

### 4. 数据文件

| 选项 | 说明 |
|------|------|
| `--include-data-files=SRC=DEST` | 包含数据文件 |
| `--include-data-dir=DIR=DEST` | 包含数据目录 |
| `--include-package-data=PKG` | 包含包的所有数据文件 |
| `--noinclude-data-files=PATTERN` | 排除匹配的数据文件 |
| `--include-raw-directory=DIR` | 包含原始目录内容到根目录 |

### 5. 插件控制

| 选项 | 说明 |
|------|------|
| `--enable-plugin=PLUGIN` | 启用插件 |
| `--disable-plugin=PLUGIN` | 禁用插件 |
| `--plugin-list` | 列出所有可用标准插件 |
| `--user-plugin=PATH` | 加载用户自定义插件 |
| `--plugin-no-detection` | 禁用插件自动检测 |
| `--plugin-enable=list,of,plugins` | 批量启用插件 |

### 6. 优化与性能

| 选项 | 说明 |
|------|------|
| `--lto=MODE` | 链接时优化（auto/yes/no），默认yes |
| `--jobs=N` / `-j N` | 并行编译任务数（默认CPU核心数） |
| `--python-flag=FLAG` | Python标志（-O/-S/-E/-v等） |
| `--python-debug` | 使用Python调试版本 |
| `--no-pgo` | 禁用PGO（Profile-Guided Optimization） |
| `--pgo` | 使用PGO（先运行收集profile，再编译优化） |
| `--pgo-args=ARGS` | PGO运行时参数 |
| `--pgo-executable=PATH` | PGO分析用的Python路径 |
| `--static-libpython` | 静态链接Python库（如果可用） |
| `--full-compat` | 完全兼容模式（禁用某些可能有兼容问题的优化） |

### 7. 输出与调试

| 选项 | 说明 |
|------|------|
| `--debug` | 生成调试版本（无优化、含调试信息、运行时检查） |
| `--verbose` | 输出详细编译信息 |
| `--show-scons` | 显示SCons编译输出 |
| `--show-memory` | 显示内存使用 |
| `--show-progress` | 显示编译进度 |
| `--report=FILE` | 生成编译报告（JSON/XML/HTML） |
| `--xml` | 输出XML格式报告 |
| `--quiet` / `-q` | 静默模式，减少输出 |
| `--generate-c-only` | 仅生成C代码，不调用C编译器 |
| `--recompile-c-only` | 仅重编译C代码（复用之前的C文件） |
| `--clean-cache=CACHE` | 清理指定缓存（ccache/build/all） |
| `--explain-imports` | 解释为什么某模块被包含 |
| `--explain-missing-imports` | 解释为什么某模块未找到 |
| `--trace-execution` | 生成执行追踪代码 |

### 8. 缓存控制

| 选项 | 说明 |
|------|------|
| `--disable-cache=CACHE` | 禁用指定缓存 |
| `--cache-dir=DIR` | 缓存根目录 |
| `--ccache=PATH` | 指定ccache/sccache路径 |
| `--disable-ccache` | 禁用ccache |
| `--clang` | 使用clang而非系统默认编译器 |
| `--mingw64` | Windows下强制使用MinGW64 |
| `--msvc=VERSION` | 指定MSVC版本 |

### 9. Windows 特定选项

| 选项 | 说明 |
|------|------|
| `--windows-console-mode=MODE` | 控制台模式（force/disable/attach） |
| `--windows-disable-console` | 不显示控制台窗口（GUI程序） |
| `--windows-icon-from-ico=FILE` | 设置EXE图标（.ico） |
| `--windows-icon-from-exe=FILE` | 从EXE提取图标 |
| `--windows-file-version=VER` | 文件版本号 |
| `--windows-product-version=VER` | 产品版本号 |
| `--windows-product-name=NAME` | 产品名称 |
| `--windows-company-name=NAME` | 公司名称 |
| `--windows-file-description=DESC` | 文件描述 |
| `--windows-uac-admin` | 请求UAC管理员权限 |
| `--windows-uac-uiaccess` | UAC UI访问权限 |
| `--windows-dependency-tool=TOOL` | DLL依赖工具（depends/pefile） |

### 10. macOS 特定选项

| 选项 | 说明 |
|------|------|
| `--macos-create-app-bundle` | 创建.app应用包 |
| `--macos-app-icon=FILE` | .icns图标文件 |
| `--macos-app-name=NAME` | 应用名称 |
| `--macos-app-version=VER` | 应用版本 |
| `--macos-sign-identity=ID` | 代码签名身份 |
| `--macos-target-arch=ARCH` | 目标架构（x86_64/arm64/universal2） |
| `--macos-minimum-deployment-target=VER` | 最低部署版本 |

### 11. Linux 特定选项

| 选项 | 说明 |
|------|------|
| `--linux-onefile-icon=FILE` | Onefile图标 |
| `--linux-icon=FILE` | 桌面图标 |

## 选项解析流程

选项解析在__main__.py中完成：

```
1. 解析环境变量（NUITKA_*）
2. 加载nuitka.cfg配置文件（项目目录/用户目录/系统目录）
3. 解析命令行参数（optparse）
4. 验证选项组合的合法性
5. 应用默认值
6. 传递给Options模块，供后续阶段使用
```

### 选项优先级（从低到高）
1. Nuitka内置默认值
2. 系统配置文件（`/etc/nuitka.cfg`）
3. 用户配置文件（`~/.nuitka.cfg`）
4. 项目配置文件（`./nuitka.cfg`）
5. 环境变量（`NUITKA_*`）
6. 命令行参数（最高优先级）

## 配置文件支持

Nuitka支持INI格式的配置文件`nuitka.cfg`：

```ini
[nuitka]
# 独立分发模式
standalone = true
# 不显示控制台（Windows GUI）
windows-disable-console = true
# 输出目录
output-dir = build
# 启用插件
enable-plugin = numpy,pyqt6
# 包含数据文件
include-data-files = resources/*=resources/
# 优化级别
lto = yes
```

配置文件位置搜索顺序：
1. `./nuitka.cfg`（当前目录）
2. `~/.config/nuitka/nuitka.cfg`（Linux）/`%APPDATA%/nuitka/nuitka.cfg`（Windows）
3. `/etc/nuitka.cfg`（Linux）

## 环境变量

| 环境变量 | 对应选项 | 说明 |
|---------|---------|------|
| `NUITKA_CCACHE_BINARY` | `--ccache` | ccache路径 |
| `NUITKA_CACHE_DIR` | `--cache-dir` | 缓存目录 |
| `NUITKA_MSVC` | `--msvc` | MSVC版本 |
| `NUITKA_PYTHONPATH` | - | 额外的Python路径 |
| `NUITKA_CONSOLE_MODE` | `--windows-console-mode` | 控制台模式 |
| `NUITKA_LTO` | `--lto` | LTO开关 |
| `NUITKA_JOBS` | `-j` | 并行任务数 |
| `NUITKA_VERBOSE` | `--verbose` | 详细输出 |
| `NUITKA_SYS_PREFIX` | - | Python sys.prefix路径 |

## 常用命令速查

### 编译脚本为可执行文件
```bash
nuitka script.py
```

### 独立可执行文件（包含所有依赖）
```bash
nuitka --standalone --windows-disable-console --output-dir=dist app.py
```

### 单文件分发
```bash
nuitka --onefile --windows-icon-from-ico=app.ico app.py
```

### 编译为扩展模块
```bash
nuitka --module mymodule.py
# 生成mymodule.pyd（Windows）或mymodule.so（Linux/macOS）
```

### 调试版本
```bash
nuitka --debug --show-scons --verbose script.py
```

### 使用Qt插件+数据文件
```bash
nuitka --standalone --enable-plugin=pyqt6 \
       --include-data-files=icons/*=icons/ \
       --windows-disable-console \
       app.py
```

### 带PGO优化
```bash
# 第一步：运行程序收集profile
nuitka --pgo app.py
# 第二步：使用profile数据重新编译（自动执行）
nuitka --pgo app.py
```

### 并行编译加速
```bash
nuitka --standalone -j 8 app.py
```
