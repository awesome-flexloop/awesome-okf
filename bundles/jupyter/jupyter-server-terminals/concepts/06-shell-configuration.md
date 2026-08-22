---
type: Concept
title: Shell 配置与平台差异
description: 终端 Shell 配置机制——平台默认 Shell、自定义 Shell 命令、Login Shell 模式、环境变量传递、跨平台行为差异
tags: [jupyter, terminals, shell, configuration, cross-platform, powershell, bash]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# Shell 配置与平台差异

## Shell 确定流程

终端使用的 Shell 命令在 `TerminalsExtensionApp.initialize_configurables()` 中确定，遵循一套优先级链：

```python
# app.py
default_shell = "powershell.exe" if os.name == "nt" else which("sh")
shell_override = self.serverapp.terminado_settings.get("shell_command")
if isinstance(shell_override, str):
    shell_override = shlex.split(shell_override)
shell = (
    [os.environ.get("SHELL") or default_shell] if shell_override is None else shell_override
)
if os.name != "nt" and shell_override is None and not sys.stdout.isatty():
    shell.append("-l")
```

决策流程可以表示为：

```
确定 Shell 命令
    │
    ├─ 1. 用户自定义了 terminado_settings["shell_command"]?
    │   └─ Yes → 使用自定义命令（字符串自动 shlex.split 分词）
    │
    └─ No → 使用默认 Shell
        │
        ├─ Windows (os.name == "nt") → "powershell.exe"
        │
        └─ 非 Windows → $SHELL 环境变量?
            ├─ Yes → [$SHELL]
            └─ No → [which("sh")]（通常是 /bin/sh 或 /bin/bash）
                │
                └─ 非 TTY 环境 + 无自定义 Shell?
                    └─ Yes → 追加 "-l"（login shell）
```

## 平台默认 Shell

| 平台 | os.name | 默认 Shell | 说明 |
|------|---------|-----------|------|
| Windows | `"nt"` | `powershell.exe` | 使用 PowerShell，非 cmd.exe |
| Linux/macOS | `"posix"` | `$SHELL` 或 `sh` | 优先使用用户默认 Shell，回退到 sh |

Windows 上没有使用 `cmd.exe` 作为默认 Shell，而是直接使用 `powershell.exe`。

## 自定义 Shell 命令

通过 Jupyter Server 配置可以覆盖默认 Shell：

```python
# jupyter_server_config.py
c.ServerApp.terminado_settings = {
    "shell_command": "/bin/zsh"
}

# 或者带参数
c.ServerApp.terminado_settings = {
    "shell_command": ["/bin/bash", "--login"]
}
```

两种格式均可：
- **字符串格式**：`"/bin/zsh -l"` 会通过 `shlex.split()` 自动分词为 `["/bin/zsh", "-l"]`
- **列表格式**：`["/bin/bash", "--login"]` 直接使用，不做分词

自定义 Shell 时不会自动追加 `-l` 参数，如需 login shell 需手动指定。

## Login Shell 模式

在非 Windows 平台上，当以下条件同时满足时，扩展会自动追加 `-l` 参数启用 login shell：

1. **非 Windows**：`os.name != "nt"`
2. **无自定义 Shell**：`shell_override is None`
3. **非交互式环境**：`not sys.stdout.isatty()`（即 Jupyter Server 不是在终端中直接启动）

这一逻辑的设计意图是：当 Jupyter Server 由 JupyterHub 等 spawner 启动（而非用户在终端中直接运行），用户环境可能尚未初始化（如 `/etc/profile`、`~/.bash_profile` 未被 source），login shell 可以确保环境变量、PATH 等正确加载。

如果你在非 TTY 环境中不希望使用 login shell，可以通过显式设置 `shell_command` 来覆盖：

```python
c.ServerApp.terminado_settings = {
    "shell_command": ["/bin/bash"]  # 不追加 -l
}
```

## 传递给终端的环境变量

创建 TerminalManager 时，`extra_env` 字典传递两个环境变量给终端进程：

```python
self.terminal_manager = self.terminal_manager_class(
    shell_command=shell,
    extra_env={
        "JUPYTER_SERVER_ROOT": self.serverapp.root_dir,
        "JUPYTER_SERVER_URL": self.serverapp.connection_url,
    },
    parent=self.serverapp,
)
```

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `JUPYTER_SERVER_ROOT` | Jupyter Server 的根目录（notebook 启动目录） | `/home/user/notebooks` |
| `JUPYTER_SERVER_URL` | Jupyter Server 的完整连接 URL（含 token） | `http://localhost:8888/?token=abc123...` |

终端 Shell 中可以直接使用这些环境变量：

```bash
echo "Jupyter root: $JUPYTER_SERVER_ROOT"
echo "Server URL: $JUPYTER_SERVER_URL"
cd $JUPYTER_SERVER_ROOT
```

## 工作目录（cwd）处理

创建终端时可以指定初始工作目录：

```bash
curl -X POST http://localhost:8888/api/terminals \
  -H "Content-Type: application/json" \
  -d '{"cwd": "/home/user/projects"}'
```

cwd 参数的解析逻辑（在 `TerminalRootHandler.post()` 中）：

1. 尝试将 cwd 作为绝对路径解析，如果存在则使用
2. 如果是相对路径或绝对路径不存在，尝试相对于 `server_root_dir` 拼接
3. 如果拼接后的路径仍不存在，**静默忽略 cwd**（终端使用默认工作目录，通常是 Jupyter Server 启动目录）

这种设计确保无效的 cwd 不会导致错误，终端始终能创建成功。

## 跨平台注意事项

### Windows 特定行为

- 默认 Shell 是 PowerShell（`powershell.exe`），不是 CMD
- Windows 依赖 `pywinpty` 包提供 PTY 功能
- 不使用 login shell（`-l`）逻辑（Windows Shell 没有该概念）
- cwd 测试中的路径分隔符和比较逻辑在 Windows 上有所不同

### Linux/macOS 特定行为

- 默认使用 `$SHELL` 环境变量指定的 Shell
- 非 TTY 环境自动使用 login shell
- PTY 通过系统原生的 `/dev/ptmx` 机制实现

### 路径分隔符

WebSocket 测试中的路径比较考虑了平台差异：

```python
expected = terminal_root_dir.name if sys.platform == "win32" else str(terminal_root_dir)
```

Windows 上只比较目录名（避免盘符和路径分隔符差异导致测试失败）。

## 常见配置示例

### 使用 Zsh

```python
c.ServerApp.terminado_settings = {
    "shell_command": ["/bin/zsh", "-l"]
}
```

### 使用 Fish Shell

```python
c.ServerApp.terminado_settings = {
    "shell_command": ["/usr/bin/fish", "-l"]
}
```

### Windows 使用 CMD（不推荐）

```python
c.ServerApp.terminado_settings = {
    "shell_command": "cmd.exe"
}
```

### 禁用终端

```python
c.ServerApp.terminals_enabled = False
```

## 相关概念

- [TerminalsExtensionApp 扩展应用](/concepts/02-extension-app.md)
- [5分钟快速上手](/concepts/01-getting-started.md)
- [TerminalManager 终端管理器](/concepts/03-terminal-manager.md)
- [配置自动清理与指定工作目录](/examples/culler-and-cwd.md)
- [jupyter_server_terminals 源码信源登记](/references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](/references/jupyter-server-terminals-source.md)。
