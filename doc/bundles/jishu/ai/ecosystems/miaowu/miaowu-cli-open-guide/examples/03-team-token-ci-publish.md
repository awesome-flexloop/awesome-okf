---
type: Example
title: 命令流三：团队 token 签发、Skill 安装与 CI 直发
description: 接入方服务端 HMAC 签发成员临时 token 的 HTTP 报文、tgz 安装 meoo skill install、MEOO_TOKEN/MEOO_API_URL 注入、whoami/projects 核验、项目操作序列与 CI --skip-build --skip-push --force 直发的完整命令流（文档级复现）
tags: [meoo, miaowu, cli, token, ci, integration, example]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
status: stable
stale_after: "2027-01-18"
sources:
  - id: cli-open-guide
    resource: https://docs.meoo.com/open/guides/cli
    title: CLI 开放集成接入
  - id: open
    resource: https://docs.meoo.com/open
    title: Meoo 开放平台
---

# 命令流三：团队 token 签发、Skill 安装与 CI 直发

> **复现性质声明**：**文档级复现，未做运行验证（2026-10-18）**。报文与命令逐字摘自 [CLI 开放集成接入](https://docs.meoo.com/open/guides/cli)；本示例不替代「团队系统集成」页的签名算法文档（未在抓取范围内）。原理见 [06 团队 Skill+CLI 集成](../concepts/06-team-skill-cli-integration.md)。

## 前置：拿到团队凭证

- 团队 AK/SK 当前**暂不支持自助创建**，需联系秒悟团队人工创建并提供团队账号；Secret 仅创建时交付一次（F-037 ⚠️ dated）；
- AK/SK 只保存在接入方可信服务端，完成请求签名，**四不入**：浏览器、移动端、代码仓库、构建产物（F-038、F-044）；
- 权限配齐：`team.member.token.issue`、`team.member.read`、委托含 `cli.compat`（F-045）；
- 运行环境 Node.js 18 或以上（F-046）。

## 阶段 1：服务端签发成员 token

在接入方服务端按 HMAC 签名协议发起（F-048，报文逐字）：

```http
POST /open/v1/team/members/{member_id}/tokens
Content-Type: application/json

{
  "scopes": ["cli.compat"],
  "expires_in": 900
}
```

- `{member_id}` 换成本次任务对应的团队成员（联调可用 Owner，业务用户用虚拟成员映射，F-044）；
- `expires_in: 900` 为示例有效期秒数（15 分钟），按任务时长设置且须落在团队凭证允许范围内（F-049）；
- 响应取 `access_token` 与 `expires_in`，服务端记录到期时间（F-048）。

## 阶段 2：在 Agent/CI 环境安装 CLI 与 Skill

安装包路径替换为实际路径（F-050，逐字）：

```bash
npm install -g "/path/to/meoo-cli.tgz"
meoo --version
meoo skill install
```

`meoo skill install` 自动检测 Claude Code、Cursor、Trae、CodeBuddy、Qoder 的配置目录（F-051）。自有 Agent 改装到实际加载目录：

```bash
meoo skill install --target /path/to/agent/skills/meoo-cli
```

该目录含 `SKILL.md` 与 `references/`，需加入 Agent 的 Skill 加载路径；升级 CLI 后重装以同步指引（F-052）。

## 阶段 3：注入环境变量

由服务端/Secret 管理/任务调度器注入 Agent 命令进程（F-053，逐字）：

```bash
export MEOO_TOKEN="<access_token>"
export MEOO_API_URL="https://meoo.com"
```

多业务用户并发时，每个任务传入**各自成员**的 token（F-058）；联调环境地址与该环境凭证成对替换（F-047）。

## 阶段 4：身份与项目核验

```bash
meoo --json whoami
meoo --json projects list
```

（F-054，逐字）`--json` 输出结构化结果供 Agent 解析。

## 阶段 5：项目操作序列

在本地应用目录中，把 `<项目 urlId>` 换成实际值（F-055，逐字）：

```bash
meoo projects use "<项目 urlId>"
meoo cloud status
meoo sandbox push
meoo deploy
```

依次为选择项目 → 查云服务状态 → 同步本地源码 → 构建发布。

## 阶段 6：CI 已构建产物直发

CI 流水线里已完成静态构建时，跳过构建与源码推送（F-056，逐字）：

```bash
meoo --json deploy --project "<项目 urlId>" --skip-build --skip-push --force
```

硬前提：**先完成构建并核对项目**；`--force` 仅用于自动化任务中替代人工确认（F-056）。

## 阶段 7：token 生命周期管理

| 阶段 | 动作（F-057） |
|---|---|
| 任务启动 | 定 member_id → 签发/复用 token → 注入执行进程 |
| 临近到期 | 同一成员重新签发；执行器更新**后续子进程**环境 |
| 身份/权限报错 | 按序排查：目标环境 → token 到期时间 → `cli.compat` → 成员状态 → 项目权限 |
| 任务完成 | 回收 token；保留任务结果与脱敏操作记录 |

## 自查清单

- [ ] AK/SK 只在服务端，未进任何客户端与仓库（F-038）
- [ ] token 按成员、按任务签发，scope 为 `cli.compat`（F-048、F-058）
- [ ] 测试/生产的地址与凭证未混用（F-041、F-047）
- [ ] CI 直发前构建产物已就绪、项目 urlId 已核对（F-056）
- [ ] 任务结束 token 已回收、日志已脱敏（F-057）
