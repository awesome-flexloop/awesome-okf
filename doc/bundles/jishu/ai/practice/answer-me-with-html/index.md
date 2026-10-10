---
okf_version: "0.2"
type: bundle
title: "answer-me-with-html：让 Agent 交付可视化页面的 Skill"
description: "开源星探公众号 2026-10-06 博文经 OKF v0.2 七阶段转化——Agent Skill answer-me-with-html 把『模型写内容、程序做排版』落地：模型只写 Markdown 草稿 + 九种组件指令，CLI 渲染出可读 HTML 页面 / 讲解视频；含基准测试核验、三种安装方式、配置与 Always-on 模式（操作教程，非纯案例）"
tags: [answer-me-with-html, agent-skill, open-source, html-rendering, token-optimization, claude-code]
generated: { by: "process:wechat-public-okf", at: 2026-10-10T00:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-10-10T00:00:00Z }
status: draft
stale_after: 2026-12-31
sources:
  - id: refs
    resource: /references/article-source.md
  - id: blog
    url: https://mp.weixin.qq.com/s/A-9ViZO69NJ30ZTsofjYeQ
  - id: github
    url: https://github.com/QingYunA/answer-me-with-html
  - id: karpathy-x
    url: https://x.com/karpathy/status/2105819303471976479
---

# answer-me-with-html：让 Agent 交付可视化页面的 Skill

> 📊 **数据性质提示**：文内 token / 耗时 / 成本基准与组件、安装、配置说明以 [源码仓库 README](https://github.com/QingYunA/answer-me-with-html)（权威源）为准；本项目为**快速迭代开源项目**，版本、默认值等随时可能变化，引用时须核对仓库当前状态并注意时点口径。

## 项目速览

**answer-me-with-html** 是一个装在 AI Coding Agent（Claude Code / Codex / Cursor / OpenCode）里的 **Skill**——模型只写一段很短的 Markdown 草稿（标题 + 几个组件指令），剩下的布局、配色、画图、导出全部交给随 Skill 自带的 CLI 工具 `am` 完成，最终交付可读、可分享、单文件无依赖的 HTML 页面（或 3Blue1Brown 风格讲解视频），而非一屏文字。

| 项 | 值 | 核验 |
|----|----|:---:|
| 项目 | answer-me-with-html（作者 QingYunA） | ✅ |
| 类型 | Agent Skill（非 Web App / 非 Prompt 网站） | ✅ |
| 语言 | Node.js 20+（CLI 内嵌，无 npm install 步骤） | ✅ |
| 许可证 | MIT | ✅ |
| GitHub | github.com/QingYunA/answer-me-with-html | ✅ |
| 页面场景基准（Claude Sonnet 5.5） | token 870 vs 5,341（6.1× 更少） | ⚠️ 口径见正文 |
| 讲解视频场景基准 | token 1,566 vs 27,839（17.8× 更少） | ⚠️ 单 topic 五轮 |

## 阅读路径

1. [核心理念与项目定位](concepts/00-overview-and-philosophy.md)——「让程序做排版」哲学、Karpathy 观察、为什么不用直接写 HTML；
2. [机制、九种组件与基准](concepts/01-mechanics-benchmarks-components.md)——Agent 自主判断 + 组件指令 + CLI 渲染，含页面/视频基准核验与 token 经济性边界；
3. [特性与 STE 写作检查](concepts/02-features-writing-check.md)——自动布局、报错自愈、双主题明暗、STE 受控语言检查、单文件无依赖；
4. [安装与 CLI 使用](concepts/03-install-usage.md)——三种安装方式、常用配置与命令行；
5. [模式与防踩坑](concepts/04-modes-gotchas.md)——Always-on 模式、抑制模式、更新清理，以及博文与权威源的勘误 E-1。

## 已知边界

- ❌ **勘误 E-1**：博文「Always-on 模式」一节给出的 `/plugin install answer-me-with-html-always@answer-me-with-html` 安装方式已被仓库废弃——该插件已从仓库移除，官方改用「在规则文件中写入一条全局规则」来开启（详见[核验报告](references/verification.md)）；
- ⚠️ 基准为官方自测口径（同模型同规格）：页面×3 次取中位数、视频仅单 topic 五轮（3 手写 / 2 am video），属「量级参考」而非精确比值；重上下文装载（约 51k token）时因额外两次往返反而约贵 20%；
- ⚠️ 配置项默认值依仓库 README 为准（如 `theme` 默认 `auto`，`update_check` 默认 `on`），与博文所述「blueprint、无声明 update_check」存在差异，属版本演进；
- 本项目未做真机复测；版本迭代极快（发布当天仍有多处提交），`status: draft` 待独立审查。

## 主题关联

- [🧘 上下文优化（Context Optimization）](../context-optimization/index.md)——同属「省 token / 提升阅读带宽」主题，本 Skill 是「改变呈现方式」路径的具体实现；
- [🗜️ planning-with-files 像 Manus 一样工作](../planning-with-files/index.md)——同为 Agent 脚手架 / Skill 级工具拆解；
- [🛠️ 工程实践、方法论与行业洞察](../index.md)——返回分组总览。

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
references/index
log
```