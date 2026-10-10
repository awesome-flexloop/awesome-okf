---
okf_version: "0.2"
type: Concept
title: "特性与 STE 写作检查"
description: "自动布局、错误自愈提示、双主题 + 明暗模式、STE 受控语言写作检查（源自 ASD-STE100）、单文件无依赖交付"
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

# 特性与 STE 写作检查

## 自动布局，不画图也不错位

组件自动布局：流程图 / 时序图 / 树 / 时间线等都由 CLI 排版，Agent 不需要手画坐标也不会有「错位」问题（F-012）。

## 写错了会自己告诉你怎么改

草稿里的语法错误，CLI 报出**行号、组件名**，还会附带一个**正确示例**。Agent 看到报错通常一轮就能修好（F-013）。

## 双主题 + 明暗模式

- **Blueprint** 主题：工程蓝图风（白底、蓝色线条）；
- **shadcn** 主题：干净的卡片风。
- 每主题支持 `light` / `dark` / `auto` 三种颜色模式切换。
- 页面右上角按钮可直接切换，也可在草稿 frontmatter 写 `theme: blueprint` 覆盖默认。

> ⚠️ 仓库 README（权威源）当前默认 `theme: auto`（长文用 paper、图表用 blueprint），并另支持 `paper` 与自定义主题；博文所述「默认 blueprint」为版本演进前的口径，见[勘误](04-modes-gotchas.md)。

## STE 写作检查

STE 是 Field of analogical 灵感来源（README 指出来自 **ASD-STE100**，航空维护手册使用的受控英语）。项目把「能被机器检查」的 STE 规则翻译成**中英文规则集**，每次渲染都会跑一遍（F-014）：

- **句长约束**：英文 ≤20 词、中文 ≤35 字；描述 ≤25 词 / 45 字；单段落 ≤6 句；
- **常用词偏好**：用 `use` 不用 `utilize`；中文用「优化」不用「进行优化」；
- **模糊词与错别字**：中文错别字、模糊词（尽快、若干、大概、多次）、以及「以上 / 以下 / 以内」与数字连用时的歧义；
- **套话与腔调**：英文被动语态、中文一句里三个以上「的」、「赋能」「闭环」等套话。
- **模式**：默认 `warn`（只提示不改内容）；设成 `strict` 会**拒绝渲染**。

## 单文件无依赖

生成出来的 `.html` 页面**不引用任何 CDN 或网络字体**，丢给别人双击就能开，方便上传内网或归档（F-015）；讲解视频页面则把音频内嵌、支持离线播放。

## 关键事实引用

特性细节对应 [信源事实清单](../references/article-source.md) F-012~F-015。