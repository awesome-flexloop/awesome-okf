---
okf_version: "0.2"
type: Concept
title: "模式与防踩坑"
description: "Always-on 模式、两种抑制模式、更新清理机制，以及博文与权威源之间的勘误 E-1（always 插件已废弃改规则文件）"
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

# 模式与防踩坑

## Always-on 模式

默认是「按需」：Agent 只在判断问题值得做页面时才生成。若希望**每次回答都带小页面**（哪怕是一个对比、计划、总结），开启 Always-on：

- 开启后，Agent 每回合收到一条约 90 token 的短提醒；
- 每次给出结论 / 对比 / 计划 / 总结时，自动附一张 2–4 个面板的小页面，路径贴在回复末尾；
- 聊天、命令输出、纯文本请求**不触发**，且不会弹浏览器（页面不主动弹出，不打搅）；
- Claude Code 在 plan mode 下不生成页面。

### ⚠️ 勘误 E-1：开启方式已从「插件」改为「规则文件」

博文的「Always-on 模式」一节给出的开启方式是再装一个插件：

```
/plugin marketplace add QingYunA/answer-me-with-html
/plugin install answer-me-with-html-always@answer-me-with-html
```

**仓库 README（权威源）明确表示该 `answer-me-with-html-always` 插件「已经从这个仓库移除」**，继续装只是在保有旧副本时不断提醒。官方当前做法：**在你的 Agent 规则文件中加一条全局规则**（例如 `~/.claude/CLAUDE.md` 或 `AGENTS.md`）：

> [answer-me-with-html always-on] Whenever a reply gives a conclusion, summary, plan, comparison, review or explanation, even a short one, also make a page with the answer-me-with-html skill (2 to 4 panels for routine answers), render it with `--no-open` before you write the reply, and end the reply with a `file://` link to the page. Skip casual chat, one- or two-sentence replies with no conclusion, pure command output, and requests for plain text.

关闭只需从规则文件删掉这条规则。若老插件还挂着提醒，先 `/plugin uninstall answer-me-with-html-always@answer-me-with-html` 再贴规则。（详见[核验报告](../references/verification.md)勘误 E-1。）

## 削减「太主动问题」的两种方式

默认 Agent 在「有帮助就做页」；若嫌太频繁，可选其一（**不要与 Always-on 组合**）：

1. **仅在你用文字要求时**（适用于所有 Agent）：在规则文件中加一条——
   > Do not use the answer-me-with-html skill unless I ask for a page, a diagram or a visual explanation, or say I don't get it.
   （规则在更新后保留，Agent 仍看得到技能，靠判断遵循。）

2. **仅用 slash 命令**（Claude Code）：给已装的 `SKILL.md` 的 frontmatter 加 `disable-model-invocation: true`，Agent 就不再主动看到技能，只有输入 `/answer-me-with-html` 才出页。注意更新会覆盖该文件，需更新后重加。

## 更新与清理

- **更新是手动的**。每周后台只读 GitHub 版本号（不发送任何你的数据），有新版时提及。关掉用 `/answer-me-with-html:config update_check off`；更新用 `npx skills update answer-me-with-html -y` 或告诉 Agent「update answer-me-with-html」；
- **清理**：页面 / 视频 / 旁白缓存在 `~/.answer-me-with-html/` 累积，文件夹变大时 Agent 会先征询再删，`am clean --dry-run` 可先预览。

## 防踩坑速记

| 坑 | 正确做法 |
|----|---------|
| 按博文装 `answer-me-with-html-always` 插件 | 已废弃，改用规则文件（勘误 E-1） |
| 默认主题照博文写「blueprint」 | README 现默认 `auto`，草稿内写 `theme:` 覆盖即可 |
| 把 27% 更便宜当普适结论 | 重型上下文（~51k token）下反而约贵 20%，须按实测 |
| 以为 Always-on 会弹窗打断 | 不弹；只是回复末尾附链接 + 页面累积 |
| 低估视频 `--mp4` 前置 | 需 Chrome + ffmpeg + Node.js 22+ |

## 关键事实引用

模式与勘误对应 [信源事实清单](../references/article-source.md) F-019~F-021 与 [P0 核验报告](../references/verification.md) 勘误 E-1。