---
type: Concept
title: 安装与快速开始
description: 安装jupyterlab-webrtc-docprovider扩展，配置Jupyter Server启用协作，通过URL参数创建共享房间
tags: [install, pip, conda, configuration, getting-started, url-params]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README.md - Installation guide
  - id: contributing
    resource: /references/readme-source.md
    title: CONTRIBUTING.md - Development install
---

## 安装

### 通过 pip 安装

```bash
pip install jupyterlab-webrtc-docprovider
```

### 通过 conda/mamba 安装

```bash
mamba install -c conda-forge jupyterlab-webrtc-docprovider
# 或
conda install -c conda-forge jupyterlab-webrtc-docprovider
```

安装后 JupyterLab 会自动注册扩展，无需手动启用。

### 验证安装

```bash
jupyter labextension list
```

应看到 `@jupyterlite/webrtc-docprovider` 在列表中，状态为 `enabled`。

## 服务器配置

安装后需要在 Jupyter Server 配置中启用协作模式：

### 方法1：配置文件

创建或编辑 `jupyter_server_config.json`：

```json
{
  "LabServerApp": {
    "collaborative": true
  }
}
```

### 方法2：命令行参数

```bash
jupyter lab --collaborative
```

### JupyterLite 配置

在 `jupyter-lite.json` 中配置：

```json
{
  "jupyter-config-data": {
    "collaborative": true
  }
}
```

> **注意**：如果 `collaborative` 为 false，WebRTC DocProvider 将返回 `ProviderMock`（空提供者），不会实际建立 P2P 连接。

## 快速开始

### 1. 启动 JupyterLab

```bash
jupyter lab
```

### 2. 创建共享房间

在浏览器中打开 JupyterLab，通过 URL 参数指定房间：

```
http://localhost:8888/lab?room=demo
```

### 3. 指定用户名和颜色（可选）

```
http://localhost:8888/lab?room=demo&username=jo&usercolor=e65100
```

| URL 参数 | 说明 | 示例 |
|----------|------|------|
| `room` | 房间名称 | `?room=my-meeting` |
| `username` | 显示的用户名 | `?username=Alice` |
| `usercolor` | 光标颜色（hex，不含#） | `?usercolor=e65100` |

### 4. 打开共享文档

打开 Notebook 或文本编辑器，在同一房间的其他用户将能看到彼此的光标和编辑操作。

### 5. 查看协作状态

- **JupyterLab**：右下角状态栏显示 peer 数量、房间名、用户名
- **RetroLab**：工具栏中显示状态图标
- 点击命令面板中的 "Toggle WebRTC Sharing" 可随时启用/禁用分享

## 开发安装

如需修改源码进行开发：

```bash
git clone https://github.com/jupyterlite/jupyterlab-webrtc-docprovider.git
cd jupyterlab-webrtc-docprovider
python -m pip install -e .
jupyter labextension develop . --overwrite
jlpm build
```

开发时使用 watch 模式自动重新构建：

```bash
# 终端1：监听源码变更
jlpm watch
# 终端2：启动 JupyterLab
jupyter lab --no-browser --debug
```

## 卸载

```bash
pip uninstall jupyterlab-webrtc-docprovider
# 或
mamba uninstall jupyterlab-webrtc-docprovider
```

## 相关概念

- [项目介绍](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [配置三级优先级系统](09-configuration.md)
