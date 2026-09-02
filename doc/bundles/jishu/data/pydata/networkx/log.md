# NetworkX Bundle 变更日志

## 2026-09-02 — 初始版本（基于 2020 年前后简书连载教程）

- 基于简书连载《matplotlib & pillow & networkx 手册(停止维护)》中 3 篇 NetworkX 文章生成
- 覆盖 3 个概念文档 + 2 个示例文档 + 3 个信源登记文档
- 全部内容引用编号事实（spec:jianshu-blogs-to-okf-wiki 的 facts.md，F-106~F-197），无 facts 之外的事实
- 信源：source-01（节点与边，F-192~F-197）、source-02（画出简单路径，F-114~F-119）、source-03（画神经网络，F-106~F-113）
- 过时 API 处理：文档标注「本文基于 2020 年前后教程」（对应 networkx 2.x 时代），对 `node_color` 整数序列着色、`nx.draw` 渲染依赖等给出「现状」说明
- 本批次文档 `stale_after` 设为 2026-12-31（旧教程时效性保守节点）
