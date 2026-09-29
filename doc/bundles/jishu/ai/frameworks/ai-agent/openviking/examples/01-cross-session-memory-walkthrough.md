---
okf_version: "0.2"
type: Example
title: "实战：VikingBot 跨会话记忆三步验证"
description: "复现博文实测：让 Agent 记住职业 → 新会话考它 → 终端检索并定位明文记忆文件，理解写记忆/召回/落盘的完整闭环"
tags: [OpenViking, VikingBot, 跨会话记忆, Memory URI, 实测]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/OFS4DzgTEcEgzNHyvRVD0g
  - id: github-readme
    url: https://github.com/volcengine/OpenViking
---

# 实战：VikingBot 跨会话记忆三步验证

> 前置：已完成 [实战 00 的 Docker 部署与双密钥配置](00-docker-server-deployment.md)，并在 Studio 工作台以用户身份（博文用户 macro）进入会话。本篇复现博文 F-025~F-028 的最小验证闭环。

## 实验设计

要证明的不是"Agent 这次记得"，而是**信息不来自当前会话历史**：

```mermaid
flowchart LR
    A["会话 1：写入一条偏好"] --> B["关闭 / 新建会话"]
    B --> C["会话 2：直接提问"]
    C --> D["终端检索 + 文件定位"]
    D --> E["确认记忆明文落盘"]
```

## 第 1 步：写记忆（会话 1）

在 Studio 工作台的 **Agent 模式**输入：

```text
记住我的职业：Java开发工程师
```

博文实测现象（F-025）：

- Agent 调用记忆写入工具（博文记录工具名为 `openviking_memory_commit`）把偏好提交进记忆
- 回复中给出一条 **Memory URI**，说明这条偏好存到了哪个 viking:// 路径

后台实际发生的事（官方机制，F-038）：

1. 当轮会话结束（Stop Hook 触发 / 手动 commit）后，服务端归档对话
2. VLM 异步抽取候选记忆
3. 与该用户既有记忆比对：create（新建）/ merge（合并）/ skip（跳过）

> ⚠️ 工具名口径：官方 2026-09 MCP 工具清单中没有 `openviking_memory_commit`，对应能力是会话 commit 机制 + `remember` 工具（主动固化）。不影响本实验观察——以实际界面显示的工具调用为准，机制说明见 [概念 02](../concepts/02-memory-lifecycle-integrations.md) 与[核验报告](../references/verification.md)。

## 第 2 步：新会话召回（会话 2）

**新建一个全新会话**（关键：上下文里没有上一轮对话），直接问：

```text
我的职业是什么？
```

博文实测现象（F-026）：

- Agent 对当前会话"毫无印象"，但先发起记忆检索（博文记录工具名为 `openviking_search`），再回答："你的职业是 Java 开发工程师"
- 这条信息**不在会话历史里**，是从 OpenViking 召回的——跨会话记忆成立

判断要点：看回答前是否有检索类工具调用；若直接凭上下文答对，说明会话没切干净，实验无效。

## 第 3 步：终端检索与明文定位

切到工作台的**终端模式**，执行博文所用的斜杠命令（F-027）：

```text
/search 职业
```

博文实测返回：

- 命中的资源、记忆、技能列表
- 每条结果带文件名：`.abstract.md`、`.overview.md`、`profile.md`
- 带 L0/L1/L2 层级标注与相似度 score

然后在左侧上下文树手动展开同一路径（F-028）：

```text
user/macro/peers/macro/memories/profile.md
```

预览该文件，内容是明文的"职业：Java开发工程师"。

## 这三步验证了什么

| 验证点 | 观察证据 | 对应机制 |
|--------|---------|---------|
| 偏好被写入 | Memory URI | 会话 commit → VLM 抽取 → create/merge/skip（F-038） |
| 跨会话可召回 | 新会话先检索再答对 | 自动召回 + search/find（F-009/F-026） |
| 结果可解释 | 带 L0/L1/L2、score、文件路径 | 三层加载 + 目录递归检索（F-006/F-008） |
| 记忆可审计 | profile.md 明文预览 | 记忆即文件（F-028），非黑盒向量 |

## 自己扩展实验

1. **改记忆**：再说"我的职业换成 Go 开发工程师"，新会话提问，观察是 merge 还是新建（可在 profile.md 看落地结果）
2. **资源检索**：用 `ov add-resource <一个文档 URL>` 导入资料，处理完成后 `/search` 相关问题，对比命中的 .abstract.md 与原文
3. **多 Agent 共享验证**：按[实战 02](02-agent-integration-mcp-cli.md) 把 Claude Code 接到同一服务器，在 Claude Code 会话里问"我的职业"，应能召回 VikingBot 写入的同一条记忆（F-010）
4. **清理**：官方 MCP 提供 `forget` 工具清理冗余/过时记忆（F-039）

## 注意

- 记忆抽取是**异步**的：刚结束会话立刻新开会话提问，若抽取尚未完成可能召回不到，稍等再试
- `/search` 是 VikingBot 终端内的斜杠命令（博文单源记录）；在外部终端用 ov CLI 的等价命令是 `ov find "职业"`（F-047）
- 明文记忆意味着部署侧要保护挂载卷（博文挂载在宿主机 `/mydata/openviking`）
