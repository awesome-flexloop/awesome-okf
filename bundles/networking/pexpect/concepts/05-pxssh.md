---
type: Concept
title: pxssh SSH 自动化
description: pxssh 类详解——login/logout/prompt、唯一提示符机制、force_password、SSH 选项与隧道
tags: [pexpect, pxssh, ssh, automation]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# pxssh SSH 自动化

## pxssh 的定位

`pxssh` 类（`pexpect/pxssh.py`）继承自 `spawn`，专门用于 SSH 连接自动化。它在 spawn 的基础上添加了：

- **`login()`**：处理完整的 SSH 登录流程（主机密钥确认、密码/密钥认证、终端类型、提示符同步）
- **`logout()`**：优雅退出远程 shell
- **`prompt()`**：等待 shell 提示符出现的快捷方法
- **`set_unique_prompt()`**：将远程 shell 提示符重置为唯一字符串，避免 MOTD 等输出干扰

## 基本使用

```python
from pexpect import pxssh

s = pxssh.pxssh()
s.login('remote-host', 'username', 'password')
s.sendline('uptime')
s.prompt()
print(s.before.decode())
s.logout()
```

使用上下文管理器：

```python
with pxssh.pxssh() as s:
    s.login('host', 'user', 'password')
    s.sendline('whoami')
    s.prompt()
    print(s.before.decode())
```

## 构造函数

```python
pxssh(timeout=30, maxread=2000, searchwindowsize=None,
      logfile=None, cwd=None, env=None, ignore_sighup=True, echo=True,
      options={}, encoding=None, codec_errors='strict',
      debug_command_string=False, use_poll=False)
```

与 `spawn.__init__` 的关键区别：

| 参数 | spawn 默认 | pxssh 默认 | 原因 |
|------|-----------|-----------|------|
| `ignore_sighup` | `False` | `True` | SSH 会话通常应忽略 SIGHUP |
| `command` | 必填 | 无（传 None） | pxssh 延迟启动，login() 时才 spawn ssh 命令 |
| `options` | 无 | `{}` | SSH 客户端选项字典 |
| `debug_command_string` | 无 | `False` | 仅用于测试，返回 SSH 命令字符串而不执行 |

## login() 方法

完整签名：

```python
login(server, username=None, password='', terminal_type='ansi',
      original_prompt=r"[#$]", login_timeout=10, port=None,
      auto_prompt_reset=True, ssh_key=None, quiet=True,
      sync_multiplier=1, check_local_ip=True,
      password_regex=r'(?i)(?:password:)|(?:passphrase for key)',
      ssh_tunnels={}, spawn_local_ssh=True,
      sync_original_prompt=True, ssh_config=None, cmd='ssh')
```

### 核心参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `server` | （必填） | 远程主机名或 IP |
| `username` | `None` | 用户名；为 None 时必须提供 ssh_config 且其中包含 User |
| `password` | `''` | 密码（密码认证时使用） |
| `terminal_type` | `'ansi'` | 终端类型（TERM 环境变量） |
| `login_timeout` | `10` | 登录阶段超时秒数 |
| `port` | `None` | SSH 端口（默认 22） |
| `auto_prompt_reset` | `True` | 登录后自动重置提示符为 UNIQUE_PROMPT |
| `ssh_key` | `None` | SSH 私钥文件路径；True 表示转发认证 agent |
| `quiet` | `True` | 添加 `-q` 静默选项 |
| `sync_original_prompt` | `True` | 登录后尝试同步原始提示符 |
| `ssh_config` | `None` | SSH config 文件路径 |
| `cmd` | `'ssh'` | SSH 客户端命令（可替换为网络命名空间包装） |
| `ssh_tunnels` | `{}` | 端口转发配置 |

### 登录流程

login() 内部通过 expect 模式列表处理 SSH 登录的各种情况：

```python
session_init_regex_array = [
    "(?i)are you sure you want to continue connecting",  # 0: 新主机密钥
    original_prompt,                                      # 1: 已在提示符（密钥认证）
    password_regex,                                       # 2: 密码/密码短语提示
    "(?i)permission denied",                              # 3: 权限拒绝
    "(?i)terminal type",                                  # 4: 终端类型查询
    TIMEOUT,                                              # 5: 超时
    "(?i)connection closed by remote host",               # 6: 连接被关闭
    EOF,                                                  # 7: EOF
]
```

处理逻辑：
1. **索引 0**（新主机密钥）：发送 `yes` 接受，继续 expect
2. **索引 2**（密码提示）：发送密码，继续 expect
3. **索引 4**（终端类型）：发送 terminal_type，继续 expect
4. **索引 1**（直接到提示符）：密钥认证成功
5. **索引 3/6/7**：抛出 `ExceptionPxssh`
6. **索引 5**（超时）：假设已登录（可能提示符太特殊无法匹配）
7. 登录后调用 `sync_original_prompt()` 和 `set_unique_prompt()`

## 唯一提示符机制

pxssh 的核心设计是将远程 shell 的 PS1 改为不可能在正常输出中出现的字符串：

```python
self.UNIQUE_PROMPT = r"\[PEXPECT\][\$\#] "
self.PROMPT = self.UNIQUE_PROMPT
```

### set_unique_prompt()

login() 成功后自动调用，依次尝试三种 shell 的提示符设置命令：

```python
self.PROMPT_SET_SH = r"PS1='[PEXPECT]\$ '"       # sh/bash
self.PROMPT_SET_CSH = r"set prompt='[PEXPECT]\$ '"  # csh/tcsh
self.PROMPT_SET_ZSH = "prompt restore;\nPS1='[PEXPECT]%(!.#.$) '"  # zsh
```

方法逻辑：
1. 发送 `unset PROMPT_COMMAND`（禁用 bash 的 PROMPT_COMMAND）
2. 发送 sh 风格的 PS1 设置
3. expect `[TIMEOUT, PROMPT]`
4. 若超时（说明不是 sh），尝试 csh 风格
5. 若再超时，尝试 zsh 风格
6. 全部失败返回 False（login 抛出 ExceptionPxssh）

### 微妙的 hack

源码注释指出：设置提示符的命令字符串与匹配正则故意不同。设置命令中 `$` 前有反斜杠（`\$`），确保命令本身在终端回显时不会被 UNIQUE_PROMPT 正则误匹配。

### prompt() 方法

```python
prompt(timeout=-1)
```

这是 `expect([self.PROMPT, TIMEOUT], timeout=timeout)` 的快捷方式。返回 True 表示匹配到提示符，False 表示超时。

```python
s.sendline('ls -la')
if s.prompt(timeout=30):
    print(s.before.decode())
else:
    print("Command timed out")
```

### 自定义提示符

如果不希望 pxssh 自动重置提示符：

```python
s.login('host', 'user', 'password', auto_prompt_reset=False)
s.PROMPT = r'my-custom-prompt> '  # 手动设置
s.prompt()
```

## force_password

`force_password` 属性（默认 False）设为 True 时，在 SSH 命令行追加 `-o 'PubkeyAuthentication=no'`，强制使用密码认证。这在 ssh-agent 运行时避免弹出 GUI 密码对话框：

```python
s = pxssh.pxssh()
s.force_password = True
s.login('host', 'user', 'password')
```

## SSH 选项

通过 `options` 字典传递 SSH 客户端选项：

```python
s = pxssh.pxssh(options={
    "StrictHostKeyChecking": "no",
    "UserKnownHostsFile": "/dev/null",
    "LogLevel": "ERROR",
})
s.login('host', 'user', 'password')
```

生成的 SSH 命令形如：

```
ssh -o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' -q -l user host
```

## SSH 密钥认证

```python
# 使用指定私钥
s.login('host', 'user', ssh_key='/home/user/.ssh/id_ed25519')

# 转发 SSH agent（-A 选项）
s.login('host', 'user', ssh_key=True)

# 使用 SSH config 文件
s.login('host', ssh_config='/home/user/.ssh/config')
```

当 `ssh_key` 为文件路径时，添加 `-i <path>` 选项；为 `True` 时添加 `-A` 选项转发 agent。

## 端口转发

通过 `ssh_tunnels` 参数配置本地/远程/动态端口转发：

```python
tunnels = {
    'local': ['8080:localhost:80'],       # -L 8080:localhost:80
    'remote': ['9090:localhost:3306'],    # -R 9090:localhost:3306
    'dynamic': [1080],                     # -D 1080 (SOCKS)
}
s.login('host', 'user', 'password', ssh_tunnels=tunnels)
```

## logout()

```python
logout()
```

发送 `exit` 命令。如果检测到 "there are stopped jobs"，自动发送第二次 exit，然后关闭连接。

```python
s.logout()
```

## sync_original_prompt()

在重置提示符之前，pxssh 通过发送多次回车并比较响应来检测原始提示符：

```python
sync_original_prompt(sync_multiplier=1.0)
```

- 发送 4 次回车，用 `try_read_prompt()` 读取响应
- 计算第 3 次和第 4 次响应的 Levenshtein 距离
- 如果相似度 > 60%（距离/长度 < 0.4），认为已到提示符
- `sync_multiplier` 调整超时倍数，慢速连接可增大此值

## ExceptionPxssh

pxssh 所有错误都抛出 `ExceptionPxssh`（继承 `ExceptionPexpect`）：

```python
from pexpect import pxssh

try:
    s = pxssh.pxssh()
    s.login('host', 'user', 'wrong-password')
except pxssh.ExceptionPxssh as e:
    print(f"pxssh failed: {e}")
```

常见错误消息：
- `'Could not establish connection to host'`
- `'password refused'`
- `'permission denied'`
- `'could not synchronize with original prompt'`
- `'could not set shell prompt'`
- `'connection closed'`

## 相关概念

- [spawn 类详解](/concepts/02-spawn-class.md)
- [expect 模式匹配](/concepts/03-expect-patterns.md)
- [跨平台 spawn 变体](/concepts/06-cross-platform-spawn.md)
- [SSH 自动登录示例](/examples/ssh-login-automation.md)
- [密码提示处理示例](/examples/password-prompts.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](/references/pexpect-source.md)。
