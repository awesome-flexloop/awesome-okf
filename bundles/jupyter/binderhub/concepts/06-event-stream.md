---
type: Concept
title: "SSE 事件流：BuildHandler 构建处理器"
description: "深入解析 BinderHub 的 Server-Sent Events (SSE) 事件流实现，包括 BuildHandler 的连接建立与验证、keep-alive 保活机制、镜像存在性检查、构建提交与事件处理循环、JWT 构建 Token 验证、速率限制、配额检查、JupyterHub 启动流程、master/main→HEAD 回退逻辑以及 Prometheus 指标采集。"
tags: [binderhub, sse, server-sent-events, event-stream, buildhandler, tornado, jwt, ratelimit, quota, prometheus]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T20:45:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/binderhub/binderhub/
---

# SSE 事件流：BuildHandler 构建处理器

## 概述

BuildHandler 定义在 [builder.py](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py) 中，是 BinderHub 最核心的 HTTP 请求处理器。它通过 **Server-Sent Events (SSE)** 协议向浏览器客户端实时推送构建和启动进度。当用户点击"launch"按钮时，前端 JavaScript 代码通过 `EventSource` API 连接到 `/build/<provider>/<spec>` 端点，BuildHandler 负责完整的构建生命周期：仓库引用解析、镜像缓存检查、镜像构建、JupyterHub 服务器启动，全程通过 SSE 推送状态事件。

## SSE 协议基础

Server-Sent Events 是一种基于 HTTP 的单向实时通信协议，服务器通过持续的 HTTP 响应流向客户端推送事件。与 WebSocket 不同，SSE 是单向的（服务器→客户端），使用简单的文本格式：

```
data: {"phase": "waiting", "message": "Waiting for build to start...\n"}\n\n
```

每条事件以 `data: ` 开头，以两个换行符 `\n\n` 结束。SSE 天然支持自动重连，这是 BinderHub 选择它的关键原因之一。

## BuildHandler 类结构

BuildHandler 继承自 `BaseHandler`（[base.py](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/base.py)），获得了 JupyterHub OAuth 认证、IP 黑名单检查、速率限制、构建 Token 验证等基础能力。

```python
class BuildHandler(BaseHandler):
    """A handler for working with GitHub."""
    KEEPALIVE_INTERVAL = 25
    build = None
    spec_prefix = "/build/"
```

### 类级常量

| 常量 | 值 | 说明 |
|---|---|---|
| `KEEPALIVE_INTERVAL` | `25` | keep-alive 注释行发送间隔（秒） |
| `spec_prefix` | `"/build/"` | 路由前缀标识 |

## Prometheus 指标

BuildHandler 定义了多个 Prometheus 指标用于监控构建和启动性能：

| 指标名 | 类型 | 标签 | 说明 |
|---|---|---|---|
| `binderhub_build_time_seconds` | Histogram | `status` | 构建耗时分布 |
| `binderhub_launch_time_seconds` | Histogram | `status`, `retries` | 启动耗时分布 |
| `binderhub_build_count` | Counter | `status`, `provider`, `repo` | 构建计数 |
| `binderhub_launch_count` | Counter | `status`, `provider`, `repo` | 启动计数 |
| `binderhub_inprogress_builds` | Gauge | - | 当前进行中的构建数 |
| `binderhub_inprogress_launches` | Gauge | - | 当前进行中的启动数 |
| `binderhub_builds_rejected` | Counter | `reason`, `spec`, `user_agent` | 被拒绝的构建请求计数 |

### Histogram 桶配置

构建和启动的时间特征差异很大，使用不同的桶配置：

```python
BUILD_BUCKETS = [60, 120, 300, 600, 1800, 3600, 7200, float("inf")]
LAUNCH_BUCKETS = [2, 5, 10, 20, 30, 60, 120, 300, 600, float("inf")]
```

构建时间桶从 1 分钟到 2 小时（构建可能非常慢），启动时间桶从 2 秒到 10 分钟（启动通常较快）。

## HTTP 响应头设置

`set_default_headers()` 方法在每个请求开始时设置 SSE 必要的响应头：

```python
def set_default_headers(self):
    super().set_default_headers()
    self.set_header("content-type", "text/event-stream")
    self.set_header("cache-control", "no-cache")
```

| 头部 | 值 | 说明 |
|---|---|---|
| `Content-Type` | `text/event-stream` | 标识 SSE 事件流 |
| `Cache-Control` | `no-cache` | 禁止中间代理缓存事件 |

## prepare()：请求预检

`prepare()` 是 Tornado 提供的请求预处理钩子，在 `get()` 之前执行，用于验证请求合法性：

```python
async def prepare(self):
    super().prepare()

    # 验证 Accept 头
    accept_header = self.request.headers.get("Accept", "")
    accept = {s.strip().lower() for s in accept_header.split(",")}

    # User-Agent 机器人检测
    user_agent = self.request.headers.get("User-Agent", "")
    block_build_user_agents = self.settings.get("block_build_user_agents", [])
    for pattern in block_build_user_agents:
        if pattern.match(user_agent):
            self._record_rejected_build(reason="user_agent", ...)
            raise HTTPError(403, "Bots not allowed")

    if "text/event-stream" not in accept:
        self._record_rejected_build(reason="accept_header", ...)
        raise HTTPError(400, "Missing Accept header: text/event-stream")
```

### 预检检查项

1. **User-Agent 黑名单**：使用配置的正则模式列表匹配 User-Agent，阻止 bot、crawler、spider、gpt 等自动客户端触发构建；
2. **Accept 头验证**：确保客户端明确请求 `text/event-stream` 内容类型，防止普通浏览器导航直接访问端点。

### 重定向禁用

```python
def redirect(self, *args, **kwargs):
    # disable redirect to login, which won't work for EventSource
    raise HTTPError(403)
```

EventSource API 无法处理 HTTP 重定向（特别是 OAuth 登录重定向），因此直接禁用重定向，返回 403 错误通过 SSE 事件传递。

## emit()：事件发送核心方法

```python
async def emit(self, data):
    """Emit an eventstream event"""
    if type(data) is not str:
        serialized_data = json.dumps(data)
    else:
        serialized_data = data
    try:
        self.write(f"data: {serialized_data}\n\n")
        await self.flush()
    except StreamClosedError:
        app_log.warning(
            "Stream closed while handling %s, ip=%s, user_agent=%r",
            self.request.uri, self.request.remote_ip,
            self.request.headers.get("User-Agent", None),
        )
        raise Finish()
```

关键细节：
- 非字符串数据自动序列化为 JSON；
- 严格遵循 SSE 格式：`data: {json}\n\n`；
- `await self.flush()` 确保事件立即发送到客户端（不等缓冲区满）；
- 捕获 `StreamClosedError`（客户端断开连接），记录详细日志（IP、User-Agent）后通过 `raise Finish()` 终止处理器。

## keep_alive()：连接保活机制

```python
async def keep_alive(self):
    self._keepalive = True
    while True:
        await asyncio.sleep(self.KEEPALIVE_INTERVAL)
        if not self._keepalive:
            return
        try:
            self.write(":keepalive\n\n")
            await self.flush()
        except (StreamClosedError, RuntimeError):
            return
```

SSE 注释行（以 `:` 开头的行）会被 EventSource 客户端忽略，不会触发事件回调。每 25 秒发送一次 keepalive 注释，防止中间代理（Nginx、ELB 等）因连接空闲而超时断开。选择 25 秒是因为很多代理默认 30 秒空闲超时，留出 5 秒余量。

### on_finish()：清理

```python
def on_finish(self):
    """Stop keepalive when finish has been called"""
    self._keepalive = False
    if self.build:
        self.build.stop()
```

当请求结束时（正常完成或客户端断开），停止 keepalive 循环并通知构建执行器停止监听日志。这确保不会泄漏线程和资源。

## send_error()：SSE 错误传递

```python
def send_error(self, status_code, **kwargs):
    """event stream cannot set an error code, so send an error event"""
    self.set_status(status_code)
    exc_info = kwargs.get("exc_info")
    message = ""
    if exc_info:
        message = self.extract_message(exc_info)
    if not message:
        message = responses.get(status_code, "Unknown HTTP Error")
    evt = json.dumps({
        "phase": "failed",
        "status_code": status_code,
        "message": message + "\n",
    })
    self.write(f"data: {evt}\n\n")
    self.finish()
```

由于 SSE 响应已经开始发送 `text/event-stream` 内容，无法通过常规 HTTP 状态码报告错误。`send_error()` 重写了 Tornado 默认行为，将错误信息包装为 `phase: "failed"` 的 SSE 事件发送给前端。

## get()：主处理方法

`get()` 方法（[builder.py:322-676](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L322-L676)）是整个构建流程的主入口，使用 `@authenticated` 装饰器保护。

### 1. Token 与限流验证

```python
build_token = self.get_argument("build_token", None)
self.check_build_token(build_token, f"{provider_prefix}/{spec}")
self.check_rate_limit()
```

- **build_token**：JWT 格式的一次性令牌，由前端页面生成，防止跨站请求伪造（CSRF）和直接 API 滥用；
- **rate_limit**：基于 IP 的速率限制，防止单个客户端短时间内触发大量构建。

### 2. Provider 实例化与黑名单检查

```python
if provider_prefix not in self.settings["repo_providers"]:
    await self.fail(f"No provider found for prefix {provider_prefix}")
    return
provider = self.get_provider(provider_prefix, spec=spec)
if provider.is_banned():
    await self.emit({"phase": "failed", "message": f"Sorry, {spec} is not allowed..."})
    return
```

### 3. Ref 解析与 master/main→HEAD 回退

```python
ref = await provider.get_resolved_ref()
if ref is None:
    error_message = [f"Could not resolve ref for {key}."]
    if provider.name == "GitHub":
        if provider.unresolved_ref in {"master", "main"}:
            # GitHub 默认分支从 master 改为 main 的回退逻辑
            pre_ref_spec, _ = spec.rsplit("/", 1)
            spec = f"{pre_ref_spec}/HEAD"
            provider = self.get_provider(provider_prefix, spec=spec)
            await self.emit({
                "phase": "waiting",
                "message": "Trying again with HEAD instead of master/main...\n",
            })
            await asyncio.sleep(10)  # 人工延迟，提示用户更新链接
            ref = await provider.get_resolved_ref()
```

当用户使用 `master` 或 `main` 作为分支名但解析失败时（可能仓库已更改默认分支名），BinderHub 会自动回退到 `HEAD`（始终解析为仓库默认分支），并在重试前发送提示消息和 10 秒延迟，鼓励用户更新链接。

### 4. 镜像名与构建名生成

```python
safe_build_slug = _safe_build_slug(
    provider.get_build_slug(), limit=255 - len(image_prefix)
)
build_name = _generate_build_name(
    provider.get_build_slug(), ref, prefix="build-"
)
image_name = "{prefix}{build_slug}:{ref}".format(
    prefix=image_prefix, build_slug=safe_build_slug, ref=ref
).replace("_", "-").lower()
```

镜像名规则：
- 最大 255 字符（Docker 镜像名限制）；
- 使用 `_safe_build_slug()` 将任意字符串转为安全格式（小写字母、数字、连字符）+ 哈希后缀；
- 所有下划线替换为连字符（Docker 镜像名不允许下划线）；
- 构建名（Pod 名）最大 63 字符（Kubernetes DNS 限制），格式为 `build-<slug>-<ref-hash>`。

### 镜像名解析辅助函数

```python
def _get_image_basename_and_tag(full_name):
    tag_splits = full_name.rsplit(":", 1)
    if len(tag_splits) == 2:
        image_name = tag_splits[0]
        tag = tag_splits[1]
    else:
        image_name = full_name
        tag = "latest"
    if re.fullmatch("[a-z0-9]{4,40}/[a-z0-9._-]{2,255}", image_name):
        return image_name, tag  # Docker Hub 格式
    image_basename = "/".join(image_name.split("/")[1:])
    return image_basename, tag
```

区分 Docker Hub 镜像（`user/repo:tag`）和其他注册表镜像（`registry.example.com/user/repo:tag`），正确提取镜像名和标签。

### 5. 镜像缓存检查

#### 注册表模式（use_registry=True）

```python
if self.settings["use_registry"]:
    for _ in range(3):  # 最多重试 3 次
        try:
            image_manifest = await self.registry.get_image_manifest(
                image_without_tag, image_tag
            )
            image_found = bool(image_manifest)
            break
        except HTTPClientError:
            app_log.exception("Failed to get image manifest for %s", image_name)
            image_found = False
```

通过 Docker Registry V2 API 检查镜像 manifest 是否存在，失败最多重试 3 次。

#### 本地 Docker 模式（use_registry=False）

```python
else:
    docker_client = docker.from_env(version="auto")
    try:
        docker_client.images.get(image_name)
    except docker.errors.ImageNotFound:
        image_found = False
    else:
        image_found = True
```

单节点开发模式下，直接通过 Docker SDK 检查本地镜像。

### 6. build_only API 模式

```python
def _get_build_only(self):
    enable_api_only_mode = self.settings.get("enable_api_only_mode", False)
    build_only_query_parameter = str(
        self.get_query_argument(name="build_only", default="")
    )
    build_only = False
    if build_only_query_parameter.lower() == "true":
        if not enable_api_only_mode:
            raise HTTPError(400, "build_only requires enable_api_only_mode=True")
        build_only = True
    return build_only
```

当 `enable_api_only_mode=True` 且客户端传递 `build_only=true` 时，只构建镜像不启动服务器，适用于 API 集成场景（如 CI/CD 预构建）。

### 7. 镜像已存在：直接启动

```python
if image_found:
    if build_only:
        await self.emit({
            "phase": "ready",
            "imageName": image_name,
            "message": "Done! Found built image\n",
        })
    else:
        await self.emit({
            "phase": "built",
            "imageName": image_name,
            "message": "Found built image, launching...\n",
        })
        with LAUNCHES_INPROGRESS.track_inprogress():
            await self.launch(provider)
        self.emit_launch_event(provider, spec, ref)
    return
```

如果镜像已存在，跳过构建阶段直接启动（或在 build_only 模式下直接返回 ready）。

### 8. 配额检查

```python
try:
    await self.check_quota(provider)
except LaunchQuotaExceeded:
    return
```

在开始新构建前检查配额，防止系统过载。

### 9. 构建提交与事件循环

```python
q = Queue()
BuildClass = self.settings.get("build_class")
build = BuildClass(
    parent=self.settings["traitlets_parent"],
    q=q,
    name=build_name,
    repo_url=repo_url,
    ref=ref,
    image_name=image_name,
    git_credentials=provider.git_credentials,
)
if self.settings["use_registry"]:
    push_token = await self.registry.get_credentials(image_without_tag, image_tag)
    if push_token:
        build.registry_credentials = push_token
self.build = build
```

实例化构建执行器，传入 tornado Queue 用于接收进度事件，配置动态推送凭证（如果注册表支持）。

#### 构建任务提交

```python
with BUILDS_INPROGRESS.track_inprogress():
    done = False
    failed = False

    def _check_result(future):
        nonlocal done, failed
        try:
            r = future.result()
        except Exception:
            app_log.error("Build task failed", exc_info=True)
            done = True
            failed = True
            build.progress(LOG_MESSAGE, json.dumps({
                "phase": "failed",
                "message": "Unhandled error watching for build events.\n",
            }))

    build_starttime = time.perf_counter()
    pool = self.settings["build_pool"]
    submit_future = pool.submit(build.submit)
    submit_future.add_done_callback(_check_result)
```

构建的 `submit()` 方法在 `build_pool` 线程池中执行（不阻塞 Tornado 事件循环）。`_check_result` 回调处理构建线程中的未捕获异常，确保主线程事件循环能收到失败通知。

#### 初始等待事件

```python
await self.emit({
    "phase": "waiting",
    "message": "Waiting for build to start...\n",
})
```

#### 事件处理主循环

```python
while not done:
    progress = await q.get()
    if progress.kind == ProgressEvent.Kind.BUILD_STATUS_CHANGE:
        phase = progress.payload.value
        if progress.payload == ProgressEvent.BuildStatus.PENDING:
            continue  # Pod 等待调度，无需特殊处理
        elif progress.payload == ProgressEvent.BuildStatus.BUILT:
            if build_only:
                event = {"phase": "ready", "message": "Done! Image built\n", "imageName": image_name}
            else:
                event = {"phase": "built", "message": "Built image, launching...\n", "imageName": image_name}
            BUILD_TIME.labels(status="success").observe(time.perf_counter() - build_starttime)
            BUILD_COUNT.labels(status="success", ...).inc()
            done = True
        elif progress.payload == ProgressEvent.BuildStatus.RUNNING:
            # Pod 开始运行，启动日志流式获取
            if log_future is None:
                log_future = pool.submit(build.stream_logs)
                log_future.add_done_callback(_check_result)
            continue
        elif progress.payload == ProgressEvent.BuildStatus.FAILED:
            event = {"phase": phase}
        elif progress.payload == ProgressEvent.BuildStatus.UNKNOWN:
            event = {"phase": phase}
    elif progress.kind == ProgressEvent.Kind.LOG_MESSAGE:
        event = progress.payload
        payload = json.loads(event)
        if payload.get("phase") in ("failure", "failed"):
            failed = True
            BUILD_TIME.labels(status="failure").observe(...)
            BUILD_COUNT.labels(status="failure", ...).inc()
    await self.emit(event)
```

事件循环处理两种事件类型：
- **BUILD_STATUS_CHANGE**：状态机转换，PENDING→继续等待，RUNNING→启动日志流，BUILT→完成构建并启动服务器，FAILED→标记失败；
- **LOG_MESSAGE**：直接转发 repo2docker 的 JSON 日志给前端展示，检测到 `phase: "failure"` 时记录失败指标。

### 10. 启动 JupyterHub 服务器

构建成功后（或镜像已存在时），调用 `launch()` 方法与 JupyterHub API 交互：

```python
async def launch(self, provider):
    quota_check = await self.check_quota(provider)
    await self.emit({"phase": "launching", "message": "Launching server...\n"})

    launcher = self.settings["launcher"]
    retry_delay = launcher.retry_delay
    for i in range(launcher.retries):
        if self.settings["auth_enabled"]:
            user_model = self.hub_auth.get_user(self)
            username = user_model["name"]
            server_name = launcher.unique_name_from_repo(self.repo_url) if launcher.allow_named_servers else ""
        else:
            username = launcher.unique_name_from_repo(self.repo_url)
            server_name = ""
        try:
            async def handle_progress_event(event):
                await self.emit({"phase": "launching", "message": event["message"] + "\n"})

            extra_args = {
                "binder_ref_url": self.ref_url,
                "binder_launch_host": self.binder_launch_host,
                "binder_request": self.binder_request,
                "binder_persistent_request": self.binder_persistent_request,
                "binder_client_ip": client_ip,
            }
            server_info = await launcher.launch(
                image=self.image_name,
                username=username,
                server_name=server_name,
                repo_url=self.repo_url,
                extra_args=extra_args,
                event_callback=handle_progress_event,
            )
        except Exception as e:
            if i + 1 == launcher.retries:
                raise  # 最后一次重试失败，抛出异常
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # 指数退避
            continue
        else:
            break
    await self.emit({"phase": "ready", "message": f"server running at {server_info['url']}\n", **server_info})
```

启动流程特点：
- **重试机制**：最多重试 `launcher.retries` 次（默认 5 次），使用指数退避（retry_delay 倍增）；
- **临时用户**：`auth_enabled=False` 时，基于 repo_url 哈希生成唯一临时用户名；
- **认证模式**：`auth_enabled=True` 时，使用已登录用户的用户名，支持命名服务器（每个仓库一个独立服务器名）；
- **进度回调**：Launcher 通过 `event_callback` 推送启动进度事件。

### 11. 事件上报与延迟关闭

```python
self.emit_launch_event(provider, spec, ref)
await asyncio.sleep(60)
```

启动成功后：
1. 向 EventLog 发送 `binderhub.jupyter.org/launch` 事件，记录提供者、spec、ref、状态、来源等信息；
2. **等待 60 秒**再关闭连接。这是因为 EventSource 客户端会在连接断开后自动重连，如果服务端先关闭连接，客户端会重连并可能触发新的构建。等待 60 秒让行为良好的客户端（在收到 ready 事件后主动关闭连接）先断开。

## emit_launch_event()：活动事件上报

```python
def emit_launch_event(self, provider, spec, ref):
    host = self.settings["normalized_origin"] or self.request.host
    request_origin = self.request.headers.get("Origin")
    if request_origin is None:
        request_origin = self.request.headers.get("Sec-Fetch-Site", "")
    self.event_log.emit("binderhub.jupyter.org/launch", 6, {
        "provider": provider.name,
        "spec": spec,
        "ref": ref,
        "status": "success",
        "build_token": self._have_build_token,
        "origin": host,
        "request_origin": request_origin,
    })
```

事件 schema 版本为 6，包含完整的启动上下文信息，用于活动审计和使用分析。

## check_quota()：配额验证

```python
async def check_quota(self, provider):
    repo_config = provider.repo_config(self.settings)
    launch_quota = self.settings["launch_quota"]
    try:
        return await launch_quota.check_repo_quota(self.image_name, repo_config, self.repo_url)
    except LaunchQuotaExceeded as e:
        LAUNCH_COUNT.labels(status=e.status, **self.repo_metric_labels).inc()
        await self.fail(e.message)
        raise
```

配额检查使用 provider 的 repo_config（包含 per-repo 配额设置），由 LaunchQuota 实现类执行实际检查（KubernetesLaunchQuota 查询当前运行的 Pod 数量）。

## 被拒绝构建记录

`_record_rejected_build()` 方法在各种拒绝场景中调用，记录详细日志和 Prometheus 指标：

```python
def _record_rejected_build(self, reason, msg=""):
    provider_id, spec = self.get_spec_from_request()
    spec = f"{provider_id}/{spec}"
    user_agent = self.request.headers.get("User-Agent", "")
    ip = self.request.remote_ip
    app_log.warning(
        "Rejecting build: %s reason=%s spec=%s ip=%s user_agent=%r",
        msg, reason, spec, ip, user_agent,
    )
    BUILDS_REJECTED.labels(reason=reason, spec=spec, user_agent=user_agent).inc()
```

拒绝原因（reason）包括：
- `banned_ip`：IP 在黑名单网络中；
- `rate_limit`：超过速率限制；
- `banned_repo`：仓库被黑名单禁止；
- `user_agent`：User-Agent 匹配机器人模式；
- `accept_header`：缺少正确的 Accept 头。

## SSE 事件阶段总览

前端通过监听 `phase` 字段判断当前状态：

| phase | 说明 | 典型动作 |
|---|---|---|
| `waiting` | 等待构建开始 / 重试提示 | 显示等待消息 |
| `running`/`<repo2docker-phase>` | 构建进行中（来自 repo2docker 日志） | 显示构建日志 |
| `built` | 镜像构建完成，开始启动 | 切换到启动状态 |
| `launching` | 正在启动 JupyterHub 服务器 | 显示启动进度 |
| `ready` | 服务器就绪 | 重定向到 JupyterHub |
| `failed` | 构建/启动失败 | 显示错误信息 |

repo2docker 的 JSON 日志中可能出现的 phase 值由 repo2docker 自身定义，通常包括：`fetching`、`building`、`pushing` 等。

## 前端连接示例

前端 JavaScript 使用 EventSource 连接：

```javascript
// 注意：EventSource 不支持自定义 headers，build_token 通过 URL 参数传递
const eventSource = new EventSource(
    `/build/gh/user/repo/main?build_token=${token}`
);

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.phase) {
        case 'waiting':
            updateStatus('Waiting for build to start...');
            break;
        case 'built':
            updateStatus('Build complete! Launching...');
            break;
        case 'ready':
            eventSource.close();
            window.location.href = data.url;
            break;
        case 'failed':
            showError(data.message);
            eventSource.close();
            break;
        default:
            // 追加构建日志
            appendLog(data.message);
    }
};

eventSource.onerror = () => {
    // EventSource 自动重连，无需手动处理
};
```

## 关键源码引用

- BuildHandler 类定义：[builder.py:149-858](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L149-L858)
- emit() 方法：[builder.py:157-176](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L157-L176)
- keep_alive() 方法：[builder.py:185-201](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L185-L201)
- send_error() 方法：[builder.py:203-223](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L203-L223)
- prepare() 预检：[builder.py:299-319](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L299-L319)
- get() 主处理方法：[builder.py:322-676](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L322-L676)
- launch() 启动方法：[builder.py:734-858](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L734-L858)
- emit_launch_event()：[builder.py:678-705](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L678-L705)
- 镜像名辅助函数：[builder.py:66-87](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L66-L87)
- 构建名生成函数：[builder.py:90-147](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L90-L147)
- Prometheus 指标定义：[builder.py:30-63](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py#L30-L63)
