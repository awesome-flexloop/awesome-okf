---
type: Example
title: "基本服务器启动"
description: "从零开始启动 Jupyverse 服务器，使用无认证模式，在浏览器中访问 JupyterLab。"
tags: [quickstart, server, startup, noauth]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: getting_started
    resource: /concepts/01-getting-started.md
    title: 安装与启动
---

# 基本服务器启动

本示例演示如何在本地启动一个最小可用的 Jupyverse 服务器。

## 前置条件

- Python 3.10+
- pip 包管理器

## 步骤

### 1. 安装 Jupyverse

```bash
pip install "jupyverse[jupyterlab,noauth]"
```

`jupyterlab` 可选依赖安装 JupyterLab 前端，`noauth` 安装无认证插件。

### 2. 切换到工作目录

Jupyverse 以当前目录作为文件服务根目录，先切换到你的 Notebook 目录：

```bash
mkdir -p ~/jupyverse-work
cd ~/jupyverse-work
```

### 3. 启动服务器

```bash
jupyverse
```

Jupyverse 会自动选择 NoAuth 插件（因为安装了且其他认证插件未安装），默认监听 `127.0.0.1:8000`。

### 4. 访问 JupyterLab

打开浏览器访问：

```
http://127.0.0.1:8000/lab
```

你应该能看到 JupyterLab 界面，可以创建 Notebook、终端和文本文件。

## 常用启动变体

### 允许局域网访问

```bash
jupyverse --host 0.0.0.0
```

### 自定义端口

```bash
jupyverse --port 9999
```

### 自动打开浏览器

```bash
jupyverse --open-browser
```

### 启用调试日志

```bash
jupyverse --debug
```

## 验证服务器状态

```bash
curl http://127.0.0.1:8000/api/status
```

返回 JSON 包含内核数和连接数：

```json
{
  "connections": 0,
  "kernels": 0,
  "started": "2024-01-01T00:00:00Z",
  "last_activity": "2024-01-01T00:00:00Z"
}
```

## 停止服务器

在终端中按 `Ctrl+C` 停止服务器。
