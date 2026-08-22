---
type: Reference
title: hooks.py 源码信源
description: tljh/hooks.py 模块插件钩子规范信源文档
tags: [reference, source, hooks, pluggy, plugin, api]
sources:
  - id: tljh-hooks
    title: tljh/hooks.py
---

# hooks.py 源码信源

> TLJH 插件钩子规范定义模块。基于 pluggy 框架定义 9 个 hookspec，插件通过 @hookimpl 实现这些钩子来扩展 TLJH。

## 全局对象

```python
hookspec = pluggy.HookspecMarker("tljh")
hookimpl = pluggy.HookimplMarker("tljh")
```

## 钩子规范（Hookspecs）

### `tljh_extra_apt_packages() → list[str]`

**调用时机**：安装阶段，所有包安装之前
**返回**：需要通过 apt 安装的系统包名列表
**注意**：apt 包最先安装，因为后续 pip/conda 包可能依赖系统库

### `tljh_extra_user_conda_channels() → list[str]`

**调用时机**：安装阶段，安装 user conda 包时
**返回**：额外的 Conda channel 名称列表
**默认**：无额外 channel 时使用 conda-forge

### `tljh_extra_user_conda_packages() → list[str]`

**调用时机**：安装阶段，apt 包和 hub pip 包之后
**返回**：需要安装到 User Conda 环境的包名列表

### `tljh_extra_user_pip_packages() → list[str]`

**调用时机**：安装阶段，conda 包之后
**返回**：需要安装到 User 环境的 pip 包名列表

### `tljh_extra_hub_pip_packages() → list[str]`

**调用时机**：安装阶段，apt 包之后，conda 包之前
**返回**：需要安装到 Hub 环境的 pip 包名列表
**典型用途**：安装自定义认证器、Spawner 等

### `tljh_custom_jupyterhub_config(c)`

**调用时机**：JupyterHub 启动时，在 jupyterhub_config.py 中
**参数**：`c` — JupyterHub Traitlets 配置对象
**用途**：直接修改 JupyterHub 任意配置项（最强大的钩子）
**注意**：此钩子在所有默认配置应用之后、jupyterhub_config.d/*.py 之前调用

### `tljh_config_post_install(config)`

**调用时机**：安装阶段，ensure_config_yaml 中
**参数**：`config` — dict-like 配置对象（**原地修改**）
**用途**：修改 config.yaml 的默认值
**注意**：修改后会被写回 config.yaml

### `tljh_post_install()`

**调用时机**：安装阶段，所有包安装完成后（installer 最后）
**参数**：无
**用途**：执行安装后的自定义操作（重启服务、下载数据、初始化等）

### `tljh_new_user_create(username)`

**调用时机**：新用户首次登录、系统用户创建后
**参数**：`username` — JupyterHub 用户名
**用途**：新用户初始化（创建默认文件、设置环境等）

## 插件发现机制

插件通过 Python 包的 setuptools entry points 注册，entry point 组名为 `"tljh"`：

```python
# setup.py
setup(
    entry_points={"tljh": ["my_plugin = my_plugin_module"]},
)
```

PluginManager 通过 `pm.load_setuptools_entrypoints("tljh")` 自动发现并加载所有注册的插件。

## 钩子执行顺序

安装阶段：
1. tljh_extra_apt_packages → apt install
2. tljh_extra_hub_pip_packages → hub pip install
3. tljh_extra_user_conda_channels + tljh_extra_user_conda_packages → user conda install
4. tljh_extra_user_pip_packages → user pip install
5. tljh_post_install

配置阶段：
- tljh_config_post_install（写 config.yaml）

运行时（JupyterHub 启动）：
- 默认配置 → update_* 函数 → tljh_custom_jupyterhub_config(c) → jupyterhub_config.d/*.py

新用户创建：
- ensure_user() 创建系统用户后 → tljh_new_user_create(username)
