---
okf_version: "0.2"
type: Example
title: "安装与调用实操：npx 安装、三种调用、WorkBuddy 路径"
date: 2026-09-16
tags: ["实操", "安装", "npx", "show-me", "WorkBuddy", "GitHub连接器"]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ
  - id: official-blog
    url: https://www.humanlayer.dev/blog/show-me-skill
  - id: workbuddy-docs
    url: https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Task-Bar
---

# 安装与调用实操

> 命令以 HumanLayer 官方博客代码块为准（2026-08-12，F-026/F-031 逐字核验）；WorkBuddy 路径来自博文（F-029）并经 WorkBuddy 官方文档能力核验（F-038）。

## 前置条件

- 一个支持 Agent Skills（SKILL.md 形态）的编码 Agent，如 Claude Code、Codex、WorkBuddy 等；
- 本机有 Node.js / npx 环境（`npx skills` 分发器）；
- WorkBuddy 用户另需客户端与可用的连接器配置（见方式 C）。

## 方式 A：npx 命令安装（官方，通用）

官方仓库给出的命令（F-026，与官方博客逐字一致）：

```bash
npx skills add humanlayer/skills --skill show-me
```

在目标 Agent 的技能安装入口/终端执行即可；该命令在官方博客正文与结尾共出现两次，是官方指定的通用安装方式（F-031）。

> 注：本次转化未直取仓库内 SKILL.md 的目录路径（F-039），实际安装落点以 npx 分发器与各 Agent 的技能目录约定为准。

## 三种调用方式

安装后任选其一（F-027/F-028/F-035）：

```text
# 1) 斜杠命令直接调用
/show-me

# 2) 自然语言要求使用该 Skill
请使用 show-me skill 解释一下这个流程
# 官方英文话术示例：this is too much content. show me.

# 3) 内容特别复杂时，要求生成 HTML 讲解页
/show-me as an html explainer
```

调用时可以把目标明确指向某个对象（F-035，官方建议）：

- 一个路由 / 服务 / 功能模块；
- 一个 pull request 或当前改动（大 diff 回顾）；
- 当前讨论的主题；
- 或仅用于让模型把刚才的问题/陈述重新结构化表述一遍。

## 方式 B：让 Agent 自己找并安装（WorkBuddy 极简路径）

博文给出的免命令路径（F-029）：直接对 WorkBuddy 说让它去搜索 "show me" 这个 Skill 并完成安装。WorkBuddy 的 Skill 体系以 SKILL.md 为定义、支持项目级 `.codebuddy/skills/` 与用户级目录（F-038），Agent 可自行发现并使用已安装技能。

## 方式 C：WorkBuddy + GitHub 连接器（博文推荐的高效率路径）

1. 在 WorkBuddy 中开启 **GitHub 连接器**（WorkBuddy 连接器列表包含 GitHub，F-038）；
2. 让 WorkBuddy 通过连接器搜索 `humanlayer/skills` 仓库中的 show-me；
3. 确认安装后，在输入框用 `/show-me` 触发——WorkBuddy 输入框支持斜杠命令补全（与 CodeBuddy Code 一致，F-038）。

## 一次自测：复刻博文的最小验证

不依赖剪视频场景，用任意复杂主题验证安装是否生效：

1. 先问一个容易得到长文回答的问题（如"解释一下这个服务的请求生命周期/这个模块的调用关系"），记录默认回答形态；
2. 同一问题追加 `/show-me`，对比输出是否切换为图/树/表等紧凑视觉结构（官方预期：Mermaid 状态图/序列图、组件树、调用栈等，见 [01-visual-vocabulary.md](../concepts/01-visual-vocabulary.md)）；
3. 再试 `/show-me as an html explainer`：HumanLayer 产品内回复可直接内嵌 HTML；其他环境把生成的 HTML 文件在浏览器中打开（F-036）。

## 避坑提示

- **小事别调用**：改标题、写小函数、问命令类单点任务无需画图（F-024，作者经验）；
- **图要可审查**：优先让 Agent 输出 Mermaid/diff 等文本化图（可 diff、可复制复核），截图形态不可 diff、出错更难发现；
- **HTML 渲染差异**：只有 HumanLayer 自家产品支持回复内嵌 HTML，其他编码 Agent 以浏览器打开为准（F-036）；
- **命令时效**：`npx skills` 生态与 Skill 仓库结构可能迭代，若命令失效以 HumanLayer 官方博客/仓库最新说明为准（本包 stale_after: 2026-12-31）。
