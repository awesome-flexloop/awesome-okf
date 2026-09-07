---
type: reference
title: Manager + Mixin + 异常 + SSH + Quadlets 信源锚点（30+ 条 + 1 调用链图）
description: Manager基类 7 组成员；Mixin横切3类清单；RunMixin.run 4分支返回；ImagesManager Rich try/except Import；Quadlet模型 6@property + 3方法；异常 8类继承链；SSHSocket ssh -N -L清单+100ms轮询；PodmanConfig is_machine
tags: [podman-py, manager-mixin, runmixin-four-branches, rich-import-graceful, quadlet-model, exception-inheritance, sshsocket, podmanconfig-ismachine]
generated:
  by: process:seven-concepts/sc-20260907-podman-py/e-phase
  at: 2026-09-07
verified:
  by: human:xinzo
  at: 2026-09-07
status: stable
stale_after: 2027-09-07
sources:
  - id: src-manager
    resource: external/dao/action/Containers/podman-py/podman/domain/manager.py
    title: Manager 基类 + PodmanResource 源码
  - id: src-runmixin
    resource: external/dao/action/Containers/podman-py/podman/domain/containers_run.py
    title: RunMixin.run 4 分支源码
  - id: src-buildmixin
    resource: external/dao/action/Containers/podman-py/podman/domain/images_build.py
    title: BuildMixin.build 20+ kwargs + BuildError 抛出
  - id: src-quadlet-model
    resource: external/dao/action/Containers/podman-py/podman/domain/quadlets.py
    title: Quadlet 6 @property + delete/get_contents/print_contents + install 三形态
  - id: src-ssh-socket
    resource: external/dao/action/Containers/podman-py/podman/api/ssh.py
    title: SSHSocket connect() — shell-out ssh -N -L 隧道 + 100ms 轮询
  - id: src-exceptions-chain
    resource: external/dao/action/Containers/podman-py/podman/errors/exceptions.py
    title: 完整 8 类异常继承链 + 构造参数
  - id: src-createmixin
    resource: external/dao/action/Containers/podman-py/podman/domain/containers_create.py
    title: CreateMixin.create 30+ kwargs + HostConfig 转换
---

# Manager + Mixin + 异常 + SSH + Quadlets 信源锚点（30+ 条 + 1 调用链图）

## 30+ 条锚点编号清单

### 1. Manager 基类 7 组成员（M-1 ~ M-7）
| 编号 | 成员类型 | 名称/签名 | 职责 |
|---|---|---|---|
| M-1 | 构造参数 | `__init__(client.api, client)` | 持有 api 传输对象 + 回指 PodmanClient |
| M-2 | 抽象属性 | `resource` (abstract @property) | 返回 PodmanResource 子类，prepare_model() 用它实例化 |
| M-3 | 查询三件套 | `list(**kwargs)`, `get(id)`, `exists(id)` | 默认实现；子类常重写（如 list 加 reference 过滤） |
| M-4 | 序列化 | `prepare_model(attrs) → PodmanResource` | attrs dict → Python 对象 |
| M-5 | 创建/删除 | `create(**kw)`, `remove(id, force)`, `prune(filters)` | 可选；有 Mixin 时走 Mixin |
| M-6 | API 调用辅助 | `self.get/post/put/delete(path, params, stream)` | 转发 `self.api.XXX`，自动带路径模板 |
| M-7 | 反向引用 | `.client → PodmanClient`、`.manager → 对应 Manager`（在 PodmanResource 侧） | 资源实例取 client 的通路 |

### 2. Mixin 横切 3 类清单（MX-1 ~ MX-3）
| 编号 | Mixin 类 | 注入的方法 | 注入到哪个 Manager | MRO 左端顺序（决定方法查找） |
|---|---|---|---|---|
| MX-1 | RunMixin | `run(image, command, stdout, stderr, remove, **kwargs)` → 4 分支返回（见下节） | ContainersManager | 左端第 1，`RunMixin` 优先于 `CreateMixin` 优先于 `Manager` → 若同名方法存在，RunMixin 的 win |
| MX-2 | CreateMixin | `create(**kwargs 30+)` → Container | ContainersManager | 左端第 2 |
| MX-3 | BuildMixin | `build(**kwargs 20+)` → (Image, Iterator[bytes]) + 抛 BuildError | ImagesManager | 左端第 1，BuildMixin 优先于 Manager |

### 3. RunMixin.run 4 分支（R-1 ~ R-4）
```python
def run(image, command, stdout=True, stderr=True, remove=False, stream=False, detach=False, **kwargs):
    # Case R-1: detach=True + remove=False
    if detach and not remove:
        return Container(...)

    # Case R-2: detach=True + remove=True → 后台 thread 清理
    if detach and remove:
        container = Container(...)
        threading.Thread(
            target=lambda c: c.wait(timeout=None) and c.remove(v=True),
            args=(container,), daemon=True,
        ).start()
        return container

    # Case R-3: detach=False + stream=True → Generator (yield bytes)
    if not detach and stream:
        return self._stream_generator(container, stdout, stderr)

    # Case R-4: detach=False + stream=False + exit_code!=0
    if not detach and not stream:
        exit_code = container.wait()
        output = container.logs(stdout=stdout, stderr=stderr)
        if exit_code != 0:
            raise ContainerError(container, exit_code, command, image, stderr=output)
        return output
```

### 4. ImagesManager Rich 优雅降级 + pull policy（I-1 ~ I-6）
| 编号 | 代码位置 | 语义 |
|---|---|---|
| I-1 | images_manager.py L23-32 | `try: from rich.progress import Progress except ImportError: Progress=None` —— **不因为没装 rich 就让 import podman 失败** |
| I-2 | `pull(progress_bar=True)` 入口 L388-L393 | `Progress is None` → **抛 `ModuleNotFoundError`（明确告诉用户装 extras）**，不是静默降级纯文本 |
| I-3 | progress_bar → 强制 `compatMode=True + stream=True`（L392-L393） | 因为只有 docker-compat 端点输出 pull 事件流 JSON；libpod 端点走 quiet 模式 |
| I-4 | policy 默认 "always"（L361） | 4 选 1：`missing` / `always`（default）/ `never` / `newer` |
| I-5 | platform token 拆分 L374-L382 | `os/arch/variant` → `params["OS"]`, `params["Arch"]`, `params["Variant"]`；长度 1~3 合法；其余抛 `ValueError` |
| I-6 | BuildError 抛出来源 images_build.py BuildMixin.build | `raise BuildError(reason=f"line {n} failed", build_log=last_50_lines)` → build_log 是 `Iterable[str]`，**不会内存爆（可增量消费）** |

### 5. Quadlet 模型 6 属性 + 3 方法 + install 三形态（Q-1 ~ Q-10）
| 编号 | 元素 | 定义 |
|---|---|---|
| Q-1 | `.name` @property | `attrs["Name"]` (key 双写 Name/name 兼容) |
| Q-2 | `.unit_name` @property | `attrs["UnitName"]` —— e.g. `"myapp.service"` / `"myapp-volume.service"` / `"myapp-network.service"` |
| Q-3 | `.path` @property | 磁盘绝对路径 |
| Q-4 | `.status` @property | `running` / `stopped` / `failed` / `generated` |
| Q-5 | `.application` @property | `attrs["App"]` —— Podman Desktop / cockpit 分组用 |
| Q-6 | `delete(force, ignore, reload_systemd)`（实例方法） | 转发 `self.manager.delete(self.name, ...)` |
| Q-7 | `get_contents()`（实例） / `get_contents(name)`（Manager） | GET `/quadlets/{name}/file` → plain text（非 JSON） |
| Q-8 | `print_contents()` | `print(response.text.strip())` —— strip 空行前后空白 |
| Q-9 | install 形态 A | `str / PathLike` —— 磁盘路径，自动读二进制 |
| Q-10 | install 形态 B | `tuple[str, str|bytes]` —— (文件名, 内存内容)，Content 为 str 时 encode UTF-8；multipart/form-data 编码 |
| Q-11 | install 形态 C | 单个 `.tar` / `.tar.gz` 路径 → Content-Type: `application/x-tar` 直接 POST 字节 |

### 6. 8 类异常继承链（E-1 ~ E-8）
```
HTTPError(requests)                            Exception                      RuntimeError
└── APIError (E-1)                              └── DockerException (E-5)        └── StreamParseError (E-8)
      ├── .status_code / .explanation                └── PodmanError (E-6)              .msg = 失败原因
      ├── is_client_error() 4xx                            ├── BuildError (E-7a) .msg + .build_log
      └── is_server_error() 5xx                            ├── ContainerError (E-7b) .container + .exit_status + .command + .image + .stderr
            ├── NotFound (E-2) ← 通用 404                  └── InvalidArgument (E-7c) 参数校验
            └── ImageNotFound (E-3) ← 镜像 404 (APIClient raise_for_status(not_found=ImageNotFound))
```

### 7. SSHSocket 隧道建立（S-1 ~ S-8）
| 编号 | 步骤 | 命令/伪代码 |
|---|---|---|
| S-1 |本地 socket 路径生成 | `tempfile.mktemp(prefix="podman-forward-", suffix=".sock", dir=runtime_dir)`（⚠️ mktemp 已知 TOCTOU，后续版本可能换） |
| S-2 | shell-out ssh 命令拼接 | `ssh -N -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i <identity> -L <local_sock>:<remote_sock> ssh://user@host[:port]`（用户密码交互=挂起 → R5 陷阱） |
| S-3 | StrictHostKeyChecking=no 仅示例 | AGENTS.md Security：**生产必须 `StrictHostKeyChecking=yes` + known_hosts 预配置**（不要把 no 放到生产） |
| S-4 | 身份文件权限校验 | `chmod 600 ~/.ssh/id_ed25519`，否则 ssh 静默拒绝读私钥 → R5 挂起 |
| S-5 | 子进程 stdout/stderr → DEVNULL | 不继承当前 shell，避免污染日志 |
| S-6 | 100ms 轮询 local_sock | `while time.time() - start < timeout: try connect → break`；超时抛 `ConnectionError` |
| S-7 | close() 语义 | `SIGTERM` ssh 子进程 → 400ms 后 `SIGKILL` → 删除 local_sock 文件 |
| S-8 | 前置条件（R5） | **`ssh <host> exit` 必须 <0.5s + rc=0**；否则跳过 integration test（pytest.skip） |

### 8. PodmanConfig.is_machine（PM-1 ~ PM-3）
```python
# podman/config.py PodmanConfig — 只 macOS/Windows 常用
class Service:
    identity: SSHIdentity      # ssh 私钥
    is_machine: bool            # True = Podman Machine VM 管理的远端 Podman

class PodmanConfig:
    active_service: Optional[Service]
    services: dict[str, Service]
```
- PM-1：macOS/Windows 下 Podman Desktop → 自动创建 `podman-machine-default` 服务
- PM-2：`is_machine=True` 时 CL-3 第 3 优先级命中；否则走回退本地 socket
- PM-3：Linux 桌面 `active_service` 通常为 None（直接用本地 UDS）

## 1 张调用链图（images.pull progress_bar=True 端到端）

```
[调用者] images.pull("alpine:3", progress_bar=True)
  │
  ├─ 1. ImagesManager.pull() → 参数校验 (policy/all_tags/platform tokens)
  │    └─ Progress is None? → Y → 抛 ModuleNotFoundError
  │
  ├─ 2. params["compatMode"] = True, params["stream"] = True (强制)
  │
  ├─ 3. self.api.post("/images/pull", stream=True, headers={X-Registry-Auth})
  │    │
  │    └── APIClient → requests.Session.post(stream=True) → HTTP chunked
  │
  ├─ 4. 创建 Progress(TextColumn + BarColumn + TaskProgressColumn + TimeRemainingColumn)
  │
  ├─ 5. with progress:
  │       for line_bytes in response.iter_lines():
  │           line_json = json.loads(line_bytes.decode('utf-8'))
  │
  ├─ 6. __show_progress_bar(line_json, progress, tasks_dict)
  │     ├─ "Downloading"      → tasks[id] 不存在则 add_task(total=progressDetail.total)
  │     │                       存在则 update(completed=progressDetail.current)
  │     └─ "Download complete"→ update(completed=100, total=100, force绿色)
  │                              （防止小块跳过 Downloading 事件直接完成）
  │
  └─ 7. return None (progress_bar 模式无 Image 返回)
```
> 注意：progress_bar=True → 返回 None（不是 Image 对象）；要拿 Image 另调 `images.get(repo:tag)`。
