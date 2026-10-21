---
type: Concept
title: "清理命令的安全契约：批量删除必须先证明你有范围"
description: "vk kb prune 必须带 --pattern 或 --older-than、默认 dry-run 的 JSON 载荷与 --yes 执行路径、prunePageSize=100 分页、vk jobs prune 裸调用被拒与本地账本语义、kb delete 保留交互提示"
tags: [vibeknow, cli, prune, 安全, dry-run, 知识库]
generated:
  by: trae-seven-concepts
  at: "2026-10-21T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T00:00:00+08:00"
status: stable
stale_after: "2027-04-21"
sources:
  - id: vksrc
    resource: https://github.com/vibeknow/cli
    title: "VibeKnow CLI 源码仓库 v0.9.2 @ 93a26eca"
  - id: flags
    resource: /references/flag-inventory.md
    title: "VibeKnow CLI 旗标清单"
---

# 清理命令的安全契约：批量删除必须先证明你有范围

> **事实编号**：F-081~F-085（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


CLI 里有两类「删东西」的命令：删知识库（`vk kb prune` / `vk kb delete`）与清理本地账本（`vk jobs prune`）。两者的共同点是**把「删掉一切」这个默认结果变成需要显式声明的意图**。

## vk kb prune：必须带筛选条件

```bash
vk kb prune --pattern "vibeknow-cli-*"        # 按名字匹配
vk kb prune --older-than 7d                    # 按创建时间
vk kb prune --pattern "tmp-*" --yes            # 真正执行
```

`--pattern` 与 `--older-than` **至少要给一个**。两个都不给直接报校验失败（退出码 2）。源码注释直说这是为了拒绝「删掉一切」。

筛选条件在联网之前就被检查：glob 语法用 `filepath.Match` 预检，坏 glob 退出 2，不浪费一次 HTTP 往返；`--older-than` 的时长字符串同样先解析。

分页尺寸常量 `prunePageSize = 100`，源码注明是后端上限、内部细节、不对外暴露。扫描时每页向 stderr 打一行进度。

## 默认 dry-run

不传 `--yes` 时走 dry-run 路径：

| 输出格式 | 载荷 |
|---|---|
| `json` | `dry_run: true`、`matched` 计数、`items` 列表（每项含 `id`、`name`、`created_at`、`status: "would_delete"`） |
| 文本 | 匹配计数 + 每行一条 `id  name  created_at` + 一行 dry-run 提示 |

加上 `--yes` 才进入执行路径：逐个删除，删除成功 `status: "deleted"`，失败 `status: "failed"`。JSON 载荷此时为 `dry_run: false`、`matched`、`deleted`、`failed` 与 `items`。

**404 算成功。** 后端回报知识库已不存在时，CLI 计入 `deleted` 并标注「already gone」——重跑一次 prune 不应该把幂等结果当成失败。

## 退出码分三档

| 情形 | 退出码 |
|---|---|
| 全部成功 | 0 |
| 部分失败 | 7 |
| 全部失败 | 5 |

与 `vk video export` 的退出码 7 同义：7 = 部分成功。5 = 请求本身没问题但事情没做成。

## vk jobs prune：裸调用被拒

```bash
vk jobs prune --terminal     # 只丢已成功或已失败的运行
vk jobs prune --older-than 30d
vk jobs prune --all
```

`--older-than`、`--terminal`、`--all` 三个旗标至少要有一个，否则报校验失败。错误信息直接说明意图：「拒绝默认把整个账本都清掉」。提示给出替代方案：`vk jobs prune --terminal` 丢掉已结束的运行、保留仍在进行中的。

**`vk jobs prune` 只动本地账本，从不碰后端。** 命令的 Long 描述写明：修剪一条运行记录不会取消它、不会删除 work、不会退还额度——**它只是忘掉了指向它的指针**。

这与账本的定位一致：账本是建议性的，缺失不等于不存在。

## 位置参数一律拒绝

两条 prune 命令都声明 `Args: cobra.NoArgs`。源码注释说明原因：cobra 默认接受并静默丢弃位置参数，那样一个多余的参数看起来就像成功。

## vk kb delete 保留交互提示

单条删除保留交互确认：它是销毁性操作，但**不计费**。这一点与 `vk video export` 的授权门形成对照——一个要钱，一个只是要你的手指点一下。

## 实践建议

1. **第一次 prune 一定不加 `--yes`**，先看 JSON 里的 `items`。
2. **`--pattern` 尽量收窄**，用前缀而不是 `*`。
3. **`vk jobs prune` 用 `--terminal`**，不要随手 `--all`。
4. **看到退出码 7 就是部分成功**，逐项看 `items` 里的 `failed`。

## 相关概念

- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码 7 与 5 的语义
- [/concepts/04-run-ledger-and-async.md](/concepts/04-run-ledger-and-async.md) —— 账本语义与「缺失≠不存在」
- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— 与计费动作的授权门对照
- [/references/flag-inventory.md](/references/flag-inventory.md) —— 旗标全清单
