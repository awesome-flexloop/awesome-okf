---
type: Example
title: "OpenCode 状态与回放阅读实验"
description: "通过固定源码和夹具核验确认点，不执行网络请求、更新或安装"
source: "../spec/facts-deepening-2.0.32.md"
tags: [opencode, reading-lab, persistence, replay]
status: draft
sources:
  - id: source
    resource: ../references/source-deepening-2.0.32.md
    title: 同快照深化信源
---

# OpenCode 状态与回放阅读实验

这是静态源码导读，不是可运行脚本，也不要求安装OpenCode依赖。先读[状态篇](../concepts/13-product-state-persistence.md)、[回放篇](../concepts/14-simulation-record-replay.md)和[更新篇](../concepts/15-cloud-update-boundaries.md)，再按[F-136～F-151](../spec/facts-deepening-2.0.32.md)的固定链接完成下列核验。不要运行record模式或真实更新。

## 练习一：哪里已经“保存”

对照TUI storage update与Desktop StorageUpdate handler：

```text
TUI：lock → load → mutation → writeJsonAtomic → setStore
Desktop：renderer cache → RPC → state.update → revision
                                      → 延迟SQLite writer
```

轨迹来自F-136、F-139、F-140，是阅读标记，不是实际运行日志。请找出原子写和transaction的位置，再回答：

| 问题 | 源码应支持的判断 |
|---|---|
| TUI setStore是否早于本次原子写？ | 该update路径中晚于写成功。 |
| Desktop revision是否证明transaction完成？ | 不证明；返回后还有write-behind。 |
| 某层flush resolve是否总能证明写成功？ | 不能通用化；需看allSettled、错误报告及重试队列。 |
| App late hydration怎样避免覆盖修改？ | 未touched时才应用异步初始值；仍需单独读写入路径。 |

核验通过的标准是能指出具体调用顺序与失败分支，不是仅复述“最终一致”之类标签。

## 练习二：回放为什么没有消耗那条记录

打开固定`http/multi-step.json`，它包含step=1/2与first/second。再读HTTP测试“a mismatch does not consume an interaction”与“distinct requests replay in any order”，最后看`makeReplayPoolState`的claim。（F-144～F-146）

| 输入情境 | 需要定位的证据 |
|---|---|
| step=3不匹配 | 匹配失败不能先标used；测试随后仍可请求step=2。 |
| step=2先于step=1 | 不同请求由未领取pool匹配，不要求全局顺序固定。 |
| 并发请求 | claim由SynchronizedRef更新，不能重复领取同条记录。 |
| CI且缺cassette | auto仍选replay；请求失败不自动变成record。 |

不要把这些判断称为本轮测试通过；它们来自测试定义与实现对照。也不要把HTTP记录当作终端JSONL时间线，二者记录不同对象。

## 练习三：更新ready之后还有什么

打开GUI updater main/machine/platform及machine测试片段，定位packaged/non-dev启用条件、stage、ready、install与restart handoff。测试用假platform，并不触发真实安装。（F-150）

再读TUI notification的apply与exit，指出两个实现各自的确认含义。（F-151）

- Desktop ready：暂存的更新可供后续安装，不是已安装。
- TUI installed：该source.apply已resolve；底层安装器未在本轮穷尽。
- Desktop handoff timeout：重启开始未获得确认时有失败路径，不是按计时器宣告安装成功。

## 证据等级自检

阅读后给每个结论标上“实现静态核验”“测试断言存在”或“本轮实际运行”。本实验只提供前两类；本轮实际运行记录属于文档门禁与构建，不能替代OpenCode运行验证。Console鉴权计费、Stats core、Drive UI与真实云部署仍在未读/未运行边界内。

## 相关概念

- [新增事实与固定源码](../spec/facts-deepening-2.0.32.md)
- [六主题信源范围](../references/source-deepening-2.0.32.md)
- [本轮学习地图](../spec/insights-deepening-2.0.32.md)
