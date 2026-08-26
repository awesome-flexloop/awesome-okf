# Examples

pyzmq 完整可运行示例。

| 文档 | 模式 | 说明 |
|------|------|------|
| [sync-pubsub.md](sync-pubsub.md) | 同步 PUB/SUB | Context 单例、主题订阅、Poller 超时、优雅关闭 |
| [asyncio-pushpull.md](asyncio-pushpull.md) | asyncio PUSH/PULL | zmq.asyncio.Context、await send/recv、asyncio.Poller、gather 并发 |

```{toctree}
:maxdepth: 7

asyncio-pushpull
sync-pubsub
```
