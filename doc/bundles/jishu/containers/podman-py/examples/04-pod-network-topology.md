---
type: Example
title: 04 - 多容器 Pod 网络拓扑实战（自定义子网 + Secret + Volume + 事件流）
description: 用 IPAM 租约创建 bridge 网络、Secret 裸字节上送、命名卷挂载、Pod 内容器组协同（app+sidecar），并以 events NDJSON 流后台监听全生命周期，含幂等清理与 404 异常映射
tags: [podman-py, example, pods, networks, ipam, secrets, volumes, events, rootless]
generated:
  by: source-code-to-okf-wiki/sc-20260914-podman-py-wiki
  at: 2026-09-14
verified:
  by: process:seven-concepts-v
  at: 2026-09-14
status: stable
stale_after: 2027-09-14
sources:
  - id: src-code-map
    resource: /references/source-code-map.md
    title: podman-py vendor 全量源码信源登记（commit 5dd81b4）
  - id: src-container-ops
    resource: /examples/02-container-ops.md
    title: 三服务编排生命周期（R2 示例基线）
---

# 04 - 多容器 Pod 网络拓扑实战（自定义子网 + Secret + Volume + 事件流）

本例把 [06 Pod/Network/Volume](../concepts/06-pods-networks-volumes.md)、[07 Secret/Manifest](../concepts/07-secrets-manifests-registry.md)、[08 事件流](../concepts/08-events-and-streams.md) 的概念串成一个可运行脚本：在**自定义 bridge 子网**里创建一个含两个容器的 **Pod**（app + sidecar），为其挂载**命名卷**与 **Secret**，同时用 `events()` 后台 NDJSON 流监听全过程，最后按依赖逆序幂等清理。

- Pod 内 app 与 sidecar 共享 network/UTS/IPC 命名空间，经 **localhost** 互访；
- Pod 外再挂一张自定义网络（演示 `networks={name: {}}` 端点配置）；
- Secret 默认在容器内落到 `/run/secrets/<source>`（[07](../concepts/07-secrets-manifests-registry.md) 记载的 source 默认回退）；
- rootless 环境直接可跑（socket 经 `from_env()`/本地回退自动解析）。

## 前置条件

```bash
pip install "podman>=5.8.0"
podman info --format '{{.Version.Version}}'   # 建议 ≥ 5.8
podman network exists okf04net || true        # 仅人工预检，脚本自身幂等
```

## 完整脚本

```python
"""
podman-py R3 示例：Pod + 自定义网络 + Secret/Volume + 事件流监听。
对应概念文档：06 / 07 / 08。所有 API 用法均可在 vendor/podman-py
commit 5dd81b4 源码中找到对应端点。
"""
import queue
import threading
from datetime import datetime, timezone

from podman import PodmanClient
from podman.domain.ipam import IPAMConfig, IPAMPool
from podman.errors import APIError, NotFound

POD_NAME = "okf04-pod"
NET_NAME = "okf04net"
VOL_NAME = "okf04data"
SEC_NAME = "okf04-token"


def listen_events(client: PodmanClient, sink: queue.Queue, stop: threading.Event) -> None:
    """后台线程：消费 /events NDJSON 流（协议①），只收 container/pod 两类事件。"""
    try:
        # since 接受 tz-aware datetime；decode=True 时每行直接是 dict
        for event in client.events(
            since=datetime.now(timezone.utc),
            decode=True,
            filters={"type": "container"},
        ):
            sink.put(event)
            if stop.is_set():
                break
    except APIError as exc:
        sink.put({"_listener_error": str(exc)})


def fetch_or_create_network(client: PodmanClient):
    # get 端点不带 /json 后缀；exists 走 /networks/{key}/exists
    if client.networks.exists(NET_NAME):
        return client.networks.get(NET_NAME)

    # IPAM：host-local 驱动，Podman 仅支持一个 pool；IPRange 会被换算成
    # lease_range.start_ip=net[1] / end_ip=net[-2]（跳过网络与广播地址）
    pool = IPAMPool(
        subnet="10.89.0.0/24",
        iprange="10.89.0.128/25",
        gateway="10.89.0.1",
    )
    return client.networks.create(
        NET_NAME,
        driver="bridge",
        ipam=IPAMConfig(driver="host-local", pool_configs=[pool]),
    )


def main() -> None:
    sink: queue.Queue = queue.Queue()
    stop = threading.Event()

    with PodmanClient() as client:
        assert client.ping(), "Podman 服务不可达（HEAD /_ping 失败）"

        listener = threading.Thread(
            target=listen_events, args=(client, sink, stop), daemon=True
        )
        listener.start()

        try:
            # 1) 网络 / 卷 / 密钥 —— 三种资源各自的幂等语义
            network = fetch_or_create_network(client)

            volume = (
                client.volumes.get(VOL_NAME)
                if client.volumes.exists(VOL_NAME)
                else client.volumes.create(VOL_NAME)
            )

            # Secret.create 的 data 是原始字节（非 JSON），name/driver 走 query
            try:
                secret = client.secrets.get(SEC_NAME)
            except NotFound:
                secret = client.secrets.create(SEC_NAME, b"okf04-demo-token\n")

            # 2) 清理同名旧 Pod（force 连内容器一起停删）
            try:
                client.pods.get(POD_NAME).remove(force=True)
            except NotFound:
                pass

            pod = client.pods.create(POD_NAME)

            # 3) Pod 内两个容器（共享 localhost）；app 额外挂卷与密钥
            app = client.containers.create(
                "quay.io/libpod/alpine:latest",
                command=["sh", "-c", "cat /run/secrets/okf04-token; sleep 60"],
                pod=pod,                                 # Pod 实例自动取 .id
                name="okf04-app",
                networks={network.name: {}},             # 空 dict 是合法端点配置
                volumes={VOL_NAME: {"bind": "/data", "mode": "rw"}},  # 命名卷
                secrets=[
                    secret,                              # Secret 实例 → {"source": id}
                    {"source": SEC_NAME, "target": "token", "mode": "0440"},
                ],
                environment={"DEMO": "okf04"},
            )
            sidecar = client.containers.create(
                "quay.io/libpod/alpine:latest",
                command=["sh", "-c", "sleep 60"],
                pod=pod,
                name="okf04-sidecar",
            )

            # 4) 组级启动；Pod 动作方法走 POST /pods/{id}/start 等
            pod.start()
            app.reload()

            # 5) 验证：Pod 内通过 localhost 共享网络；exec 走两段式 /exec 协议
            code, output = sidecar.exec_run(
                ["sh", "-c", "wget -qO- http://127.0.0.1:9999 || true; echo sidecar-ok"]
            )
            print("sidecar exec:", code, output.decode().strip())

            # Pod 资源占用（非流式需 decode=True 才是 dict，否则为原始字节）
            stats = list(client.pods.stats(name=POD_NAME, stream=True, decode=True))
            print("pod stats frames:", len(stats))

        finally:
            # 6) 逆序清理：Pod（force 带走成员容器）→ 密钥 → 卷 → 网络
            stop.set()
            listener.join(timeout=2)

            try:
                client.pods.get(POD_NAME).remove(force=True)
            except NotFound:
                pass

            # 注意各 remove 签名不同：networks/volumes 接 force，secrets 只接 all
            for cleanup in (
                lambda: client.secrets.remove(SEC_NAME),
                lambda: client.volumes.remove(VOL_NAME, force=True),
                lambda: client.networks.remove(NET_NAME, force=True),
            ):
                try:
                    cleanup()
                except NotFound:
                    pass

        # 7) 输出监听到的事件（create/start/remove 等 Action）
        actions = []
        while not sink.empty():
            event = sink.get()
            if "_listener_error" in event:
                print("listener error:", event["_listener_error"])
                continue
            actor = event.get("Actor", {}).get("Attributes", {})
            actions.append(f'{event.get("Action")}:{actor.get("name", event.get("id", "")[:12])}')
        print("observed events:", ", ".join(actions) or "(无事件：检查 since 时钟)")


if __name__ == "__main__":
    main()
```

## 关键 API 与源码对应

| 脚本用法 | libpod 端点 / 行为 | 源码出处（commit 5dd81b4） |
|---------|--------------------|---------------------------|
| `client.ping()` | HEAD `/_ping` 返 bool | domain/system.py |
| `networks.create(..., ipam=IPAMConfig(...))` | POST `/networks/create`；IPAM 转 subnets/lease_range | networks_manager.py `_prepare_ipam`、ipam.py |
| `secrets.create(name, bytes)` | POST `/secrets/create`（裸字节 body） | secrets.py |
| `pods.create` / `pod.start/remove` | `/pods/create`、POST `/pods/{id}/start`、DELETE `?force=` | pods_manager.py / pods.py |
| `containers.create(pod=, networks=, volumes=, secrets=)` | POST `/libpod/containers/create` 透传 | containers_create.py（Pod 取 id；Secret→`{"source": id}`；命名卷→volumes，目录→mounts） |
| `pods.stats(stream=True, decode=True)` | GET `/pods/stats?namesOrIDs=` NDJSON | pods_manager.py（默认 stream=False，本例显式流式） |
| `client.events(decode=True)` | GET `/events?stream=true` 行流 | events.py（门面每次现建 EventsManager） |
| `sidecar.exec_run(cmd)` | POST `/containers/{name}/exec` + `/exec/{id}/start` | containers.py |

## 预期结果（要点）

- `sidecar exec` 返回退出码与 `sidecar-ok`（app 未监听 9999，wget 输出被 `|| true` 吞掉属预期）；
- `pod stats frames` 至少 1 帧 JSON；
- `observed events` 包含 `create:okf04-app`、`start:okf04-app`、`cleanup/remove` 等动作（事件到达略有延迟，线程 join 留出 2 秒排水）；
- 清理后 `podman pod ls`、`podman network ls`、`podman volume ls`、`podman secret ls` 中均无 `okf04-*` 残留。

## 排障清单

| 现象 | 原因与处理 |
|------|-----------|
| `events()` 阻塞且无输出 | 它是无限长连接流；必须放后台线程并自行设停止信号，不要在主线程直接迭代 |
| 事件时间为空 | `since` 用了 naive datetime 或宿主时钟偏差；统一用 `datetime.now(timezone.utc)` |
| `pods.stats(decode=False)` 拿到 bytes 不是 dict | 非流式默认返回原始 content；流式也要 `decode=True` 才给 dict（见 [06 §6.1.3](../concepts/06-pods-networks-volumes.md)） |
| 网络删除失败 | 仍有容器连接；先 `pod.remove(force=True)` 再删网络 |
| 404 异常类型不符预期 | 镜像相关端点 404 映射 `ImageNotFound`，通用资源为 `NotFound`；except 顺序先具体后泛化（见 [10 §10.9](../concepts/10-transport-deep-dive.md)） |
| rootless 下 socket 连不上 | 确认 `XDG_RUNTIME_DIR` 或 `/run/user/$UID` 存在；回退逻辑会建 0700 临时目录但服务端 socket 不会因此出现 |
| Secret 在容器内位置 | 未给 target 时默认 `/run/secrets/<source>`；需自定义用 dict 形态（source/target/uid/gid/mode） |

## 相关示例与概念

- [02 - 三服务编排生命周期](02-container-ops.md)：Quadlet + Postgres/Redis 的 15 步流水线
- [06 - Pod / Network / Volume](../concepts/06-pods-networks-volumes.md)
- [07 - Secret / Manifest / Registry](../concepts/07-secrets-manifests-registry.md)
- [08 - 事件与三套流协议](../concepts/08-events-and-streams.md)
