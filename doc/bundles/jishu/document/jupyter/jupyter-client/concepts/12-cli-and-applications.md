---
okf_version: "0.2"
type: concept
title: "CLI工具与应用"
description: "jupyter-kernelspec/jupyter-run/jupyter-kernel 三个CLI入口、KernelSpecApp/RunApp/KernelApp/JupyterConsoleApp 应用类、run_kernel便捷函数"
tags: ["cli", "command-line", "jupyter-kernelspec", "jupyter-run", "jupyter-kernel", "consoleapp", "runapp", "kernelapp"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: kernelspecapp-py
    resource: jupyter_client/kernelspecapp.py
    title: jupyter_client/kernelspecapp.py
  - id: runapp-py
    resource: jupyter_client/runapp.py
    title: jupyter_client/runapp.py
  - id: consoleapp-py
    resource: jupyter_client/consoleapp.py
    title: jupyter_client/consoleapp.py
  - id: kernelapp-py
    resource: jupyter_client/kernelapp.py
    title: jupyter_client/kernelapp.py
---

# CLI工具与应用

jupyter_client 提供三个命令行入口点和相应的应用类，分别用于内核规范管理、脚本执行和内核进程启动。

## CLI 入口总览

| 命令 | 入口函数 | 应用类 | 用途 |
|------|---------|--------|------|
| `jupyter-kernelspec` | `KernelSpecApp.launch_instance` | `KernelSpecApp` | 管理内核规范（安装/列出/删除） |
| `jupyter-run` | `RunApp.launch_instance` | `RunApp` | 运行脚本文件（类似 `python script.py` 但通过内核） |
| `jupyter-kernel` | `kernelapp:main` | `KernelApp` | 启动内核进程（通常由 KernelManager 调用） |

所有应用类都继承自 `traitlets.config.Application`，使用 traitlets 配置系统。

## jupyter-kernelspec：内核规范管理

### 用法

```bash
# 列出所有已安装的内核
jupyter-kernelspec list

# 安装内核规范
jupyter-kernelspec install /path/to/kernel_spec_dir [--user] [--prefix=PREFIX] [--replace] [--name=NAME]

# 删除内核规范
jupyter-kernelspec remove KERNEL_NAME

# 查看内核规范安装路径
jupyter-kernelspec install --help
```

### KernelSpecApp 实现

```python
class KernelSpecApp(Application):
    name = "jupyter-kernelspec"
    description = "Manage Jupyter kernel specifications"

    subcommands = {
        "list": (ListKernelSpecs, "List installed kernel specifications."),
        "install": (InstallKernelSpec, "Install a kernel specification."),
        "remove": (RemoveKernelSpec, "Remove a kernel specification."),
        # "uninstall" 是 "remove" 的别名
    }
```

三个子命令对应三个子应用：

```python
class ListKernelSpecs(Application):
    def start(self):
        ksm = KernelSpecManager()
        specs = ksm.find_kernel_specs()
        for name, path in sorted(specs.items()):
            print(f"  {name}\t{path}")

class InstallKernelSpec(Application):
    user = Bool(False, help="Install for current user")
    prefix = Unicode("", help="Installation prefix")
    replace = Bool(False, help="Replace existing kernel")
    kernel_name = Unicode("", help="Kernel name")

    def start(self):
        ksm = KernelSpecManager()
        ksm.install_kernel_spec(
            self.sourcedir,
            kernel_name=self.kernel_name or None,
            user=self.user,
            prefix=self.prefix or None,
            replace=self.replace,
        )

class RemoveKernelSpec(Application):
    def start(self):
        ksm = KernelSpecManager()
        for name in self.extra_args:
            ksm.remove_kernel_spec(name)
```

## jupyter-run：脚本执行

### 用法

```bash
# 运行脚本
jupyter-run my_script.py

# 使用指定内核运行
jupyter-run --kernel=python3 my_script.py

# 带参数运行（参数传递给脚本）
jupyter-run my_script.py --arg1 value1 --arg2
```

### RunApp 实现

`RunApp` 启动内核、执行脚本、输出结果后关闭内核：

```python
class RunApp(Application):
    name = "jupyter-run"
    description = "Run a script in a kernel"

    kernel_name = Unicode("python3", config=True)
    filename = Unicode()
    meta = Instance(SimpleNamespace, allow_none=True)

    def initialize(self, argv=None):
        super().initialize(argv)
        self.filename = self.extra_args[0] if self.extra_args else ""

    def start(self):
        # 1. 启动内核
        km, kc = start_new_kernel(kernel_name=self.kernel_name)

        try:
            # 2. 读取脚本内容
            with open(self.filename, encoding="utf-8") as f:
                code = f.read()

            # 3. 执行脚本
            reply = kc.execute_interactive(
                code,
                output_hook=self._output_hook,
                timeout=None,
            )

            # 4. 根据执行状态设置退出码
            if reply["content"]["status"] != "ok":
                sys.exit(1)
        finally:
            # 5. 清理
            kc.stop_channels()
            km.shutdown_kernel()

    def _output_hook(self, msg):
        """处理输出消息——直接打印到 stdout/stderr"""
        msg_type = msg["header"]["msg_type"]
        if msg_type == "stream":
            text = msg["content"]["text"]
            if msg["content"]["name"] == "stdout":
                sys.stdout.write(text)
            elif msg["content"]["name"] == "stderr":
                sys.stderr.write(text)
        elif msg_type == "error":
            # 打印 traceback
            for line in msg["content"]["traceback"]:
                sys.stderr.write(line + "\n")
```

## jupyter-kernel：内核启动

`jupyter-kernel` 命令启动一个内核进程，通常由 KernelManager 通过 Provisioner 调用，不需要手动执行。

### 用法

```bash
# 通过连接文件启动内核
jupyter-kernel -f /path/to/connection-file.json

# 指定内核实现类
jupyter-kernel --kernel-class=ipykernel.kernelapp.IPKernelApp
```

### KernelApp 实现

```python
class KernelApp(Application):
    """启动内核的应用基类"""

    connection_file = Unicode("", config=True)
    parentpid = Integer(0, config=True)

    def initialize(self, argv=None):
        super().initialize(argv)
        self.init_connection_file()
        self.init_sockets()
        self.init_session()

    def init_connection_file(self):
        """从 --file 参数加载连接文件"""
        if not self.connection_file:
            # 从命令行 -f 参数获取
            ...
        self.connection_info = json.loads(open(self.connection_file).read())

    def init_sockets(self):
        """创建 ZMQ sockets 并绑定到连接文件指定的端口"""
        ...

    def init_session(self):
        """初始化 Session 对象"""
        ...

    def start(self):
        """启动内核事件循环"""
        self.log.info("Starting kernel...")
        # 子类实现具体的内核逻辑（如 ipykernel 的 IPKernelApp）
```

实际的内核逻辑（代码执行、消息处理）由具体的内核实现提供（如 ipykernel），jupyter_client 只提供启动框架和连接管理。

## JupyterConsoleApp：控制台基类

`JupyterConsoleApp` 是 Jupyter 控制台应用的基类，被 `jupyter_console` 等前端使用：

```python
class JupyterConsoleApp(Application):
    """控制台应用基类"""

    kernel_name = Unicode("python3", config=True)
    existing = Unicode("", config=True)  # 连接到已有内核
    connection_file = Unicode("", config=True)

    def initialize(self, argv=None):
        super().initialize(argv)
        if self.existing:
            self.init_connection_file()
            self.init_kc()  # 创建 client 连接到已有内核
        else:
            self.init_kernel_manager()  # 启动新内核
            self.init_kc()
```

## run_kernel 便捷函数

```python
def run_kernel(**kwargs):
    """运行内核的便捷入口（用于 jupyter-kernel 命令）"""
    return KernelApp.launch_instance(**kwargs)
```

## 编程方式使用 CLI 类

CLI 应用类也可以在 Python 代码中直接使用：

```python
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client import start_new_kernel

# 等价于 jupyter-kernelspec list
ksm = KernelSpecManager()
kernels = ksm.find_kernel_specs()
for name, path in kernels.items():
    print(f"{name}: {path}")

# 等价于 start_new_kernel + 执行代码
km, kc = start_new_kernel()
kc.execute_interactive("print('hello')")
kc.stop_channels()
km.shutdown_kernel()
```

## Entry Points 注册

jupyter_client 通过 pyproject.toml 注册 CLI 入口点：

```toml
[project.scripts]
jupyter-kernelspec = "jupyter_client.kernelspecapp:KernelSpecApp.launch_instance"
jupyter-run = "jupyter_client.runapp:RunApp.launch_instance"
jupyter-kernel = "jupyter_client.kernelapp:main"
```

以及在 Jupyter 应用子命令组中注册：

```toml
[project.entry-points.jupyter_commands]
kernelspec = "jupyter_client.kernelspecapp:KernelSpecApp"
run = "jupyter_client.runapp:RunApp"
kernel = "jupyter_client.kernelapp:KernelApp"
```

这使得 `jupyter kernelspec` 和 `jupyter run` 也可以工作（通过 jupyter_core 的子命令发现）。

## 相关概念

- [内核规范管理](09-kernel-spec.md)
- [5分钟快速上手](01-getting-started.md)
- [内核管理器](06-kernel-manager.md)
