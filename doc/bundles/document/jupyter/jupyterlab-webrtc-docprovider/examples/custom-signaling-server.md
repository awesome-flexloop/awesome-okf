---
type: Example
title: 自定义信令服务器部署
description: 部署私有y-webrtc信令服务器并配置jupyterlab-webrtc-docprovider使用，适用于生产环境
tags: [signaling-server, deployment, production, y-webrtc, websocket, security]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config
    resource: /concepts/09-configuration.md
    title: 配置三级优先级系统
  - id: signaling
    resource: /concepts/05-room-and-signaling.md
    title: 房间ID与信令机制
---

## 自定义信令服务器部署

默认的公共信令服务器（yjs.dev、Heroku EU/US）仅适合开发测试。生产环境应部署私有信令服务器。

## 背景：信令服务器的作用

信令服务器仅协助 WebRTC 连接建立：
1. 帮助同一房间的 peer 互相发现
2. 转发 SDP offer/answer（连接协商数据）
3. 转发 ICE candidates（网络路径候选）
4. **不传输文档内容**（数据通过 WebRTC DataChannel P2P 传输）

## 步骤1：部署信令服务器

### 使用 y-webrtc 内置服务器

y-webrtc 提供了一个简单的信令服务器实现：

```bash
# 安装
npm install y-webrtc

# 或使用内置的 bin/server.js
npx y-webrtc-server
```

默认监听端口 4444。

### 简单的 Node.js 信令服务器

```javascript
// signaling-server.js
const WebSocket = require('ws');
const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('y-webrtc signaling server\n');
});

const wss = new WebSocket.Server({ server });
const rooms = new Map();

wss.on('connection', (ws) => {
  let roomName = null;

  ws.on('message', (message) => {
    const data = JSON.parse(message);

    if (data.type === 'subscribe') {
      roomName = data.room;
      if (!rooms.has(roomName)) {
        rooms.set(roomName, new Set());
      }
      rooms.get(roomName).add(ws);
      // 通知现有 peer 有新成员
      broadcastToRoom(roomName, { type: 'peer-join' }, ws);
    }

    if (data.type === 'unsubscribe' && roomName) {
      removeFromRoom(roomName, ws);
    }

    // 转发信令消息给同一房间的其他 peer
    if (roomName) {
      broadcastToRoom(roomName, data, ws);
    }
  });

  ws.on('close', () => {
    if (roomName) {
      removeFromRoom(roomName, ws);
    }
  });
});

function broadcastToRoom(roomName, message, exclude = null) {
  const room = rooms.get(roomName);
  if (!room) return;
  const msg = JSON.stringify(message);
  room.forEach((client) => {
    if (client !== exclude && client.readyState === WebSocket.OPEN) {
      client.send(msg);
    }
  });
}

function removeFromRoom(roomName, ws) {
  const room = rooms.get(roomName);
  if (room) {
    room.delete(ws);
    if (room.size === 0) rooms.delete(roomName);
    broadcastToRoom(roomName, { type: 'peer-leave' }, ws);
  }
}

const PORT = process.env.PORT || 4444;
server.listen(PORT, () => {
  console.log(`Signaling server running on ws://0.0.0.0:${PORT}`);
});
```

运行：

```bash
npm install ws
node signaling-server.js
```

### 使用 HTTPS/WSS（生产环境必需）

WebRTC 在安全上下文之外可能受限。生产环境使用反向代理（nginx/Caddy）添加 TLS：

```nginx
# nginx 配置示例
server {
    listen 443 ssl;
    server_name signaling.your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:4444;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 步骤2：配置 JupyterLab 使用私有信令服务器

### 方式A：overrides.json（系统级）

```json
{
  "@jupyterlite/webrtc-docprovider:plugin": {
    "signalingUrls": ["wss://signaling.your-domain.com"],
    "roomPrefix": "your-org-unique-prefix-2024"
  }
}
```

放置路径：`{sys.prefix}/share/jupyter/lab/settings/overrides.json`

### 方式B：Jupyter Server 页面配置

在 Jupyter Server 配置中注入信令服务器 URL：

```python
# jupyter_server_config.py
c.LabServerApp.app_settings = {
    'fullWebRtcSignalingUrls': ['wss://signaling.your-domain.com'],
    'webRtcRoomPrefix': 'your-org-unique-prefix-2024',
    'collaborative': True,
}
```

### 方式C：JupyterLite 配置

```json
// jupyter-lite.json
{
  "jupyter-config-data": {
    "collaborative": true,
    "fullWebRtcSignalingUrls": ["wss://signaling.your-domain.com"],
    "webRtcRoomPrefix": "your-org-unique-prefix-2024"
  }
}
```

### 方式D：用户设置面板

Settings → Settings Editor → WebRTC Sharing → Signaling URLs

## 步骤3：配置多个信令服务器（推荐）

配置多个信令服务器提供冗余：

```json
{
  "@jupyterlite/webrtc-docprovider:plugin": {
    "signalingUrls": [
      "wss://signaling1.your-domain.com",
      "wss://signaling2.your-domain.com"
    ]
  }
}
```

客户端会连接到所有列出的信令服务器，通过任意一个发现 peer 即可建立连接。

## 步骤4：验证

1. 启动 JupyterLab：`jupyter lab --collaborative`
2. 打开浏览器开发者工具 → Network 标签 → WS 过滤
3. 确认 WebSocket 连接到你的私有信令服务器（而非公共服务器）
4. 控制台不应出现 "Using default public WebRTC signaling servers" 警告
5. 使用相同 room 参数在两个窗口中测试协作

## 安全建议

1. **使用 WSS（WebSocket Secure）**：生产环境始终使用 TLS 加密
2. **设置唯一 roomPrefix**：防止与其他部署的房间冲突
3. **信令服务器不存储数据**：信令服务器应无状态，不记录消息内容
4. **考虑身份验证**：如需控制访问，可在反向代理层添加认证
5. **定期更新**：关注 y-webrtc 更新，及时升级信令服务器

## 相关概念

- [房间ID与信令机制](../concepts/05-room-and-signaling.md)
- [配置三级优先级系统](../concepts/09-configuration.md)
- [基本协作使用](basic-collaboration.md)
- [JupyterLite集成配置](jupyterlite-integration.md)
