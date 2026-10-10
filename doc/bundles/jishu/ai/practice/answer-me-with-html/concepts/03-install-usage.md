---
okf_version: "0.2"
type: Concept
title: "安装与 CLI 使用"
description: "三种安装方式（agent 自装 / Claude Code 插件 / 手动 clone+cp）、常用配置项与 am 命令行使用"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/A-9ViZO69NJ30ZTsofjYeQ
    title: "开源星探 2026-10-06 公众号文章"
  - id: github
    url: https://github.com/QingYunA/answer-me-with-html
    title: "answer-me-with-html 仓库 README"
last_modified: 2026-10-10
status: draft
stale_after: 2026-12-31
---

# 安装与 CLI 使用

前置要求：**Node.js 20 或更新**；无 `npm install` 步骤，CLI 随 Skill 内嵌。

## 三种安装方式

### 方式一：让 Agent 自己装（官方推荐）

直接复制以下指令丢给 Claude Code / Codex / Cursor / OpenCode，Agent 会自行安装并自测：

> Install the Answer me with HTML skill: run `npx -y skills add QingYunA/answer-me-with-html -g -y`, and pass `-a` with your own agent name (for Claude Code, `-a claude-code`). Then read its SKILL.md and use it to make a page that explains the TCP three-way handshake, so we know it works.

Agent 会自己跑安装、自己读 SKILL.md、自己做一张 TCP 握手页来验证（F-016）。README 也支持「让 Agent 读 INSTALL.md 并照做」的路径——INSTALL.md 专门写给 Agent，能自动装插件/技能、保留既有安装、用完以 TCP 握手页自检并给一份报告。

### 方式二：Claude Code 插件市场

在 Claude Code 内直接跑：

```
/plugin marketplace add QingYunA/answer-me-with-html
/plugin install answer-me-with-html@answer-me-with-html
```

### 方式三：手动安装

```
git clone --depth 1 https://github.com/QingYunA/answer-me-with-html.git /tmp/answer-me-with-html
cp -R /tmp/answer-me-with-html/skills/answer-me-with-html ~/.claude/skills/answer-me-with-html
```

其他 Agent 的 Skill 目录：Codex `~/.codex/skills/`、Cursor `~/.cursor/skills/`、OpenCode `~/.config/opencode/skill/`。

## 安装完怎么用

装好**不用配置**，像往常一样提问即可。如需手动调 CLI（F-018）：

| 命令 | 作用 |
|------|------|
| `am render draft.md` | 把草稿渲染成 HTML 页面 |
| `am video draft.md` | 生成 3Blue1Brown 风格讲解视频页面 |
| `am video draft.md --mp4` | 额外导出 mp4（需 Chrome + ffmpeg + Node 22） |
| `am config` | 查看当前配置 |
| `am config set open off` | 关闭自动弹浏览器 |
| `am clean [--dry-run]` | 清理积累的页面/视频/旁白缓存 |
| `am help <component>` | 查询某个组件的完整语法 |
| `am help video` | 视频完整语法 |

## 常用配置项

全部通过 slash 命令或 CLI 改，**无需手编配置文件**（默认值以仓库 README 为准）。

| 键 | 默认 | 作用 |
|----|------|------|
| `open` | `on` | 生成后自动弹浏览器。关掉免得打断节奏 |
| `always`→（现为规则文件） | `off` | 见 [Always-on 模式](04-modes-gotchas.md)，README 已用规则文件取代插件 |
| `theme` | `auto` | 默认主题：`auto` / `blueprint` / `shadcn` / `paper` 或自定义 |
| `mode` | `auto` | 颜色模式：`auto` / `light` / `dark` |
| `style` | `80` | 写作检查：`off` / `80`（warn）/ `strict`（拒绝渲染） |
| `update_check` | `on` | 每周检查 GitHub 新版本并提及，从不自动更新 |
| `voice` | `auto` | 视频旁白：`auto`（有 ELEVENLABS_API_KEY 用 ElevenLabs，否则系统音）/ `elevenlabs` / `local` / `system` / `off` |
| `--open` / `--no-open` | 本次运行 | 仅影响单次运行是否弹浏览器 |

配置文件实际存在 `~/.answer-me-with-html/config.json`，一般无需手动改。草稿内写主题会覆盖默认。slash 命令形态：

- Claude Code（插件安装）：`/answer-me-with-html:config` 交互问改什么；`/answer-me-with-html:config open off` 直接改；
- 任意 Agent：`/answer-me-with-html config open off`，或直接说「别弹浏览器」。

## 关键事实引用

安装与配置对应 [信源事实清单](../references/article-source.md) F-016~F-018。