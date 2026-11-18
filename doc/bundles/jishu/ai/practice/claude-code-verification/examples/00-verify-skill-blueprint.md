---
type: Example
title: "搭建 verify skill 与 feature map"
description: "按原文做法整理的可复现配方：目录结构、SKILL.md 骨架、feature map 模板、提交前强制与验收清单"
tags: [verify-skill, smoke-test, feature-map, cdp, checklist]
status: stable
sources:
  - id: blog
    resource: https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/
---

# 搭建 `verify` skill 与 feature map

> **性质**：依据博文（F-018、F-019、F-034—F-038）与官方文档整理的**配方**，非实测记录。命令与路径需按你的项目改写。

## 目标与验收

| 项 | 目标 | 验收方式 |
|---|---|---|
| 单一入口 | 一条命令启动应用并跑通一条真实用户流 | 执行命令后退出码为 0 且产出截图/日志证据 |
| 提交前强制 | Agent 在 commit 前调用该 skill | 用 hook 或 `/goal` 检查会话中出现调用记录 |
| 快速可靠 | 冒烟流程短、无随机失败 | 连续多次运行，结果稳定 |
| 完成条件可读 | feature map 覆盖主流程的路径、选择器、预期结果 | 人工逐条核对 |

## 步骤 1：确定宿主入口

按改动类型从原文的四种入口里选一种（F-034）：Web 用 Claude Chrome 扩展，移动端用 iOS/Android MCP，桌面用 computer use，后端直接在本地起服务。E2E 场景再通过 CDP、模拟器或 API harness 驱动（F-018）。

## 步骤 2：目录与 skill 骨架

原文要求把 skill 放在 `.claude/skills/` 下，**尽量靠近相关代码**，需要几个就建几个（F-035）：

```text
your-repo/
├── .claude/
│   └── skills/
│       └── verify/
│           ├── SKILL.md          # 启动与冒烟步骤
│           └── feature-map.md    # 用户视角的功能清单
└── src/
```

`SKILL.md` 骨架（示意，按项目替换）：

```markdown
---
name: verify
description: 启动本地应用并按 feature map 跑一条端到端冒烟流程；
             在提交改动前必须使用，输出截图与命令返回值作为证据。
---

# verify

1. 启动：`<你的启动命令>`，等待健康检查通过。
2. 驱动：按 `feature-map.md` 的 P0 流程逐步操作。
3. 取证：每步记录实际命令、退出码与结果截图。
4. 判定：全部 P0 通过才输出 PASS；任一失败即输出 FAIL 与具体环节。
5. 收尾：关闭进程，不留下后台服务。
```

第 3 步对应 [验证循环四要素](../concepts/00-verification-loops.md) 的「交出证据」——要求证据而非「已通过」的断言。

## 步骤 3：feature map 模板

feature map 从用户视角列功能，同时充当向导与评分 rubric（F-019）：

| 编号 | 用户动作 | 路径/入口 | 选择器或快捷键 | 预期结果 | 优先级 |
|---|---|---|---|---|---|
| P0-1 | 打开首页 | `/` | `#app` 可见 | 首屏渲染完成、无控制台错误 | P0 |
| P0-2 | 加入购物车 | `/items/1` | `[data-test=add-to-cart]` | 购物车计数变为 1 | P0 |
| P0-3 | 结账 | `/cart` | `[data-test=checkout]` | 跳转确认页并展示订单号 | P0 |
| P1-1 | 返回修改 | 浏览器返回 | — | 保留已填表单 | P1 |

把 P0 流程作为 done 判据；P1 供扩展，不阻塞提交。

## 步骤 4：让调用成为硬约束

原文说 Claude 知道在提交前使用 `verify` skill（F-036），团队则用 hook 或 `/goal` 强制便宜检查先行（F-051）。两种方式：

- **Stop hook**：官方文档的 `Stop` 事件在 Claude 完成响应时触发，可跑确定性脚本检查本轮是否留下验证证据。
- **`/goal`**：设置「测试通过且 lint 干净」一类的完成条件，官方语义是每轮结束后由独立模型判定（见 [E-2](../references/verification.md) 的评估器边界）。

## 步骤 5：把 skill 自己也纳入验证

原文要求持续投资让 `verify` skill 快且可靠，让 Claude 迭代并压测它（F-037）。建议的复核清单：

- 启动脚本在无缓存、端口被占、依赖缺失三种情况下是否给出明确失败信息；
- 连续多次运行是否结果稳定（无 flaky，见 F-010）；
- 单轮耗时是否短到可以放进提交前高频循环（见 F-011）；
- feature map 是否随功能变更同步更新（对应 [规则清理](../concepts/05-misses-into-rules.md)）。

## 反模式核对

- 只跑单测就宣称「已验证」（F-017）；
- 让同一个 Agent 既写代码又独自判定通过（与 F-005 的独立 grader 相悖）；
- skill 写好后长期不维护，feature map 与实际界面漂移；
- 冒烟流程太重，被 Agent 自动跳过（F-011、F-012）。
