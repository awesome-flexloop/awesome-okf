---
okf_version: "0.2"
type: concept
title: "配置与设置系统"
description: "JupyterLab 前端设置 Schema（baseUrl/accessToken/defaultRepo）、服务端 traitlets 配置项、GitHub Enterprise 支持与安全设置详解"
tags: [configuration, settings, schema, traitlets, access-token, github-enterprise, security, ssl, customization]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: drive-json
    resource: "../../../../../external/libs/jupyter/jupyterlab-github/schema/drive.json"
    title: "schema/drive.json"
  - id: init-py
    resource: "/references/init-py-source.md"
    title: "服务端扩展源码"
  - id: index-ts
    resource: "/references/index-ts-source.md"
    title: "插件入口源码"
  - id: contents-ts
    resource: "/references/contents-ts-source.md"
    title: "GitHub Drive 实现源码"
---

# 配置与设置系统

jupyterlab-github 提供两层配置：前端 JupyterLab 设置（用户可在 Settings 面板中修改）和后端 traitlets 配置（管理员在服务器配置文件中设置）。

## 前端设置（JupyterLab Settings）

前端设置通过 JSON Schema（`schema/drive.json`）定义，可在 JupyterLab 的 Settings → Advanced Settings Editor → GitHub 中配置。

### 设置项一览

| 设置键 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `baseUrl` | string | `'https://github.com'` | GitHub 网页基础 URL（用于"在GitHub打开"按钮） |
| `accessToken` | string | `''` | GitHub Personal Access Token（**有安全风险**） |
| `defaultRepo` | string | `''` | 启动时自动打开的仓库（格式：`'owner/repo'`） |

### baseUrl

设置 GitHub 的基础 URL，主要影响"在 GitHub 打开"按钮的链接构造。

- **默认值**：`https://github.com`（公开 GitHub）
- **GitHub Enterprise**：设置为你的 GHE 实例地址，如 `https://github.yourcompany.com`

> 注意：`baseUrl` 仅影响网页链接和前端 API 请求的地址。API 请求的地址在前端由 `DEFAULT_GITHUB_API_URL`（`https://api.github.com`）控制，直连模式下 API 请求始终发往 `api.github.com`。对于 GitHub Enterprise，需要同时配置服务端的 `api_url`。

### accessToken

客户端 Access Token 设置。此字段带有安全警告描述：

> "WARNING: For security reasons access tokens should be set in the server extension."

当用户在设置中输入 Token 时：
1. **首次加载**：不弹警告，直接应用 Token（`shouldWarn = false`）
2. **后续修改**：弹出安全警告对话框，提示使用服务端扩展更安全
3. 用户点击 CANCEL → 移除已输入的 Token
4. 用户点击 PROCEED → 应用 Token
5. 如果服务端设置了 `allow_client_side_access_token = False`（默认），代理请求会返回 403 错误，Token 不会生效

**推荐做法**：不在客户端设置 Token，而是配置服务端的 `c.GitHubConfig.access_token`。

### defaultRepo

设置 JupyterLab 启动时自动导航到的仓库。格式为 `'owner/repository'`。

```json
{
  "defaultRepo": "jupyterlab/jupyterlab-github"
}
```

启动后文件浏览器会自动执行 `cd('/jupyterlab/jupyterlab-github')`，直接展示该仓库根目录。

实现逻辑：
1. 设置加载后读取 `defaultRepo`
2. 等待 FileBrowser 模型恢复（`browser.model.restored`）
3. 执行 `browser.model.cd('/${defaultRepo}')`

## 服务端配置（traitlets）

服务端配置在 Jupyter Server 配置文件（通常是 `~/.jupyter/jupyter_server_config.py`）中设置，使用 `c.GitHubConfig.` 前缀。

### 配置项一览

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `access_token` | Unicode | `''` | GitHub Personal Access Token（**推荐方式**） |
| `api_url` | Unicode | `'https://api.github.com'` | GitHub API 端点（支持 GitHub Enterprise） |
| `allow_client_side_access_token` | Bool | `False` | 是否允许前端传递 Token |
| `validate_cert` | Bool | `True` | 是否验证 GitHub API 的 SSL 证书 |

### access_token（推荐）

在服务端配置文件中设置 Personal Access Token：

```python
c.GitHubConfig.access_token = 'ghp_your_token_here'
```

这是最安全的 Token 配置方式：
- Token 存储在服务器上，不暴露给浏览器
- 所有代理请求自动附加 Authorization 头
- 获得 5000次/小时的速率限制
- 支持私有仓库访问（如果 Token 有 repo 权限）

### api_url（GitHub Enterprise 支持）

如果使用 GitHub Enterprise 部署，设置为你的 GHE API 端点：

```python
c.GitHubConfig.api_url = 'https://github.yourcompany.com/api/v3'
```

同时需要设置前端的 `baseUrl` 为 GHE 网页地址。

### allow_client_side_access_token

控制是否接受前端传递的 Token：

```python
c.GitHubConfig.allow_client_side_access_token = True  # 不推荐
```

- `False`（默认）：前端传递的 Token 被拒绝，返回 403 错误
- `True`：允许使用前端 Token（安全风险：Token 可能被 XSS 窃取）

### validate_cert

控制是否验证 SSL 证书：

```python
c.GitHubConfig.validate_cert = False  # 仅用于自签名证书的内部环境
```

> ⚠️ 文档明确警告："In general this is a bad idea so only disable SSL validation if you know what you are doing!"

仅在使用自签名证书的 GitHub Enterprise 内部环境中才考虑关闭。

## 配置优先级

### Token 优先级（服务端）

当多个 Token 来源同时存在时，服务端按以下优先级选择：

1. **客户端 Token + 允许客户端 Token**：如果请求中带有 `access_token` 参数且 `allow_client_side_access_token=True`
2. **服务端配置 Token**：如果 `c.GitHubConfig.access_token` 非空（推荐）
3. **无 Token**：未认证请求（60次/小时限制）

### 请求路径选择（前端）

```
_useProxy Promise（构造时检测）
  ├─ true（代理可用）→ 请求发往 {serverBaseUrl}/github/...
  │   └─ accessToken 设置时追加 access_token 查询参数
  └─ false（代理不可用）→ 请求发往 https://api.github.com/...
      └─ 无认证头，受 60次/小时 限制
```

## 自动启用配置

pip 安装时，两个 JSON 配置文件被自动复制到 Jupyter 配置目录：

**Jupyter Server（jupyter-server）**：
```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "jupyterlab_github": true
    }
  }
}
```

**经典 Notebook Server（notebook<7）**：
```json
{
  "NotebookApp": {
    "nbserver_extensions": {
      "jupyterlab_github": true
    }
  }
}
```

这确保了安装后服务端扩展自动启用，无需手动执行 enable 命令。

## 刷新间隔设置

虽然不在 Settings Schema 中暴露，但 FileBrowser 的刷新间隔在代码中硬编码为 **5分钟**（300000ms），比本地文件浏览器的默认间隔长，目的是减少 API 请求、避免触发速率限制。

```typescript
const browser = factory.createFileBrowser(NAMESPACE, {
  driveName: drive.name,
  refreshInterval: 300000  // 5分钟
});
```

---

**相关概念**：
- [GitHubDrive 虚拟文件系统](03-github-drive.md) — 了解 Drive 如何使用这些配置
- [服务端代理与认证](05-server-proxy.md) — Token 处理和代理逻辑
