---
type: example
title: 02 - 三服务编排生命周期（Quadlet + Postgres + Redis + Nginx）
description: 端到端15步流水线：socket前置检查→清理旧资源→拉镜像→Quadlet安装→contents校验→report健康→容器create+start→exec_run(pg_isready/redis-cli ping)→logs→优雅stop顺序→remove v=True→prune label=env=demo；异常捕获清单
tags: [podman-py, quadlets, postgres, redis, nginx, lifecycle-ops, multi-service]
generated:
  by: process:seven-concepts/sc-20260907-podman-py/e-phase
  at: 2026-09-07
verified:
  by: human:xinzo
  at: 2026-09-07
status: stable
stale_after: 2027-09-07
sources:
  - id: src-quadlets-install
    resource: external/dao/action/Containers/podman-py/podman/domain/quadlets.py#L229-L318
    title: QuadletsManager.install 源码 — tuple(str,bytes)/路径/tarball 三形态 + replace/reload_systemd
  - id: src-containers-run
    resource: external/dao/action/Containers/podman-py/podman/domain/containers_run.py
    title: RunMixin.run 源码 — 4 返回分支
  - id: src-containers-exec
    resource: external/dao/action/Containers/podman-py/podman/domain/containers.py
    title: Container.exec_run / logs / start / stop / remove
---

# 02 - 三服务编排生命周期（Quadlet + Postgres + Redis + Nginx）

> **场景**：本地开发环境用 Quadlet 描述 Postgres 持久化服务；Redis + Nginx 用 SDK 临时容器做演示。
> **前置要求**：Podman ≥ 5.8（Quadlets API），Rootless，`loginctl enable-linger $USER`（logout 不丢 quadlet 服务）

## E2.1 前置断言函数（3 条检查不通过直接退出）

```python
import os
import subprocess
from podman import PodmanClient
from podman.errors import (
    ContainerError, ImageNotFound, APIError, NotFound,
)

def preflight(client: PodmanClient):
    """前置 3 条健康检查，1 条失败就 fail-fast"""
    # 1. socket 可 ping
    assert client.ping(), "socket 不可达，检查 podman.service"
    # 2. podman --version ≥ 5.8（Quadlets 需要）
    ver = client.version()["Version"].split(".")
    ver_t = tuple(int(x) for x in ver[:2])
    assert ver_t >= (5, 8), f"需要 podman ≥ 5.8 实际 {'.'.join(ver)}"
    # 3. enable-linger 已开（否则 loginctl logout 会杀掉 systemd --user）
    r = subprocess.run(["loginctl", "show-user", str(os.getuid()),
                         "-p", "Linger", "--value"], capture_output=True, text=True)
    assert r.stdout.strip() == "yes", (
        "loginctl enable-linger $USER 未执行，"
        "logout 后 quadlet systemd 服务会停止"
    )
    print(f"[preflight] podman {'.'.join(ver)} + linger=yes  ✅")
```

## E2.2 15 步生命周期流水线（完整脚本）

```python
ENV_LABEL = "env=demo"

def pipeline():
    with PodmanClient(compatible=True) as client:
        preflight(client)

        # ───────────────── Step 1: version / Step 2: 清理旧资源 ─────────────────
        info = client.info()
        print(f"[1/15] host={info['Host']['hostname']} arch={info['Host']['arch']}")

        print("[2/15] 清理 label=env=demo 的容器和 quadlet")
        for ct in client.containers.list(all=True, filters={"label": ENV_LABEL}):
            ct.remove(force=True, v=True)
        for q in client.quadlets.list():
            if "demo" in q.name:
                client.quadlets.delete(q.name, force=True, ignore=True)
        pr = client.containers.prune(filters={"label": ENV_LABEL})
        print(f"       containers prune {len(pr['ContainersDeleted'])} 个")

        # ───────────────── Step 3: 拉取三张镜像 ─────────────────
        IMGS = [
            ("postgres:16-alpine", "PG主库"),
            ("redis:7-alpine",    "Redis缓存"),
            ("nginx:alpine",      "Nginx反代"),
        ]
        print("[3/15] images.pull 三张镜像（progress_bar=True, policy=newer）")
        for ref, _desc in IMGS:
            try:
                client.images.pull(ref, policy="newer", progress_bar=True)
            except ModuleNotFoundError as e:
                # pip install 'podman[progress]' 没装时降级
                print(f"       {ref}: rich.progress 未装，降级纯文本 pull")
                client.images.pull(ref, policy="newer")
            print(f"       {ref} ✅")

        # ───────────────── Step 4-6: Quadlet 安装 postgres 持久化服务 ─────────────────
        postgres_quadlet = ("demo-postgres.container", f"""[Container]
Image=postgres:16-alpine
ContainerName=demo-postgres
PublishPort=5432:5432
Volume=demo-pgdata:/var/lib/postgresql/data
Environment=POSTGRES_PASSWORD=demo-pass
Environment=POSTGRES_USER=demo
Environment=POSTGRES_DB=demodb
Label={ENV_LABEL}
HealthCmd=CMD-SHELL pg_isready -U demo -d demodb
HealthInterval=10s

[Service]
Restart=always
""")
        print("[4/15] quadlets.install — demo-postgres.container (内存 tuple)")
        r = client.quadlets.install(postgres_quadlet, replace=True, reload_systemd=True)
        assert not r["QuadletErrors"], f"quadlet 安装失败: {r['QuadletErrors']}"
        for src, dst in r["InstalledQuadlets"].items():
            print(f"       {src} → {dst}")

        print("[5/15] 等待 postgres 健康（重试 30 次 × 2s）")
        import time
        pg_healthy = False
        for i in range(30):
            q = client.quadlets.get("demo-postgres.container")
            if q.status.lower() == "running":
                # 用 SDK 连容器，exec pg_isready
                ct = client.containers.get("demo-postgres")
                ec, out = ct.exec_run("pg_isready -U demo -d demodb")
                if ec == 0:
                    pg_healthy = True
                    break
            time.sleep(2)
        assert pg_healthy, f"Postgres 30 次重试后仍不健康 status={q.status}"
        print("       pg_isready=accept connections ✅")

        print("[6/15] quadlets.report + get_contents 校验")
        try:
            # 部分构建没实现 report 端点，容错
            client.quadlets.report()
        except Exception:
            pass
        content = client.quadlets.get_contents("demo-postgres.container")
        assert "demo-postgres.container" in content or "[Container]" in content
        print("       contents 校验 OK ✅")

        # ───────────────── Step 7-9: Redis + Nginx 容器 create + start ─────────────────
        print("[7/15] containers.create Redis (named volume demo-redis)")
        redis_ct = client.containers.create(
            "redis:7-alpine",
            name="demo-redis",
            ports={"6379/tcp": 6379},
            volumes=["demo-redis:/data"],
            labels={ENV_LABEL.split("=")[0]: ENV_LABEL.split("=")[1]},
            healthcheck={
                "test": ["CMD", "redis-cli", "ping"],
                "interval": 10_000_000_000, "timeout": 2_000_000_000,
                "retries": 5,
            },
        )
        print(f"       redis id={redis_ct.short_id}")

        print("[8/15] containers.create Nginx 反代 8080→80, 日志卷")
        nginx_ct = client.containers.create(
            "nginx:alpine",
            name="demo-nginx",
            ports={"80/tcp": 8080},
            volumes={
                "demo-nginx-logs": {"bind": "/var/log/nginx", "mode": "rw"},
            },
            labels={ENV_LABEL.split("=")[0]: ENV_LABEL.split("=")[1]},
        )
        print(f"       nginx id={nginx_ct.short_id}")

        print("[9/15] 按依赖顺序 start：redis → nginx")
        redis_ct.start(); print("       redis.start() ✅")
        nginx_ct.start(); print("       nginx.start() ✅")
        # 让 services 初始化 3 秒（生产请用健康检查）
        time.sleep(3)

        # ───────────────── Step 10-11: exec_run + logs tail ─────────────────
        print("[10/15] exec_run 健康探测：redis-cli ping + curl nginx")
        ec, out = redis_ct.exec_run("redis-cli ping")
        assert ec == 0 and b"PONG" in out, f"redis 不 pong ec={ec} out={out}"
        print("       redis-cli PING → PONG ✅")

        ec, out = nginx_ct.exec_run("wget -qO- http://127.0.0.1:80/")
        assert ec == 0 and b"Welcome to nginx" in out
        print("       nginx 默认页下载 OK ✅")

        print("[11/15] 各取最后 10 行 logs")
        for ct_name in ["demo-postgres", "demo-redis", "demo-nginx"]:
            ct = client.containers.get(ct_name)
            last = ct.logs(tail=10).decode(errors="replace")
            print(f"       ── {ct_name} (last 10) ──")
            for ln in last.splitlines():
                print(f"         | {ln[:100]}")

        # ───────────────── Step 12: 批量 label=env=prod 启停演示 ─────────────────
        print("[12/15] 批量演示：env=prod 标签的启动/停止/删除（dry-run 风格）")
        # 只演示 label filter，不实际建 prod 容器
        prod_cts = client.containers.list(all=True, filters={"label": "env=prod"})
        print(f"       当前 env=prod 容器 {len(prod_cts)} 个（跳过操作）")

        # ───────────────── Step 13: 优雅停止顺序（反依赖）─────────────────
        print("[13/15] 优雅 stop 顺序（依赖逆序）：nginx → redis → postgres")
        nginx_ct.stop(timeout=15)
        print("       nginx.stop(15s) ✅")
        redis_ct.stop(timeout=5)
        print("       redis.stop(5s) ✅")
        # postgres 作为 quadlet 交给 systemd 管，不手动 stop

        # ───────────────── Step 14: remove(v=True) 匿名卷一起删 ─────────────────
        print("[14/15] remove(v=True) 临时容器；quadlet 交给 systemd 保活")
        nginx_ct.remove(v=True)
        redis_ct.remove(v=True)
        print("       临时容器 remove(v=True) ✅")
        # 列出 PG quadlet，确认它依然在运行（没被清理）
        q = client.quadlets.get("demo-postgres.container")
        print(f"       quadlet demo-postgres status={q.status}（保留）✅")

        # ───────────────── Step 15: prune label=env=demo ─────────────────
        print("[15/15] prune containers + images dangling")
        r1 = client.containers.prune(filters={"label": ENV_LABEL})
        r2 = client.images.prune(filters={"dangling": True})
        print(f"       containers pruned: {len(r1['ContainersDeleted'] or [])}")
        print(f"       images pruned:     {len(r2['ImagesDeleted'] or [])} "
              f"reclaimed {r2['SpaceReclaimed'] // 1024 // 1024} MB")
        print("\n" + "=" * 60)
        print("🎉 15步三服务编排生命周期演示 COMPLETE")
        print("   持久化 Postgres (quadlet systemd) 仍在运行，下次可直接复用")
        print("=" * 60)
```

## E2.3 推荐异常捕获分层（8 类清单精修版）

```python
def run_safe():
    try:
        pipeline()
    except ContainerError as e:
        print(f"❌ [容器业务失败] image={e.image} "
              f"exit={e.exit_status} cmd={e.command}")
        return 2
    except ImageNotFound as e:
        print(f"❌ [镜像缺失] 先拉取: {e}")
        return 3
    except NotFound as e:
        print(f"❌ [资源 404] {e.status_code}: {e.explanation or e}")
        return 4
    except APIError as e:
        print(f"❌ [HTTP {e.status_code}] {e} explanation={e.explanation}")
        return 5
    except AssertionError as e:
        print(f"❌ [断言不通过] {e}")
        return 10
    except Exception as e:
        # 兜底：避免未捕获的 exception 让 quadlet 孤儿进程跑着
        print(f"💥 [未预期异常] {type(e).__name__}: {e}")
        import traceback; traceback.print_exc()
        return 99
    return 0

if __name__ == "__main__":
    raise SystemExit(run_safe())
```

## E2.4 常见报错速查

| 异常/现象 | 根因 | 修复 |
|---|---|---|
| `NotFound: 404 Client Error: quadlet demo-postgres.container not found` | `install()` 返回成功但 systemd --user 没 reload | `reload_systemd=True` 默认 True 已传；加 `systemctl --user daemon-reload` shell 再试 |
| `redis-cli` → `Connection refused` | create 后立刻 start + 立刻 exec，redis fork 没起完 | 健康检查 healthcheck + retry 5 次 |
| Postgres `exec_run pg_isready` 失败 → `Permission denied` | quadlet Volume=demo-pgdata 第一次启动后 root 所有者 | 老 volume 先清 `client.volumes.get("demo-pgdata").remove()` 再重建 |
| `client.quadlets.install([tarball])` 抛 `No such file: 'xxx.tar'` | 代码里写了相对路径，cwd 不对 | 传绝对 `pathlib.Path(tar_path).resolve()` |
| 容器里 nslookup host 域名失败 | Rootless slirp4netns 默认 DNS 走宿主机 resolv.conf，nss-myhostname 没装 | `apt install libnss-myhostname` + `podman network create demo-net --dns=1.1.1.1` |
