---
type: Example
title: 基本协作使用
description: 从零开始安装配置jupyterlab-webrtc-docprovider，创建第一个P2P协作文档会话
tags: [basic, collaboration, getting-started, tutorial, peer-to-peer]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README.md - Usage guide
  - id: getting-started
    resource: /concepts/01-getting-started.md
    title: 安装与快速开始
---

## 基本协作使用教程

本示例演示如何使用 jupyterlab-webrtc-docprovider 创建一个多人实时协作的 JupyterLab 会话。

## 前置条件

- Python >= 3.7
- JupyterLab >= 3.1
- 现代浏览器（Chrome/Firefox/Edge/Safari，支持 WebRTC）

## 步骤1：安装扩展

```bash
pip install jupyterlab-webrtc-docprovider
```

验证安装：

```bash
jupyter labextension list
```

确认输出中包含 `@jupyterlite/webrtc-docprovider` 且状态为 enabled。

## 步骤2：启用协作模式

创建 Jupyter Server 配置文件（如果不存在）：

```bash
jupyter server --generate-config
```

编辑配置文件，启用协作：

```python
# jupyter_server_config.py
c.LabServerApp.collaborative = True
```

或者直接使用命令行参数启动：

```bash
jupyter lab --collaborative
```

## 步骤3：创建共享房间

启动 JupyterLab 后，在浏览器中访问：

```
http://localhost:8888/lab?room=my-first-collab
```

其中 `my-first-collab` 是房间名，可以自定义。

### 可选：指定用户名和颜色

```
http://localhost:8888/lab?room=my-first-collab&username=Alice&usercolor=4caf50
```

- `username=Alice`：你在协作中显示的名字
- `usercolor=4caf50`：你的光标颜色（绿色，hex 格式，不含 #）

## 步骤4：邀请协作者

将相同的 URL 分享给其他人：

```
http://your-server:8888/lab?room=my-first-collab&username=Bob&usercolor=e65100
```

> **注意**：协作者需要能访问到你的 Jupyter Server（或使用同一个 JupyterHub 部署）。WebRTC 连接建立后，文档数据通过 P2P 直接传输，不经过服务器。

如果是在同一台机器上测试，可以打开两个浏览器窗口（或普通窗口+无痕窗口），使用相同的 room 参数。

## 步骤5：开始协作

1. 在 JupyterLab 中创建一个新的 Notebook（或打开现有 Notebook）
2. 在另一个浏览器窗口/标签页中打开同一个 Notebook
3. 观察右下角状态栏：
   - 显示 peer 数量（如 "1↔ share my-first-collab"）
   - 你的用户名显示在状态栏中
4. 在一个窗口中输入内容，另一个窗口应实时看到更改
5. 不同用户的光标会以不同颜色显示，并附带用户名标签

## 步骤6：控制共享

### 通过命令面板切换

1. 按 `Ctrl+Shift+C`（Mac: `Cmd+Shift+C`）打开命令面板
2. 搜索 "Toggle WebRTC Sharing"
3. 点击命令可以启用/禁用共享

### 通过设置面板配置

1. 打开 Settings → Settings Editor
2. 选择 "WebRTC Sharing"
3. 可以配置：
   - Disable WebRTC Sharing：禁用/启用
   - Room Name：预设房间名
   - Room Prefix：房间前缀
   - Signaling URLs：信令服务器
   - User Color：光标颜色
   - User Name：用户名

## 预期结果

- 多个用户可以同时编辑同一文档
- 每个用户的光标位置实时可见
- 编辑操作实时同步，无冲突（Yjs CRDT 自动合并）
- 状态栏显示当前 peer 数量和房间名
- 同一浏览器的多个标签页通过 BroadcastChannel 自动发现

## 常见问题

**Q: 状态栏显示 "Not Sharing"？**
A: 检查是否启用了 `collaborative: true`。如果未启用，WebRTC 被强制禁用。

**Q: 看不到其他用户？**
A: 确认使用了相同的 `room` 参数，检查信令服务器是否可达（浏览器控制台查看 WebSocket 连接状态）。

**Q: 连接断开了怎么办？**
A: y-webrtc 会自动重连。刷新页面可以重新建立连接。

## 相关概念

- [安装与快速开始](../concepts/01-getting-started.md)
- [房间ID与信令机制](../concepts/05-room-and-signaling.md)
- [配置三级优先级系统](../concepts/09-configuration.md)
- [自定义信令服务器部署](custom-signaling-server.md)
