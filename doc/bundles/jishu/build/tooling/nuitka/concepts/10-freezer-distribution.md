---
okf_version: "0.2"
type: Concept
title: "打包分发"
description: "Nuitka打包分发系统——Standalone目录分发、Onefile单文件、DLL依赖检测、数据文件收集、子进程导入检测"
tags: ["nuitka", "freezer", "standalone", "onefile", "dll", "distribution"]
sources:
  - id: REF-FRZ-001
    path: "nuitka/freezer/Standalone.py"
    description: "Standalone模式核心"
  - id: REF-FRZ-002
    path: "nuitka/freezer/Onefile.py"
    description: "Onefile模式核心"
  - id: REF-FRZ-003
    path: "nuitka/freezer/DllDependenciesCommon.py"
    description: "DLL依赖通用逻辑"
  - id: REF-FRZ-004
    path: "nuitka/freezer/IncludedEntryPoints.py"
    description: "文件包含管理"
  - id: REF-FRZ-005
    path: "nuitka/freezer/ImportDetection.py"
    description: "子进程导入检测"
prerequisites:
  - "06-module-import-system"
  - "09-c-compilation-backend"
next:
  - "11-plugin-system"
related:
  - "../examples/standalone-build.md"
  - "../examples/onefile-build.md"
  - "../references/plugin-base-api.md"
verified: true
status: active
---

# 打包分发

Nuitka编译的C程序依赖CPython运行时和各种DLL/so文件。打包分发阶段（freezer/模块）负责将所有运行时依赖收集在一起，生成**可分发的**最终产物。两种主要模式：`--standalone`（目录分发）和`--onefile`（单文件分发）。

## 为什么需要打包

C编译后的可执行文件仍然需要：
1. **Python运行时DLL**：python3x.dll（Windows）/libpython3.x.so（Linux）/Python.framework（macOS）
2. **C扩展模块**：被导入的.pyd/.so文件（如numpy.core._multiarray_umath.pyd）
3. **标准库**：未编译为C的标准库模块（.py/.pyc文件）
4. **DLL依赖**：C扩展依赖的第三方DLL（如numpy依赖OpenBLAS.dll）
5. **数据文件**：包内的数据文件（.json、.png、.cfg等）
6. **frozen模块**：CPython启动时自动加载的模块

没有standalone模式，编译出的exe只能在安装了对应Python环境的机器上运行。

## Standalone模式

`--standalone`选项将所有依赖收集到一个`dist/<appname>/`目录中，该目录可以复制到其他机器上直接运行。

### 流程

```
C编译完成（生成<app>.exe）
  │
  ├── 1. 检测DLL依赖 (detectUsedDLLs)
  │     ├── 分析主二进制的DLL导入表
  │     ├── 递归分析每个C扩展的DLL依赖
  │     ├── 过滤系统DLL（白名单/黑名单）
  │     └── 收集需要打包的DLL列表
  │
  ├── 2. 收集Python文件
  │     ├── 编译模块的C扩展(.pyd/.so)
  │     ├── 未编译模块的字节码(.pyc)
  │     └── 标准库模块
  │
  ├── 3. 收集额外文件（插件钩子）
  │     ├── Plugins.getExtraDlls() → 插件提供的DLL
  │     ├── Plugins.considerDataFiles() → 插件提供的数据文件
  │     ├── Plugins.getExtraFiles() → 额外文件
  │     └── --include-data-files/--include-data-dir 用户指定
  │
  ├── 4. 复制文件到dist目录 (copyDllsUsed)
  │     ├── 复制主EXE
  │     ├── 复制所有DLL到dist/
  │     ├── 复制Python文件到dist/的对应包路径
  │     └── 复制数据文件
  │
  └── 5. 后处理
        ├── Windows: 设置DLL搜索路径
        ├── Linux: 设置RPATH=$ORIGIN
        └── macOS: 修正dylib引用路径
```

### DLL依赖检测

DllDependenciesCommon.py和平台特定模块处理DLL检测：

| 平台 | 检测工具 | 说明 |
|------|---------|------|
| Windows | **PEFile** 或 depends.exe | 解析PE文件导入表，递归查找DLL |
| Linux | **ldd** | 解析ELF的NEEDED条目 |
| macOS | **otool -L** | 解析Mach-O的LC_LOAD_DYLIB |

DLL白名单（总是打包）：
- MSVC Redist DLL（vcruntime140.dll, msvcp140.dll等）
- UCRT DLL（ucrtbase.dll等，Windows 10+）
- C扩展模块依赖的第三方DLL

DLL黑名单（从不打包）：
- **api-ms-win-\*.dll**：Windows API集，操作系统提供
- **kernel32.dll, ntdll.dll, user32.dll**等：Windows核心DLL
- **libc.so, libpthread.so, libdl.so**等：Linux系统C库
- **/usr/lib**下的系统库（Linux）
- **/usr/lib**或`/System/Library`下的系统框架（macOS）

### ImportDetection：子进程自动导入检测

CPython启动时会自动加载一些模块（如encodings、codecs、io、abc等），这些模块在用户代码中没有显式import语句。Nuitka通过ImportDetection.py检测：

```python
def detectEarlyImports():
    """启动子进程运行Python，检测启动时自动加载的模块。"""
    # 启动: python -s -S -v -c "pass" 2>&1
    # -s: 不添加用户site目录
    # -S: 不导入site模块
    # -v: 输出import信息到stderr
    # -c "pass": 立即退出
    #
    # 解析stderr输出，提取所有import信息：
    # import 'encodings' # 内置
    # import 'codecs' # 内置
    # ...
```

这些"frozen stdlib"模块被嵌入到二进制中，确保运行时行为与CPython一致。

### IncludedEntryPoint：文件包含管理

IncludedEntryPoint类表示一个需要包含到分发中的文件：

| 属性 | 说明 |
|------|------|
| `source_path` | 源文件路径 |
| `dest_path` | 目标路径（相对于dist目录） |
| `kind` | 类型（"dll", "data", "python_module", "extension"） |
| `package` | 所属Python包（如有） |
| `reason` | 包含原因（用于日志和调试） |

```python
# 示例：添加一个数据文件
yield IncludedDataFile(
    source_path="/path/to/data.json",
    dest_path="mypackage/data.json",
    reason="package data file",
)
```

## Onefile模式

`--onefile`选项在standalone基础上，将整个dist目录压缩为单个可执行文件。

### 流程

```
Standalone处理完成（dist/目录就绪）
  │
  ├── 1. 编译OnefileBootstrap.c为引导程序
  │     └── 不链接Python库，是独立的小exe
  │
  ├── 2. 压缩dist目录
  │     ├── 使用zstandard压缩整个dist目录
  │     └── 生成压缩归档blob
  │
  ├── 3. 追加归档到引导程序
  │     └── 将压缩数据附加到OnefileBootstrap.exe末尾
  │
  └── 4. 运行时流程（用户执行onefile exe时）:
        ├── 1. OnefileBootstrap启动
        ├── 2. 在临时目录（%TEMP%/onefile_xxx/）解压归档
        ├── 3. 启动实际程序
        ├── 4. 等待程序退出
        └── 5. 清理临时目录（--onefile-tempdir-spec控制）
```

### OnefileBootstrap.c

OnefileBootstrap.c是一个独立的C程序（约1000行），职责：
1. 找到自身exe路径
2. 读取exe末尾附加的压缩数据
3. 使用内嵌的zstd解压到临时目录
4. 启动解压后的实际程序（CreateProcess/execv）
5. 等待子进程退出
6. 清理临时文件

### 临时目录策略

通过`--onefile-tempdir-spec`控制临时目录位置：
- `%TEMP%`：默认，系统临时目录
- `%CACHE_DIR%`：用户缓存目录（跨运行保留）
- 自定义路径

### 压缩算法

Nuitka使用**zstandard**（zstd）压缩，兼顾压缩率和速度：
- 压缩级别可通过`--onefile-compression-level`调整（默认约12-15）
- 压缩率通常50-70%（Python程序+DLL压缩效果好）
- 解压速度非常快（GB/s级别）

需要Python环境安装zstandard包；如果Nuitka运行的Python没有zstandard，会尝试查找备用Python。

## 数据文件收集

除了DLL和Python模块，standalone/onefile还需要收集数据文件：

### 自动检测
- 包内的非.py文件（通过包的`__file__`路径推断）
- 插件声明的数据文件（如NumPy的测试数据、Qt的插件目录）

### 用户指定选项

| 选项 | 说明 |
|------|------|
| `--include-data-files=<src>=<dest>` | 包含指定数据文件 |
| `--include-data-dir=<dir>=<dest>` | 包含整个数据目录 |
| `--include-package-data=<pkg>` | 包含包的所有数据文件 |
| `--noinclude-data-files=<pattern>` | 排除匹配的数据文件 |

### 插件贡献

插件通过`considerDataFiles()`方法贡献数据文件：
```python
def considerDataFiles(self, module):
    if module.getFullName() == "mypackage":
        yield self.makeIncludedDataFile(
            source_path="data/config.json",
            dest_path="mypackage/config.json",
            reason="config for mypackage",
        )
```

YAML插件通过配置声明数据文件：
```yaml
data-files:
  - pattern: "resources/*"
    dirs: false
    reason: "UI resources"
```

## 反膨胀（Anti-Bloat）

`anti-bloat`插件通过替换或移除不需要的代码来减小分发体积：
- 移除测试代码（`test/`, `tests/`目录）
- 移除debug日志和断言
- 替换重量级依赖的导入为stub
- 移除`if TYPE_CHECKING:`块中的代码（类型注解，运行时不需要）

## 常见问题与选项

| 选项 | 用途 |
|------|------|
| `--standalone` | 生成目录分发 |
| `--onefile` | 生成单文件分发 |
| `--onefile-tempdir-spec=PATH` | 控制onefile临时目录 |
| `--include-qt-plugins=PLUGINS` | 包含Qt插件 |
| `--windows-disable-console` | Windows下不显示控制台窗口（GUI程序） |
| `--windows-icon-from-ico=FILE` | 设置EXE图标 |
| `--macos-create-app-bundle` | macOS下生成.app包 |
| `--output-dir=DIR` | 指定输出目录 |
| `--output-filename=NAME` | 指定输出文件名 |
