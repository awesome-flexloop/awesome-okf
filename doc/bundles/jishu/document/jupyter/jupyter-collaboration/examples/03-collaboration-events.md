---
type: Example
title: 监听协作事件和扩展开发
description: 监听协作用户事件、房间事件、fork事件，构建协作扩展和审计功能
tags: [events, extension, audit, listeners, jupyter-events]
concepts: [/concepts/06-awareness-protocol.md, /concepts/08-fork-timeline.md, /concepts/03-document-room.md]
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# 监听协作事件和扩展开发

## 后端事件系统

jupyter-collaboration 使用 Jupyter Events 框架发射协作事件。扩展可以监听这些事件实现审计、通知、分析等功能。

### 事件Schema URI

| 事件类型 | Schema URI | 触发时机 |
|---|---|---|
| Session | `https://schema.jupyter.org/jupyter_collaboration/session/v1` | 文档会话创建/清理 |
| Room | `https://schema.jupyter.org/jupyter_collaboration/room/v1` | 文档房间生命周期 |
| Awareness | `https://schema.jupyter.org/jupyter_collaboration/awareness/v1` | 用户加入/离开 |
| Fork | `https://schema.jupyter.org/jupyter_collaboration/fork/v1` | Fork创建/删除 |
| Document | `https://schema.jupyter.org/jupyter_collaboration/document/v1` | 文档保存/共享/overwrite |
| Load | `https://schema.jupyter.org/jupyter_collaboration/load/v1` | 文档加载/外带变更 |
| File | `https://schema.jupyter.org/jupyter_collaboration/file/v1` | 文件重命名 |

Schema文件位于 `jupyter_server_ydoc/events/` 目录。

### 事件监听器示例

```python
from jupyter_events import EventLogger
from jupyter_server.extension.application import ExtensionApp

class AuditExtension(ExtensionApp):
    name = "collaboration-audit"
    
    def initialize_settings(self):
        # 获取EventLogger
        event_logger = self.settings["event_logger"]
        
        # 监听所有协作事件
        event_logger.add_listener(
            self._on_collab_event,
            schema_id_starts_with="https://schema.jupyter.org/jupyter_collaboration"
        )
    
    def _on_collab_event(self, logger, schema_id, data):
        if "session" in schema_id:
            self._on_session_event(schema_id, data)
        elif "awareness" in schema_id:
            self._on_awareness_event(schema_id, data)
        elif "room" in schema_id:
            self._on_room_event(schema_id, data)
    
    def _on_awareness_event(self, schema_id, data):
        """用户加入/离开事件"""
        username = data["username"]
        action = data["action"]  # "join" or "leave"
        room_id = data["roomid"]
        
        if action == "join":
            self.log.info(f"👤 {username} joined document {room_id}")
            # 发送通知、更新在线用户列表等
        elif action == "leave":
            self.log.info(f"👋 {username} left document {room_id}")
    
    def _on_session_event(self, schema_id, data):
        """会话事件"""
        room_id = data["room_id"]
        action = data["action"]  # 各种action
        self.log.info(f"📄 Session event: {action} on {room_id}")
```

### 注册为Server Extension

```python
def _load_jupyter_server_extension(serverapp):
    event_logger = serverapp.config.EventLogger.instance(parent=serverapp)
    listener = AuditListener()
    event_logger.add_listener(listener.handle_event)
```

### 在事件中记录额外信息

如果你自己的server extension需要发射协作相关事件，可以复用jupyter-collaboration的schema或创建自定义schema：

```python
from jupyter_server_ydoc.handlers import (
    JUPYTER_COLLABORATION_AWARENESS_EVENTS_URI,
)

# 发射自定义事件
self.event_logger.emit(
    schema_id=JUPYTER_COLLABORATION_AWARENESS_EVENTS_URI,
    data={
        "roomid": room_id,
        "username": username,
        "action": "custom_action"  # 必须匹配schema定义
    }
)
```

### 事件数据字段

以Awareness事件为例（定义在 `events/awareness.yaml`）：

```yaml
properties:
  roomid:
    type: string
    description: "The room ID that triggered the event"
  username:
    type: string
    description: "The username"
  action:
    type: string
    enum: ["join", "leave"]
```

## 前端事件系统

前端使用 Lumino Signal 和 Jupyter Event 系统传播协作状态变化。

### 监听Provider事件

```typescript
import { IDocumentProviderFactory, WebSocketProvider } from '@jupyter/docprovider';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-collab-plugin',
  requires: [IDocumentProviderFactory],
  activate: (app, providerFactory) => {
    // ... 获取provider引用后
    
    // 监听连接状态变化
    provider.onConnectionStatusChanged((status) => {
      switch (status) {
        case 'connected':
          console.log('协作连接已建立');
          break;
        case 'disconnected':
          console.log('协作连接已断开');
          break;
      }
    });
  }
};
```

### 监听Awareness变化

```typescript
import { Awareness } from 'y-protocols/awareness';

function trackCollaborators(awareness: Awareness) {
  awareness.on('change', (changes: { added: number[], updated: number[], removed: number[] }) => {
    // 新用户加入
    for (const clientId of changes.added) {
      const state = awareness.getStates().get(clientId);
      if (state?.user) {
        console.log(`User ${state.user.name} joined`);
        sendNotification(`👤 ${state.user.name} 开始编辑`);
      }
    }
    
    // 用户离开
    for (const clientId of changes.removed) {
      console.log(`Client ${clientId} left`);
    }
    
    // 更新在线用户数
    const userCount = awareness.getStates().size;
    updateUserCountUI(userCount);
  });
}
```

### 监听Fork事件

```typescript
import { IForkManagerToken } from '@jupyter/docprovider';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-fork-tracker',
  requires: [IForkManagerToken],
  activate: (app, forkManager) => {
    forkManager.forkAdded.connect((_, emission) => {
      console.log('New fork created:', emission.fork_roomid);
      console.log('  Root:', emission.fork_info.root_roomid);
      console.log('  By:', emission.username);
    });
    
    forkManager.forkDeleted.connect((_, emission) => {
      console.log('Fork deleted:', emission.fork_roomid);
    });
  }
};
```

### 监听文件变更/保存

```typescript
// 通过RtcContentProvider的信号
rtcContentProvider.fileChanged.connect((_, change) => {
  if (change.type === 'save') {
    console.log('文档已保存到服务器');
    // 例如：触发自动提交到git
  } else if (change.type === 'rename') {
    console.log(`文件重命名: ${change.oldValue.path} → ${change.newValue.path}`);
  }
});
```

## 实用扩展示例

### 示例1：协作活动日志

```python
import json
from datetime import datetime

class CollaborationLogger:
    """记录所有协作活动到JSONL文件"""
    
    def __init__(self, log_path="/var/log/jupyter_collab.log"):
        self.log_path = log_path
    
    def __call__(self, logger, schema_id, data):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "schema": schema_id,
            "data": data
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

# 注册
event_logger.add_listener(CollaborationLogger())
```

### 示例2：用户在线时长统计

```python
from collections import defaultdict
from datetime import datetime

class OnlineTimeTracker:
    def __init__(self):
        self.join_times = {}  # (room_id, username) -> datetime
        self.total_times = defaultdict(float)  # username -> total seconds
    
    def __call__(self, logger, schema_id, data):
        if "awareness" not in schema_id:
            return
        
        key = (data["roomid"], data["username"])
        now = datetime.utcnow()
        
        if data["action"] == "join":
            self.join_times[key] = now
        elif data["action"] == "leave" and key in self.join_times:
            duration = (now - self.join_times.pop(key)).total_seconds()
            self.total_times[data["username"]] += duration
```

### 示例3：前端协作者通知

```typescript
// 监听awareness变化显示桌面通知
function setupDesktopNotifications(awareness: Awareness) {
  // 请求通知权限
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
  
  const seenUsers = new Set<number>();
  
  awareness.on('change', ({ added, removed }) => {
    if (Notification.permission !== 'granted') return;
    
    for (const clientId of added) {
      if (seenUsers.has(clientId)) continue;
      seenUsers.add(clientId);
      
      const state = awareness.getStates().get(clientId);
      if (state?.user && state.user.name) {
        new Notification('协作者加入', {
          body: `${state.user.name} 开始编辑文档`,
          icon: state.user.avatar_url,
        });
      }
    }
    
    for (const clientId of removed) {
      seenUsers.delete(clientId);
    }
  });
}
```

### 示例4：文档自动版本快照

```python
class AutoSnapshotListener:
    """文档保存后自动创建git提交"""
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
    
    def __call__(self, logger, schema_id, data):
        if "document" not in schema_id or data.get("action") != "saved":
            return
        
        room_id = data.get("roomid")
        # 从room_id解析文件路径
        # 自动git commit...
```

## 扩展开发注意事项

1. **事件处理要快**：事件监听器同步执行，耗时操作应该放到后台任务
2. **错误隔离**：监听器中的异常不应该影响主流程
3. **Schema验证**：自定义事件数据必须符合schema定义
4. **信号清理**：前端Signal连接需要在组件dispose时断开
5. **权限控制**：监听事件时注意用户权限，避免泄露信息
6. **日志级别**：生产环境避免过度日志记录
7. **Schema版本**：事件schema可能随版本变化，注意向后兼容
