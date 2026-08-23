---
okf_version: "0.2"
type: reference
title: "第六章 Ollama 可视化界面部署"
bundle: /datawhale/handy-ollama
sources:
  - https://github.com/datawhalechina/handy-ollama/blob/main/docs/C6/
tags: [chapter6, webui, fastapi, open-webui, docker, websocket]
status: stable
---

# 第六章 Ollama 可视化界面部署

## 信源定位

- **源码路径**：`docs/C6/`（2 节）+ `notebook/C6/fastapi_chat_app/`（完整应用代码）
- **在线阅读**：[第六章](https://datawhalechina.github.io/handy-ollama/#/C6/)
- **内容性质**：界面部署，自建和现成两种可视化方案

## 章节结构

| 节 | 文件 | 核心内容 |
|----|------|----------|
| 6.1 | `1. 使用 FastAPI 部署 Ollama 可视化对话界面.md` | FastAPI + WebSocket + 静态前端的流式对话应用 |
| 6.2 | `2. 使用 WebUI 部署 Ollama 可视化对话界面.md` | Open WebUI（原 ollama-webui-lite）的 Node.js 和 Docker 两种部署方式 |

## 关键事实

### FastAPI 方案

- 架构：浏览器 ↔ WebSocket ↔ FastAPI ↔ HTTP ↔ Ollama
- 技术栈：FastAPI + uvicorn + httpx + 原生 HTML/JS
- WebSocket 实现流式逐字输出效果
- 代码位于 `notebook/C6/fastapi_chat_app/`，含 app.py、websocket_handler.py、static/index.html

### Open WebUI 方案

- 仓库地址：https://github.com/ollama-webui/ollama-webui-lite
- Node.js 部署：`git clone` → `npm ci` → `npm run dev`，访问 http://localhost:3000/
- Docker 部署命令：

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

- Docker 关键参数：`--add-host=host.docker.internal:host-gateway` 让容器访问宿主机 Ollama
- 首次访问需注册账号
- 支持多用户、模型选择、对话历史

## 代码资产

- `notebook/C6/fastapi_chat_app/app.py`：FastAPI 主应用
- `notebook/C6/fastapi_chat_app/websocket_handler.py`：WebSocket 处理
- `notebook/C6/fastapi_chat_app/static/index.html`：前端页面
- `notebook/C6/fastapi_chat_app/requirements.txt`：依赖清单

## 关联概念

- [WebUI 与工具集成](../concepts/webui-tool-integration.md) — 两种部署方案的概念整理
- [生产部署实践](../concepts/production-deployment.md) — Docker Compose 编排和生产配置
- [API 与 OpenAI 兼容接口](../concepts/api-openai-compatibility.md) — 可视化界面对接的后端 API
