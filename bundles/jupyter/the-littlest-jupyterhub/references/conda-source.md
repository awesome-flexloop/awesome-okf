---
type: Reference
title: conda.py 源码信源
description: tljh/conda.py 模块公共 API 信源文档
tags: [reference, source, conda, mamba, miniforge, package-management, api]
sources:
  - id: tljh-conda
    title: tljh/conda.py
---

# conda.py 源码信源

> Conda/Miniforge 环境管理模块。负责 Miniforge 下载安装、Conda/pip 包安装、权限修复等。

## 公共函数

### `sha256_file(fname) → str`

计算文件 SHA256 哈希值，4096 字节分块读取。

### `get_conda_package_versions(prefix) → dict`

执行 `<prefix>/bin/conda list --json`，解析 JSON 输出返回 `{package_name: version}` 字典。

### `download_miniconda_installer(installer_url, sha256sum)`（上下文管理器）

下载 Miniforge 安装脚本到临时文件：
1. 下载到 NamedTemporaryFile
2. 计算 SHA256 校验和，不匹配则 raise
3. yield 临时文件路径
4. 退出时自动清理临时文件

### `fix_permissions(prefix)`

修复 Conda 环境文件权限：
1. `chown -R {uid}:{gid} prefix`（当前用户）
2. `chmod -R o-w prefix`（移除其他用户写权限）

### `install_miniconda(installer_path, prefix)`

安装 Miniforge：
1. 执行 `/bin/bash {installer_path} -u -b -p {prefix}`
   - `-u`：接受许可协议
   - `-b`：batch 模式（无交互）
   - `-p`：安装前缀
2. 调用 `fix_permissions(prefix)`

### `ensure_conda_packages(prefix, packages, channels=("conda-forge",), force_reinstall=False)`

在指定 Conda 环境中安装包：
1. 优先使用 mamba（`<prefix>/bin/mamba` 存在则使用），否则使用 conda
2. 构建命令：`{bin} install --yes [-c channel...] --prefix {abspath(prefix)} [--force-reinstall] packages`
3. 通过 `run_subprocess` 执行

### `ensure_pip_packages(prefix, packages, upgrade=False)`

在指定环境中使用 pip 安装包：
1. 命令：`{prefix}/bin/python -m pip install [--upgrade] packages`

### `ensure_pip_requirements(prefix, requirements_path, upgrade=False)`

从 requirements 文件安装：
1. 命令：`{prefix}/bin/python -m pip install [--upgrade] --requirement {requirements_path}`
2. requirements_path 可以是本地文件路径或 URL
