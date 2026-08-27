---
type: Example
title: 使用 Agent 面板
description: 掌握 intelligent-terminal 的 Agent 面板操作，包括快捷键打开/隐藏面板、Stash/Restore 面板状态、拖拽分屏、会话管理和 tmux 风格 CLI 命令控制终端。
tags:
  - intelligent-terminal
  - wta
  - agent-pane
  - tui
  - keyboard-shortcuts
  - tmux
related:
  - "[Agent Pane UI](../concepts/agent-pane-ui.md)"
  - "[Dual Process Architecture](../concepts/dual-process-architecture.md)"
  - "[WT CLI Command Tool](../concepts/wtcli-command-tool.md)"
  - "[Named Pipe Transport](../concepts/named-pipe-transport.md)"
sources:
  - "tools/wta/README.md"
  - "tools/wta/src/app.rs"
  - "tools/wta/src/app_keys.rs"
  - "tools/wta/src/cli/args.rs"
  - "tools/wta/src/shell/wt_channel/cli_channel.rs"
---

## 场景说明

intelligent-terminal 的 Agent 面板（Agent Pane）是 WTA 的 TUI 聊天界面，嵌入在 Windows Terminal 窗格中。每个终端标签页可以有一个关联的 Agent 面板，用户通过快捷键打开/隐藏、发送消息、查看建议、管理会话。此外，WTA 还提供 tmux 风格的 CLI 命令，允许通过命令行控制终端窗口、标签页和窗格。

本示例演示 Agent 面板的核心操作：快捷键导航、面板显隐、Stash/Restore、会话切换、分屏拖拽，以及使用 wta CLI 进行 tmux 风格的终端控制。

## 操作示例

### 示例 1：Agent 面板基本快捷键

在 Windows Terminal 中，Agent 面板支持以下快捷键操作：

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+.` | 打开/切换 Agent 面板（Stash/Restore） |
| `Ctrl+Shift+/` | 打开会话列表视图（Agents 视图） |
| `Ctrl+Alt+.` | 触发 Autofix（检测到错误时） |
| `Ctrl+C` | 取消当前正在生成的响应 |
| `Ctrl+C×2` | 关闭/隐藏 Agent 面板 |
| `Enter` | 发送消息 / 执行推荐操作 |
| `Escape` | 取消/关闭弹窗或 Autofix 建议 |
| `↑/↓` | 在输入框中浏览历史命令 |
| `Tab` | 在推荐选项间切换 |
| `Alt+V` | 粘贴剪贴板中的图片 |

### 示例 2：打开 Agent 面板并发送消息

```
步骤：
1. 在 Windows Terminal 中打开任意终端标签页（PowerShell、WSL、cmd 均可）
2. 按 Ctrl+Shift+. 打开 Agent 面板
3. 面板出现在当前窗格的分屏中，显示欢迎界面
4. 在输入框中输入问题，按 Enter 发送
5. Agent 响应流式显示在聊天区域
6. 再次按 Ctrl+Shift+. 将面板 Stash（隐藏但保留会话状态）
```

### 示例 3：Stash 和 Restore 面板状态

Agent 面板支持 Stash（暂存）模式——面板隐藏但 ACP 会话和聊天历史保持活跃：

```
Stash 操作：
- 按 Ctrl+Shift+. 当面板已打开时 → 面板隐藏（Stash）
- 面板中的 Agent 会话继续运行，不会中断正在生成的响应
- Autofix 等功能仍然在后台工作

Restore 操作：
- 在同一标签页按 Ctrl+Shift+. → 面板恢复显示
- 之前的聊天历史和会话状态完整保留
- 如果在 Stash 期间收到了 Autofix 结果，面板会显示 Review 提示

注意：Stash ≠ 关闭。Stash 保留会话和 ACP 连接；关闭（Ctrl+C×2）释放会话绑定。
```

### 示例 4：会话管理（Session Management）

通过会话列表视图管理多个 Agent 会话：

```
步骤：
1. 按 Ctrl+Shift+/ 打开会话列表（Agents 视图）
2. 列表显示当前标签页和历史标签页的 Agent 会话
3. 使用 ↑/↓ 选择会话
4. 按 Enter 在当前标签页恢复选中的会话
5. 按 Shift+Enter 在新标签页中恢复会话
6. 按 F2 恢复历史会话（从磁盘加载）

斜杠命令（在输入框中输入）：
/new        — 创建新会话（清除当前标签页的聊天历史）
/agent      — 切换 Agent（弹出 Agent 选择器）
/model      — 切换模型（弹出模型选择器）
/restart    — 重启 ACP 连接（重新初始化 Agent）
/sessions   — 打开会话列表（同 Ctrl+Shift+/）
```

### 示例 5：拖拽调整面板大小

Agent 面板作为 Windows Terminal 的标准窗格（Pane），支持拖拽操作：

```
1. 打开 Agent 面板后，面板与终端各占一半空间
2. 将鼠标移到面板与终端之间的分隔线上
3. 当光标变为调整大小图标时，拖拽分隔线调整面板宽度
4. Windows Terminal 会记住每个标签页的面板大小比例

也可以通过 wt 命令控制分屏大小：
```

### 示例 6：使用 wta CLI 进行 tmux 风格终端控制

`wta` CLI 提供类似 tmux 的终端控制命令，可以在脚本或 Agent 工具中调用：

```powershell
# 列出所有 Windows Terminal 窗口
wta list-windows
# 别名: wta lsw

# 列出指定窗口的标签页（不指定 window_id 则使用第一个窗口）
wta list-tabs
wta list-tabs -w <window-id>
# 别名: wta lst

# 列出标签页中的窗格
wta list-panes
wta list-panes -t <tab-id> -w <window-id>
# 别名: wta lsp

# 显示当前活动窗格信息
wta active-pane

# 水平分屏（左右并排）
wta split-pane -h -s 0.5 -c "pwsh.exe"
# -s 0.5 表示新窗格占 50% 空间

# 垂直分屏（上下堆叠）
wta split-pane -v -s 0.4
# 不指定 -c 则使用默认 profile

# 创建新标签页
wta new-tab -c "wsl.exe -d Ubuntu" -d "D:\projects" -n "Ubuntu Dev"
# 别名: wta neww

# 捕获窗格输出（类似 tmux capture-pane -p）
wta capture-pane -l 50
# --last-prompt: 只捕获最近一次完成的命令及其输出（需要 OSC 133 shell 集成）
wta capture-pane --last-prompt

# 关闭指定窗格
wta kill-pane -t <pane-id>
# 别名: wta killp

# 等待窗格中的进程退出
wta wait-for -t <pane-id> --timeout 30

# 查看窗格进程状态
wta pane-status -t <pane-id>

# 以委托模式在新标签页中打开 Agent
wta delegate "分析当前目录的 git 状态"
wta delegate --agent "codex" --delegate-model "gpt-5-codex" -c "D:\projects"
```

### 示例 7：监听终端事件

```powershell
# 监听 Windows Terminal 的 VT 序列和连接状态变化事件
wta listen

# 只监听特定窗格的事件
wta listen -t <pane-id>
# 别名: wta mon
```

事件输出示例：

```json
{"type":"event","method":"autofix_state","params":{"state":"detected","pane_id":"{12345}","summary":"Command 'npm t' exited with code 1","hotkey_hint":"Ctrl+Alt+."}}
{"type":"event","method":"autofix_state","params":{"state":"pending","pane_id":"{12345}","summary":"Command 'npm t' exited with code 1","tab_id":"{67890}"}}
```

### 示例 8：设置环境变量以允许 Agent 控制终端

```powershell
# PowerShell 中设置 WT_COM_CLSID 环境变量
wta set-env -s powershell | Invoke-Expression

# CMD 中设置
wta set-env -s cmd

# bash/WSL 中设置
eval $(wta set-env -s bash)
```

这会设置 `WT_COM_CLSID` 环境变量，使 wta CLI 能够通过 COM 接口与 Windows Terminal 通信。也可以通过 `wta pipe-id` 查看当前 WT 实例的 COM CLSID。

## 逐步解释

1. **双进程架构**：Agent 面板由 wta-helper（每个窗格的 TUI 进程）和 wta-master（单例 ACP 多路复用器）组成。`wta-master` 通过命名管道（`\\.\pipe\wta-master-<GUID>`）与 helper 通信，所有 helper 共享同一个 Agent CLI 子进程，避免重复启动。

2. **面板显隐机制**：Ctrl+Shift+. 触发的 Stash/Restore 通过 WT COM 接口控制窗格可见性。Stash 时 helper 进程保持运行，ACP 连接不断开；Restore 时 helper 重新附着到 master 的管道。

3. **会话绑定**：每个 WT 标签页通过 `owner_tab_id`（Stable GUID）与 ACP SessionId 绑定。`HelperConfig` 中的 `owner_tab_id` 和 `owner_window_id` 由 WT 在 spawn helper 时传入，确保面板绑定到正确的标签页。

4. **CLI 通道**：`cli_channel.rs` 通过 `wtcli.exe` 与 Windows Terminal 的 COM 接口通信，实现窗格控制（分屏、创建标签页、发送输入等）。这是 tmux 风格 CLI 命令的底层实现。

5. **TUI 状态机**：`app.rs` 实现了 TUI 的状态机，管理聊天视图、输入框、弹窗（Agent 选择器、模型选择器、权限确认）、推荐卡片和调试面板。

6. **事件协议**：WTA 通过 WT SendEvent 总线向 C++ 端发送 JSON 事件（如 `autofix_state`、`agent_state_changed`），C++ 端通过 VT 序列向 WTA 发送通知（命令完成、窗格变化等）。

## 输出结果

- 按 `Ctrl+Shift+.` 后 Agent 面板出现在当前窗格旁，可以立即与 Agent 对话
- `wta list-windows` 输出窗口列表 JSON（加 `--json` 参数）或人类可读表格
- `wta capture-pane --last-prompt` 输出最近一次命令及其输出（需 OSC 133 shell 集成）
- `wta delegate "任务"` 在新标签页打开 Agent 并自动执行任务
- Stash 后面板隐藏但 Agent 继续工作，Restore 后聊天历史完整保留

`wta list-windows` 输出示例：

```
Window ID                              Tabs
{abc123...}                            3
```

`wta active-pane` 输出示例：

```
Active pane: {def456...} in tab {789...}, window {abc123...}
```

## 注意事项

- **快捷键冲突**：如果 Ctrl+Shift+. 与其他软件冲突，可在 Windows Terminal 的 `actions` 配置中自定义键绑定。
- **Stash 不等于关闭**：Stash 状态下 ACP 连接保持活跃，Agent 仍在运行。长时间不使用建议用 `/new` 或 Ctrl+C×2 关闭以释放资源。
- **COM 接口依赖**：`wta split-pane`、`new-tab` 等 CLI 命令需要 WT_COM_CLSID 环境变量正确设置。如果命令报错"COM not available"，请先运行 `wta set-env | Invoke-Expression`。
- **capture-pane --last-prompt**：该功能依赖 OSC 133 shell 集成。未安装 shell 集成脚本时，此选项无法准确获取上一条命令输出。
- **委托模式是 fire-and-forget**：`wta delegate` 打开新标签页后立即返回，不等待 Agent 完成任务。
- **多窗口支持**：wta-master 是 per-window 单例，每个 WT 窗口有独立的 master 进程和命名管道。跨窗口的 Agent 会话是隔离的。
