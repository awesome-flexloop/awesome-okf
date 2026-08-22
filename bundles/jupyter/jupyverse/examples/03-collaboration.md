---
type: Example
title: "实时协作编辑"
description: "启用 Yjs 协作模式，让多个用户同时编辑同一个 Notebook，实时同步内容和光标位置。"
tags: [collaboration, yjs, multi-user, realtime, crdt]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: yjs
    resource: /concepts/09-collaboration-yjs.md
    title: 协作编辑 Yjs
---

# 实时协作编辑

本示例演示如何启用 Jupyverse 的实时协作功能。

## 安装协作插件

```bash
pip install "jupyverse[jupyterlab,noauth,collaboration]"
```

`collaboration` extra 安装 Yjs 协作模块、pycrdt 库、文件 ID 服务和 SQLite 文档存储。

## 启动协作模式

```bash
jupyverse --set "frontend.collaborative=true"
```

关键配置项 `frontend.collaborative=true` 启用：
- PageConfig 中 `collaborative: true`
- Yjs WebSocket 端点
- 多用户光标和选区显示
- CRDT 文档同步

默认监听 `127.0.0.1:8000`。

## 验证协作功能

### 1. 打开两个浏览器窗口

- 窗口1：访问 `http://127.0.0.1:8000/lab`
- 窗口2：访问 `http://127.0.0.1:8000/lab`（或使用不同浏览器/隐身模式模拟不同用户）

### 2. 创建/打开同一个 Notebook

在窗口1中创建 `shared.ipynb`，窗口2中也打开 `shared.ipynb`。

### 3. 观察实时同步

- 在窗口1中输入代码，窗口2应实时看到
- 每个用户显示不同颜色的光标
- 用户名称显示在其他用户的光标旁

## 协作 + Token 认证

生产环境协作部署应使用认证：

```bash
pip install "jupyverse[jupyterlab,auth,collaboration]"
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --host 0.0.0.0 \
  --set "auth.token=my-secret-token" \
  --set "frontend.collaborative=true"
```

每个用户使用 token 连接，Awareness 信息显示认证后的用户名。

## 局域网协作

```bash
jupyverse --host 0.0.0.0 --set "frontend.collaborative=true"
```

其他用户通过 `http://<your-ip>:8000/lab` 访问，即可共同编辑。

## 协作 REST API 示例

```bash
# 获取/创建协作会话
curl -X POST "http://127.0.0.1:8000/api/collaboration/session/shared.ipynb"

# 返回
# {"format": "json", "fileId": "uuid", "sessionId": "uuid"}
```

## 注意事项

- 协作功能需要安装 `collaboration` extra（含 fps-yjs、fps-yrooms、fps-ystore-sqlite、fps-file-id）
- SQLite 文档存储（fps-ystore-sqlite）自动持久化文档更新，无需额外配置
- 默认情况下所有用户关闭文档后协作房间仍然保留（直到服务器重启）
