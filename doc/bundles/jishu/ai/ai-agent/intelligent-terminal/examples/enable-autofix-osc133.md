---
type: Example
title: 启用 OSC 133 自动修复
description: 配置 Shell Integration 脚本以启用 OSC 133 协议（FinalTerm 命令标记），让 WTA 能够检测命令失败并自动触发 AI Autofix 修复建议，支持 PowerShell、bash、zsh、fish。
tags:
  - intelligent-terminal
  - wta
  - osc133
  - autofix
  - shell-integration
  - ftcs
related:
  - "[OSC 133 Autofix](../concepts/osc133-autofix.md)"
  - "[Settings Configuration](../concepts/settings-configuration.md)"
  - "[Agent Pane UI](../concepts/agent-pane-ui.md)"
sources:
  - "tools/wta/terminal-acp-shell-integration.md"
  - "tools/wta/src/app/autofix.rs"
  - "tools/wta/src/wt_protocol_events.rs"
  - "tools/wta/wt-agent-hooks/README.md"
---

## 场景说明

intelligent-terminal 的 Autofix（自动修复）功能通过 OSC 133 协议（FinalTerm Command Sequences，FTCS）检测终端中命令的执行结果。当 shell 发出 `OSC 133;D;<exit_code>` 序列标记命令完成且退出码非零时，WTA 会自动检测到失败，在终端底部显示"检测到错误"提示，用户可通过快捷键 `Ctrl+Alt+.` 触发 AI 分析并提供修复建议。

OSC 133 协议定义了 4 种标记序列：
- **A（Prompt Start）**：`ESC]133;A ST` — 提示符开始
- **B（Command Start）**：`ESC]133;B ST` — 命令开始执行
- **C（Command Executed）**：`ESC]133;C ST` — 命令已提交执行（输出前）
- **D（Command Finished）**：`ESC]133;D;<exit_code> ST` — 命令完成，携带退出码

要启用 Autofix，必须在 shell 中安装 Shell Integration 脚本来发射这些 OSC 序列。本示例演示为 PowerShell、bash、zsh、fish 配置 Shell Integration，以及如何使用和自定义 Autofix 行为。

## 配置示例

### 示例 1：PowerShell 7+ 配置 Shell Integration

PowerShell 7+ 可通过配置 `$PROFILE` 文件添加 Shell Integration：

```powershell
# 检查 PROFILE 文件是否存在
Test-Path $PROFILE

# 如果不存在则创建
if (!(Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }

# 编辑 PROFILE
notepad $PROFILE
```

在 `$PROFILE` 中添加以下内容：

```powershell
# Guard: 防止重复注入
if ($env:WT_SHELL_INTEGRATION) { return }
$env:WT_SHELL_INTEGRATION = "1"

# Emit shell self-identification (OSC 9001)
Write-Host -NoNewline ("`e]9001;ShellType;pwsh;CapFTCS,CapCompletions,CapOSC9`e\")

function prompt {
    # OSC 133;A — Prompt Start
    $exitCode = $LASTEXITCODE
    Write-Host -NoNewline ("`e]133;D;{0}`e\" -f $exitCode)
    Write-Host -NoNewline "`e]133;A`e\"

    # OSC 9;9 — CWD reporting (ConEmu style for PowerShell)
    $cwd = (Get-Location).Path
    Write-Host -NoNewline ("`e]9;9;`"{0}`"`e\" -f $cwd)

    # Your custom prompt here
    $promptString = "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "

    # OSC 133;B — Command Start (after prompt, before command input line)
    Write-Host -NoNewline "`e]133;B`e\"

    return $promptString
}

# Pre-command: OSC 133;C — Command Executed (fires before command output)
$ExecutionContext.InvokeCommand.PreCommandLookupAction = {
    param($commandName, $eventArgs)
    Write-Host -NoNewline "`e]133;C`e\"
}
```

> **注意**：PowerShell 5.1 不支持 `` `e `` 转义序列，需使用 `[char]0x1b` 替代：
> ```powershell
> $ESC = [char]0x1b
> Write-Host -NoNewline ("$ESC]133;D;$exitCode$ESC\")
> ```

### 示例 2：bash 配置 Shell Integration（Linux/WSL/Git Bash）

编辑 `~/.bashrc`：

```bash
# Guard against double-injection
[ -n "$WT_SHELL_INTEGRATION" ] && return
export WT_SHELL_INTEGRATION=1

# Shell self-identification
printf '\e]9001;ShellType;bash;CapFTCS,CapCompletions,CapOSC7\e\\'

# OSC 7 — CWD reporting (file URI)
__wt_osc7() {
    local url="file://$HOSTNAME"
    local dir="$PWD"
    # URL-encode the path
    printf -v encoded_dir '%s' "$dir" | sed 's/ /%20/g;s/!/%21/g;s/"/%22/g;s/#/%23/g;s/\$/%24/g;s/\&/%26/g;s/'"'"'/%27/g;s/(/%28/g;s/)/%29/g;s/\*/%2a/g;s/+/%2b/g;s/,/%2c/g;s/;/%3b/g;s/=/%3d/g;s/?/%3f/g;s/@/%40/g;s/\[/%5b/g;s/\]/%5d/g'
    printf '\e]7;%s%s\e\\' "$url" "$encoded_dir"
}

# PROMPT_COMMAND: runs before each prompt
__wt_prompt_command() {
    local exit_code=$?
    # OSC 133;D — Command Finished (with exit code from last command)
    printf '\e]133;D;%d\e\\' "$exit_code"
    # OSC 133;A — Prompt Start
    printf '\e]133;A\e\\'
    # Update CWD
    __wt_osc7
}
PROMPT_COMMAND="__wt_prompt_command;$PROMPT_COMMAND"

# PS0: fires right after command is read, before execution
PS0='\e]133;C\e\\'

# PS1: wrap prompt with OSC 133;B (Command Start marker at end of prompt)
PS1='\e]133;B\e\\'"$PS1"
```

对于 WSL Ubuntu（默认 bash），可以将此配置放入 `~/.bashrc`，重启 shell 即可生效。

### 示例 3：zsh 配置 Shell Integration

编辑 `~/.zshrc`：

```zsh
# Guard
[[ -n "$WT_SHELL_INTEGRATION" ]] && return
export WT_SHELL_INTEGRATION=1

# Shell self-identification
printf '\e]9001;ShellType;zsh;CapFTCS,CapCompletions,CapOSC7\e\\'

# OSC 7 — CWD reporting (using built-in URL encoding)
__wt_osc7() {
    printf '\e]7;file://%s%s\e\\' "$HOST" "${PWD// /%20}"
}

# precmd: runs before each prompt display
__wt_precmd() {
    local exit_code=$?
    printf '\e]133;D;%d\e\\' "$exit_code"
    printf '\e]133;A\e\\'
    __wt_osc7
}
precmd_functions+=(__wt_precmd)

# preexec: runs right before command execution
__wt_preexec() {
    printf '\e]133;C\e\\'
}
preexec_functions+=(__wt_preexec)

# End prompt with OSC 133;B (Command Start)
__wt_set_prompt() {
    PROMPT="%{$'\e]133;B'$'\e\\\\'%}${PROMPT}"
}
__wt_set_prompt
```

### 示例 4：fish 配置 Shell Integration

创建或编辑 `~/.config/fish/conf.d/wt-integration.fish`：

```fish
# Guard
if set -q WT_SHELL_INTEGRATION
    return
end
set -x WT_SHELL_INTEGRATION 1

# Shell self-identification
printf '\e]9001;ShellType;fish;CapFTCS,CapCompletions,CapOSC7\e\\'

# OSC 7 — CWD reporting
function __wt_osc7 --on-event fish_prompt
    printf '\e]7;file://%s%s\e\\' (hostname) (pwd | string replace ' ' '%20')
end

# fish_prompt event: prompt is about to show
function __wt_prompt_start --on-event fish_prompt
    # OSC 133;D from previous command (fish stores $status)
    printf '\e]133;D;%d\e\\' $status
    printf '\e]133;A\e\\'
end

# fish_preexec event: command is about to execute
function __wt_preexec --on-event fish_preexec
    printf '\e]133;C\e\\'
end

# Command start marker at end of prompt
function fish_prompt
    set_color $fish_color_cwd
    echo -n (prompt_pwd)
    set_color normal
    echo -n '> '
    printf '\e]133;B\e\\'
end
```

### 示例 5：验证 OSC 133 是否生效

配置完成后，重启 shell 并验证 OSC 序列是否正常发射：

```powershell
# PowerShell 中测试：运行一个会失败的命令
nonexistent_command
# 终端底部应该出现 Autofix 提示条
```

```bash
# bash/zsh 中测试
false  # exit code 1
# 终端底部应该出现 "Detected" 提示
```

验证 shell 集成是否被 WTA 检测到：

```powershell
# 在 Agent 面板中询问 Agent
# Agent 应该能通过 OSC 133 标记获取到命令退出码
```

### 示例 6：安装 wt-agent-hooks 桥接

WTA 还提供了 `wt-agent-hooks` 桥接，用于在 Agent CLI（Copilot、Claude 等）与 Windows Terminal 之间传递事件。安装方法：

```powershell
# 为所有支持的 CLI 安装 hooks
wta hooks install

# 查看安装状态
wta hooks status

# 为特定 CLI 安装
wta hooks install --cli copilot
wta hooks install --cli claude
wta hooks install --cli gemini
wta hooks install --cli codex

# 卸载 hooks
wta hooks uninstall
wta hooks uninstall --cli copilot
```

`wta hooks status` 输出示例：

```
CLI        Installed   Hooks Path
---        ---------   ----------
copilot    Yes         ~/.copilot/wt-agent-hooks/
claude     Yes         ~/.claude/wt-agent-hooks/
gemini     Yes         ~/.gemini/wt-agent-hooks/
codex      No          -
opencode   No          -
```

### 示例 7：控制 Autofix 行为

Autofix 有两种模式：自动建议模式（默认）和手动触发模式。

**通过命令行禁用 Autofix**：

```powershell
# 启动时禁用 Autofix（不自动检测错误）
wta --no-autofix
```

**使用自定义运行时提示调整 Autofix 行为**：

编辑 `%LOCALAPPDATA%\IntelligentTerminal\prompts\terminal-agent.md`，在 Autofix 部分添加指令：

```markdown
## Auto-Fix Behavior

When a command failure is detected:
1. First check if the error is due to a missing command or typo
2. Suggest the corrected command with explanation
3. For build/test errors, identify the root cause file and line
4. Always provide the fix as a recommended action card
5. Do NOT auto-execute commands that modify files without user approval
```

参考 `prompts/auto-fix.md` 了解默认的 Autofix 提示词模板。

## 逐步解释

1. **Autofix 状态机**：Autofix 由 `TabAutofixState` 管理，每个标签页独立跟踪自己的 Autofix 状态。状态流转为：`Idle` → `Detected`（检测到错误，显示提示条）→ `Pending`（AI 分析中）→ `Review`（结果就绪，等待用户查看）。

2. **错误检测**：当 shell 发射 `OSC 133;D;<exit_code>` 时，WT 的 VT 解析器在 `adaptDispatch.cpp` 中解析退出码，存储到 `ScrollbarData.exitCode`，然后通过 `autofix_state` 事件通知 WTA。`trigger_autofix_inner()` 处理错误通知并触发 LLM 分析。

3. **Detected 状态**：当自动建议模式关闭（`autofix_enabled=false`）时，只显示 `Detected` 提示条，不自动调用 LLM。用户按 `Ctrl+Alt+.` 或点击提示条触发分析。当自动建议模式开启时，直接进入 `Pending` 状态并发送 prompt 给 Agent。

4. **Shell Integration 层级**：根据终端-Shell 集成研究文档，Shell Integration 分为 4 个层级：
   - Level 0：无任何集成（裸 SSH 等）
   - Level 1：仅 OS 级检测（PEB CWD、autoMarkPrompts）
   - Level 2：最小 OSC（OSC 9;9 报告 CWD）
   - Level 3：FTCS 标记（OSC 133 A/B，无退出码）
   - Level 4：完整集成（OSC 133 A/B/C/D + 退出码 + CWD + Shell 类型）

   Autofix 功能要求 **Level 4**（需要 OSC 133;D 携带退出码）。

5. **OSC 7 vs OSC 9;9**：Windows 上的 PowerShell 使用 OSC 9;9（ConEmu 协议）报告 CWD，而 bash/zsh/fish（特别是 WSL 中）使用标准的 OSC 7（file:// URI）。两者都被 WTA 支持。

6. **wt-agent-hooks**：hooks 桥接在 Agent CLI（如 copilot CLI）内部安装事件发送脚本，使 WTA 能够知道 Agent CLI 何时启动/停止/发送事件，从而正确绑定窗格与会话。

## 输出结果

正确配置 Shell Integration 后：

1. 终端中命令失败（exit code ≠ 0）时，底部状态栏显示错误提示 pill，包含错误摘要和快捷键提示 `Ctrl+Alt+.`
2. 按 `Ctrl+Alt+.`（或自动建议模式开启时自动触发），Agent 开始分析错误，底部状态栏显示 "Analyzing…"
3. Agent 返回修复建议后，底部状态栏显示 "Review" 提示（如果 Agent 面板已关闭），打开面板即可看到建议
4. 建议以卡片形式展示，包含修复命令的推荐操作（RecommendedAction），用户按 Enter 确认执行
5. 按 Escape 可随时取消 Autofix 提示

Autofix 事件 JSON 格式（通过 `wta listen` 可观察）：

```json
// Detected: 检测到错误
{"type":"event","method":"autofix_state","params":{"state":"detected","pane_id":"{...}","summary":"Command 'npm t' exited with code 1","hotkey_hint":"Ctrl+Alt+."}}

// Pending: 正在分析
{"type":"event","method":"autofix_state","params":{"state":"pending","pane_id":"{...}","summary":"Command 'npm t' exited with code 1"}}

// Review: 结果就绪
{"type":"event","method":"autofix_state","params":{"state":"review","pane_id":"{...}","hotkey_hint":"Ctrl+Alt+."}}

// Cleared: 已清除
{"type":"event","method":"autofix_state","params":{"state":"cleared"}}
```

## 注意事项

- **cmd.exe 无法支持 OSC 133;D**：cmd.exe 没有 post-command hook 机制，无法在命令完成后发射退出码。在 cmd.exe 中 Autofix 完全无法工作，建议使用 PowerShell 或 WSL bash。
- **PowerShell 5.1 转义差异**：PowerShell 5.1 不支持 `` `e `` 转义符（PS7+ 才支持），必须使用 `[char]0x1b` 代替。
- **避免重复注入**：所有 Shell Integration 脚本开头都要有 guard（`WT_SHELL_INTEGRATION` 检查），否则每次启动子 shell 都会重复注册 hook，导致 OSC 序列重复发射。
- **autoMarkPrompts 兜底**：Windows Terminal 默认开启 `autoMarkPrompts`，会在按 Enter 时自动添加提示标记（Level 1），但无法获取退出码。这是降级方案，不如手动配置的 Shell Integration 可靠。
- **TUI 应用干扰**：当运行 vim、htop、less 等 TUI 应用时，它们使用备用屏幕缓冲区，OSC 133 标记可能被干扰。退出 TUI 后恢复正常。
- **WSL 路径转换**：在 WSL 中配置 Shell Integration 时，OSC 7 报告的是 Linux 路径（`/home/user/project`），WTA 会自动处理 WSL 到 Windows 的路径映射。
- **Autofix 不会自动执行命令**：出于安全考虑，Autofix 只提供建议和推荐操作卡片，用户必须按 Enter 确认才会执行命令，不会自动修改文件或运行危险命令。
- **SSH 会话限制**：通过 SSH 连接到远程服务器时，远程 shell 需要配置 Shell Integration 才能支持 Autofix，且本地的 PEB CWD 回退机制无法读取远程进程信息。
