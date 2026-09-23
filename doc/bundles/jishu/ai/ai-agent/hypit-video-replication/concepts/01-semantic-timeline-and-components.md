---
type: Concept
title: "语义时间线与组件化编排"
description: "解释词级锚定、语义事件和可替换组件如何让视频结构随新内容重排。"
tags: ["Hypit", "SVML", "语义时间线", "组件化"]
generated: { by: "reference_agent", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: skill
    resource: https://raw.githubusercontent.com/hypit-ai/hypit/main/skills/hypit/SKILL.md
---

# 语义时间线与组件化

## 时间不要只绑定秒数

固定时间码的问题是：配音变长、翻译变短或删掉一段内容后，原来位于 `00:09:12` 的字幕仍会停在旧位置。Hypit 的官方描述强调以 words 而不是 seconds 作为锚点（F-005）。

更稳的做法是把关系写成：

```text
某个视觉元素 -> 响应某个词、Selection、Moment 或 Segment
```

当脚本和语音改变时，系统重新计算词级时间，绑定关系仍然成立。

## 组件边界

官方 Skill 将视觉系统拆成可独立维护的组件，并要求组件拥有清晰责任和可参数化的输入（F-021、F-022）。常见组件包括：

- 字幕与 Karaoke 高亮；
- 排行榜、评论贴纸和 CTA；
- A-roll、B-roll 与人物/产品卡；
- 屏幕特效、转场和音效；
- 代码渲染的图形或动效。

组件化的价值不在于“把文件拆得更碎”，而在于让替换动作局部化：换主持人时不应重写字幕；换产品时不应破坏镜头节奏。

## 语义关系的四种提问

对参考视频逐项问：

1. 这个 cut 响应了哪句话或哪种状态？
2. 这个 picture 解释了哪个词或比较？
3. 这个 reveal 是答案、结果还是 CTA？
4. 这个 sound 是由动作、节拍还是语义事件触发？

这组问题来自官方 Skill 对 clone 过程的要求（F-022），也可作为人工复核清单。
