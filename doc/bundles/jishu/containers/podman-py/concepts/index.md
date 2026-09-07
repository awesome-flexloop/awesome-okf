# 核心概念

本目录按学习路径组织 podman-py 的核心概念文档，从快速入门与 Docker SDK 兼容性 → 四级连接配置与传输适配器 → 管理器+Mixin组合架构 → 容器六状态机生命周期 → 镜像 Rich 进度条构建 → Quadlet v5.8 高级资源+异常体系+AGENTS工程治理陷阱全覆盖。**概念 6 篇**，建议按顺序阅读，02-managers 之后可分支 03/04 并行，最后 05 总收束高级议题与工程治理。

* [00 - 快速入门与 Docker SDK 兼容性](00-introduction.md) — Python ≥ 3.9 支持、4 组 extras 依赖、三层代码架构图（薄门面→domain Manager+Mixin→api 传输）、Docker兼容三要素（别名/双前缀/签名）、6 项不支持边界（Swarm/BuildKit/docker.types/npipe）、版本号双轨。
* [01 - 连接配置（UDS/SSH/TCP）](01-connection.md) — 四级连接优先级伪代码（connection→base_url→is_machine→本地回退）、from_env 6 双前缀环境变量表、Rootless/Rootful socket 路径对比、SSHSocket 隧道 ssh -N -L 4步骤流程图、6 scheme 路由表、6 条故障排查清单。
* [02 - 资源管理器架构](02-managers.md) — 9 个 @cached_property 管理器字母序表、Manager 基类 7 组成员骨架图、Mixin 横切扩展表（Run/Create/Build 三组合）、MRO 左端顺序的重要性、RunMixin.run 5步协作流程图、PodmanResource 基类 6+20 成员分类、G3 可迁移模式表。
* [03 - 容器生命周期操作](03-containers.md) — created/running/paused/exited/dead/restarting 六状态流转图、list/get/exists 查询三件套差异表、sparse=not compatible 默认陷阱 + reload() 补全、Create 30+ kwargs 完整示例、Run 4 分支返回代码、remove vs auto_remove 双保险表、exec_run/logs/prune、8 类异常捕获清单。
* [04 - 镜像管理与 Rich 进度条构建](04-images.md) — BuildMixin+Manager 继承链图、name→reference 过滤映射（G2洞察#3）、pull 4 policy + Rich Progress 优雅降级 5步骤、Containerfile 20+ 参数速查（含 Podman-only）、BuildError + build_log 三部曲诊断模式、push/remove/prune/search/scp 语义、7 条本节陷阱清单。
* [05 - 高级资源、异常体系与工程治理](05-advanced.md) — QuadletsManager v5.8 CRUD 速查 + install 三形态 + 6 属性 3 方法、其他 6 个高级管理器（Pods/Secrets/Volumes/Networks/Manifests/System 7直方法）、8 类异常继承链全景图 + 分层捕获 9行模板、AGENTS.md 7大AI陷阱 R1-R7 原文编号锚定、测试双态治理（unit requests-mock + integration PODMAN_BINARY+SSH预断言）、skipif 三元组+pnext前瞻用例、覆盖率双轨 80% vs 85% 处理方案 + pylint 不默认 + DCO git-validation、G3 工程治理版 5 模式表。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-connection
02-managers
03-containers
04-images
05-advanced
```
