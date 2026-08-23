---
type: Changelog
scope: nanobot
name: log
version: "0.1.0"
source: local
description: nanobot OKF 知识库变更日志。
---

# Changelog

## 2026-08-23

### 新增

- 初始创建 nanobot OKF v0.2 wiki bundle。
- **spec/facts.md**：94 条从源码提取的可验证事实（F-001 ~ F-094），覆盖项目元数据、核心依赖、包初始化、SDK 主类、CLI 入口层、消息总线、SDK 类型系统、WebUI 开发服务器、构建钩子、Docker 部署、测试基础设施、TUI、WebUI、WebSocket 通道、内存系统和架构文档。
- **spec/insights.md**：4 条架构与工程洞察：
  - 三端共享同一 Agent 核心，入口分层而非分叉
  - 启动性能通过延迟导入和快速路径分层优化
  - WebUI 构建产物嵌入 Python Wheel，前后端版本强绑定
  - 安全模型以最小权限和纵深防御为核心
- **concepts/00-introduction.md**：nanobot 简介、核心定位、Python Agent 核心与多接口概览。
- **concepts/01-architecture.md**：整体架构图、nanobot.py 主入口、MessageBus、CLI 入口分层、网关模式、关键子系统表。
- **concepts/02-agent-runtime.md**：AgentLoop、AgentRunner、LLM Provider 抽象、工具调用与自动发现、钩子系统、模型覆盖与回退、流式运行。
- **concepts/03-bus-messaging.md**：MessageBus 实现、数据流模式、WebSocket 通信协议、多聊天复用、认证与安全、可信代理模式。
- **concepts/04-sdk-types.md**：StreamEventType、RunResult、StreamEvent、SessionSnapshot、SessionInfo、延迟导出机制。
- **concepts/05-multi-interface.md**：CLI/TUI/WebUI 三端对比、入口分发、TUI 技术栈与协议、WebUI 状态机与 REST API、共享网关模型。
- **examples/01-basic-usage.md**：安装方式（脚本/uv/pip/源码）、模型配置、安装验证、WebUI/TUI/SDK 使用示例、后台网关。
- **references/source.md**：26 个关键源文件索引，按模块分类，映射到事实 ID。
- **index.md**：bundle 根索引，含功能特性、导航表、目录结构和技术栈。
- **concepts/index.md、examples/index.md、references/index.md**：各分区索引。

### 信源

- 读取 26 个源文件，包括 `pyproject.toml`、`README.md`、`AGENTS.md`、`Dockerfile`、`docker-compose.yml`、`conftest.py`、`hatch_build.py`、Python 核心模块（`__init__.py`、`__main__.py`、`nanobot.py`、`cli/`、`bus/queue.py`、`sdk/types.py`、`webui/dev.py`）、7 篇文档、TUI 源码（`package.json`、`app.ts`、`host.ts`、`protocol.ts`）和 WebUI 源码（`package.json`、`App.tsx`、`lib/api.ts`）。
- nanobot 源码版本：0.3.0（The Agency Release）。
