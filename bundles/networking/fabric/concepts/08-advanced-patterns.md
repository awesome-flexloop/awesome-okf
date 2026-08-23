---
type: Concept
title: 高级模式
description: Executor 按主机分组执行、ConnectionCall 任务参数化、OpenSSHAuthStrategy 认证策略、MockRemote 测试工具与自定义 Runner
tags: [fabric, advanced, executor, auth, testing, mock]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# 高级模式

## Executor — 按主机分组执行

`Executor` 继承 `invoke.Executor`，是 fabric CLI（`fab` 命令）的核心调度器。它理解主机参数化，能将一个任务定义展开为针对多台主机的多次执行。

### 工作原理

当通过 CLI 或装饰器指定主机时，Executor 的 `expand_calls()` 方法将通用任务调用展开：

1. CLI `-H host1,host2` 参数解析为主机列表
2. 对每个任务，CLI hosts 优先于 `@task(hosts=[...])` 装饰器中的 hosts
3. 调用 `normalize_hosts()` 将字符串统一为 `{"host": "..."}` 字典
4. 为每个主机创建 `ConnectionCall`（携带 Connection 初始化参数）
5. pre/post 任务只添加一次，不按主机展开

### normalize_hosts()

```python
def normalize_hosts(self, hosts):
    dicts = []
    for value in hosts or []:
        if not isinstance(value, dict):
            value = dict(host=value)
        dicts.append(value)
    return dicts
```

主机列表成员可以是字符串（简写）或字典（完整 Connection 参数），两者可混合：

```python
@task(hosts=[
    "web1.example.com",
    {"host": "web2.example.com", "port": 2222, "user": "admin"},
])
def deploy(c):
    c.run("git pull")
```

### parameterize()

`parameterize(call, connection_init_kwargs)` 将通用 Call 克隆为 `ConnectionCall`，附加 `init_kwargs`。执行时 `ConnectionCall.make_context()` 使用这些参数创建 Connection 实例。

### dedupe()

Executor 覆盖了 `dedupe()` 使其直接返回 tasks 不去重——因为不同主机上的"相同"任务实际是不同的执行。

### remainder 执行

当 CLI 使用 `fab -H host1,host2 -- command` 形式时，Executor 创建匿名任务包装 `c.run(remainder)`，并为每个主机参数化执行。如果给了 remainder 但没有主机，抛出 `NothingToDo` 异常。

## ConnectionCall

`ConnectionCall` 继承 `invoke.Call`，是携带 Connection 创建参数的任务调用：

```python
class ConnectionCall(invoke.Call):
    def __init__(self, *args, init_kwargs, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_kwargs = init_kwargs

    def make_context(self, config, core_parse_result):
        kwargs = dict(
            self.init_kwargs,
            config=config,
            remainder=core_parse_result.remainder,
        )
        return Connection(**kwargs)
```

`__repr__` 会追加主机信息：`<Call 'deploy', host='web1'>`。

通常不直接使用 ConnectionCall——它由 Executor 内部创建。

## Task 与 task 装饰器

### Task 类

`fabric.Task` 继承 `invoke.Task`，额外存储 `hosts` 属性：

```python
class Task(invoke.Task):
    def __init__(self, *args, **kwargs):
        self.hosts = kwargs.pop("hosts", None)
        super().__init__(*args, **kwargs)
```

### task() 装饰器

`fabric.task` 包装 `invoke.task`，默认设置 `klass=Task`：

```python
def task(*args, **kwargs):
    kwargs.setdefault("klass", Task)
    return invoke.task(*args, **kwargs)
```

使用方式：

```python
from fabric import task

@task
def deploy(c):
    c.run("git pull")

@task(hosts=["web1", "web2"])
def restart(c):
    c.sudo("systemctl restart myapp")
```

`hosts` 参数接受字符串列表或字典列表。CLI 的 `-H` 参数优先级高于装饰器的 hosts。

## 认证策略

### OpenSSHAuthStrategy

`fabric.auth.OpenSSHAuthStrategy`（v3.1 新增，标记为实验性）继承 `paramiko.auth_strategy.AuthStrategy`，模拟 OpenSSH 客户端的认证行为：

```python
config = Config(overrides={
    "authentication": {
        "strategy_class": OpenSSHAuthStrategy,
        "identities": ["/path/to/key"],
    }
})
c = Connection("host", config=config)
```

### 密钥加载顺序

`get_pubkeys()` 按 OpenSSH 相同顺序加载并 yield 密钥源：

1. SSH config 中的证书（CertificateFile）
2. CLI/config 指定的证书
3. ssh-agent 中的密钥（配置文件中提及的优先）
4. CLI/config 指定的普通密钥（`authentication.identities`）
5. SSH config IdentityFile 中的普通密钥
6. 默认路径密钥（`~/.ssh/id_rsa`、`id_ecdsa`、`id_ed25519`、`id_dsa`）

### get_sources()

认证源的完整顺序：
1. 所有公钥（来自 `get_pubkeys()`）
2. 密码（通过 `getpass.getpass(f"{username}'s password: ")` 提示输入）

### 自动启用

当 `authentication.strategy_class` 不为 None 时，`Connection.open()` 自动：
1. 从 connect_kwargs 移除冲突的认证参数（`allow_agent`、`key_filename`、`look_for_keys`、`passphrase`、`password`、`pkey`、`username`）
2. 创建策略实例：`strategy_class(ssh_config=..., fabric_config=..., username=...)`
3. 通过 `auth_strategy` 参数传给 `SSHClient.connect()`

### 资源清理

`authenticate()` 在 finally 中调用 `self.agent.close()` 关闭 SSH agent 连接。

## 测试工具

fabric 提供 `fabric.testing` 模块帮助测试基于 fabric 的代码。

### MockRemote

`MockRemote` 是最常用的测试工具，patch `fabric.connection.SSHClient` 并模拟远程会话：

```python
from fabric.testing.base import MockRemote

def test_my_command():
    with MockRemote() as remote:
        remote.expect("uname -a", out=b"Linux web1\n")
        c = Connection("host")
        result = c.run("uname -a", hide=True)
        assert "Linux" in result.stdout
```

核心方法：
- `expect(cmd=None, out=b"", err=b"", exit=0, ...)`：创建单命令 Session 并返回 MockChannel
- `expect_sessions(*sessions)`：设置多命令会话
- `start()`/`stop()`：启停 patch
- `safety()`：执行后验证（检查预期命令是否被调用）

支持上下文管理器，退出时自动 safety 检查和 stop。

### Session

`Session` 描述一个模拟的远程连接会话：

```python
from fabric.testing.base import Session, Command

session = Session(
    host="web1",
    user="deploy",
    commands=[
        Command(cmd="uname -a", out=b"Linux\n"),
        Command(cmd="false", exit=1),
    ],
)
```

参数：
- `host`/`user`/`port`：连接预期（None 表示接受任何值）
- `commands`：Command 对象列表
- `cmd`/`out`/`err`/`exit`/`waits`：单命令简写
- `enable_sftp`：是否启用 SFTP mock
- `transfers`：预期的 SFTP 传输列表

### Command

```python
Command(cmd="hostname", out=b"web1\n", err=b"", exit=0, waits=0)
```

`waits` 参数控制 `exit_status_ready()` 返回 False 的次数，用于测试异步等待场景。

`ShellCommand(Command)` 用于 `shell()` 方法的测试，断言 `invoke_shell()` 被调用。

### MockChannel

`MockChannel` 继承 Mock，使用独立的 BytesIO 跟踪 stdout/stderr/stdin 状态：
- `recv(count)` 从 stdout BytesIO 读取
- `recv_stderr(count)` 从 stderr BytesIO 读取
- `sendall(data)` 写入 stdin BytesIO

### SFTP 测试

设置 `enable_sftp=True` 启用 SFTP mock：

```python
remote = MockRemote(enable_sftp=True)
# 或
session = Session(enable_sftp=True, transfers=[
    {"method": "put", "localpath": "/local/file", "remotepath": "/remote/file"},
])
```

### pytest fixtures

`fabric.testing.fixtures` 提供 pytest fixtures：

| Fixture | 说明 |
|---------|------|
| `connection` / `cxn` | 预配置的 Connection（run/local 被 Mock 替换） |
| `remote` | MockRemote 实例（yield 后自动 safety+stop） |
| `remote_with_sftp` | 启用 SFTP 的 MockRemote |
| `client` | 直接 mock SSHClient |
| `sftp` | (Transfer, SFTPClient, mock_os) 三元组 |
| `sftp_objs` | (Transfer, SFTPClient) 二元组 |
| `transfer` | 仅 Transfer 对象 |

使用方式：

```python
# conftest.py
from fabric.testing.fixtures import remote, connection

def test_deploy(remote):
    remote.expect("git pull")
    # ... 执行测试代码
```

### MockSFTP（已废弃）

`MockSFTP` 类在 3.2 版本标记为 deprecated，其功能已合并到 `MockRemote(enable_sftp=True)`。

## 自定义 Runner

fabric Config 的 `runners` 配置允许替换 Runner 类：

```python
from fabric import Config, Remote

class MyRemote(Remote):
    def generate_result(self, **kwargs):
        result = super().generate_result(**kwargs)
        result.timestamp = datetime.now()
        return result

config = Config(overrides={
    "runners": {"remote": MyRemote, "remote_shell": MyRemoteShell}
})
c = Connection("host", config=config)
```

自定义 Remote 可以覆盖：
- `start()`：通道创建和命令发送
- `send_start_message()`：exec_command vs invoke_shell
- `generate_result()`：Result 对象构造
- `handle_window_change()`：窗口大小变化处理

## CLI 扩展

Fab 类继承 invoke.Program，可子类化自定义 CLI 行为：

```python
from fabric.main import Fab

class MyFab(Fab):
    def core_args(self):
        args = super().core_args()
        args.append(Argument(names=("my-flag",), kind=bool))
        return args
```

核心任务集合名默认为 `fabfile`（通过 `tasks.collection_name` 配置），可在配置中修改。

## 相关概念

- [Connection 详解](02-connection.md)
- [配置体系](03-configuration.md)
- [多主机并行](05-group-parallel.md)
- [命令执行](04-command-execution.md)
- [pyinvoke 执行模型](../../../tooling/pyinvoke/index.md)
- [paramiko 认证体系](../../paramiko/concepts/05-authentication.md)
