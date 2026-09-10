---
type: Concept
title: 依赖图与 up/down 生命周期
description: 源码视角解析 depends_on 依赖图构建、12 种条件等待机制，以及 up 重建判定、镜像拉取策略、pod 创建与 down 清理的完整生命周期
tags: [podman, compose, source-code, lifecycle, dependencies, up-down]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
---

# 依赖图与 up/down 生命周期

本文解析 podman-compose 的运行期编排：服务间依赖如何建模与等待，`up` 如何决定"重建谁、何时拉镜像、按什么顺序启动"，以及 `down` 的清理顺序。

## 依赖模型：_deps 与 _dependents

依赖图在配置加载阶段由 `flat_deps()`（L1719）构建，每个服务得到两个内部字段：

- `_deps`：该服务**依赖谁**。来源有三：`depends_on`（归一化后为带 `condition` 的 dict）、`links`（旧式 `service:alias` 声明，别名写入被依赖方的 `_aliases` 供网络别名使用）、`extends`（被继承服务视为 `service_started` 依赖）。
- `_dependents`：由 `calc_dependents()`（L1709）反向计算的**谁依赖我**，供 down 排除与重建联动使用。

`rec_deps()`（L1685）递归展开传递依赖，同时做两道环防护：跳过自依赖（A 依赖 A）与回溯到起点的环（A→B→A）。

### 12 种依赖条件

`ServiceDependencyCondition` 枚举（L1625）包含 12 个值：`configured/created/exited/healthy/initialized/paused/removing/running/stopped/stopping/unhealthy/service_completed_successfully`。Docker 风格条件名自动映射：`service_started → running`、`service_healthy → healthy`、`service_completed_successfully` 保留。

### 条件等待：启动屏障而非看护

`check_dep_conditions()`（L3863）在容器 **start 之前**执行（见 `run_container`，L3923：仅当命令含 start 时等待）：

- 按条件分组，对每组依赖容器执行 `podman wait --condition=<条件> <容器>`；
- 命令失败（容器尚未就绪等）时每秒重试，形成轮询；
- podman 版本低于 4.6.0 时，`healthy/unhealthy` 条件不支持，仅告警跳过；`--wait` 同理。

`service_completed_successfully` 是特例（`_validate_completed_successfully`，L3812）：先以 50ms 间隔轮询直到依赖容器离开 `created` 状态（避免与启动过程竞争），再 `podman wait --condition=stopped`，最后 inspect 检查 `ExitCode` 必须为 0，否则抛错。

> 边界认知：依赖条件只在**启动时刻**构成屏障。容器启动后依赖方崩溃不会触发联动重启——运行期可靠性由 `restart` 策略或 systemd 集成承担，depends_on 不提供 HA 语义。

## up 生命周期全景

`compose_up()`（L4158）的执行顺序：

```text
1. prepare_images   预拉取/构建镜像（在拆除旧容器之前完成，缩短停机）
2. existing_containers 查询项目现存容器（标签过滤）
3. create_secrets_from_environment 从环境变量创建 podman secret
4. 重建判定         force / 镜像变化 / config-hash 变化 → recreate_services
5. down(teardown)   仅拆除需重建的服务
6. create_pods      创建 pod（若启用）
7. podman create    为缺失/需重建的容器创建容器（不启动）
8. 启动             detach：逐服务 start；前台：start -a 任务组 + 日志聚合
```

### 重建判定的三个条件

对每个现存容器（L4213-2256），满足任一即加入重建集合：

1. `--force-recreate`（且目标服务匹配，或带 `--always-recreate-deps`）；
2. **镜像 ID 变化**：通过 `podman inspect -t image -f {{.Id}}` 取当前镜像 ID，与现存容器记录的 `ImageID` 比较；
3. **配置哈希变化**：容器标签 `io.podman.compose.config-hash` 与当前服务的 `config_hash()` 不一致。

此外，被重建服务的**正在运行的依赖方（dependents）**会被联动加入重建集合——因为旧容器被拆除后，依赖它的容器也必须重新创建。

### 镜像准备与拉取策略

`prepare_images()`（L4076）：仅当 podman ≥ 5.6.0（`pull --policy` 标志引入版本）时，在拆除旧容器**之前**显式拉取镜像，使后续 create 时镜像已在本地缓存，最小化停机窗口。

拉取策略由 `PullImageSettings`（L3992）统一，优先级为 `always(3) > newer(2) > missing(1) > never/build(0)`：同一镜像被多个服务引用时取最高优先级；同时声明 `build` 与 `image` 的服务，拉取失败被忽略（随后构建兜底，符合 Compose Spec 对 build+image 的定义）。`is_local()` 判定本地镜像（`localhost/` 前缀，或有 build 段且镜像名不含 `/`），默认不参与 pull。

构建走独立的拓扑调度：`additional_contexts` 中的 `service:<名>` 引用被解析为 `docker://<镜像>` 并形成 `build_deps`（`_resolve_context_dependencies`，L3092，含循环依赖检测），`compose_build` 按依赖分层并行构建。

### pod 创建

`create_pods()`（L3772）在容器创建前执行：pod 已存在则跳过，否则 `podman pod create --name=<名> <pod 参数>`。pod 名解析优先级：`--in-pod` > `x-podman.in_pod` > 默认 `pod_<项目名>`；`--in-pod=false` 禁用。默认 pod 参数为 `--infra=false --share=`（`resolve_pod_args`，L2581），可由 `--pod-args` 覆盖。

### 前台模式的任务组语义

非 detach 模式下，每个服务启动一个 `podman start -a <容器>` 协程并聚合彩色日志：

- SIGINT（非 Windows）：触发 `handle_sigint`，先执行一次 down 优雅清理，再取消所有任务；
- `--abort-on-container-exit`：任一容器退出即取消其余任务；
- `--abort-on-container-failure`：仅当某容器以非零码退出才中止；
- `--exit-code-from <服务>`：隐含 abort-on-exit，并把指定服务的退出码作为整体退出码传播。

任务取消时子进程收到 terminate，10 秒未退出才升级为 kill（见[单文件架构](04-source-architecture.md)）。

## down 生命周期

`compose_down()`（L4445）的顺序与 up 严格相反：

1. **计算排除集**：方向与 up 相反，使用 `_dependents`——停止指定服务时保留其依赖方；
2. **逆序并行停止**：容器列表反转后并行 `podman stop`，超时取 `--timeout` 或服务的 `stop_grace_period`（默认 10 秒，`str_to_seconds` 解析）；
3. **顺序删除容器** `podman rm`；
4. `--remove-orphans`：按项目标签查出全部容器，减去当前 compose 定义的服务，孤儿逐个 stop/rm；
5. `-v/--volumes`：按标签列出项目卷并删除，但**保留排除集服务仍在使用的卷**；
6. `--rmi local/all`：删除镜像，`local` 模式经 `is_local()` 过滤只删本地构建镜像；
7. 最后删除 pod 与项目网络（同样靠标签枚举）。

## 其他命令的生命周期要点

- `run`（L4549）：一次性容器。先以 detach 模式 up 依赖服务，再按需构建；容器名改为随机临时名（`<项目>_<服务>_tmp<随机数>`），默认不发布服务端口（`--service-ports` 可开启），`--rm` 时删除 restart 策略，最终执行 `podman run`。
- `start/stop/restart`（L4708 `transfer_service_status`）：stop/restart 逆序、并行执行；start 后可选 `--wait` 等待 running|healthy（podman < 4.6.0 跳过）。
- `logs`：每个服务一个 `podman logs` 协程，前缀着色与前台 up 同一套机制。
- `systemd`（L3412）：register 把 `COMPOSE_/PODMAN_` 前缀环境变量写入 `~/.config/containers/compose/projects/<项目>.env`；create-unit 生成 `/etc/systemd/user/podman-compose@.service`（`ExecStartPre` 先 `up --no-start` 再 `podman pod start`，`ExecStart` 为 `wait`），从而把生命周期托管给用户级 systemd（配合 `loginctl enable-linger` 实现开机驻留）。

## 相关概念

- [CLI 翻译层与标签状态](05-cli-translation-layer.md)：config-hash 与项目标签的生成方式
- [单文件架构与 asyncio 执行模型](04-source-architecture.md)：任务组、信号量与取消语义
- [配置加载管线](06-config-pipeline.md)：depends_on 归一化与服务拓扑排序
- [Compose 文件常见模式](03-compose-patterns.md)：depends_on/profiles/scale 的配置写法
- [源码信源登记](../references/source-code-map.md)：行号与符号索引
