---
okf_version: "0.2"
type: Example
title: "安装 Agent Reach 并完成首次体检（v1.6.0）"
description: "uv 安装与一句话安装、agent-reach setup、doctor --text/JSON 体检、从 1.5 迁移、按需加渠道与干净卸载的可照做流程"
tags: [agent-reach, install, uv, upgrade, doctor, uninstall]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-26T11:35:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: blog2
    url: https://mp.weixin.qq.com/s/kk4iSX6xdk3IsNKO4eVy9w
  - id: official-install
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
---

# 示例 00：安装 Agent Reach 并完成首次体检（v1.6.0）

> 可复现流程，以 **v1.6.0** 的 docs/install.md 为准（F-109）。1.5 时代的 pipx 命令仍保留在文末作历史对照，但**不要再用**。
> ⚠️ 本知识包未在本机实际执行安装，以下为官方文档口径的照做流程；第一次装建议先看 `--dry-run` 再真装。

## 前置条件

- **能执行终端命令**。若 Agent 说自己不能跑命令，先在它的设置里开启命令执行（OpenClaw 为 `openclaw config set tools.profile "coding"`）。
- **不需要预装 pipx**。v1.6.0 用 uv 管理工具环境；仓库徽章仍标 Python 3.10+，uv 会处理解释器。
- **不要从 PyPI 装**：`pip install agent-reach` 装到的是别人的同名包（F-095/F-109）。

## 第一步：两条安装路径

### 路径 A：一句话安装（官方主推）

在 Claude Code / Cursor / OpenClaw 里直接发送：

```text
帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md
```

Agent 会读文档、装 uv（如缺）、安装 CLI、跑 `setup`，最后把程序生成的安装报告原样贴给你（F-081/F-109）。

### 路径 B：手动执行（想自己掌控每一步时）

```bash
# 1) 没有 uv 先装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh                 # macOS / Linux
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

# 2) 安装最新 release
uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip

# 3) 初始化：启用默认渠道 + 安装给 Agent 的 skill
agent-reach setup
```

装完若提示 `agent-reach: command not found`，执行 `uv tool update-shell` 并新开一个终端（F-109）。

> **版本锁定提示**：`latest/download/...` 会随版本漂移。团队基线建议把 URL 中的 `latest` 换成具体 release（如 `v1.6.0`），并在变更记录里写明（见 [04](../concepts/04-team-rollout-and-compliance.md)）。

## 第二步：从 1.5 或更早升级

1.5 是 pipx/pip 装的，1.6 改成 uv，官方要求显式迁移（F-109）：

```bash
uv tool install --force https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
# 新开终端确认
agent-reach version        # 1.6+ 输出 JSON；1.5 输出一行纯文本
agent-reach setup          # 保留 ~/.agent-reach/config.yaml，移除旧程序，刷新各 Agent 的 skill
```

`setup` 会保留你的 `~/.agent-reach/config.yaml`（含密钥与设置），只移除旧版 Agent Reach 自身，不动你其他工具（F-109）。

## 第三步：体检

```bash
agent-reach doctor --text      # 人读：每个渠道通不通、当前走哪个后端、坏了怎么修
agent-reach doctor             # JSON：给 Agent 读 ok / result / error.hint
agent-reach check bilibili --text   # 实测单一渠道
```

v1.6.0 起所有命令默认输出单个 JSON（F-111）。`doctor` 的价值在于**真实执行**上游命令，而不是只看命令是否存在：missing / broken / timeout 三态对应不同处方（F-084，见 [概念 02](../concepts/02-doctor-health-and-security-model.md)）。

## 第四步：按需加渠道

默认装好的是 5 个：web、youtube、github、bilibili、v2ex（F-108）。其余按需加：

```bash
agent-reach add xiaohongshu     # 加渠道，依赖自动装
agent-reach remove v2ex         # 去掉渠道，同时清该站登录与存储
agent-reach channels            # 看每个渠道支持的动作与参数
```

也可以直接对 Agent 说"帮我加上小红书""去掉 V2EX"（F-119）。需要登录的渠道见 [示例 02](02-login-channels-and-cookie-safety.md)；转文字需要 Key 的渠道用：

```bash
agent-reach configure groq-key   # 由用户本人在终端填写，不要发聊天里
```

## 第五步：日常升级与卸载

```bash
agent-reach update                        # 升级程序 + 已加渠道的工具 + skill
agent-reach uninstall --dry-run           # 先列出会删什么
agent-reach uninstall                     # 确认后删除
```

卸载只删 Agent Reach 自己装的东西；你的其他文件与浏览器不受影响（F-118）。需要保留凭据方便重装时，先备份 `~/.agent-reach/config.yaml`（Windows：`%USERPROFILE%\.agent-reach\config.yaml`），权限应为 600（F-115）。

## 历史对照：1.5 的安装命令（不要再用）

```bash
# v1.5.0 及更早
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto [--safe | --dry-run]
```

> ⚠️ 两个常见错误：一是 `pip install agent-reach`（PyPI 同名包，非本项目）；二是 `--system`（**该参数从未存在**，见 F-092/F-110）。旧教程里的这两条都要改。

## 排障速查

| 现象 | 处理 |
|------|------|
| `agent-reach` 找不到 | `uv tool update-shell` 后新开终端；确认 `uv tool list` 里有它 |
| `version` 还是旧的一行文本 | 仍是 1.5，按"第二步"迁移 |
| doctor 报某后端 missing | 按输出给的安装命令装上游，或对 Agent 说"帮我配 XX" |
| doctor 报 broken | 按重装处方重建该上游工具环境（如 shebang 失效） |
| doctor 报 timeout | 检查网络/代理；登录态渠道检查会话是否过期（F-118） |
| 平台要求验证/风控 | 停下，由本人在官方页面处理；不换账号、不换后端重试（F-119） |
| `setup` 后 Agent 仍不会用 | 确认 skill 已注册：`agent-reach skill`；需要给另一个 AI 用时 `agent-reach skill link <目录>` |
| 装了 PyPI 同名包 | 卸载后用官方 release zip / install.md 重装（F-109） |

## 下一步

- [示例 01：默认渠道实操](01-zero-config-channels.md)
- [示例 02：登录态渠道与 Cookie 安全](02-login-channels-and-cookie-safety.md)
- [概念 05：版本漂移与迁移清单](../concepts/05-version-drift-and-channel-matrix.md)
