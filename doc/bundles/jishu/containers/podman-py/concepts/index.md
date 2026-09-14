# 核心概念

本目录按学习路径组织 podman-py 的核心概念文档，从快速入门与 Docker SDK 兼容性 → 四级连接配置与传输适配器 → 管理器+Mixin组合架构 → 容器六状态机生命周期 → 镜像 Rich 进度条构建 → Quadlet v5.8 高级资源+异常体系+AGENTS工程治理（00-05，R1/R2 基线）；R3（2026-09-14）续接 06-10：组编排原语（Pod/Network/Volume）→ 密钥与多架构分发（Secret/Manifest/Registry）→ 事件与三套流协议 → 构建上下文管线 → 传输/配置深化。**概念 11 篇**，建议按顺序阅读；02-managers 之后可分支 03/04 并行，05 总收束高级议题；06-10 为 R3 全量源码深化，可按需独立选读。

* [00 - 快速入门与 Docker SDK 兼容性](00-introduction.md) — Python ≥ 3.9 支持、4 组 extras 依赖、三层代码架构图（薄门面→domain Manager+Mixin→api 传输）、Docker兼容三要素（别名/双前缀/签名）、6 项不支持边界（Swarm/BuildKit/docker.types/npipe）、版本号双轨。
* [01 - 连接配置（UDS/SSH/TCP）](01-connection.md) — 四级连接优先级伪代码（connection→base_url→is_machine→本地回退）、from_env 6 双前缀环境变量表、Rootless/Rootful socket 路径对比、SSHSocket 隧道 ssh -N -L 4步骤流程图、6 scheme 路由表、6 条故障排查清单。
* [02 - 资源管理器架构](02-managers.md) — 9 个 @cached_property 管理器字母序表、Manager 基类 7 组成员骨架图、Mixin 横切扩展表（Run/Create/Build 三组合）、MRO 左端顺序的重要性、RunMixin.run 5步协作流程图、PodmanResource 基类 6+20 成员分类、G3 可迁移模式表。
* [03 - 容器生命周期操作](03-containers.md) — created/running/paused/exited/dead/restarting 六状态流转图、list/get/exists 查询三件套差异表、sparse=not compatible 默认陷阱 + reload() 补全、Create 30+ kwargs 完整示例、Run 4 分支返回代码、remove vs auto_remove 双保险表、exec_run/logs/prune、8 类异常捕获清单。
* [04 - 镜像管理与 Rich 进度条构建](04-images.md) — BuildMixin+Manager 继承链图、name→reference 过滤映射（G2洞察#3）、pull 4 policy + Rich Progress 优雅降级 5步骤、Containerfile 20+ 参数速查（含 Podman-only）、BuildError + build_log 三部曲诊断模式、push/remove/prune/search/scp 语义、7 条本节陷阱清单。
* [05 - 高级资源、异常体系与工程治理](05-advanced.md) — QuadletsManager v5.8 CRUD 速查 + install 三形态 + 6 属性 3 方法、其他 6 个高级管理器（Pods/Secrets/Volumes/Networks/Manifests/System 7直方法）、8 类异常继承链全景图 + 分层捕获 9行模板、AGENTS.md 7大AI陷阱 R1-R7 原文编号锚定、测试双态治理（unit requests-mock + integration PODMAN_BINARY+SSH预断言）、skipif 三元组+pnext前瞻用例、覆盖率双轨 80% vs 85% 处理方案 + pylint 不默认 + DCO git-validation、G3 工程治理版 5 模式表。
* [06 - Pod / Network / Volume：组编排原语与资源契约差异](06-pods-networks-volumes.md) — Pod 身份 ID 优先/stop 参数名 t/stats 默认非流；Network id 哈希推导/get 无 /json 后缀/prune 错误键 Error；IPAMPool/IPAMConfig host-local 单池与 lease_range（net[1]/net[-2]）；Volume.id==name、list 404→[]、prune 真实 Size、export/import 互斥；三资源身份-端点-语义差异矩阵与"禁止类推"原则。
* [07 - Secret / Manifest / Registry：密钥与多架构镜像分发](07-secrets-manifests-registry.md) — Secret 裸字节上送、名在 Spec.Name、exists 借用 /json；Manifest add/remove 的 PUT operation 语义、push X-Registry-Auth、list 抛 NotImplementedError；RegistryData.has_platform 的 variant 不承载；push 进度为客户端合成两条消息、load 返回生成器、prune 防 JSON null、prune_builds 不发请求。
* [08 - 事件系统与三套流协议](08-events-and-streams.md) — NDJSON 行流（events/pull/build，json_stream raw_decode 容错+chunked 错误内联）、Docker 8 字节多路复用帧（frames/stream_frames/demux_output，logs 无 demux 开关）、HTTP Upgrade 裸 socket（exec_run socket=True 劫持且禁 SSH）三协议矩阵；stream 默认值跨方法差异表（container.stats True vs pods.stats False）；attach 两方法 NotImplementedError；mermaid 消费决策流程。
* [09 - 镜像构建上下文管线](09-build-context-pipeline.md) — custom_context/fileobj/path 三入口归约 x-tar；.containerignore 优先（仅 fnmatch 无 !/**）、Containerfile 随机代理名拷贝、create_tar 四步过滤脱敏（uid=0/root）；_render_params 参数映射表（OCI 默认清单格式、未支持 kwargs 静默丢弃）；响应 tee 分叉+正则提取 image id；BuildError 诊断三部曲。
* [10 - 传输与配置深化](10-transport-deep-dive.md) — URL 一生轨迹图（scheme 改写/netlog quote_plus/双 mount/trust_env=False）、UDS 四层连接栈与 PoolKey key_uds、TLSConfig 兼容空壳（currently ignored）与 verify 一词两义、libpod /v5.8.0 与兼容 /v1.4 双前缀（/auth 唯一显式兼容端点）、containers.conf 新旧 JSON/TOML 双格式（JSON 同名覆盖）、XDG /tmp 回退 0700+lstat 防 symlink、SystemManager 五端点、prepare_filters/prepare_body 编码约定、APIResponse 参数化 404。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-connection
02-managers
03-containers
04-images
05-advanced
06-pods-networks-volumes
07-secrets-manifests-registry
08-events-and-streams
09-build-context-pipeline
10-transport-deep-dive
```
