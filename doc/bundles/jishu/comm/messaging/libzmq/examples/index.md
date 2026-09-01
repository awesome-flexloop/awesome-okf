# 示例代码

* [PUSH/PULL 流水线模式](push-pull-pipeline.md) — 任务分发器+多工作者+结果收集器，演示负载均衡与公平队列
* [PUB/SUB 主题订阅与过滤](pub-sub-filtering.md) — 天气发布订阅，演示前缀匹配、trie/mtrie 双端过滤
* [ROUTER/DEALER 异步请求-回复](router-dealer-async.md) — 异步服务端+worker+客户端，演示 identity 路由
* [inproc 线程间零拷贝通信](inproc-zero-copy.md) — 多线程 inproc，演示 msg_t 引用计数零拷贝传递

```{toctree}
:hidden:
:maxdepth: 7

inproc-zero-copy
pub-sub-filtering
push-pull-pipeline
router-dealer-async
```
