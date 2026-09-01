---
type: Concept
title: "Pi AI CLI 简介"
description: "Pi 是一个多包 monorepo 形式的 AI 编码代理，包含统一 LLM API、代理运行时、TUI 库和交互式 CLI，支持 OpenAI、Anthropic、Google 等 40 家提供商。"
tags: [pi-cli, overview, monorepo, introduction]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# Pi AI CLI 简介

Pi（项目名 `pi-monorepo`）是一个自扩展的 AI 编码代理工具链，以 npm workspaces 多包 monorepo 形式组织。它提供从底层多提供商 LLM 统一 API 到上层交互式编码代理 CLI 的完整栈。

## 核心包

README 列出了三个核心包：

- **`@earendil-works/pi-coding-agent`**：交互式编码代理 CLI，是最终用户直接使用的入口。
- **`@earendil-works/pi-agent-core`**：带工具调用和状态管理的代理运行时，构建于 pi-ai 之上。
- **`@earendil-works/pi-ai`**：统一多提供商 LLM API，支持 OpenAI、Anthropic、Google、Bedrock、DeepSeek、xAI、Groq、Mistral、Moonshot、Kimi、小米等 40 个已知 provider。

此外还有两个基础库：

- **`@earendil-works/pi-telemetry`**：厂商中立的遥测契约、参考适配器与一致性测试。
- **`@earendil-works/pi-tui`**：带差分渲染的终端 UI 组件库。

根 `package.json` 声明项目为私有 ESM 包：

```json
{
  "name": "pi-monorepo",
  "private": true,
  "type": "module",
  "version": "0.0.3",
  "engines": { "node": ">=22.19.0" }
}
```

## 权限模型

Pi **不内置**文件系统、进程、网络或凭证访问的权限系统，默认以启动用户和进程的权限运行。如需更强隔离，README 文档化了三种容器化/沙箱模式：

- **Gondolin 扩展**：在主机保留 pi 和提供商认证，将内置工具和 `!` 命令路由到本地 Linux 微 VM。
- **Plain Docker**：将整个 pi 进程运行在本地容器中。
- **OpenShell**：在策略控制的沙箱中运行整个 pi 进程。

## 安装与开发环境

从源码构建需要 Node.js >= 22.19.0。开发安装必须使用 `--ignore-scripts`：

```bash
npm install --ignore-scripts   # 安装依赖但不运行生命周期脚本
npm run build                  # 构建所有 9 个包
npm run build:offline          # 使用已有模型数据离线构建
npm run check                  # biome lint + 类型检查 + 供应链检查
./test.sh                      # 运行测试（无 API key 时跳过 LLM 测试）
./pi-test.sh                   # 从源码运行 pi（可在任意目录执行）
```

`--ignore-scripts` 不是可选的安全建议，而是开发、CI 和发布的默认操作模式。直接外部依赖固定到精确版本，`.npmrc` 设置 `save-exact=true` 与 `min-release-age=2`，发布包包含 `npm-shrinkwrap.json` 固定传递依赖。

## 运行时要求

- Node.js >= 22.19.0
- TypeScript 5.9.3（开发时）
- Biome 2.3.5（代码检查与格式化）
- 支持 Kitty 键盘协议的终端可获得增强键盘体验

## 相关概念

- [Monorepo 架构](01-monorepo-architecture.md)
- [AI 包（packages/ai）](02-ai-package.md)
- [TUI 系统](03-tui-system.md)
- [内置 Prompts](04-builtin-prompts.md)
- [基础使用示例](../examples/01-basic-usage.md)
