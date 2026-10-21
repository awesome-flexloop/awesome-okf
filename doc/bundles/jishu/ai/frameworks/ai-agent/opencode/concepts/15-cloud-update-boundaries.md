---
type: Concept
title: "OpenCode 云端服务与更新边界"
description: "沿兼容代理、统计daemon、对象服务和桌面更新状态辨认失败与确认"
source: "../spec/facts-deepening-2.0.32.md"
tags: [opencode, console, stats, files, updater]
status: draft
sources:
  - id: source
    resource: ../references/source-deepening-2.0.32.md
    title: 同快照深化信源
---

# OpenCode 云端服务与更新边界

本篇从[产品交付入口](09-product-surfaces-and-delivery.md)继续读代表性服务和更新实现。对象是固定`2.0.32`源码，不能推断当前线上可用性、结算正确性或某版本更新成功。依据[F-147～F-151](../spec/facts-deepening-2.0.32.md)。

## Console：读兼容代理，不代替计费审计

Zen的responses POST直接把request交给`proxyInference`。代理执行路径映射和key归一，再调用`Resource.INFERENCE.fetch`；fetch异常返回503/no-store，上游404转换400。（F-147）

这是兼容代理链的证据。新inference服务的鉴权与计费实现未读，不能凭“请求转发了”证明额度检查、扣费或交易闭环正确。排查应先分辨错误来自proxy本身、绑定服务还是下游，而不是把所有400/503当作相同原因。

## Stats：一次full失败后的节奏

统计daemon以1小时节奏执行；UTC日首次尝试full，失败后运行incremental，并仍记录当天full已尝试。重启initialDelay依据lastSyncedAt恢复节奏。（F-148）

这意味着full失败不保证下一轮立刻再full。源码显示调度和降级路径，但Stats core的查询与写库实现未读，不能把daemon调度正常扩写为数据已完整同步或统计口径已验证。

## Files：metadata与字节不能混用

files Worker接受`/files/`的GET/HEAD/OPTIONS；缓存命中可直接返回，未从缓存返回时先head，处理条件请求和单段Range，再get。get带`etagMatches`；head/get间对象改变时返回503/no-store，防止旧metadata与新body组合。（F-149）

完整、允许缓存且不大于512MiB的响应可异步进入cache；部分响应等路径不满足同一缓存分支。512MiB是该分支条件，不是整个服务最大对象大小。这里有失败保护，不代表真实R2绑定、cache部署或所有请求组合本轮均运行验证。

## Desktop：暂存、安装与重启交接

GUI updater main仅在packaged且channel非dev时启用platform。machine把check、stage、install与restart分开，以Deferred合并并发；已有downloaded缓存时向平台传`differential:false`。平台实际设置`disableDifferentialDownload`的逻辑仅对Windows生效，macOS走另一分支，不能扩写为全平台禁用。platform设置`autoDownload=false`，下载由上层stage触发；重启交接10秒未开始会报错。（F-150）

```text
check → stage/download → ready → install → restart handoff
```

`ready`表示已暂存，不是已安装。machine测试片段定义了启动再确认persisted target、离线保留staged，以及并发install等场景；本轮只阅读，没有执行真实自动更新或Electron运行。开发构建没有启用platform也不能直接判定updater损坏。

## TUI：另一个更新确认契约

TUI的`UpdateSource`分subscribe/check/apply。available时install调用apply，resolve后设installed，reject后failed；installed时restart调用exit。自动通知的持久化历史与主动检查状态分开。（F-151）

这与Desktop的暂存缓存和restart handoff不同；不能把TUI通知当作桌面安装已完成，或把source.apply的resolve扩写为未读底层安装器的全平台结果。TUI底层安装实现没有纳入本轮深读。

## 阅读后应能回答

分别指出proxy响应转换、统计full降级、files etag保护、Desktop ready及TUI installed的具体条件。遇到未知条件回查事实链接，不从service名称猜行为。其他services、新inference鉴权计费、Stats core和真实部署更新明确留为后续研究范围。

## 相关概念

- [产品入口与工程交付](09-product-surfaces-and-delivery.md)
- [三端状态持久化](13-product-state-persistence.md)
- [模拟与录制回放](14-simulation-record-replay.md)
