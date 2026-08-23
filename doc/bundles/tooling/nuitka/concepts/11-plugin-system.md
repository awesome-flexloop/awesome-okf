---
okf_version: "0.2"
type: Concept
title: "插件系统"
description: "Nuitka插件扩展机制——NuitkaPluginBase 60+钩子方法、Plugins管理器、YAML声明式插件、34个标准插件"
tags: ["nuitka", "plugin", "hook", "extension", "yaml", "customization"]
sources:
  - id: REF-PLG-001
    path: "nuitka/plugins/Plugins.py"
    description: "插件管理器"
  - id: REF-PLG-002
    path: "nuitka/plugins/PluginBase.py"
    description: "插件基类"
  - id: REF-PLG-003
    path: "nuitka/plugins/NuitkaYamlPluginBase.py"
    description: "YAML插件基类"
  - id: REF-PLG-004
    path: "nuitka/plugins/PluginsMeta.py"
    description: "插件元类"
  - id: REF-PLG-005
    path: "nuitka/plugins/standard/"
    description: "34个标准插件"
prerequisites:
  - "06-module-import-system"
  - "10-freezer-distribution"
next:
  - "12-variables-closures"
related:
  - "../examples/plugin-usage.md"
  - "../references/plugin-base-api.md"
verified: true
status: active
---

# 插件系统

Nuitka的插件系统是其核心扩展机制，允许在不修改Nuitka源码的情况下适配第三方库、修改编译行为、添加额外打包文件、生成定制化代码。插件在编译流程的**每个关键节点**都有钩子回调，提供了细粒度的扩展能力。

## 为什么需要插件

Python生态中有大量第三方库，这些库经常：
1. 使用C扩展，需要特殊的DLL/so打包处理
2. 使用隐式导入（运行时动态加载），静态分析无法发现
3. 包含数据文件（模型、配置、资源），需要被打包
4. 使用了特殊的导入hack（如`__getattr__`延迟加载），需要编译器理解
5. 需要在编译时修改源码（如移除debug检查、patch兼容性问题）

Nuitka通过插件机制处理这些库特殊性——每个主流库（NumPy、PyTorch、Qt、Tkinter等）都有对应的插件。

## Plugins 管理器

[Plugins](file:///d:/spaces/SpecWeave/playground/chaos/libs/Nuitka/nuitka/plugins/Plugins.py)是全局单例，管理所有插件的生命周期。

### 插件分类列表

为了优化遍历效率，Plugins维护7个按回调能力分类的列表：

| 列表 | 包含的钩子 | 调用时机 |
|------|-----------|---------|
| `before_parsing` | `beforeParsing()` | AST解析前 |
| `module_discovery` | `onModuleDiscovered()` | 发现新模块时 |
| `module_encounter` | `onModuleEncountered()` | 遇到导入时（决定是否跟随） |
| `on_module_source_code` | `onModuleSourceCode()` | 读取源码后（可修改） |
| `extra_dlls` | `getExtraDlls()` | Standalone收集DLL时 |
| `data_files` | `considerDataFiles()` | 收集数据文件时 |
| `final_result` | `onFinalResult()` | 编译完成后 |

插件只被加入到它实际实现了的钩子对应的列表中，避免遍历不相关的插件。

### 插件激活流程

```
1. Nuitka启动时:
   Plugins.init(plugins_dir)
     ├── 扫描plugins/standard/目录
     ├── 使用PluginsMeta元类注册所有插件类
     └── 构建插件类列表

2. 激活isAlwaysEnabled()插件:
   for plugin_class in all_plugins:
       if plugin_class.isAlwaysEnabled():
           Plugins.activatePluginByName(plugin_class.plugin_name)

3. 处理用户--enable-plugin/--disable-plugin选项:
   for name in user_enabled:
       Plugins.activatePluginByName(name, options)
   for name in user_disabled:
       Plugins.deactivatePluginByName(name)

4. Detector插件执行检测:
   for detector in detector_plugins:
       detected = detector.detect()  # 检查库是否安装
       if detected:
           Plugins.activatePluginByName(detector.detector_for)

5. 调用onInitialization():
   for plugin in active_plugins:
       plugin.onInitialization()
```

### Detector 插件

Detector插件是一种特殊的插件，它不参与编译过程，只负责**检测系统中是否安装了某库**，从而自动激活对应的实际插件。

```python
class NumpyDetectorPlugin(NuitkaPluginBase):
    plugin_name = "numpy-detector"
    detector_for = "numpy"  # 检测到numpy后激活numpy插件

    @classmethod
    def isDetector(cls):
        return True

    def onModuleEncountered(self, module_name, ...):
        return None  # detector不参与决策

    def detect(self):
        return isInstalledModule("numpy")
```

Detector插件不计入激活插件计数，仅用于自动激活。

## NuitkaPluginBase 钩子

[NuitkaPluginBase](file:///d:/spaces/SpecWeave/playground/chaos/libs/Nuitka/nuitka/plugins/PluginBase.py)定义了约60个可覆盖的钩子方法。以下是最常用的：

### 编译生命周期

| 钩子 | 调用时机 | 典型用途 |
|------|---------|---------|
| `onInitialization()` | 插件激活后，编译开始前 | 初始化插件状态 |
| `onFinalization()` | 编译全部完成后 | 清理资源 |
| `beforeParsing(source_dir)` | AST解析前 | 设置解析选项 |
| `onFinalResult(filename)` | 编译产物就绪后 | 后处理（签名、上传等） |

### 模块处理

| 钩子 | 调用时机 | 返回值 | 典型用途 |
|------|---------|--------|---------|
| `onModuleDiscovered(module)` | 模块树构建前 | None | 记录模块、准备数据 |
| `onModuleEncountered(name, filename)` | 遇到import时 | True/False/None | 决定是否跟随导入 |
| `decideCompilation(module, name)` | 决定编译模式 | "compiled"/"bytecode"/None | 强制某些模块字节码模式 |
| `getImplicitImports(module)` | 收集隐式导入 | yield (name, required) | 声明运行时动态导入 |
| `onModuleSourceCode(name, code)` | 源码读取后 | 修改后的源码 | patch源码兼容性 |
| `onFrozenModuleSourceCode(name, pkg, code)` | 冻结模块源码读取后 | 修改后的源码 | patch冻结模块 |
| `onModuleComplete(module)` | 模块优化+代码生成完成后 | None | 模块完成通知 |
| `createPreLoadedModule(name, code)` | 提供fake模块 | 源码字符串 | 替换整个模块实现 |

### 打包分发

| 钩子 | 调用时机 | 返回值 | 典型用途 |
|------|---------|--------|---------|
| `getExtraDlls(module)` | 收集DLL | yield IncludedDLL | 添加C扩展依赖的DLL |
| `considerDataFiles(module)` | 收集数据文件 | yield IncludedDataFile | 添加包数据文件 |
| `getExtraFiles()` | 全局额外文件 | yield IncludedDataFile | 非模块相关的文件 |
| `removeDllDependencies(dll, name)` | 过滤DLL | bool | 排除不需要的DLL |

### 代码生成

| 钩子 | 调用时机 | 返回值 | 典型用途 |
|------|---------|--------|---------|
| `onGeneratedSourceCode(module, filename)` | C文件写入后 | None | 后处理C文件 |
| `getPreprocessorSymbols()` | SCons编译前 | list[(name, value)] | 添加C宏定义 |
| `getExtraBuildFiles()` | 构建时 | list[path] | 添加额外C文件 |

### 选项工具方法

| 方法 | 说明 |
|------|------|
| `getPluginOptionBool(name, default)` | 获取布尔选项 |
| `getPluginOptionString(name, default)` | 获取字符串选项 |
| `getPluginOptionList(name, default)` | 获取列表选项 |
| `getPluginOptionInteger(name, default)` | 获取整数选项 |
| `info(message)` | 输出信息日志 |
| `warning(message)` | 输出警告日志 |

## YAML 声明式插件

很多库适配不需要写Python代码，只需要声明配置。[NuitkaYamlPluginBase](file:///d:/spaces/SpecWeave/playground/chaos/libs/Nuitka/nuitka/plugins/NuitkaYamlPluginBase.py)允许通过YAML配置文件定义插件行为。

### YAML配置示例

```yaml
module_name: "mypackage"
plugin_name: "mypackage"
plugin_desc: "MyPackage support"

# 隐式导入
implicit_imports:
  - depends:
      - "mypackage._config"
      - "mypackage._c_impl"
        # 这些模块被mypackage隐式导入

# 额外DLL
dlls:
  - pattern: "bin/*.dll"
    relative_path: "mypackage/bin"
    reason: "native libraries"

# 数据文件
data_files:
  - pattern: "resources/**/*"
    dirs: true
    reason: "UI resources"

# 反膨胀
anti_bloat:
  - pattern: "**/debug.py"
    replacement: "pass"
    description: "remove debug module"
  - pattern: "**/testing.py"
    replacement: "pass"

# DLL依赖黑名单
no_dlls:
  - "unnecessary_debug.dll"
```

### YAML插件类型

| 类型 | 配置键 | 说明 |
|------|--------|------|
| 隐式导入 | `implicit_imports` | 声明隐式导入模块 |
| DLL文件 | `dlls` | 声明额外DLL依赖 |
| 数据文件 | `data_files` | 声明数据文件 |
| 反膨胀 | `anti_bloat` | 替换/移除臃肿代码 |
| 预处理 | `preprocess_code` | 源码预处理规则 |

## 34个标准插件概览

| 插件 | 功能 | 自动激活条件 |
|------|------|------------|
| `anti-bloat` | 移除测试/debug代码，替换臃肿导入 | 始终激活 |
| `data-files` | 通用数据文件收集 | 始终激活 |
| `implicit-imports` | 通用隐式导入声明 | 始终激活 |
| `dll-files` | 通用DLL文件声明 | 始终激活 |
| `numpy` | NumPy科学计算库适配（BLAS DLL、隐式导入） | numpy安装时 |
| `torch` | PyTorch深度学习框架适配（CUDA DLL、插件目录） | torch安装时 |
| `tensorflow` | TensorFlow适配 | tensorflow安装时 |
| `scipy` | SciPy科学计算库适配 | scipy安装时 |
| `pandas` | Pandas数据分析库适配 | pandas安装时 |
| `matplotlib` | Matplotlib绘图库适配（后端选择、数据文件） | matplotlib安装时 |
| `tk-inter` | Tkinter GUI适配（Tcl/Tk DLL、init.tcl） | tkinter使用时 |
| `qt-plugins` | Qt5/Qt6通用插件适配 | PyQt/PySide安装时 |
| `pyqt5` | PyQt5特定适配（sip、QML插件） | PyQt5安装时 |
| `pyqt6` | PyQt6特定适配 | PyQt6安装时 |
| `pyside2` | PySide2特定适配 | PySide2安装时 |
| `pyside6` | PySide6特定适配 | PySide6安装时 |
| `pygobject` | GTK/GObject Introspection适配 | gi安装时 |
| `wxpython` | wxPython GUI适配 | wx安装时 |
| `kivy` | Kivy GUI框架适配 | kivy安装时 |
| `gevent` | Gevent协程适配（monkey patch处理） | gevent安装时 |
| `trio` | Trio异步库适配 | trio安装时 |
| `eventlet` | Eventlet协程适配 | eventlet安装时 |
| `multiprocessing` | multiprocessing适配（spawn/fork处理） | multiprocessing使用时 |
| `opengl` | PyOpenGL适配（DLL依赖） | OpenGL使用时 |
| `transformers` | HuggingFace Transformers适配 | transformers安装时 |
| `lxml` | lxml XML库适配 | lxml安装时 |
| `pygame` | Pygame游戏库适配 | pygame安装时 |
| `pywebview` | pywebview GUI适配 | webview安装时 |
| `delvewheel` | delvewheel DLL修复 | Windows + DLL检测 |
| `upx` | UPX压缩EXE/DLL | --upx选项 |
| `pkg-resources` | pkg_resources运行时适配 | pkg_resources使用时 |
| `importlib-metadata` | importlib.metadata适配 | 使用时 |
| `setuptools` | setuptools运行时适配 | setuptools使用时 |
| `gi` | PyGObject Introspection特定适配 | gi安装时 |

## 编写自定义插件

### 最小插件示例

```python
from nuitka.plugins.PluginBase import NuitkaPluginBase

class MyPlugin(NuitkaPluginBase):
    plugin_name = "my-plugin"
    plugin_desc = "我的自定义Nuitka插件"

    @classmethod
    def isAlwaysEnabled(cls):
        return False  # 用户需要--enable-plugin=my-plugin

    def getImplicitImports(self, module):
        if module.getFullName() == "mypackage":
            # mypackage在导入时会隐式加载mypackage._native
            yield "mypackage._native", True  # True表示必需
            yield "mypackage.config", False  # False表示可选

    def considerDataFiles(self, module):
        if module.getFullName().startswith("mypackage"):
            yield self.locateDataFile(module, "data/config.json")

    def getExtraDlls(self, module):
        if module.getFullName() == "mypackage._native":
            yield self.locateDLL("mynative.dll", package="mypackage")
```

### 插件选项

插件可以定义自己的命令行选项：

```python
class MyPlugin(NuitkaPluginBase):
    # ...
    @classmethod
    def addPluginCommandLineOptions(cls, group):
        group.add_option(
            "--myplugin-mode",
            action="store",
            dest="mode",
            default="auto",
            help="MyPlugin mode: auto/full/minimal",
        )
```

用户通过`--enable-plugin=myplugin --myplugin-mode=full`使用。

### 插件注册

将插件Python文件放入以下目录之一，Nuitka会自动发现：
1. `nuitka/plugins/standard/`（内置标准插件）
2. `nuitka/plugins/user/`（用户插件目录）
3. 由`--user-plugin=path/to/plugin.py`指定的路径
4. 通过entry point `nuitka.plugins`注册的包
