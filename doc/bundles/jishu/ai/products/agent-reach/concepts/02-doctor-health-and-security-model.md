---
okf_version: "0.2"
type: Concept
title: "doctor 真体检与安全授权模型"
description: "probe 真跑的 missing/broken/timeout 三态诊断、doctor --json 人机双输出、安装默认只读/dry-run/system 三档授权、凭据 600 与干净卸载"
tags: [agent-reach, doctor, probe, health-check, security, dry-run]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-08T12:10:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
---

# doctor 真体检与安全授权模型

> 工程机制层。本文讲两件事：健康检查为什么要"真跑一遍"（probe.py 三态），以及一个能让 Agent 动系统的安装器如何设计授权边界。

## 1. doctor：真跑一遍，而不是"看命令在不在"

博文批评一类常见健康检查：只做 `which xxx`，有输出就算通过（F-019）。但真实世界的失败形态包括：

- 命令装了，系统 Python 升级后 venv 的 shebang 失效；
- 依赖在，但网络超时；
- 二进制存在，但登录态过期。

Agent Reach 的 `probe.py` 会**真实执行上游命令**，把每个后端的状态分为三类并给出不同处方（F-020，README 核验一致 F-065）：

| 状态 | 含义 | 处方 |
|------|------|------|
| `missing` | 压根没装 | 给出安装命令 |
| `broken` | 装了但跑不通（如 shebang 失效） | 给出重装处方 |
| `timeout` | 能跑但超时 | 提示网络或凭据问题 |

关键差别在于：它不是告诉用户"有/没有"，而是告诉用户"**哪里坏了、怎么修**"。配合 [01](01-capability-layer-architecture.md) 的有序后端列表，探测结果还决定当前由哪个后端提供服务——渠道上报的 `active_backend` 字段即探测选主的结果；当无任何后端可用时，该字段为 `null`（F-065，GitCode 旁证文档确认此语义）。

## 2. 人机双输出：文本给人，JSON 给 Agent

```bash
agent-reach doctor         # 文本报告，给人读
agent-reach doctor --json  # 结构化 JSON，给 Agent 读
```

`doctor --json` 的设计目标读者是 Agent 而非人（F-021）：JSON 里的 `active_backend` 让 Agent 在动手之前就知道"这个平台我现在该调哪套命令"，而不是先盲试一轮再从报错里猜。这也被写进给 Agent 的操作纪律——SKILL.md 要求"动手前先跑 `doctor --json` 看 `active_backend`"（F-040，文件实际位置见 [03](03-skill-md-agent-distribution-paradigm.md) 的路径勘误）。

推介作者把它提炼为一条产品判断（F-022，V）："同一份诊断信息同时服务人和 Agent——文本报告给人读，JSON 给 Agent 读。做 Agent 基础设施的项目，几乎都会走到这一步。"

## 3. 安装授权三档：默认只读 → dry-run → 显式 system

一个会安装上游工具、改 shell 配置、写 MCP 接线的 CLI，如果又是被 Agent 自动调用的，授权边界就变得关键。Agent Reach 的 install 分三档（F-034/F-035，README 逐字核验 F-065/F-066）：

```bash
agent-reach install --env=auto               # 默认：只读检查，不装包、不写配置，只列出缺什么
agent-reach install --env=auto --dry-run     # 预览：把准备做的事全列出，一个字节不改
agent-reach install --env=auto --system      # 显式授权：才真正动系统安装
```

README 另有 `--safe` 开关（F-065）。三档的安全语义是：

1. **默认只读**——不带 `--system` 时 install 不产生任何系统变更，天然适合让 Agent 先跑一遍收集缺口；
2. **`--dry-run` 预览**——把计划动作完整摊开，人确认后再执行；
3. **`--system` 显式授权**——真正写系统必须由人明确加参数，Agent 无法在默认路径上越权。

博文对此的判断（F-039，V）："Agent 能执行 shell 命令，就意味着它能改你的系统。凡是要交给 Agent 自动跑的安装器，'默认只读 + 显式授权 + dry-run'应该成为标配，而不是加分项。"

## 4. 凭据边界与卸载

| 机制 | 设计 | 出处 |
|------|------|------|
| 凭据存储 | Cookie、Token 只存在 `~/.agent-reach/config.yaml`，文件权限 **600**（仅所有者可读写），不上传、不外传 | F-036/F-065 |
| 登录克制 | 不替用户登录、不读浏览器 Cookie；OpenCLI 只用用户已有且明确控制的浏览器会话 | F-032 |
| 干净卸载 | `uninstall` 清除配置目录、各 Agent 的 skill 文件、MCP 配置 | F-037/F-065 |
| 卸载预览 | `uninstall --dry-run` 只预览不删 | F-037 |
| 保留凭据 | `uninstall --keep-config` 保留凭据，方便日后重装 | F-037 |
| 组件可插拔 | 不信任某个组件就换掉对应 channel 文件，不影响其他渠道 | F-038 |

Windows 下配置目录对应 `%USERPROFILE%\.agent-reach\config.yaml`（权限模型以类 Unix 600 表述为准）。

## 5. 采用前应知悉的边界

- **Cookie 即完整登录权限**：需要登录态的渠道（小红书/Reddit/Facebook/Instagram 及 Twitter token）一旦被平台判定异常，风险落在所用账号上——项目方与博文都一致建议使用**专用小号**（F-033/F-068）。
- **宿主权限前置**：在 OpenClaw 中使用需先 `openclaw config set tools.profile "coding"` 打开 exec 权限；官方另建议需要稳定登录态时走约 $1/月的服务器代理方案（F-068）。这些是运行环境成本，不在"零配置"范围内。
- **供应链注意**：官方明确警告**不要从 PyPI 安装同名包**，应以 GitHub archive 或一句话安装文档为准（F-069）。
- 本知识包核验了上述机制在 README/install.md 中的**文字记载与命令逐字一致性**，但未在本机实际安装运行、未复现三态输出；采用时建议自己先跑一次 `install --env=auto --dry-run` 与 `doctor` 验证。

## 阅读导航

- 实操命令见 [示例 00：安装与体检](../examples/00-install-and-doctor.md)
- 登录态渠道配置与小号纪律见 [示例 02](../examples/02-login-channels-and-cookie-safety.md)
- 这套"真体检 + 双输出"思想在五条设计启示中的位置见 [概念 03](03-skill-md-agent-distribution-paradigm.md)
