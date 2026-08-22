---
type: Reference
title: "fps-kernels 实现信源"
description: "Kernels 服务的 FPS 插件实现，提供内核生命周期管理、会话管理和 WebSocket 通道的具体实现。"
tags: [fps-kernels, implementation, kernel-lifecycle, session, websocket]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: fps_kernels_main
    resource: /external/libs/jupyter/jupyverse/plugins/kernels/src/fps_kernels/main.py
    title: fps_kernels/main.py
---

# fps-kernels 实现信源

## KernelsModule

```python
class KernelsModule(Module):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.config = KernelsConfig(**kwargs)

    async def prepare(self) -> None:
        self.put(self.config, KernelsConfig)

        app = await self.get(App)
        auth = await self.get(Auth)
        frontend_config = await self.get(FrontendConfig)
        lifespan = await self.get(Lifespan)
        yjs = await self.get(Yjs) if self.config.require_yjs else None
        default_kernel_factory = await self.get(DefaultKernelFactory)
        file_watcher = await self.get(FileWatcher)

        self.kernels = _Kernels(
            app, self.config, auth, frontend_config, yjs,
            lifespan, default_kernel_factory, file_watcher,
        )
        self.put(self.kernels, Kernels, teardown_callback=self.kernels.stop)

        async with create_task_group() as tg:
            tg.start_soon(self.kernels.start)
            self.done()
```

### 依赖注入关系

KernelsModule 在 prepare 阶段获取以下依赖：

| 依赖 | 类型 | 来源 |
|------|------|------|
| App | App | AppModule |
| Auth | Auth | auth 插件 |
| FrontendConfig | FrontendConfig | FrontendModule |
| Lifespan | Lifespan | JupyverseModule |
| Yjs | Yjs (optional) | fps-yjs 插件 |
| DefaultKernelFactory | KernelFactory | fps-kernel-subprocess |
| FileWatcher | FileWatcher | fps-file-watcher |

### 生命周期

- prepare()：创建 `_Kernels` 实例并注册，启动 `kernels.start()` 后台任务
- teardown_callback：容器关闭时调用 `kernels.stop()` 清理
