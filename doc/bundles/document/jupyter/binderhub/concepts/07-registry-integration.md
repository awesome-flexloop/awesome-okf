---
type: Concept
title: "Docker Registry 镜像注册表集成"
description: "深入解析 BinderHub 与 Docker Registry V2 API 的集成机制，包括 DockerRegistry 类的认证流程（Bearer Token 与 Basic Auth）、docker config.json 凭证解析、WWW-Authenticate 头处理、get_image_manifest() 镜像检查流程、GoogleArtifactRegistry 的 GCE 元数据服务器认证、FakeRegistry 测试桩，以及 ExternalRegistryHelper 微服务集成（自动创建仓库和动态推送令牌）。"
tags: [binderhub, docker, registry, oci, authentication, bearer-token, google-artifact-registry, oauth2, container-registry]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T20:45:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/binderhub/binderhub/
---

# Docker Registry 镜像注册表集成

## 概述

BinderHub 的注册表集成系统定义在 registry.py 中，负责与 Docker Registry V2 API 交互以检查镜像是否已存在、获取认证令牌以及管理推送凭证。该系统采用可扩展的类层次结构，支持 Docker Hub、Google Artifact Registry、Oracle Cloud Infrastructure Registry (OCIR) 等多种注册表实现，同时提供测试用的 `FakeRegistry` 和基于微服务的 `ExternalRegistryHelper` 用于复杂场景。

## 模块常量

```python
DEFAULT_DOCKER_REGISTRY_URL = "https://registry-1.docker.io"
DEFAULT_DOCKER_AUTH_URL = "https://index.docker.io/v1/"
```

Docker Hub 使用分离的注册表 URL 和认证 URL：实际镜像存储在 `registry-1.docker.io`，但认证配置键使用 `index.docker.io/v1/`（旧版 v1 注册表遗留约定）。

## 类继承体系

```
LoggingConfigurable
    └── DockerRegistry              # 基础注册表类
        ├── GoogleArtifactRegistry  # Google Artifact Registry (GCE 元数据认证)
        ├── FakeRegistry            # 测试用空注册表
        └── ExternalRegistryHelper  # 外部微服务辅助注册表
```

## DockerRegistry 基础类

`DockerRegistry`（registry.py:20-341）是所有注册表实现的基类，封装了 Docker Registry V2 HTTP API 的认证和镜像查询逻辑。

### 核心 Traitlets 属性

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `url` | `Unicode` | 从 docker config.json 或 `DEFAULT_DOCKER_REGISTRY_URL` | 注册表 V2 API URL |
| `auth_config_url` | `Unicode` | 自动检测 | docker config.json 中查找凭证的 URL 键 |
| `docker_config_path` | `Unicode` | `~/.docker/config.json`（尊重 `$DOCKER_CONFIG`） | Docker 客户端配置文件路径 |
| `token_url` | `Unicode` | 自动检测（Docker Hub/gcr.io 内置支持） | OAuth2 Bearer Token 获取端点 |
| `username` | `Unicode` | 从 docker config.json 解析 | Basic Auth 用户名 |
| `password` | `Unicode` | 从 docker config.json 解析 | Basic Auth 密码 |
| `not_found_401` | `Bool` | Docker Hub 为 True，其他为 False | 注册表是否对不存在的镜像返回 401 而非 404 |

### Docker Config 加载与凭证解析

`_load_docker_config()` 方法（registry.py:110-117）在类实例化时自动加载 Docker 配置文件：

```python
@default("_docker_config")
def _load_docker_config(self):
    if not os.path.exists(self.docker_config_path):
        self.log.warning("No docker config at %s", self.docker_config_path)
        return {}
    self.log.info("Loading docker config %s", self.docker_config_path)
    with open(self.docker_config_path) as f:
        return json.load(f)
```

Docker config.json 的典型格式：

```json
{
    "auths": {
        "https://index.docker.io/v1/": {
            "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="
        }
    }
}
```

`auth` 字段是 `username:password` 的 base64 编码。用户名和密码通过以下方式解析：

```python
@default("username")
def _default_username(self):
    b64_auth = None
    if self.auth_config_url in self._docker_config.get("auths", {}):
        b64_auth = self._docker_config["auths"][self.auth_config_url].get("auth")
    if not b64_auth:
        return ""
    return base64.b64decode(b64_auth.encode("utf-8")).decode("utf-8").split(":", 1)[0]

@default("password")
def _default_password(self):
    b64_auth = None
    if self.auth_config_url in self._docker_config.get("auths", {}):
        b64_auth = self._docker_config["auths"][self.auth_config_url].get("auth")
    if not b64_auth:
        return ""
    return base64.b64decode(b64_auth.encode("utf-8")).decode("utf-8").split(":", 1)[1]
```

解析流程：
1. 在 `auths` 字典中查找 `auth_config_url` 对应的条目；
2. 获取 `auth` 字段的 base64 编码字符串；
3. 解码后按第一个 `:` 分割，前半部分为用户名，后半部分为密码。

### URL 自动检测逻辑

#### url 默认值

```python
@default("url")
def _default_url(self):
    cfg = self._docker_config
    auths = cfg.get("auths", {})
    if not auths:
        return DEFAULT_DOCKER_REGISTRY_URL
    auth_config_url = next(iter(auths.keys()))
    if "://" not in auth_config_url:
        auth_config_url = "https://" + auth_config_url
    if auth_config_url == DEFAULT_DOCKER_AUTH_URL:
        return DEFAULT_DOCKER_REGISTRY_URL
    return auth_config_url
```

默认 URL 的选择逻辑：
1. 如果 docker config.json 没有 `auths` 配置，使用 Docker Hub 默认 URL；
2. 否则使用第一个 auth 条目的 URL；
3. 如果该 URL 是 Docker Hub 的 v1 auth URL（`index.docker.io/v1/`），映射到 v2 API URL（`registry-1.docker.io`）。

#### auth_config_url 默认值

```python
@default("auth_config_url")
def _auth_config_url_default(self):
    url = urlparse(self.url)
    auths = self._docker_config.get("auths", {})
    if self.url in auths:
        return self.url
    if url.hostname in auths:
        return url.hostname
    if ("." + url.hostname).endswith((".docker.io", ".docker.com")):
        return DEFAULT_DOCKER_AUTH_URL
    return self.url
```

按优先级匹配 docker config.json 中的凭证：
1. 完整 URL 匹配；
2. 仅主机名匹配（config.json 中常省略协议前缀）；
3. Docker Hub 特殊处理（映射到 v1 auth URL）；
4. 回退到使用 `url` 自身。

#### token_url 自动检测

```python
@default("token_url")
def _default_token_url(self):
    url = urlparse(self.url)
    if ("." + url.hostname).endswith(".gcr.io"):
        return "https://{0}/v2/token?service={0}".format(url.hostname)
    elif self.url.endswith(".docker.io"):
        return "https://auth.docker.io/token?service=registry.docker.io"
    else:
        return ""  # 需要通过 WWW-Authenticate 头动态发现
```

- **gcr.io**（Google Container Registry）：使用 `https://<hostname>/v2/token?service=<hostname>` 格式；
- **Docker Hub**：使用 `https://auth.docker.io/token?service=registry.docker.io`；
- **其他注册表**：返回空字符串，在首次请求时通过 `WWW-Authenticate` 响应头动态发现 token 端点。

### not_found_401：401 作为 404 处理

```python
@default("not_found_401")
def _default_not_found_401(self):
    return self.url.endswith(".docker.io")
```

Docker Hub 的一个特殊行为：当使用有效的 Bearer Token 请求不存在的私有仓库时，返回 401 Unauthorized 而非 404 Not Found。`not_found_401=True` 时，这种 401 被解释为"镜像不存在"。

> **注意**：这无法区分真正的权限不足和仓库不存在，但在 BinderHub 的使用场景中，token 是刚刚获取的有效 token，401 基本等同于"没有访问权限"即"不存在（对我们而言）"。

## Docker Registry V2 认证流程

Docker Registry V2 API 使用两种认证方式：

1. **Basic Authentication**：简单的用户名密码认证，适用于私有部署的简单注册表；
2. **Bearer Token (OAuth2)**：通过独立 token 端点获取短期令牌，Docker Hub、gcr.io、Quay.io、OCIR 等大多数云注册表使用此方式。

Bearer Token 认证流程（RFC 6750）：

```
客户端                         Registry                    Auth Service
  |                              |                             |
  |--- GET /v2/:image/manifests/:tag ->|                       |
  |<-- 401 Unauthorized -------------|                        |
  |    WWW-Authenticate: Bearer                                 |
  |    realm="https://auth.example.com/token",                  |
  |    service="registry.example.com",                          |
  |    scope="repository:image:pull"                             |
  |                                                            |
  |--- GET realm?service=...&scope=... (Basic Auth) ---------->|
  |<-- {"token": "..."} ----------------------------------------|
  |                                                            |
  |--- GET /v2/:image/manifests/:tag -------------------------->|
  |    Authorization: Bearer <token>                            |
  |<-- 200 OK (manifest JSON) ----------------------------------|
```

### _parse_www_authenticate_header()

```python
def _parse_www_authenticate_header(self, header):
    self.log.debug("Parsing WWW-Authenticate %r", header)
    if not header.lower().startswith("bearer "):
        raise ValueError(f"Only WWW-Authenticate Bearer type supported: {header}")
    try:
        realm = re.search(r'realm="([^"]+)"', header).group(1)
        service = re.search(r'service="([^"]*)"', header).group(1)
        scope = re.search(r'scope="([^"]*)"', header).group(1)
        return realm, service, scope
    except AttributeError:
        raise ValueError(
            f"Expected WWW-Authenticate to include realm service scope: {header}"
        ) from None
```

解析 WWW-Authenticate 响应头，提取三个关键参数：

| 参数 | 说明 |
|---|---|
| `realm` | Token 颁发服务的 URL |
| `service` | 注册表服务标识符 |
| `scope` | 请求的权限范围（如 `repository:library/ubuntu:pull`） |

头格式示例：

```
WWW-Authenticate: Bearer realm="https://auth.docker.io/token",service="registry.docker.io",scope="repository:jupyterhub/repo2docker:pull"
```

### _get_token()：获取 Bearer Token

```python
async def _get_token(self, client, token_url, service, scope):
    auth_req = httpclient.HTTPRequest(
        url_concat(token_url, {"scope": scope, "service": service}),
        auth_username=self.username,
        auth_password=self.password,
    )
    self.log.debug(f"Getting registry token from {token_url} service={service} scope={scope}")
    auth_resp = await client.fetch(auth_req)
    response_body = json.loads(auth_resp.body.decode("utf-8", "replace"))
    if "token" in response_body.keys():
        token = response_body["token"]
    elif "access_token" in response_body.keys():
        token = response_body["access_token"]
    else:
        raise ValueError(f"No token in response from registry: {response_body}")
    return token
```

向 token 端点发送 GET 请求，使用 Basic Auth（username/password）认证，返回的 JSON 中可能包含 `token` 或 `access_token` 字段（不同注册表实现差异），两者都作为 Bearer Token 使用。

### _get_image_manifest_from_www_authenticate()：完整握手流程

```python
async def _get_image_manifest_from_www_authenticate(self, client, www_auth_header, url):
    realm, service, scope = self._parse_www_authenticate_header(www_auth_header)
    token = await self._get_token(client, realm, service, scope)
    req = httpclient.HTTPRequest(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        resp = await client.fetch(req)
    except httpclient.HTTPError as e:
        if e.code == 404:
            return None
        else:
            raise
    return json.loads(resp.body.decode("utf-8"))
```

此方法实现完整的"收到 401 → 解析头 → 获取 token → 带 token 重发请求"流程。

### get_image_manifest()：镜像查询主入口

`get_image_manifest()` 方法（registry.py:272-333）是检查镜像是否存在的核心方法。

```python
async def get_image_manifest(self, image, tag):
    """
    Get the manifest for an image.
    Returns None if image doesn't exist, manifest dict if it does.
    """
    client = httpclient.AsyncHTTPClient()
    url = f"{self.url}/v2/{image}/manifests/{tag}"
    token = None
    headers = {"Accept": "application/vnd.oci.image.manifest.v1+json"}
```

> **Accept 头**：使用 `application/vnd.oci.image.manifest.v1+json` 请求 OCI 格式的 manifest，兼容 Docker V2 Schema 2 和 OCI Image Format。

#### 认证策略选择

```python
    if self.token_url:
        # 策略 1：已知 token_url，预先获取 Bearer Token
        token = await self._get_token(
            client,
            self.token_url,
            scope=f"repository:{image}:pull",
            service="container_registry",
        )
        req = httpclient.HTTPRequest(
            url,
            headers=headers | {"Authorization": f"Bearer {token}"},
        )
    else:
        # 策略 2：无已知 token_url，尝试 Basic Auth
        req = httpclient.HTTPRequest(
            url,
            headers=headers,
            auth_username=self.username,
            auth_password=self.password,
        )
```

两种初始策略：
1. **已知 token_url**（Docker Hub、gcr.io）：先获取 token，再带 Bearer 头请求；
2. **未知 token_url**（私有注册表）：先尝试 Basic Auth。

#### 响应处理与错误恢复

```python
    try:
        resp = await client.fetch(req)
    except httpclient.HTTPError as e:
        if e.code == 404:
            return None  # 镜像不存在
        elif e.code == 401 and token and self.not_found_401:
            # 已使用有效 token 但收到 401（Docker Hub 不存在镜像行为）
            self.log.debug("Interpreting 401 error as not found on %s:%s", image, tag)
            return None
        elif e.code == 401 and not token and "www-authenticate" in e.response.headers:
            # Basic Auth 失败但返回 WWW-Authenticate 头，切换到 Bearer Token 流程
            www_auth_header = e.response.headers["www-authenticate"]
            return await self._get_image_manifest_from_www_authenticate(
                client, www_auth_header, url
            )
        else:
            raise
    return json.loads(resp.body.decode("utf-8"))
```

错误处理优先级：
1. **404** → 镜像不存在，返回 `None`；
2. **401 + 已使用有效 token + not_found_401** → Docker Hub 式"不存在"，返回 `None`；
3. **401 + 未使用 token + WWW-Authenticate 头存在** → 动态发现 token 端点并执行 Bearer 握手；
4. 其他错误 → 抛出异常（触发 BuildHandler 中的重试逻辑）。

### get_credentials()：推送凭证钩子

```python
async def get_credentials(self, image, tag):
    """
    Return a dict of push credentials, or None if static credentials should be used.
    """
    return None
```

基类实现返回 `None`，表示使用静态配置的 `push_secret`。子类可重写此方法返回动态凭证（如短期 token），返回格式为：

```python
{
    "registry": "docker.io",
    "username": "user",
    "password": "temporary-token"
}
```

这些凭证通过 `CONTAINER_ENGINE_REGISTRY_CREDENTIALS` 环境变量传递给 repo2docker。

## GoogleArtifactRegistry

`GoogleArtifactRegistry`（registry.py:344-370）是为 Google Cloud Platform 的 Artifact Registry（以及 GCR）设计的子类，使用 GCE 元数据服务器自动获取服务账户令牌，无需手动配置凭证。

```python
class GoogleArtifactRegistry(DockerRegistry):
    @default("token_url")
    def _default_token_url(self):
        return "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"

    async def _get_token(self, client, token_url, service, scope):
        auth_req = httpclient.HTTPRequest(
            token_url, headers={"Metadata-Flavor": "Google"}
        )
        auth_resp = await client.fetch(auth_req)
        response_body = json.loads(auth_resp.body.decode("utf-8", "replace"))
        if "access_token" in response_body.keys():
            token = response_body["access_token"]
        else:
            raise ValueError(f"No token in response from registry: {response_body}")
        return token
```

关键差异：
- **token_url** 指向 GCE 元数据服务器（`metadata.google.internal`），而非注册表自身的 auth 端点；
- 请求必须包含 `Metadata-Flavor: Google` 头（GCE 元数据服务器的必需标识）；
- 不使用 username/password Basic Auth，元数据服务器通过 GCE 实例的服务账户自动授权；
- 返回的字段名为 `access_token`（而非 `token`）；
- 获取的 access_token 可直接作为 Bearer Token 访问 GCR/GAR。

> **注意**：此类仅在 BinderHub 运行在 GCE/GKE 环境中时有效，元数据服务器仅在 GCP 内部网络可访问。

## FakeRegistry：测试用空注册表

```python
class FakeRegistry(DockerRegistry):
    """Fake registry that contains no images"""
    async def get_image_manifest(self, image, tag):
        return None
```

`FakeRegistry` 始终返回 `None`，即所有镜像都"不存在"，强制每次请求都执行完整构建。用于测试和本地 UI 开发（与 `FakeBuild` 配合使用）。

配置示例：

```python
c.BinderHub.use_registry = True
c.BinderHub.registry_class = FakeRegistry
c.BinderHub.build_class = FakeBuild
c.BinderHub.builder_required = False
```

## ExternalRegistryHelper：外部微服务注册表

`ExternalRegistryHelper`（registry.py:382-478）通过一个辅助微服务（通常以 sidecar 形式部署在 BinderHub Pod 中）与注册表交互，解决某些云注册表需要动态创建仓库和短期推送令牌的问题。

### 配置属性

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `service_url` | `Unicode` | `"http://binderhub-container-registry-helper:8080"` | 辅助微服务 URL |
| `auth_token` | `Unicode` | 环境变量 `BINDERHUB_CONTAINER_REGISTRY_HELPER_AUTH_TOKEN` | 访问微服务的 Bearer Token |

### _request()：带认证的微服务调用

```python
async def _request(self, endpoint, **kwargs):
    client = httpclient.AsyncHTTPClient()
    repo_url = f"{self.service_url}{endpoint}"
    headers = {"Authorization": f"Bearer {self.auth_token}"}
    repo = await client.fetch(repo_url, headers=headers, **kwargs)
    return json.loads(repo.body.decode("utf-8"))
```

所有对微服务的请求都附带 Bearer Token 认证。

### get_image_manifest()：仓库自动创建

```python
async def get_image_manifest(self, image, tag):
    repo_url = f"/repo/{image}"
    try:
        repo_json = await self._request(repo_url)
    except httpclient.HTTPError as e:
        if e.code == 404:
            repo_json = None
        else:
            raise

    if repo_json:
        # 仓库存在，检查镜像
        return await self._get_image(image, tag)
    else:
        # 仓库不存在，自动创建
        self.log.debug(f"Creating repository: {repo_url}")
        await self._request(repo_url, method="POST", body="")
        return None
```

ExternalRegistryHelper 的特殊行为：
1. 首先检查仓库是否存在（`GET /repo/{image}`）；
2. 如果仓库不存在（404），自动发送 POST 请求创建仓库；
3. 仓库存在时，再检查具体镜像标签（`GET /image/{image}:{tag}`）。

这解决了某些注册表（如 OCIR）需要在推送镜像前显式创建仓库的问题。

### get_credentials()：动态推送令牌

```python
async def get_credentials(self, image, tag):
    token_url = f"/token/{image}:{tag}"
    try:
        token_json = await self._request(token_url, method="POST", body="")
    except httpclient.HTTPError as e:
        if e.code == 404:
            return None
        raise
    token = {
        k: v for (k, v) in token_json.items()
        if k in ["username", "password", "registry"]
    }
    return token
```

通过 POST 请求到微服务获取短期推送凭证。微服务负责与云供应商 API 交互生成有时效的令牌，避免在 BinderHub 配置中存储长期凭证。返回的字典只提取 `username`、`password`、`registry` 三个字段，传递给构建容器。

### 对 OCIR 等注册表的特殊处理

ExternalRegistryHelper 还负责处理镜像名称映射问题。例如 Oracle Cloud Infrastructure Registry (OCIR) 的镜像名格式为 `<tenancy-namespace>/<repo-name>:<tag>`，而 BinderHub 生成的镜像名可能包含额外的命名空间组件。辅助服务会自动处理这些差异，使 BinderHub 核心无需了解各注册表的命名规则。

## Accept 头与 OCI 兼容性

所有 manifest 请求都使用 OCI 标准 Accept 头：

```python
headers = {"Accept": "application/vnd.oci.image.manifest.v1+json"}
```

这确保了与以下注册表的兼容性：
- Docker Hub（支持 Docker Manifest V2 Schema 2 和 OCI）；
- Google Container Registry / Artifact Registry；
- Amazon ECR；
- Azure Container Registry；
- Quay.io；
- CNCF Harbor；
- 自建 Docker Registry v2。

较旧的 Docker V2 Schema 1 格式（`application/vnd.docker.distribution.manifest.v1+json`）已不再请求。

## 认证流程完整决策树

```
get_image_manifest(image, tag)
    │
    ├── token_url 已配置（Docker Hub/gcr.io/自定义）？
    │   ├── YES → _get_token() [使用配置的 token_url + Basic Auth]
    │   │         → GET manifest with Bearer token
    │   │         │
    │   │         ├── 200 → 返回 manifest JSON
    │   │         ├── 404 → 返回 None（镜像不存在）
    │   │         ├── 401 + not_found_401 → 返回 None（Docker Hub 式不存在）
    │   │         └── 其他错误 → 抛出异常
    │   │
    │   └── NO → GET manifest with Basic Auth
    │             │
    │             ├── 200 → 返回 manifest JSON
    │             ├── 404 → 返回 None
    │             ├── 401 + WWW-Authenticate 头存在
    │             │   → _parse_www_authenticate_header()
    │             │   → _get_token() [从 WWW-Authenticate 中的 realm 获取]
    │             │   → GET manifest with Bearer token
    │             │   ├── 200 → 返回 manifest JSON
    │             │   └── 404 → 返回 None
    │             └── 其他错误 → 抛出异常
    │
    └── ExternalRegistryHelper 子类
        ├── GET /repo/{image} → 检查仓库是否存在
        │   ├── 404 → POST /repo/{image}（创建仓库）→ 返回 None
        │   └── 200 → GET /image/{image}:{tag} → 返回 manifest 或 None
        └── get_credentials() → POST /token/{image}:{tag} → 返回临时凭证
```

## 配置示例

### Docker Hub 配置

```python
c.BinderHub.use_registry = True
c.BinderHub.image_prefix = "myuser/binder-"
# Docker Hub 凭证通过 ~/.docker/config.json 自动加载
```

### GCR/GAR 配置（在 GKE 上运行）

```python
c.BinderHub.use_registry = True
c.DockerRegistry.url = "https://gcr.io"
c.DockerRegistry.token_url = "https://gcr.io/v2/token?service=gcr.io"
c.BinderHub.image_prefix = "gcr.io/my-project/binder-"
```

或使用 GoogleArtifactRegistry 自动认证：

```python
c.BinderHub.registry_class = GoogleArtifactRegistry
c.BinderHub.image_prefix = "us-docker.pkg.dev/my-project/binder/"
```

### 私有注册表（Basic Auth）

```python
c.DockerRegistry.url = "https://registry.example.com"
c.DockerRegistry.username = "admin"
c.DockerRegistry.password = "secret"
c.DockerRegistry.token_url = ""  # 空字符串表示使用 Basic Auth
c.BinderHub.image_prefix = "registry.example.com/binder-"
```

### ExternalRegistryHelper 配置

```python
c.BinderHub.registry_class = ExternalRegistryHelper
c.ExternalRegistryHelper.service_url = "http://binderhub-container-registry-helper:8080"
c.ExternalRegistryHelper.auth_token = "my-helper-secret-token"
c.BinderHub.image_prefix = "ocir.io/my-tenancy/binder-"
```

## 关键源码引用

- DockerRegistry 基类：registry.py:20-341
- 模块常量：registry.py:16-17
- docker config 加载：registry.py:110-117
- WWW-Authenticate 解析：registry.py:209-225
- _get_token()：registry.py:227-251
- get_image_manifest()：registry.py:272-333
- GoogleArtifactRegistry：registry.py:344-370
- FakeRegistry：registry.py:373-379
- ExternalRegistryHelper：registry.py:382-478
