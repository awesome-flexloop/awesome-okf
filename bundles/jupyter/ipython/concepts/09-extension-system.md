---
type: concept
title: "09 - 扩展系统"
description: IPython ExtensionManager 扩展加载/卸载机制、扩展入口点协议、内置扩展（autoreload/storemagic）、安全考虑
tags: [extensions, extension-manager, load-extension, autoreload, storemagic, plugin]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-extensions
    title: IPython/core/extensions.py
  - id: ipython-ext-autoreload
    title: IPython/extensions/autoreload.py
---

## ExtensionManager 扩展管理器

`ExtensionManager` 负责 IPython 扩展的加载、卸载和重载 [F-430]。扩展是一种 Python 模块，在加载时可以注册魔法、事件回调、钩子、formatter 等任意定制，是 IPython 最强大的扩展机制。

```python
class ExtensionManager(Configurable):
    """管理 IPython 扩展的加载/卸载 [F-430]"""
    
    loaded: set[str]  # 已加载的扩展模块名集合
```

### 核心方法

| 方法 | 说明 | 事实 |
|------|------|------|
| `load_extension(module_name)` | 加载扩展，调用 `load_ipython_extension(ipython)` | [F-431] |
| `unload_extension(module_name)` | 卸载扩展，调用 `unload_ipython_extension(ipython)` | [F-432] |
| `reload_extension(module_name)` | 重新加载扩展（先卸载再加载） | [F-433] |

### 加载流程

```
%load_ext my_extension
  │
  ▼
ExtensionManager.load_extension("my_extension")
  │
  ├── 1. import my_extension（如果尚未导入）
  ├── 2. 检查是否有 load_ipython_extension 函数
  ├── 3. 调用 my_extension.load_ipython_extension(ip)  [F-434]
  │     └── 扩展在此函数中注册魔法、事件、钩子等
  └── 4. 将 "my_extension" 加入 loaded 集合
```

卸载流程：
```
%unload_ext my_extension
  │
  ▼
ExtensionManager.unload_extension("my_extension")
  │
  ├── 1. 检查是否已加载
  ├── 2. 如果模块有 unload_ipython_extension 函数，调用之 [F-435]
  │     └── 扩展在此函数中清理注册的魔法、事件等
  └── 3. 将 "my_extension" 从 loaded 集合移除
```

## 扩展入口点协议

IPython 扩展是一个普通的 Python 模块（或包），只要实现特定的入口函数即可：

### load_ipython_extension（必需）

```python
def load_ipython_extension(ipython):
    """加载扩展时调用 [F-434]
    
    Parameters
    ----------
    ipython : InteractiveShell
        当前 IPython Shell 实例，可以通过它注册魔法、事件、钩子等
    """
    # 在这里注册自定义魔法
    ipython.register_magics(MyMagics)
    
    # 注册事件回调
    ipython.events.register('post_run_cell', my_callback)
    
    # 设置钩子
    ipython.set_hook('editor', my_editor_hook)
    
    # 注册 formatter
    ipython.display_formatter.formatters['text/html'].for_type(MyClass, my_to_html)
    
    # 修改 shell 属性
    # ...
```

### unload_ipython_extension（可选但推荐）

```python
def unload_ipython_extension(ipython):
    """卸载扩展时调用 [F-435]
    
    清理 load_ipython_extension 中注册的资源。
    如果不提供此函数，IPython 不会报错，但会有资源泄漏警告。
    """
    # 注销事件回调
    ipython.events.unregister('post_run_cell', my_callback)
    
    # 注意：注销魔法比较复杂，需要手动从 magics_manager 中移除
    # 注销 formatter
    # ...
```

## 魔法命令

扩展管理通过三个魔法命令暴露给用户 [F-341]：

| 魔法 | 说明 |
|------|------|
| `%load_ext <module>` | 加载指定扩展 |
| `%unload_ext <module>` | 卸载指定扩展 |
| `%reload_ext <module>` | 重新加载（先卸载再加载） |

```python
# 加载 autoreload 扩展
%load_ext autoreload
%autoreload 2  # 加载后可以使用其魔法

# 卸载扩展
%unload_ext autoreload

# 重新加载（开发扩展时很有用）
%reload_ext my_extension
```

## 内置扩展

IPython 自带几个官方扩展 [F-520][F-521][F-522]：

### autoreload —— 自动重载模块

`autoreload` 扩展自动重新加载已导入但在磁盘上被修改的模块 [F-520]，开发过程中非常有用：

```python
%load_ext autoreload

# 模式 1：重载所有导入的模块（除了 %aimport 排除的）
%autoreload 1

# 模式 2：重载所有模块（默认排除的模块除外）
%autoreload 2

# 模式 0：禁用自动重载
%autoreload 0

# 指定要自动重载的模块
%aimport mymodule
# 排除不重载的模块
%aimport -mymodule

# 查看自动重载状态
%aimport
```

autoreload 通过在执行前检查模块文件的修改时间，自动调用 `importlib.reload()` 重载变化的模块。对于频繁修改的开发模块，这避免了手动重启 IPython。

### storemagic —— 变量持久化

`storemagic` 扩展提供 `%store` 魔法，允许在 IPython 会话间持久化变量 [F-521]：

```python
%load_ext storemagic

# 保存变量到磁盘
data = {"key": "value", "numbers": [1, 2, 3]}
%store data

# 查看所有已存储的变量
%store

# 恢复变量
%store -r data

# 删除存储的变量
%store -d data

# 恢复所有变量
%store -z  # 先清空当前命名空间
%store -r  # 恢复所有
```

变量通过 pickle 序列化到 IPython profile 目录下的数据库中。

### deduperreload —— 去重重载

`deduperreload/` 是一个扩展包，提供改进的模块重载机制，避免重复重载相同模块 [F-522]。

## 编写 IPython 扩展

### 最小扩展示例

```python
# my_extension.py
"""一个简单的 IPython 扩展示例"""

from IPython.core.magic import Magics, magics_class, line_magic, cell_magic

@magics_class
class MyExtensionMagics(Magics):
    """扩展提供的自定义魔法"""
    
    @line_magic
    def hello(self, line):
        """问候魔法"""
        name = line.strip() or "World"
        print(f"Hello, {name}!")
    
    @cell_magic
    def count_lines(self, line, cell):
        """统计代码行数"""
        lines = [l for l in cell.split('\n') if l.strip() and not l.strip().startswith('#')]
        print(f"非空非注释行数: {len(lines)}")

def load_ipython_extension(ipython):
    """加载扩展"""
    ipython.register_magics(MyExtensionMagics)
    print("my_extension loaded! Use %hello or %%count_lines")

def unload_ipython_extension(ipython):
    """卸载扩展"""
    print("my_extension unloaded!")
```

使用扩展：

```python
%load_ext my_extension
%hello IPython      # → "Hello, IPython!"
%%count_lines
# 这是注释
def foo():
    return 42
# 非空非注释行数: 2
```

### 通过配置自动加载扩展

在 `ipython_config.py` 中配置自动加载的扩展：

```python
# ~/.ipython/profile_default/ipython_config.py
c = get_config()
c.InteractiveShellApp.extensions = [
    'autoreload',
    'my_extension',
]
# 启动时自动执行 autoreload 2
c.InteractiveShellApp.exec_lines = ['%autoreload 2']
```

### 通过 startup 文件加载

将扩展加载脚本放在 profile 的 `startup/` 目录下：

```python
# ~/.ipython/profile_default/startup/00-my-setup.py
from IPython import get_ipython
ip = get_ipython()
ip.extension_manager.load_extension('autoreload')
```

## 安全考虑

扩展加载执行的是**任意 Python 代码**——`load_ipython_extension(ipython)` 函数可以做任何事情：

- 修改 `sys.path`、`sys.modules`
- 读写文件系统
- 发起网络请求
- 修改 shell 的任何内部状态
- 执行系统命令

因此 [F-341 洞察]：
- **只加载你信任来源的扩展**
- `%load_ext` 等价于 `import 模块` 并执行其 `load_ipython_extension()` 函数
- 配置文件中 `extensions` 列表和 startup 目录下的脚本也有同样风险
- 与 `pip install` 安装第三方包一样，扩展的安全边界等同于你对其来源的信任

## IPython 扩展 vs Jupyter 扩展

IPython 扩展和 Jupyter 扩展是不同的概念：

| 特性 | IPython 扩展 | Jupyter 扩展 |
|------|-------------|-------------|
| **作用范围** | IPython 内核（Python 进程内） | Jupyter Lab/Notebook 前端 |
| **入口点** | `load_ipython_extension(ipython)` | `_jupyter_nbextension_paths()` 或 npm 包 |
| **语言** | Python | JavaScript/TypeScript |
| **加载方式** | `%load_ext` 或配置 | `jupyter labextension install` |
| **能力** | 注册魔法/事件/钩子/formatter | 添加 UI 组件/工具栏/菜单项 |
| **运行位置** | Kernel 进程 | 浏览器前端 |

两者可以配合使用：一个包可以同时提供 IPython 扩展（内核端功能）和 Jupyter 扩展（前端 UI），如 ipywidgets 同时提供内核端的 Widget 模型和前端的 Widget 渲染。

## 通过 LazyMagic 延迟加载扩展

扩展也可以通过 `MagicsManager.register_lazy()` 延迟注册，避免在启动时导入开销大的模块：

```python
# 在配置中声明延迟魔法
c.MagicsManager.lazy_magics = {
    "my_heavy_magic": "my_package.heavy_module:HeavyMagics",
    "another_ext": "my_package.another_ext",
}
```

`"module:Class"` 形式直接导入并实例化 Magics 类，不经过扩展机制；`"module"` 形式作为扩展加载，调用 `load_ipython_extension()` [F-302 源码]。

## 相关概念

- [事件与钩子](/concepts/10-events-hooks.md)
- [魔法命令系统](/concepts/04-magic-system.md)
- [自定义魔法开发](/concepts/11-custom-magics.md)
- [信源参考 - 扩展系统](/references/extension-source.md)
