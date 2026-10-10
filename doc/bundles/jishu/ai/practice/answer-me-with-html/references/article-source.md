---
okf_version: "0.2"
type: Reference
title: "answer-me-with-html 博文信源事实清单"
description: "公众号「开源星探」博文 + GitHub 仓库 README 的 F 编号事实登记：产品定位、机制、基准、安装、配置与模式"
tags: [answer-me-with-html, agent-skill, open-source, token-optimization, 信源登记]
generated: { by: "process:wechat-public-okf", at: 2026-10-10T00:00:00Z }
status: draft
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/A-9ViZO69NJ30ZTsofjYeQ
  - id: github
    url: https://github.com/QingYunA/answer-me-with-html
  - id: karpathy-x
    url: https://x.com/karpathy/status/2105819303471976479
---

# answer-me-with-html 博文信源事实清单（F 编号登记）

> 信源主体：公众号「开源星探」2026-10-06《1.4K Star！这个开源 Agent Skill 把一屏文字墙撕成了可视化页面！一看就懂！》；交叉源：仓库 GitHub 官方 README（权威源，采集于 2026-10-10）。
> 层级：【博文】= 博文声明；【官方】= GitHub README / 官方文档（权威源）。

## A. 信源元数据

| 编号 | 事实 | 层级 |
|------|------|------|
| F-001 | 文章以 Andrej Karpathy 在 X 上的帖子开篇（F-001 起因）：「当 LLM 的输出越来越长，跟不上它反而是我们自己」；X 帖子链接为 x.com/karpathy/status/2105819303471976479。 | 【博文/官方】 |
| F-002 | answer-me-with-html **不是独立的 Web App**，也不是写 Prompt 的网站，而是一个 **Agent Skill**，可装进 Claude Code、Codex、Cursor、OpenCode。 | 【博文/官方】 |
| F-003 | 核心哲学：「让模型写它擅长的内容，把排版、布局、画图这些机械活交给程序」；模型只写很短 Markdown 草稿（标题 + 几个组件指令），其余交给随 Skill 内嵌的 CLI 工具 `am`。 | 【博文/官方】 |
| F-004 | 项目三天前（相对 2026-10-06 发稿）在 GitHub 出现，已冲到 **1.4K Star**。发布时间为约量级描述，仓库当日仍在快速迭代。 | 【博文】 |
| F-005 | 支持 Agent：Claude Code、Codex、Cursor、OpenCode；installer（vercel-labs/skills）官方声明支持 70+ agents。 | 【博文/官方】 |
| F-006 | 运行前置：Node.js 20 或更新；无 `npm install` 步骤，CLI 内嵌在技能目录内。 | 【官方】 |
| F-007 | 交互机制：Agent 自行判断问题「值得做页面」，写 Markdown 草稿，由 CLI 约 50ms 渲染出可读页面；页面保存在 `~/.answer-me-with-html/pages/`，右上角可切主题/明暗并复制草稿。 | 【官方】 |
| F-008 | 九种组件：flow / sequence / tree / timeline / limits / annot / kv / callout / table；Agent 根据问题类型自动选组件。 | 【博文/官方】 |
| F-009 | 页面基准（Claude Sonnet 5.5，3 topics × 3 runs 取中位数）：token 870 vs 5,341（6.1× 更少）、耗时 12s vs 33s（2.8× 更快）、成本 $0.067 vs $0.092（27% 更便宜）。 | 【官方】 |
| F-010 | README 边界提示：Skill 额外加入两次短往返（每往返会重读上下文）；普通装载下省 token 划算，重型装载（约 51k token 上下文）下实测反而贵约 20%。 | 【官方】 |
| F-011 | 讲解视频基准（单 topic，5 runs：3 手写 / 2 `am video`，取中位数）：token 1,566 vs 27,839（17.8× 更少）、耗时 17s vs 202s（11.8× 更快）；README 建议按量级参考而非精确比值。 | 【官方】 |
| F-012 | 自动布局：流程图/时序图/树/时间线等由 CLI 排版，Agent 无需手画坐标，不错位。 | 【博文/官方】 |
| F-013 | 草稿语法错误：CLI 报行号 + 组件名 + 正确示例，Agent 通常一轮修好。 | 【博文】 |
| F-014 | STE 写作检查：灵感来自 ASD-STE100（航空维护手册受控英语）；中英规则集，句长/常用词/模糊词/套话规则；默认 `warn`，可设 `strict` 拒绝渲染。 | 【博文/官方】 |
| F-015 | 单文件无依赖：生成的 `.html` 不引用 CDN 或网络字体，双击即开，便于内网/归档；视频页面内嵌音频、离线可播。 | 【博文/官方】 |
| F-016 | 安装方式：① Agent 自装（复制 `npx -y skills add QingYunA/answer-me-with-html -g -y` + `-a <agent>`，Agent 自跑安装/读 SKILL.md/自测 TCP 手页）；② Claude Code 插件市场（`/plugin marketplace add` + `/plugin install answer-me-with-html@answer-me-with-html`）；③ 手动 clone+cp。README 另支持「让 Agent 读 INSTALL.md 照做」。 | 【博文/官方】 |
| F-017 | 手动安装目录：Claude Code `~/.claude/skills/`，Codex `~/.codex/skills/`，Cursor `~/.cursor/skills/`，OpenCode `~/.config/opencode/skill/`。 | 【官方】 |
| F-018 | CLI 与配置：`am render` / `am video` / `am video --mp4`（需 Chrome+ffmpeg+Node22）/ `am config` / `am config set …` / `am help <component>`；配置存在 `~/.answer-me-with-html/config.json`，一般无需手编。 | 【博文/官方】 |
| F-019 | 配置键（官方 README，默认值与其一致）：open=on、theme=auto、mode=auto、style=80、update_check=on、voice=auto；`--open`/`--no-open` 仅影响单次运行。(注：博文称默认 blueprint / 未列 update_check，与权威源差异见勘误。) | 【官方】 |
| F-020 | Always-on 模式：Agent 每回合收约 90 token 提醒，每次结论/对比/计划/总结自动附 2–4 面板小页面、路径贴末尾；不弹浏览器；聊天/命令输出/纯文本不触发；Claude Code plan mode 不生成。 | 【博文/官方】 |
| F-021 | 官方当前以「规则文件加一条全局规则」开启 Always-on（README 声明原 `answer-me-with-html-always` 插件已移除）；削减主动性的两种方式：仅文字要求 / 仅 slash 命令（`disable-model-invocation: true`）。 | 【官方】 |

> 说明：本项目为**单源blog→多源核验**。所有与「数字 / 默认值 / 安装入口」相关的事实均以仓库 README（官方权威源）为准交叉核验；博文为第三方转述，`【博文】`独有、`【官方】`无法对拍的表述按单源标注并在 P0 报告中给出结论。