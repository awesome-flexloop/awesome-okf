---
type: Example
title: 使用Fork和时间线
description: 通过REST API和前端接口创建文档分叉、浏览历史版本、恢复误删内容的完整操作流程
tags: [fork, timeline, undo, version-history, api]
concepts: [/concepts/08-fork-timeline.md, /concepts/05-websocket-protocol.md]
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# 使用 Fork 和时间线

## Fork 使用示例

### 创建实验性Fork

通过REST API创建文档分叉：

```bash
# 获取session信息
curl -X PUT "http://localhost:8888/api/collaboration/session/notebooks/test.ipynb" \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"format": "json", "type": "notebook"}'

# 响应：
# {"format": "json", "type": "notebook", "fileId": "abc123", "sessionId": "uuid-xxx"}

# 创建Fork（不与主文档同步）
curl -X PUT "http://localhost:8888/api/collaboration/fork/json:notebook:abc123" \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "synchronize": false,
    "title": "实验性分析重构",
    "description": "尝试用不同的数据处理方式"
  }'

# 响应：
# {"forkRoomId": "fork-uuid-456", "roomId": "json:notebook:abc123"}
```

### 创建同步Fork

synchronize=true时，主文档的更改会实时同步到fork：

```bash
curl -X PUT "http://localhost:8888/api/collaboration/fork/json:notebook:abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "synchronize": true,
    "title": "基于最新内容的实验"
  }'
```

### 连接到Fork房间编辑

前端通过 `WebSocketProvider.connectToForkDoc()` 连接到fork：

```typescript
const provider = new WebSocketProvider({
  url: wsUrl,
  format: 'json',
  contentType: 'notebook',
  path: 'notebooks/test.ipynb',
  model: sharedModel,
  awareness: sharedModel.awareness,
});

// 连接到fork进行编辑
await provider.connectToForkDoc('fork-uuid-456', sessionId);

// 在fork中自由编辑...
// 编辑内容不会影响主文档
```

### 删除Fork并合并

满意fork中的更改后，删除并合并到主文档：

```bash
# merge=true：将fork内容合并到主文档
curl -X DELETE "http://localhost:8888/api/collaboration/fork/fork-uuid-456?merge=true" \
  -H "Authorization: Token <your-token>"
```

### 删除Fork不合并

放弃fork中的更改：

```bash
curl -X DELETE "http://localhost:8888/api/collaboration/fork/fork-uuid-456?merge=false"
```

### 查询文档的所有Fork

```bash
curl "http://localhost:8888/api/collaboration/fork/json:notebook:abc123" \
  -H "Authorization: Token <your-token>"

# 响应：
# {
#   "fork-uuid-456": {
#     "root_roomid": "json:notebook:abc123",
#     "synchronize": false,
#     "title": "实验性分析重构",
#     "description": "尝试用不同的数据处理方式"
#   }
# }
```

## 时间线使用示例

### 获取文档时间线

```bash
curl "http://localhost:8888/api/collaboration/timeline/notebooks/test.ipynb?format=json&type=notebook" \
  -H "Authorization: Token <your-token>"

# 响应：
# {
#   "roomId": "json:notebook:abc123",
#   "timestamps": [1713600000, 1713600100, 1713600200, ...],
#   "forkRoom": "timeline-fork-uuid-789",
#   "sessionId": "server-session-uuid"
# }
```

`timestamps` 是每个可撤销操作的时间点（Unix时间戳）。

### 通过时间线导航历史

前端连接到时间线fork房间，然后通过Undo/Redo浏览历史：

```typescript
// 1. 获取时间线
const timeline = await fetchTimeline('notebooks/test.ipynb', 'json', 'notebook');
// { timestamps: [t1, t2, t3, ...], forkRoom: "timeline-fork-789", ... }

// 2. 连接到时间线fork
await provider.connectToForkDoc(timeline.forkRoom, timeline.sessionId);

// 3. 导航到特定时间点
// 当前状态是最新版本
// timestamps数组长度 = 可撤销操作总数
// undo N步回到第(N)个时间点之前
async function goToTimestamp(targetIndex: number) {
  const currentSteps = getCurrentUndoSteps(); // 需要自己追踪
  const targetSteps = timeline.timestamps.length - targetIndex;
  
  if (targetSteps > currentSteps) {
    // 需要redo
    await redo(targetSteps - currentSteps);
  } else if (targetSteps < currentSteps) {
    // 需要undo
    await undo(currentSteps - targetSteps);
  }
}
```

### 通过REST API执行Undo/Redo

```bash
# Undo 3步
curl -X PUT "http://localhost:8888/api/collaboration/undoredo/json:notebook:abc123?action=undo&steps=3&forkRoom=timeline-fork-789" \
  -H "Authorization: Token <your-token>"

# 响应：{"status": "undone"}

# Redo 1步
curl -X PUT "http://localhost:8888/api/collaboration/undoredo/json:notebook:abc123?action=redo&steps=1&forkRoom=timeline-fork-789" \
  -H "Authorization: Token <your-token>"

# 响应：{"status": "redone"}
```

### 恢复到历史版本

```bash
# 1. 先通过undo导航到目标版本
curl -X PUT ".../undoredo/json:notebook:abc123?action=undo&steps=5&forkRoom=timeline-fork-789"

# 2. 确认内容后执行restore
curl -X PUT ".../undoredo/json:notebook:abc123?action=restore&forkRoom=timeline-fork-789" \
  -H "Authorization: Token <your-token>"

# 响应：{"code": 200, "status": "Document restored successfully"}
```

## Python客户端示例

```python
import requests
import websocket
import json

class CollabClient:
    """简单的jupyter-collaboration REST客户端"""
    
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Authorization": f"Token {token}"}
    
    def create_session(self, path, format, content_type):
        """创建或获取文档会话"""
        url = f"{self.base_url}/api/collaboration/session/{path}"
        resp = requests.put(url, headers=self.headers, json={
            "format": format, "type": content_type
        })
        resp.raise_for_status()
        return resp.json()
    
    def create_fork(self, room_id, synchronize=False, title="", description=""):
        """创建文档分叉"""
        url = f"{self.base_url}/api/collaboration/fork/{room_id}"
        resp = requests.put(url, headers=self.headers, json={
            "synchronize": synchronize,
            "title": title,
            "description": description
        })
        resp.raise_for_status()
        return resp.json()
    
    def delete_fork(self, fork_id, merge=False):
        """删除fork（可选合并）"""
        url = f"{self.base_url}/api/collaboration/fork/{fork_id}?merge={'true' if merge else 'false'}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()
    
    def get_timeline(self, path, format, content_type):
        """获取文档时间线"""
        url = f"{self.base_url}/api/collaboration/timeline/{path}"
        resp = requests.get(url, headers=self.headers, params={
            "format": format, "type": content_type
        })
        resp.raise_for_status()
        return resp.json()
    
    def undo_redo(self, room_id, fork_room, action, steps=1):
        """执行undo/redo/restore"""
        url = f"{self.base_url}/api/collaboration/undoredo/{room_id}"
        resp = requests.put(url, headers=self.headers, params={
            "action": action, "steps": steps, "forkRoom": fork_room
        })
        resp.raise_for_status()
        return resp.json()


# 使用示例
if __name__ == "__main__":
    client = CollabClient("http://localhost:8888", "your-token-here")
    
    # 创建会话
    session = client.create_session("notebooks/test.ipynb", "json", "notebook")
    room_id = f"json:notebook:{session['fileId']}"
    print(f"Room: {room_id}")
    
    # 创建实验fork
    fork = client.create_fork(room_id, synchronize=True, title="实验分支")
    print(f"Fork room: {fork['forkRoomId']}")
    
    # 获取时间线
    timeline = client.get_timeline("notebooks/test.ipynb", "json", "notebook")
    print(f"时间点数量: {len(timeline['timestamps'])}")
    
    # 如果有历史，尝试undo一步查看
    if timeline['timestamps']:
        result = client.undo_redo(room_id, timeline['forkRoom'], "undo", 1)
        print(f"Undo result: {result}")
```

## 前端TypeScript示例

```typescript
class ForkManager {
  /**创建实验性fork并切换到fork编辑模式*/
  async experimentWithFork(
    provider: WebSocketProvider,
    path: string,
    format: string,
    type: string,
    title: string
  ): Promise<string> {
    // 1. 先获取session
    const session = await this.getSession(path, format, type);
    const roomId = `${format}:${type}:${session.fileId}`;
    
    // 2. 创建fork（同步主文档更新）
    const fork = await this.createFork(roomId, true, title);
    
    // 3. 连接到fork编辑
    await provider.connectToForkDoc(fork.forkRoomId, session.sessionId);
    
    return fork.forkRoomId;
  }
  
  /**将fork结果合并回主文档*/
  async mergeFork(forkId: string): Promise<void> {
    await fetch(`/api/collaboration/fork/${forkId}?merge=true`, {
      method: 'DELETE',
    });
  }
  
  /**放弃fork*/
  async discardFork(forkId: string): Promise<void> {
    await fetch(`/api/collaboration/fork/${forkId}?merge=false`, {
      method: 'DELETE',
    });
  }
}
```

## 典型使用场景流程

### 场景1：恢复误删的内容

```
1. 用户误删了重要代码块
2. 点击时间线按钮 → GET /timeline 获取历史
3. 拖动滑块浏览历史版本
4. 找到删除前的版本
5. 点击"恢复" → undo + restore
6. 内容恢复到主文档
```

### 场景2：实验新功能

```
1. 用户想尝试大规模重构
2. 创建synchronize=true的fork
3. 在fork中自由编辑
4. 其他用户继续在主文档工作，更新实时同步到fork
5. 满意后删除fork(merge=true) → 更改合并到主文档
6. 不满意则删除fork(merge=false) → 丢弃更改
```

### 场景3：代码审查

```
1. 开发者完成一组更改后创建fork
2. 审查者连接到fork房间查看更改
3. 在fork中讨论、提出修改建议
4. 通过后merge到主文档
```

## 注意事项

1. **Fork内存开销**：每个fork在服务器内存中维护独立的YDoc，大量fork会增加内存使用
2. **同步模式单向**：synchronize=true只同步主→fork，fork的更改不影响主文档直到merge
3. **时间线依赖YStore**：必须配置YStore持久化才能使用时间线功能
4. **临时Fork清理**：时间线操作创建的临时fork在restore后需要清理
5. **Undo/Redo栈有限**：Yjs UndoManager的栈大小有限制，过旧的历史可能无法导航
6. **CRDT合并特性**：merge时使用CRDT自动合并，如果主文档和fork同时修改同一位置可能产生需要人工解决的冲突
