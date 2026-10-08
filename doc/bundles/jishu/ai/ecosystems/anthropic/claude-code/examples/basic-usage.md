---
type: example
title: "基本使用示例"
tags: [claude-code, installation, getting-started, commands, plugin]
---

# 基本使用示例

本文档展示 Claude Code 的基本安装、启动和常用操作。

## 1. 安装 Claude Code

根据你的操作系统选择对应的安装方式：

### Mac/Linux（curl 脚本）

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### Mac（Homebrew）

```bash
brew install claude-code
```

### Windows（PowerShell 脚本）

以管理员权限打开 PowerShell，执行：

```powershell
irm https://claude.ai/install.ps1 | iex
```

### Windows（WinGet）

```powershell
winget install Anthropic.ClaudeCode
```

### 验证安装

安装完成后，验证是否安装成功：

```bash
claude --version
```

## 2. 启动 Claude Code

进入你的项目目录，然后启动 Claude Code：

```bash
# 进入项目目录
cd your-project-directory

# 启动 Claude Code 交互式会话
claude
```

首次启动会自动打开浏览器要求登录 Anthropic 账号进行认证。认证成功后即可在终端中使用。

## 3. 基础对话：询问代码

启动后，你可以直接用自然语言询问关于代码库的问题：

```
> 这个项目的整体架构是什么样的？

> src/utils/ 目录下的工具函数主要做什么？

> 解释一下 auth.ts 中 authenticate 函数的逻辑
```

Claude Code 会自动索引项目文件，基于代码库上下文给出回答。

## 4. 执行任务：重构代码

你可以直接委派编码任务，Claude Code 会自主规划并执行：

```
> 重构 src/utils/format.ts 中的 formatDate 函数，把重复的日期格式化逻辑提取成辅助函数

> 为 api/users.ts 中的所有接口添加 TypeScript 类型定义

> 找出所有使用 var 声明变量的地方，改成 const 或 let
```

Claude Code 会：
1. 分析相关文件
2. 提出修改计划
3. 在关键操作前请求你的确认
4. 执行修改并汇报结果

## 5. Git 工作流：使用斜杠命令

安装 `commit-commands` 插件后（官方插件），可以使用便捷的 Git 斜杠命令：

```
> /commit
```

这会自动：
- 分析当前工作区变更
- 生成符合 Conventional Commits 规范的提交信息
- 让你确认后执行 commit

其他常用 Git 相关命令（需插件支持）：
- `/commit-push-pr`：一键完成 commit → push → 创建 PR
- `/clean_gone`：清理已合并到远端的本地分支

## 6. 安装插件示例

使用 `/plugin` 命令安装官方插件：

```
# 列出可用的官方插件
> /plugin list

# 安装代码审查插件
> /plugin install code-review

# 安装功能开发工作流插件
> /plugin install feature-dev

# 安装提交命令插件
> /plugin install commit-commands

# 查看已安装的插件
> /plugin list
```

安装完成后，对应的斜杠命令和代理就可以使用了。例如安装 code-review 后：

```
> /code-review
```

会自动启动 5 个并行的 Sonnet agents 从不同维度审查当前代码变更。

## 7. 常用斜杠命令速查

以下是 Claude Code 中常见的内置斜杠命令（注意：部分命令可能因版本不同有所差异，以 `/help` 输出为准）：

| 命令 | 用途 |
|------|------|
| `/help` | 显示帮助信息，列出所有可用命令 |
| `/bug` | 报告 Bug，自动收集环境信息 |
| `/clear` | 清空当前会话上下文 |
| `/compact` | 压缩会话历史，减少 token 占用，保留关键上下文 |
| `/cost` | 显示当前会话的 token 使用量和费用统计 |
| `/doctor` | 运行诊断检查，排查环境配置问题 |
| `/exit` 或 `/quit` | 退出 Claude Code |
| `/plugin` | 插件管理（安装/列表/更新/卸载） |

> 💡 **提示**：输入 `/` 后按 Tab 键可以自动补全可用命令。输入 `/help` 可以查看你当前安装版本的完整命令列表。

## 8. 退出 Claude Code

在交互界面中：

- 输入 `/exit` 或 `/quit` 退出
- 按 `Ctrl + C` 两次退出
- 按 `Ctrl + D` 发送 EOF 信号退出

## 相关资源

- [Claude Code 概览](../concepts/00-overview.md) — 了解核心能力和安装方式详解
- [插件体系](../concepts/01-plugin-system.md) — 深入理解插件扩展机制
- [官方插件索引](../references/plugins-index.md) — 13 个官方插件功能一览
