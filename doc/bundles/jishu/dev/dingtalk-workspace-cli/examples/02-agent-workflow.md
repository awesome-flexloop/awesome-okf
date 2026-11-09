---
okf_version: "0.2"
type: Example
title: "演练：把 dws 接入 Agent 工作流"
description: "从安装技能到稳定执行的七步闭环——Schema 渐进发现、dry-run 预演、确认门放行、jq 投影、事件订阅与 raw api 兜底"
---

# 02 · 演练：把 dws 接入 Agent 工作流

> **性质**：命令逐字取自仓库 `README.md` 的 Using with Agents、Agent Skills、Events 与 Raw API 章节（F-079 ~ F-081），**未在本机实跑**。
> 相关概念：[07 Agent 技能与事件](../concepts/07-agent-skills-and-events.md)、[06 安全、预览与审计](../concepts/06-safety-dry-run-and-audit.md)。

## 七步闭环

```text
装技能 → 发现契约 → 预演 → 确认执行 → 投影结果 → 订阅事件 → （兜底）raw api
  1        2          3        4          5          6            7
```

每一步都有对应的命令面与失败模式。跳步是最常见的错误：不读 Schema 直接拼参数，或不预演直接写。

## 步骤 1：安装技能

```bash
npx skills add DingTalk-Real-AI/dingtalk-workspace-cli -g
```

安装器会先列出**计划**——装哪些技能、写到哪些目录、同名内容如何处理——确认后才写入。`-y` 只用于自动化，且必须在用户已明确确认安装目标与覆盖行为之后使用：该路径不维护 `dws skill setup` 的所有权、备份与 mono↔multi 互斥清理状态（F-081）。

官方路径（中国网络、升级、模式切换）：

```bash
dws skill setup --mode multi --target cursor --dry-run
dws skill setup --mode multi --target cursor
dws skill setup --mode mono --target all
```

`skills/mono` 的前端标记为 `metadata.internal: true`，因此 `npx skills add` 不会默认安装它，Agent 不会在 `dws` 与产品技能之间双重路由。

## 步骤 2：渐进发现契约

不要一次导出全部 Schema 塞进上下文。按三级推进：

```bash
dws schema <domain> --compact                 # 产品域：有哪些命令族
dws schema "<domain> <action>" --compact      # 叶命令：参数、约束、风险、确认要求
dws schema --all                              # 仅工具链/CI/审计使用
```

`<domain>` 与 `<action>` 取自 `dws --help` 与 `dws <domain> --help` 的实际路径。

`--compact` 使用**正向字段白名单**，新增的 full/audit 字段不会静默撑大 Agent 上下文；`--all` 是给兼容性基线与审计用的完整导出（F-080）。

Schema 与 `--help` 的分工：

| 来源 | 回答什么 | 权威性 |
|------|---------|--------|
| `dws <path> --help` | 命令是否存在、二进制接受哪些 flag | 命令存在性与 flag 的最终依据 |
| `dws schema "<path>" --compact` | 参数约束、风险、确认要求、选择依据 | Agent 决策的规范视图 |

二者冲突时视为**契约漂移**：只传 Cobra 接受的 flag，并采用更保守的安全语义（F-080）。

## 步骤 3：预演

```bash
dws contact user search --query "engineering" --dry-run
dws calendar event list --dry-run
```

`--dry-run` 打印将要发出的请求而不产生副作用。对写操作，这是唯一能在执行前看到完整载荷的手段。

## 步骤 4：确认执行

```bash
dws todo task create --title "Review PR" --executors "<your-userId>" --yes
```

`--yes` 是 Agent 的必需开关：非交互环境无法回答确认提示，缺少它时高风险动作会被确认门拦下（F-048）。

纪律：

- `confirmation=never` 的动作不需要 `--yes`；
- `confirmation=user_required` 的动作，必须先把预演结果呈现给用户，得到明确同意后再加 `--yes`；
- 不要用 `--yes` 包住批量循环来「省事」——每一次写操作都应可追溯到一次用户授权。

## 步骤 5：投影结果

```bash
dws contact user get-self --jq '.result[0].orgEmployeeModel | {name: .orgUserName, dept: .depts[0].deptName, userId}'
dws contact user search --query "engineering" --fields userId,name --format json
```

- `--jq`：任意表达式，最省 token；
- `--fields`：只保留指定字段，结构更稳定；
- `--format json`：Agent 消费的默认格式；
- `-o <path>`：大结果落盘，上下文只留摘要。

先用小投影确认结构，再扩大范围；不要第一次就用复杂 jq 表达式猜返回结构。

## 步骤 6：订阅事件

事件是长驻进程，不是一次性查询（F-056 ~ F-060）。

```bash
dws event list                                        # 列出可用事件
dws event list --category calendar                    # 按类别过滤
dws event schema user_calendar_event_changed --flatten # 看业务字段结构
dws event consume user_calendar_event_changed \
  --calendar-ids primary \
  --change-types eventCreated,eventUpdated,eventCancelled \
  --flatten --duration 10m -f ndjson
```

常用封装：

```bash
dws event +listen-im --kind at-me -f ndjson                    # 有人 @ 我
dws event +listen-im --kind sender --user <userId> -f ndjson   # 指定发送者
dws event consume user_todo_task_create user_todo_task_update user_todo_task_delete \
  --role-types executor --flatten -f ndjson                    # 一次订阅三类待办事件
```

运维：

```bash
dws event status            # 查看本地消费者
dws event stop <subscribe_id>  # 取消订阅
```

要点：

- 默认输出保留传输信封（`type`、`event_type`、字符串 `data`、`headers`）；`--flatten` 才把业务字段提到顶层；
- `--flatten` 不能与 `-f raw` 或 `--debug-raw-events` 组合；
- 个人身份由 OAuth 令牌决定，不能用命令行身份 flag 代替；
- 事件与命令共享同一条总线，长驻进程需独立于一次性调用管理。

## 步骤 7：raw api 兜底

仅当产品命令未覆盖某个内部应用 OpenAPI 时使用（F-060）：

```bash
dws api GET /v1.0/microApp/allApps --dry-run
dws api POST /v1.0/contact/users/search --data '{"queryWord":"engineering","offset":0,"size":10}'
dws api POST /v1.0/microApp/... --page-all --page-limit 5
```

边界：

- 必须有一对完整的自有应用 Client ID/Secret（flag、环境变量或登录时保存的配置三选一，且必须成对）；
- 域名白名单仅 `api.dingtalk.com` 与 `oapi.dingtalk.com`；
- `--page-all` 默认最多 10 页，`--page-limit 0` 表示不限但硬上限 500；
- raw `api` **不进入 Agent Schema**，必须由人显式选择该逃逸通道；
- 创建、更新、删除、撤销、发送类调用先 `--dry-run`，再确认。

## Agent 标识

多 Agent 共用一台机器时，设置环境变量让审计日志可归因（F-059）：

```bash
export DWS_AGENT_PRODUCT="trae"
export DWS_AGENT_HOST="dev-laptop"
export DWS_AGENT_VER="1.0.0"
```

审计记录会带上这些标识，便于事后回答「是哪个 Agent 在什么时候发起的」。

## 反模式清单

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| 每次调用前 `dws schema --all` | 上下文被完整契约撑爆 | 按域 → 叶逐级 `--compact` |
| 所有写操作无脑加 `--yes` | 用户授权被架空 | 先预演、再确认、后执行 |
| 用 raw api 绕过产品命令 | 失去 Schema 约束与审计语义 | 优先产品命令，raw 仅兜底 |
| 用 `dws --help` 文案推断参数约束 | 文案不是契约 | 约束以 Schema 为准 |
| 把事件流当一次性命令跑 | 进程立即退出或挂死 | 用 `--duration` 或长期进程管理 |
| 只看退出码 0 就认为成功 | 空结果也可能是 0 | 读结构化返回与 `reason` |

## 一次完整调用的最小样板

```bash
# 1. 发现
dws schema "todo task create" --compact
# 2. 预演
dws todo task create --title "Review PR" --executors "<userId>" --dry-run
# 3. 执行（用户已确认）
dws todo task create --title "Review PR" --executors "<userId>" --yes --format json
# 4. 回读
dws todo task list --format json --jq '.result[] | {id, title, done}'
```

四步都留下证据：Schema 快照、预演载荷、执行返回、回读结果。审计侧再由 JSONL 哈希链补齐「谁在何时做了什么」。

返回 [示例索引](index.md) · 返回 [概念地图](../concepts/index.md)