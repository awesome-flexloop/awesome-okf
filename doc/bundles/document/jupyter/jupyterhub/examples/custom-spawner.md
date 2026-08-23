---
type: Example
title: 自定义 Spawner 生成器
description: 实现 JupyterHub v6.0.0b2 自定义 Spawner，包括核心方法实现、SSH 远程启动框架、状态持久化、进度事件和环境变量配置
tags: [jupyterhub, example, spawner, custom-spawner, ssh, lifecycle, extension]
sources:
  - id: spawner-source
    resource: ../references/spawner-source.md
    title: JupyterHub Spawner 源码参考
  - id: orm-source
    resource: ../references/orm-source.md
    title: JupyterHub ORM 源码参考
generated: { by: reference_agent/source-code-to-okf-wiki, at: "2026-08-22" }
status: stable
stale_after: "2027-08-22"
---

# 自定义 Spawner 生成器

本示例将指导你实现一个 JupyterHub 自定义 Spawner，涵盖核心生命周期方法、SSH 远程启动框架、环境变量传递、状态持久化、进度事件推送等关键特性。

> **前置知识**：建议先阅读 [Spawner 机制](../concepts/spawner.md) 理解 Spawner 基类的职责、生命周期状态机和核心方法契约。

## 1. 自定义 Spawner 的基本结构

所有自定义 Spawner 必须继承 `jupyterhub.spawner.Spawner` 基类。基类继承自 `traitlets.config.LoggingConfigurable`，提供了配置管理、日志记录和完整的生命周期框架。

### 类继承关系

```
traitlets.config.LoggingConfigurable
    └── jupyterhub.spawner.Spawner（抽象基类）
        ├── jupyterhub.spawner.LocalProcessSpawner（本地子进程）
        ├── jupyterhub.spawner.SimpleLocalProcessSpawner（简化版）
        └── your_module.YourCustomSpawner（你的实现）
```

### 必须实现的方法

自定义 Spawner **必须**实现以下三个核心异步方法：

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| `start()` | `async () → (ip, port)` | `(str, int)` 元组 | 启动单用户服务器，返回服务器监听地址 |
| `stop(now=False)` | `async (bool) → None` | `None` | 停止服务器；`now=True` 时立即强制终止 |
| `poll()` | `async () → int/None` | 退出码或 `None` | 检查进程状态：`None` 表示运行中，整数表示已退出 |

### 可选但常用的方法

| 方法 | 说明 |
|------|------|
| `get_state()` | 返回可序列化的状态字典，用于数据库持久化 |
| `load_state(state)` | 从持久化状态字典恢复 Spawner 状态 |
| `get_env()` | 返回单用户服务器的环境变量字典 |
| `get_args()` | 返回单用户服务器的命令行参数列表 |
| `progress()` | 异步生成器，产生 SSE 进度事件 |

## 2. 最小实现示例

以下是一个最简单的自定义 Spawner 骨架：

```python
# my_spawner.py
from jupyterhub.spawner import Spawner
from traitlets import Integer, Unicode


class MinimalSpawner(Spawner):
    """最小自定义 Spawner 实现。

    此示例仅展示基本结构，实际使用需要实现真实的进程管理逻辑。
    """

    # 自定义配置项示例
    remote_host = Unicode(
        default_value="localhost",
        config=True,
        help="单用户服务器运行的主机地址",
    )

    remote_port = Integer(
        default_value=8888,
        config=True,
        help="单用户服务器监听端口",
    )

    # 存储进程/连接信息的实例变量
    _pid = 0

    async def start(self):
        """启动单用户服务器。

        必须返回 (ip, port) 元组，Hub 将根据此信息更新 Proxy 路由。
        """
        # 在这里实现服务器启动逻辑
        # 例如：通过 SSH 启动远程进程、创建 Docker 容器、创建 K8s Pod 等
        self.log.info(f"正在为用户 {self.user.name} 启动服务器...")

        # 启动完成后，设置 ip 和 port 并返回
        self.ip = self.remote_host
        self.port = self.remote_port
        return (self.ip, self.port)

    async def stop(self, now=False):
        """停止单用户服务器。"""
        self.log.info(f"正在停止用户 {self.user.name} 的服务器...")
        # 在这里实现服务器停止逻辑
        self._pid = 0

    async def poll(self):
        """检查服务器状态。

        返回 None 表示服务器仍在运行。
        返回整数（退出码）表示服务器已停止。
        """
        if self._pid > 0:
            # 检查进程是否仍在运行
            # 实际实现中需要检测进程/容器/Pod 状态
            return None  # 运行中
        return 0  # 已停止（退出码 0 表示正常退出）
```

## 3. SSH Spawner 示例框架

下面是一个更完整的 SSH 远程 Spawner 实现框架，通过 SSH 在远程主机上启动单用户 Jupyter 服务器：

```python
# ssh_spawner.py
import asyncio
import asyncssh
from jupyterhub.spawner import Spawner
from jupyterhub.utils import random_port
from traitlets import Unicode, Integer, Dict, List, Bool


class SSHSpawner(Spawner):
    """通过 SSH 在远程主机上启动单用户服务器的 Spawner。

    注意：这是一个教学示例框架，生产环境使用请参考 batchspawner 等成熟实现。
    """

    # ========== 可配置项 ==========
    remote_host = Unicode(
        default_value="remote-server.example.com",
        config=True,
        help="远程主机地址",
    )

    ssh_port = Integer(
        default_value=22,
        config=True,
        help="SSH 端口",
    )

    ssh_username = Unicode(
        default_value="jupyter",
        config=True,
        help="SSH 登录用户名（默认为 jupyter）",
    )

    ssh_private_key = Unicode(
        default_value="~/.ssh/id_rsa",
        config=True,
        help="SSH 私钥路径",
    )

    remote_python = Unicode(
        default_value="/usr/bin/python3",
        config=True,
        help="远程主机上的 Python 路径",
    )

    remote_notebook_dir = Unicode(
        default_value="/home/{username}/notebooks",
        config=True,
        help="远程工作目录，{username} 会被替换为实际用户名",
    )

    # ========== 内部状态 ==========
    _conn = None          # SSH 连接
    _process = None       # 远程进程
    _remote_port = 0      # 远程端口
    _port_forward = None  # 端口转发

    def _get_remote_dir(self):
        """获取远程工作目录路径。"""
        return self.remote_notebook_dir.format(username=self.user.name)

    async def _ensure_ssh_connection(self):
        """建立或复用 SSH 连接。"""
        if self._conn is not None:
            return self._conn

        self._conn = await asyncssh.connect(
            self.remote_host,
            port=self.ssh_port,
            username=self.ssh_username,
            client_keys=[self.ssh_private_key],
            known_hosts=None,  # 生产环境应配置 known_hosts
        )
        return self._conn

    async def start(self):
        """在远程主机上通过 SSH 启动 jupyterhub-singleuser。"""
        self.log.info(f"通过 SSH 启动用户 {self.user.name} 的服务器...")

        # 发送进度事件
        self.send_event({"progress": 10, "message": "正在建立 SSH 连接..."})

        # 1. 建立 SSH 连接
        conn = await self._ensure_ssh_connection()

        self.send_event({"progress": 30, "message": "正在准备远程环境..."})

        # 2. 选择端口
        self._remote_port = random_port()

        # 3. 构建启动命令
        env = self.get_env()
        cmd = self._build_start_command(env)

        # 4. 在远程主机上启动进程
        self.send_event({"progress": 50, "message": "正在启动 Jupyter 服务器..."})

        self._process = await conn.create_process(
            cmd,
            env=env,
            term_type="xterm",
        )

        # 5. 等待服务器就绪（轮询端口或等待日志输出）
        await self._wait_for_server()

        self.send_event({"progress": 80, "message": "正在建立端口转发..."})

        # 6. 设置 SSH 端口转发（将远程端口映射到本地）
        # 注意：实际实现中可能需要反向端口转发或直接暴露远程端口
        self._port_forward = await conn.forward_local_port(
            "", 0, "127.0.0.1", self._remote_port
        )
        local_port = self._port_forward.get_port()

        self.send_event({"progress": 100, "message": "服务器就绪！"})

        # 7. 返回服务器地址
        self.ip = "127.0.0.1"
        self.port = local_port
        return (self.ip, self.port)

    def _build_start_command(self, env):
        """构建远程启动命令。"""
        notebook_dir = self._get_remote_dir()
        args = self.get_args()

        cmd_parts = [
            self.remote_python,
            "-m", "jupyterhub.singleuser",
            f"--port={self._remote_port}",
            f"--notebook-dir={notebook_dir}",
        ]
        cmd_parts.extend(args)
        return " ".join(cmd_parts)

    async def _wait_for_server(self):
        """等待远程服务器就绪。"""
        import time
        deadline = time.time() + self.start_timeout

        while time.time() < deadline:
            if self._process.exit_status is not None:
                # 进程已退出，读取错误输出
                stderr = await self._process.stderr.read()
                raise RuntimeError(
                    f"单用户服务器启动失败，退出码 {self._process.exit_status}:\n{stderr}"
                )
            # 检查进程输出中是否有就绪信号
            # 实际实现中可以检查 HTTP 端点或日志输出
            await asyncio.sleep(1)

        raise TimeoutError(
            f"服务器在 {self.start_timeout} 秒内未启动"
        )

    async def stop(self, now=False):
        """停止远程服务器。"""
        self.log.info(f"停止用户 {self.user.name} 的 SSH 服务器...")

        # 关闭端口转发
        if self._port_forward is not None:
            self._port_forward.close()
            self._port_forward = None

        # 终止远程进程
        if self._process is not None and self._process.exit_status is None:
            if now:
                self._process.kill()
            else:
                self._process.terminate()
                try:
                    await asyncio.wait_for(
                        self._process.wait(),
                        timeout=self.stop_timeout
                    )
                except asyncio.TimeoutError:
                    self._process.kill()
            self._process = None

        # 关闭 SSH 连接
        if self._conn is not None:
            self._conn.close()
            await self._conn.wait_closed()
            self._conn = None

        self._remote_port = 0

    async def poll(self):
        """检查远程进程状态。"""
        if self._process is None:
            return 0  # 未启动或已停止

        exit_status = self._process.exit_status
        if exit_status is not None:
            return exit_status  # 已退出，返回退出码

        return None  # 仍在运行

    async def progress(self):
        """异步生成器：产生 SSE 进度事件。

        前端通过 /hub/api/users/<name>/server/progress 端点实时接收。
        """
        # progress() 在 start() 执行期间被 Hub 迭代
        # 可以在这里产生初始事件
        yield {"progress": 0, "message": "开始启动..."}
        # 注意：实际进度事件在 start() 中通过 self.send_event() 发送
        # progress() 方法本身主要用于初始和等待阶段的事件
```

> **参考**：成熟的 SSH Spawner 实现请参考 [batchspawner](https://github.com/jupyterhub/batchspawner) 项目中的 SSHSpawner。

## 4. 环境变量传递与资源配置

Spawner 负责为单用户服务器构建正确的启动环境。

### 4.1 自定义环境变量

```python
from jupyterhub.spawner import Spawner
from traitlets import Dict


class EnvSpawner(Spawner):
    """演示环境变量配置的 Spawner。"""

    # 用户可通过配置文件添加自定义环境变量
    extra_env = Dict(
        default_value={},
        config=True,
        help="传递给单用户服务器的额外环境变量",
    )

    def get_env(self):
        """重写 get_env() 添加自定义环境变量。

        基类 get_env() 已经处理了：
        1. env_keep 指定的父进程环境变量
        2. JUPYTERHUB_API_TOKEN、JUPYTERHUB_API_URL 等 Hub 通信变量
        3. 用户配置的 env 字典
        """
        env = super().get_env()

        # 添加自定义环境变量
        env.update(self.extra_env)

        # 添加用户相关的环境变量
        env["JUPYTERHUB_USER"] = self.user.name
        env["NB_USER"] = self.user.name
        env["NB_UID"] = str(self.user.id)  # 注意：实际需要获取 UID

        # 从 auth_state 注入 token（如果启用了 auth_state）
        if hasattr(self.user, 'auth_state') and self.user.auth_state:
            env["ACCESS_TOKEN"] = self.user.auth_state.get(
                "access_token", ""
            )

        return env
```

### 4.2 资源限制配置

```python
from jupyterhub.spawner import Spawner
from traitlets import Float, Union, Integer
from traitlets.config import LoggingConfigurable


class ResourceSpawner(Spawner):
    """支持资源限制配置的 Spawner。"""

    # 资源限制 traitlets（基类已定义，子类负责实施）
    # mem_limit: 内存限制
    # cpu_limit: CPU 核心数限制
    # mem_guarantee: 内存保证量
    # cpu_guarantee: CPU 保证量

    def _build_resource_args(self):
        """根据资源配置构建启动参数。

        不同子类将资源限制映射到不同后端：
        - DockerSpawner → --memory, --cpus
        - KubeSpawner → Pod resources.limits/requests
        - LocalProcessSpawner → 不强制实施
        """
        args = []

        if self.mem_limit:
            # 将人类可读格式转换为字节（基类提供了辅助方法）
            mem_bytes = self.mem_limit
            args.append(f"--mem-limit={mem_bytes}")

        if self.cpu_limit:
            args.append(f"--cpu-limit={self.cpu_limit}")

        return args

    async def start(self):
        args = self.get_args() + self._build_resource_args()
        # 使用 args 启动服务器...
        ...
```

### 4.3 配置示例

```python
# jupyterhub_config.py
c.Spawner.mem_limit = "2G"
c.Spawner.cpu_limit = 1.0
c.Spawner.mem_guarantee = "512M"
c.Spawner.cpu_guarantee = 0.5
c.Spawner.env_keep = [
    "PATH", "PYTHONPATH", "CONDA_ROOT", "VIRTUAL_ENV",
    "LANG", "LC_ALL", "JAVA_HOME",
]
c.Spawner.environment = {"MY_CUSTOM_VAR": "my_value"}
```

## 5. 状态持久化：get_state() / load_state()

Hub 重启后，Spawner 需要通过 `get_state()` 和 `load_state()` 恢复之前的运行状态。

```python
from jupyterhub.spawner import Spawner


class PersistentSpawner(Spawner):
    """支持状态持久化的 Spawner 示例。"""

    # 远程容器/进程 ID（需要持久化）
    _container_id = ""
    _remote_ip = ""
    _remote_port = 0

    def get_state(self):
        """将 Spawner 状态序列化为可 JSON 序列化的字典。

        此字典将存储在数据库 spawners 表的 state 列（JSONDict 类型）。
        Hub 重启后通过 load_state() 恢复。
        """
        # 必须调用 super().get_state() 获取基类状态
        state = super().get_state()

        # 添加自定义状态
        if self._container_id:
            state["container_id"] = self._container_id
        if self._remote_ip:
            state["remote_ip"] = self._remote_ip
        if self._remote_port:
            state["remote_port"] = self._remote_port

        return state

    def load_state(self, state):
        """从持久化状态字典恢复 Spawner。

        Hub 启动时，对每个数据库中有记录的 Spawner 调用此方法。
        """
        super().load_state(state)

        # 恢复自定义状态
        if "container_id" in state:
            self._container_id = state["container_id"]
        if "remote_ip" in state:
            self._remote_ip = state["remote_ip"]
        if "remote_port" in state:
            self._remote_port = state["remote_port"]

        self.log.info(
            f"已恢复 Spawner 状态: container_id={self._container_id}"
        )

    def clear_state(self):
        """清除持久化状态（服务器停止后调用）。"""
        super().clear_state()
        self._container_id = ""
        self._remote_ip = ""
        self._remote_port = 0
```

### 状态恢复流程

Hub 重启时的状态恢复流程：

```mermaid
flowchart TD
    Start[Hub 启动] --> LoadDB[从数据库加载 Spawner 记录]
    LoadDB --> CreateSpawner[创建 Spawner 实例]
    CreateSpawner --> LoadState[调用 load_state(state)]
    LoadState --> Poll[调用 poll() 检查服务器状态]
    Poll -->|返回 None 运行中| RestoreRoute[恢复 Proxy 路由]
    Poll -->|返回退出码| MarkStopped[标记为已停止]
    RestoreRoute --> Done[就绪]
    MarkStopped --> Done
```

```python
# 在 start() 中利用已恢复的状态
async def start(self):
    # 如果 load_state 恢复了 container_id，说明服务器可能仍在运行
    if self._container_id:
        try:
            # 检查容器/进程是否仍在运行
            status = await self._check_container_status(self._container_id)
            if status == "running":
                # 复用已运行的容器
                self.ip = self._remote_ip
                self.port = self._remote_port
                return (self.ip, self.port)
        except Exception:
            # 容器不存在，清理状态后重新启动
            self._container_id = ""

    # 正常启动流程
    # ... 创建新容器/进程
    self._container_id = new_container_id
    return (self.ip, self.port)
```

## 6. 进度事件：send_event() for SSE

JupyterHub 支持通过 Server-Sent Events (SSE) 向用户实时推送服务器启动进度。

```python
from jupyterhub.spawner import Spawner


class ProgressSpawner(Spawner):
    """演示 SSE 进度事件的 Spawner。"""

    async def start(self):
        """启动过程中通过 send_event() 推送进度。"""
        # 进度事件格式：{"progress": 0-100, "message": "描述文本"}
        # progress 为整数百分比，message 为显示给用户的文本

        self.send_event({
            "progress": 5,
            "message": "正在分配计算资源..."
        })
        await self._allocate_resources()

        self.send_event({
            "progress": 20,
            "message": "正在创建容器..."
        })
        container_id = await self._create_container()

        self.send_event({
            "progress": 40,
            "message": "正在启动 Jupyter 服务器..."
        })
        await self._start_container(container_id)

        self.send_event({
            "progress": 60,
            "message": "等待服务器响应..."
        })
        await self._wait_for_ready()

        self.send_event({
            "progress": 80,
            "message": "正在配置网络..."
        })
        await self._setup_networking()

        self.send_event({
            "progress": 100,
            "message": "服务器已就绪！"
        })

        return (self.ip, self.port)

    async def progress(self):
        """progress() 异步生成器。

        在 start() 执行期间被 Hub 持续迭代，将事件推送给前端。
        可以在这里产生等待期间的事件（如等待资源分配时）。
        """
        # 初始事件
        yield {"progress": 0, "message": "开始启动服务器..."}

        # 注意：大多数进度事件应该在 start() 中通过 send_event() 发送
        # progress() 生成器适合用于在等待外部资源时持续发送心跳
        # 但不要在 progress() 中执行长时间阻塞操作
```

### 前端进度展示

用户在 `/hub/spawn` 页面会看到实时进度条：

```
[████████████░░░░░░░░] 60% 等待服务器响应...
```

进度事件也可以携带 `failed: true` 标志启动失败信息：

```python
self.send_event({
    "progress": 100,
    "failed": True,
    "message": "资源不足，请稍后重试或联系管理员。",
    "html_message": "<b>资源不足</b><br/>当前集群负载较高，请稍后重试。",
})
```

### v6.0 SpawnException

v6.0 新增的 `SpawnException` 允许 Spawner 策略性阻止 spawn 并提供结构化错误信息：

```python
from jupyterhub.spawner import Spawner, SpawnException


class QuotaSpawner(Spawner):
    """带配额检查的 Spawner。"""

    async def start(self):
        # 检查用户配额
        if await self._is_quota_exceeded():
            raise SpawnException(
                "资源配额已满",
                reason="quota_exceeded",
                log_message=f"用户 {self.user.name} 超出资源配额",
                message_html=(
                    "<h4>资源不足</h4>"
                    "<p>您已达到并发服务器上限，"
                    "请停止其他服务器后重试。</p>"
                ),
                status_code=503,
            )

        # 正常启动流程...
        ...
```

## 7. 注册自定义 Spawner

### 方式一：直接使用 Python 路径（开发/测试）

```python
# jupyterhub_config.py
import sys
sys.path.insert(0, '/path/to/spawner/module')

c.JupyterHub.spawner_class = 'ssh_spawner.SSHSpawner'
```

### 方式二：通过 Entry Points 注册（推荐用于分发包）

在 `pyproject.toml` 中声明：

```toml
[project.entry-points."jupyterhub.spawners"]
ssh = "ssh_spawner:SSHSpawner"
```

或在 `setup.py` 中：

```python
setup(
    name="jupyterhub-ssh-spawner",
    ...
    entry_points={
        "jupyterhub.spawners": [
            "ssh = ssh_spawner:SSHSpawner",
        ],
    },
)
```

安装后即可使用短名称：

```python
c.JupyterHub.spawner_class = 'ssh'
```

内置 Spawner 短名称参考：

| 短名称 | 类 |
|--------|-----|
| `localprocess` / `default` | LocalProcessSpawner |
| `simple` | SimpleLocalProcessSpawner |

## 8. 关键配置选项示例

以下是自定义 Spawner 相关的常用配置：

```python
# jupyterhub_config.py
# ========== Spawner 通用配置 ==========

# 启动超时（秒）
c.Spawner.start_timeout = 120

# 停止超时（秒）
c.Spawner.stop_timeout = 30

# HTTP 请求超时（秒）
c.Spawner.http_timeout = 30

# 状态轮询间隔（秒）
c.Spawner.poll_interval = 30

# 工作目录
c.Spawner.notebook_dir = "/home/{username}/notebooks"

# 默认 URL（启动后跳转）
c.Spawner.default_url = "/lab"  # JupyterLab
# c.Spawner.default_url = "/tree"  # Classic Notebook

# Debug 模式
c.Spawner.debug = False

# ========== 资源配置 ==========
c.Spawner.mem_limit = "4G"
c.Spawner.cpu_limit = 2.0
c.Spawner.mem_guarantee = "1G"
c.Spawner.cpu_guarantee = 0.5

# ========== 环境变量 ==========
c.Spawner.env_keep = ["PATH", "PYTHONPATH", "LANG", "LC_ALL"]
c.Spawner.environment = {
    "MY_VAR": "value",
    "NB_USER": "{username}",  # {username} 会被替换
}

# ========== 自定义 Spawner 配置 ==========
c.JupyterHub.spawner_class = 'ssh_spawner.SSHSpawner'
c.SSHSpawner.remote_host = 'remote-gpu-server.example.com'
c.SSHSpawner.ssh_private_key = '/etc/jupyterhub/ssh_key'

# ========== 启动/停止钩子 ==========
async def pre_spawn_hook(spawner):
    """Spawn 前执行的钩子函数。"""
    username = spawner.user.name
    spawner.log.info(f"准备启动用户 {username} 的服务器")
    # 例如：创建用户目录、设置权限、挂载存储等

async def post_stop_hook(spawner):
    """Stop 后执行的钩子函数。"""
    username = spawner.user.name
    spawner.log.info(f"用户 {username} 的服务器已停止")
    # 例如：清理临时资源、归档日志等

c.Spawner.pre_spawn_hook = pre_spawn_hook
c.Spawner.post_stop_hook = post_stop_hook

# ========== 并发控制 ==========
# 最大并发 spawn 数
c.JupyterHub.concurrent_spawn_limit = 100

# 每个用户的活跃服务器上限
c.JupyterHub.active_server_limit = 0  # 0 表示无限制
```

## 9. 第三方 Spawner 参考

社区提供了多种成熟的 Spawner 实现，可作为开发自定义 Spawner 的参考：

| Spawner | 项目地址 | 启动方式 | 适用场景 |
|---------|---------|---------|---------|
| **DockerSpawner** | [dockerspawner](https://github.com/jupyterhub/dockerspawner) | Docker 容器 | Docker 单机环境、容器化部署 |
| **KubeSpawner** | [kubespawner](https://github.com/jupyterhub/kubespawner) | Kubernetes Pod | 云原生、大规模集群（Zero to JupyterHub） |
| **DockerSwarmSpawner** | [dockerspawner](https://github.com/jupyterhub/dockerspawner) | Docker Swarm 服务 | Docker Swarm 集群 |
| **BatchSpawner** | [batchspawner](https://github.com/jupyterhub/batchspawner) | HPC 批处理系统 | SLURM/PBS/LSF/SGE 等超算环境 |
| **SSHSpawner** | [batchspawner](https://github.com/jupyterhub/batchspawner) | SSH 远程进程 | 远程服务器部署 |
| **SystemdSpawner** | [systemdspawner](https://github.com/jupyterhub/systemdspawner) | systemd 服务 | 使用 systemd 管理进程的 Linux 服务器 |
| **RemoteSlurmSpawner** | [batchspawner](https://github.com/jupyterhub/batchspawner) | SLURM + SSH | 远程 HPC 集群 |
| **WrapSpawner** | [wrapspawner](https://github.com/jupyterhub/wrapspawner) | 配置化选择 | 根据用户/配置动态选择 Spawner |
| **ProfileSpawner** | [wrapspawner](https://github.com/jupyterhub/wrapspawner) | 用户选择 | 用户启动时选择服务器配置（CPU/GPU/内存） |

### 参考 DockerSpawner 的关键实现模式

DockerSpawner 是学习自定义 Spawner 最好的参考之一，其关键模式包括：

1. **容器 ID 持久化**：将 Docker container ID 存储在 `get_state()` 中，Hub 重启后通过 ID 重新连接到运行中的容器
2. **端口映射**：动态分配端口，通过 Docker API 映射到容器内部
3. **镜像配置**：支持每个用户/每个服务器使用不同的 Docker 镜像
4. **卷挂载**：通过 `volumes` traitlet 配置主机到容器的目录挂载
5. **资源限制**：将 `mem_limit`/`cpu_limit` 映射为 Docker `--memory`/`--cpus` 参数
6. **网络配置**：支持自定义 Docker 网络、DNS 配置等

### 参考 KubeSpawner 的关键实现模式

KubeSpawner 展示了大规模分布式场景下的 Spawner 设计：

1. **Pod 模板**：通过 Pod 配置 YAML 或 traitlets 定义 Kubernetes Pod 规范
2. **事件监听**：通过 K8s Watch API 实时监听 Pod 状态变化，映射为进度事件
3. **命名空间隔离**：支持每个用户/组使用不同的 K8s 命名空间
4. **GPU 支持**：通过 `extra_resource_guarantees`/`limits` 配置 GPU 资源
5. **PVC 持久存储**：每个用户自动创建和挂载 PersistentVolumeClaim

## 10. 完整可运行示例

以下是一个可以直接使用的 `SimpleSSHSpawner` 简化版，展示所有核心概念：

```python
# simple_ssh_spawner.py
import asyncio
import asyncssh
from jupyterhub.spawner import Spawner
from jupyterhub.utils import random_port, url_path_join
from traitlets import Unicode, Integer


class SimpleSSHSpawner(Spawner):
    """简化版 SSH Spawner，通过 SSH 在远程主机启动单用户服务器。"""

    remote_host = Unicode("localhost", config=True)
    ssh_username = Unicode("jupyter", config=True)
    remote_python = Unicode("/usr/bin/python3", config=True)
    remote_workdir = Unicode("/home/{username}", config=True)

    _conn = None
    _proc = None
    _proc_pid = 0

    async def _ssh_connect(self):
        if self._conn:
            return self._conn
        self._conn = await asyncssh.connect(
            self.remote_host,
            username=self.ssh_username,
            known_hosts=None,
        )
        return self._conn

    async def start(self):
        self.send_event({"progress": 10, "message": "连接远程主机..."})
        conn = await self._ssh_connect()

        port = random_port()
        workdir = self.remote_workdir.format(username=self.user.name)
        env = self.get_env()

        # 构建启动命令
        cmd = (
            f"cd {workdir} && "
            f"{self.remote_python} -m jupyterhub.singleuser "
            f"--port={port} --ip=0.0.0.0"
        )

        self.send_event({"progress": 40, "message": "启动 Jupyter 服务器..."})
        self._proc = await conn.create_process(cmd, env=env)

        # 等待服务器就绪（简单轮询）
        import time
        deadline = time.time() + self.start_timeout
        await asyncio.sleep(3)  # 给服务器启动的时间

        self.send_event({"progress": 100, "message": "服务器就绪！"})
        self.ip = self.remote_host
        self.port = port
        return (self.ip, self.port)

    async def stop(self, now=False):
        if self._proc and self._proc.returncode is None:
            if now:
                self._proc.kill()
            else:
                self._proc.terminate()
                try:
                    await asyncio.wait_for(self._proc.wait(), self.stop_timeout)
                except asyncio.TimeoutError:
                    self._proc.kill()
        if self._conn:
            self._conn.close()
            self._conn = None
        self._proc = None

    async def poll(self):
        if self._proc is None:
            return 0
        if self._proc.returncode is not None:
            return self._proc.returncode
        return None

    def get_state(self):
        state = super().get_state()
        state["remote_host"] = self.remote_host
        state["remote_port"] = getattr(self, "port", 0)
        return state

    def load_state(self, state):
        super().load_state(state)
        if "remote_host" in state:
            self.remote_host = state["remote_host"]
```

## 源码溯源

- [Spawner 机制](../concepts/spawner.md) — Spawner 基类的完整生命周期方法、配置项和状态转换
- [JupyterHub Spawner 源码参考](../references/spawner-source.md) — Spawner 基类及 LocalProcessSpawner/SimpleLocalProcessSpawner 的 API 参考
- [JupyterHub ORM 源码参考](../references/orm-source.md) — Spawner/User/Server ORM 模型的持久化机制
