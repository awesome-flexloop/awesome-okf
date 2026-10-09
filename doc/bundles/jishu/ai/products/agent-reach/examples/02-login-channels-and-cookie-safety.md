---
okf_version: "0.2"
type: Example
title: "登录态渠道配置与 Cookie 安全纪律"
description: "Twitter token、OpenCLI 浏览器会话渠道配置，雪球/小宇宙/LinkedIn/Boss 一句话解锁路径，以及专用小号、服务器代理与凭据 600 安全纪律"
tags: [agent-reach, login, cookie, twitter, xiaohongshu, reddit, opencli, security]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-08T12:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
---

# 示例 02：登录态渠道配置与 Cookie 安全纪律

> 需要登录/凭据的渠道不是装完就能用，但配置方式仍是"对 Agent 说一句话 + 按引导走"。本文同时给出必须遵守的账号安全纪律——这部分比配置本身更重要。

## 1. 两档非零配置渠道

| 档位 | 渠道 | 解锁方式 |
|------|------|---------|
| 一句话解锁（5） | Twitter/X、雪球、小宇宙播客、LinkedIn、Boss直聘 | 对 Agent 说"帮我配 XXX"，引导配置（F-030） |
| 需要登录态（4） | 小红书、Reddit、Facebook、Instagram | 涉及浏览器会话或 Cookie（F-031） |

统一入口（F-046）：

```text
帮我配 Twitter
帮我配 小红书
帮我配 小宇宙
```

Agent 会依据 `agent_reach/skill/` 内的说明（SKILL.md + references/ 分类文档，F-062）引导你完成，并在配置后以 `doctor` 验证。

## 2. Twitter/X：两个环境变量

Twitter 渠道（选型链 twitter-cli ▸ OpenCLI ▸ bird，F-025）需要登录凭据，官方文档给出的环境变量为（F-068）：

```bash
export TWITTER_AUTH_TOKEN="..."     # auth_token
export TWITTER_CT0="..."            # ct0
```

Windows PowerShell：

```powershell
$env:TWITTER_AUTH_TOKEN="..."
$env:TWITTER_CT0="..."
```

能力为搜索、时间线（F-030）。token 等价于登录态，务必使用专用小号获取（纪律见第 5 节）。

## 3. 小红书 / Reddit / Facebook / Instagram：浏览器会话

这四个渠道走 **OpenCLI 复用用户已有浏览器会话**的方式（Reddit 首选 OpenCLI 桌面、备选 rdt-cli；小红书选型链 OpenCLI ▸ xiaohongshu-mcp ▸ xhs-cli，F-025/F-031）。

关键边界（F-032，README 一致）：

- ✅ 只使用**用户本人已有、且明确控制**的浏览器会话；
- ❌ 项目**不替用户登录**、**不读取浏览器 Cookie 文件**。

也就是说，你需要自己先在浏览器里登录好对应平台（建议用专用小号的浏览器配置），OpenCLI 在该会话基础上工作。这一"不代登录、不偷 Cookie"的克制被博文作者评价为"同类项目里很少见"（F-032，V）。

## 4. 雪球 / 小宇宙 / LinkedIn / Boss直聘

- **雪球**：行情、热门（F-030，渠道文件 `xueqiu.py` 实际存在 F-063）。
- **小宇宙播客**：音频转文字（F-030）。
- **LinkedIn**：选型 mcp-server-linkedin ▸ Jina Reader（F-025 之外的官方选型补充）。
- **Boss直聘**：招聘信息（渠道文件 `boss.py` 存在，README 树图漏画但实现在位 F-063）。

这四个按"帮我配 XXX"引导即可；其中 LinkedIn/Boss 同样涉及登录身份，遵守小号纪律。

## 5. 必须遵守的 Cookie/账号安全纪律

项目方与博文口径一致（F-033/F-068）：

1. **一律使用专用小号**，不要用日常主号。脚本调用有被平台检测并限制的风险。
2. **Cookie/Token 等同完整登录权限**——一旦泄露或被判定异常，影响范围就是该账号本身；小号能把损失圈住。
3. 凭据只落在本机 `~/.agent-reach/config.yaml`（Windows：`%USERPROFILE%\.agent-reach\config.yaml`），文件权限 600，不上传不外传（F-036）。不要把该文件提交到 Git、不要贴进对话或工单。
4. 不再使用时 `agent-reach uninstall --keep-config` 决定去留；要彻底清除连凭据一起删（不加 `--keep-config`，F-037）。

## 6. 稳定登录态的可选环境：服务器代理

官方文档提到，需要长期稳定登录态时可使用**服务器代理方案，成本约 $1/月**（F-068）。这类方案的意义是把"带登录态的浏览器会话"放在网络环境稳定的服务器上，减少本机网络波动导致的 `timeout`（doctor 三态见 [概念 02](../concepts/02-doctor-health-and-security-model.md)）。是否采用取决于你对账号、成本与合规的权衡，官方仅作建议。

OpenClaw 宿主别忘了执行权限前置（F-068）：

```bash
openclaw config set tools.profile "coding"
```

## 7. 配置后验证

```bash
agent-reach doctor --json
```

确认目标渠道的 `active_backend` 已指向可用后端、状态非 missing/timeout（F-021/F-065）。例如：

- Twitter 显示 twitter-cli 且 token 探测通过；
- 小红书/ Reddit 显示 OpenCLI 且浏览器会话可用；
- `timeout` 多为网络/代理问题，`broken` 多为会话/安装问题，按处方分别处理（F-020）。

## 阅读导航

- 安装与三档授权：[示例 00](00-install-and-doctor.md)
- 零配置 6 渠道 + B站：[示例 01](01-zero-config-channels.md)
- 安全机制全貌（默认只读/dry-run/凭据 600/卸载）：[概念 02](../concepts/02-doctor-health-and-security-model.md)
