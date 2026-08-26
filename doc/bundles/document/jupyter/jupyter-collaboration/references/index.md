# References 索引

源码信源登记文档，按模块组织。

## 后端源码（jupyter-server-ydoc）

- [app-source.md](app-source.md) — YDocExtension入口，配置与路由注册
- [handlers-source.md](handlers-source.md) — WebSocket/REST处理器，通信协议实现
- [rooms-source.md](rooms-source.md) — DocumentRoom/TransientRoom文档房间管理
- [stores-source.md](stores-source.md) — SQLiteYStore/TempFileYStore CRDT持久化
- [loaders-source.md](loaders-source.md) — FileLoader/FileLoaderMapping文件I/O与外带变更检测
- [websocketserver-source.md](websocketserver-source.md) — JupyterWebsocketServer连接管理与消息转发
- [tokens-source.md](tokens-source.md) — Lumino Token依赖注入定义

## 前端源码（@jupyter/docprovider）

- [yprovider-source.md](yprovider-source.md) — WebSocketProvider前端同步提供者

## 信源清单

| 信源ID | 文件 | 核心类/函数 |
|---|---|---|
| app-py | app.py | YDocExtension |
| handlers-py | handlers.py | YDocWebSocketHandler, DocSessionHandler, DocForkHandler, TimelineHandler, UndoRedoHandler |
| rooms-py | rooms.py | DocumentRoom, TransientRoom |
| stores-py | stores.py | SQLiteYStore, TempFileYStore, BaseYStore |
| loaders-py | loaders.py | FileLoader, FileLoaderMapping, OutOfBandChanges |
| wsserver-py | websocketserver.py | JupyterWebsocketServer |
| tokens-ts | tokens.ts | IDocumentProviderFactory, IAwarenessProviderFactory, IForkManagerToken |
| yprovider-ts | yprovider.ts | WebSocketProvider, RtcContentProvider, SharedModelFactory |

```{toctree}
:maxdepth: 7

app-source
handlers-source
loaders-source
rooms-source
stores-source
tokens-source
websocketserver-source
yprovider-source
```
