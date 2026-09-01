# DeepEP API 参考

本目录包含 DeepEP 各组件的详细 API 参考文档。

## API 参考文档

| 文档 | 说明 |
|------|------|
| [公开 API](api.md) | 包导出一览、数据类型、初始化行为、工具函数 |
| [ElasticBuffer API](buffer-elastic.md) | V2 弹性缓冲区完整 API：构造、dispatch/combine、Engram、PP、AGRS |
| [Buffer (Legacy) API](buffer-legacy.md) | V1 遗留缓冲区 API：三模式 dispatch/combine、低延迟专用接口 |
| [JIT 编译系统](jit-system.md) | 运行时 CUDA 内核编译：编译器、缓存、CRTP 启动器框架 |
| [事件系统](events.md) | EventOverlap/EventHandle：计算-通信重叠、流同步、钩子机制 |

```{toctree}
:hidden:
:maxdepth: 7

api
buffer-elastic
buffer-legacy
events
jit-system
```
