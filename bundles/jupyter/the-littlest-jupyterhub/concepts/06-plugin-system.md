---
title: TLJH 插件系统
description: 基于 pluggy 框架的 8 个扩展点，通过 Python 包扩展 TLJH 功能
type: Explanation
tags: [concept, plugins, pluggy, extension, hooks, jupyterhub, tljh, python]
sources:
  - id: tljh-hooks
    title: tljh/hooks.py
  - id: tljh-installer
    title: tljh/installer.py
  - id: tljh-utils
    title: tljh/utils.py
  - id: tljh-configurer
    title: tljh/configurer.py
---

# TLJH 插件系统

TLJH 基于 **pluggy** 框架实现插件系统（与 pytest 插件系统相同的框架）。插件是标准的 Python 包，通过 setuptools entry points 自动发现，可在安装和运行的多个阶段注入自定义行为。

## 插件架构概述

```
tljh/hooks.py (hookspec 定义)
    ↓ pluggy
插件 Python 包 (hookimpl 实现)
    ↓ entry_points {"tljh": ["plugin = package.module"]}
PluginManager 自动发现并加载
    ↓
安装阶段和运行阶段调用钩子
```

## 8 个扩展钩子（Hookspec）

### 1. tljh_extra_apt_packages()

**时机**：安装阶段，在 pip/conda 包之前执行。
**返回**：需要通过 apt 安装的额外包名列表。

```python
@hookspec
def tljh_extra_apt_packages():
    return ["my-system-dependency"]
```

apt 包最先安装，因为后续的 pip/conda 包可能依赖系统库。

### 2. tljh_extra_hub_pip_packages()

**时机**：安装阶段，在 apt 包之后。
**返回**：需要安装到 Hub 环境的 pip 包名列表。

```python
@hookspec
def tljh_extra_hub_pip_packages():
    return ["my-authenticator", "my-spawner"]
```

这些包安装到 `/opt/tljh/hub/` 环境，JupyterHub 可直接 import。

### 3. tljh_extra_user_conda_packages()

**时机**：安装阶段，在 hub pip 包之后。
**返回**：需要安装到 User 环境的 Conda 包名列表。

```python
@hookspec
def tljh_extra_user_conda_packages():
    return ["numpy", "pandas"]
```

默认从 conda-forge channel 安装。

### 4. tljh_extra_user_conda_channels()

**时机**：与 conda packages 同时。
**返回**：额外的 Conda channel 列表。

```python
@hookspec
def tljh_extra_user_conda_channels():
    return ["pytorch", "nvidia"]
```

### 5. tljh_extra_user_pip_packages()

**时机**：安装阶段，在 conda 包之后。
**返回**：需要安装到 User 环境的 pip 包名列表。

```python
@hookspec
def tljh_extra_user_pip_packages():
    return ["scikit-learn", "matplotlib"]
```

### 6. tljh_custom_jupyterhub_config(c)

**时机**：JupyterHub 启动时，在 `jupyterhub_config.py` 中调用。
**参数**：`c` — JupyterHub 的 Traitlets 配置对象。

这是最强大的钩子，可以直接修改 JupyterHub 的任何配置：

```python
@hookspec
def tljh_custom_jupyterhub_config(c):
    c.Spawner.default_url = "/lab"
    c.JupyterHub.active_server_limit = 50
    c.Authenticator.admin_users.add("admin")
```

### 7. tljh_config_post_install(config)

**时机**：安装阶段，在 config.yaml 创建后调用。
**参数**：`config` — dict-like 配置对象，**原地修改**。

```python
@hookspec
def tljh_config_post_install(config):
    config["https"]["enabled"] = True
```

此钩子可以修改 config.yaml 的默认值。修改后会被写回文件。

### 8. tljh_post_install()

**时机**：安装阶段，在所有包安装和配置完成后执行。
**用途**：执行安装后的自定义操作（重启服务、下载数据、初始化等）。

```python
@hookspec
def tljh_post_install():
    # 安装后的自定义操作
    subprocess.run(["/opt/tljh/hub/bin/tljh-config", "set", "..."])
```

### 9. tljh_new_user_create(username)

**时机**：新用户首次登录、系统用户创建后调用。
**参数**：`username` — JupyterHub 用户名。

```python
@hookspec
def tljh_new_user_create(username):
    # 为新用户初始化文件、设置环境等
    pass
```

## 插件执行顺序

安装阶段插件钩子执行顺序：

```
apt packages → hub pip packages → user conda channels
                                  ↓
                           user conda packages
                                  ↓
                            user pip packages
                                  ↓
                              post_install
```

配置阶段：

```
config.yaml 创建 → tljh_config_post_install → 写回 config.yaml
```

运行时（JupyterHub 启动）：

```
默认配置加载 → update_* 函数应用 → tljh_custom_jupyterhub_config(c) → jupyterhub_config.d/*.py
```

## 开发 TLJH 插件

### 步骤1：创建 Python 包

创建标准 Python 包结构：

```
my-tljh-plugin/
├── setup.py
└── my_tljh_plugin.py
```

### 步骤2：实现钩子

```python
# my_tljh_plugin.py
from tljh.hooks import hookimpl

@hookimpl
def tljh_extra_user_pip_packages():
    return ["my-favorite-package"]

@hookimpl
def tljh_custom_jupyterhub_config(c):
    c.Spawner.mem_limit = "2G"
```

### 步骤3：配置 entry_points

在 `setup.py` 中注册插件：

```python
from setuptools import setup

setup(
    name="my-tljh-plugin",
    version="0.1",
    py_modules=["my_tljh_plugin"],
    entry_points={
        "tljh": [
            "my_plugin = my_tljh_plugin",
        ],
    },
    install_requires=["the-littlest-jupyterhub"],
)
```

entry_points 中的 `"tljh"` 组名是固定的，TLJH 通过 `pm.load_setuptools_entrypoints("tljh")` 发现所有注册在此组下的插件。

### 步骤4：安装插件

将插件安装到 Hub 环境：

```bash
sudo /opt/tljh/hub/bin/pip install /path/to/my-tljh-plugin
```

或者在 bootstrap 时通过 `--plugin` 参数：

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - --plugin my-tljh-plugin --admin admin
```

### 步骤5：重新运行安装以应用插件

插件安装后需要重新执行安装器以触发安装阶段的钩子：

```bash
sudo /opt/tljh/hub/bin/python -m tljh.installer
```

运行时钩子（如 `tljh_custom_jupyterhub_config`）在重启 Hub 后生效：

```bash
sudo tljh-config reload hub
```

## PluginManager 管理

### 获取 PluginManager

```python
from tljh.utils import get_plugin_manager
pm = get_plugin_manager()
```

每次调用 `get_plugin_manager()` 都会创建新的 PluginManager 实例，注册 hookspecs 并加载所有 entry points。

### 手动调用钩子

```python
pm.hook.tljh_custom_jupyterhub_config(c=c)
```

## 安全注意事项

插件以 **root 权限**运行，可以执行任意代码（安装系统包、修改配置、访问文件系统）。只安装可信来源的插件。

插件钩子的执行权限：
- 安装阶段钩子：root 权限（installer 以 root 运行）
- 运行时钩子（tljh_custom_jupyterhub_config）：root 权限（jupyterhub.service 以 root 运行）
- 新用户钩子：Hub 进程以 root 调用

## 现有插件示例

TLJH 生态中的常见插件模式：

1. **认证器插件**：添加额外的 OAuth/SSO 认证器（通过 tljh_extra_hub_pip_packages + tljh_custom_jupyterhub_config）
2. **Spawner 插件**：替换 SystemdSpawner 为其他 Spawner（如 DockerSpawner）
3. **环境预设插件**：预装常用数据科学包（通过 tljh_extra_user_*_packages）
4. **配置预设插件**：预设最佳实践配置（通过 tljh_config_post_install）
5. **自定义页面插件**：修改 JupyterHub 模板和静态资源

## 下一步

- [安装流程深度解析](07-installation-deep-dive.md)：了解安装各阶段细节
- [简单插件开发示例](../examples/05-custom-plugin.md)：从零创建一个插件
