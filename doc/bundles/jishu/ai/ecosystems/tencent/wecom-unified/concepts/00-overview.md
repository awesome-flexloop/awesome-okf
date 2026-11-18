---
type: concept
title: 套件定位与依赖
description: 厘清 wecom-unified 作为「Markdown 契约 + 脚本工具链」Skill 包的边界，以及它与 wecom-cli 的进程调用关系。
tags: [wecom, wecom-unified, overview]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# 套件定位与依赖

`wecom-unified` 是企业微信官方开源的「全能 Skill 套件」：它把企业微信的通讯录、文档、在线表格、智能表格、智能文档、在线 PPT、日程、会议、待办、微盘、邮件、消息等业务能力，封装成一套供 AI 宿主读取的 Markdown 契约与辅助脚本。理解它的第一步，是放弃「这是一个 SDK」的预设——套件本身不实现任何企业微信接口，接口能力全部来自另一个独立命令行工具 `wecom-cli`。

## 一、仓库形态：Skill 主体位于第二层

仓库根目录只有 5 个条目（`.git`、`.gitignore`、`LICENSE`、`README.md`、`skills`），**根目录没有 `SKILL.md`**；真正的技能主体在 `skills/wecom-unified/` 这一层，其下再分为 `SKILL.md`、`assets`、`references`、`scripts` 四类内容。这种「仓库 → `skills/` → 具体 Skill」的双层结构，是为同一仓库容纳多个 Skill 预留的布局。

| 层级 | 条目 | 说明 | 证据 |
|---|---|---|---|
| 仓库根 | 5 个条目 | `.git`、`.gitignore`、`LICENSE`、`README.md`、`skills` | F-001 |
| 根目录 | 无 `SKILL.md` | 技能入口不在仓库根 | F-003 |
| `skills/` | 2 个条目 | `wecom-unified/` 目录与 `wecom-unified.zip` 归档 | F-004 |
| `skills/wecom-unified/` | 4 个条目 | `SKILL.md`、`assets`、`references`、`scripts` | F-007 |
| 递归文件数 | 193 个 | 不含 `.git` 与 zip | F-008 |

193 这个数字并非偶然：1 篇 `SKILL.md` + 133 篇 `references` + 6 个 `scripts` + 53 个模板文件，恰好等于 193，说明技能目录内没有游离于这四类之外的内容（F-008、F-009、F-010、F-011）。

## 二、三块构成与各自职责

| 组成 | 体量 | 职责 | 证据 |
|---|---|---|---|
| `SKILL.md` | 15233 字节 | 意图分流、前置检查、输出约束、14 个业务域概览 | F-019、F-023 |
| `references/` | 133 篇 `.md` | 每个业务域的参数契约与操作细则 | F-009、F-045 |
| `scripts/` | 6 个 `.py` | DOCX/HTML/PPT 预览/表格采集与重算等物料工具 | F-010 |
| `assets/templates/` | 53 个文件 | 9 套 PPT 模板（preset + shell + slides + 注册表） | F-011、F-094 |

`SKILL.md` 只承担约 15 KB 的分流与约束，真正的参数知识外置在 133 篇 reference 中；它明确要求「判断业务域 → 读取该域 reference → 按其中参数规范构造命令」，并禁止凭路由表描述或记忆猜参数（F-023）。因此，套件的能力上限取决于「是否读到了正确的 reference」，而不是模型对接口的熟悉程度。

这也带来一个直接的上下文预算问题：133 篇 reference 的总量远超单次对话可容纳的范围，正确做法是「按需加载」——只在确定业务域后读取对应入口，以及该入口指向的少数细则。把整套 references 预读进上下文既不经济，也会稀释当前任务的指令权重；路由层的价值正在于把「读什么」从模型自觉变成流程约束。对维护者而言，新增能力应优先续写域内细则，而不是持续膨胀 `SKILL.md`。

## 三、与 wecom-cli 的进程调用关系

套件与 CLI 是两条独立交付链，运行时通过 shell 进程连接：

```text
宿主 Agent（Codex / Cursor / Claude Code 等）
  └─ 读取 SKILL.md，判定业务域
       └─ 读取 references/wecomcli-<域>.md，取得参数契约
            └─ Bash: wecom-cli <域> <动作> --json '{...}'
                 └─ 企业微信接口
scripts/*.py 仅在生成 DOCX / 页面 / 预览图时旁路运行
```

这条链有三处硬证据。其一，`SKILL.md` 的 `allowed-tools` 仅为 `Bash, Read`，说明技能没有原生函数调用通道，一切业务动作都要落到命令行（F-022）。其二，CLI 由 npm 包 `@wecom/cli` 提供，安装命令为 `npm install -g @wecom/cli`，并有 `1.2.1` 的版本下限（F-027、F-106）。其三，6 个脚本都不导入企业微信 SDK，且全部脚本中 `wecom-cli` 字符串只出现 1 处——`build_page.py` 的 `--cli` 默认值；对外部 CLI 的唯一子进程调用点也在 `build_page.py:2403`（F-107、F-108）。脚本是物料生成器，不是接口封装层。

由此可以得出一条部署纪律：**安装 Skill 不等于安装 CLI**。Skill 安装成功只代表 Markdown 契约与脚本就位，业务能否调用仍取决于 `wecom-cli` 是否存在、版本是否达标、凭证是否有效。

## 四、安装与运行环境

| 项目 | 要求 | 证据 |
|---|---|---|
| 安装命令 | `npx skills add WecomTeam/wecom-unified -y -g` | F-102 |
| 支持平台 | macOS（x64/arm64）、Linux（x64/arm64）、Windows（x64） | F-103 |
| 运行时 | Node.js >= 18 | F-103 |
| 宿主适配 | 支持 WorkBuddy、CodeBuddy、MiniMax Code、Kimi Work、Codex、Cursor 等，一行命令自动检测已安装平台 | F-104 |
| 业务 CLI | `npm install -g @wecom/cli`，版本 >= 1.2.1 | F-027、F-106 |
| 首次使用 | Skill 声称会自动检查并安装所需 CLI，并引导完成凭证配置 | F-105 |

`README.md` 的「自动检查并安装 CLI」是便利性承诺，不能替代后文的显式门禁：安装动作只是修复手段，安装后仍要复验版本与授权态（F-028、F-032）。在离线或内网环境中，可改用仓库同级的 `skills/wecom-unified.zip` 归档分发（423870 字节、198 个归档条目），但 `@wecom/cli` 仍需单独准备离线包（F-005、F-006）。

## 五、许可与版本口径

仓库采用 MIT 许可证，`LICENSE` 第 1 行为 `MIT License`，第 3 行为 `Copyright (c) 2026 WeCom`（F-012）。`SKILL.md` 的 frontmatter 只有 `name`、`description`、`allowed-tools` 三项，**没有 `version` 字段**，因此本知识包不引用「套件版本号」，一律以 commit `cae8a5befac67d96bfe573b1675c5faab474758e` 为基线（F-019～F-022）。这一口径差异在升级评审时很关键：Skill 侧看 commit，CLI 侧看 `1.2.1` 下限，两者不能混用。

## 延伸阅读

- [前置检查与身份](01-preflight-and-identity.md)：三步门禁与 `identity whoami` 的具体判定。
- [意图路由](02-intent-routing.md)：14 个业务域如何从自然语言与链接特征中分流。
- [脚本工具链](04-scripts-toolchain.md)：6 个脚本的输入输出与部署依赖。
- [信源登记](../references/sources.md)：上游仓库、基线 commit 与核对命令。