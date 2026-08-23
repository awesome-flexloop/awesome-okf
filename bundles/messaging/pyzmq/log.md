---
type: log
title: pyzmq 变更日志
description: 记录文档生成与更新历史
generated: true
verified: pending
status: stable
stale_after: 2027-08-23
---

# Bundle Update Log

## 2026-08-23

* **Creation**: R阶段118条事实，I阶段5洞察，E阶段8概念+4信源+2示例。

### R 阶段（事实采集）

- 产出 `spec/facts.md`，118 条编号事实（F-001~F-118），覆盖 20+ 源码文件
- 覆盖模块：顶层包、sugar（Context/Socket/Frame/Poller/Tracker/attrsettr）、_future 异步层、asyncio 集成、backend 选择与 CFFI、constants/error、decorators、auth、eventloop/green/devices/log/utils

### I 阶段（架构洞察）

- 产出 `spec/insights.md`，5 个核心洞察：
  1. 双层架构——后端 C 绑定 + sugar 纯 Python 语法层
  2. 后端可插拔——运行时选择 Cython 或 CFFI
  3. asyncio 集成通过子类覆写而非全局猴子补丁
  4. attrsettr 描述符系统统一套接字选项访问
  5. 两条异步路径——_FutureSocket 回调风格与 asyncio 原生协程
- 完成知识地图设计：8 概念 + 4 信源 + 2 示例

### E 阶段（批量生成）

- **信源文档（references/）**：
  - `constants-enums.md` — 枚举常量全量参考
  - `error-hierarchy.md` — 异常类层次与 _check_rc
  - `cffi-internals.md` — CFFI 后端内部实现
  - `attrsettr-options.md` — 选项访问三层模型
- **概念文档（concepts/）**：
  - `00-architecture-dual-backend.md` — 整体架构与双后端
  - `01-context-lifecycle.md` — Context 生命周期
  - `02-socket-sugar.md` — Socket sugar 语法层
  - `03-frame-message.md` — Frame 与消息
  - `04-poller.md` — Poller 多路复用
  - `05-async-future-asyncio.md` — 异步与 asyncio
  - `06-auth-zap.md` — 认证与 ZAP
  - `07-ecosystem-eventloop-green-devices-log.md` — 生态模块
- **示例文档（examples/）**：
  - `sync-pubsub.md` — 同步 PUB/SUB 完整示例
  - `asyncio-pushpull.md` — asyncio PUSH/PULL 管道示例
- **索引文件**：根 `index.md`、3 个子目录 `index.md`

* **Verify**: V阶段独立验证通过——结构/frontmatter/链接/API真实性/代码示例全部PASS。pyzmq验证30+类名函数名Grep命中；修复2处断链。
