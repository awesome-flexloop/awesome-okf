---
type: Example
title: "Claude Code 经 MemoryProxy 零插件接入"
description: "不装插件、Hook 或 MCP，只改两个环境变量把 Claude Code 指向 proxy，完成首轮 team/agent/task 绑定并使用 mem 会话指令。"
tags: [tencentdb-agent-memory, example, claude-code, proxy, zero-plugin]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-deploy
    resource: /references/04-deploy-install.md
    title: 安装与部署信源
  - id: s-proxy-doc
    resource: /references/03-api-references.md
    title: v3 API 三卷与 OpenAPI 信源
---

# Claude Code 经 MemoryProxy 零插件接入

> 本示例基于 commit 8b86874 截面的文档与源码整理，未在真实环境运行验证；命令中的 env/端点均带（F-xxx）溯源，落地前请先实测。

## 1. 前置条件

1. 已按《一键部署最小闭环》拉起三件套，proxy 监听 `0.0.0.0:8096`（F-218/F-022）。
2. 手头有 `.admin-key` 中的 `sk-mem-` key（F-275）。
3. 理解接入形态：协议不变，把 Agent 的 base URL 指向 proxy，不需要插件、Hook 或 MCP（F-026/F-245）。

## 2. 导出两个环境变量（原样照抄）

INSTALL_CN 给出的 Claude Code 配置（F-029）：

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default
export ANTHROPIC_AUTH_TOKEN=<.admin-key 中的 sk-mem-*>
# 并配置 --model（F-029）
```

proxy 同时讲 Anthropic 兼容的 `/v1/messages` 与 OpenAI 兼容的 `/v1/chat/completions`，支持 SSE 流式（F-219）。Claude Code 走 `/claude-code/default` 前缀即由 claude-code 适配器接管（F-220）。

## 3. 首轮 sessionInit：选 team/agent/task

1. 启动 Claude Code 后，首轮会话由 sessionInit 引导：proxy 通过 AskUserQuestion 让你选择 team / agent / task（F-232）。
2. proxy 持久化该绑定，后续轮次无需重复选择（F-232）。
3. 冷启动特性：创建团队或用户时即自动生成默认 Agent，管理员也可自定义默认 Agent 模板（F-015）。

## 4. 后续每轮：记忆自动注入

绑定完成后，每轮请求由注入管线自动处理，客户端侧无感知（F-225/F-224）：

- 8 个注入器：tdai-tools、tdai-profile-memory、tdai-l1-recall、tdai-fixed-asset、skill-tools、skill、knowledge-tools、asset-reflection（F-225）。
- 6 个注入边界标记：`<tdai_recalled_l1_memories>`、`<tdai_profile_memory>`、`<l3_core_memory>`、`<l2_scene_index>`、`<tdai_memory_tools>`、`<memory-tools-guide>`（F-224）。

## 5. 鉴权链路

请求到达 proxy 后的身份链路（F-233）：

```text
x-tdai-user-key → 内核 /v3/meta/auth/verify 换取 user_id → 按用户维度控制资产可见性
```

因此同一 proxy 对不同用户呈现的资产范围不同；可见性还受 private/team/restricted/agent 四值约束（F-233/F-046）。

## 6. 会话内 mem 指令（6 个）

会话中途可直接下发 `mem:` 指令，共 6 个（F-234）：

| 指令 | 作用 | 备注 |
|------|------|------|
| `mem:create-task` | 对话内创建任务 | 重点：不必离开会话即可建档（F-234/F-014） |
| `mem:update-task` | 对话内更新任务 | 2.0.1 起支持（F-014） |
| `mem:session-reset` | 一键重置绑定（换团队/Agent/任务） | 重点：切换上下文用它，不必重启客户端（F-234/F-014） |
| `mem:sync` | 同步会话/任务状态 | F-234 |
| `mem:create-skill` | 从当前会话创建技能 | F-234 |
| `mem:help` | 查看指令帮助 | F-234 |

## 7. 适配口径、旁路与开关

1. proxy 的 agent-adapters 工厂注册 8 个适配器：claude-code、codebuddy、codex、workbuddy、dsh、opencode、pi、default（F-220）。
2. 客户端数量存在文档口径差异：README 列 7 个（不含 OpenCode），INSTALL_CN 列 8 类；OpenCode 为 2.0.1 起新增（F-027/F-028/F-013）。
3. 需要绕过记忆注入时，可走 proxy 的 `/direct/*` 旁路路由（F-221）。
4. `PROXY_FULL_STACK=1` 同时启用 auth、tdai、sessionInit 三个开关；不设置时三者各自默认关闭（F-270）。一键部署默认开启（F-264），手动起 proxy 时若首轮没有绑定引导，先检查此开关。

## 8. 失败处置

| 现象 | 依据 | 处置 |
|------|------|------|
| 首轮直接报错、无 AskUserQuestion 引导 | sessionInit 未启用（F-270/F-232） | 确认 proxy 以 `PROXY_FULL_STACK=1` 启动（F-264） |
| 401/403 鉴权失败 | user-key 经 `/v3/meta/auth/verify` 校验（F-233） | 核对 `ANTHROPIC_AUTH_TOKEN` 与 `.admin-key` 一致（F-275） |
| 想换团队或 Agent | 绑定已持久化（F-232） | 会话内执行 `mem:session-reset`（F-234/F-014） |
| 某轮不希望带记忆 | 注入每轮自动执行（F-225） | 该请求改走 `/direct/*` 旁路（F-221） |
| 换了 OpenCode 等其他客户端 | README 与 INSTALL 客户端清单口径不同（F-027/F-028） | 以 INSTALL_CN 的 8 类清单与对应适配器为准（F-220） |
| 重置后 token 失效 | `--purge` 清除 admin key（F-036） | 重新读取新 `.admin-key` 并重新 export（F-275） |

## 相关概念

- [MemoryProxy：LLM 代理](../concepts/09-memory-proxy.md)
- [网关、隔离与 API 契约](../concepts/06-gateway-isolation.md)
- [部署拓扑与脚本](../concepts/11-deploy-topology.md)
- 信源：[v3 API 三卷与 OpenAPI 信源](../references/03-api-references.md)、[安装与部署信源](../references/04-deploy-install.md)
