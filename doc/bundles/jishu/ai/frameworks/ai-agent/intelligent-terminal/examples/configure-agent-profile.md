---
type: Example
title: 配置 Agent Profile
description: 通过 Windows Terminal settings.json 配置 WTA 的 Agent CLI 路径、委托 Agent 和模型参数，选择内置 Agent（Copilot/Claude/Codex/Gemini/OpenCode）或自定义命令。
tags:
  - intelligent-terminal
  - wta
  - configuration
  - settings.json
  - agent-profile
related:
  - "[Agent Registry](../concepts/agent-registry.md)"
  - "[Settings Configuration](../concepts/settings-configuration.md)"
  - "[Dual Process Architecture](../concepts/dual-process-architecture.md)"
sources:
  - "tools/wta/CUSTOMIZATION.md"
  - "tools/wta/src/agent_registry.rs"
  - "tools/wta/src/cli/args.rs"
  - "tools/wta/src/helper/config.rs"
---

## 场景说明

intelligent-terminal 的 WTA（Windows Terminal Agent）通过内置的 Agent 注册表支持 5 种 Agent CLI：GitHub Copilot、Claude Code、Codex、Gemini CLI 和 OpenCode。用户可以通过 Windows Terminal 的 `settings.json` 文件配置默认使用哪个 Agent、传递哪些启动参数（如模型选择），以及配置委托模式（Delegate）使用的 Agent CLI。配置修改后需重启 Terminal 生效。

本示例演示如何定位 settings.json、配置 Agent CLI 路径与模型、配置委托 Agent，以及使用命令行参数临时覆盖配置。

## 配置示例

### 示例 1：定位并编辑 settings.json（Packaged 版本）

Packaged 版本（Microsoft Store 安装）的 settings.json 路径：

```powershell
# 打开 Packaged 版本的 settings.json 所在目录
explorer "$env:LOCALAPPDATA\Packages\Microsoft.IntelligentTerminal_8wekyb3d8bbwe\LocalState"

# 使用 VS Code 直接编辑
code "$env:LOCALAPPDATA\Packages\Microsoft.IntelligentTerminal_8wekyb3d8bbwe\LocalState\settings.json"
```

### 示例 2：定位并编辑 settings.json（Portable 版本）

Portable/本地安装版本的 settings.json 路径：

```powershell
# 打开 Portable 版本的 settings 目录
explorer "$env:LOCALAPPDATA\Programs\IntelligentTerminal\settings"

# 使用 VS Code 直接编辑
code "$env:LOCALAPPDATA\Programs\IntelligentTerminal\settings\settings.json"
```

### 示例 3：配置 Agent CLI 路径和模型

在 settings.json 中添加或修改 `agentCliPath` 字段：

```json
{
  "$schema": "https://aka.ms/terminal-profiles-schema",
  "defaultProfile": "{574e775e-4f2a-5b96-ac1e-a2962a402336}",
  "agentCliPath": "copilot --acp --stdio --model gpt-5",
  "profiles": {
    "defaults": {},
    "list": [
      {
        "guid": "{574e775e-4f2a-5b96-ac1e-a2962a402336}",
        "name": "PowerShell",
        "commandline": "pwsh.exe"
      }
    ]
  }
}
```

常用 Agent 配置：

```json
// 使用 GitHub Copilot（默认），指定模型
"agentCliPath": "copilot --acp --stdio --model gpt-5"

// 使用 Claude Code（通过 npx ACP 适配器）
"agentCliPath": "npx -y @agentclientprotocol/claude-agent-acp"

// 使用 Codex（固定适配器版本）
"agentCliPath": "npx -y @agentclientprotocol/codex-acp@1.1.4"

// 使用 Gemini CLI（原生 ACP 支持）
"agentCliPath": "gemini --experimental-acp --model gemini-2.5-pro"

// 使用 OpenCode（原生 ACP 支持）
"agentCliPath": "opencode acp"
```

### 示例 4：配置委托 Agent CLI

委托模式（Delegate）用于在新标签页/面板中启动 Agent 执行一次性任务，独立于 ACP 模式配置：

```json
{
  "agentCliPath": "copilot --acp --stdio --model gpt-5",
  "delegateAgentCliPath": "codex --model gpt-5-codex"
}
```

委托模式下，WTA 会自动将 ACP 标志从命令中剥离。例如 ACP 模式的 `copilot --acp --stdio --model gpt-5` 在委托模式下会自动转换为 `copilot --model gpt-5`。

### 示例 5：使用命令行参数临时覆盖

直接运行 `wta` 时可通过命令行参数覆盖 settings.json 配置：

```powershell
# 指定 Agent 和模型启动 WTA
wta --agent "copilot --acp --stdio --model claude-haiku-4.5"

# 指定规范的 Agent ID（推荐，避免命令解析歧义）
wta --agent "copilot --acp --stdio" --agent-id copilot --acp-model "gpt-5"

# 启动时直接发送初始提示
wta "帮我分析当前目录的项目结构"

# 在 WSL 发行版中运行 Agent
wta --agent "copilot --acp --stdio" --agent-source wsl --agent-wsl-distro Ubuntu

# 禁用自动修复功能
wta --no-autofix

# 启动时直接进入会话列表视图
wta --initial-view sessions
```

### 示例 6：自定义运行时提示（System Prompt）

WTA 支持自定义 Agent 的运行时提示词，该文件在每次提交提示时重新加载：

```powershell
# 创建自定义提示目录
New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\IntelligentTerminal\prompts" | Out-Null

# 复制默认提示作为参考
Copy-Item "$env:LOCALAPPDATA\IntelligentTerminal\prompts\terminal-agent.default.md" `
          "$env:LOCALAPPDATA\IntelligentTerminal\prompts\terminal-agent.md"

# 编辑自定义提示
notepad "$env:LOCALAPPDATA\IntelligentTerminal\prompts\terminal-agent.md"
```

自定义提示示例内容（追加到默认提示之后）：

```markdown
## Additional Instructions

- Always respond in Chinese unless the user explicitly requests English.
- When suggesting shell commands, prefer PowerShell syntax on Windows.
- For file operations, always verify paths before executing.
- When analyzing errors, include the exit code if available.
```

## 逐步解释

1. **定位配置文件**：根据安装方式（Packaged/Portable）选择正确的 settings.json 路径。Packaged 版本位于 `%LOCALAPPDATA%\Packages\` 下的应用数据目录，Portable 版本位于 `%LOCALAPPDATA%\Programs\IntelligentTerminal\settings\`。

2. **`agentCliPath` 字段**：这是核心配置项，指定启动 ACP Agent 的完整命令行。内置 Agent 通过 `AgentProfile` 结构体定义，包含 ACP 启动标志、模型标志、认证流程等元数据。

3. **内置 Agent 解析**：`lookup_profile()` 函数会自动从命令行中提取 Agent ID，剥离路径和扩展名（`.exe`/`.cmd`/`.bat`），然后匹配到对应的 `AgentProfile`。

4. **ACP 命令构建**：`build_acp_command()` 根据 Agent ID 和模型参数构建完整的 ACP 启动命令。对于不支持原生 ACP 的 Agent（如 Claude、Codex），会自动使用 npx 适配器命令。

5. **`delegateAgentCliPath` 字段**：配置委托模式的 Agent CLI。委托模式通过 `strip_acp_flags_for_delegate()` 自动剥离 ACP 特有标志，保留模型参数。

6. **命令行参数优先级**：CLI 参数（`--agent`、`--agent-id`、`--acp-model` 等）优先级高于 settings.json 配置。`Cli` 结构体定义了所有可用参数。

7. **WSL Agent 支持**：通过 `--agent-source wsl --agent-wsl-distro <name>` 可在 WSL 发行版中运行 Agent。`AgentSource` 枚举支持 Host 和 Wsl 两种执行环境，CWD 会自动转换为 POSIX 路径。

8. **运行时提示热加载**：`terminal-agent.md` 在每次提示提交时重新加载，无需重启 Terminal 即可修改 Agent 的行为指令。

## 输出结果

配置完成后重启 Windows Terminal，打开 Agent 面板（默认快捷键 Ctrl+Shift+.）即可看到配置生效：

- Agent 面板标题栏显示当前 Agent 名称（如 "GitHub Copilot"、"Claude"）
- 模型选择器（`/model` 命令）列出所选 Agent 支持的模型
- 命令失败时自动触发 Autofix（除非使用了 `--no-autofix`）
- 委托 Agent 命令（`wta delegate "任务描述"`）使用 `delegateAgentCliPath` 配置的 Agent

验证配置是否生效：

```powershell
# 使用 wta CLI 探测 Agent 的可用模型列表
wta probe-models --agent "copilot --acp --stdio"
# 输出示例:
# {"available_models":[{"id":"gpt-5","name":"GPT-5","description":"..."},
#  {"id":"gpt-4.1","name":"GPT-4.1","description":"..."}],
#  "current_model_id":"gpt-5"}
```

## 注意事项

- **重启生效**：修改 settings.json 后必须完全关闭并重新打开 Windows Terminal 才能生效，直接关闭标签页不够。
- **ACP 标志必须正确**：原生 ACP Agent（copilot、gemini、opencode）必须包含 ACP 模式标志（`--acp --stdio`、`--experimental-acp`、`acp`），否则 Agent 会以交互 TUI 模式启动而非 ACP 协议模式。
- **适配器版本钉扎**：Codex 的 npx 适配器使用 `@1.1.4` 版本钉扎，未钉扎版本可能因上游更新导致启动失败。
- **npx 首次启动延迟**：Claude/Codex 通过 npx 启动适配器，首次运行需要下载 npm 包，可能有 10-60 秒延迟。
- **委托模式不使用 ACP**：委托 Agent 在独立终端标签页中以交互模式运行，不通过 ACP 协议通信，因此不需要 ACP 标志。
- **PATH 解析**：WTA 通过 `resolve_bare_agent_name()` 在 PATH 中搜索 Agent 可执行文件，搜索顺序为 `.exe` → `.cmd`。如果 Agent 不在 PATH 中，需使用完整路径。
- **自定义 Agent**：settings.json 中可以使用任意命令行作为 `agentCliPath`，但只有注册在 `KNOWN_AGENTS` 中的 Agent 才有完整的 Profile 支持（模型选择、认证提示等）。未注册的命令使用默认 Profile。
