---
okf_version: "0.2"
type: bundle
title: 书童 Pagekin 小说创作与人工审校教程
description: 公开文章经维护者文档核验转化，学习章节上下文、差异修稿、写作规则、模型接入与数据边界；不是源码或长篇效果实测
tags: [Pagekin, 小说写作, 章节蓝图, 上下文, 人工审校, Ollama]
source: https://mp.weixin.qq.com/s/fctK1OqGC9UBm__dHXXIJA
sources:
  - id: article
    resource: https://mp.weixin.qq.com/s/fctK1OqGC9UBm__dHXXIJA
  - id: official
    resource: https://www.orz.md/ai-novel-writer/
  - id: demo
    resource: https://www.orz.md/ai-novel-writer/demo/
  - id: blueprint
    resource: https://www.orz.md/ai-novel-writer/chapter-blueprint/
  - id: ollama
    resource: https://docs.ollama.com/api/openai-compatibility
generated: { by: "assistant/okf-wiki", at: "2026-11-04" }
status: flagged
stale_after: 2026-12-31
---

# 书童 Pagekin 小说创作与人工审校教程

**“100 章不丢伏笔”尚无独立效果证据，知识包保留 flagged。** 官网、历史演示和开发者自荐均由同一维护者发布，不能算独立效果验证。本轮未安装程序、未查上游源码、未执行模型调用。

Pagekin 把设定、角色、大纲、章节蓝图与稿件组织在同一个项目中。维护者说明模型需自行配置、作品保存在本机、云端生成另行计费且发送有关正文和设定（F-003、F-005、F-028、F-031）。事实出处统一见[编号台账](references/article-source.md)。

## 从哪里开始

| 文档 | 学到什么 |
|---|---|
| [概念教程](concepts/index.md) | 产品分工、上下文与连续性、审稿修稿、Skill、参考导入及模型数据 |
| [使用与学习练习](examples/index.md) | 官方操作记录改写的初次使用，以及不依赖模型的原创蓝图练习 |
| [信源与核验](references/index.md) | 单篇来源、44 条编号、逐项核验、勘误、洞察与模式 |
| [更新与审查记录](log.md) | 执行边界、独立审查和真实门禁结果 |

希望先理解方法，可从[手工蓝图练习](examples/02-blueprint-and-continuity.md)开始；准备使用软件时，先阅读[模型与数据](concepts/03-models-and-data.md)，再核对[桌面流程](examples/01-first-session.md)。

## 已知边界

- 原文章为“开源星探”2026-11-01 公开产品介绍，非维护者公告；标题 Star 和增长数字未核查。
- 官网标注 v1.3.2，审稿历史记录为 v1.3.0；不声称 v1.3.2 是访问日最新 Release。
- GPL-3.0 仅得到维护者声明对应，未读 LICENSE；Node/pnpm、Skill 不执行脚本、向量检索与 WebDAV 等未查实现。
- 云模型可能收费并接收相关稿件；本机保存和本地推理不应混同。API Key 在本机配置文件，不声称已加密。
- 演示范围不证明整本小说质量、生成速度、版权合规或商业收益。迁移模式仅为候选，实践验证和跨领域复用均为零。

`flagged` 是本工作流的扩展警示状态，消费者按草稿谨慎使用；复核待承接项见[核验表](references/verification.md)。到 `stale_after` 当日仍未复核则视为过期，不自动延长。

## 主题关联

[InkOS](../inkos/index.md)是同属 AI 小说创作工具的另一知识包，关注该系统自身的 Agent 与记忆组织。此处只提供延伸入口，不据本轮材料比较两款工具的效果、许可证或自动化质量。

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
examples/index
references/index
log
```
