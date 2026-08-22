---
okf_version: "0.2"
type: example
title: "自定义 JupyterApp 应用"
description: "通过完整可运行代码，学习如何继承 JupyterApp 创建自定义应用，添加 traitlets 配置项、使用 @run_sync 装饰异步 start 方法，并通过 launch_instance 启动。"
tags: [jupyter, core, example, JupyterApp, custom-app, async, traitlets]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: application-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/application.py"
    title: "jupyter_core/application.py"
  - id: utils-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/utils/__init__.py"
    title: "jupyter_core/utils/__init__.py"
---

# 自定义 JupyterApp 应用

本示例展示如何继承 `JupyterApp` 创建一个完整的自定义 Jupyter 应用，包括自定义配置项、命令行别名/标志、异步启动方法。

## 完整示例代码

```python
#!/usr/bin/env python
"""
myapp.py - 一个自定义 JupyterApp 示例应用

功能：
- 继承 JupyterApp 基类
- 添加自定义 traitlets 配置项
- 自定义命令行 aliases 和 flags
- 使用 @run_sync 装饰异步 start 方法
- 通过 launch_instance() 启动
"""

from __future__ import annotations

import asyncio
import logging

from traitlets import Integer, Unicode, Bool

from jupyter_core.application import JupyterApp, base_aliases, base_flags
from jupyter_core.utils import run_sync, ensure_dir_exists
from jupyter_core.paths import jupyter_data_dir


# =============================================================================
# 自定义应用类
# =============================================================================

class MyJupyterApp(JupyterApp):
    """一个示例 Jupyter 应用，展示如何扩展 JupyterApp。"""

    # --- 基本信息（子类必须覆盖） ---
    name = "myapp"
    description = "一个自定义 JupyterApp 示例应用，演示配置项和异步启动。"

    # --- 自定义配置项（traitlets） ---
    greeting = Unicode(
        "Hello",
        config=True,
        help="问候语",
    )

    target = Unicode(
        "Jupyter World",
        config=True,
        help="问候目标",
    )

    repeat = Integer(
        1,
        config=True,
        help="重复问候的次数",
    )

    async_mode = Bool(
        False,
        config=True,
        help="是否使用异步模式演示",
    )

    output_dir = Unicode(
        config=True,
        help="输出目录路径（默认为 jupyter_data_dir/myapp）",
    )

    def _output_dir_default(self) -> str:
        from pathlib import Path
        return str(Path(jupyter_data_dir()) / "myapp")

    # --- 扩展命令行 aliases ---
    # 从 base_aliases 复制并添加自定义别名
    aliases = dict(base_aliases)
    aliases.update({
        "greeting": "MyJupyterApp.greeting",
        "target": "MyJupyterApp.target",
        "repeat": "MyJupyterApp.repeat",
        "output-dir": "MyJupyterApp.output_dir",
    })

    # --- 扩展命令行 flags ---
    # 从 base_flags 复制并添加自定义标志
    flags = dict(base_flags)
    flags.update({
        "async": (
            {"MyJupyterApp": {"async_mode": True}},
            "启用异步模式演示",
        ),
        "q": (
            {"Application": {"log_level": logging.WARNING}},
            "静默模式（只显示警告和错误）",
        ),
    })

    def initialize(self, argv=None):
        """初始化应用，添加自定义初始化逻辑。"""
        super().initialize(argv)
        # 自定义初始化逻辑
        ensure_dir_exists(self.output_dir, mode=0o700)
        self.log.info("输出目录: %s", self.output_dir)

    @run_sync
    async def start(self):
        """启动应用（异步方法，通过 @run_sync 装饰器同步调用）。"""
        # 先调用父类 start() 处理 subcommand/generate_config 分发
        # 父类 start() 在分发时会抛出 NoStart，launch_instance 会捕获它
        try:
            super().start()
        except SystemExit:
            # 当 generate_config 等情况发生时，正常流程会通过 NoStart 控制
            # 但为了安全，这里也处理 SystemExit
            raise

        # --- 应用主逻辑 ---
        self.log.info("启动 %s...", self.name)

        if self.async_mode:
            await self._run_async_demo()
        else:
            self._run_sync_demo()

        self.log.info("完成！")

    def _run_sync_demo(self):
        """同步演示：打印问候语。"""
        self.log.info("运行同步模式")
        for i in range(self.repeat):
            print(f"  {self.greeting}, {self.target}! (第 {i + 1} 次)")

    async def _run_async_demo(self):
        """异步演示：模拟异步 I/O 操作。"""
        self.log.info("运行异步模式")
        for i in range(self.repeat):
            print(f"  {self.greeting}, {self.target}! (第 {i + 1} 次, 异步)")
            # 模拟异步操作（如网络请求、文件 I/O）
            await asyncio.sleep(0.05)

        # 写入一个输出文件演示
        from pathlib import Path
        output_file = Path(self.output_dir) / "output.txt"
        content = f"{self.greeting}, {self.target}!\n"
        from jupyter_core.paths import secure_write
        with secure_write(str(output_file)) as f:
            for _ in range(self.repeat):
                f.write(content)
        self.log.info("输出已写入: %s", output_file)


# =============================================================================
# 入口点
# =============================================================================

def main():
    """命令行入口。"""
    MyJupyterApp.launch_instance()


if __name__ == "__main__":
    main()
```

## 运行示例

将上面的代码保存为 `myapp.py`，然后通过以下方式运行：

```bash
# 基本运行
python myapp.py

# 自定义问候语和次数
python myapp.py --greeting "Hi" --target "Developer" --repeat 3

# 异步模式
python myapp.py --async --repeat 2

# 查看帮助（显示所有选项）
python myapp.py --help

# 生成默认配置文件
python myapp.py --generate-config

# 使用自定义配置文件
python myapp.py --config myapp_config.py

# 静默模式
python myapp.py -q

# 调试模式
python myapp.py --debug
```

## 关键要点解析

### 1. 类属性设置

```python
class MyJupyterApp(JupyterApp):
    name = "myapp"                          # 必须覆盖，用于配置文件名
    description = "..."                     # 显示在帮助信息中
    aliases = dict(base_aliases)            # 从 base_aliases 复制再扩展
    flags = dict(base_flags)                # 从 base_flags 复制再扩展
```

- `name` 决定默认配置文件名：`{name}_config.py`，即 `myapp_config.py`
- 直接赋值 `aliases = base_aliases` 会导致修改基类字典，必须用 `dict()` 复制
- `--log-level` 和 `--config` 已在 `base_aliases` 中定义，无需重复添加
- `--debug`、`--generate-config`、`-y` 已在 `base_flags` 中定义

### 2. Traitlets 配置项

```python
from traitlets import Integer, Unicode, Bool

greeting = Unicode("Hello", config=True, help="问候语")
repeat = Integer(1, config=True, help="重复次数")
```

- `config=True` 使得该配置项可以通过配置文件和命令行设置
- `help` 文本会显示在 `--help` 输出中
- 默认值通过赋值或 `_<trait_name>_default()` 方法设置（适用于需要动态计算的默认值）

### 3. @run_sync 装饰异步 start

```python
@run_sync
async def start(self):
    super().start()  # 处理 subcommand/generate_config
    # 异步业务逻辑
    await asyncio.sleep(0.1)
```

- `@run_sync` 装饰器要求被装饰的函数是协程函数（`async def`）
- 调用时自动检测是否有运行中的事件循环：
  - 无循环：直接在当前线程运行 `run_until_complete`
  - 有循环：通过后台 `_TaskRunner` 线程运行
- `super().start()` 必须调用以处理 `--generate-config`、子命令分发等逻辑

### 4. initialize 自定义初始化

```python
def initialize(self, argv=None):
    super().initialize(argv)
    # 自定义初始化...
    ensure_dir_exists(self.output_dir, mode=0o700)
```

- 先调用 `super().initialize(argv)` 完成命令行解析、配置加载
- 然后添加自己的初始化逻辑（如创建目录、建立连接等）

### 5. launch_instance 启动

```python
MyJupyterApp.launch_instance()
```

- 类方法，完成实例创建、初始化、启动的完整生命周期
- 内部自动调用 `ensure_event_loop()` 确保事件循环可用
- 捕获 `NoStart` 异常正常退出（用于 subcommand/generate-config 场景）

### 6. 打包为 CLI 命令

在 `pyproject.toml` 中添加入口点：

```toml
[project.scripts]
myapp = "myapp:main"
```

安装后即可通过 `myapp` 命令直接运行，`jupyter myapp` 也会通过 PATH 发现机制自动可用。

---

**下一步阅读：**
- [路径定制与环境变量](03-path-customization.md) — 通过环境变量控制应用路径
- [应用基类 JupyterApp](../concepts/05-application-base.md) — 深入理解 JupyterApp API
- [异步支持机制](../concepts/06-async-support.md) — 深入理解 @run_sync 工作原理
