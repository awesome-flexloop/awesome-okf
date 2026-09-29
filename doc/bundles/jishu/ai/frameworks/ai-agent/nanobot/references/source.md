---
type: reference
scope: nanobot
name: source
version: "0.1.0"
source: local
description: nanobot 源码信源索引，列出关键源文件及其覆盖的事实 ID。
---

# 源码信源索引

本参考文档列出 nanobot 项目中已读取的关键源文件，以及每个文件所支撑的事实 ID。所有路径相对于 nanobot 源码根目录。

## 项目配置与构建

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `pyproject.toml` | 包元数据、依赖、构建配置、lint/typecheck 设置 | F-001 ~ F-012 |
| `hatch_build.py` | 自定义 hatch 构建钩子，自动打包 WebUI | F-005, F-050 ~ F-052 |
| `Dockerfile` | 多阶段 Docker 镜像构建 | F-053 ~ F-055, F-058 |
| `docker-compose.yml` | 三服务 Compose 编排 | F-056, F-057 |
| `conftest.py` | 跨测试套件基础设施 | F-059, F-060 |

## Python 核心

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `nanobot/__init__.py` | 包初始化、版本解析、延迟导出 | F-013 ~ F-015 |
| `nanobot/__main__.py` | `python -m nanobot` 入口 | F-016 |
| `nanobot/nanobot.py` | `Nanobot` SDK 主类，编程式门面 | F-017 ~ F-023 |
| `nanobot/bus/queue.py` | `MessageBus` 异步消息队列 | F-037 ~ F-039 |
| `nanobot/sdk/types.py` | SDK 公共值对象与事件常量 | F-040 ~ F-045 |

## CLI 层

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `nanobot/cli/entry.py` | 控制台入口，TUI 快速路径分发 | F-024 ~ F-027 |
| `nanobot/cli/agent.py` | `nanobot agent` 命令，classic/TUI 双模式 | F-028 ~ F-032 |
| `nanobot/cli/webui.py` | `nanobot webui` 命令，网关与浏览器启动 | F-033 ~ F-036 |

## WebUI 开发支持

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `nanobot/webui/dev.py` | Vite 开发服务器生命周期管理 | F-046 ~ F-049 |

## TUI（终端 UI）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `tui/package.json` | TUI 包配置与依赖 | F-061, F-062 |
| `tui/src/app.ts` | `NanobotTui` 主类，终端渲染与交互 | F-063 ~ F-065, F-071 |
| `tui/src/host.ts` | TUI Host 抽象（Standalone/Herdr） | F-069, F-070 |
| `tui/src/protocol.ts` | WebSocket 协议类型定义与客户端实现 | F-066 ~ F-068 |

## WebUI（浏览器 UI）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `webui/package.json` | WebUI 包配置与依赖 | F-072 ~ F-074 |
| `webui/src/App.tsx` | React 应用根组件，引导与状态机 | F-075 ~ F-078 |
| `webui/src/lib/api.ts` | REST API 客户端函数集合 | F-079, F-080 |

## 文档

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `docs/concepts.md` | 运行时概念、配置与工作区、架构概览 | F-085, F-089 |
| `docs/quick-start.md` | 安装与快速入门指南 | — |
| `docs/memory.md` | 内存系统设计：Consolidator 与 Dream | F-086 ~ F-088 |
| `docs/providers.md` | LLM 提供商与模型配置 | — |
| `docs/python-sdk.md` | Python SDK 使用指南与 API 参考 | — |
| `docs/websocket.md` | WebSocket 通道协议与配置 | F-081 ~ F-084 |
| `docs/deployment.md` | Docker、systemd、LaunchAgent 部署指南 | — |
| `AGENTS.md` | AI 编码代理指南，高层架构说明 | F-089 ~ F-094 |
| `CLAUDE.md` | 指向 AGENTS.md 的引用 | — |
| `README.md` | 项目简介、安装、功能概览 | — |

## 事实统计

- 总事实数：94 条（F-001 ~ F-094）
- 涉及源文件：26 个
- 编程语言：Python、TypeScript/TSX、JSON、YAML、Dockerfile、Markdown
