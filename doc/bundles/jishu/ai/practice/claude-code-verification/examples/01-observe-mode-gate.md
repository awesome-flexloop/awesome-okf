---
type: Example
title: "observe 模式门禁落地"
description: "commit 验证戳与 off/observe/enforce 三态门禁的可复现配方：判定条件、日志字段、误报复核与卡死兜底"
tags: [observe-mode, commit-gate, verification-stamp, false-positive, rollout]
status: stable
sources:
  - id: blog
    resource: https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/
---

# observe 模式门禁落地

> **性质**：依据博文 F-052—F-056 整理的**配方**，非实测记录。脚本为示意伪代码，需按你的 Git 工作流改写。

## 目标

给每个 commit 打「怎么验证的」戳，并让一道门禁能拦截完全没验证的会话；上线过程不影响任何人（F-052、F-053、F-054）。

## 步骤 1：定义验证戳

原文中戳的取值包含 `none`，以便直接查询未验证的 commit（F-052）。建议取值：

| 取值 | 含义 |
|---|---|
| `verify` | 会话中出现过 `verify` skill 调用且留下证据 |
| `code-review` | 会话中出现过 `/code-review` |
| `both` | 两者都有 |
| `none` | 两者都没有 |

戳可以写在 commit message 的 trailer 里，例如 `Verified-By: verify`；写入理由是 `enforce` 模式下允许在 commit message 中说明为何未验证（F-055）。

## 步骤 2：三态配置

| 模式 | gate 行为 | 观察指标 |
|---|---|---|
| `off` | 不检查，仅记录戳 | 戳的覆盖率 |
| `observe` | 记录「本会被拦下」的提交，不真的拦 | 假阳性数量与原因分布 |
| `enforce` | 真正拦截 | 被拦率、绕过理由、卡死次数 |

原文把 observe 的目的写得很明确：先看会被拦下什么，复核误报，确保没有人受影响（F-054）。

## 步骤 3：判定逻辑（示意）

```python
# 示意伪代码：不含任何仓库特定实现
def evaluate(session_events, mode, blocked_count_in_session):
    stamps = [e for e in session_events if e in ("verify", "code-review")]
    stamp = "both" if len(set(stamps)) == 2 else (stamps[0] if stamps else "none")
    would_block = stamp == "none"

    if mode == "off":
        return {"stamp": stamp, "action": "allow"}

    if mode == "observe":
        return {"stamp": stamp, "action": "allow",
                "would_block": would_block,
                "log": {"reason": "no verify or code-review in session"}}

    # enforce：被拦两次后放行一次，避免 Agent 卡死（F-056）
    if would_block and blocked_count_in_session < 2:
        return {"stamp": stamp, "action": "block",
                "hint": "在 commit message 中写明未验证的理由"}
    return {"stamp": stamp, "action": "allow", "bypassed": True}
```

第 3 分支是全文最容易被省略的一条：**同一会话内被拦两次后，下一次放行**（F-056）。理由是 Claude Code 并不完美，门禁需要有退出机制。

## 步骤 4：observe 阶段的误报复核清单

在切到 `enforce` 之前，逐条看 `would_block` 日志：

- 是否存在合法的「纯文档 / 纯配置」提交被判为无验证？
- 是否存在验证发生在会话外（CI、别的人工流程）而未留痕的情况？
- `none` 戳的写入是否完整，能否一次查询出全部未验证提交？
- 每类误报是否需要一条豁免规则，还是应该改为让证据留痕？

复核完成后再切 `enforce`，并在 commit message 中保留说明理由的通道（F-055）。

## 步骤 5：验收清单

| 检查 | 通过标准 |
|---|---|
| 戳覆盖率 | 所有新 commit 都有戳，含 `none` |
| 查询能力 | 一条命令列出全部 `none` 提交 |
| observe 无影响 | observe 期间零真实拦截 |
| 误报已归因 | 每类误报有处置结论 |
| 兜底生效 | 连续两次拦截后第三次放行 |
| 可回退 | 一键切回 `off` / `observe` |

## 与评测体系的衔接

门禁上线后不要只看「拦了多少」。按 [门禁治理](../concepts/04-gate-governance.md) 的做法，用带对照组的 eval 分层量召回率，并把 recall 调到过拟合边界就停（F-057—F-059、F-062）；同时按 [漏检规则化](../concepts/05-misses-into-rules.md) 例行修剪规则，避免验证步骤只增不减（F-069）。

## 反模式核对

- 跳过 observe 直接 enforce；
- 没有 `none` 戳，导致「未验证」不可查询；
- 没有卡死兜底，Agent 被反复拦截后停滞；
- 用拦截数量作为唯一成效指标（缺少对照组与分层召回）。
