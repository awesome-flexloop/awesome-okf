---
type: Facts
okf_version: "0.2"
title: "enterprise-gateway 源码事实清单"
tags: [jupyter, kubernetes, enterprise, kernel-gateway, yarn, remote-kernel]
generated: "2026-08-22"
sources:
  - ../../../../../external/libs/jupyter/enterprise_gateway/pyproject.toml
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/__init__.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/_version.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/__main__.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/enterprisegatewayapp.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/mixins.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/kernels/remotemanager.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/kernels/handlers.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/processproxy.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/container.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/k8s.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/yarn.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/distributed.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/docker_swarm.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/conductor.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/crd.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/spark_operator.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/sessions/kernelsessionmanager.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/sessions/sessionmanager.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/sessions/handlers.py
  - ../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/client/gateway_client.py
---

# enterprise-gateway 源码事实清单

## 项目元数据

- F-001: pyproject.toml:6 — 包名为 `jupyter_enterprise_gateway`，版本为 `3.4.0.dev0`。
- F-002: pyproject.toml:8 — 项目描述为 "A web server for spawning and communicating with remote Jupyter kernels"。
- F-003: pyproject.toml:9 — 许可证为 BSD License（LICENSE.md 文件）。
- F-004: pyproject.toml:18-19 — 支持 Python 3.10 和 3.11 两个版本。
- F-005: pyproject.toml:21 — 要求 Python >= 3.10。
- F-006: pyproject.toml:22-39 — 核心依赖包括 docker>=3.5.0、jinja2>=3.1、jupyter_client>=6.1.12<7、jupyter_core>=4.7.0、kubernetes>=18.20.0、jupyter_server>=1.7<2.0、paramiko>=2.11、pexpect>=4.8.0、pycryptodomex>=3.9.7、pyzmq>=20.0<25.0、requests>=2.14.2、tornado>=6.1<7.0、traitlets>=5.3.0、watchdog>=2.1.3、yarn-api-client>=1.0。
- F-007: pyproject.toml:26 — jupyter_client 版本上限 <7，注释说明待支持 kernel provisioners 后移除。
- F-008: pyproject.toml:29 — jupyter_server 版本上限 <2.0，同样待支持 provisioners。
- F-009: pyproject.toml:53 — CLI 入口点为 `jupyter-enterprisegateway = enterprise_gateway.enterprisegatewayapp:launch_instance`。
- F-010: pyproject.toml:76 — wheel 构建仅包含 enterprise_gateway 包。
- F-011: enterprise_gateway/_version.py:6 — 版本号硬编码为 `3.4.0.dev0`。
- F-012: enterprise_gateway/__init__.py:8-10 — 提供 `launch_instance` 延迟加载入口，从 enterprisegatewayapp 模块导入。

## 目录结构

- F-013: enterprise_gateway/enterprisegatewayapp.py — 主应用文件，定义 EnterpriseGatewayApp 类。
- F-014: enterprise_gateway/mixins.py — 包含 CORS、Token 认证、JSON 错误等 Tornado Mixin 以及配置 Mixin。
- F-015: enterprise_gateway/services/kernels/ — 内核管理服务目录，含 remotemanager.py 和 handlers.py。
- F-016: enterprise_gateway/services/kernels/remotemanager.py — 远程内核管理器，定义 RemoteMappingKernelManager 和 RemoteKernelManager。
- F-017: enterprise_gateway/services/processproxies/ — 进程代理目录，包含所有远程后端实现。
- F-018: enterprise_gateway/services/processproxies/processproxy.py — 进程代理抽象基类及本地/远程基础实现。
- F-019: enterprise_gateway/services/processproxies/container.py — 容器类进程代理基类 ContainerProcessProxy。
- F-020: enterprise_gateway/services/processproxies/k8s.py — Kubernetes Pod 进程代理。
- F-021: enterprise_gateway/services/processproxies/yarn.py — YARN 集群进程代理。
- F-022: enterprise_gateway/services/processproxies/distributed.py — 分布式（SSH）进程代理。
- F-023: enterprise_gateway/services/processproxies/docker_swarm.py — Docker Swarm 和 Docker 进程代理。
- F-024: enterprise_gateway/services/processproxies/conductor.py — IBM Spectrum Conductor 进程代理。
- F-025: enterprise_gateway/services/processproxies/crd.py — Kubernetes CRD（自定义资源）进程代理。
- F-026: enterprise_gateway/services/processproxies/spark_operator.py — Spark Operator 进程代理。
- F-027: enterprise_gateway/services/sessions/ — 会话管理服务目录。
- F-028: enterprise_gateway/services/sessions/kernelsessionmanager.py — 内核会话持久化管理器（文件/Webhook）。
- F-029: enterprise_gateway/client/gateway_client.py — 实验性客户端 GatewayClient，用于集成测试。
- F-030: etc/kernel-launchers/ — 内核启动脚本目录，包含 Python/R/Scala/Docker/Kubernetes/Operators 等多种 launcher。
- F-031: etc/kernelspecs/ — 内核规格目录，包含 R/Python/Scala/Docker/Kubernetes/YARN/Conductor/Spark Operator 等 25+ 种 kernel.json。
- F-032: etc/kubernetes/helm/ — Helm Chart 目录，用于 Kubernetes 部署。

## GatewayApp 主应用

- F-033: enterprisegatewayapp.py:56 — EnterpriseGatewayApp 继承 EnterpriseGatewayConfigMixin 和 JupyterApp。
- F-034: enterprisegatewayapp.py:67 — 应用名为 `jupyter-enterprise-gateway`。
- F-035: enterprisegatewayapp.py:76-81 — 注册的可配置类包括 KernelSpecCache、FileKernelSessionManager、WebhookKernelSessionManager、RemoteMappingKernelManager。
- F-036: enterprisegatewayapp.py:86-98 — initialize() 方法依次调用 init_configurables()、init_webapp()、init_http_server()。
- F-037: enterprisegatewayapp.py:104 — 使用标准 jupyter_client 的 KernelSpecManager。
- F-038: enterprisegatewayapp.py:120-126 — 内核管理器使用 kernel_manager_class 配置，默认为 RemoteMappingKernelManager。
- F-039: enterprisegatewayapp.py:128 — SessionManager 使用自定义的 sessionmanager。
- F-040: enterprisegatewayapp.py:130-135 — 内核会话管理器使用可配置类，默认为 FileKernelSessionManager。
- F-041: enterprisegatewayapp.py:139-154 — 会话持久化与 availability_mode 联动：启用持久化自动设置 replication 模式；设置 availability_mode 自动启用持久化。
- F-042: enterprisegatewayapp.py:157-158 — standalone 模式下在启动时自动恢复持久化的内核会话。
- F-043: enterprisegatewayapp.py:160 — contents_manager 设为 None，网关不使用内容管理器。
- F-044: enterprisegatewayapp.py:164-187 — 请求处理器由 api、kernel、kernelspec、session、base 五组 handler 组合而成，路径挂载在 base_url 下。
- F-045: enterprisegatewayapp.py:218-219 — 使用可配置的 authorizer_class，默认为 AllowAllAuthorizer。
- F-046: enterprisegatewayapp.py:221-254 — Tornado Application 设置包含内核管理器、会话管理器、认证 Token、CORS 头、最大内核数、环境变量白名单、用户授权列表等。
- F-047: enterprisegatewayapp.py:248 — allow_remote_access 强制设为 True，允许远程访问。
- F-048: enterprisegatewayapp.py:279-303 — HTTP 服务器支持端口重试，默认最多尝试 50 个端口。
- F-049: enterprisegatewayapp.py:316-324 — impersonation 模式下若网关用户不在 unauthorized_users 中，发出安全警告。
- F-050: enterprisegatewayapp.py:342-353 — shutdown() 遍历所有内核 ID 并强制关闭每个内核。
- F-051: enterprisegatewayapp.py:373-407 — 动态配置更新机制：通过 PeriodicCallback 轮询配置文件修改时间，热更新 Configurable 实例。
- F-052: enterprisegatewayapp.py:429-453 — 动态配置注册包括 EnterpriseGatewayApp、MappingKernelManager、KernelSpecManager、KernelSessionManager 四类对象。

## 远程内核管理

- F-053: remotemanager.py:159 — RemoteMappingKernelManager 继承 AsyncMappingKernelManager。
- F-054: remotemanager.py:164-183 — 覆盖 _context_default()，可通过 EG_ZMQ_MAX_SOCKETS 和 EG_ZMQ_IO_THREADS 环境变量调整 ZMQ 上下文参数。
- F-055: remotemanager.py:185-187 — 使用 TrackPendingRequests 类追踪待处理的内核启动请求，用于异步竞争条件下的限流。
- F-056: remotemanager.py:209-234 — start_kernel() 先检查内核数量限制，然后调用父类 start_kernel，之后创建会话记录。
- F-057: remotemanager.py:236-247 — restart_kernel() 使用 restarting 标志防止重复重启请求。
- F-058: remotemanager.py:282-325 — _enforce_kernel_limits() 同时检查全局 max_kernels 和每用户 max_kernels_per_user 限制，超限返回 403。
- F-059: remotemanager.py:338-417 — start_kernel_from_session() 用于 HA 场景下从持久化会话恢复内核，重建 process proxy 并验证存活。
- F-060: remotemanager.py:427 — RemoteKernelManager 继承 EnterpriseGatewayConfigMixin 和 AsyncIOLoopKernelManager。
- F-061: remotemanager.py:453-454 — 禁用 cache_ports（设置为 False），因为远程内核不需要端口缓存且会干扰本地端口范围限制。
- F-062: remotemanager.py:466-494 — _link_dependent_props() 使用 traitlets directional_link 将 EG 实例的配置属性（authorized_users、port_range、impersonation_enabled、yarn_endpoint 等）双向同步到 KernelManager。
- F-063: remotemanager.py:496-508 — start_kernel() 先调用 _get_process_proxy() 获取进程代理，再捕获用户覆盖参数，最后调用父类。
- F-064: remotemanager.py:531-555 — format_kernel_cmd() 替换命令中的 {response_address}、{public_key}、{port_range}、{kernel_id} 模板变量。
- F-065: remotemanager.py:557-582 — _launch_kernel() 先应用 user_overrides，设置 KERNEL_GATEWAY=1，移除 EG/KG_AUTH_TOKEN，然后委托给 process_proxy.launch_process()。
- F-066: remotemanager.py:595-648 — restart_kernel() 对于远程内核在无连接时跳过自动重启（避免孤儿进程）；重启后重建活动监控。
- F-067: remotemanager.py:650-686 — signal_kernel() 支持 EG_ALTERNATE_SIGINT 环境变量为特定语言（如 Scala）配置替代中断信号。
- F-068: remotemanager.py:723-743 — write_connection_file() 对远程内核使用 response_address 模式时跳过本地连接文件写入，避免分配无用端口。
- F-069: remotemanager.py:745-762 — _get_process_proxy() 从 kernelspec.metadata.process_proxy 读取配置，动态 import 并实例化进程代理类。
- F-070: remotemanager.py:62-86 — get_process_proxy_config() 函数从 kernelspec metadata 提取 process_proxy 配置，默认返回 LocalProcessProxy。
- F-071: remotemanager.py:89-128 — new_kernel_id() 支持客户端通过 KERNEL_ID 环境变量指定内核 ID，需为有效的 UUID v4。

## 进程代理（Process Proxy）

- F-072: processproxy.py:397 — BaseProcessProxyABC 是进程代理抽象基类，使用 abc.ABCMeta 元类。
- F-073: processproxy.py:405 — 构造函数接收 kernel_manager 和 proxy_config 两个参数。
- F-074: processproxy.py:421 — 初始化时将 kernel_manager.ip 设为 "0.0.0.0"，防止本地限制干扰远程内核。
- F-075: processproxy.py:485-535 — launch_process() 是抽象方法，基类实现设置 KERNEL_ID、KERNEL_LANGUAGE，执行授权检查，并过滤敏感环境变量日志。
- F-076: processproxy.py:555-565 — poll() 对本地进程调用 local_proc.poll()，对远程进程发送信号 0 检测存活。
- F-077: processproxy.py:590-616 — send_signal() 优先使用 local_proc 发信号，否则根据 IP 判断本地/远程选择 local_signal/remote_signal。
- F-078: processproxy.py:618-643 — kill() 先发送 SIGTERM 优雅终止，轮询等待 max_poll_attempts 次后发送 SIGKILL 强杀。
- F-079: processproxy.py:673-724 — _get_ssh_client() 使用 paramiko 创建 SSH 连接，支持密码认证、密钥认证和 GSS 认证。
- F-080: processproxy.py:804-849 — _enforce_authorization() 检查 KERNEL_USERNAME 是否在 unauthorized_users 或 authorized_users 中，不合法则抛出 403。
- F-081: processproxy.py:851-871 — get_process_info()/load_process_info() 序列化/反序列化 pid、pgid、ip 用于会话持久化。
- F-082: processproxy.py:873-945 — _validate_port_range() 验证端口范围配置：最小范围 1000 端口，有效范围 1024-65535。
- F-083: processproxy.py:947-1008 — select_ports()/select_socket() 在配置的端口范围内随机选择可用端口。
- F-084: processproxy.py:1035 — LocalProcessProxy 继承 BaseProcessProxyABC，管理本地启动的内核进程。
- F-085: processproxy.py:1045 — LocalProcessProxy 初始化时将 kernel_manager.ip 设为 localhost。
- F-086: processproxy.py:1070 — RemoteProcessProxy 是远程进程代理抽象基类，继承 BaseProcessProxyABC。
- F-087: processproxy.py:1088-1093 — RemoteProcessProxy 使用单例 ResponseManager，注册 kernel_id 事件，设置 response_address 和 public_key。
- F-088: processproxy.py:144-160 — ResponseManager 是 SingletonConfigurable 单例，管理 RSA 密钥对和响应 socket。
- F-089: processproxy.py:162 — RSA 密钥大小为 1024 位，仅用于加密 AES 密钥。
- F-090: processproxy.py:207-252 — ResponseManager 在端口 8877（可配置）上监听，接受远程 launcher 的连接信息回传。
- F-091: processproxy.py:295-379 — _decode_payload() 支持 v1（RSA+AES 混合加密）和 v0（legacy，kernel_id 前16字节作 AES 密钥）两种响应格式。
- F-092: processproxy.py:1139-1201 — _tunnel_to_kernel() 通过 SSH 隧道转发 5 个 ZMQ 端口，要求无密码 SSH 登录。
- F-093: processproxy.py:1297-1323 — receive_connection_info() 通过 ResponseManager 异步等待 launcher 回传连接信息，超时则 kill 内核。
- F-094: processproxy.py:1499-1532 — _send_listener_request() 通过 comm_port 向 launcher listener 发送 JSON 请求（如信号、关闭指令）。
- F-095: processproxy.py:1534-1565 — RemoteProcessProxy.send_signal() 优先通过 comm_port 发送信号，失败则回退到 SSH kill。

## Kubernetes 支持

- F-096: k8s.py:34 — 模块加载时调用 config.load_incluster_config()，默认假设运行在 K8s 集群内部。
- F-097: k8s.py:26 — 默认命名空间由 EG_NAMESPACE 环境变量控制，默认为 "default"。
- F-098: k8s.py:57 — KubernetesProcessProxy 继承 ContainerProcessProxy，object_kind 为 "Pod"。
- F-099: k8s.py:96-98 — 初始状态集为 {"pending", "running"}，错误状态集为 {"failed"}。
- F-100: k8s.py:104-131 — get_container_status() 通过 label selector `kernel_id=<id>,component=kernel` 查询 Pod，Running 时捕获 pod_ip 和 host_ip。
- F-101: k8s.py:157-237 — terminate_container_resources() 先删除 Pod，若自创建了 namespace 且非重启场景则删除 namespace，同时清理 kpt 模板文件。
- F-102: k8s.py:275-312 — _determine_kernel_pod_name() 支持 Jinja2 风格模板变量替换，DNS 合规化处理（小写、非法字符转横线）。
- F-103: k8s.py:314-339 — _determine_kernel_namespace() 可由客户端指定 KERNEL_NAMESPACE，或共享网关命名空间，否则为每个内核创建独立 namespace。
- F-104: k8s.py:351-400 — _create_kernel_namespace() 创建带标签的 namespace，并创建 RoleBinding 绑定 ClusterRole（默认 cluster-admin）。
- F-105: crd.py:18 — CustomResourceProcessProxy 继承 KubernetesProcessProxy，object_kind 为 "CustomResourceDefinition"。
- F-106: crd.py:67-74 — get_container_status() 使用 CustomObjectsApi 查询 CRD 状态，先检查 CRD 的 applicationState，Running 后再委托父类检查 Pod。
- F-107: spark_operator.py:11 — SparkOperatorProcessProxy 继承 CustomResourceProcessProxy，管理 sparkoperator.k8s.io/v1beta2 的 SparkApplication 资源。

## YARN 支持

- F-108: yarn.py:42 — YarnClusterProcessProxy 继承 RemoteProcessProxy。
- F-109: yarn.py:47-48 — 初始状态集为 {NEW, SUBMITTED, ACCEPTED, RUNNING}，终止状态集为 {FINISHED, KILLED, FAILED}。
- F-110: yarn.py:84-124 — _initialize_resource_manager() 初始化 YARN ResourceManager 客户端，支持 Kerberos/SPNEGO 认证和 SimpleAuth。
- F-111: yarn.py:154-254 — confirm_yarn_queue_availability() 提交前检查队列资源：容器内存是否足够、分区容量是否低于阈值（默认 95%），最多等待 20% 的 kernel_launch_timeout。
- F-112: yarn.py:270-287 — poll() 查询 YARN app 状态，初始状态视为存活（返回 None）。
- F-113: yarn.py:454-482 — _get_application_id() 通过 kernel_id 作为 app 名称查询 YARN apps API 获取 application ID，忽略终止状态的 app。
- F-114: yarn.py:437-452 — _get_application_state() 查询 app 状态，首次发现 amHostHttpAddress 时解析 assigned_host 和 assigned_ip。

## Docker 支持

- F-115: docker_swarm.py:27 — 使用 DockerClient.from_env() 创建 Docker 客户端。
- F-116: docker_swarm.py:30 — DockerSwarmProcessProxy 继承 ContainerProcessProxy，管理 Docker Swarm 服务。
- F-117: docker_swarm.py:50-56 — Swarm 初始状态为 {preparing, starting, running}，错误状态为 {failed, rejected, complete, shutdown, orphaned, remove}。
- F-118: docker_swarm.py:167 — DockerProcessProxy 继承 ContainerProcessProxy，管理单个 Docker 容器（非 Swarm）。
- F-119: docker_swarm.py:183-189 — Docker 模式初始状态为 {created, running}，错误状态为 {restarting, removing, paused, exited, dead}。
- F-120: container.py:60-61 — 默认禁止 UID 0（root）和 GID 0，通过 EG_PROHIBITED_UIDS/EG_PROHIBITED_GIDS 环境变量配置。
- F-121: container.py:81-104 — _determine_kernel_images() 从 proxy_config.image_name 或 EG_KERNEL_IMAGE 环境变量确定镜像，支持 executor 镜像。

## 分布式（SSH）支持

- F-122: distributed.py:25-63 — TrackKernelOnHost 类维护主机到内核的映射计数，支持 least-connection 负载均衡。
- F-123: distributed.py:65 — DistributedProcessProxy 继承 RemoteProcessProxy，通过 SSH 在多主机间分发内核。
- F-124: distributed.py:78 — 负载均衡算法由 EG_LOAD_BALANCING_ALGORITHM 控制，支持 round-robin 和 least-connection。
- F-125: distributed.py:147-179 — _build_startup_command() 为远程主机构建 nohup 命令，导出所有环境变量，重定向日志到 /tmp/kernel-<id>.log，后台运行并 echo PID。
- F-126: distributed.py:181-195 — _determine_next_host() 支持客户端通过 KERNEL_REMOTE_HOST 指定目标主机。

## Conductor 支持

- F-127: conductor.py:31 — ConductorClusterProcessProxy 继承 RemoteProcessProxy，支持 IBM Spectrum Conductor 集群。
- F-128: conductor.py:36-37 — 初始状态集为 {SUBMITTED, WAITING, RUNNING}，终止状态集为 {FINISHED, KILLED, RECLAIMED}。
- F-129: conductor.py:65-78 — 认证支持 EGO_SERVICE_CREDENTIAL 或 JWT Token（从 kernel_headers 的 Jwt-Auth-User-Payload 获取 accessToken）。
- F-130: conductor.py:657-770 — _performConductorJWTLogonAndRetrieval() 执行 JWT 登录→EGO Token 登录→获取 Anaconda 路径→获取实例组信息的完整流程。

## 会话/API

- F-131: kernelsessionmanager.py:26 — KernelSessionManager 是抽象基类，提供内核会话的创建、刷新、删除、启动（HA 恢复）能力。
- F-132: kernelsessionmanager.py:47-52 — enable_persistence 默认 False，由 EG_KERNEL_SESSION_PERSISTENCE 环境变量控制。
- F-133: kernelsessionmanager.py:82-111 — create_session() 保存 kernel_id、username、kernel_name、connection_info、launch_args、process_info。
- F-134: kernelsessionmanager.py:330 — FileKernelSessionManager 将会话持久化到 JUPYTER_DATA_DIR/kernel_sessions/ 下的 JSON 文件。
- F-135: kernelsessionmanager.py:408 — WebhookKernelSessionManager 通过 REST API（GET/POST/DELETE）持久化到外部 Webhook 服务，支持 Basic/Digest 认证。
- F-136: kernels/handlers.py:35-37 — MainKernelHandler 通过 Mixin 叠加 Token 认证、CORS、JSON 错误处理，继承 jupyter_server 的 MainKernelHandler。
- F-137: kernels/handlers.py:32 — PROHIBITED_ENV_VALUE_CHARS 禁止环境变量值包含 `$``（反引号）、换行、回车、null 字符，防止 shell 注入。
- F-138: kernels/handlers.py:50-72 — _build_kernel_env() 仅允许 KERNEL_ 前缀的环境变量和 client_envs 白名单中的变量透传，值长度限制 4096。
- F-139: kernels/handlers.py:192-200 — default_handlers 动态包装 jupyter_server 的所有 handler，统一加上 Token、CORS、JSONErrors Mixin。
- F-140: mixins.py:75-108 — TokenAuthorizationMixin 在 prepare() 中检查 token 参数或 Authorization header，不匹配返回 401。
- F-141: mixins.py:35-72 — CORSMixin 通过 SETTINGS_TO_HEADERS 映射注入 CORS 响应头。
- F-142: mixins.py:111-158 — JSONErrorsMixin 将错误响应统一为 JSON 格式 `{"reason": ..., "message": ...}`。

## 认证与安全

- F-143: mixins.py:216-223 — auth_token 由 EG_AUTH_TOKEN 环境变量配置，支持通过 ?token= 参数或 Authorization: token <value> header 传递。
- F-144: mixins.py:566-576 — impersonation_enabled 由 EG_IMPERSONATION_ENABLED 控制，启动内核时以 KERNEL_USERNAME 身份执行。
- F-145: mixins.py:579-594 — unauthorized_users 默认为 {"root"}，匹配 KERNEL_USERNAME（大小写敏感）则禁止启动内核。
- F-146: mixins.py:597-611 — authorized_users 为白名单模式，非空时仅允许列表内用户启动内核。
- F-147: mixins.py:614-621 — authorized_origin 通过 SSL 证书主机名匹配验证请求来源，要求 TLS 启用。
- F-148: mixins.py:766-789 — authorizer_class 默认为 AllowAllAuthorizer，可通过 EG_AUTHORIZER_CLASS 配置自定义授权器。
- F-149: mixins.py:273-285 — trust_xheaders 由 EG_TRUST_XHEADERS 控制，信任 X-Forwarded-For 等反向代理头。
- F-150: processproxy.py:61 — 敏感环境变量键名通过 EG_SENSITIVE_ENV_KEYS 配置，日志中用 EG_REDACTION_MASK（默认 "********"）替换。
