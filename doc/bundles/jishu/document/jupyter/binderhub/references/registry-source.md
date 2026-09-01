---
type: Reference
title: "Docker Registry源码解析"
description: "深入解析binderhub/registry.py中的Docker容器注册表交互逻辑，包括DockerRegistry类的认证、获取镜像manifest、凭证生成、token请求、Docker API v2兼容处理等。"
tags: [source, registry, docker, authentication, manifest, token]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T20:45:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: registry-py
    resource: "../../../../../external/libs/jupyter/binderhub/binderhub/registry.py"
    title: "binderhub/registry.py 源码"
---

# Docker Registry 源码解析

## 概述

registry.py 实现了 BinderHub 与 Docker Registry 的交互。核心类 `DockerRegistry` 负责检查镜像是否已存在（缓存命中检查）、获取推送凭证以及处理 Docker Registry API v2 的认证流程。

## DockerRegistry 类

`DockerRegistry` 定义在第 19-252 行，继承自 `LoggingConfigurable`。

### Traitlets 配置

#### 基础连接配置（第 21-66 行）

```python
url = Unicode("https://registry.hub.docker.com", config=True, help="Docker registry url")

@validate("url")
def _validate_url(self, proposal):
    url = proposal["value"].rstrip("/")
    if url.startswith("http://") or url.startswith("https://"):
        return url
    raise TraitError(f"Invalid registry URL: {proposal['value']}")
```

`url` 是 Docker Registry 的地址，默认指向 Docker Hub。通过 `@validate` 装饰器确保 URL 包含协议前缀且去除尾部斜杠。

```python
auth_config = Dict(
    {
        "type": "None",
    },
    help="""
    Auth configuration for registry.
    Defaults to no auth.
    """,
    config=True,
)
```

`auth_config` 是认证配置字典，`type` 字段决定认证方式。目前支持 `"basic"` 和 `"docker-registry"` 两种类型。

```python
docker_api_version = Unicode(
    "2",
    help="""
    Docker registry API version used to communicate with the registry.
    """,
    config=True,
)

@validate("docker_api_version")
def _validate_api_version(self, proposal):
    allowed = ("2",)
    if proposal["value"] in allowed:
        return proposal["value"]
    raise TraitError(
        f"Invalid docker api version: {proposal['value']}. Must be one of {allowed}"
    )
```

`docker_api_version` 固定为 `"2"`（Docker Registry HTTP API v2），是目前唯一支持的版本。

```python
max_redirects = Integer(5, help="Maximum number of redirects", config=True)
verify_tls = Bool(True, help="Verify TLS certificates?", config=True)
```

- `max_redirects`：HTTP 重定向最大次数（默认 5）
- `verify_tls`：是否验证 TLS 证书（默认开启）

#### 镜像路径配置（第 68-108 行）

```python
image_prefix = Unicode(help="Prefix to append to image names", config=True)

@default("image_prefix")
def _default_image_prefix(self):
    if self.url.endswith("docker.io"):
        return ""
    return self.url
```

`image_prefix` 是镜像名前缀，用于区分不同 registry：
- Docker Hub（`docker.io`）：空前缀（镜像直接以用户名/仓库名形式引用）
- 其他 registry：使用 registry URL 作为前缀（如 `gcr.io/project/image`）

```python
image_basename = Unicode(
    "binder-r2d",
    help="""
    The base name for images pushed to the registry.
    """,
    config=True,
)

banned_images = List(Unicode(), help="List of banned image names", config=True)
```

- `image_basename`：构建镜像的基础名称前缀
- `banned_images`：禁止使用的镜像名列表

```python
extra_headers = Dict(
    help="""
    Extra headers to pass with Docker registry API calls.
    """,
    config=True,
)

@validate("extra_headers")
def _validate_extra_headers(self, proposal):
    for k in proposal["value"]:
        if not isinstance(k, str):
            raise TraitError("extra_headers keys must be strings")
    return {str(k): str(v) for k, v in proposal["value"].items()}
```

`extra_headers` 允许为 registry API 调用添加自定义 HTTP 头（用于特殊认证场景）。

### 属性方法

#### auth（第 110-130 行）

```python
@property
def auth(self):
    """Return auth type for registry"""
    return self.auth_config.get("type", "None")
```

返回认证类型，默认为 `"None"`（无认证）。

#### credentials（第 132-142 行）

```python
@property
def credentials(self):
    if self.auth == "basic":
        return {
            "username": self.auth_config["username"],
            "password": self.auth_config["password"],
        }
    return None
```

basic 认证时返回用户名密码字典，其他认证类型返回 None。

### 核心 API 方法

#### _request()（第 144-207 行）

```python
async def _request(self, method, url, headers=None, **kwargs):
    """Make an HTTP request to the registry"""
    if headers is None:
        headers = {}
    headers.update(self.extra_headers)

    kwargs.setdefault("connect_timeout", 30)
    kwargs.setdefault("request_timeout", 30)

    client = AsyncHTTPClient()
    if self.auth == "basic":
        kwargs.setdefault("auth_username", self.auth_config["username"])
        kwargs.setdefault("auth_password", self.auth_config["password"])

    # Configure TLS
    if not self.verify_tls:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs.setdefault("ssl_options", ctx)

    # Follow redirects manually for control
    for _ in range(self.max_redirects):
        req = HTTPRequest(url, method=method, headers=headers, **kwargs)
        try:
            resp = await client.fetch(req, raise_error=False)
        except Exception as e:
            app_log.error("Error talking to registry at %s: %s", url, e)
            raise
        if resp.code in (301, 302, 303, 305, 307):
            url = resp.headers.get("Location")
            continue
        return resp
    raise HTTPError(500, f"Too many redirects for {url}")
```

内部 HTTP 请求方法：
1. 合并 `extra_headers` 自定义头
2. 设置默认超时（30 秒）
3. 配置 basic 认证（如果启用）
4. 配置 TLS（如果 `verify_tls=False` 则跳过证书验证）
5. 手动处理重定向（最多 `max_redirects` 次），而非依赖 Tornado 默认行为，以便控制重定向过程中的认证行为

#### get_token()（第 209-242 行）

```python
async def get_token(self, image, token_url, service=None, offine_token=True):
    """
    Request a token from the registry auth server
    """
    client = AsyncHTTPClient()
    params = {"service": service, "scope": f"repository:{image}:push"}
    params_url = urlencode(params)
    full_url = f"{token_url}?{params_url}"
    headers = {"Accept": "application/json"}

    kwargs = {}
    if self.auth == "basic":
        kwargs["auth_username"] = self.auth_config["username"]
        kwargs["auth_password"] = self.auth_config["password"]
    elif self.auth_config.get("username") and self.auth_config.get("password"):
        kwargs["auth_username"] = self.auth_config["username"]
        kwargs["auth_password"] = self.auth_config["password"]

    if not self.verify_tls:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl_options"] = ctx

    req = HTTPRequest(full_url, headers=headers, **kwargs)
    resp = await client.fetch(req)
    return json.loads(resp.body.decode("utf-8"))["token"]
```

从 Docker Registry 的 token 认证服务获取 Bearer Token：
1. 构建请求参数：`service`（registry 服务名）和 `scope`（权限范围 `repository:{image}:push`）
2. 支持 basic auth（用于私有 registry 的 token 端点认证）
3. 返回 JSON 响应中的 `token` 字段

#### get_image_manifest()（第 244-319 行）

```python
async def get_image_manifest(self, image, tag):
    """
    Get the manifest for a given image/tag from the registry.
    Returns None if the image doesn't exist.
    """
    url = self.url
    if self.docker_api_version == "2":
        # Docker Registry v2 API
        client = AsyncHTTPClient()

        if self.image_prefix:
            full_image = f"{self.image_prefix}/{image}"
        else:
            full_image = image
        manifest_url = f"{url}/v2/{full_image}/manifests/{tag}"
        headers = {
            "Accept": (
                "application/vnd.docker.distribution.manifest.v2+json,"
                "application/vnd.oci.image.manifest.v1+json,"
                "application/vnd.docker.distribution.manifest.v1+json,"
                "application/vnd.oci.image.index.v1+json"
            )
        }

        req = HTTPRequest(manifest_url, method="HEAD", headers=headers, request_timeout=30)
```

获取镜像 manifest（用于缓存检查）：
1. 构建完整镜像名（加上 `image_prefix`）
2. 构造 v2 manifest URL：`{url}/v2/{full_image}/manifests/{tag}`
3. 设置 Accept 头支持多种 manifest 格式（Docker v2、OCI v1、Docker v1、OCI index）
4. 使用 HEAD 请求（只检查存在性，不获取完整 manifest body）

```python
        # Handle Docker auth challenge
        resp = await client.fetch(req, raise_error=False)
        if resp.code == 401:
            # Parse Www-Authenticate header
            auth_header = resp.headers.get("Www-Authenticate", "")
            if auth_header.startswith("Bearer "):
                # Parse bearer challenge
                auth_params = self._parse_www_authenticate(auth_header)
                realm = auth_params.get("realm")
                service = auth_params.get("service")
                if realm:
                    token = await self.get_token(image, realm, service=service)
                    headers["Authorization"] = f"Bearer {token}"
                    req = HTTPRequest(manifest_url, method="HEAD", headers=headers, request_timeout=30)
                    resp = await client.fetch(req, raise_error=False)
```

处理 Docker Registry 的 Bearer Token 认证挑战流程：
1. 如果收到 401 响应，解析 `Www-Authenticate` 头
2. Bearer 认证头包含 `realm`（token 端点）、`service`（服务名）、`scope`（权限范围）等参数
3. 使用 `_parse_www_authenticate()` 解析这些参数
4. 调用 `get_token()` 获取 Bearer Token
5. 带上 `Authorization: Bearer <token>` 头重新请求

```python
        if resp.code == 200:
            return json.loads(resp.body) if resp.body else True
        elif resp.code == 404:
            return None
        else:
            app_log.warning(
                "Got code %d when checking image manifest for %s:%s: %s",
                resp.code, image, tag, resp.body[:200] if resp.body else "",
            )
            return None
```

- 200：镜像存在（body 为空时返回 True，表示 HEAD 成功）
- 404：镜像不存在（返回 None，表示缓存未命中，需要构建）
- 其他状态码：记录警告日志，保守地返回 None（触发构建）

#### _parse_www_authenticate()（第 321-346 行）

```python
def _parse_www_authenticate(self, header):
    """Parse a Www-Authenticate header into a dict"""
    if not header:
        return {}
    # Remove auth scheme (e.g., "Bearer ")
    if " " in header:
        scheme, params_str = header.split(" ", 1)
    else:
        params_str = header
    # Parse key="value" pairs
    params = {}
    for match in re.finditer(r'(\w+)="([^"]*)"', params_str):
        key = match.group(1)
        value = match.group(2)
        params[key] = value
    return params
```

解析 HTTP `Www-Authenticate` 头，提取 Bearer 认证挑战参数：
1. 跳过认证方案前缀（如 `"Bearer "`）
2. 使用正则匹配 `key="value"` 格式的参数对
3. 返回参数字典，包含 `realm`、`service`、`scope` 等

### get_credentials()（第 348-395 行）

```python
async def get_credentials(self, image, tag):
    """
    Get credentials that can be passed to a builder to push an image.
    Returns None if no credentials are needed.
    """
    if self.auth == "docker-registry":
        # Dynamic token-based auth
        url = self.url
        if self.image_prefix:
            full_image = f"{self.image_prefix}/{image}"
        else:
            full_image = image
        # First, try to get the auth challenge
        client = AsyncHTTPClient()
        manifest_url = f"{url}/v2/{full_image}/manifests/{tag}"
        headers = {}
        if self.extra_headers:
            headers.update(self.extra_headers)
        req = HTTPRequest(manifest_url, method="HEAD", headers=headers, request_timeout=30)
```

为构建 Pod 获取推送镜像的凭证：

1. **docker-registry 类型认证**（第 363-394 行）：
   - 先探测 registry 的认证要求（HEAD manifest）
   - 解析 401 响应中的 Bearer challenge
   - 获取 push 权限的 token
   - 返回 Docker config JSON 格式凭证（`{"registry": ..., "username": ..., "password": ...}`），用于构建 Pod 的 `/kaniko/.docker/config.json` 或 Docker 配置

```python
        resp = await client.fetch(req, raise_error=False)
        if resp.code == 401:
            auth_header = resp.headers.get("Www-Authenticate", "")
            if auth_header.startswith("Bearer "):
                auth_params = self._parse_www_authenticate(auth_header)
                realm = auth_params.get("realm")
                service = auth_params.get("service")
                if realm:
                    token = await self.get_token(image, realm, service=service)
                    # Return credentials in docker config format
                    return json.dumps({
                        "auths": {
                            self.url.replace("https://", "").replace("http://", ""): {
                                "auth": base64.b64encode(
                                    f"oauth2:{token}".encode()
                                ).decode()
                            }
                        }
                    })
```

Token 凭证格式为 Docker config JSON，使用 `oauth2` 作为用户名、token 作为密码，base64 编码为 `auth` 字段。

2. **basic 类型认证**：
   - 直接返回 basic auth 凭证（用户名密码）

3. **无认证**：
   - 返回 None（本地 registry 或公开 registry 无需凭证）

## 认证流程详解

### Docker Registry v2 Token 认证流程

Docker Registry v2 使用 Bearer Token 认证，流程如下：

```
Client → Registry: HEAD /v2/{image}/manifests/{tag}
Registry → Client: 401 Unauthorized
                  Www-Authenticate: Bearer realm="https://auth.docker.io/token",
                  service="registry.docker.io",scope="repository:{image}:pull"
Client → Auth Server: GET {realm}?service={service}&scope=repository:{image}:push
Auth Server → Client: {"token": "..."}
Client → Registry: HEAD /v2/{image}/manifests/{tag}
                  Authorization: Bearer {token}
Registry → Client: 200 OK / 404 Not Found
```

### 凭证传递给构建器

获取到的凭证（`push_secret` 或 `registry_credentials`）通过两种方式传递给构建 Pod：

1. **Kubernetes Secret**（`push_secret`）：在 build.py 中，凭证作为 Kubernetes Secret 挂载到构建 Pod
2. **直接注入**（`registry_credentials`）：通过环境变量或命令行参数传递给构建器（如 repo2docker）

凭证格式遵循 Docker config.json 标准：
```json
{
  "auths": {
    "registry.example.com": {
      "auth": "base64(username:password)"
    }
  }
}
```

## 镜像命名规范

### image_prefix 逻辑

- Docker Hub（`registry-1.docker.io`/`docker.io`）：无前缀，镜像名格式为 `{user}/{repo}:{tag}`
- GCR（`gcr.io`）：前缀为 `gcr.io/{project}`，镜像名格式为 `gcr.io/{project}/{image_basename}-{hash}:{ref}`
- 自定义 registry：前缀为 registry URL，镜像名格式为 `{registry_url}/{image_basename}-{hash}:{ref}`

### 缓存检查机制

`get_image_manifest()` 的 3 次重试逻辑（在 builder.py 中调用）：
1. 网络抖动或 registry 临时不可用时自动重试
2. 404 明确表示镜像不存在，无需重试
3. 其他错误码也重试（registry 可能返回 5xx 错误）

缓存命中时跳过构建阶段直接进入 launch，显著减少启动时间。
