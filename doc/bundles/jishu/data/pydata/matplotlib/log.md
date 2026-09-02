# matplotlib Bundle 变更日志

## 2026-08-22 — 初始版本

- 基于 matplotlib 源码（`external/libs/python/matplotlib/lib/matplotlib/` 目录）核心模块深度阅读生成
- 覆盖 4 个概念文档 + 1 个示例文档 + 1 个信源登记文档
- 核心子系统覆盖：Artist层级体系、后端系统（渲染/交互）、pyplot状态机
- 17个源码信源编号（S-ARTIST到S-AXIS），所有类名方法名带行号溯源

## 2026-09-02 — 扩展（examples/ 增量，基于 2020 年前后简书连载教程）

- 新增 3 个示例文档：examples/event-handling.md（事件处理）、examples/patches-and-path.md（形状与路径）、examples/fractal.md（Chaos Game 分形三角形）
- 新增 3 个信源登记文档：references/source-18.md（事件处理，F-162~F-169）、source-19.md（形状与路径，F-184~F-191）、source-20.md（分形，F-101~F-105）
- 全部内容引用编号事实（spec:jianshu-blogs-to-okf-wiki 的 facts.md），无 facts 之外的事实
- 过时 API 处理：文档标注「本文基于 2020 年前后教程」，对 qt4 后端演进、逐点 scatter 性能等给出「现状」说明，未虚构当代行为
- 同步更新 examples/index.md、references/index.md、根 index.md 与学习路径
- 本批次文档 `stale_after` 设为 2026-12-31（旧教程时效性保守节点）
