---
type: Concept
title: CLI 命令与会话管理
description: deepcode-cli 提供丰富的命令行参数和斜杠命令，支持交互式 TUI 和非交互执行模式，会话自动持久化并支持恢复、分叉和撤销操作。
tags: [deepcode-cli, cli, 命令行, 会话管理, tui, slash-commands]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: deepcode-cli 源码信源
---

# CLI 命令与会话管理

## 命令行参数

CLI 使用 [yargs](https://github.com/yargs/yargs) 解析命令行参数，定义于 `packages/cli/src/cli-args.ts`。

### 参数列表

| 参数 | 别名 | 类型 | 说明 |
|------|------|------|------|
| `--prompt` | `-p` | string | 启动时提交提示文本 |
| `--exec` | `-x` | boolean | 非交互模式运行单次提示（需配合 `--prompt`） |
| `--resume` | `-r` | string | 恢复指定会话（不带值时显示选择器） |
| `--fork` | `-f` | string | 从指定会话分叉（不带值时分叉最近会话） |
| `--last` | `-l` | boolean | 恢复当前项目最近的会话 |
| `--version` | `-v` | boolean | 显示版本号 |
| `--help` | `-h` | boolean | 显示帮助信息 |

### 参数校验规则

`cli-args.ts:114-155` 中的 `.check()` 回调实现以下校验：

- `--prompt` 与位置参数 query 不能同时使用
- 裸 `--resume`（无 ID）不能与 `--prompt` 同时使用
- `--last` 不能与 `--resume` 同时使用
- `--fork` 不能与 `--resume` 同时使用
- `--last` 不能与 `--fork` 同时使用
- `--resume <sessionId>` 和 `--fork <sessionId>` 的值必须符合 UUID v4 格式
- `--prompt` 的值不能为空字符串
- `--exec` 必须配合非空的 `--prompt` 使用
- `--exec` 不能使用裸 `--resume`（无 ID）

### 使用示例

```bash
# 启动交互式 TUI
deepcode

# 启动并提交提示
deepcode -p "解释这段代码"

# 非交互模式运行单次提示
deepcode -x -p "列出当前目录的文件"

# 管道输入作为上下文
cat error.log | deepcode -x -p "Explain this error"

# 恢复指定会话
deepcode --resume 123e4567-e89b-12d3-a456-426614174000

# 恢复最近会话
deepcode --last

# 从最近会话分叉
deepcode --fork

# 从指定会话分叉
deepcode --fork 123e4567-e89b-12d3-a456-426614174000
```

## 非交互执行模式（--exec）

`runExecMode` 函数（`packages/cli/src/exec-runner.ts:57-153`）实现非交互模式：

1. 解析当前项目设置
2. 创建 `SessionManager` 实例（`nonInteractive: true`）
3. 初始化 MCP 服务器
4. 若指定 `--resume`/`--fork`，验证会话存在
5. 构建提示（支持 stdin 管道输入）
6. 处理分叉或恢复逻辑
7. 调用 `handleUserPrompt` 执行单次模型轮次
8. 输出助手回复到 stdout

### 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 执行成功 |
| 1 | 执行失败（会话不存在、权限确认、需要用户输入、其他错误） |
| 130 | 被 SIGINT 中断 |

非交互模式遇到以下情况会失败退出：
- 会话状态为 `ask_permission`（需要权限确认）
- 会话状态为 `waiting_for_user`（需要用户输入）
- 会话状态不是 `completed`

## 交互式 TUI

### 启动流程

`cli.tsx` 的 `main()` 函数（`packages/cli/src/cli.tsx:16-167`）执行以下步骤：

1. 获取包信息并解析命令行参数
2. 处理 `--version`/`--help`（提前退出）
3. 配置 Windows shell 环境（设置 `NoDefaultCurrentDirectoryInExePath`，解析 Git Bash 路径）
4. 解析 `--last`/`--fork` 为具体会话 ID
5. 若 `--exec` 则运行非交互模式并退出
6. 检查 stdin 是否为 TTY（非 TTY 环境报错退出）
7. 验证 `--resume`/`--fork` 指定的会话 ID 是否存在
8. 检查 npm 更新
9. 使用 Ink 的 `render()` 挂载 `AppContainer` 组件

TUI 渲染配置（`cli.tsx:137-147`）：

```typescript
const inkInstance = render(
  <AppContainer
    projectRoot={projectRoot}
    version={packageInfo?.version ?? CLI_VERSION}
    initialPrompt={appInitialPrompt}
    resumeSessionId={appResumeSessionId}
    forkSessionId={typeof appForkSessionId === "string" ? appForkSessionId : undefined}
    onRestart={() => restartRef.current?.()}
  />,
  { exitOnCtrlC: false }
);
```

### TUI 快捷键

| 快捷键 | 功能 |
|--------|------|
| Enter | 发送提示 |
| Shift+Enter | 插入换行 |
| Shift+Tab | 切换 Plan Mode |
| Home/End | 行首/行尾移动 |
| Alt+Left/Right | 按单词移动 |
| Ctrl+W | 删除前一个单词 |
| Ctrl+V | 从剪贴板粘贴图片 |
| Ctrl+X | 清除已粘贴图片 |
| Esc | 中断当前模型轮次 |
| `/` | 打开技能/命令菜单 |
| Ctrl+D 两次 | 退出 |

### Windows 特殊处理

`configureWindowsShell()` 函数（`cli.tsx:175-184`）：

- 设置 `NoDefaultCurrentDirectoryInExePath=1`，防止 Windows 在当前目录查找可执行文件
- 调用 `setShellIfWindows()` 解析 Git Bash 路径
- 在无 Git Bash 的 Windows 机器上，此步骤会报错并以退出码 1 终止
- 该步骤在 `--version`/`--help` 处理之后执行，确保帮助信息在任何环境下可用

## 斜杠命令

在 TUI 中输入 `/` 打开命令菜单。EPILOG（`cli-args.ts:53-77`）中列出的斜杠命令：

| 命令 | 功能 |
|------|------|
| `/skills` | 列出可用技能 |
| `/model` | 选择模型、思考模式和推理力度 |
| `/plan` | 切换输入到 Plan Mode |
| `/new` | 开始新对话 |
| `/init` | 初始化 AGENTS.md 文件（包含 LLM 指令） |
| `/resume` | 选择之前的对话继续 |
| `/fork` | 分叉当前对话 |
| `/continue` | 继续当前对话，或在为空时恢复一个 |
| `/undo` | 将代码和/或对话恢复到之前的点 |
| `/mcp` | 显示 MCP 服务器状态和可用工具 |
| `/raw` | 切换显示模式（查看/折叠推理内容） |
| `/exit` | 退出 |

## 会话管理

### 会话状态

`SessionStatus` 类型（`packages/core/src/session.ts:211-219`）定义 8 种状态：

```typescript
export type SessionStatus =
  | "failed"
  | "pending"
  | "processing"
  | "waiting_for_user"
  | "completed"
  | "interrupted"
  | "ask_permission"
  | "permission_denied";
```

### 会话存储

会话索引存储路径（`cli.tsx:39`）：

```
~/.deepcode/projects/<projectCode>/sessions-index.json
```

`projectCode` 由 `getProjectCode()` 函数（`session.ts:98-114`）生成：

- 若路径转换后的长度 <= 64 字符，直接使用路径替换（`/` → `-`，`:` → 空）
- 若超过 64 字符，使用目录名前缀 + `-` + SHA-256 哈希前 16 字符
- Windows 平台路径在哈希前转小写

最大会话条目数 `MAX_SESSION_ENTRIES = 50`（`session.ts:72`）。

### 会话恢复

`--resume <sessionId>` 恢复指定会话：

1. 读取 `sessions-index.json`
2. 验证会话 ID 存在于条目列表
3. 若不存在，输出错误并退出
4. 进入 TUI 时将会话 ID 传递给 `AppContainer`

`--last`（`-l`）自动选择 `updateTime` 最新的会话条目。

### 会话分叉

`--fork <sessionId>` 从已有会话创建分叉：

- 分叉的新会话记录 `forkedFrom: { sessionId, messageId }`
- 不带值的裸 `--fork` 自动选择最近会话
- 分叉与恢复互斥（不能同时使用 `--fork` 和 `--resume`）

### 会话 ID 格式

会话 ID 使用 UUID v4 格式，验证正则（`cli-args.ts:13`）：

```typescript
const SESSION_ID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
```

### SessionManager 类

`SessionManager`（`session.ts:367`）是会话管理的核心类，内部持有：

- `activeSessionId: string | null`：当前活跃会话
- `activePromptController: AbortController | null`：当前提示的中断控制器
- `mcpManager = new McpManager()`：MCP 服务器管理器实例
- `toolExecutor: ToolExecutor`：工具执行器
- `messageConverter: OpenAIMessageConverter`：消息格式转换器

## 配置文件路径

| 配置类型 | 用户级 | 项目级 |
|---------|--------|--------|
| 设置文件 | `~/.deepcode/settings.json` | `<projectRoot>/.deepcode/settings.json` |
| 原生技能 | `~/.deepcode/skills/*/SKILL.md` | `./.deepcode/skills/*/SKILL.md` |
| 互操作技能 | `~/.agents/skills/*/SKILL.md` | `./.agents/skills/*/SKILL.md` |
| 会话数据 | `~/.deepcode/projects/<code>/sessions-index.json` | — |

## 相关概念

- [项目简介](/concepts/00-introduction.md)
- [三包 monorepo 架构](/concepts/01-architecture.md)
- [权限系统](/concepts/02-permission-system.md)
- [MCP 集成](/concepts/03-mcp-integration.md)
