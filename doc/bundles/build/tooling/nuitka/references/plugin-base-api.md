---
okf_version: "0.2"
type: Reference
title: "Nuitka 插件基类 API"
description: "nuitka/plugins/——NuitkaPluginBase核心钩子方法、插件分类和YAML声明式插件"
tags: ["nuitka", "plugin", "hook", "extension", "yaml"]
sources:
  - id: REF-PLUGIN-001
    path: "nuitka/plugins/PluginBase.py"
    description: "插件基类定义（约60个钩子方法）"
  - id: REF-PLUGIN-002
    path: "nuitka/plugins/Plugins.py"
    description: "插件管理器（Plugins单例）"
  - id: REF-PLUGIN-003
    path: "nuitka/plugins/standard/"
    description: "34个标准插件目录"
  - id: REF-PLUGIN-004
    path: "nuitka/plugins/NuitkaYamlPluginBase.py"
    description: "YAML配置驱动插件基类"
  - id: REF-PLUGIN-005
    path: "nuitka/plugins/PluginsMeta.py"
    description: "插件元类自动注册"
verified: true
status: active
---

# Nuitka 插件基类 API 参考

> 源码路径：nuitka/plugins/

## Plugins 管理器（单例）

`Plugins`类是全局单例，管理所有已激活插件实例：

| 属性/方法 | 说明 |
|----------|------|
| `Plugins.active_plugins` | OrderedDict，按激活顺序存储所有插件实例 |
| `Plugins.plugins_by_name` | dict，按插件名称索引 |
| `Plugins.always_enabled_plugins` | list，始终激活的插件（`isAlwaysEnabled()`返回True） |
| `Plugins.detector_plugins` | list，仅用于检测系统环境的detector插件 |
| `Plugins.init(plugins_dir)` | 初始化插件系统，加载所有插件类 |
| `Plugins.activatePluginByName(name, options)` | 按名称激活插件 |
| `Plugins.deactivatePluginByName(name)` | 按名称停用插件 |

插件按回调能力分为7个分类列表，优化遍历效率：
1. `before_parsing`：解析前钩子
2. `module_discovery`：模块发现钩子
3. `module_encounter`：模块遇到钩子
4. `on_module_source_code`：源码处理钩子
5. `extra_dlls`：额外DLL收集
6. `data_files`：数据文件收集
7. `final_result`：最终结果钩子

---

## NuitkaPluginBase 核心钩子

### 生命周期钩子

| 钩子方法 | 调用时机 | 返回值 |
|---------|---------|--------|
| `onInitialization()` | 插件激活后，编译开始前 | None |
| `onFinalization()` | 编译全部完成后 | None |
| `beforeParsing(source_dir)` | AST解析开始前 | None |
| `onFinalResult(binary_filename)` | 编译产出最终文件后 | None |

### 模块处理钩子

| 钩子方法 | 调用时机 | 返回值 |
|---------|---------|--------|
| `onModuleDiscovered(module)` | 发现新模块时（构建树前） | None |
| `onModuleEncountered(module, module_name)` | 遇到模块导入时，决定是否跟随 | True/False/None |
| `decideCompilation(module, module_name)` | 决定模块编译模式 | "compiled"/"bytecode"/None |
| `getImplicitImports(module)` | 获取模块的隐式导入 | list[(module_name, required)] |
| `onModuleSourceCode(module_name, source_code)` | 模块源码读取后（可修改源码） | 修改后的源码 |
| `onFrozenModuleSourceCode(module_name, is_package, source_code)` | 冻结模块源码读取后 | 修改后的源码 |
| `onModuleComplete(module)` | 模块编译完全完成后 | None |

### 打包分发钩子

| 钩子方法 | 调用时机 | 返回值 |
|---------|---------|--------|
| `getExtraDlls(module)` | Standalone模式收集额外DLL | yield IncludedDLL |
| `considerDataFiles(module)` | 考虑数据文件打包 | yield IncludedDataFile |
| `getExtraFiles()` | 收集不依赖于特定模块的额外文件 | yield IncludedDataFile |
| `removeDllDependencies(dll_filename, dll_basename)` | 移除DLL依赖（反膨胀） | bool |

### 代码生成钩子

| 钩子方法 | 调用时机 | 返回值 |
|---------|---------|--------|
| `onGeneratedSourceCode(module, filename)` | C代码生成写入文件后 | None |
| `getPreprocessorSymbols()` | SCons编译前，提供C预处理器宏 | list[(name, value)] |
| `getExtraBuildFiles()` | 获取额外的构建文件 | list[path] |

### 选项与配置钩子

| 钩子方法 | 说明 |
|---------|------|
| `isAlwaysEnabled()` | 返回True则始终激活（不需要用户--enable-plugin） |
| `isDetector()` | 返回True则是detector插件（不计入激活计数） |
| `detector_for` | detector插件指向的实际插件名称 |
| `getPluginOptionBool(name, default)` | 获取布尔型插件选项 |
| `getPluginOptionChoice(name, choices, default)` | 获取选项型插件选项 |
| `getPluginOptionList(name, default)` | 获取列表型插件选项 |
| `getPluginOptionInteger(name, default)` | 获取整数型插件选项 |
| `warnUnsupportedPython()` | 检测到不支持的Python版本时警告 |
| `info(message)` / `warning(message)` | 输出插件日志 |

### YAML配置驱动

`NuitkaYamlPluginBase`通过YAML配置声明插件行为，无需编写Python代码：

```yaml
# 示例：一个YAML插件配置
module_name: "mypackage"
implicit_imports:
  - name: "mypackage._impl"
    required: true
data_files:
  - pattern: "data/*.json"
    dirs: false
extra_dlls:
  - pattern: "lib/*.dll"
anti_bloat:
  - pattern: "**/unused_debug.py"
    replacement: "pass"
```

内置YAML插件类型：
- **AntiBloat**：移除臃肿依赖（如删除测试代码、debug日志）
- **DataFileCollector**：自动收集包数据文件
- **ImplicitImports**：声明隐式导入
- **DLLFiles**：声明额外DLL依赖
- **NumpyPlugin**/PandasPlugin等：特定库适配

---

## 标准插件清单（34个）

| 插件名 | 功能 | 自动激活 |
|--------|------|---------|
| `anti-bloat` | 移除臃肿代码（测试、debug等） | 是 |
| `data-files` | 通用数据文件收集 | 是 |
| `implicit-imports` | 通用隐式导入声明 | 是 |
| `dll-files` | 通用DLL文件声明 | 是 |
| `numpy` | NumPy库适配 | NumPy安装时 |
| `torch` | PyTorch库适配 | PyTorch安装时 |
| `tensorflow` | TensorFlow库适配 | TF安装时 |
| `scipy` | SciPy库适配 | SciPy安装时 |
| `pandas` | Pandas库适配 | Pandas安装时 |
| `matplotlib` | Matplotlib库适配 | Matplotlib安装时 |
| `tk-inter` | Tkinter GUI适配 | tkinter使用时 |
| `qt-plugins` | Qt5/Qt6绑定适配 | PyQt/PySide安装时 |
| `pyqt5` / `pyqt6` | PyQt5/6特定适配 | PyQt安装时 |
| `pyside2` / `pyside6` | PySide2/6特定适配 | PySide安装时 |
| `pygobject` | GTK/GObject适配 | gi安装时 |
| `wxpython` | wxPython GUI适配 | wx安装时 |
| `kivy` | Kivy GUI适配 | kivy安装时 |
| `gevent` | Gevent协程适配 | gevent安装时 |
| `trio` | Trio异步适配 | trio安装时 |
| `eventlet` | Eventlet适配 | eventlet安装时 |
| `multiprocessing` | multiprocessing适配 | multiprocessing使用时 |
| `pmw-freezer` | Python Mega Widgets适配 | Pmw安装时 |
| `opengl` | PyOpenGL适配 | OpenGL使用时 |
| `pyside6` | PySide6特定支持 | 是 |
| `pywebview` | pywebview GUI适配 | webview安装时 |
| `delvewheel` | delvewheel DLL修复 | Windows + DLL检测 |
| `upx` | UPX压缩支持 | --upx选项 |
| `gi` | PyGObject Introspection适配 | gi安装时 |
| `pygame` | Pygame适配 | pygame安装时 |
| `pkg-resources` | pkg_resources适配 | pkg_resources使用时 |
| `importlib-metadata` | importlib.metadata适配 | 使用时 |
| `setuptools` | setuptools运行时适配 | setuptools使用时 |
| `transformers` | HuggingFace Transformers适配 | transformers安装时 |
| `lxml` | lxml XML库适配 | lxml安装时 |

---

## 插件注册机制

插件类通过`@register_plugin`装饰器或元类自动注册：

```python
from nuitka.plugins.PluginBase import NuitkaPluginBase

class MyPlugin(NuitkaPluginBase):
    plugin_name = "my-plugin"
    plugin_desc = "我的自定义插件"

    @classmethod
    def isAlwaysEnabled(cls):
        return False

    def getImplicitImports(self, module):
        if module.getFullName() == "mypackage":
            yield ("mypackage._c_impl", True)
```

`PluginsMeta`元类在类定义时自动将插件注册到插件类列表。

---

## 相关概念

- [插件系统](../concepts/11-plugin-system.md)
- [编译流水线](../concepts/01-compilation-pipeline.md)
- [模块导入系统](../concepts/06-module-import-system.md)
- [打包分发](../concepts/10-freezer-distribution.md)
