---
type: Reference
title: "BuildHandler源码解析"
description: "深入解析binderhub/builder.py中的BuildHandler请求处理器，包括辅助函数、Prometheus指标定义、SSE事件流处理、构建流程控制、镜像缓存检查、启动JupyterHub服务器等完整逻辑。"
tags: [source, builder, handler, SSE, prometheus, build, launch]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T20:45:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: builder-py
    resource: "../../../../../external/libs/jupyter/binderhub/binderhub/builder.py"
    title: "binderhub/builder.py 源码"
---

# BuildHandler 源码解析

## 概述

[builder.py](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/builder.py) 实现了 BinderHub 的核心构建与启动处理器 `BuildHandler`。该模块包含辅助函数、Prometheus 指标定义以及基于 Server-Sent Events (SSE) 的构建流程控制。

## 辅助函数

### _get_image_basename_and_tag()（第 66-87 行）

```python
def _get_image_basename_and_tag(full_name):
    """Get a supposed image name and tag without the registry part"""
    tag_splits = full_name.rsplit(":", 1)
    if len(tag_splits) == 2:
        image_name = tag_splits[0]
        tag = tag_splits[1]
    else:
        image_name = full_name
        tag = "latest"

    if re.fullmatch("[a-z0-9]{4,40}/[a-z0-9._-]{2,255}", image_name):
        return image_name, tag
    image_basename = "/".join(image_name.split("/")[1:])
    return image_basename, tag
```

解析完整镜像名为不含 registry 的名称和 tag：
1. 使用 `rsplit(":", 1)` 从最后一个冒号分割镜像名和 tag
2. 如果没有冒号，tag 默认为 `"latest"`
3. 检查是否为 Docker Hub 格式的镜像名（`[a-z0-9]{4,40}/[a-z0-9._-]{2,255}`），如果是则直接返回
4. 否则去掉第一个路径段（registry 主机名），返回剩余部分

### _generate_build_name()（第 90-120 行）

```python
def _generate_build_name(build_slug, ref, prefix="", limit=63, ref_length=6):
    build_slug = _safe_build_slug(
        build_slug, limit=limit - len(prefix) - ref_length - 1
    )
    ref = _safe_build_slug(ref, limit=ref_length, hash_length=2)
    return "{prefix}{safe_slug}-{ref}".format(
        prefix=prefix,
        safe_slug=build_slug,
        ref=ref[:ref_length],
    ).lower()
```

生成符合 Kubernetes DNS 规范的构建名称（最长 63 字符，小写字母+数字+连字符）：
- `prefix`：前缀（如 `"build-"`）
- `build_slug`：仓库 slug，经过 `_safe_build_slug()` 安全转义
- `ref`：Git ref，截取前 `ref_length`（默认 6）个字符
- 格式：`{prefix}{safe_slug}-{ref}`，全部转小写

### _safe_build_slug()（第 123-146 行）

```python
def _safe_build_slug(build_slug, limit, hash_length=6):
    build_slug_hash = hashlib.sha256(build_slug.encode("utf-8")).hexdigest()
    safe_chars = set(string.ascii_letters + string.digits)

    def escape(s):
        return escapism.escape(s, safe=safe_chars, escape_char="-")

    build_slug = escape(build_slug)
    return "{name}-{hash}".format(
        name=build_slug[: limit - hash_length - 1],
        hash=build_slug_hash[:hash_length],
    ).lower()
```

创建 DNS 安全的 slug：
1. 使用 `escapism` 库将非安全字符转义为 `-` 前缀的形式
2. 对原始 slug 计算 SHA-256 哈希
3. 截断转义后的名称，附加哈希前缀作为碰撞保护
4. 最终格式：`{truncated_name}-{hash_prefix}`，全部小写
5. 此机制确保即使名称截断，仍可通过哈希区分不同的 slug

## Prometheus 指标定义

第 27-63 行定义了 BinderHub 的核心 Prometheus 指标：

### Histogram 直方图

```python
BUILD_BUCKETS = [60, 120, 300, 600, 1800, 3600, 7200, float("inf")]
LAUNCH_BUCKETS = [2, 5, 10, 20, 30, 60, 120, 300, 600, float("inf")]

BUILD_TIME = Histogram(
    "binderhub_build_time_seconds",
    "Histogram of build times",
    ["status"],
    buckets=BUILD_BUCKETS,
)

LAUNCH_TIME = Histogram(
    "binderhub_launch_time_seconds",
    "Histogram of launch times",
    ["status", "retries"],
    buckets=LAUNCH_BUCKETS,
)
```

- `BUILD_TIME`：构建时间直方图，标签为 `status`（success/failure），桶从 60 秒到 2 小时
- `LAUNCH_TIME`：启动时间直方图，标签为 `status` 和 `retries`（重试次数），桶从 2 秒到 10 分钟

### Counter 计数器

```python
BUILD_COUNT = Counter(
    "binderhub_build_count",
    "Counter of builds by repo",
    ["status", "provider", "repo"],
)

LAUNCH_COUNT = Counter(
    "binderhub_launch_count",
    "Counter of launches by repo",
    ["status", "provider", "repo"],
)

BUILDS_REJECTED = Counter(
    "binderhub_builds_rejected",
    "Counter of rejected build requests",
    ["reason", "spec", "user_agent"],
)
```

- `BUILD_COUNT`：构建计数，按状态/提供商/仓库维度
- `LAUNCH_COUNT`：启动计数，按状态/提供商/仓库维度
- `BUILDS_REJECTED`：被拒绝的构建请求计数，按原因/spec/UA 维度

### Gauge 仪表盘

```python
BUILDS_INPROGRESS = Gauge("binderhub_inprogress_builds", "Builds currently in progress")
LAUNCHES_INPROGRESS = Gauge(
    "binderhub_inprogress_launches", "Launches currently in progress"
)
```

- `BUILDS_INPROGRESS`：当前进行中的构建数
- `LAUNCHES_INPROGRESS`：当前进行中的启动数

使用 `track_inprogress()` 上下文管理器自动增减。

## BuildHandler 类

`BuildHandler` 定义在第 149-857 行，继承自 `BaseHandler`，实现了基于 SSE（Server-Sent Events）的构建和启动流程。

### 类属性（第 152-155 行）

```python
KEEPALIVE_INTERVAL = 25
build = None
spec_prefix = "/build/"
```

- `KEEPALIVE_INTERVAL`：保活间隔 25 秒，防止中间代理关闭空闲连接
- `build`：当前 BuildExecutor 实例
- `spec_prefix`：URL 路径前缀

### SSE 事件发送方法

#### emit()（第 157-176 行）

```python
async def emit(self, data):
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
            self.request.uri,
            self.request.remote_ip,
            self.request.headers.get("User-Agent", None),
        )
        raise Finish()
```

发送 SSE 事件，格式为 `data: {json}\n\n`。遇到连接关闭时记录日志（包含 IP 和 UA，用于分析 bot 流量）并抛出 `Finish()` 终止处理。

#### on_finish()（第 178-183 行）

```python
def on_finish(self):
    self._keepalive = False
    if self.build:
        self.build.stop()
```

请求结束时停止保活定时器，并通知构建执行器停止监听。

#### keep_alive()（第 185-201 行）

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

以 25 秒间隔发送 SSE 注释行（`:keepalive\n\n`），防止中间代理因空闲超时而关闭连接。SSE 中以 `:` 开头的行是注释，会被客户端忽略。

#### send_error()（第 203-223 行）

```python
def send_error(self, status_code, **kwargs):
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

重写 Tornado 的 `send_error`，因为 SSE 无法设置 HTTP 错误码。错误通过 SSE 事件以 `phase: "failed"` 形式发送，包含状态码和消息。

### 初始化与配置

#### initialize()（第 225-230 行）

```python
def initialize(self):
    super().initialize()
    if self.settings["use_registry"]:
        self.registry = self.settings["registry"]
    self.event_log = self.settings["event_log"]
```

从 settings 中获取 Registry 和 EventLog 实例。

#### set_default_headers()（第 240-244 行）

```python
def set_default_headers(self):
    super().set_default_headers()
    self.set_header("content-type", "text/event-stream")
    self.set_header("cache-control", "no-cache")
```

设置 SSE 必需的响应头：`Content-Type: text/event-stream` 和 `Cache-Control: no-cache`。

#### redirect()（第 265-267 行）

```python
def redirect(self, *args, **kwargs):
    raise HTTPError(403)
```

禁用重定向（如登录重定向），因为 EventSource API 无法处理重定向。

### 安全检查方法

#### _get_build_only()（第 246-263 行）

```python
def _get_build_only(self):
    enable_api_only_mode = self.settings.get("enable_api_only_mode", False)
    build_only_query_parameter = str(
        self.get_query_argument(name="build_only", default="")
    )
    build_only = False
    if build_only_query_parameter.lower() == "true":
        if not enable_api_only_mode:
            raise HTTPError(
                status_code=400,
                log_message="Building but not launching is not permitted when the API only mode was not enabled.",
            )
        build_only = True
    return build_only
```

解析 `build_only=true` 查询参数，仅在 API-only 模式下允许仅构建不启动。

#### check_request_ip()（第 269-274 行）

```python
def check_request_ip(self):
    try:
        super().check_request_ip()
    except HTTPError:
        self._record_rejected_build(reason="banned_ip")
        raise
```

覆盖基类 IP 检查，被拒绝时记录 `banned_ip` 原因。

#### check_rate_limit()（第 276-281 行）

```python
def check_rate_limit(self):
    try:
        super().check_rate_limit()
    except HTTPError:
        self._record_rejected_build(reason="rate_limit")
        raise
```

覆盖基类限流检查，被拒绝时记录 `rate_limit` 原因。

#### _record_rejected_build()（第 283-297 行）

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

记录被拒绝的构建请求到日志和 Prometheus 计数器。

#### prepare()（第 299-319 行）

```python
async def prepare(self):
    super().prepare()
    accept_header = self.request.headers.get("Accept", "")
    accept = {s.strip().lower() for s in accept_header.split(",")}
    user_agent = self.request.headers.get("User-Agent", "")
    block_build_user_agents = self.settings.get("block_build_user_agents", [])
    for pattern in block_build_user_agents:
        if pattern.match(user_agent):
            self._record_rejected_build(reason="user_agent", msg=f"user agent matching {pattern}")
            raise HTTPError(403, "Bots not allowed")
    if "text/event-stream" not in accept:
        self._record_rejected_build(reason="accept_header", msg=f"Accept={accept_header!r}")
        raise HTTPError(400, "Missing Accept header: text/event-stream")
```

请求预处理阶段：
1. 检查 User-Agent 是否匹配 bot 阻止模式（默认阻止 bot/gpt/crawler/spider）
2. 验证 Accept 头包含 `text/event-stream`，确保是真正的 EventSource 请求

#### fail()（第 232-238 行）

```python
async def fail(self, message):
    await self.emit({
        "phase": "failed",
        "message": message + "\n",
    })
```

发送失败事件的辅助方法。

### get() 主处理方法

`get()` 方法定义在第 321-857 行，使用 `@authenticated` 装饰器，是构建和启动流程的核心入口。

方法签名：
```python
@authenticated
async def get(self, provider_prefix, _unescaped_spec):
```

参数 `provider_prefix` 是仓库提供商前缀（如 `gh`），`_unescaped_spec` 是 URL 编码的 spec（但实际使用重新从路径提取的原始 spec）。

#### 阶段 1：Token 和限流验证（第 337-342 行）

```python
_, spec = self.get_spec_from_request()
build_token = self.get_argument("build_token", None)
self.check_build_token(build_token, f"{provider_prefix}/{spec}")
self.check_rate_limit()
```

从请求路径提取原始 spec（避免 Tornado 自动解码），验证 build_token 并检查限流。

#### 阶段 2：Provider 验证和实例化（第 347-362 行）

```python
if provider_prefix not in self.settings["repo_providers"]:
    await self.fail(f"No provider found for prefix {provider_prefix}")
    return

asyncio.create_task(self.keep_alive())
spec = spec.rstrip("/")
key = f"{provider_prefix}:{spec}"

try:
    provider = self.get_provider(provider_prefix, spec=spec)
except Exception as e:
    app_log.exception("Failed to get provider for %s", key)
    await self.fail(str(e))
    return
```

启动保活协程，实例化对应的 RepoProvider。

#### 阶段 3：禁止列表检查（第 364-372 行）

```python
if provider.is_banned():
    self._record_rejected_build(reason="banned_repo")
    await self.emit({
        "phase": "failed",
        "message": f"Sorry, {spec} is not allowed to launch. Please contact admins for more info!",
    })
    return
```

检查仓库是否在禁止列表中。

#### 阶段 4：Ref 解析（第 382-431 行）

```python
repo_url = self.repo_url = provider.get_repo_url()
self.repo_metric_labels = {
    "provider": provider.name,
    "repo": repo_url,
}

try:
    ref = await provider.get_resolved_ref()
except Exception as e:
    await self.fail(f"Error resolving ref for {key}: {e}")
    return
```

获取仓库 URL 并解析 ref 到 commit SHA。如果 ref 解析失败且是 GitHub 上的 master/main 分支，会尝试自动回退到 HEAD：

```python
if ref is None:
    error_message = [f"Could not resolve ref for {key}."]
    if provider.name == "GitHub":
        if provider.unresolved_ref in {"master", "main"}:
            # 提示 GitHub 已更改默认分支
            pre_ref_spec, _ = spec.rsplit("/", 1)
            spec = f"{pre_ref_spec}/HEAD"
            # 重新创建 provider 并尝试解析
            provider = self.get_provider(provider_prefix, spec=spec)
            ref = await provider.get_resolved_ref()
            # ... 发送等待消息，延迟 10 秒
            await asyncio.sleep(10)
```

#### 阶段 5：生成构建名称和镜像名（第 433-471 行）

```python
self.ref_url = await provider.get_resolved_ref_url()
resolved_spec = await provider.get_resolved_spec()

badge_base_url = self.get_badge_base_url()
self.binder_launch_host = badge_base_url or "{proto}://{host}{base_url}".format(
    proto=self.request.protocol, host=self.request.host, base_url=self.settings["base_url"],
)
self.binder_request = "v2/{provider}/{spec}".format(provider=provider_prefix, spec=spec)
self.binder_persistent_request = "v2/{provider}/{spec}".format(provider=provider_prefix, spec=resolved_spec)

image_prefix = self.settings["image_prefix"]
safe_build_slug = _safe_build_slug(provider.get_build_slug(), limit=255 - len(image_prefix))
build_name = _generate_build_name(provider.get_build_slug(), ref, prefix="build-")
image_name = self.image_name = "{prefix}{build_slug}:{ref}".format(
    prefix=image_prefix, build_slug=safe_build_slug, ref=ref
).replace("_", "-").lower()
```

设置徽章 URL、binder 请求路径，生成安全的构建名和镜像名。镜像名最长 255 字符，下划线替换为连字符，转小写。

#### 阶段 6：镜像缓存检查（第 473-498 行）

```python
image_without_tag, image_tag = _get_image_basename_and_tag(image_name)
if self.settings["use_registry"]:
    for _ in range(3):
        try:
            image_manifest = await self.registry.get_image_manifest(image_without_tag, image_tag)
            image_found = bool(image_manifest)
            break
        except HTTPClientError:
            app_log.exception("Failed to get image manifest for %s", image_name)
            image_found = False
else:
    docker_client = docker.from_env(version="auto")
    try:
        docker_client.images.get(image_name)
    except docker.errors.ImageNotFound:
        image_found = False
    else:
        image_found = True
```

检查镜像是否已存在：
- 使用 Registry 时，重试 3 次获取镜像 manifest
- 不使用 Registry 时（单节点模式），检查本地 Docker 镜像

#### 阶段 7：缓存命中路径（第 500-524 行）

```python
build_only = self._get_build_only()
if image_found:
    if build_only:
        await self.emit({"phase": "ready", "imageName": image_name, "message": "Done! Found built image\n"})
    else:
        await self.emit({"phase": "built", "imageName": image_name, "message": "Found built image, launching...\n"})
        with LAUNCHES_INPROGRESS.track_inprogress():
            try:
                await self.launch(provider)
            except LaunchQuotaExceeded:
                return
        self.emit_launch_event(provider, spec, ref)
    return
```

如果镜像已缓存：
- `build_only` 模式：直接发送 `ready` 事件
- 正常模式：发送 `built` 事件，然后调用 `launch()` 启动服务器

#### 阶段 8：配额检查（第 526-530 行）

```python
try:
    await self.check_quota(provider)
except LaunchQuotaExceeded:
    return
```

在开始新构建前检查配额。

#### 阶段 9：提交构建任务（第 532-598 行）

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
else:
    build.push_secret = ""

self.build = build

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
            build.progress(
                ProgressEvent.Kind.LOG_MESSAGE,
                json.dumps({"phase": ProgressEvent.BuildStatus.FAILED.value, "message": "Unhandled error...\n"}),
            )

    build_starttime = time.perf_counter()
    pool = self.settings["build_pool"]
    submit_future = pool.submit(build.submit)
    submit_future.add_done_callback(_check_result)
    IOLoop.current().add_callback(lambda: submit_future)
```

创建 BuildExecutor 实例，获取动态推送凭证，提交到构建线程池。`_check_result` 回调处理构建任务异常。

#### 阶段 10：事件处理循环（第 600-657 行）

```python
await self.emit({"phase": "waiting", "message": "Waiting for build to start...\n"})

while not done:
    progress = await q.get()
    if progress.kind == ProgressEvent.Kind.BUILD_STATUS_CHANGE:
        phase = progress.payload.value
        if progress.payload == ProgressEvent.BuildStatus.PENDING:
            continue
        elif progress.payload == ProgressEvent.BuildStatus.BUILT:
            if build_only:
                message = "Done! Image built\n"
                phase = "ready"
            else:
                message = "Built image, launching...\n"
            event = {"phase": phase, "message": message, "imageName": image_name}
            BUILD_TIME.labels(status="success").observe(time.perf_counter() - build_starttime)
            BUILD_COUNT.labels(status="success", **self.repo_metric_labels).inc()
            done = True
        elif progress.payload == ProgressEvent.BuildStatus.RUNNING:
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
            BUILD_TIME.labels(status="failure").observe(time.perf_counter() - build_starttime)
            BUILD_COUNT.labels(status="failure", **self.repo_metric_labels).inc()
    await self.emit(event)
```

事件循环处理两种事件类型：
1. **BUILD_STATUS_CHANGE**：
   - PENDING：等待中，不发送事件
   - RUNNING：开始流式传输日志（提交 `stream_logs` 到线程池）
   - BUILT：构建成功，记录指标，设置 done=True
   - FAILED/UNKNOWN：发送对应阶段事件
2. **LOG_MESSAGE**：JSON 日志消息直接转发，如果包含 failure/failed 阶段则记录失败指标

#### 阶段 11：构建后启动或延迟关闭（第 659-676 行）

```python
if build_only:
    return

if not failed:
    with LAUNCHES_INPROGRESS.track_inprogress():
        await self.launch(provider)
    self.emit_launch_event(provider, spec, ref)

await asyncio.sleep(60)
```

构建成功后：
- `build_only` 模式直接返回
- 否则调用 `launch()` 启动服务器
- 最后等待 60 秒再关闭连接——这是为了防止行为良好的客户端自动重连导致重复构建（客户端应在收到 ready 事件后主动关闭连接）

### emit_launch_event()（第 678-705 行）

```python
def emit_launch_event(self, provider, spec, ref):
    host = (
        self.settings["normalized_origin"]
        if self.settings["normalized_origin"]
        else self.request.host
    )
    request_origin = self.request.headers.get("Origin")
    if request_origin is None:
        request_origin = self.request.headers.get("Sec-Fetch-Site", "")
    self.event_log.emit(
        "binderhub.jupyter.org/launch",
        6,
        {
            "provider": provider.name,
            "spec": spec,
            "ref": ref,
            "status": "success",
            "build_token": self._have_build_token,
            "origin": host,
            "request_origin": request_origin,
        },
    )
```

向 EventLog 发送 `binderhub.jupyter.org/launch` schema v6 事件，包含提供商、spec、ref、状态、build_token 存在标志以及来源信息。使用 `Sec-Fetch-Site` 头作为脚本请求的辅助判断。

### check_quota()（第 707-732 行）

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

调用 LaunchQuota 检查配额，配额超时时记录失败指标并发送失败事件。

### launch() 方法（第 734-857 行）

`launch()` 方法负责通过 JupyterHub API 启动用户服务器。

#### 前置检查和重试循环（第 736-842 行）

```python
async def launch(self, provider):
    quota_check = await self.check_quota(provider)
    if quota_check:
        if quota_check.matching >= 0.5 * quota_check.quota:
            log = app_log.warning
        else:
            log = app_log.info
        log("Launching server for %s: %s other servers running this repo (%s total)",
            self.repo_url, quota_check.matching, quota_check.total)

    await self.emit({"phase": "launching", "message": "Launching server...\n"})

    client_ip = self.request.remote_ip
    launcher = self.settings["launcher"]
    retry_delay = launcher.retry_delay
    for i in range(launcher.retries):
        launch_starttime = time.perf_counter()
```

首先再次检查配额，然后进入重试循环（默认 4 次重试，指数退避）。

#### 用户身份确定（第 763-775 行）

```python
if self.settings["auth_enabled"]:
    user_model = self.hub_auth.get_user(self)
    username = user_model["name"]
    if launcher.allow_named_servers:
        server_name = launcher.unique_name_from_repo(self.repo_url)
    else:
        server_name = ""
else:
    username = launcher.unique_name_from_repo(self.repo_url)
    server_name = ""
```

- **认证模式**：使用登录用户的名称，如允许命名服务器则为每次启动生成唯一 server_name
- **匿名模式**：基于仓库 URL 生成唯一临时用户名

#### 启动调用（第 777-801 行）

```python
async def handle_progress_event(event):
    message = event["message"]
    await self.emit({"phase": "launching", "message": message + "\n"})

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
```

调用 `Launcher.launch()`，传入镜像名、用户名、服务器名、额外参数和进度回调。`extra_args` 包含 Binder 上下文信息（ref URL、启动主机、请求路径、客户端 IP）。

#### 重试逻辑和指标记录（第 802-851 行）

```python
except Exception as e:
    duration = time.perf_counter() - launch_starttime
    if i + 1 == launcher.retries:
        status = "failure"
    else:
        status = "retry"
    LAUNCH_TIME.labels(status=status, retries=-1).observe(time.perf_counter() - launch_starttime)
    if status == "failure":
        LAUNCH_COUNT.labels(status=status, **self.repo_metric_labels).inc()
    if i + 1 == launcher.retries:
        raise
    await asyncio.sleep(retry_delay)
    retry_delay *= 2
    continue
else:
    duration = time.perf_counter() - launch_starttime
    LAUNCH_TIME.labels(status="success", retries=i).observe(duration)
    LAUNCH_COUNT.labels(status="success", **self.repo_metric_labels).inc()
    app_log.info("Launched %s in %.0fs", self.repo_url, duration)
    break
```

重试使用指数退避（`retry_delay *= 2`）。失败时记录 retry/failure 指标，成功时记录 success 指标和重试次数。

#### 成功事件（第 853-857 行）

```python
event = {"phase": "ready", "message": f"server running at {server_info['url']}\n"}
event.update(server_info)
await self.emit(event)
```

启动成功后发送 `ready` 事件，包含服务器 URL 和其他信息。
