---
type: Example
title: "组建专家团队：主持人与成员编排"
description: "用内置专家模板准备两名以上成员，通过 /api/teams 创建 kind=team 的主持人，理解主持人仅有的 5 个工具、45 秒空闲收尾与 IM 通道投递行为。"
tags: [octop, team, expert, host, orchestration, im]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: teams
    resource: /concepts/10-agent-teams.md
    title: 专家团队
  - id: cli
    resource: /concepts/06-cli-commands.md
    title: CLI 命令体系
---

# 组建专家团队：主持人与成员编排

本示例演示创建一个「专家团队」：团队本身是一个 `kind="team"` 的特殊 Agent（主持人），成员是至少 2 个普通专家 Agent。主持人只负责调度，专业工作异步派给成员。

## 场景与前置条件

- 实例内已有 **至少 2 个**可用的普通专家（自己的或分享给自己的，F-217）
- 团队不可嵌套：成员只能是 `kind=expert`；团队第一版不支持共享（F-210）
- 成员必须处于 running 才能被派工，主持人不会自动拉起停用成员

### 用内置专家模板准备成员

内置专家库共 18 个 manifest，可直接当模板的 id 例如 `ops-engineer`（运维）、`news-trend`（热点资讯）、`stock-assistant`（股票助手）——id 需逐字使用（F-246）。

```bash
octop agent from-expert --template ops-engineer --name "运维工程师"
octop agent from-expert --template news-trend  --name "热点观察员"
octop agent start <agent-id-of-ops>
octop agent start <agent-id-of-news>
```

记录返回的两个 agent_id，下一步作为 `member_ids`。

## 1. 创建团队

团队规格（F-215、F-210）：`kind="team"`、`template_name="team-host"`、`member_ids` 至少 2 个（`TEAM_MIN_MEMBERS = 2`），服务端在创建时把模板 `team-host` 的工作区种子写入主持人目录，并把编制写入主持人工作区 `.octop/manifest.json`。

### HTTP（推荐，v1.0.2b5 的正式路径）

```bash
curl -X POST http://127.0.0.1:8088/api/teams \
  -H "Authorization: Bearer <jwt-token>" -H "Content-Type: application/json" \
  -d '{
    "name": "运维播报小队",
    "description": "故障研判结合当日热点",
    "default_model": "openai/gpt-4o",
    "color": "#6366F1",
    "icon_name": "users",
    "welcome_message": "把现象告诉我，我来分工。",
    "member_ids": ["<agent-id-ops>", "<agent-id-news>"]
  }'
```

`POST /api/teams` 的请求体字段（TeamCreateBody）：`name`（必填）、`description`、`default_model`、`color`、`icon_name`、`icon_url`、`welcome_message`、`member_ids`、`config`。服务端据此构造的 `AgentCreateSpec` 固定 `kind="team"`、`template_name="team-host"`、`mcp_servers=[]`、`icon_name` 缺省 `"users"`。底层创建规格共 22 个字段（含 `is_shared`、`skill_package_ids`、`knowledge_base_ids` 等，但团队创建路径不接受这些字段）。

### 命令行方式说明

v1.0.2b5 的 CLI 共 22 个命令，其中没有 team 子命令；`octop agent create` 也没有 `--kind`/`--member-ids` 选项。因此命令行环境直接用 curl 完成创建（如上），创建后用 CLI 查看：

```bash
octop agent list          # 团队主持人作为普通 agent 行出现
```

## 2. 查询与改编制

```bash
# 当前用户的团队（含成员摘要）
curl http://127.0.0.1:8088/api/teams -H "Authorization: Bearer <jwt-token>"

# PATCH 改名/模型/欢迎语/成员；成员变更后服务自动 reload 主持人
curl -X PATCH http://127.0.0.1:8088/api/teams/<team_id> \
  -H "Authorization: Bearer <jwt-token>" -H "Content-Type: application/json" \
  -d '{"member_ids": ["<agent-id-ops>", "<agent-id-news>", "<agent-id-stock>"]}'
```

## 3. 主持人的行为预期

创建后主持人被剥权为「只调度」形态（F-216、F-222）：

- 仅保留 5 个工具（`HOST_TOOLS_ALLOWED`）：`agent_list`、`ask_agent`、`memory_search`、`memory_get`、`current_time`；内置工具目录中其余工具全部进入 `tools_disabled`（含通常不可关的文件系统与 task）
- 不挂文件系统、浏览器、Web 搜索、MCP、技能包、插件、知识库、cron、mobile（F-273）
- `peer_invoke_mode="async"`，`team_peers` 即成员列表；主持人一轮可并行派多人，成员气泡直接上团队房间时间线
- **45 秒空闲收尾**：主持人等待成员回叫的轮询间隔 0.05s，空闲等待上限 `_HOST_IDLE_WAIT_SEC = 45.0` 秒（F-219），到点后主持人总结并判断是否收工
- 成员在自己侧只看到一条标题为「来自团队 {name}」的派生会话（session_key 前缀 `team:`），仍可被单独聊天，也可加入多个团队

## 4. 团队回复投递到 IM 通道

通道只绑主持人（决策 #19）。绑定时主持人通道被强制为 `response_mode="stream"`（群聊场景还会结合 QQ 的 c2c 配置），避免 invoke 模式折叠掉派工叙述（F-334）。IM 侧看不到团队房间 WebSocket，投递节奏为（F-273 文档行为）：

1. 派工成功后立即推一条「已请 {成员} 处理，请稍候…」
2. 成员收口后推一条带说话人姓名的完整消息
3. 主持人最终总结以「【主持人总结】…」补推

## 排错

| 现象 / 报错 | 原因与处理 |
|-------------|-----------|
| `TEAM_MEMBERS_TOO_FEW`（details.min_members=2） | `member_ids` 可用成员少于 2；团队不含主持人计数，先 `octop agent from-expert` 补齐（F-217） |
| `TEAM_MEMBER_INVALID` | 成员 id 不存在、不可见（非自己且未分享给自己），或传了团队 id；成员只能是普通专家（F-217） |
| `TEAM_NOT_SHAREABLE`（"teams cannot be shared"） | 团队不能 `is_shared`；TeamCreateBody 也没有该字段，勿走通用 `/api/agents` 造团队 |
| 主持人调用浏览器/文件工具被拒 | 预期行为：主持人仅 5 个工具，这些调用要由成员完成；若给主持人强行加工具也会在装配时被剥除（F-222） |
| 派工失败、提示对方未运行 | 成员 `last_state` 非 running 时 harness 调用失败，主持人走失败回叫且不自动启动；先 `octop agent start <member>`（F-273） |
| 在途派工时移不掉成员 | 有在途 job 的成员不能移出、该专家不能删除；等成员收口（重启后内存 job 锁消失）后再 PATCH（F-223） |
| 创建后找不到 CLI 命令 | v1.0.2b5 CLI 无 team 命令，使用 `/api/teams` 六个端点（GET/POST 列表与创建、GET/PATCH/DELETE 单项） |

## 相关概念

- [/concepts/10-agent-teams.md](../concepts/10-agent-teams.md)
- [/concepts/06-cli-commands.md](../concepts/06-cli-commands.md)
