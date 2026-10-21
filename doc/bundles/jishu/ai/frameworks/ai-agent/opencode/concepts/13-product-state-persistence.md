---
type: Concept
title: "OpenCode 三端状态与持久化确认"
description: "对照TUI原子写、App延迟保存及Desktop IPC与SQLite write-behind"
source: "../spec/facts-deepening-2.0.32.md"
tags: [opencode, tui, app, desktop, persistence]
status: draft
sources:
  - id: source
    resource: ../references/source-deepening-2.0.32.md
    title: 同快照深化信源
---

# OpenCode 三端状态与持久化确认

[产品入口篇](09-product-surfaces-and-delivery.md)说明从哪里进入，本篇继续追踪各端一条代表性持久化链。共享UI或类型不表示保存时点相同。依据[F-136～F-140](../spec/facts-deepening-2.0.32.md)，只覆盖本地状态存储，不代表全部会话同步。

## TUI：写成功后更新响应式状态

`createStorage`的update在`Flock.withLock`内重读当前文件，执行mutation、克隆结果、`writeJsonAtomic`，最后才`setStore`。原子写通过临时文件和rename完成；失败清理临时文件并抛错。（F-136）

```text
取得锁 → 重读文件 → mutation → 原子写 → setStore
```

因此这条update路径的响应式更新晚于写成功。不要只看本地旧store生成修改，否则会漏掉锁内重读的并发语义。watcher合并50ms事件后重读；读取或解析失败回initial，watch失败关闭live reload，不能把没有收到watch通知当作文件一定未变化。（F-137）

TUI `flush`等待pending并使用allSettled；`close`关watcher/timer，不自动flush。调用close不等于排队任务已保存完，flush resolve也不自动表达“所有Promise都fulfilled”。

## App：响应式修改与延迟写入分离

settings的`settings.v3`经`persisted`分流storage。`persistStore`默认100ms延迟保存；异步初始加载仅在尚未touched时hydrate，避免晚到数据覆盖已经发生的修改；dirty期间收到remote值会暂存。（F-138）

```text
本地状态修改 → dirty/延迟调度 → serialize → storage.setItem
```

该路径的`storage.setItem`没有await。读者要分别查同步与异步storage驱动，而不能由一次界面变更或调度完成推断最终写入成功。这里的late hydration保护与写入错误传播是不同问题，前者存在不代表后者得到同样保证。

## Desktop：ACK后仍有write-behind

renderer storage复用App `createNamespaceStorage`，driver连接storeItems/update/clear。namespace即时改cache，本地sequence与host revision排除过期ACK/event；失败重新排队尚未被新值替代的key。（F-139）

`StorageUpdate` RPC提交name/insert/remove，返回Number。主进程handler先`state.update`、广播其他窗口并返回revision；state writer延迟250ms执行SQLite transaction，write-behind失败保留可重试记录。（F-140）

```text
renderer cache → namespace driver → StorageUpdate
→ main state.update → 广播/返回revision
→ 延迟writer → SQLite transaction
```

RPC resolve确认主进程接受了这次状态更新，不证明最后的transaction已经完成。某层flush可在错误被报告、记录保留重试后返回；排查必须继续核对writer错误与pending记录，不能以“flush没抛异常”作通用落盘证明。

## 如何选择核验点

遇到保存问题，先辨认是哪端、哪个namespace和哪个确认点；再核对该端文件写或SQLite写入及失败处理。App persist和Desktop state测试片段已对照，TUI实现正文已读；测试定义不等于本轮已执行。

TUI session sync、App global-sync、Desktop draft及全部migration不在穷尽范围。本篇不能转述为OpenCode全部状态同步审计，也没有真实Electron E2E证据。

## 相关概念

- [产品入口与工程交付](09-product-surfaces-and-delivery.md)
- [模拟与录制回放](14-simulation-record-replay.md)
- [状态与回放阅读实验](../examples/03-state-and-replay-reading-lab.md)
