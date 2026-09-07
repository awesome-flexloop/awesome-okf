---
type: Concept
title: 01 - 连接配置与远程传输适配器
description: 四级连接优先级（connection/base_url/active_service is_machine/本地 socket 回退）、from_env 双前缀6环境变量、rootless/rootful socket 路径、SSH identity 密钥隧道机制、SSHSocket 100ms×N forward sock 轮询、supported_schemes 6方案路由、with 上下文管理器、max_pool_size 连接池配置
tags: [Connection, SSH Tunnel, UDS, TCP, from_env, PodmanConfig, active_service, SSHAdapter, UDSAdapter]
generated:
  by: method_orchestrator/seven-concepts-cmd
  at: 2026-09-07T00:00:00Z
verified:
  by: process:podman-py-grep-20260907
  at: 2026-09-07T00:00:00Z
status: stable
stale_after: 2027-09-07
sources:
  - id: src-client-init
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/client.py
    title: PodmanClient.__init__ L36-L82 四级优先级分支
  - id: src-from-env
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/client.py
    title: from_env() L90-L140 环境变量双前缀
  - id: src-apiclient-init
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/api/client.py
    title: APIClient supported_schemes / Adapter 选择 / base_url normalize
  - id: src-ssh
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/api/ssh.py
    title: SSHSocket connect() ssh -N -L 命令 / 轮询等待 forward sock
  - id: src-config
    resource: ../../../../../external/dao/action/Containers/podman-py/podman/domain/config.py
    title: PodmanConfig services / active_service / is_machine 字段
---

# 01 - 连接配置与远程传输适配器

## 1. 四级连接优先级（PodmanClient.__init__ 决策树）

`PodmanClient(...)` 构造时，按 **L66→L72→L73→L78** 的顺序选择连接目标（**前一级命中则跳过后续所有**）：

```
PodmanClient(connection=..., base_url=..., identity=...)
   │
   ├─① if "connection" in kwargs：读取 containers.conf 命名连接
   │     config.services[connection]  →  用其 .url.geturl() 作为 base_url；.identity 作为 SSH密钥（kwargs["identity"] 可覆盖）
   │     示例：connection="production-edge"
   │
   ├─② elif "base_url" not in kwargs：没有显式传 base_url → 尝试 active_service
   │     ├─ config.active_service 存在  AND  active_service.is_machine=True →  用 machine 连接（podman machine 启动的 VM）
   │     └─ else：回退到本地 UDS socket（最常用，开发者默认）
   │
   └─③ kwargs["base_url"] 已显式给定 → 直接用（第四层）
```

**核心逻辑源码**（client.py L62-L82）：

```python
# 伪代码对应真实分支
config = PodmanConfig()                         # 读 $XDG_CONFIG_HOME/containers/containers.conf
if "connection" in api_kwargs:                   # ① 命名连接最高优先级
    conn = config.services[api_kwargs["connection"]]
    api_kwargs["base_url"] = conn.url.geturl()
    api_kwargs["identity"] = kwargs.get("identity", str(conn.identity))
elif "base_url" not in api_kwargs:               # ② 无 base_url → active_service or 本地
    active = config.active_service
    if active and active.is_machine:             # ②a：podman machine
        api_kwargs["base_url"] = active.url.geturl()
        api_kwargs["identity"] = kwargs.get("identity", str(active.identity))
    else:                                        # ②b：本地 socket 回退
        path = Path(get_runtime_dir()) / "podman" / "podman.sock"  # XDG_RUNTIME_DIR 默认
        api_kwargs["base_url"] = "http+unix://" + str(path)
self.api = APIClient(**api_kwargs)               # 进入传输层
```

## 2. from_env()：6 环境变量双前缀自动识别

`PodmanClient.from_env(**overrides)` 是迁移 docker-py 最推荐的方式——直接复用现有 Docker 环境变量：

| 变量名（Docker 兼容） | Podman 原生同名（优先级更高） | 含义 |
|---|---|---|
| `DOCKER_HOST` | `CONTAINER_HOST` | Podman 服务 URL：unix:///… / tcp://… / ssh://… |
| `DOCKER_TLS_VERIFY` | `CONTAINER_TLS_VERIFY` | 对 tcp://https:// 是否校验 CA：`"1"` 校验，其他不校验 |
| `DOCKER_CERT_PATH` | `CONTAINER_CERT_PATH` | TLS 证书（cert/key/ca.pem）所在目录 |

**同变量双前缀冲突规则**：先读 CONTAINER_*，值为 None/空再读 DOCKER_* → **原生优先，兼容兜底**。环境变量读取来源默认 `os.environ`；可传 `environment=dict(...)` 覆盖。

```python
# 典型迁移场景：CI 已有 docker-py 脚本配置 DOCKER_HOST=tcp://...
from podman import PodmanClient
# 下面这行不改 CI 配置、不改脚本即可从 docker 切 podman
client = PodmanClient.from_env(timeout=30)
```

from_env 参数清单：`version`、`timeout`、`max_pool_size`、`ssl_version`（SSH 连接忽略，走 SSH host config）、`assert_hostname`（SSH忽略）、`environment`（默认 os.environ）、`credstore_env`、`use_ssh_client`（始终 True，shell 出系统 ssh，不用 paramiko 类库）。

## 3. 本地 Socket：Rootless vs Rootful 路径

Podman 区分 Rootful（用 sudo 运行，监听系统级 socket）与 Rootless（普通用户，用户级 socket）**两种 socket 路径不可互换**：

| 模式 | 默认 socket URL | 典型使用方 | 权限要求 |
|---|---|---|---|
| **Rootless（推荐开发机）** | `unix:///run/user/$UID/podman/podman.sock`（也写为 `http+unix:///run/user/1000/podman/podman.sock`） | 普通用户 `podman system service --time=0` 或 `systemctl --user enable podman.socket` | 当前用户即可；需 `loginctl enable-linger $USER` 保证注销后 socket 存活 |
| **Rootful（服务器）** | `unix:///run/podman/podman.sock` | `sudo podman system service` 或 `systemctl enable podman.socket` | root 权限，等价于 docker.sock 权限 |

> ⚠️ **路径差异是 docker-py → podman-py 迁移最常见踩坑点**（G2 洞察 #1）：docker 默认 `/var/run/docker.sock`，podman **rootless** 不是这个路径；如果直接搬老脚本会抛 "Cannot connect to Podman API"。要么切换到 from_env()，要么按上表改 URL。

Rootless 启用一键命令（EL9/Fedora/Ubuntu 24.04+）：

```bash
sudo loginctl enable-linger $USER
systemctl --user enable --now podman.socket
# 验证 socket 存在：
ls -l /run/user/$UID/podman/podman.sock
```

## 4. SSH 远程连接：http+ssh:// + identity 密钥

跨主机连接 Podman（例如笔记本 Python 脚本操控服务器上的 Podman）时使用 **http+ssh://** 协议：

```
http+ssh://[<user>@]<host>[:<port>][/<remote_sock_path>][?secure=True]
```

- `user`：SSH 登录用户名，默认当前用户
- `host/port`：SSH 服务器地址：端口（默认 22）
- `/path`：**远端 Podman socket 绝对路径**；rootless 用 `/run/user/<UID>/podman/podman.sock`，rootful 用 `/run/podman/podman.sock`
- `?secure=True`：示例里保留给 CI 场景的标记（实际 host key 验证由 `~/.ssh/config` 和系统 ssh 可执行文件处理）

`PodmanClient(base_url="http+ssh://ops@pod-prod-01:22/run/user/1100/podman/podman.sock", identity="~/.ssh/prod_ed25519")` 时：

### 4.1 SSHSocket 真实行为（`podman/api/ssh.py:SSHSocket.connect`）

不是直接在 Python 里实现 SSH 客户端，而是**shell 出系统 `ssh` 可执行文件**建立端口转发隧道（对应 AGENTS.md Security 章节 "use_ssh_client=True always"）：

```
① parse URL → user=ops, host=pod-prod-01, port=22, path=/run/user/1100/podman/podman.sock
② 本地创建 runtime_dir/podman/podman-forward-<rand>.sock（权限 0700）
③ 启动子进程：
   ssh -N \
       -o StrictHostKeyChecking=no \   # ‼️示例默认！生产环境应改为 yes 并配置 known_hosts
       -L /local/.sock:/remote/sock    \
       -i ~/.ssh/prod_ed25519          \
       ssh://ops@pod-prod-01:22
④ 轮询 local_sock 是否存在且可 connect：
   while not 可连：sleep 0.1s；超时抛 subprocess.TimeoutExpired（AGENTS.md 常见问题 ③：Waiting on ... podman-forward-*.sock 挂起即此处）
```

**SSH 模式反模式（与 AGENTS.md Security + Common Issues 对应）**：

* ❌ **不要在生产保留 StrictHostKeyChecking=no**。把它从示例代码里删掉，提前 `ssh ops@pod-prod-01` 首次交互写入 `known_hosts`；
* ❌ **不要让 identity 文件权限大于 0600**；`chmod 600 ~/.ssh/prod_ed25519` 否则 ssh 会静默拒绝；
* ❌ **集成测试之前务必先手动验证 `ssh <host> exit`**：如果需要输入密码/确认 host key，`SSHSocket` 子进程会 stdin 挂死，轮询永远超时；
* ❌ **不要用 paramiko**；podman-py 强制 use_ssh_client=True，即永远 shell-out ssh（因为系统 ssh 与 Podman Go 实现行为最一致，paramiko 在某些 key 格式/转发场景有差异）。

## 5. APIClient：6 种 scheme + Adapter 路由

APIClient（继承 requests.Session）在 `_normalize_url()` 之后，按 URL scheme 从这 6 种路由（见 `podman/api/client.py L94-L101`）：

| scheme 集合 | 对应 Adapter | 用途 |
|---|---|---|
| `unix`, `http+unix` | **UDSAdapter**（podman/api/uds.py，AF_UNIX + HTTPAdapter 组合） | 本地 socket（开发机 rootless/rootful） |
| `ssh`, `http+ssh` | **SSHAdapter**（podman/api/ssh.py，SSHSocket 隧道） | 跨主机远程（笔记本→服务器、CI→staging） |
| `tcp`, `http` | **requests.adapters.HTTPAdapter**（原生） | 绑定网卡暴露的 Podman API（`podman system service tcp:0.0.0.0:8888 --time=0`） |

> 注意：**`tcp://` 不加密！** 若跨主机且走 tcp://，务必 + TLS（TLSConfig）或走 WireGuard/VPN；内网开发环境才可裸 tcp://。

## 6. 上下文管理器与连接池

### 6.1 with 语句自动 close（推荐）

`PodmanClient` 继承 `AbstractContextManager`，`__exit__` 自动调 `close()` → 关闭 requests.Session 连接池、清理可能的 SSH 子进程（避免僵尸进程）：

```python
with PodmanClient.from_env() as client:
    for c in client.containers.list(all=True, sparse=False):
        print(c.name, c.status, ", attrs.network:", c.attrs.get("NetworkSettings"))
# 离开作用域：自动 close，不需要 try/finally
```

### 6.2 连接池大小

`max_pool_size` / `num_pools` 两个参数透传给 requests.HTTPAdapter / UDSAdapter / SSHAdapter：
- `num_pools`：连接池数（默认 `urllib3` 10，按域名/ socket 路径哈希）
- `max_pool_size`：**单池最大连接数**；批量并发多容器 `exec_run`/`logs` 流时建议 32–128，避免 Pool is full, discarding connection 警告。

```python
# 生产用例：批量抓取 200 容器日志
client = PodmanClient.from_env(max_pool_size=128, timeout=120)
```

## 7. 常见连接故障排查 6 条（与 AGENTS.md Common local issues 对齐）

| 故障现象 | 根因（高概率） | 排查命令 |
|---|---|---|
| `FileNotFoundError` / "No such file or directory" 抛在 unix connect | socket 路径不存在；或 rootful 误写 rootless 路径 | `systemctl --user status podman.socket` 或 `sudo systemctl status podman.socket`；`ls -l <URL中的path>` |
| SSH 模式 `Waiting on podman-forward-xxx.sock` 卡住 >5 秒，抛 TimeoutExpired | ssh 子进程未成功建隧道（需密码 / StrictHostKeyChecking 要求交互 / 远端 socket 无权限） | 在同 shell 先跑：`ssh <host> -i <identity> -L /tmp/test.sock:<remote_path> -N -v` 看 stderr |
| tcp:// 连接 refused | 远端未启动 `podman system service tcp://`；防火墙未放行端口 | `ss -lntp \| grep 8888`；`firewall-cmd --add-port=8888/tcp --permanent && firewall-cmd --reload` |
| 401 Unauthorized / login 后仍 403 | CONTAINER_HOST 指向远端但 auth.json 未写入对应 registry | `client.login("registry.example.com", username="ci", password=...)`；检查 `~/.config/containers/auth.json` |
| 抛 `ValueError: Unsupported URL scheme` | URL 错写为 npipe://、docker://、podman:// 等不支持的 scheme | 一定按 6 scheme 用；Windows 走 WSL2 ssh 或 tcp |
| 并发下 requests 警告 `Connection pool is full, discarding connection` | `max_pool_size` 太小 | 加大 max_pool_size=64 / 128（不要默认 10） |
