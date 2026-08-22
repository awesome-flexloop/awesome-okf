---
type: Example
title: 基础部署示例
description: 从零开始创建一个包含xeus-python内核的JupyterLite站点并部署到静态文件服务器
tags: [deploy, getting-started, xeus-python, static-site]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /examples/basic-deploy.md
    title: README.md usage section
  - id: getting-started
    resource: /concepts/01-getting-started.md
    title: 快速开始
---

## 目标

创建一个最小可用的 JupyterLite 站点，包含 xeus-python 内核，可以部署到任意静态文件服务器。

## 前置条件

- Python 3.10+
- pip
- 网络连接（首次构建需要下载micromamba和conda包）

## 步骤

### 步骤1：创建项目目录

```bash
mkdir my-jupyterlite-site
cd my-jupyterlite-site
```

### 步骤2：安装依赖

```bash
pip install jupyterlite-core jupyterlite-xeus
```

验证安装：

```bash
jupyter lite --version
# 应输出 0.7.x 或 0.8.x
```

### 步骤3：创建默认环境配置（可选）

创建 `environment.yml` 来预装常用包：

```yaml
name: xeus-python-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-python
  - numpy
  - pandas
  - matplotlib-base
```

> 如果不创建environment.yml，默认会安装xeus-python（通过REQUIRED_PACKAGES）。

### 步骤4：构建站点

```bash
jupyter lite build
```

首次构建需要几分钟——会自动下载micromamba、创建emscripten-wasm32 conda环境、安装包、empack打包。

构建完成后，`_output/` 目录包含所有静态文件。

### 步骤5：本地预览

```bash
jupyter lite serve
```

打开浏览器访问 `http://localhost:8000`。

> 注意：`jupyter lite serve` 使用的开发服务器可能不发送COOP/COEP头，会以comlink模式运行。这在开发时完全正常。

验证功能：
1. 点击 Launcher 中的 "Python (XPython)" 创建Notebook
2. 执行 `print("Hello from xeus-python!")`
3. 执行 `import numpy as np; np.array([1,2,3])` 验证numpy可用
4. 执行 `import pandas as pd; pd.DataFrame({'a':[1,2,3]})` 验证pandas可用

### 步骤6：部署到静态服务器

**方式A：GitHub Pages**

```bash
# 安装ghp-import
pip install ghp-import

# 将_output目录推送到gh-pages分支
ghp-import -n -p -f _output
```

在GitHub仓库Settings→Pages中选择gh-pages分支作为源。

**方式B：Nginx**

```nginx
server {
    listen 80;
    server_name jupyterlite.example.com;
    root /var/www/jupyterlite/_output;
    index index.html;

    # 推荐：启用crossOriginIsolated获得更好性能
    add_header Cross-Origin-Opener-Policy "same-origin" always;
    add_header Cross-Origin-Embedder-Policy "require-corp" always;
    add_header Cross-Origin-Resource-Policy "cross-origin" always;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**方式C：本地快速测试（Python HTTP Server）**

```bash
cd _output
python -m http.server 8080
```

> Python http.server不发送COOP/COEP头，使用comlink模式。

## 构建产物结构

构建后的 `_output/` 目录应包含：

```
_output/
├── index.html
├── jupyterlite/
├── lab/                    # JupyterLab界面
├── repl/                   # REPL界面
├── xeus/
│   ├── kernels.json
│   ├── kernels/
│   │   └── xpython/        # xeus-python内核文件
│   └── xpython/
│       └── kernel_packages/  # empack打包的conda包
├── files/                  # 用户文件目录
└── api/
```

## 常见问题排查

### 构建失败：micromamba下载超时

设置环境变量使用本地micromamba：

```bash
# 先手动下载micromamba到本地
export JUPYTERLITE_MICROMAMBA_PATH=/path/to/micromamba
jupyter lite build
```

### 内核启动失败：WASM文件404

检查构建输出中的xeus目录结构是否完整：

```bash
ls _output/xeus/kernels/xpython/
# 应包含 xpython.js, xpython.wasm, xpython.data, kernel.json
```

如果缺少文件，可能是构建过程中copy_xpython_static步骤失败。检查构建日志中是否有ELF文件复制相关的错误。

### Notebook中无法导入包

包必须在environment.yml中声明并通过conda安装（构建时预装）或通过%conda install运行时安装。pip只能安装纯Python包。

## 下一步

- 自定义预装包：→ [自定义环境示例](custom-env.md)
- 生产环境优化：→ [生产部署示例](advanced-deploy.md)
- 了解构建过程：→ [构建系统详解](../concepts/05-build-system.md)
