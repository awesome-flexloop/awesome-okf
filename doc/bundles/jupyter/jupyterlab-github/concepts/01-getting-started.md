---
okf_version: "0.2"
type: concept
title: "安装与快速上手"
description: "安装 jupyterlab-github（pip 安装前后端双组件）、获取 GitHub Access Token、配置服务端认证、启动浏览"
tags: [installation, pip, access-token, configuration, quickstart, rate-limit, oauth]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-github/README.md"
    title: "README.md"
  - id: pyproject
    resource: "../../../../../external/libs/jupyter/jupyterlab-github/pyproject.toml"
    title: "pyproject.toml"
  - id: init-py
    resource: "/references/init-py-source.md"
    title: "服务端扩展源码"
  - id: drive-json
    resource: "../../../../../external/libs/jupyter/jupyterlab-github/schema/drive.json"
    title: "schema/drive.json"
---

# 安装与快速上手

## 安装

### JupyterLab 4.x（推荐）

使用 pip 一键安装前后端双组件：

```bash
pip install jupyterlab-github
```

此命令会同时安装：
- **Lab 扩展**（前端）：预编译的 JavaScript 包，自动注册到 JupyterLab
- **Server 扩展**（后端）：Python 包，自动启用 Jupyter Server 扩展

### JupyterLab 3.x

需要锁定版本为 3.0.1：

```bash
pip install 'jupyterlab-github==3.0.1'
```

### 验证安装

安装后重启 JupyterLab，运行以下命令验证服务端扩展是否启用：

```bash
jupyter server extension list
```

应看到：

```
- Validating jupyterlab_github...
     jupyterlab_github 4.0.0 OK
```

对于使用旧版 `notebook` 服务器（而非 `jupyter-server`）的环境（如旧版 JupyterHub）：

```bash
jupyter serverextension list
```

如果扩展未启用，手动启用：

```bash
jupyter server extension enable jupyterlab_github
```

## 获取 GitHub Access Token（推荐方式）

未认证请求的速率限制为每小时60次，实际使用中几分钟就会触发。强烈建议配置 Access Token。

### 步骤

1. 在 GitHub 上[验证邮箱地址](https://help.github.com/articles/verifying-your-email-address)
2. 进入 GitHub → Settings → Developer Settings → Personal access tokens
3. 点击 "Generate new token"，输入密码确认
4. 给 token 添加描述，勾选 **repo** 权限范围
5. 点击 "Generate token"，复制生成的 token 字符串

> ⚠️ **安全提示**：Access Token 相当于你的 GitHub 密码，不要分享给他人，不要提交到版本控制中。

### 配置到服务端（推荐）

生成 Jupyter Server 配置文件（如果没有）：

```bash
jupyter server --generate-config
```

编辑配置文件（通常在 `~/.jupyter/jupyter_server_config.py`），添加：

```python
c.GitHubConfig.access_token = 'ghp_your_token_here'
```

### 关于 OAuth App 方式（已废弃）

README 中也提到了注册 OAuth App 的方式，但已明确标记为 deprecated，未来版本将移除。新用户应使用 Access Token 方式。

## 启动浏览

1. 启动 JupyterLab：`jupyter lab`
2. 在左侧面板找到 GitHub 标签页（Octocat 图标）
3. 在顶部输入框中输入 GitHub 用户名或组织名，按 Enter
4. 点击仓库名进入仓库
5. 浏览文件、打开 Notebook 并运行

## 自定义默认仓库

可以通过 JupyterLab 设置面板配置启动时自动打开的仓库：

1. 打开 Settings → Advanced Settings Editor
2. 选择 "GitHub" 插件
3. 在 User Preferences 中添加：

```json
{
  "defaultRepo": "owner/repository"
}
```

其中 `owner` 是 GitHub 用户/组织名，`repository` 是仓库名。

## 速率限制说明

| 请求方式 | 速率限制 | 体验 |
|---------|---------|------|
| 无 Token 直连 | ~60次/小时 | 几分钟后被限流，需等待约1小时恢复 |
| 服务端 Token 代理 | ~5000次/小时 | 正常使用不受影响 |
| 客户端 Token（设置面板） | ~5000次/小时 | 可用，但有安全风险（token 存储在浏览器） |

**推荐始终配置服务端 Token**。如果在客户端设置面板中输入 Token，JupyterLab 会弹出安全警告对话框，提醒考虑使用服务端扩展方式。

## 启动参数

jupyterlab-github 安装后不添加独立的 CLI 命令，它通过 JupyterLab 的扩展机制自动加载。服务端扩展配置使用 traitlets 系统：

```python
# jupyter_server_config.py
c.GitHubConfig.access_token = 'ghp_xxx'       # Personal Access Token
c.GitHubConfig.api_url = 'https://api.github.com'  # GitHub API URL（可配置为 GitHub Enterprise）
c.GitHubConfig.validate_cert = True            # SSL 证书验证（生产环境保持 True）
c.GitHubConfig.allow_client_side_access_token = False  # 允许客户端 Token（不推荐）
```

---

**下一步阅读：**
- [架构总览](02-architecture-overview.md) — 理解双组件架构的设计思路
- [GitHubDrive 虚拟文件系统](03-github-drive.md) — 深入核心 Drive 实现
- [浏览器 UI 组件](04-browser-ui.md) — 了解界面交互逻辑
