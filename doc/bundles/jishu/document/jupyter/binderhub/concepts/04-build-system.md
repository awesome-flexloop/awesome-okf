---
type: Concept
title: "构建系统：BuildExecutor 与 KubernetesBuildExecutor"
description: "深入解析 BinderHub 的镜像构建执行系统，包括 ProgressEvent 事件模型、BuildExecutor 抽象基类、KubernetesBuildExecutor 的 Pod 创建与日志流式处理机制、KubernetesCleaner 构建 Pod 清理器，以及本地开发用的 LocalRepo2dockerBuild 执行器。"
tags: [binderhub, build, kubernetes, repo2docker, pod, docker, executor, event-stream, cleanup]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T20:45:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/binderhub/binderhub/
---

# 构建系统：BuildExecutor 与 KubernetesBuildExecutor

## 概述

BinderHub 的构建系统定义在 build.py 和 build_local.py 中，负责将 Git 仓库代码通过 [repo2docker](https://github.com/jupyterhub/repo2docker) 构建为可运行的 Docker 镜像。构建系统采用抽象基类 + 具体实现的插件架构，核心抽象是 `BuildExecutor`，生产环境使用 `KubernetesBuildExecutor`（在 Kubernetes Pod 中运行 repo2docker），本地开发可使用 `LocalRepo2dockerBuild`（直接调用本地 repo2docker 进程）。此外还有 `FakeBuild` 用于纯 UI 开发，以及 `KubernetesCleaner` 负责定期清理过期构建 Pod。

## ProgressEvent：构建进度事件模型

`ProgressEvent` 类（build.py:26-54）是构建系统中所有进度事件的统一数据结构。

```python
class ProgressEvent:
    """Represents an event that happened in the build process"""

    class Kind(Enum):
        BUILD_STATUS_CHANGE = 1
        LOG_MESSAGE = 2

    class BuildStatus(Enum):
        PENDING = "pending"
        RUNNING = "running"
        BUILT = "built"
        FAILED = "failed"
        UNKNOWN = "unknown"

    def __init__(self, kind: Kind, payload: Union[str, BuildStatus]):
        self.kind = kind
        self.payload = payload
```

### 事件类型 (Kind)

| Kind 值 | 说明 | payload 类型 |
|---|---|---|
| `BUILD_STATUS_CHANGE` | 构建状态变更事件 | `BuildStatus` 枚举值 |
| `LOG_MESSAGE` | 构建日志消息事件 | JSON 字符串（repo2docker 的 `--json-logs` 输出） |

### 构建状态 (BuildStatus)

| BuildStatus 值 | 说明 |
|---|---|
| `PENDING` | 构建 Pod 已创建，等待调度或拉取镜像 |
| `RUNNING` | 构建容器正在运行，repo2docker 执行中 |
| `BUILT` | 构建成功完成，镜像已推送（如果配置了注册表） |
| `FAILED` | 构建失败 |
| `UNKNOWN` | 无法识别的 Pod 阶段 |

事件通过线程安全的队列传递到 Tornado 主线程：

```python
def progress(self, kind: ProgressEvent.Kind, payload: str):
    """Put current progress info into the queue on the main thread"""
    self.main_loop.add_callback(self.q.put, ProgressEvent(kind, payload))
```

使用 `IOLoop.add_callback()` 确保队列操作始终在事件循环线程中执行，这是 Tornado 线程安全编程的标准模式。

## BuildExecutor：构建执行器抽象基类

`BuildExecutor`（build.py:57-222）继承自 `traitlets.config.LoggingConfigurable`，是所有构建执行器的抽象基类。

### 核心 Traitlets 属性

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `q` | `Any` | 无 | 接收进度事件的队列（由 BuildHandler 传入） |
| `name` | `Unicode` | 无 | 构建的唯一名称，用于标识同一 (repo, ref) 的构建 |
| `repo_url` | `Unicode` | 无 | 要构建的 Git 仓库 URL |
| `ref` | `Unicode` | 无 | 要构建的 Git 引用（commit SHA） |
| `image_name` | `Unicode` | 无 | 目标镜像全名（含 tag） |
| `git_credentials` | `Unicode` | `""` | Git 克隆凭证，通过 `GIT_CREDENTIAL_ENV` 环境变量传递 |
| `push_secret` | `Unicode` | `""` | 推送镜像到注册表的静态凭证 Secret 名称 |
| `registry_credentials` | `Dict` | `{}` | 动态注册表凭证（覆盖 push_secret） |
| `memory_limit` | `ByteSpecification` | `0` | 构建内存限制（已废弃，使用 resources） |
| `appendix` | `Unicode` | `""` | 追加到 repo2docker Dockerfile 末尾的 Dockerfile 片段 |
| `builder_info` | `Dict` | 无 | 构建器元数据（如 repo2docker 版本），暴露在 /versions 端点 |
| `repo2docker_extra_args` | `List(Unicode)` | `[]` | 传递给 jupyter-repo2docker 的额外命令行参数 |

### repo2docker 命令构建

`get_r2d_cmd_options()` 方法构建 repo2docker 的命令行参数列表：

```python
def get_r2d_cmd_options(self):
    """Get options/flags for repo2docker"""
    r2d_options = [
        f"--ref={self.ref}",
        f"--image={self.image_name}",
        "--no-clean",
        "--no-run",
        "--json-logs",
        "--user-name=jovyan",
        "--user-id=1000",
    ]
    if self.appendix:
        r2d_options.extend(["--appendix", self.appendix])
    if self.push_secret:
        r2d_options.append("--push")
    r2d_options += self.repo2docker_extra_args
    return r2d_options
```

关键参数说明：
- `--ref`：指定要构建的 Git commit；
- `--image`：目标镜像名；
- `--no-clean`：构建后不清理中间容器（有利于缓存）；
- `--no-run`：只构建不运行；
- `--json-logs`：输出结构化 JSON 日志（前端解析展示）；
- `--user-name=jovyan` / `--user-id=1000`：容器内用户设置，与 JupyterHub 兼容；
- `--push`：构建完成后推送到注册表（仅当配置了 push_secret 时添加）。

`get_cmd()` 方法组装完整命令：

```python
def get_cmd(self):
    cmd = ["jupyter-repo2docker"] + self.get_r2d_cmd_options()
    cmd.append(self.repo_url)  # repo_url 放在最后，避免参数混淆
    return cmd
```

### 抽象方法

子类必须实现以下方法：

| 方法 | 说明 |
|---|---|
| `submit()` | 提交构建任务，进度事件通过 `self.q` 队列传递 |
| `stream_logs()` | 流式获取构建日志，将日志行通过 `progress()` 发送 |
| `cleanup()` | 清理构建资源（如删除 Pod） |

### 停止机制

```python
stop_event = Any()

@default("stop_event")
def _default_stop_event(self):
    return threading.Event()

def stop(self):
    """Stop watching progress of build"""
    self.stop_event.set()
```

使用 `threading.Event` 实现跨线程的停止信号。当客户端断开连接时，`BuildHandler.on_finish()` 调用 `build.stop()` 设置此事件，通知日志流和 Pod 监听循环退出。

## KubernetesBuildExecutor：Kubernetes 构建执行器

`KubernetesBuildExecutor`（build.py:225-733）是生产环境使用的构建执行器，它通过 Kubernetes API 创建一个运行 repo2docker 的 Pod 来执行镜像构建。

### 类继承关系

```
LoggingConfigurable
    └── BuildExecutor
        └── KubernetesBuildExecutor
```

### 核心 Traitlets 属性

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `api` | `Any` | 自动检测 | Kubernetes CoreV1Api 客户端 |
| `namespace` | `Unicode` | 环境变量 `BUILD_NAMESPACE` 或 `"default"` | 构建 Pod 所在命名空间 |
| `build_image` | `Unicode` | `"quay.io/jupyterhub/repo2docker:2024.07.0"` | repo2docker 镜像地址 |
| `push_secret` | `Unicode` | `"binder-build-docker-config"` | 包含 docker config.json 的 K8s Secret 名称 |
| `docker_host` | `Unicode` | `"/var/run/docker.sock"` | Docker socket 路径，设为 None 禁用 DinD |
| `resources` | `Dict` | 见下方 | Pod 资源请求/限制 |
| `memory_request` | `ByteSpecification` | `0` | 内存请求（已废弃，使用 resources） |
| `node_selector` | `Dict` | `{}` | Pod 节点选择器 |
| `extra_envs` | `Dict` | `{}` | Pod 额外环境变量 |
| `image_pull_secrets` | `List` | `[]` | 拉取构建镜像的 pull secret |
| `log_tail_lines` | `Integer` | `100` | 连接已运行构建时获取的日志尾部行数 |
| `sticky_builds` | `Bool` | `False` | 是否将同一仓库的构建调度到同一节点（利用 Docker 层缓存） |

#### 默认资源配置

```python
@default("resources")
def _default_resources(self):
    resources = {"limits": {}, "requests": {}}
    if self.memory_limit:
        resources["requests"]["memory"] = self.memory_request
        resources["limits"]["memory"] = self.memory_limit
    if self.memory_request:
        resources["requests"]["memory"] = self.memory_request
    return resources
```

默认资源为空，所有资源限制通过新的 `resources` 字典配置：

```python
c.KubernetesBuildExecutor.resources = {
    "requests": {"memory": "2Gi", "cpu": "1"},
    "limits": {"memory": "4Gi", "cpu": "2"},
}
```

### 节点亲和性策略

`get_affinity()` 方法（build.py:391-455）实现了两种调度策略：

#### 1. 粘性构建（sticky_builds=True）

使用 **Rendezvous Hashing**（一致性哈希的一种）将同一仓库的构建调度到同一节点，以复用 Docker 守护进程的镜像层缓存：

```python
if self.sticky_builds and image_builder_pods:
    node_names = [pod["spec"]["nodeName"] for pod in image_builder_pods["items"]]
    ranked_nodes = rendezvous_rank(node_names, self.repo_url)
    best_node_name = ranked_nodes[0]

    affinity = client.V1Affinity(
        node_affinity=client.V1NodeAffinity(
            preferred_during_scheduling_ignored_during_execution=[
                client.V1PreferredSchedulingTerm(
                    weight=100,
                    preference=client.V1NodeSelectorTerm(
                        match_expressions=[
                            client.V1NodeSelectorRequirement(
                                key="kubernetes.io/hostname",
                                operator="In",
                                values=[best_node_name],
                            )
                        ]
                    ),
                )
            ]
        )
    )
```

使用 `rendezvous_rank()` 工具函数（来自 `binderhub.utils`）计算 repo_url 的首选节点。这是"软"亲和性（preferredDuringScheduling），权重 100，不会强制绑定。

#### 2. 默认策略（反亲和性）

默认情况下，构建 Pod 之间设置**Pod 反亲和性**，尽量分散到不同节点：

```python
affinity = client.V1Affinity(
    pod_anti_affinity=client.V1PodAntiAffinity(
        preferred_during_scheduling_ignored_during_execution=[
            client.V1WeightedPodAffinityTerm(
                weight=100,
                pod_affinity_term=client.V1PodAffinityTerm(
                    topology_key="kubernetes.io/hostname",
                    label_selector=client.V1LabelSelector(
                        match_labels=dict(component=self._component_label)
                    ),
                ),
            )
        ]
    )
)
```

### 卷挂载配置

`get_builder_volumes()` 方法（build.py:457-495）配置 Pod 的存储卷：

1. **Docker Socket 挂载**（docker_host 不为 None 时）：将宿主机的 Docker socket 挂载到容器内 `/var/run/docker.sock`，实现 Docker-outside-of-Docker 构建。

```python
if self.docker_host is not None:
    volume_mounts.append(
        client.V1VolumeMount(
            mount_path="/var/run/docker.sock", name="docker-socket"
        )
    )
    docker_socket_path = urlparse(self.docker_host).path
    volumes.append(
        client.V1Volume(
            name="docker-socket",
            host_path=client.V1HostPathVolumeSource(
                path=docker_socket_path, type="Socket"
            ),
        )
    )
```

2. **Docker Config Secret 挂载**（使用 push_secret 且无动态凭证时）：将包含注册表认证信息的 Secret 挂载到 `/root/.docker/config.json`。

```python
if not self.registry_credentials and self.push_secret:
    volume_mounts.append(
        client.V1VolumeMount(
            mount_path="/root/.docker/config.json",
            name="docker-config",
            sub_path="config.json",
        )
    )
    volumes.append(
        client.V1Volume(
            name="docker-config",
            secret=client.V1SecretVolumeSource(secret_name=self.push_secret),
        )
    )
```

> **注意**：当使用动态 `registry_credentials` 时，不挂载 push_secret，凭证通过环境变量 `CONTAINER_ENGINE_REGISTRY_CREDENTIALS` 以 JSON 形式传递给 repo2docker。

### submit() 方法：构建 Pod 创建

`submit()` 方法（build.py:509-677）是构建执行的核心入口。

#### Pod 定义构建

```python
self.pod = client.V1Pod(
    metadata=client.V1ObjectMeta(
        name=self.name,
        labels={
            "name": self.name,
            "component": self._component_label,  # "binderhub-build"
        },
        annotations={
            "binder-repo": self.repo_url,
        },
    ),
    spec=client.V1PodSpec(
        containers=[
            client.V1Container(
                image=self.build_image,
                name="builder",
                args=self.get_cmd(),
                volume_mounts=volume_mounts,
                resources=self.resources,
                env=env,
            )
        ],
        tolerations=[...],
        node_selector=self.node_selector,
        volumes=volumes,
        restart_policy="Never",
        affinity=self.get_affinity(),
        image_pull_secrets=self.get_image_pull_secrets(),
    ),
)
```

#### 环境变量设置

```python
env = [
    client.V1EnvVar(name=key, value=value)
    for key, value in self.extra_envs.items()
]
if self.git_credentials:
    env.append(
        client.V1EnvVar(name="GIT_CREDENTIAL_ENV", value=self.git_credentials)
    )
if self.registry_credentials:
    env.append(
        client.V1EnvVar(
            name="CONTAINER_ENGINE_REGISTRY_CREDENTIALS",
            value=json.dumps(self.registry_credentials),
        )
    )
```

#### 容忍度配置

Pod 配置了两个容忍度以支持 JupyterHub 的专用节点污点：

```python
tolerations=[
    client.V1Toleration(
        key="hub.jupyter.org/dedicated",
        operator="Equal",
        value="user",
        effect="NoSchedule",
    ),
    client.V1Toleration(
        key="hub.jupyter.org_dedicated",
        value="user",
        effect="NoSchedule",
    ),
]
```

> 第二个容忍度处理 GKE（Google Kubernetes Engine）不允许 taint key 包含 `/` 的限制。

#### Pod 创建与并发处理

```python
try:
    _ = self.api.create_namespaced_pod(
        self.namespace, self.pod, _request_timeout=KUBE_REQUEST_TIMEOUT,
    )
except client.rest.ApiException as e:
    if e.status == 409:
        # Someone else created it!
        app_log.info("Build %s already running", self.name)
        pass
    else:
        raise
else:
    app_log.info("Started build %s", self.name)
```

HTTP 409 Conflict 表示同名 Pod 已存在（可能是另一个 BinderHub 实例或之前的请求创建的），此时不报错而是直接监听已有 Pod。这利用了 Kubernetes API 本身的幂等性作为分布式锁。

#### Pod 状态监听循环

创建 Pod 后，使用 Kubernetes Watch API 持续监听 Pod 状态变化：

```python
while not self.stop_event.is_set():
    w = watch.Watch()
    try:
        for f in w.stream(
            self.api.list_namespaced_pod,
            self.namespace,
            label_selector=f"name={self.name}",
            timeout_seconds=30,
            _request_timeout=KUBE_REQUEST_TIMEOUT,
        ):
            if f["type"] == "DELETED":
                phase = f["object"].status.phase
                if phase == "Succeeded":
                    self.progress(BUILD_STATUS_CHANGE, BuildStatus.BUILT)
                else:
                    self.progress(BUILD_STATUS_CHANGE, BuildStatus.FAILED)
                return
            self.pod = f["object"]
            phase = self.pod.status.phase
            if phase == "Pending":
                self.progress(BUILD_STATUS_CHANGE, BuildStatus.PENDING)
            elif phase == "Running":
                self.progress(BUILD_STATUS_CHANGE, BuildStatus.RUNNING)
            elif phase == "Failed":
                self.progress(BUILD_STATUS_CHANGE, BuildStatus.FAILED)
            elif phase == "Unknown":
                self.progress(BUILD_STATUS_CHANGE, BuildStatus.UNKNOWN)

            if self.pod.status.phase in ("Succeeded", "Failed"):
                self.cleanup()
    except ReadTimeoutError:
        pass  # 超时重试
    except Exception:
        app_log.exception("Error in watch stream for %s", self.name)
        raise
    finally:
        w.stop()
```

Watch 流每 30 秒超时一次以避免长时间连接挂起，超时后自动重连。Pod 被删除时（DELETED 事件）根据最终阶段发出 BUILT 或 FAILED 事件。

### stream_logs() 方法：日志流式处理

`stream_logs()` 方法（build.py:679-715）在 Pod 进入 Running 状态后启动，通过 Kubernetes API 跟随 Pod 日志输出。

```python
def stream_logs(self):
    app_log.info("Watching logs of %s", self.name)
    for line in self.api.read_namespaced_pod_log(
        self.name,
        self.namespace,
        follow=True,
        tail_lines=self.log_tail_lines,
        _request_timeout=(3, None),  # 连接超时3秒，读取无超时
        _preload_content=False,
    ):
        if self.stop_event.is_set():
            return
        line = line.decode("utf-8")
        try:
            json.loads(line)
        except ValueError:
            # 非 JSON 日志行，包装为 unknown phase
            app_log.error("log event not json: %r", line)
            line = json.dumps({"phase": "unknown", "message": line})

        self.progress(ProgressEvent.Kind.LOG_MESSAGE, line)
```

关键细节：
- `follow=True` 启用日志跟随（类似 `tail -f`）；
- `tail_lines=100` 在连接已有构建时获取最近 100 行日志，让用户看到构建进度；
- `_request_timeout=(3, None)` 设置连接超时3秒、读取无超时（长连接）；
- `_preload_content=False` 以流方式读取响应，避免一次性加载所有日志到内存；
- repo2docker 以 `--json-logs` 模式运行，每行日志都是一个 JSON 对象，包含 `phase` 和 `message` 字段；
- 非 JSON 行（如 kubelet 系统消息）被包装为 `{"phase": "unknown", "message": ...}`。

### cleanup() 方法：Pod 清理

```python
def cleanup(self):
    """Delete the kubernetes build pod"""
    try:
        self.api.delete_namespaced_pod(
            name=self.name,
            namespace=self.namespace,
            body=client.V1DeleteOptions(grace_period_seconds=0),
            _request_timeout=KUBE_REQUEST_TIMEOUT,
        )
    except client.rest.ApiException as e:
        if e.status == 404:
            pass  # 已被其他人删除，忽略
        else:
            raise
```

`grace_period_seconds=0` 表示立即强制删除 Pod，不等待优雅终止。404 错误被忽略（可能已被清理器删除）。

## KubernetesCleaner：构建 Pod 定期清理器

`KubernetesCleaner`（build.py:736-821）负责定期清理已完成和超时的构建 Pod。

### 属性配置

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `kube` | `Any` | 自动检测 | Kubernetes CoreV1Api 客户端 |
| `namespace` | `Unicode` | 环境变量 `BUILD_NAMESPACE` 或 `"default"` | 清理的命名空间 |
| `max_age` | `Integer` | `14400`（4小时） | 构建 Pod 最大存活时间 |

### cleanup() 方法

```python
def cleanup(self):
    builds = self.kube.list_namespaced_pod(
        namespace=self.namespace,
        label_selector="component=binderhub-build",
    ).items
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    start_cutoff = now - datetime.timedelta(seconds=self.max_age)
    deleted = 0
    for build in builds:
        phase = build.status.phase
        delete = False
        if build.status.phase in {"Failed", "Succeeded", "Evicted"}:
            delete = True  # 已终止的 Pod 立即删除
        else:
            started = build.status.start_time
            if self.max_age and started and started < start_cutoff:
                delete = True  # 运行超过 max_age 的 Pod 强制删除
        if delete:
            deleted += 1
            try:
                self.kube.delete_namespaced_pod(...)
            except client.rest.ApiException as e:
                if e.status == 404:
                    pass
                else:
                    raise
```

清理逻辑：
1. 列出所有带有 `component=binderhub-build` 标签的 Pod；
2. **立即删除** Failed/Succeeded/Evicted 状态的 Pod；
3. **强制删除**运行时间超过 `max_age`（默认4小时）的 Running/Pending Pod，防止构建挂死泄漏资源；
4. 输出删除计数和各阶段 Pod 数量统计日志。

## LocalRepo2dockerBuild：本地开发构建器

`LocalRepo2dockerBuild` 定义在 build_local.py:107-179，用于本地开发环境，直接在本地机器上调用 repo2docker 命令。

### _execute_cmd() 辅助函数

由于 BinderHub 运行在异步 Tornado 环境中，但 subprocess 调用是同步的，`_execute_cmd()`（build_local.py:45-104）使用独立线程 + 队列模式实现可中断的子进程输出捕获：

```python
def _execute_cmd(cmd, capture=False, break_callback=None, **kwargs):
    proc = subprocess.Popen(cmd, **kwargs)
    q = queue.Queue()

    def read_to_queue(proc, capture, q):
        try:
            for line in proc.stdout:
                q.put(line)
        finally:
            proc.wait()

    t = Thread(target=read_to_queue, args=(proc, capture, q))
    t.daemon = True
    t.start()

    while True:
        try:
            line = q.get(True, timeout=DEFAULT_READ_TIMEOUT)
            yield line.decode("utf8", "replace")
            if break_callback and break_callback():
                proc.kill()
                terminated = True
        except queue.Empty:
            if break_callback and break_callback():
                proc.kill()
                terminated = True
            if not t.is_alive():
                break
    t.join()
```

- 子进程输出在独立线程中读取并放入 `queue.Queue`；
- 主线程每秒检查一次队列和停止回调，实现及时中断；
- `break_callback` 返回 True 时立即 kill 子进程。

### submit() 实现

```python
def submit(self):
    def break_callback():
        return self.stop_event.is_set()

    env = os.environ.copy()
    if self.git_credentials:
        env["GIT_CREDENTIAL_ENV"] = self.git_credentials

    cmd = self.get_cmd()
    app_log.info("Starting build: %s", " ".join(cmd))

    try:
        self.progress(BUILD_STATUS_CHANGE, BuildStatus.RUNNING)
        for line in _execute_cmd(
            cmd, capture=True, break_callback=break_callback, env=env
        ):
            self._handle_log(line)
        self.progress(BUILD_STATUS_CHANGE, BuildStatus.BUILT)
    except subprocess.CalledProcessError:
        self.progress(BUILD_STATUS_CHANGE, BuildStatus.FAILED)
```

本地构建不经过 Kubernetes，直接运行 repo2docker 进程，逐行处理日志输出。

## FakeBuild：无构建基础设施的 UI 开发

`FakeBuild`（build.py:824-877）是一个模拟构建器，用于在没有 Kubernetes/Docker 的环境下开发前端 UI：

```python
class FakeBuild(BuildExecutor):
    """Fake Building process to be able to work on the UI without a builder."""

    def submit(self):
        self.progress(BUILD_STATUS_CHANGE, BuildStatus.RUNNING)
        return

    def stream_logs(self):
        import time
        time.sleep(3)
        for phase in ("Pending", "Running", "Succeed", "Building"):
            if self.stop_event.is_set():
                return
            self.progress(LOG_MESSAGE, json.dumps({"phase": phase, "message": f"{phase}...\n"}))
        for i in range(5):
            time.sleep(1)
            self.progress("log", json.dumps({"phase": "unknown", "message": f"Step {i+1}/10\n"}))
        self.progress(BUILD_STATUS_CHANGE, BuildStatus.BUILT)
```

配置使用 FakeBuild：

```python
c.BinderHub.build_class = FakeBuild
c.BinderHub.builder_required = False
```

## 构建流程时序

下图展示了从 BuildHandler 提交构建到完成的完整流程：

```
BuildHandler.get()
    │
    ├── 检查镜像是否存在（registry 或本地 docker）
    │   └── 已存在 → 直接 launch
    │
    ├── 创建 Queue()
    ├── 实例化 BuildExecutor（传入 q, name, repo_url, ref, image_name）
    ├── build_pool.submit(build.submit)  ← 在线程池中提交
    │   │
    │   ├── KubernetesBuildExecutor.submit()
    │   │   ├── 创建 V1Pod 定义（含 repo2docker 容器、卷、环境变量）
    │   │   ├── api.create_namespaced_pod()
    │   │   └── Watch Pod 状态变化
    │   │       ├── Pending → progress(PENDING)
    │   │       ├── Running → progress(RUNNING) → 触发 stream_logs
    │   │       │   └── pool.submit(build.stream_logs)
    │   │       │       └── follow Pod logs → 逐行 progress(LOG_MESSAGE)
    │   │       ├── DELETED(Succeeded) → progress(BUILT)
    │   │       └── DELETED(Failed) → progress(FAILED)
    │   │
    │   └── LocalRepo2dockerBuild.submit()
    │       ├── subprocess.Popen(jupyter-repo2docker ...)
    │       └── 逐行读取输出 → progress(LOG_MESSAGE)
    │
    └── 主循环: await q.get() 处理事件
        ├── BUILD_STATUS_CHANGE → 更新前端状态、触发 stream_logs
        └── LOG_MESSAGE → 转发给前端显示
```

## 关键源码引用

- ProgressEvent 类：build.py:26-54
- BuildExecutor 基类：build.py:57-222
- KubernetesBuildExecutor：build.py:225-733
- submit() 方法：build.py:509-677
- stream_logs() 方法：build.py:679-715
- cleanup() 方法：build.py:717-733
- KubernetesCleaner：build.py:736-821
- LocalRepo2dockerBuild：build_local.py:107-179
- FakeBuild：build.py:824-877
