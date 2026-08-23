---
type: Concept
title: 安装与启用
description: pip/conda安装方法、JupyterLab 4.x与旧版本兼容、自动启用机制、手动启用命令、开发安装
tags: [jupyter-resource-usage, installation, pip, conda, jupyter-server-extension]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 安装与启用

## 使用 pip 安装

### JupyterLab 4.x / Notebook 7.x（推荐）

安装最新版本（>=1.0.0）以获得 JupyterLab 4 兼容性：

```bash
pip install jupyter-resource-usage
```

安装后扩展会**自动启用**，无需额外命令。重启 JupyterLab 即可在状态栏看到内存使用指标。

### JupyterLab 3.x / Notebook 6.x（旧版本）

对于旧版 Jupyter 环境，需要安装 <1.0.0 版本：

```bash
pip install 'jupyter-resource-usage<1.0.0'
```

## 使用 conda 安装

```bash
# JupyterLab 4.x
conda install -c conda-forge jupyter-resource-usage

# JupyterLab 3.x
conda install -c conda-forge 'jupyter-resource-usage<1.0.0'
```

## 自动启用机制

安装后，扩展通过 `jupyter-config/` 目录下的 JSON 配置文件实现自动启用：

**Jupyter Server 配置**（`jupyter_server_config.d/jupyter_resource_usage.json`）：

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "jupyter_resource_usage": true
    }
  }
}
```

**经典 Notebook 配置**（`jupyter_notebook_config.d/jupyter_resource_usage.json`）：

```json
{
  "NotebookApp": {
    "nbserver_extensions": {
      "jupyter_resource_usage": true
    }
  }
}
```

这些配置文件在wheel构建时被复制到 Jupyter 的配置目录（`etc/jupyter/`），Jupyter 启动时自动扫描加载。

### Lab 扩展自动发现

前端 Lab 扩展通过 `install.json` 和 `_jupyter_labextension_paths()` 钩子自动注册：

```python
def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "@jupyter-server/resource-usage"}]
```

wheel包中 `jupyter_resource_usage/labextension/` 目录包含预构建的前端资源（由 hatch-jupyter-builder 在构建时通过 `jlpm build:prod` 编译）。

## 手动启用（Notebook < 5.3）

如果使用 Notebook 版本 < 5.3（不支持自动发现），需要手动启用：

```bash
jupyter serverextension enable --py jupyter_resource_usage --sys-prefix
jupyter nbextension install --py jupyter_resource_usage --sys-prefix
jupyter nbextension enable --py jupyter_resource_usage --sys-prefix
```

## 验证安装

安装完成后，可以通过以下方式验证：

1. **启动 JupyterLab**：状态栏左侧应显示 "Mem: X.XX MB"
2. **检查API端点**：访问 `http://localhost:8888/api/metrics/v1`（需带认证token），应返回JSON格式的资源指标
3. **检查扩展列表**：
   ```bash
   jupyter serverextension list
   jupyter labextension list
   ```

## 前端三个插件的启用状态

安装后三个前端插件的默认行为不同：

| 插件 | 默认状态 | 启用方式 |
|------|:-------:|---------|
| 状态栏指标（status-item） | ✅ 自动启用 | 安装后即可见 |
| 顶栏监控（topbar-item） | ❌ 默认禁用 | Settings → Settings Editor → Resource Usage Indicator → 勾选"Enable resource usage indicators" |
| 内核侧边栏（kernel-panel-item） | ✅ 自动启用 | 右侧边栏转速表图标，Notebook 7中通过 View → Right Sidebar → Show Kernel Usage |

## 卸载

```bash
pip uninstall jupyter-resource-usage
# 或
conda remove jupyter-resource-usage
```

## 开发安装

如需从源码开发：

```bash
git clone https://github.com/jupyter-server/jupyter-resource-usage.git
cd jupyter-resource-usage

# 安装Python包（editable模式）
pip install -e ".[dev]"

# 安装前端依赖并链接
jlpm
jlpm build:prod
jupyter labextension develop --overwrite .
```

开发模式下可使用 `jlpm watch` 实时监听前端文件变更。

## 相关概念

- [简介与功能概述](00-introduction.md) — 了解扩展功能
- [架构总览](02-architecture.md) — 理解前后端架构
- [配置系统详解](05-configuration.md) — 安装后的配置选项
