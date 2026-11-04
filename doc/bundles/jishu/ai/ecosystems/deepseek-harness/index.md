---
okf_version: "0.2"
type: bundle
title: "DeepSeek Harness 与创造模式"
description: "Harness 与 Creator Mode 中文教程：插件化工作台、五案例解读、倒计时练习、权限与热更新、官方能力核验；保留历史文章快照，案例待独立复现。"
source: references/source-manifest.md
total_bundles: 1
total_content_docs: 14
total_md_files: 19
generated: { by: "process:seven-concepts-cmd+wechat-public-okf", at: "2026-11-04T10:18:07+08:00" }
status: draft
tags: [DeepSeek, Harness, AI-Coding, Desktop-App, Agent, Codex, PTC, Minimal, Creator]
stale_after: 2026-12-04
sources:
  - id: wx-creator
    resource: https://mp.weixin.qq.com/s/pslQaWATxQDlhBBAZROEwg
    title: DeepSeek 再放大招，上线 Creator Mode。
    author: 沉默王二
    last_modified: 2026-11-03
  - id: official-home
    resource: https://deepseek.com/harness/en/
  - id: official-start
    resource: https://deepseek-harness.github.io/deepseek-harness/en/guide/quickstart
  - id: official-publish
    resource: https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish
  - id: wx-pjfnnu
    resource: https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw
    title: DeepSeek Harness 2.0 来了，Codex 该退休
    author: 有限进步Seven
    last_modified: 2026-10-05
---

# DeepSeek Harness 与创造模式

官方将 Creator 定位为保留 Standard 能力、支持运行时检查、插件试验及自定义预设创作的模式。[F-055](references/creator-mode-facts.md) 公众号作者将其用于五种 UI 插件，本次按 R→I→E→V 学习链整理为原创教程。

**当前状态为 draft。** 官方能力已有文档支持，五个案例仍是作者单源演示，没有本次独立执行。原文 13 张图片未逐图核读，精确工具契约与权限条件仍有缺口。官方仍称 developer preview；旧文章标题中的“2.0”不作为官方版本号。[核验记录](references/verification.md)

已完成四视角内容审查与修正回归，包内事实编号、元数据、编码、计数、本地链接和导航静态检查通过。外部事实没有全部逐字独立回验，案例与跨领域迁移没有实测，不能把静态验收当成运行或生产准入证明。

## 推荐学习路径

| 步骤 | 内容 | 阅读后能判断什么 |
|---|---|---|
| 1 | [创造模式与插件化工作台](concepts/creator-mode.md) | 模型、Harness、插件、bundle 与 profile 的分工 |
| 2 | [从一个倒计时插件开始](examples/creator-first-plugin.md) | 如何预览、授权、测试和恢复 |
| 3 | [五案例设计与证据](concepts/creator-case-studies.md) | 倒计时、主题、Transformer、建筑、体素海岛的需求与结果差异 |
| 4 | [权限、热更新与恢复](concepts/creator-safety-and-lifecycle.md) | 如何核对安装、激活、配置覆盖与清理 |
| 5 | [知识地图与迁移方法](concepts/knowledge-map.md) | 三条分析性洞察与单案例待验证模式 |

## 信源与历史内容

[来源台账](references/source-manifest.md)记录账号、公开性及官方页面；[49 条新事实](references/creator-mode-facts.md)使用 F-017 至 F-065；[覆盖索引](references/article-source.md)与事实编号机械对齐。

旧内容见[概念索引](concepts/index.md)及[练习索引](examples/index.md)，原事实 F-001 至 F-016 保留不重排。旧定价、Automation 与旧示例不在本次全面复验范围内，不据此采购或判断当前能力。

本次扩展已有知识包，不增加全库束数。没有提交、推送、插件安装、权限切换或付费模型调用。版本与权限类内容在 2026-12-04 前复核。

## 关联阅读

- [Harness 框架源码教程](../../frameworks/ai-agent/deepseek-harness/index.md)：历史版本源码架构，不替代当前运行时契约。
- [Cordis 框架教程](../../frameworks/ai-agent/cordis/index.md)：依赖、服务与生命周期背景。
- [V4.1-Flash-1017 知识包](../../practice/deepseek-v41-flash-1017/index.md)：模型更新专题，与本文插件使用分工不同。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
