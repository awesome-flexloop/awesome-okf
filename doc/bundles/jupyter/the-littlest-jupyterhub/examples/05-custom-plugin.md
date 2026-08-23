---
title: 开发一个简单 TLJH 插件
description: 从零创建一个 TLJH 插件，预装数据科学包并自定义配置
type: Tutorial
tags: [example, plugin, pluggy, tutorial, extension, python, jupyterhub, tljh]
sources:
  - id: tljh-hooks
    title: tljh/hooks.py
  - id: tljh-installer
    title: tljh/installer.py
---

# 开发一个简单 TLJH 插件

本文档演示如何创建一个 TLJH 插件，实现：
1. 在 User 环境预装常用数据科学包
2. 设置默认内存限制
3. 安装后显示欢迎信息

## 插件结构

```
tljh-datascience/
├── setup.py
└── tljh_datascience.py
```

## 步骤1：创建插件文件

创建 `tljh_datascience.py`：

```python
"""TLJH 插件：预装数据科学环境"""
from tljh.hooks import hookimpl


@hookimpl
def tljh_extra_user_conda_packages():
    """在 User 环境预装 conda 包"""
    return [
        "numpy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "scipy",
    ]


@hookimpl
def tljh_extra_user_conda_channels():
    """添加 conda-forge channel"""
    return ["conda-forge"]


@hookimpl
def tljh_extra_user_pip_packages():
    """在 User 环境预装 pip 包"""
    return [
        "seaborn",
        "plotly",
        "jupyter-resource-usage",
    ]


@hookimpl
def tljh_extra_hub_pip_packages():
    """在 Hub 环境安装额外包"""
    return []


@hookimpl
def tljh_extra_apt_packages():
    """安装系统依赖"""
    return [
        "build-essential",
    ]


@hookimpl
def tljh_config_post_install(config):
    """修改默认配置：设置内存限制和默认应用"""
    # 设置默认内存限制为 4GB
    if "limits" not in config:
        config["limits"] = {}
    config["limits"]["memory"] = "4G"
    config["limits"]["cpu"] = 2.0

    # 默认使用 JupyterLab
    if "user_environment" not in config:
        config["user_environment"] = {}
    config["user_environment"]["default_app"] = "jupyterlab"

    # 延长空闲超时到 1 小时
    if "services" not in config:
        config["services"] = {}
    if "cull" not in config["services"]:
        config["services"]["cull"] = {}
    config["services"]["cull"]["timeout"] = 3600


@hookimpl
def tljh_custom_jupyterhub_config(c):
    """自定义 JupyterHub 配置"""
    # 限制最大同时运行服务器数
    c.JupyterHub.active_server_limit = 50

    # 设置 Notebook 启动超时
    c.Spawner.start_timeout = 120
    c.Spawner.http_timeout = 60


@hookimpl
def tljh_post_install():
    """安装完成后的操作"""
    print("=" * 60)
    print("数据科学环境插件安装完成！")
    print("预装包：numpy, pandas, matplotlib, scikit-learn, scipy, seaborn, plotly")
    print("默认配置：4GB 内存限制, 2核 CPU, JupyterLab, 1小时空闲超时")
    print("=" * 60)


@hookimpl
def tljh_new_user_create(username):
    """新用户创建时的操作"""
    print(f"新用户 {username} 已创建，可以使用数据科学环境")
```

## 步骤2：创建 setup.py

```python
from setuptools import setup

setup(
    name="tljh-datascience",
    version="0.1.0",
    description="TLJH 插件：数据科学环境预设",
    py_modules=["tljh_datascience"],
    entry_points={
        "tljh": [
            "datascience = tljh_datascience",
        ],
    },
    install_requires=[
        "the-littlest-jupyterhub",
    ],
)
```

关键点：
- `entry_points` 中的 `"tljh"` 组名是固定的
- entry point 名称（如 `datascience`）可以任意，但等号右边必须是模块名

## 步骤3：安装插件

### 方式一：本地安装

将插件目录复制到服务器上：

```bash
sudo /opt/tljh/hub/bin/pip install /path/to/tljh-datascience/
```

### 方式二：从 Git 安装

```bash
sudo /opt/tljh/hub/bin/pip install git+https://github.com/yourusername/tljh-datascience.git
```

### 方式三：bootstrap 时安装

```bash
curl -L https://tljh.jupyter.org/bootstrap.py | sudo python3 - \
  --plugin tljh-datascience \
  --admin admin
```

## 步骤4：重新运行安装器以应用插件

安装阶段的钩子（apt/pip/conda 包、config_post_install、post_install）需要重新运行 installer 才会执行：

```bash
sudo /opt/tljh/hub/bin/python -m tljh.installer
```

运行时钩子（tljh_custom_jupyterhub_config）在 Hub 重启后生效：

```bash
sudo tljh-config reload hub
```

## 步骤5：验证插件

检查配置是否被插件修改：

```bash
sudo tljh-config show
```

应看到：
- `limits.memory: "4G"`
- `limits.cpu: 2.0`
- `user_environment.default_app: "jupyterlab"`
- `services.cull.timeout: 3600`

检查包是否安装：

```bash
/opt/tljh/user/bin/python -c "import numpy; import pandas; import sklearn; print('OK')"
```

## 插件钩子类型总结

| 钩子 | 调用时机 | 用途 |
|------|---------|------|
| `tljh_extra_apt_packages` | 安装时 | 安装系统包 |
| `tljh_extra_hub_pip_packages` | 安装时 | Hub 环境包 |
| `tljh_extra_user_conda_packages` | 安装时 | User 环境 conda 包 |
| `tljh_extra_user_conda_channels` | 安装时 | Conda channels |
| `tljh_extra_user_pip_packages` | 安装时 | User 环境 pip 包 |
| `tljh_custom_jupyterhub_config(c)` | Hub 启动时 | 任意 JupyterHub 配置 |
| `tljh_config_post_install(config)` | 安装时 | 修改 config.yaml 默认值 |
| `tljh_post_install()` | 安装完成时 | 任意安装后操作 |
| `tljh_new_user_create(username)` | 用户创建时 | 新用户初始化 |

## 更高级的插件示例

### 自定义认证插件

```python
# tljh_myauth.py
from tljh.hooks import hookimpl


@hookimpl
def tljh_extra_hub_pip_packages():
    return ["my-custom-authenticator"]


@hookimpl
def tljh_custom_jupyterhub_config(c):
    c.JupyterHub.authenticator_class = "myauth.MyAuthenticator"
    c.MyAuthenticator.some_option = "value"
```

### 安装 nbextension 插件

```python
@hookimpl
def tljh_extra_user_pip_packages():
    return [
        "jupyter_contrib_nbextensions",
    ]


@hookimpl
def tljh_post_install():
    import subprocess
    subprocess.run([
        "/opt/tljh/user/bin/jupyter", "contrib", "nbextension", "install", "--user"
    ])
```

## 调试插件

查看插件是否被正确加载：

```bash
sudo /opt/tljh/hub/bin/python -c "
from tljh.utils import get_plugin_manager
pm = get_plugin_manager()
print('Loaded plugins:', [p.__name__ for p in pm.get_plugins()])
print('Available hooks:', [h.name for h in pm.hook.tljh_extra_user_pip_packages.get_hookimpls()])
"
```

查看安装日志中的插件输出：

```bash
sudo cat /opt/tljh/installer.log | grep -A5 "插件名"
```

## 注意事项

1. **root 权限**：插件钩子以 root 运行，只安装可信插件
2. **幂等性**：插件安装钩子可能被多次调用（re-run installer），确保操作幂等
3. **版本兼容**：插件依赖的包版本应与 TLJH 的依赖兼容
4. **错误处理**：钩子中应适当处理异常，避免安装中断
