---
type: Reference
title: "构建执行器源码解析"
description: "深入解析binderhub/build.py中的构建执行器体系，包括ProgressEvent事件模型、BuildExecutor基类、KubernetesBuildExecutor Kubernetes构建实现、KubernetesCleaner清理器以及FakeBuild测试桩。"
tags: [source, build, kubernetes, repo2docker, executor]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T20:45:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-py
    resource: "../../../../../external/libs/jupyter/binderhub/binderhub/build.py"
    title: "binderhub/build.py 源码"
---

# 构建执行器源码解析

## 概述

[build.py](file:///D:/spaces/SpecWeave/external/libs/jupyter/binderhub/binderhub/build.py) 定义了 BinderHub 的镜像构建执行体系。该模块包含三个核心类层次：`ProgressEvent`（构建进度事件）、`BuildExecutor`（构建执行器基类）、`KubernetesBuildExecutor`（Kubernetes Pod 构建实现）、`KubernetesCleaner`（过期 Pod 清理器）和 `FakeBuild`（测试用假构建器）。

## ProgressEvent：构建进度事件模型

`ProgressEvent` 定义在第 26-54 行，是构建过程中所有状态变化和日志消息的统一事件表示。

### Kind 枚举（第 31-37 行）

```python
class Kind(Enum):
    BUILD_STATUS_CHANGE = 1
    LOG_MESSAGE = 2
```

事件类型分为两种：
- `BUILD_STATUS_CHANGE`（值 1）：构建状态发生变化（如从 Pending 到 Running）
- `LOG_MESSAGE`（值 2）：来自 repo2docker 的 JSON 日志消息

### BuildStatus 枚举（第 39-50 行）

```python
class BuildStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    BUILT = "built"
    FAILED = "failed"
    UNKNOWN = "unknown"
```

构建状态枚举与 Kubernetes Pod 阶段对应：
| 状态 | 值 | 含义 |
|------|-----|------|
| `PENDING` | `"pending"` | Pod 已创建但尚未运行 |
| `RUNNING` | `"running"` | Pod 正在执行构建 |
| `BUILT` | `"built"` | 构建成功完成 |
| `FAILED` | `"failed"` | 构建失败 |
| `UNKNOWN` | `"unknown"` | 无法确定构建状态 |

### 构造函数（第 52-54 行）

```python
def __init__(self, kind: Kind, payload: Union[str, BuildStatus]):
    self.kind = kind
    self.payload = payload
```

每个事件包含 `kind`（类型）和 `payload`（负载）。对于状态变更事件，payload 是 `BuildStatus` 枚举值；对于日志消息，payload 是 JSON 字符串。

## BuildExecutor：构建执行器基类

`BuildExecutor` 定义在第 57-222 行，继承自 `LoggingConfigurable`，是所有构建执行器的抽象基类。

### 核心 Traitlets 属性

#### 基本标识属性（第 62-77 行）

```python
q = Any(help="Queue that receives progress events after the build has been submitted")
name = Unicode(help="A unique name for the thing (repo, ref) being built. Used to coalesce builds.")
repo_url = Unicode(help="URL of repository to build.")
ref = Unicode(help="Ref of repository to build.")
image_name = Unicode(help="Full name of the image to build. Includes the tag.")
```

- `q`：Tornado 队列，用于向主线程传递进度事件
- `name`：构建的唯一名称，用于合并相同 (repo, ref) 的构建请求，利用 Kubernetes API 的原子性避免重复创建 Pod
- `repo_url`：要构建的仓库 URL
- `ref`：要构建的 Git ref（分支/commit SHA）
- `image_name`：完整的目标镜像名（包含 tag）

#### 凭证配置（第 79-107 行）

```python
git_credentials = Unicode(
    "",
    help="Git credentials to use when cloning the repository, passed via the GIT_CREDENTIAL_ENV environment variable.",
    config=True,
)

push_secret = Unicode(
    "",
    help="Implementation dependent static secret for pushing image to a registry.",
    config=True,
)

registry_credentials = Dict(
    {},
    help="Implementation dependent credentials for pushing image to a registry. "
         'e.g. `{"registry": "docker.io", "username":"user", "password":"password"}`. '
         "Passed via CONTAINER_ENGINE_REGISTRY_CREDENTIALS environment variable.",
    config=True,
)
```

- `git_credentials`：Git 克隆凭证，通过 `GIT_CREDENTIAL_ENV` 环境变量传递给 repo2docker
- `push_secret`：静态 Registry 推送凭证（如 Kubernetes Secret 名称）
- `registry_credentials`：动态 Registry 凭证字典，通过 `CONTAINER_ENGINE_REGISTRY_CREDENTIALS` 环境变量传递；如果提供则优先于 `push_secret`

#### 构建配置（第 109-142 行）

```python
memory_limit = ByteSpecification(
    0,
    help="Memory limit for the build process in bytes (optional suffixes K M G T). DEPRECATED.",
    config=True,
)

appendix = Unicode(
    "",
    help="Appendix to be added at the end of the Dockerfile used by repo2docker.",
    config=True,
)

builder_info = Dict(
    help="Metadata about the builder e.g. repo2docker version.",
    config=True,
)

repo2docker_extra_args = List(
    Unicode,
    default_value=[],
    help="Extra commandline parameters to be passed to jupyter-repo2docker during build",
    config=True,
)
```

- `memory_limit`：构建内存限制（已废弃，repo2docker 不支持 per-build 资源限制）
- `appendix`：追加到 Dockerfile 末尾的指令
- `builder_info`：构建器元数据（如 repo2docker 版本），用于 `/versions` 端点
- `repo2docker_extra_args`：传递给 jupyter-repo2docker 的额外命令行参数

#### 线程安全属性（第 144-152 行）

```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.main_loop = IOLoop.current()

stop_event = Any()

@default("stop_event")
def _default_stop_event(self):
    return threading.Event()
```

构造函数获取当前 IOLoop 引用用于跨线程回调。`stop_event` 是一个 `threading.Event`，用于安全地停止日志流监听。

### 核心方法

#### get_r2d_cmd_options()（第 154-173 行）

```python
def get_r2d_cmd_options(self):
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

生成 repo2docker 命令行参数：
- `--ref`：指定构建的 Git ref
- `--image`：目标镜像名
- `--no-clean`：不清理构建缓存
- `--no-run`：构建后不运行容器
- `--json-logs`：输出 JSON 格式日志
- `--user-name=jovyan`/`--user-id=1000`：设置容器内用户
- `--appendix`：如果有 appendix 则追加
- `--push`：如果配置了 push_secret 则推送镜像

#### get_cmd()（第 175-186 行）

```python
def get_cmd(self):
    cmd = ["jupyter-repo2docker"] + self.get_r2d_cmd_options()
    cmd.append(self.repo_url)
    return cmd
```

组装完整的 repo2docker 命令。注意 `repo_url` 放在最后，避免被误认为是子命令参数。

#### progress()（第 188-192 行）

```python
def progress(self, kind: ProgressEvent.Kind, payload: str):
    self.main_loop.add_callback(self.q.put, ProgressEvent(kind, payload))
```

线程安全的进度事件发送方法。通过 `IOLoop.add_callback()` 将事件放入主线程的队列，确保跨线程通信安全。

#### 抽象方法和默认实现

```python
def submit(self):
    raise NotImplementedError()

def stream_logs(self):
    pass

def cleanup(self):
    pass

def stop(self):
    self.stop_event.set()
```

- `submit()`：提交构建任务（抽象方法，子类必须实现）
- `stream_logs()`：流式传输构建日志（默认空实现）
- `cleanup()`：清理构建资源（默认空实现）
- `stop()`：停止构建监听（设置 `stop_event`，不停止构建本身）

## KubernetesBuildExecutor：Kubernetes 构建执行器

`KubernetesBuildExecutor` 定义在第 225-733 行，继承自 `BuildExecutor`，通过在 Kubernetes 集群中创建 Pod 来执行 repo2docker 构建。

### 核心设计思想

类文档字符串（第 226-244 行）明确了关键设计原则：

> 多个 Build 对象可以指向同一个 Pod。`name` 属性必须唯一且不可变，基于 `(repo_url, ref)` 元组生成。相同元组对应相同 name，利用 Kubernetes API 的锁机制避免重复创建 Pod，无需自行实现分布式锁。

### Traitlets 属性

#### Kubernetes API 配置（第 247-291 行）

```python
api = Any(help="Kubernetes API object to make requests (kubernetes.client.CoreV1Api())")

@default("api")
def _default_api(self):
    try:
        kubernetes.config.load_incluster_config()
    except kubernetes.config.ConfigException:
        kubernetes.config.load_kube_config()
    return client.CoreV1Api()

namespace = Unicode(help="Kubernetes namespace to spawn build pods into", config=True)

@default("namespace")
def _default_namespace(self):
    return os.getenv("BUILD_NAMESPACE", "default")
```

- `api`：Kubernetes CoreV1Api 客户端，默认自动检测 in-cluster 或本地 kubeconfig
- `namespace`：构建 Pod 所在命名空间，默认从 `BUILD_NAMESPACE` 环境变量获取，默认值 `"default"`

#### 构建镜像配置（第 293-305 行）

```python
build_image = Unicode(
    "quay.io/jupyterhub/repo2docker:2024.07.0",
    help="Docker image containing repo2docker that is used to spawn the build pods.",
    config=True,
)

@default("builder_info")
def _default_builder_info(self):
    return {"build_image": self.build_image}

image_pull_secrets = List([], help="Pull secrets for the builder image", config=True)
```

- `build_image`：包含 repo2docker 的构建镜像，默认使用 `quay.io/jupyterhub/repo2docker:2024.07.0`
- `builder_info`：默认返回包含 `build_image` 的字典
- `image_pull_secrets`：拉取构建镜像所需的 imagePullSecrets

#### Docker 配置（第 307-318 行）

```python
docker_host = Unicode(
    "/var/run/docker.sock",
    allow_none=True,
    help="The docker socket to use for building the image. Must be a unix domain socket.",
    config=True,
)
```

Docker socket 路径，支持 DinD（Docker-in-Docker）模式。设为 None 可禁用（如使用不需要 Docker socket 的替代构建器）。

#### 资源配置（第 320-357 行）

```python
resources = Dict(help="Kubernetes resources for the build pod.", config=True)

@default("resources")
def _default_resources(self):
    resources = {"limits": {}, "requests": {}}
    if self.memory_limit:
        self.log.warning("Using deprecated KubernetesBuildExecutor.memory_limit.")
        resources["requests"]["memory"] = self.memory_request
        resources["limits"]["memory"] = self.memory_limit
    if self.memory_request:
        self.log.warning("Using deprecated KubernetesBuildExecutor.memory_request.")
        resources["requests"]["memory"] = self.memory_request
    return resources

memory_request = ByteSpecification(
    0,
    help="DEPRECATED: use KubernetesBuildExecutor.resources. Memory request of the build pod.",
    config=True,
)
```

- `resources`：标准 Kubernetes 资源请求/限制字典，包含 `limits` 和 `requests`
- `memory_request`：内存请求（已废弃，通过 `resources` 配置）

#### 调度配置（第 359-387 行）

```python
node_selector = Dict({}, help="Node selector for the kubernetes build pod.", config=True)

extra_envs = Dict({}, help="Extra environment variables for the kubernetes build pod.", config=True)

log_tail_lines = Integer(
    100,
    help="Number of log lines to fetch from a currently running build.",
    config=True,
)

sticky_builds = Bool(
    False,
    help="If true, builds for the same repo will try to schedule on the same node to reuse docker layer cache.",
    config=True,
)

_component_label = Unicode("binderhub-build")
```

- `node_selector`：Pod 节点选择器
- `extra_envs`：额外环境变量
- `log_tail_lines`：连接到已运行构建时获取的日志行数（默认 100）
- `sticky_builds`：粘性构建——同仓库构建调度到同一节点以利用 Docker 层缓存
- `_component_label`：Pod 标签的 component 值（内部使用）

#### 凭证覆盖（第 260-283 行）

重写了基类的 `push_secret` 和 `registry_credentials`：

```python
push_secret = Unicode(
    "binder-build-docker-config",
    help="Name of a Kubernetes secret containing static credentials for pushing an image to a registry.",
    config=True,
)
```

默认 push_secret 为 `"binder-build-docker-config"`。

### get_affinity()：Pod 亲和性调度（第 391-455 行）

```python
def get_affinity(self):
    resp = self.api.list_namespaced_pod(
        self.namespace,
        label_selector="component=image-builder,app=binder",
        _request_timeout=KUBE_REQUEST_TIMEOUT,
        _preload_content=False,
    )
    image_builder_pods = json.loads(resp.read())
```

该方法根据配置决定 Pod 的亲和性策略：

**粘性构建模式**（`sticky_builds=True` 且有镜像构建器 Pod）：
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

使用 Rendez-vous 哈希（`rendezvous_rank`）将同一仓库的构建分配到同一节点，优先选择权重 100 的节点亲和性。

**默认模式**（Pod 反亲和性）：
```python
else:
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

构建 Pod 倾向于调度到不同节点（Pod 反亲和性），避免单节点负载过高。

### get_builder_volumes()：卷挂载配置（第 457-495 行）

```python
def get_builder_volumes(self):
    volume_mounts = []
    volumes = []

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

    return volumes, volume_mounts
```

配置两种卷：
1. **docker-socket**：HostPath 卷，挂载宿主机 Docker socket 到容器 `/var/run/docker.sock`，用于 DinD 模式
2. **docker-config**：当使用静态 push_secret 时，将 Kubernetes Secret 挂载为 `/root/.docker/config.json`

当使用动态 `registry_credentials` 时，不挂载 docker-config 卷，凭证通过环境变量传递。

### get_image_pull_secrets()（第 497-507 行）

```python
def get_image_pull_secrets(self):
    image_pull_secrets = []
    for secret in self.image_pull_secrets:
        image_pull_secrets.append(client.V1LocalObjectReference(name=secret))
    return image_pull_secrets
```

将 `image_pull_secrets` 字符串列表转换为 Kubernetes `V1LocalObjectReference` 对象列表。

### submit()：提交构建 Pod（第 509-677 行）

这是构建执行的核心方法，完整流程如下：

#### 1. 构建环境变量（第 516-533 行）

```python
volumes, volume_mounts = self.get_builder_volumes()

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

#### 2. 创建 Pod 定义（第 535-579 行）

```python
self.pod = client.V1Pod(
    metadata=client.V1ObjectMeta(
        name=self.name,
        labels={
            "name": self.name,
            "component": self._component_label,
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
        tolerations=[
            client.V1Toleration(
                key="hub.jupyter.org/dedicated",
                operator="Equal",
                value="user",
                effect="NoSchedule",
            ),
            client.V1Toleration(
                key="hub.jupyter.org_dedicated",
                operator="Equal",
                value="user",
                effect="NoSchedule",
            ),
        ],
        node_selector=self.node_selector,
        volumes=volumes,
        restart_policy="Never",
        affinity=self.get_affinity(),
        image_pull_secrets=self.get_image_pull_secrets(),
    ),
)
```

Pod 规格关键点：
- 标签 `component=binderhub-build` 和 `name=<build-name>`
- 注解 `binder-repo=<repo_url>` 用于清理时日志记录
- 容器使用 `build_image`，命令来自 `get_cmd()`
- 容忍 JupyterHub 用户节点污点（`hub.jupyter.org/dedicated=user:NoSchedule`），包括 GKE 兼容性变体
- `restart_policy="Never"`：构建 Pod 不重启
- 使用 `get_affinity()` 返回的亲和性规则

#### 3. 创建 Pod（第 581-595 行）

```python
try:
    _ = self.api.create_namespaced_pod(
        self.namespace,
        self.pod,
        _request_timeout=KUBE_REQUEST_TIMEOUT,
    )
except client.rest.ApiException as e:
    if e.status == 409:
        app_log.info("Build %s already running", self.name)
        pass
    else:
        raise
else:
    app_log.info("Started build %s", self.name)
```

处理 409 Conflict 状态码——表示同名 Pod 已存在（另一个请求已创建），这是利用 Kubernetes API 实现幂等性的关键。

#### 4. Watch 监控 Pod 状态（第 597-677 行）

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
```

使用 Kubernetes Watch API 持续监控 Pod 状态变化，每 30 秒超时重试：

```python
if f["type"] == "DELETED":
    phase = f["object"].status.phase
    if phase == "Succeeded":
        self.progress(
            ProgressEvent.Kind.BUILD_STATUS_CHANGE,
            ProgressEvent.BuildStatus.BUILT,
        )
    else:
        self.progress(
            ProgressEvent.Kind.BUILD_STATUS_CHANGE,
            ProgressEvent.BuildStatus.FAILED,
        )
    return
```

Pod 被删除时根据最终阶段发送 BUILT 或 FAILED 事件。

```python
phase = self.pod.status.phase
if phase == "Pending":
    self.progress(ProgressEvent.Kind.BUILD_STATUS_CHANGE, ProgressEvent.BuildStatus.PENDING)
elif phase == "Running":
    self.progress(ProgressEvent.Kind.BUILD_STATUS_CHANGE, ProgressEvent.BuildStatus.RUNNING)
elif phase == "Succeeded":
    pass  # 等待 Pod 删除时发送 BUILT
elif phase == "Failed":
    self.progress(ProgressEvent.Kind.BUILD_STATUS_CHANGE, ProgressEvent.BuildStatus.FAILED)
elif phase == "Unknown":
    self.progress(ProgressEvent.Kind.BUILD_STATUS_CHANGE, ProgressEvent.BuildStatus.UNKNOWN)
```

阶段转换映射：
- `Pending` → 发送 PENDING 事件
- `Running` → 发送 RUNNING 事件（触发日志流开始）
- `Succeeded` → 不立即发送 BUILT，等待 Pod 被清理后发送
- `Failed` → 发送 FAILED 事件
- `Unknown` → 发送 UNKNOWN 事件

```python
if self.pod.status.phase == "Succeeded":
    self.cleanup()
elif self.pod.status.phase == "Failed":
    self.cleanup()
```

Pod 进入 Succeeded 或 Failed 阶段时立即调用 `cleanup()` 删除 Pod。

异常处理包括：
- `ReadTimeoutError`：超时后重试
- 其他异常：记录日志后重新抛出
- `finally` 块确保 Watch 被停止

### stream_logs()：流式日志传输（第 679-715 行）

```python
def stream_logs(self):
    app_log.info("Watching logs of %s", self.name)
    for line in self.api.read_namespaced_pod_log(
        self.name,
        self.namespace,
        follow=True,
        tail_lines=self.log_tail_lines,
        _request_timeout=(3, None),
        _preload_content=False,
    ):
        if self.stop_event.is_set():
            return
        line = line.decode("utf-8")
        try:
            json.loads(line)
        except ValueError:
            app_log.error("log event not json: %r", line)
            line = json.dumps({"phase": "unknown", "message": line})
        self.progress(ProgressEvent.Kind.LOG_MESSAGE, line)
```

关键点：
- 使用 `follow=True` 持续跟随日志输出
- `tail_lines=self.log_tail_lines` 获取最近 N 行（对已运行的构建很重要）
- `_preload_content=False` 启用流式读取
- 每行验证是否为 JSON，非 JSON 行包装为 `{"phase": "unknown", "message": ...}`
- 检查 `stop_event` 实现安全退出

### cleanup()：清理构建 Pod（第 717-733 行）

```python
def cleanup(self):
    try:
        self.api.delete_namespaced_pod(
            name=self.name,
            namespace=self.namespace,
            body=client.V1DeleteOptions(grace_period_seconds=0),
            _request_timeout=KUBE_REQUEST_TIMEOUT,
        )
    except client.rest.ApiException as e:
        if e.status == 404:
            pass
        else:
            raise
```

删除构建 Pod，`grace_period_seconds=0` 表示立即删除。404 错误表示 Pod 已被其他进程删除，属于正常情况。

## KubernetesCleaner：构建 Pod 清理器

`KubernetesCleaner` 定义在第 736-821 行，负责定期清理过期和已完成的构建 Pod。

### Traitlets 属性

```python
kube = Any(help="kubernetes API client")

@default("kube")
def _default_kube(self):
    try:
        kubernetes.config.load_incluster_config()
    except kubernetes.config.ConfigException:
        kubernetes.config.load_kube_config()
    return client.CoreV1Api()

namespace = Unicode(help="Kubernetes namespace")

@default("namespace")
def _default_namespace(self):
    return os.getenv("BUILD_NAMESPACE", "default")

max_age = Integer(
    3600 * 4,
    help="Maximum age of build pods to keep",
    config=True,
)
```

- `kube`：Kubernetes API 客户端
- `namespace`：目标命名空间，默认从 `BUILD_NAMESPACE` 环境变量获取
- `max_age`：Pod 最大保留时间，默认 4 小时（14400 秒）

### cleanup() 方法（第 764-821 行）

```python
def cleanup(self):
    builds = self.kube.list_namespaced_pod(
        namespace=self.namespace,
        label_selector="component=binderhub-build",
    ).items
```

首先列出所有带有 `component=binderhub-build` 标签的 Pod。

删除逻辑：
1. **已终止的 Pod**：阶段为 `Failed`、`Succeeded`、`Evicted` 的 Pod 立即删除（第 781-790 行）
2. **超时的运行中 Pod**：运行时间超过 `max_age` 的 Pod 强制删除（第 793-800 行）

```python
phases = defaultdict(int)
now = datetime.datetime.now(tz=datetime.timezone.utc)
start_cutoff = now - datetime.timedelta(seconds=self.max_age)
deleted = 0
for build in builds:
    phase = build.status.phase
    phases[phase] += 1
    annotations = build.metadata.annotations or {}
    repo = annotations.get("binder-repo", "unknown")
    delete = False
    if build.status.phase in {"Failed", "Succeeded", "Evicted"}:
        app_log.info("Deleting %s build %s (repo=%s)", phase, build.metadata.name, repo)
        delete = True
    else:
        started = build.status.start_time
        if self.max_age and started and started < start_cutoff:
            app_log.info("Deleting long-running build %s (repo=%s)", build.metadata.name, repo)
            delete = True
    if delete:
        deleted += 1
        try:
            self.kube.delete_namespaced_pod(
                name=build.metadata.name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(grace_period_seconds=0),
            )
        except client.rest.ApiException as e:
            if e.status == 404:
                pass
            else:
                raise
```

清理完成后输出统计日志：
```python
if deleted:
    app_log.info("Deleted %i/%i build pods", deleted, len(builds))
app_log.debug("Build phase summary: %s", json.dumps(phases, sort_keys=True, indent=1))
```

## FakeBuild：测试用假构建器

`FakeBuild` 定义在第 824-877 行，继承自 `BuildExecutor`，用于无构建基础设施时的 UI 开发测试。

### submit()（第 829-833 行）

```python
def submit(self):
    self.progress(
        ProgressEvent.Kind.BUILD_STATUS_CHANGE, ProgressEvent.BuildStatus.RUNNING
    )
    return
```

立即发送 RUNNING 状态事件。

### stream_logs()（第 835-877 行）

模拟构建过程，等待 3 秒后依次发送 Pending、Running、Succeed、Building 阶段消息，然后发送 5 个步骤消息，最后发送 BUILT 状态和 Deleted 消息。
