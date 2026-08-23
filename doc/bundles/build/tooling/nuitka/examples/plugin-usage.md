---
okf_version: "0.2"
type: Example
title: "使用与创建插件"
description: "如何使用Nuitka标准插件适配第三方库，以及如何编写自定义插件"
tags: ["nuitka", "plugin", "custom-plugin", "yaml-plugin", "extension"]
difficulty: advanced
time_to_complete: "15分钟"
prerequisites:
  - "standalone-build.md"
  - "../concepts/11-plugin-system.md"
related_concepts:
  - "../concepts/06-module-import-system.md"
  - "../concepts/10-freezer-distribution.md"
related_references:
  - "../references/plugin-base-api.md"
verified: true
status: active
---

# 示例：使用与创建插件

Nuitka插件系统让你能够适配第三方库的特殊需求（隐式导入、DLL依赖、数据文件），也可以编写自定义插件来修改编译行为。

## 第一部分：使用标准插件

### 查看可用插件

```bash
nuitka --plugin-list
```

输出所有34个标准插件及其描述。

### 常用插件使用

#### 1. NumPy插件

```bash
pip install numpy
nuitka --standalone --enable-plugin=numpy numpy_app.py
```

NumPy插件自动处理：
- OpenBLAS/MKL等DLL依赖
- .pyx C扩展文件
- 隐式导入的子模块
- 随机数生成器状态

#### 2. Tkinter插件

```bash
nuitka --standalone --enable-plugin=tk-inter --windows-disable-console tk_app.py
```

Tkinter插件自动包含：
- Tcl/Tk运行时DLL
- init.tcl等初始化脚本
- Tk主题文件
- 编码文件

#### 3. PyQt6插件

```bash
pip install PyQt6
nuitka --standalone \
       --enable-plugin=pyqt6 \
       --include-qt-plugins=sensible,multimedia,platforms \
       --windows-disable-console \
       qt_app.py
```

Qt插件自动处理：
- Qt平台插件（qwindows.dll等）
- Qt模块DLL（Qt6Core、Qt6Gui等）
- QML导入路径
- 翻译文件
- 图像格式插件

`--include-qt-plugins`选项：
- `sensible`：常用插件（平台、样式、图像格式）
- `all`：所有Qt插件
- 逗号分隔的具体插件名

#### 4. Anti-bloat插件（默认启用）

Anti-bloat插件自动移除臃肿代码，无需手动启用。它会：
- 移除测试模块
- 移除debug日志调用
- 替换重量级导入为轻量stub
- 移除`if TYPE_CHECKING:`块

可以通过选项控制：
```bash
# 不进行anti-bloat处理
nuitka --standalone --disable-plugin=anti-bloat app.py
```

#### 5. 多插件组合

```bash
nuitka --standalone \
       --enable-plugin=numpy,matplotlib,tk-inter \
       --include-data-dir=data=data \
       --windows-disable-console \
       scientific_app.py
```

多个插件用逗号分隔。

### 自动检测插件

Nuitka通过detector插件自动检测已安装的库并激活对应插件：

```bash
# 如果安装了PyQt6，pyqt6插件自动激活，无需--enable-plugin
nuitka --standalone qt_app.py

# 禁用自动检测
nuitka --standalone --plugin-no-detection qt_app.py
```

## 第二部分：YAML声明式插件

最简单的自定义插件是YAML配置插件，不需要写Python代码。

### 创建YAML插件

创建插件目录结构：

```
my_nuitka_plugins/
└── mypackage-plugin/
    ├── __init__.py    # 空文件，使Python识别为包
    └── MyPackagePlugin.py
```

创建 `MyPackagePlugin.py`：

```python
# my_nuitka_plugins/mypackage-plugin/MyPackagePlugin.py
from nuitka.plugins.NuitkaYamlPluginBase import NuitkaYamlPluginBase

class MyPackagePlugin(NuitkaYamlPluginBase):
    plugin_name = "mypackage"
    plugin_desc = "Support for MyPackage library"
    
    @classmethod
    def isAlwaysEnabled(cls):
        return False  # 需要用户手动启用
    
    def getYamlPath(self):
        # 返回YAML配置文件路径
        return os.path.join(os.path.dirname(__file__), "mypackage.yaml")
```

创建YAML配置 `mypackage.yaml`：

```yaml
# mypackage 隐式导入和数据文件配置
module_name: "mypackage"

# 隐式导入：mypackage在导入时自动加载这些子模块
implicit_imports:
  - depends:
      - "mypackage._config"    # 必需的隐式导入
      - "mypackage._native"    # C扩展模块
      - name: "mypackage.optional"
        required: false        # 可选导入，不存在不报错

# 数据文件
data_files:
  - pattern: "data/*.json"     # 包含data目录下所有.json
    dirs: false
    reason: "configuration files"
  - pattern: "resources/**/*"  # 包含resources目录及子目录
    dirs: true
    reason: "UI resources"

# 额外DLL
dlls:
  - pattern: "bin/*.dll"
    relative_path: "mypackage/bin"
    reason: "native libraries"

# 反膨胀：移除不需要的代码
anti_bloat:
  - pattern: "**/debug.py"
    replacement: "pass"
    description: "remove debug utilities"
  - pattern: "**/testing.py"
    replacement: ""
    description: "remove test utilities"
```

使用：

```bash
nuitka --standalone \
       --user-plugin=my_nuitka_plugins/mypackage-plugin \
       --enable-plugin=mypackage \
       app.py
```

## 第三部分：Python代码插件

对于更复杂的需求，可以编写Python代码插件。

### 最小自定义插件

创建 `my_plugin.py`：

```python
# my_plugin.py
from nuitka.plugins.PluginBase import NuitkaPluginBase

class MyFirstPlugin(NuitkaPluginBase):
    """我的第一个Nuitka插件"""
    
    plugin_name = "my-first-plugin"
    plugin_desc = "A simple custom Nuitka plugin"

    @classmethod
    def isAlwaysEnabled(cls):
        """返回True则始终激活，不需要--enable-plugin"""
        return False

    def onInitialization(self):
        """插件初始化时调用"""
        self.info("MyFirstPlugin initialized!")

    def getImplicitImports(self, module):
        """为特定模块提供隐式导入列表"""
        if module.getFullName() == "mypackage":
            # mypackage在运行时动态导入mypackage._backend
            yield "mypackage._backend", True  # (模块名, 是否必需)
            self.info("Adding implicit import: mypackage._backend")

    def considerDataFiles(self, module):
        """为特定模块提供数据文件"""
        if module.getFullName().startswith("mypackage"):
            # 获取包目录
            package_dir = os.path.dirname(module.getCompileTimeFilename())
            data_dir = os.path.join(package_dir, "data")
            
            if os.path.isdir(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.endswith(".json"):
                        src = os.path.join(data_dir, filename)
                        dest = os.path.join("mypackage", "data", filename)
                        yield self.makeIncludedDataFile(
                            source_path=src,
                            dest_path=dest,
                            reason="mypackage data file",
                        )

    def getExtraDlls(self, module):
        """为特定模块提供额外DLL"""
        if module.getFullName() == "mypackage._native":
            package_dir = os.path.dirname(module.getCompileTimeFilename())
            dll_path = os.path.join(package_dir, "native.dll")
            if os.path.exists(dll_path):
                yield self.locateDLL(
                    dll_filename=dll_path,
                    package_name="mypackage",
                )

    def onModuleSourceCode(self, module_name, source_code):
        """修改模块源码（源码级patch）"""
        if module_name == "mypackage.compat":
            # 替换不兼容的代码
            source_code = source_code.replace(
                "sys.version_info[0] == 2",
                "sys.version_info[0] == 3"
            )
            self.info(f"Patched source code for {module_name}")
        return source_code

    def onFinalResult(self, binary_filename):
        """编译完成后的回调"""
        self.info(f"Compilation finished: {binary_filename}")
        # 可以在这里进行后处理（签名、上传等）
```

使用：

```bash
nuitka --standalone \
       --user-plugin=my_plugin.py \
       --enable-plugin=my-first-plugin \
       app.py
```

### 带选项的插件

```python
class MyConfigurablePlugin(NuitkaPluginBase):
    plugin_name = "my-configurable-plugin"
    plugin_desc = "A plugin with options"

    @classmethod
    def addPluginCommandLineOptions(cls, group):
        group.add_option(
            "--myplugin-mode",
            action="store",
            dest="mode",
            default="auto",
            choices=["auto", "full", "minimal"],
            help="MyPlugin operation mode: auto/full/minimal",
        )
        group.add_option(
            "--myplugin-extra-data",
            action="append",
            dest="extra_data",
            default=[],
            help="Additional data directories to include",
        )

    def onInitialization(self):
        mode = self.getPluginOptionString("mode", "auto")
        self.info(f"Running in {mode} mode")
        
        for data_dir in self.getPluginOptionList("extra_data", []):
            self.info(f"Will include extra data: {data_dir}")
```

使用：

```bash
nuitka --standalone \
       --user-plugin=my_plugin.py \
       --enable-plugin=my-configurable-plugin \
       --myplugin-mode=full \
       --myplugin-extra-data=./extra_data \
       app.py
```

### 控制模块编译模式

```python
class CompileControlPlugin(NuitkaPluginBase):
    plugin_name = "compile-control"
    plugin_desc = "Control which modules get compiled"

    @classmethod
    def isAlwaysEnabled(cls):
        return True

    def decideCompilation(self, module, module_name):
        """决定模块编译模式"""
        # 纯配置模块使用字节码模式（不编译C）
        if module_name.endswith(".config") or module_name.endswith(".constants"):
            self.info(f"Forcing bytecode mode for: {module_name}")
            return "bytecode"
        
        # 核心模块强制编译
        if module_name.startswith("mypackage.core"):
            return "compiled"
        
        return None  # 默认决策

    def onModuleEncountered(self, module_name, module_filename):
        """决定是否跟随导入"""
        # 不跟随测试模块
        if "test" in module_name.split(".") or "tests" in module_name.split("."):
            self.info(f"Not following import to: {module_name}")
            return False
        return None  # 默认决策
```

### Fake模块插件

```python
class StubPlugin(NuitkaPluginBase):
    """为不存在的模块提供stub实现"""
    
    plugin_name = "stub-provider"
    
    def createPreLoadedModule(self, module_name):
        if module_name == "optional_dependency":
            return (
                "optional_dependency",
                "def optional_function():\n"
                "    '''Stub implementation when optional_dependency is not installed'''\n"
                "    return None\n",
                False,  # is_package
                False,  # is_top_level
            )
        return None
```

## 第四部分：插件调试

### 查看插件决策

```bash
# 解释导入决策
nuitka --standalone --explain-imports app.py

# 列出所有包含的模块
nuitka --standalone --verbose app.py 2>&1 | grep "included"

# 显示插件加载信息
nuitka --standalone --verbose app.py 2>&1 | grep "plugin"
```

### 常见插件问题

1. **插件不生效**：
   - 检查`--plugin-list`中是否列出
   - 确认`isAlwaysEnabled()`返回True或已用`--enable-plugin`启用
   - 检查插件文件路径是否正确

2. **隐式导入仍报ModuleNotFoundError**：
   - 使用`--explain-imports`查看是否被`onModuleEncountered`排除
   - 确认`getImplicitImports()`yield的模块名正确
   - 可能需要同时在`onModuleEncountered`中返回True

3. **数据文件找不到**：
   - 检查dest_path是否相对于dist根目录
   - 使用`--verbose`查看"included data file"日志
   - 确认文件路径在运行时通过正确方式访问

## 第五部分：插件最佳实践

1. **使用YAML插件优先**：能用YAML声明的就不写Python代码
2. **isAlwaysEnabled()谨慎使用**：只有确实适用于所有编译的插件才始终启用
3. **detector插件分离**：将库检测逻辑与实际插件分离
4. **充分日志**：使用`self.info()`/`self.warning()`输出决策信息
5. **条件处理**：检查模块名用`startswith()`匹配包前缀
6. **反膨胀要保守**：只替换确定不需要的代码
7. **测试多平台**：DLL路径在Windows/Linux/macOS不同
