---
okf_version: "0.2"
type: Example
title: "登录态渠道配置与 Cookie 安全纪律"
description: "v1.6.0 专用浏览器与自动复制会话机制、login/logout/remove、Twitter token、Groq Key 配置，以及专用小号与凭据 600 纪律"
tags: [agent-reach, login, cookie, browser, twitter, xiaohongshu, reddit, security]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-26T11:55:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: blog2
    url: https://mp.weixin.qq.com/s/kk4iSX6xdk3IsNKO4eVy9w
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
  - id: official-sessions
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/agent_reach/skill/references/sessions.md
---

# 示例 02：登录态渠道配置与 Cookie 安全纪律

> 需要登录的渠道不是装完就能用，但配置方式仍是"说一句话 + 按引导走"。本文按 **v1.6.0** 的专用浏览器机制写，并在关键处标注与旧教程的差异。

## 1. 现行渠道档位

| 档位 | 渠道 | 解锁方式 |
|------|------|---------|
| 可选（6） | xiaohongshu、xueqiu、boss、xiaoyuzhou、linkedin、reddit | `agent-reach add <渠道>`，或对 Agent 说"帮我加 XX"（F-108） |
| 实验（3） | twitter、facebook、instagram | 同样 add；反爬更严，可能随时失效（F-108） |

统一入口：

```text
帮我加上小红书
帮我加上 Twitter
小红书登录过期了
```

Agent 会按 SKILL.md 的流程执行，并在完成后用 `doctor --text` 或 `check <渠道> --text` 验证（F-111/F-119）。

## 2. 专用浏览器与"自动复制会话"

v1.6.0 的机制值得完整理解，因为它直接决定账号风险（F-112/F-113）：

1. 所有浏览器渠道共用一个**专用浏览器**，与你的日常 Chrome 分开；默认无头不弹窗，闲置 10 分钟自动关闭，下次调用自动重开。
2. 第一次用某个网站时，如果 Chrome 已连 OpenCLI 扩展，程序会**把该站的 Cookie 复制一次**到专用浏览器。只复制该站；不复制整个浏览器目录、其他站点或密码库；不改动来源浏览器。
3. 之后一直复用这份会话，不按时间重新复制。Cookie 在 ≠ 登录有效，以真实动作结果为准。
4. 你本人在专用窗口登录过，或执行过 `logout`/`remove`，就不再自动复制，避免已退出的登录复活。

> ❌ **重要更正**：早期文章（含第二篇博文）写"不读取小红书浏览器 Cookie"，这与上述机制不符。准确说法是"**按站复制一次到隔离的专用浏览器**"。它不是"不碰 Cookie"，而是"不碰整库、不碰密码、不碰其他站点"。

浏览器相关命令：

```bash
agent-reach browser status                 # 专用浏览器状态
agent-reach browser setup                  # 准备内核与扩展
agent-reach browser profiles               # 本机多个浏览器都登录了该站时，列出来源
agent-reach browser use <ID>               # 选定一个来源，不随机切换
agent-reach login <渠道> --import-existing # 手动重取一次该站登录（不开窗口）
agent-reach browser stop                   # 关闭程序管理的浏览器
```

## 3. 需要本人登录时

只有实际返回 `NEED_LOGIN`、且剩余任务确实需要这条路径时，才开窗口（F-119）：

```bash
agent-reach login xiaohongshu
```

- 窗口打开后由**你本人**登录；Agent 不代登、不要密码、不输出 Cookie。
- 部分渠道（如雪球）登录后还要再跑 `agent-reach login <渠道> --sync`。
- 登录完成后重新执行原动作验证，不要反复开窗。

## 4. Twitter / X：token 与会话

Twitter 在 v1.6.0 属**实验档**（平台反爬更严）。登录方式优先走专用浏览器会话；旧版文档另给过环境变量方式（F-068）：

```bash
export TWITTER_AUTH_TOKEN="..."     # auth_token
export TWITTER_CT0="..."            # ct0
```

Windows PowerShell：

```powershell
$env:TWITTER_AUTH_TOKEN="..."
$env:TWITTER_CT0="..."
```

> 这两个值等同登录态，必须用**专用小号**获取；不要贴到聊天、工单或仓库里。

## 5. 密钥类渠道（小宇宙 / YouTube 转文字）

```bash
agent-reach configure groq-key
```

- Key 由**用户本人在终端**填写，不走聊天（F-114/F-118）。
- 小宇宙播客转文字、YouTube 无字幕转文字需要 Groq 或 OpenAI Key；有免费额度，但"零 API 费"的说法要打折（F-091/F-114）。

## 6. 必须遵守的账号安全纪律

项目方与两篇博文口径一致（F-118）：

1. **一律使用专用小号**，不要用日常主号。脚本化访问有被平台检测限制的风险。
2. **Cookie/会话等同完整登录权限**——一旦泄露或被判定异常，影响范围就是该账号；小号能把损失圈住。
3. 凭据只落在本机 `~/.agent-reach/config.yaml`（Windows：`%USERPROFILE%\.agent-reach\config.yaml`），权限 600，不上传不外传（F-115）。不要把该文件提交到 Git 或贴进对话。
4. 退出时用 `agent-reach logout <渠道>`（清该站登录）或 `agent-reach remove <渠道>`（连渠道一起清）；两者之后都不再自动复制该站登录（F-119）。

## 7. 配置后验证

```bash
agent-reach doctor --text
agent-reach check xiaohongshu --text
```

- `NEED_LOGIN`：需要本人登录，按第 3 节操作。
- `RATE_LIMITED`：按 `retry_after_seconds` 等，不换后端。
- `PLATFORM_BLOCKED`：平台要验证/风控，停下由本人在官方页面处理；**不换账号、不换后端**（F-119）。
- `BUSY`：浏览器排队满或登录窗开着，稍后再试，不关窗口。
- `TIMEOUT`：多为网络/代理问题；`UPSTREAM_BROKEN`：上游工具失效，用户同意后再 `agent-reach update`。

## 8. 与 1.5 教程的差异（别照旧文档操作）

| 项目 | v1.5 教程 | v1.6.0 现状 |
|------|-----------|-------------|
| Cookie 获取 | 推荐 Cookie-Editor 手工导出 | 首次访问自动复制该站 Cookie 到专用浏览器；`--import-existing` 可手动重取 |
| 浏览器 | 复用日常浏览器登录态 | 独立专用浏览器（优先 CloakBrowser，回退 Chrome），默认无头 |
| 隐私表述 | "不读取浏览器 Cookie" | "按站复制一次，不复制整库/密码/其他站" |
| 状态查看 | `doctor --json` | 默认 JSON；人读 `doctor --text` |

## 阅读导航

- 安装与升级：[示例 00](00-install-and-doctor.md)
- 默认 5 渠道：[示例 01](01-zero-config-channels.md)
- 安全机制全貌：[概念 02](../concepts/02-doctor-health-and-security-model.md)
- 团队凭据治理：[概念 04](../concepts/04-team-rollout-and-compliance.md)
