---
okf_version: "0.2"
type: example
title: "配置认证：避免速率限制"
description: "通过服务端配置 Access Token、GitHub Enterprise 部署配置、SSL 证书设置等完整认证配置流程"
tags: [authentication, access-token, rate-limit, github-enterprise, ssl, security, configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: init-py
    resource: "/references/init-py-source.md"
    title: "服务端扩展源码"
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-github/README.md"
    title: "README.md"
---

# 配置认证：避免速率限制

本示例演示如何正确配置 jupyterlab-github 的认证，避免 GitHub API 速率限制，以及如何配置 GitHub Enterprise 支持。

## 方式一：服务端 Access Token（推荐）

这是最安全、最推荐的方式。

### 步骤 1：获取 Personal Access Token

1. 登录 GitHub
2. 进入 Settings → Developer settings → Personal access tokens
3. 点击 "Generate new token (classic)"
4. 设置 Note（描述），选择 Expiration（过期时间）
5. 勾选 **repo** 权限范围（访问私有仓库需要）
6. 点击 "Generate token"，**立即复制**生成的 token（格式：`ghp_xxxxxxxxxx`）

### 步骤 2：生成 Jupyter 配置文件

如果还没有 Jupyter 配置文件：

```bash
jupyter server --generate-config
```

这会在 `~/.jupyter/jupyter_server_config.py` 生成配置文件。

### 步骤 3：配置 Token

编辑 `~/.jupyter/jupyter_server_config.py`，添加：

```python
c.GitHubConfig.access_token = 'ghp_your_actual_token_here'
```

### 步骤 4：重启 JupyterLab

```bash
jupyter lab
```

进入 GitHub 浏览器，浏览几个仓库后，打开浏览器开发者工具（F12）→ Network 面板，观察到 `/github/` 请求的响应正常，不再出现 403 限流错误。

### 验证 Token 是否生效

在 GitHub 浏览器中输入你自己的用户名，如果你有私有仓库，应该能看到它们出现在仓库列表中（因为 Token 带有 repo 权限）。如果 Token 未生效，你只能看到公开仓库。

## 方式二：客户端 Access Token（不推荐）

仅在你无法配置服务端（如使用托管 JupyterHub 但无管理员权限）时使用。

### 配置步骤

1. 获取 Personal Access Token（同方式一步骤1）
2. 在 JupyterLab 中打开 Settings → Advanced Settings Editor → GitHub
3. 在 User Preferences 中输入：

```json
{
  "accessToken": "ghp_your_token_here"
}
```

4. 保存设置
5. 会弹出安全警告对话框，点击 PROCEED 继续

### 安全风险

- Token 存储在 JupyterLab 设置中（浏览器 localStorage/服务端设置存储）
- 如果存在 XSS 漏洞，Token 可能被窃取
- 默认情况下服务端会拒绝客户端 Token（返回 403 错误）

如果需要启用客户端 Token 支持，服务端需额外配置：

```python
c.GitHubConfig.allow_client_side_access_token = True
```

## 配置 GitHub Enterprise

如果你的组织使用 GitHub Enterprise 部署：

### 服务端配置

```python
# jupyter_server_config.py
c.GitHubConfig.api_url = 'https://github.yourcompany.com/api/v3'
c.GitHubConfig.access_token = 'your_ghe_token_here'

# 如果 GHE 使用自签名证书，可临时关闭 SSL 验证（不推荐生产环境）
# c.GitHubConfig.validate_cert = False
```

### 前端配置

在 JupyterLab Advanced Settings 中：

```json
{
  "baseUrl": "https://github.yourcompany.com"
}
```

## 环境变量方式（可选）

如果你不想把 Token 直接写在配置文件中，可以通过环境变量传递：

```python
# jupyter_server_config.py
import os
c.GitHubConfig.access_token = os.environ.get('GITHUB_ACCESS_TOKEN', '')
```

然后启动时设置环境变量：

```bash
export GITHUB_ACCESS_TOKEN=ghp_your_token
jupyter lab
```

## 验证安装和配置

### 检查服务端扩展状态

```bash
jupyter server extension list
```

应看到：
```
- Validating jupyterlab_github...
     jupyterlab_github 4.0.0 OK
```

### 检查配置是否加载

在 JupyterLab 中打开一个终端，运行：

```bash
jupyter server --show-config | grep -i github
```

或者在 Python 中验证：

```python
from jupyterlab_github import GitHubConfig
c = GitHubConfig()
print(c.access_token)  # 应输出你的 token（非空）
print(c.api_url)       # 应输出 https://api.github.com 或你的 GHE URL
```

## 速率限制参考

| 认证方式 | 速率限制 | 适用场景 |
|---------|---------|---------|
| 无认证 | 60次/小时 | 快速浏览，很快会被限流 |
| 服务端 Token | 5000次/小时 | **推荐**，日常使用足够 |
| OAuth App（已废弃） | 5000次/小时 | 不推荐，将被移除 |
| GitHub Enterprise | 按实例配置 | 私有部署 |

## 常见问题

**Q: 配置了 Token 仍然被限流？**
A: 检查：
1. Token 是否有效（不过期、未被撤销）
2. Token 是否有 `repo` 权限
3. 重启 JupyterLab 使配置生效
4. 检查浏览器控制台是否有错误信息

**Q: 出现 SSL 证书验证错误？**
A: 如果使用 GitHub Enterprise 且有自签名证书，可以临时设置 `c.GitHubConfig.validate_cert = False`，但最好将公司 CA 证书添加到系统信任链中。

**Q: 如何撤销 Token？**
A: 在 GitHub Settings → Developer settings → Personal access tokens 中找到对应 Token，点击 Delete。

---

**相关概念**：
- [配置与设置系统](/concepts/06-configuration.md) — 所有配置项完整参考
- [服务端代理与认证](/concepts/05-server-proxy.md) — Token 处理机制详解
- [基础浏览示例](01-basic-browsing.md) — 配置后的基本使用流程
