---
title: JupyterHub集成
type: concept
bundle: jupyter-notebook
okf-version: "0.2"
chapter: "07"
difficulty: intermediate
tags: ["backend", "jupyterhub", "authentication", "multi-user"]
prerequisites: ["02-backend-app", "04-handlers"]
sources: ["F-026"]
next: ["04-custom-auth"]
---

# 07 | JupyterHub集成

Jupyter Notebook v7 内置了对JupyterHub的原生支持，可以无缝运行在JupyterHub多用户环境中。

## JupyterHub与Notebook的关系

JupyterHub是Jupyter的多用户服务器，负责：
- 用户认证（OAuth、LDAP、GitHub等）
- 为每个用户启动独立的Notebook/JupyterLab实例
- 代理用户请求到对应的后端实例
- 资源管理和监控

当Notebook运行在JupyterHub下时，Hub作为反向代理位于用户浏览器和Notebook实例之间。

```
┌──────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Browser │ ──→ │  JupyterHub  │ ──→ │ Notebook Instance    │
│          │ ←── │  (Proxy/Auth)│ ←── │ (per-user container) │
└──────────┘     └──────────────┘     └─────────────────────┘
                  端口: 8000             端口: 随机(内部)
                  URL: /hub/             URL: /user/<username>/
```

## Hub环境检测

Notebook通过检查Tornado settings中的 `hub_prefix` 来判断是否运行在JupyterHub下：

```python
if "hub_prefix" in self.serverapp.tornado_settings:
    tornado_settings = self.serverapp.tornado_settings
    hub_prefix = tornado_settings["hub_prefix"]
    page_config["hubPrefix"] = hub_prefix
    page_config["hubHost"] = tornado_settings["hub_host"]
    page_config["hubUser"] = tornado_settings["user"]
    page_config["shareUrl"] = ujoin(hub_prefix, "user-redirect")
    if hasattr(self.serverapp, "server_name"):
        page_config["hubServerName"] = self.serverapp.server_name
    page_config["token"] = ""
```

> **信源**: [app.py:L334-348](file:///d:/spaces/SpecWeave/external/libs/jupyter/notebook/notebook/app.py#L334-L348)（F-026）

这些配置在Jupyter Server启动时由 `jupyterhub` 包或 `jupyter-server-proxy` 注入。

## page_config中的Hub字段

| 字段 | 说明 | 前端用途 |
|------|------|---------|
| `hubPrefix` | Hub的URL前缀（如 `/hub/`） | 构建Hub API URL |
| `hubHost` | Hub主机地址 | 跨Hub实例通信 |
| `hubUser` | 当前用户名 | 显示用户信息 |
| `shareUrl` | 用户重定向URL（如 `/hub/user-redirect/`） | 跨实例共享链接 |
| `hubServerName` | Hub服务器名称（JupyterHub 1.0+） | 识别Hub版本/实例 |

## 安全措施：Token清空

```python
page_config["token"] = ""
```

> **信源**: [app.py:L348](file:///d:/spaces/SpecWeave/external/libs/jupyter/notebook/notebook/app.py#L348)

**这是一个关键安全措施**：

在非Hub环境下，`token` 是用户访问Notebook的认证token，嵌入在page_config中供前端API调用使用。但在JupyterHub环境下：
- Hub通过Cookie/API Token统一管理认证
- Notebook实例的token是JupyterHub内部生成的，不应该暴露给浏览器
- 前端通过Hub代理发送请求，Hub自动处理认证

如果不将token设为空字符串，可能导致：
1. 内部token泄露给浏览器端代码
2. 跨用户token窃取风险
3. 认证绕过

## Hub环境下的认证流程

```
1. 用户访问 https://hub.example.com/
       │
       ▼
2. Hub检查Cookie → 未登录 → 重定向到登录页面
       │
       ▼
3. 用户输入凭证（OAuth/GitHub/LDAP/...）
       │
       ▼
4. Hub验证凭证 → 为用户启动Notebook实例（Docker/K8s Pod）
       │
       ▼
5. Hub代理用户请求到Notebook实例
   - 添加 X-JupyterHub-Session 等头信息
   - 设置 tornado_settings 中的 hub_* 变量
       │
       ▼
6. Notebook实例启动
   - 检测到 hub_prefix → Hub模式
   - page_config中token设为空
   - 前端通过Hub代理发起API请求
       │
       ▼
7. 请求经过Hub代理 → Hub验证Cookie → 转发到Notebook
```

## user-redirect机制

`shareUrl` 设为 `/hub/user-redirect`，这是JupyterHub的一个重要功能：

当用户A分享一个Notebook链接给用户B时（如 `https://hub.example.com/user/alice/notebooks/analysis.ipynb`），如果B点击这个链接：
1. Hub检测到B不是A → 重定向到 `/hub/user-redirect/notebooks/analysis.ipynb`
2. Hub查找B的Notebook实例
3. 将B重定向到自己的实例（`/user/bob/notebooks/analysis.ipynb`）

这需要B的实例中也存在同名文件（通常在共享卷中）。

## 部署配置示例

### Docker容器中运行在Hub下

```python
# jupyter_server_config.py (在Docker镜像中)
c.ServerApp.base_url = '/'  # Hub会通过JUPYTERHUB_SERVICE_PREFIX设置
c.ServerApp.allow_origin = '*'  # Hub代理处理CORS
c.ServerApp.disable_check_xsrf = True  # Hub处理CSRF
c.IdentityProvider.token = ''  # 不使用token认证，由Hub处理
```

### JupyterHub配置

```python
# jupyterhub_config.py
c.JupyterHub.spawner_class = 'docker'
c.DockerSpawner.image = 'jupyter/minimal-notebook:latest'
c.DockerSpawner.default_url = '/tree'  # Notebook默认使用/tree而非/lab
```

## 前端Hub集成

前端JupyterLab/Notebook检测到 `hubPrefix` 后会启用Hub相关功能：
- "Control Panel"按钮指向Hub控制面板
- "Logout"按钮登出Hub而非本地
- 文件共享使用shareUrl
- API请求自动处理Hub前缀

## 与其他部署方式的对比

| 特性 | 独立Notebook | JupyterHub | Jupyter Server + Notebook扩展 |
|------|-------------|-----------|------------------------------|
| 用户数 | 单用户 | 多用户 | 单用户 |
| 认证 | Token/密码 | OAuth/LDAP/SAML等 | Token/密码 |
| 进程管理 | 手动 | Hub自动Spawn | 手动 |
| URL前缀 | 无/自定义 | `/user/<name>/` | 无/自定义 |
| token暴露 | 在page_config中 | 清空（安全） | 在page_config中 |
| 适用场景 | 个人使用 | 教学/团队/企业 | 嵌入式集成 |

## 扩展开发注意事项

开发在Hub环境下运行的扩展时：

1. **不要依赖page_config.token**: Hub环境下token为空字符串，API请求通过Hub Cookie认证
2. **URL前缀处理**: 始终使用 `PageConfig.getBaseUrl()` 获取baseUrl，Hub环境下baseUrl是 `/user/<name>/`
3. **Hub API调用**: 可通过 `hubPrefix` 构建Hub API URL（如获取用户信息）
4. **跨实例场景**: 不要假设文件在所有用户实例中都存在

```typescript
import { PageConfig } from '@jupyterlab/coreutils';

const baseUrl = PageConfig.getBaseUrl();
const hubPrefix = PageConfig.getOption('hubPrefix');
const hubUser = PageConfig.getOption('hubUser');

if (hubPrefix) {
    // Hub环境
    console.log(`Running as ${hubUser} on Hub ${hubPrefix}`);
}
```

## 常见问题

### Q: 为什么Hub下访问Notebook显示403 Forbidden？

可能原因：
1. Hub API Token未正确配置（`JUPYTERHUB_API_TOKEN` 环境变量）
2. Notebook实例未注册到Hub
3. Cookie域配置不正确

### Q: 如何在Hub下同时启用Notebook和JupyterLab？

Notebook和JupyterLab都作为Jupyter Server扩展运行，Hub用户可以通过URL切换：
- `/user/<name>/tree` → Notebook界面
- `/user/<name>/lab` → JupyterLab界面

设置 `c.DockerSpawner.default_url = '/tree'` 或 `'/lab'` 控制默认界面。

### Q: Hub环境下自定义认证页面？

在Hub环境下，登录页面由JupyterHub控制，Notebook的登录页面不会显示。如需自定义登录，应自定义JupyterHub的认证模块（如自定义Authenticator），而非修改Notebook。

## 下一步

- → [实战：集成自定义认证](../examples/04-custom-auth.md) 开发自定义认证扩展
