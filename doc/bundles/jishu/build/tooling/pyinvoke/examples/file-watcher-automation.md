---
type: Example
title: Watcher 自动化响应
description: 使用 Responder 和 FailingResponder 自动响应命令行提示（如 sudo 密码输入）
tags: [pyinvoke, watcher, Responder, FailingResponder, StreamWatcher, auto-response, sudo, password, pattern, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-src
    resource: /references/pyinvoke-source.md
    title: "PyInvoke 源码"
---

# Watcher 自动化响应

在自动化执行 shell 命令时，经常遇到需要交互式输入的场景——如 sudo 密码提示、数据库密码、SSH 主机密钥确认、`apt-get install` 的 `[Y/n]` 确认等。Invoke 提供了 `StreamWatcher` 体系（`Responder`、`FailingResponder`）来自动扫描子进程输出并自动写入响应，实现无人值守的自动化执行。[^pyinvoke-src]

## 1. Responder：基本模式响应

`Responder` 是最简单的 watcher：当子进程输出匹配指定的正则模式时，自动向 stdin 写入预设的响应字符串。

### 示例：自动输入数据库密码

```python
# tasks.py
from invoke import task, Responder


@task
def db_backup(c, db_password="secret123"):
    """备份数据库，自动输入密码。"""
    # 创建 Responder：匹配 "Password:" 提示，自动回复密码+换行
    password_prompt = Responder(
        pattern=r"Password:",
        response=f"{db_password}\n",
    )

    # 通过 watchers 参数传入 c.run()
    c.run(
        "pg_dump -U dbuser mydb > backup.sql",
        watchers=[password_prompt],
        pty=True,  # 使用 PTY 确保提示输出被正确捕获
    )
    print("✅ 数据库备份完成 → backup.sql")
```

关键要点：

- `pattern` 是正则表达式字符串，用于匹配子进程 stdout/stderr 中的提示文本。
- `response` 是匹配成功后写入子进程 stdin 的字符串，通常末尾要加 `\n`（模拟回车键）。
- `watchers` 参数接受一个 `StreamWatcher` 实例列表，可以同时传入多个 watcher。
- 某些命令（如 sudo、数据库客户端）在非 PTY 模式下不会输出密码提示，因此需要 `pty=True`。

### 示例：自动确认 apt-get install

```python
# tasks.py
from invoke import task, Responder


@task
def install_deps(c):
    """安装系统依赖，自动确认提示。"""
    # 自动回答 "Do you want to continue? [Y/n]" → 输入 Y
    confirm_prompt = Responder(
        pattern=r"Do you want to continue\? \[Y/n\]",
        response="Y\n",
    )

    c.run(
        "sudo apt-get install -y nginx postgresql",
        watchers=[confirm_prompt],
        pty=True,
    )
```

### 示例：多个 Responder 同时使用

一个 `c.run()` 调用可以传入多个 watcher，分别响应不同的提示：

```python
# tasks.py
from invoke import task, Responder


@task
def setup_ssh(c, host_key_password=None):
    """SSH 首次连接自动确认主机密钥 + 密码认证。"""
    # 自动确认 "Are you sure you want to continue connecting (yes/no)?"
    host_key_prompt = Responder(
        pattern=r"Are you sure you want to continue connecting \(yes/no\)\?",
        response="yes\n",
    )

    # 自动输入 SSH 密码
    password_prompt = Responder(
        pattern=r"\[sudo\] password for .*:|assword:",
        response=f"{host_key_password}\n",
    )

    c.run(
        "ssh user@new-server.example.com 'echo connected'",
        watchers=[host_key_prompt, password_prompt],
        pty=True,
    )
```

## 2. FailingResponder：带失败检测的响应

`FailingResponder` 继承自 `Responder`，额外增加了一个 `sentinel` 参数——当自动响应后如果在输出中检测到 sentinel 模式，说明响应被拒绝（如密码错误），会抛出 `ResponseNotAccepted` 异常。这对 sudo 密码等场景尤为重要，避免错误密码被反复尝试导致账户锁定。

### c.sudo() 内置的 FailingResponder

实际上，`c.sudo()` 方法内部已经自动使用了 `FailingResponder`，配置 sudo 密码后可以直接使用而无需手动创建 watcher：

```python
# tasks.py
from invoke import task


@task
def restart_service(c):
    """使用 c.sudo() 重启服务（自动处理密码响应与失败检测）。"""
    # sudo 密码可以通过配置文件、环境变量或运行时 --prompt-for-sudo-password 提供
    c.sudo("systemctl restart nginx")
    print("✅ nginx 已重启")
```

配置 sudo 密码的方式（在 `invoke.yaml` 或代码中）：

```yaml
# invoke.yaml
sudo:
  password: "your-sudo-password"
```

或者通过代码配置：

```python
# tasks.py
from invoke import task, Collection


@task
def restart_service(c):
    c.sudo("systemctl restart nginx")


ns = Collection(restart_service)
ns.configure({
    'sudo': {
        'password': 'your-sudo-password',
    },
})
```

`c.sudo()` 内部创建的 `FailingResponder` 等价于：

```python
FailingResponder(
    pattern=r"\[sudo\] password for .*:",   # 匹配 sudo 密码提示
    response="your-password\n",              # 自动输入密码
    sentinel="Sorry, try again.\n",          # 检测到此行说明密码错误
)
```

如果密码错误，会抛出 `AuthFailure` 异常，而不是无限循环地重试。

### 手动使用 FailingResponder

对于其他需要失败检测的交互式场景，可以手动创建 `FailingResponder`：

```python
# tasks.py
from invoke import task, FailingResponder


@task
def mysql_query(c, mysql_password="wrongpass"):
    """连接 MySQL 并执行查询，密码错误时抛出异常。"""
    # FailingResponder: 匹配密码提示 → 输入密码；如果看到 "ERROR 1045" 则报错
    mysql_auth = FailingResponder(
        pattern=r"Enter password:",
        response=f"{mysql_password}\n",
        sentinel=r"ERROR 1045",  # MySQL 认证失败的错误码
    )

    try:
        c.run(
            "mysql -u root -p -e 'SELECT 1;'",
            watchers=[mysql_auth],
            pty=True,
        )
        print("✅ MySQL 连接成功")
    except Exception as e:
        print(f"❌ MySQL 认证失败: {e}")
```

执行时如果密码错误：

```bash
$ inv mysql_query
Enter password:
ERROR 1045 (28000): Access denied for user 'root'@'localhost'
❌ MySQL 认证失败: Auto-response to r"Enter password:" failed with 'ERROR 1045'!
```

## 3. 自定义 StreamWatcher 子类

对于更复杂的交互逻辑（需要维护状态、动态生成响应、响应多个关联模式等），可以继承 `StreamWatcher` 基类实现自定义逻辑。子类需要实现 `submit(stream)` 方法，接收已读取的完整流内容，返回（yield）要写入 stdin 的字符串。

### 示例：自定义交互式部署确认

```python
# tasks.py
import re
from invoke import task, StreamWatcher


class DeploymentPrompter(StreamWatcher):
    """
    自定义 watcher：处理部署流程中的多级提示。
    - 匹配 "Are you sure? (yes/no)" → 自动输入 yes
    - 匹配 "Enter deployment ticket:" → 自动输入工单号
    - 匹配 "Confirm environment (staging/prod):" → 根据配置输入环境名
    - 如果看到 "ABORTED" 则停止响应
    """

    def __init__(self, ticket, environment="staging"):
        self.ticket = ticket
        self.environment = environment
        self.index = 0
        self.confirmed = False
        self.ticket_sent = False

    def submit(self, stream):
        # 只扫描上次 submit 之后新增的流内容
        new_content = stream[self.index:]

        # 检测中止信号
        if "ABORTED" in new_content:
            self.index = len(stream)
            return  # 不返回任何内容，放弃

        # 第一关：确认部署
        if not self.confirmed and re.search(r"Are you sure\? \(yes/no\)", new_content):
            self.confirmed = True
            self.index = len(stream)
            yield "yes\n"
            return

        # 第二关：输入工单号
        if self.confirmed and not self.ticket_sent and "Enter deployment ticket:" in new_content:
            self.ticket_sent = True
            self.index = len(stream)
            yield f"{self.ticket}\n"
            return

        # 第三关：确认环境
        if self.ticket_sent and "Confirm environment" in new_content:
            self.index = len(stream)
            yield f"{self.environment}\n"
            return

        # 更新索引，下次从新位置开始扫描
        self.index = len(stream)


@task
def deploy_production(c, ticket="OPS-2024-001"):
    """部署到生产环境（模拟多级交互提示）。"""
    prompter = DeploymentPrompter(ticket=ticket, environment="production")

    # 假设 deploy.sh 是一个交互式部署脚本
    c.run(
        "echo 'Starting deployment...' && "
        "echo 'Are you sure? (yes/no)' && read ans && "
        "echo 'Enter deployment ticket:' && read ticket && "
        "echo 'Confirm environment (staging/prod):' && read env && "
        "echo 'Deploying to' $env 'with ticket' $ticket",
        watchers=[prompter],
        pty=True,
    )
    print("✅ 生产环境部署完成")
```

### 示例：基于正则的动态响应

```python
# tasks.py
import re
from invoke import task, StreamWatcher


class RegexResponder(StreamWatcher):
    """通用正则响应器：支持 (pattern, response_fn) 对列表，动态生成响应。"""

    def __init__(self, handlers):
        """
        handlers: list of (pattern: str, response_fn: callable(match) -> str)
        """
        self.handlers = [(re.compile(p), fn) for p, fn in handlers]
        self.index = 0
        self.responded = set()  # 记录已响应过的模式

    def submit(self, stream):
        new_content = stream[self.index:]
        for pattern, response_fn in self.handlers:
            pattern_id = id(pattern)
            if pattern_id in self.responded:
                continue
            match = pattern.search(new_content)
            if match:
                self.responded.add(pattern_id)
                self.index = len(stream)
                response = response_fn(match)
                yield response
                return
        self.index = len(stream)


@task
def smart_install(c):
    """智能安装：根据提示动态生成响应。"""
    handlers = [
        # 自动确认安装
        (r"Do you want to continue\? \[Y/n\]", lambda m: "Y\n"),
        # 自动输入配置文件中的路径
        (r"Enter install directory \[.*?\]:", lambda m: "/opt/myapp\n"),
        # 对端口号提示自动分配端口
        (r"Enter port number \[(\d+)\]:", lambda m: f"{int(m.group(1)) + 1}\n"),
    ]

    watcher = RegexResponder(handlers)
    c.run(
        "echo 'Do you want to continue? [Y/n]' && read && "
        "echo 'Enter install directory [/usr/local]:' && read dir && "
        "echo 'Enter port number [8080]:' && read port && "
        "echo 'Installed to' $dir 'on port' $port",
        watchers=[watcher],
        pty=True,
    )
```

## 4. 结合 c.sudo() 与自定义 Watcher

`c.sudo()` 会自动添加 sudo 密码的 `FailingResponder`，你也可以在 `watchers` 中追加额外的 watcher 来处理其他提示：

```python
# tasks.py
from invoke import task, Responder


@task
def secure_setup(c):
    """使用 sudo 安装软件并处理额外的配置提示。"""
    # 额外的 watcher：处理包配置的交互提示
    config_prompt = Responder(
        pattern=r"Configuring .*",
        response="\n",  # 接受默认配置
    )

    # c.sudo() 自动添加 sudo 密码 watcher；我们通过 watchers 参数追加自定义 watcher
    c.sudo(
        "DEBIAN_FRONTEND=readline apt-get install -y mysql-server",
        watchers=[config_prompt],
        pty=True,
    )
```

## 相关概念

* [StreamWatcher 自动响应（§9）](../concepts/09-watchers.md)
* [Runner 与命令执行（§6）](../concepts/06-runners.md)
* [Context 对象（§3）](../concepts/03-context-object.md)
* [终端与 IO（§10）](../concepts/10-terminals-io.md)

[^pyinvoke-src]: PyInvoke 源码，见本 bundle 信源登记 [references/pyinvoke-source.md](../references/pyinvoke-source.md)。
