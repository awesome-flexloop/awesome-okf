---
type: Reference
title: Extension System API 参考
description: IPython 扩展系统完整 API 参考，包括 ExtensionManager 加载/卸载/重载机制、扩展模块入口点约定、内置扩展和魔法命令接口
tags: [api, extension, plugin, load_ext, magic, reference, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ipython-extensions
    resource: /references/extension-source.md
    title: IPython/core/extensions.py ExtensionManager
  - id: ipython-extension-magic
    resource: /references/extension-source.md
    title: IPython/core/magics/extension.py Extension Magics
---

# Extension System API 参考

IPython 扩展系统允许第三方模块通过标准入口点向 IPython 注入功能（魔法命令、别名、事件回调、自定义组件等）。核心类是 `ExtensionManager`，定义在 `IPython/core/extensions.py`。

---

## ExtensionManager

### 类定义

```python
class ExtensionManager(Configurable):
    """管理 IPython 扩展的加载、卸载和重载

    扩展是一个可 import 的 Python 模块，必须定义:
        load_ipython_extension(ipython) -> None   # 必需，加载入口
    可选定义:
        unload_ipython_extension(ipython) -> None  # 可选，清理入口
    """
```

### 构造函数

```python
def __init__(self, shell=None, **kwargs):
    """
    Parameters
    ----------
    shell : InteractiveShell — 关联的 Shell 实例
    """
    # 初始化 self.loaded = set() — 已加载扩展模块名集合
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `shell` | InteractiveShell | 关联的 IPython Shell 实例 |
| `loaded` | set[str] | 已加载的扩展模块名集合 |

### 内置扩展映射

```python
BUILTINS_EXTS = {
    "storemagic": False,    # 存储/恢复变量魔法
    "autoreload": False,    # 自动重载模块
}
```

内置扩展使用简写名加载（如 `%load_ext autoreload`），实际映射到 `IPython.extensions.autoreload` 和 `IPython.extensions.storemagic`。`False` 表示尚未加载，加载后置为 `True`。

---

### 核心方法

#### load_extension()

```python
def load_extension(self, module_str: str):
    """加载 IPython 扩展

    Parameters
    ----------
    module_str : str — 扩展模块名（可使用简写或完整模块路径）

    Returns
    -------
    str 或 None:
        "already loaded" — 扩展已加载
        "no load function" — 模块没有 load_ipython_extension 函数
        None — 加载成功

    Raises
    ------
    ModuleNotFoundError — 模块不存在（简写的内置扩展除外）
    """
```

**加载流程**：
1. 检查 `module_str` 是否在 `self.loaded` 中 → 若在则返回 "already loaded"
2. 进入 `shell.builtin_trap` 上下文（确保 builtin 命名空间正确）
3. 若模块不在 `sys.modules` 中 → `import_module(module_str)`
4. 获取已导入的模块对象
5. 调用 `_call_load_ipython_extension(mod)` → 调用 `mod.load_ipython_extension(shell)`
6. 成功则加入 `self.loaded`，失败返回 "no load function"

**内置扩展回退**：若简写模块名（如 `autoreload`）未找到，尝试从 `IPython.extensions.<name>` 加载。

#### unload_extension()

```python
def unload_extension(self, module_str: str):
    """卸载 IPython 扩展

    Parameters
    ----------
    module_str : str — 扩展模块名

    Returns
    -------
    str 或 None:
        "not loaded" — 扩展未加载
        "no unload function" — 模块没有 unload_ipython_extension 函数
        None — 卸载成功

    注意: 卸载仅调用 unload_ipython_extension，不会从 sys.modules 中移除模块
    """
```

**卸载流程**：
1. 处理内置扩展名映射
2. 检查是否在 `self.loaded` 中
3. 从 `sys.modules` 获取模块
4. 调用 `_call_unload_ipython_extension(mod)` → 调用 `mod.unload_ipython_extension(shell)`
5. 成功则从 `self.loaded` 中移除

#### reload_extension()

```python
def reload_extension(self, module_str: str):
    """重载 IPython 扩展

    若已加载: unload → importlib.reload → load
    若未加载: 直接 load
    """
```

#### 内部方法

```python
def _call_load_ipython_extension(self, mod):
    """调用 mod.load_ipython_extension(self.shell)，返回是否成功"""
    if hasattr(mod, 'load_ipython_extension'):
        mod.load_ipython_extension(self.shell)
        return True

def _call_unload_ipython_extension(self, mod):
    """调用 mod.unload_ipython_extension(self.shell)，返回是否成功"""
    if hasattr(mod, 'unload_ipython_extension'):
        mod.unload_ipython_extension(self.shell)
        return True
```

---

## 扩展模块编写约定

### 必需入口函数

```python
def load_ipython_extension(ipython):
    """扩展加载入口

    Parameters
    ----------
    ipython : InteractiveShell — 当前 IPython Shell 实例

    此函数中可执行:
    - 注册魔法命令（ipython.register_magics()）
    - 注册事件回调（ipython.events.register()）
    - 设置钩子（ipython.set_hook()）
    - 添加别名（ipython.alias_manager...）
    - 修改配置（ipython.config...）
    - 注入变量到用户命名空间
    """
```

### 可选清理函数

```python
def unload_ipython_extension(ipython):
    """扩展卸载入口（可选但推荐）

    Parameters
    ----------
    ipython : InteractiveShell — 当前 IPython Shell 实例

    此函数应清理 load_ipython_extension 中添加的资源:
    - 移除事件回调
    - 删除注入的变量
    - 恢复被修改的状态

    注意: 魔法命令目前无法完全注销
    """
```

### 扩展示例

```python
# my_extension.py
from IPython.core.magic import Magics, magics_class, line_magic

@magics_class
class MyMagics(Magics):
    @line_magic
    def hello(self, line):
        """Say hello"""
        print(f"Hello, {line}!")

def load_ipython_extension(ipython):
    ipython.register_magics(MyMagics)
    print("My extension loaded!")

def unload_ipython_extension(ipython):
    # 清理（如有需要）
    print("My extension unloaded!")
```

使用：
```python
%load_ext my_extension
%hello World  # Hello, World!
%unload_ext my_extension
```

---

## 内置扩展

### autoreload

```python
"""IPython.extensions.autoreload

自动重载已修改的模块，无需重启 IPython

魔法命令:
    %load_ext autoreload
    %autoreload 0       # 禁用
    %autoreload 1       # 仅重载 %aimport 导入的模块
    %autoreload 2       # 重载所有模块（排除 %aimport -x 的）
    %aimport module     # 添加到自动重载列表
    %aimport -module    # 从自动重载列表移除
"""
```

### storemagic

```python
"""IPython.extensions.storemagic

跨会话持久化变量

魔法命令:
    %load_ext storemagic
    %store var          # 存储变量
    %store -r var       # 恢复变量
    %store -d var       # 删除变量
    %store -z           # 删除所有变量
    %store -l           # 列出所有存储的变量
    %store -r           # 恢复所有变量（autorestore 触发）
"""
```

### deduperreload

```python
"""IPython.extensions.deduperreload

增强的模块重载，处理依赖重复加载问题
"""
```

---

## 扩展相关魔法命令

定义在 `IPython/core/magics/extension.py`，属于 `ExtensionMagics` 类。

### %load_ext

```python
@line_magic
def load_ext(self, module_str):
    """加载 IPython 扩展

    Usage:
        %load_ext module_name

    参数为空时抛出 UsageError。
    返回状态通过 print 提示:
    - "already loaded" → 提示使用 %reload_ext
    - "no load function" → 提示不是有效扩展
    """
```

### %unload_ext

```python
@line_magic
def unload_ext(self, module_str):
    """卸载 IPython 扩展

    Usage:
        %unload_ext module_name

    仅定义了 unload_ipython_extension 的扩展可被完全卸载。
    返回状态:
    - "no unload function" → 扩展无法卸载
    - "not loaded" → 扩展未加载
    """
```

### %reload_ext

```python
@line_magic
def reload_ext(self, module_str):
    """重载 IPython 扩展

    Usage:
        %reload_ext module_name

    已加载 → unload + importlib.reload + load
    未加载 → 直接 load
    """
```

---

## 在 InteractiveShell 中的初始化

```python
def init_extension_manager(self):
    """初始化扩展管理器（在 InteractiveShell.__init__ 中调用）"""
    self.extension_manager = ExtensionManager(shell=self)
```

Shell 实例提供的相关方法和属性：

| 成员 | 说明 |
|------|------|
| `extension_manager` | ExtensionManager 实例 |
| `register_magics(magics_class)` | 注册魔法类（扩展中常用） |
| `events.register/unregister/trigger` | 事件系统 |
| `set_hook()` | 设置钩子 |
| `user_ns` | 用户命名空间 dict |
| `push(variables_dict, interactive=False)` | 注入变量到用户命名空间 |
| `magic(magic_name)` | 以编程方式执行魔法命令 |
| `run_line_magic(name, arg)` | 执行行魔法 |
| `run_cell_magic(name, arg, body)` | 执行单元格魔法 |
| `system(cmd)` | 执行系统命令 |
| `getoutput(cmd)` | 执行系统命令并捕获输出 |

---

## 通过配置自动加载扩展

在 IPython 配置文件（`ipython_config.py`）中：

```python
c.InteractiveShellApp.extensions = [
    'autoreload',
    'my_extension',
]
```

配置的扩展在 Shell 初始化后、启动文件运行前加载。

---

## 扩展开发最佳实践

1. **始终提供 unload_ipython_extension**：注册的事件回调、注入的变量等应在卸载时清理
2. **使用 self.shell 而非 get_ipython()**：在 Magics 类中，通过 `self.shell` 访问 Shell 实例
3. **注册事件回调时保存引用**：unload 时需要引用以注销
4. **避免全局状态**：模块级全局变量在 reload 时可能产生问题
5. **错误处理**：load_ipython_extension 中未捕获的异常会中断加载过程

### 完整扩展示例

```python
"""示例扩展: 执行计时器"""
import time
from IPython.core.magic import Magics, magics_class, line_cell_magic

@magics_class
class TimerMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self._callbacks = []

    @line_cell_magic
    def timer(self, line='', cell=None):
        """%timer 或 %%timer — 计时执行"""
        code = cell if cell else line
        start = time.perf_counter()
        result = self.shell.run_cell(code)
        elapsed = time.perf_counter() - start
        print(f"Elapsed: {elapsed:.4f}s")
        for cb in self._callbacks:
            cb(elapsed)
        return result

    def on_timer(self, callback):
        """注册计时完成回调"""
        self._callbacks.append(callback)

def load_ipython_extension(ipython):
    magics = TimerMagics(ipython)
    ipython.register_magics(magics)
    ipython.user_ns['timer_magics'] = magics
    print("Timer extension loaded. Use %timer or %%timer.")

def unload_ipython_extension(ipython):
    ipython.user_ns.pop('timer_magics', None)
    print("Timer extension unloaded.")
```

---

## 相关概念

- **[魔法命令系统](magic-source.md)**：扩展中注册魔法命令的 API
- **[事件与钩子](events-hooks-source.md)**：扩展中使用事件回调和钩子
- **[InteractiveShell](interactiveshell-source.md)**：Shell 实例 API 参考
- **[应用层](app-source.md)**：配置 extensions 自动加载
- **扩展开发指南**：扩展开发完整指南
