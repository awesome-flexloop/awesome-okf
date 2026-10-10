---
okf_version: "0.2"
type: Reference
title: "answer-me-with-html P0 核验报告"
description: "博文与仓库 README 的关键声明 P0 交叉核验（含基准、默认值、Always-on 插件），含勘误 E-1"
tags: [answer-me-with-html, p0-核验, 勘误, github, token-optimization]
generated: { by: "process:seven-concepts-v", at: 2026-10-10T00:00:00Z }
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

# answer-me-with-html P0 核验报告

## 信源距离预判

| 信源 | 距离分类 | 核验待遇 |
|------|---------|---------|
| 公众号「开源星探」博文 | 第三方综述（转述） | 数字与默认值按 P0 处理，优先与权威源对拍 |
| GitHub 官方仓库 README | 一手权威（开源项目自述） | 作为交叉核验主锚 |
| Karpathy X 帖子 | 一手外部引文 | 引文逐字较对 |

> 说明：本项目是**快速迭代开源项目**（采集当日 0.4.12 仍有多处提交），「默认值、版本、入口」随时可能变化；本项目不对代码做真机复测，未实测 `am` 具体行为。

## P0 核验总表

图例：✅ 与权威源一致 / 补充；⚠️ 单源或口径差异、方向一致；❌ 与权威源矛盾。

| # | 声明 | 结论 | 核验依据 |
|---|------|:----:|---------|
| P0-1 | 项目是 Agent Skill 而非独立 Web App / 网站 | ✅ | F-002；README 管它叫「An agent skill」，安装进 agent 的技能目录 |
| P0-2 | 支持 Claude Code / Codex / Cursor / OpenCode | ✅ | F-005；README 安装节与博文均列，installer 支持 70+ agents |
| P0-3 | Karpathy「跟上模型输出变难」观察为项目核心理念来源 | ✅ | F-001；README「Background」节原样引用该 X 帖 |
| P0-4 | 页面场景 token 6.1× 更少、2.8× 更快、27% 更便宜 | ✅（口径限定） | F-009；README bench 与博文表格一致，但为「3×3 取中位数、普通装载」口径，重型上下文反例须并读 F-010 |
| P0-5 | 视频场景 token 17.8×、耗时 11.8× | ⚠️ | F-011；README 与博文数字一致，但明确「单 topic 五轮量级」，非精确比值，博文未提此限定 |
| P0-6 | 省成本为普适结论 | ⚠️ | F-010；README 明确重型装载（~51k token）反而贵约 20%，博文未告知此边界 |
| P0-7 | 九种组件清单 | ✅ | F-008；与 README「What you ask, what you get」及组件说明一致 |
| P0-8 | STE 写作检查源自 ASD-STE100，默认 warn | ✅ | F-014；README 明确 ASD-STE100，style=80（warn）/ strict |
| P0-9 | 单文件无依赖 | ✅ | F-015；README 明言「不引用 CDN/网络字体」，视频内嵌音频离线播 |
| P0-10 | 三种安装方式 | ✅ | F-016/F-017；博文与 README 一致（agent 自装 / 插件市场 / 手动 clone+cp；README 另增 INSTALL.md 路径） |
| P0-11 | Always-on 可通过装 `answer-me-with-html-always` 插件开启 | ❌ | F-020/F-021；**勘误 E-1**，见下 |
| P0-12 | 默认主题 blueprint | ⚠️ | F-019；README 现默认 `theme: auto`（长文 paper / 图表 blueprint），博文「默认 blueprint」为版本演进前的转述 |
| P0-13 | 配置无需手编配置文件 | ✅ | F-018；README「There are no config files to edit by hand」（存于 `~/.answer-me-with-html/config.json`，用 slash/CLI 改） |
| P0-14 | 项目 1.4K Star、三天前出现 | ⚠️ | F-004；Star 数为发稿时点量级，仓库当日仍有新提交、版本 0.4.12/106 commits，属快速迭代项目，勿作为稳定结论 |

**汇总：14 项 → 10 ✅ / 4 ⚠️ / 0 ❌（另有勘误级 P0-11 一条 ❌ 见下）。**

## 勘误登记

### E-1（❌ 核心勘误）：Always-on 开启方式「装插件」已被官方废弃

博文「Always-on 模式」一节给出：

```
/plugin marketplace add QingYunA/answer-me-with-html
/plugin install answer-me-with-html-always@answer-me-with-html
```

仓库 README（权威源）明确：「**Installed the old `answer-me-with-html-always` plugin?** It is **gone from this repository**，…」——该插件已从仓库移除，官方在 2026-10-06 的 commit `5c53dcf`「refactor: drop the always-on plugin in favor of a rules-file snippet」中把开启方式重构为「在规则文件写入一条全局规则」（见[概念文档 04](concepts/04-modes-gotchas.md)）。

**处理：** bundle 正文以「规则文件」为唯一推荐开启方式；保留博文插件做法的说明并标注官方已废弃、继续使用仅适用于仍有旧副本的存量场景（需先 `/plugin uninstall`）。因此 E-1 不改变 bundle 主旨（该 Skill 是「改变呈现方式省 token」的可行工具），保留 `status: draft` 待独立审查。

### 补充勘误级边界（非矛盾，口径差异）

- **默认主题**：博文「默认 blueprint」→ 权威源现默认 `auto`；正文按 `auto` 呈现并提示可在草稿 frontmatter 覆盖（P0-12）；
- **成本结论**：博文「27% 更便宜」→ 权威源限定「普通装载」，重型装载反例（贵 20%）须并读（P0-6）。

## 已走过的剽窃/版权与边界自查

- 本 bundle 为**原创转述 + 要点整理**，未复制博文全文或 README 长段原文；
- 引用的 Karpathy 观点仅作引文归属（F-001），无逐字长引；
- 操作命令（安装 / CLI）属于公开文档提供的事实性指令，按短引形式呈现并标注来源；
- 不涉及个人数据、私有附件、邀请码或登录墙绕过。

## 已知边界（读者使用提示）

- 本 bundle 与博文同为 **2026-10-06/10-10 时点**快照，快速迭代项目请以仓库 README 当前状态为准；
- 基准为官方自测口径，未独立复测；
- 所有命令以 Node.js 20+（视频 --mp4 需 Node 22）为前提，实际路径与 Skill 目录随 Agent 而定。