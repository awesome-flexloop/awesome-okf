---
type: Example
title: "插件接入与交付演练：add、command 接入、deliver 标签与自测命令"
description: "第三方插件安装、通用 command 接入的安全约束、Webhook 接入前的分档检查、deliver 交付演练步骤与官方四条自测命令"
tags: ["插件接入", "command", "deliver", "Webhook", "sim", "benchmark", "交付流水线"]
status: stable
sources:
  - id: official-readme
    resource: https://github.com/KKKKhazix/agent-autoloop/blob/main/README.md
    title: "Agent Autoloop 官方 README「插件体系 / 自己跑一遍 / 拿来即用的场景模板」"
  - id: blog
    resource: https://mp.weixin.qq.com/s/T9_acg247gxzUNL4j5zrCw
    title: "开源我这折腾了1年的「Agent自动化系统」（2026-11-04）"
---

# 插件接入与交付演练

> **⚠️ 可复现性声明**：本篇命令与流程**整理自官方 README（2026-11-06 `main` 分支快照）**，可照做，但**本知识包未在本机安装运行该项目**。官方明确标注四类 Webhook 模板只在本地模拟服务验证、多家 Agent 的接入命令「还没有逐个跑过」（F-054、F-055）；执行前请按本页第 2 节分档判断，不要把「内置」读成「已连真实服务验证」。

## 1. 装一个第三方插件

```bash
agent-autoloop add <git 地址>
```

官方插件安装命令（F-053）。四类插件分别是事件、Agent、通道、交付（F-052）；插件**主动连进内核**，账号凭据留在各自插件里（F-058）。

### 通用 `command` 接入（官方 F-053）

接一个能收提示词、并打印最后一条回复的命令行工具时，用 `use: "command"` 传命令数组，`{prompt}` 作为**独立参数**传递、**不当作 shell 代码执行**。官方列出的接入命令形态举例（F-054）：

```text
dsh --profile headless {prompt}
pi --print {prompt}
```

> ⚠️ 官方对这份接入清单的原话是「**我们还没有逐个跑过**」（F-054）。它们是「可照着改的配方」，不是「已验证可用」的承诺。
>
> 安全约束不要绕过：`{prompt}` 独立参数是 [指令数据分离](../concepts/02-four-mechanisms.md) 在插件接口层的延伸。把提示词拼进 shell 命令串会重新引入注入面。

## 2. 接真实服务前的分档检查

| 档 | 对象 | 动手前该做什么 | 依据 |
|----|------|---------------|------|
| **A · 实测跑通** | Claude Code、Codex、ACP；飞书卡片的发送 / 按钮回调 / 卡片更新 | 可直接进试跑；仍按本机版本核对 | F-055 |
| **B · 本地模拟验证** | GitHub / GitLab / HTTP / 定时四类 Webhook 模板 | 先用 `emit <类型> --dry-run` 预演，再用本地模拟服务验证，最后才接真实服务 | F-055、F-048 |
| **C · 仅提供接入命令** | DSH、pi、OpenClaw、Hermes、Cursor、WorkBuddy / CodeBuddy | 先单点验证该 CLI 能否「收提示词 + 打印最后一条回复」，再写规则 | F-054 |

官方另注明：**GitLab Webhook 按官方文档格式测试、没连过真实 GitLab**；场景模板样例数据均为虚构，脚本与回执只用本地 HTTP 与假飞书 CLI 验证、**未在真实账号跑完整业务**（F-055、F-067）。

教程整理的推荐顺序（非官方原文步骤）：

```bash
# ① 先看规则会怎么派活
agent-autoloop rules explain

# ② 预演事件，不连中台、不写日志
agent-autoloop emit <类型> --dry-run

# ③ 确认无误后，再启用 Webhook / cron，并用 status 观察
agent-autoloop status
```

## 3. 交付演练：`deliver` 标签走完整条流水线

官方与博文一致的主流程（F-037、F-056）：

| 步 | 动作 |
|----|------|
| 1 | 给 PR 打 `deliver` 标签 |
| 2 | 定时查看 GitHub 标签的小脚本发现标签，转成事件 |
| 3 | 专门负责上线的 Agent 审代码 |
| 4 | 等检查（CI）通过 |
| 5 | 合并 PR |
| 6 | 等发布完成 |
| 7 | 线上确认新版本 |

两条官方硬约束（F-056）：**审查与交付配置只从 `main` 读取**；**绝不在接单电脑上检出或运行 PR 里的代码**。排队、并发与重试复用内核（F-056）。

> ⚠️ **单源提示**：博文说「只想审不上线再打 `deliver-review` 标签」（F-037），但**官方 README 只列出 `deliver`**，未列 `deliver-review`（F-068）。该标签仅博文单源，动手前以仓库配置手册为准，不要凭博文直接打标签。

官方场景模板里另有「PR 自动交付」「交付 PR」两套模板可作起点（F-063）；模板样例数据为虚构（F-067）。

## 4. 官方四条自测命令（把机制变成可验证的说法）

```bash
agent-autoloop why 1                      # 查第 1 轮完整事件链
node sim/random.ts 24301 200000          # 20 万步模拟：断网 / 丢包 / 崩溃 / 重复提交
node sim/crash.ts 1000 12648430          # 强杀 1000 次，验证已确认的事不丢
npm run benchmark                        # 复现官方实测性能表
```

全部来自官方「自己跑一遍」（F-060），本知识包**未执行**。对应机制见 [02 内核四机制](../concepts/02-four-mechanisms.md)：`sim/crash.ts` 测的是**进程强杀**，不是掉电——官方原话「**整机断电没有单独测过**」（F-057），请勿把该命令的输出当成掉电可靠性证明。

`npm run benchmark` 对应的官方实测环境为 Apple M5 Pro / 24 GB / Node 24.21.0，数字见 [01 内核与五步流程](../concepts/01-kernel-and-loop.md) 第三节；该组数字为作者单环境自测、无第三方独立复现（F-061）。

## 5. 从场景模板起手

官方七套场景模板（F-063）：每日早报、跟进 GitHub Issue、线上告警排查、用户反馈处理、网站巡检、飞书周报与业务摘要、PR 自动交付；另有浏览器交接、每周代码清理、交付 PR 三套扩展模板。仓库目录含 `examples/recipes/`、`skills/agent-autoloop/`、`docs/`、`tests/` 与 `sim/`（F-059）。

> 与作者自用 7 场景（F-040）区分开：模板是仓库里可读的配方，作者场景是博文里的实践举例，官方模板表未逐项对应。详见 [03 插件生态第六节](../concepts/03-plugin-ecosystem.md)。

## 6. 收尾检查清单（教程整理）

- [ ] 插件是 A / B / C 哪一档？B、C 档是否已用 `--dry-run` 或单点命令验证？
- [ ] `{prompt}` 是否作为独立参数传递，没有拼进 shell 命令串？
- [ ] `deliver` 之外的标签（如 `deliver-review`）是否已在仓库配置手册中确认存在？
- [ ] 审查与交付配置是否只从 `main` 读取，PR 代码是否没有在接单电脑检出？
- [ ] 高频自动化场景的账号用法是否已按 [用量与合规提示](01-install-and-first-run.md) 确认（F-064）？
- [ ] 是否清楚卸载默认保留规则、密钥与记录（F-066）？

## 边界提示

1. 全部命令**未在本机实测**；官方多处标注「未测 / 未逐个跑过」，本包按三档分级呈现，不合并成「都支持」。
2. 官方引文「我们还没有逐个跑过」「整机断电没有单独测过」等限定语不得缩写为结论（见 [P0 核验报告](../references/verification.md) 引文核对表）。
3. 完整的 68 条事实与 10 大项 P0 核验见 [信源层](../references/index.md)。
