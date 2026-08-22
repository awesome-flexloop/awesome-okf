---
type: Concept
title: 自定义 Demo 站点指南
description: 如何基于 JupyterLite Demo 模板自定义自己的 JupyterLite 站点，包括添加笔记本、安装扩展、定制主题、配置语言包等
tags: [customization, themes, extensions, language-packs, branding, site-customization]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: requirements
    resource: /references/requirements-source.md
    title: 依赖配置信源
  - id: config
    resource: /references/config-source.md
    title: 站点配置信源
---

## 自定义概览

基于 JupyterLite Demo 模板创建自己的站点，主要有以下自定义维度：

| 维度 | 修改位置 | 难度 | 效果 |
|------|----------|------|------|
| 添加内容 | content/ 目录 | ⭐ | 添加笔记本、数据文件 |
| 添加内核/扩展 | requirements.txt | ⭐ | 增加功能包 |
| 站点配置 | jupyter-lite.json | ⭐⭐ | 控制扩展启用/禁用、设置覆盖 |
| 主题定制 | requirements.txt + 配置 | ⭐⭐ | 更改外观 |
| 语言包 | requirements.txt | ⭐ | 界面国际化 |
| 部署配置 | .github/workflows/ | ⭐⭐ | CI/CD 流程 |
| 自定义扩展 | 开发 JupyterLab 扩展 | ⭐⭐⭐⭐ | 深度功能定制 |

## 添加内容

### 添加笔记本

将 `.ipynb` 文件放入 content/ 目录或其子目录即可。建议：

1. 按主题创建子目录（如 `content/tutorials/`、`content/examples/`）
2. 笔记本中的数据文件路径使用相对路径
3. 包含 `%pip install` 命令的笔记本，在开头标注需要的包

### 添加数据文件

将数据文件放入 `content/data/` 或其他目录，笔记本中通过相对路径读取：

```python
import pandas as pd
df = pd.read_csv('data/my-data.csv')  # 如果笔记本在 content/ 根目录
```

### 添加 README

Demo 在 CI 中将 README.md 复制到 content/。如果你的 README 不想出现在文件浏览器中，可以跳过此步骤或使用专门的 welcome 笔记本。

## 添加内核和扩展

### 安装额外内核

在 requirements.txt 中添加内核包即可：

```txt
# 添加 Xeus Python 内核
jupyterlite-xeus-python>=0.1.0
```

### 安装 JupyterLab 扩展

JupyterLab 扩展需要包含前端资源（prebuilt extension），通过 pip 安装：

```txt
# 常用扩展示例
jupyterlab-git>=0.50.0              # Git 集成
jupyterlab-drawio>=0.9.0            # draw.io 图表（Demo 中禁用了）
jupyterlab-code-formatter>=2.0.0    # 代码格式化
jupyterlab-execute-time>=3.0.0      # 执行时间显示
jupyterlab-variableInspector>=0.3.0 # 变量检查器
```

> ⚠️ **注意**：某些扩展可能与 JupyterLite 不兼容（依赖 Node.js 原生模块或服务器端 API）。安装后测试功能是否正常。

### 禁用不需要的扩展

在 jupyter-lite.json 中通过 `disabledExtensions` 禁用：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "disabledExtensions": [
      "@jupyterlab/drawio-extension",
      "jupyterlab-kernel-spy"
    ]
  }
}
```

## 主题定制

### 使用预构建主题

Demo 预装了两个暗色主题：`jupyterlab-night` 和 `jupyterlab_miami_nights`。更多主题可从 PyPI 安装：

```txt
# requirements.txt
jupyterlab-night          # 暗色主题
jupyterlab_miami_nights   # Miami Nights 主题
jupyterlab-theme-solaris-light  # 浅色主题（示例）
```

### 设置默认主题

通过 settingsOverrides 设置默认主题：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "settingsOverrides": {
      "@jupyterlab/apputils-extension:themes": {
        "theme": "JupyterLab Dark",
        "theme-scrollbars": true
      }
    }
  }
}
```

可用的主题名取决于安装的主题包。

## 语言包

### 安装语言包

JupyterLab 语言包以 `jupyterlab-language-pack-<locale>` 格式发布：

```txt
# requirements.txt
jupyterlab-language-pack-zh-CN    # 简体中文
jupyterlab-language-pack-fr-FR    # 法语
jupyterlab-language-pack-es-ES    # 西班牙语
jupyterlab-language-pack-de-DE    # 德语
jupyterlab-language-pack-ja-JP    # 日语
jupyterlab-language-pack-ko-KR    # 韩语
```

Demo 安装了中文和法语语言包。用户可以通过 JupyterLab 菜单 **Settings → Language** 切换语言。

## 站点品牌定制

### 修改应用名称和URL

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "My JupyterLite Site",
    "appVersion": "1.0.0"
  }
}
```

### 配置 baseUrl（部署到子路径）

如果部署到 `https://example.com/mylite/`，需要设置 baseUrl：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "baseUrl": "/mylite/"
  }
}
```

### 自定义 Favicon 和 Logo

可以通过编写自定义 JupyterLab 扩展来替换 favicon 和 logo，这需要前端开发。简单的方式是在构建后修改 dist/ 中的静态文件。

## Pyodide 配置

### 自定义 Pyodide CDN

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "litePluginSettings": {
      "@jupyterlite/pyodide-kernel-extension:kernel": {
        "pyodideUrl": "https://cdn.jsdelivr.net/pyodide/v0.28.0/full/pyodide.js"
      }
    }
  }
}
```

### 禁用持久化存储

对于公开演示站点，可以禁用文件持久化，每次刷新恢复初始状态：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "enableMemoryStorage": true
  }
}
```

## 构建命令高级选项

### 选择性构建应用

```bash
# 仅构建 lab 和 repl，跳过 tree 和 retro
jupyter lite build --contents content --output-dir dist --apps lab --apps repl
```

### 指定配置目录

```bash
# 使用自定义配置目录
jupyter lite build --lite-dir ./my-config --contents content --output-dir dist
```

## 本地开发工作流

1. Fork 或复制 jupyterlite/demo 仓库
2. 克隆到本地，安装依赖：`pip install -r requirements.txt`
3. 添加自定义内容和配置
4. 本地构建预览：`jupyter lite build --contents content --output-dir dist && jupyter lite serve --output-dir dist`
5. 验证功能正常后推送到 GitHub
6. 配置 GitHub Pages 使用 Actions 部署

## 相关概念

- [站点配置详解](/concepts/02-site-configuration.md)
- [Pyodide 生态库与 %pip 安装](/concepts/05-pyodide-libraries.md)
- [GitHub Pages 部署流水线](/concepts/06-deployment-github-pages.md)
- [从零部署实战](/examples/01-first-deployment.md)
- [自定义 Demo 站点实战](/examples/07-custom-demo-site.md)
