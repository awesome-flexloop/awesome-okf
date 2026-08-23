---
okf_version: "0.2"
type: concept
title: "内核规范管理"
description: "KernelSpec 数据模型、KernelSpecManager 发现/安装/管理 kernelspec、kernel.json 格式规范、内核搜索路径与优先级、allowed_kernelspecs 过滤"
tags: ["kernelspec", "kernel-spec", "kernel.json", "find-kernels", "install-kernel", "kernel-spec-manager"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: kernelspec-py
    resource: jupyter_client/kernelspec.py
    title: jupyter_client/kernelspec.py
  - id: kernelspecapp-py
    resource: jupyter_client/kernelspecapp.py
    title: jupyter_client/kernelspecapp.py
---

# 内核规范管理

KernelSpec（内核规范）描述了如何启动一个内核以及内核的元数据。`KernelSpecManager` 负责发现、加载、安装和管理系统中所有的内核规范。

## KernelSpec 数据模型

```python
class KernelSpec(HasTraits):
    """内核规范模型对象"""

    argv: List[str] = List()                 # 启动命令行（含参数）
    name = Unicode()                         # 内核名称
    mimetype = Unicode()                     # 代码 MIME 类型（如 text/x-python）
    display_name = Unicode()                 # 显示名称（人类可读）
    language = Unicode()                     # 编程语言（如 "python"）
    kernel_protocol_version = Unicode()      # 支持的内核协议版本
    env = Dict()                             # 启动时设置的环境变量
    resource_dir = Unicode()                 # 资源目录（包含 kernel.json 和 logo）
    interrupt_mode = CaselessStrEnum(        # 中断模式
        ["message", "signal"],
        default_value="signal",
    )
    metadata = Dict()                        # 扩展元数据（provisioner配置等）
```

### kernel.json 文件格式

KernelSpec 以 `kernel.json` 文件的形式存储在目录中，典型格式：

```json
{
  "argv": ["python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
  "display_name": "Python 3",
  "language": "python",
  "interrupt_mode": "signal",
  "metadata": {},
  "env": {}
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `argv` | string[] | ✅ | 启动命令数组，`{connection_file}` 会被替换为连接文件路径 |
| `display_name` | string | ✅ | UI 中显示的名称 |
| `language` | string | ✅ | 编程语言标识符 |
| `interrupt_mode` | string | ❌ | `"signal"`（发送SIGINT）或 `"message"`（发送interrupt_request消息） |
| `metadata` | object | ❌ | 扩展元数据，如 provisioner 配置 |
| `env` | object | ❌ | 启动内核时设置的环境变量 |
| `mimetype` | string | ❌ | 代码 MIME 类型 |
| `kernel_protocol_version` | string | ❌ | 支持的协议版本 |

### 资源目录结构

每个内核规范是一个目录，包含：

```
python3/                          # 内核名称作为目录名
├── kernel.json                   # 内核规范文件（必需）
├── logo-32x32.png                # 32px logo（可选）
├── logo-64x64.png                # 64px logo（可选）
├── logo-svg.svg                  # SVG logo（可选）
└── kernel.js                     # 内核扩展 JS（可选）
```

目录名即为内核名称（kernel_name），必须匹配正则 `^[a-z0-9._\-]+$`（ASCII字母、数字、连字符、点号、下划线）。

## 内核搜索路径

KernelSpecManager 按优先级搜索多个目录（后者优先）：

```python
def _kernel_dirs_default(self) -> list[str]:
    dirs = jupyter_path("kernels")  # 系统级 + 用户级 + 环境级
    # 兼容 IPython 旧路径
    try:
        from IPython.paths import get_ipython_dir
        dirs.append(os.path.join(get_ipython_dir(), "kernels"))
    except ModuleNotFoundError:
        pass
    return dirs
```

搜索顺序（优先级从低到高）：

| 目录类型 | 路径示例（Linux/macOS） | 优先级 |
|---------|----------------------|--------|
| 系统级 | `/usr/share/jupyter/kernels/` | 最低 |
| 环境级 | `{sys.prefix}/share/jupyter/kernels/` | 中 |
| 用户级 | `~/.local/share/jupyter/kernels/` | 高 |
| IPython 兼容 | `~/.ipython/kernels/` | 最高 |
| ipykernel 内置 | ipykernel.kernelspec.RESOURCES | 兜底 |

在 Windows 上路径类似（`%APPDATA%\jupyter\kernels\` 等）。

### find_kernel_specs()：发现所有内核

```python
def find_kernel_specs(self) -> dict[str, str]:
    """返回 {kernel_name: resource_dir} 映射"""
    d = {}
    for kernel_dir in self.kernel_dirs:
        kernels = _list_kernels_in(kernel_dir)  # 扫描目录找 kernel.json
        for kname, spec in kernels.items():
            if kname not in d:  # 后面的目录优先级更高
                d[kname] = spec

    # 兜底：如果没有 python3 kernel 且 ipykernel 可用，添加内置 kernel
    if self.ensure_native_kernel and NATIVE_KERNEL_NAME not in d:
        try:
            from ipykernel.kernelspec import RESOURCES
            d[NATIVE_KERNEL_NAME] = RESOURCES
        except ImportError:
            pass

    # 白名单过滤
    if self.allowed_kernelspecs:
        d = {name: spec for name, spec in d.items() if name in self.allowed_kernelspecs}
    return d
```

### get_kernel_spec()：加载内核规范

```python
def get_kernel_spec(self, kernel_name: str) -> KernelSpec:
    """加载指定名称的 KernelSpec，找不到则抛出 NoSuchKernel"""
    resource_dir = self._find_spec_directory(kernel_name)
    if resource_dir is None:
        raise NoSuchKernel(kernel_name)
    return self._get_kernel_spec_by_name(kernel_name, resource_dir)
```

加载时还会检查该 kernelspec 需要的 provisioner 是否可用（`KPF.instance().is_provisioner_available(kspec)`），如果 provisioner 未安装则抛出 `NoSuchKernel`。

## 安装内核规范

### install_kernel_spec()

```python
def install_kernel_spec(self, source_dir, kernel_name=None,
                        user=None, prefix=None, replace=None):
    """安装内核规范到 Jupyter 搜索路径"""
    # 1. 确定目标目录
    # user=True → 用户目录 (~/.local/share/jupyter/kernels/<name>/)
    # prefix=PREFIX → {prefix}/share/jupyter/kernels/<name>/
    # 默认 → sys.prefix

    # 2. 验证 source_dir/kernel.json 存在
    # 3. 复制目录到目标位置
    # 4. 返回安装的 kernel_name
```

### CLI：jupyter-kernelspec

KernelSpecApp 提供命令行工具管理内核规范：

```bash
# 列出所有已安装的内核
jupyter-kernelspec list

# 安装内核规范
jupyter-kernelspec install /path/to/kernel_spec_dir --user

# 安装内核规范（替换已有）
jupyter-kernelspec install /path/to/kernel_spec_dir --replace

# 删除内核规范
jupyter-kernelspec remove python3-custom

# 查看内核规范信息
jupyter-kernelspec list | grep python3
```

### 通过 Python API 安装

```python
from jupyter_client.kernelspec import KernelSpecManager

ksm = KernelSpecManager()

# 安装自定义内核
ksm.install_kernel_spec(
    source_dir="/path/to/my_kernel_spec",
    kernel_name="my-python",
    user=True,       # 安装到用户目录
    replace=True,    # 替换已有
)

# 列出所有内核
all_kernels = ksm.find_kernel_specs()
print(f"Available kernels: {list(all_kernels.keys())}")

# 加载内核规范
spec = ksm.get_kernel_spec("python3")
print(f"argv: {spec.argv}")
print(f"language: {spec.language}")
```

## interrupt_mode：中断模式

| 模式 | 机制 | 适用场景 |
|------|------|---------|
| `"signal"` | 发送 SIGINT（Unix）或中断事件（Windows）到内核进程 | 本地内核，ipykernel 默认 |
| `"message"` | 通过 control 通道发送 `interrupt_request` 消息 | 远程内核（无法发送信号到远程进程） |

远程内核（SSH/Docker/K8s Provisioner）通常使用 `"message"` 模式，因为无法直接向远程容器/主机发送操作系统信号。

## Provisioner 与 KernelSpec 的关联

KernelSpec 的 `metadata.kernel_provisioner` 字段指定使用哪个供给器：

```json
{
  "argv": ["python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
  "display_name": "Python 3 (Docker)",
  "language": "python",
  "metadata": {
    "kernel_provisioner": {
      "provisioner_name": "docker-provisioner",
      "config": {
        "image": "python:3.11",
        "network": "host"
      }
    }
  }
}
```

KernelSpecManager.get_kernel_spec() 会调用 `KernelProvisionerFactory.is_provisioner_available(kspec)` 验证该供给器是否已安装。

## allowed_kernelspecs 白名单

在多租户环境中（如 JupyterHub），管理员可以限制可用内核：

```python
c.KernelSpecManager.allowed_kernelspecs = {"python3", "ir"}  # 只允许 Python 和 R
```

被排除的内核不会在 `find_kernel_specs()` 中出现，`get_kernel_spec()` 也会抛出 `NoSuchKernel`。

## 相关概念

- [内核供给器框架](08-kernel-provisioner.md)
- [内核管理器](06-kernel-manager.md)
- [内核启动与自动重启](10-kernel-launch-and-restart.md)
