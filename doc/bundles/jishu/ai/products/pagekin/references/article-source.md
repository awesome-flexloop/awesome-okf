---
type: Reference
title: Pagekin 编号事实与作者主张
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
  - id: developer-post
    resource: https://meta.appinn.net/t/topic/91203
status: flagged
stale_after: 2026-12-31
generated: { by: "assistant/okf-wiki", at: "2026-11-04" }
---

# Pagekin 编号事实与作者主张

F-001 至 F-044 连续登记，共 44 条。`page_fact` 表示页面可观察信息，`author_claim` 表示文章来源者的声明，`official_statement` 表示维护者或服务官方的声明；后两类均不自动升级为独立实验事实。执行者推论只放在[知识地图](knowledge-map.md)。

本文件是唯一事实台账；不另外复制一份 `facts.md`，以免双份登记漂移。全部编号的验证状态对应[核验表](verification.md)中的同一编号。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 页面标题包含“GitHub 2.1k Star”与“AI 写 100 章不丢伏笔” | page_fact | article | 标题 | observed |
| F-002 | 公众号与署名显示“开源星探”，时间为 2026-11-01 07:27 | page_fact | article | 页首 | observed |
| F-003 | 文章把 Pagekin 介绍为 EthanYoQ 开发的长篇小说与网文桌面工具 | author_claim | article | 开头 | official-corroborated |
| F-004 | 文章声明 GPL-3.0、2100+ Star，以及一个多月增加 1000+ | author_claim | article | 开头第二段 | mixed/unverified |
| F-005 | 文章列出前提、架构、蓝图、写稿、审稿、修稿、定稿流程 | author_claim | article | 开头流程 | official-corroborated |
| F-006 | 文章称生成过程由作者确认 | author_claim | article | 开头作者角色 | official-corroborated |
| F-007 | 文章称章级上下文包括本章蓝图、角色档案、世界观摘要、前文摘要及上一章全文 | author_claim | article | 核心亮点 1 | partially-corroborated |
| F-008 | 文章称前文摘要随写作更新 | author_claim | article | 核心亮点 1 | single-source |
| F-009 | 文章把上述设计描述为从根本上解决长篇记忆衰减，并称章数增加时上下文仍可控 | author_claim | article | 核心亮点 1 | flagged |
| F-010 | 文章描述先出审稿意见、选择意见、修稿、逐段对比确认 | author_claim | article | 核心亮点 2 | official-corroborated |
| F-011 | 文章声称不会一键覆盖原稿 | author_claim | article | 核心亮点 2 | qualified |
| F-012 | 文章称参考小说支持 txt、md、epub 导入与文风提取 | author_claim | article | 核心亮点 3 | partially-corroborated |
| F-013 | 文章称参考数据不会混进正文 | author_claim | article | 核心亮点 3 | single-source/flagged |
| F-014 | 文章称可导入原稿续写，也可选中段落续写 | author_claim | article | 核心亮点 3 | official-corroborated |
| F-015 | 文章称可从本机或 GitHub 导入写作 Skill，并绑定规划、写稿、审稿或修稿阶段 | author_claim | article | 核心亮点 4 | single-source |
| F-016 | 文章称只支持自包含 SKILL.md 提示词，不执行脚本或 hook | author_claim | article | 核心亮点 4 | single-source/flagged |
| F-017 | 文章称书房展示进度、字数、定稿数和角色数，并能跟踪主支线与伏笔 | author_claim | article | 核心亮点 5 | partially-corroborated |
| F-018 | 文章称支持版本历史、全文与向量检索、WebDAV 备份 | author_claim | article | 核心亮点 5 | partially-corroborated |
| F-019 | 文章列出 Windows x64、macOS arm64 与 x64 三种安装包 | author_claim | article | 下载安装 | official-corroborated |
| F-020 | 文章称 Windows 升级不删作品和设置，macOS 包 ad-hoc 签名且未公证 | author_claim | article | 下载安装 | partially-corroborated |
| F-021 | 文章称源码开发要求 Node.js 22.14+ 和指定 pnpm，示例为 frozen-lockfile 安装与 dev | author_claim | article | 源码构建 | single-source/unverified |
| F-022 | 文章称三平台包经 GitHub Actions 资格检查后发布同一 Release | author_claim | article | 源码构建末段 | single-source/unverified |
| F-023 | 文章称软件不自带模型，提供 OpenAI 兼容与 Gemini 原生协议 | author_claim | article | 配置模型 | official-corroborated |
| F-024 | 文章列出 DeepSeek、SiliconFlow、BigModel、OpenAI、xAI、Gemini、Ollama、NovelAI 与自定义预设 | author_claim | article | 服务商表 | partially-corroborated |
| F-025 | 文章为本地 Ollama 指定 OpenAI 兼容、127.0.0.1:11434/v1 和本机模型名，提醒勿填 /api | author_claim | article | Ollama 配置 | independently-corroborated |
| F-026 | 文章示例模型名为 qwen3:14b，并把本地模型使用描述为“完全免费” | author_claim | article | Ollama 配置 | qualified/unverified |
| F-027 | 官网称“书童 Pagekin（原 AI Novel Writer）”，显示 v1.3.2，并说明产品能力按该版 README 于 2026-10-25 核对 | official_statement | official | 页首与页尾 | observed/not-release-verified |
| F-028 | 官网称模型需自行配置，软件免费，云端调用费用另计 | official_statement | official | 页首与常见问答 | official-only |
| F-029 | 官网称围绕当前蓝图、相关角色、世界观与历史摘要组织上下文 | official_statement | official | 产品定位 | official-only |
| F-030 | 官网称审稿建议可选择，原稿与修稿可逐段比较 | official_statement | official | 核心能力 | official-only |
| F-031 | 官网称项目与 SQLite 数据库在本地，云模型会收到相关提示词和故事上下文 | official_statement | official | 模型与数据 | official-only |
| F-032 | 官网称 API Key 当前保存在本机用户目录的模型配置文件中 | official_statement | official | 模型与数据表 | official-only |
| F-033 | 官网称 Windows 包未代码签名，Mac 包未 Developer ID 签名且未公证 | official_statement | official | 安装方式 | official-only/not-binary-verified |
| F-034 | 官网明确不承诺任意第三方 API 只换 URL 与 Key 即可接入 | official_statement | official | 当前边界 | official-only |
| F-035 | 官网称不提供在线发布、阅读社区或云端模型账号 | official_statement | official | 当前边界 | official-only |
| F-036 | 官网称 DSH 插件是独立发布且冻结的开发预览，不替代桌面软件 | official_statement | official | 当前边界 | official-only |
| F-037 | 官网 v1.3.2 虚构示例规划 8 章、每章目标约 1200 字；故事前提、角色名单、世界观、情节大纲四节已确认，只展示第一章蓝图，正文待写，并声明不代表小说质量或生成速度测评 | official_statement | official | 当前图文演示 | observed/documentation-only |
| F-038 | 历史演示页标记 v1.3.0，32 秒为剪短等待后的影片长度，不是生成耗时 | official_statement | demo | 演示说明 | observed/documentation-only |
| F-039 | 历史审稿样例列 5 条意见并显示“复验：未验证”，选 4 条送修，差异页有用原稿、用修稿、手动编辑 | official_statement | demo | 历史审稿步骤 1 至 3 | observed/documentation-only |
| F-040 | 历史差异页演示“全部用修稿”和“完成合并”，合并后仍待定稿 | official_statement | demo | 历史审稿步骤 3 至 4 | observed/documentation-only |
| F-041 | 蓝图教程提供章节位置、本章目的、关键事件、悬念钩子字段，并说明是普通文本非一键导入包 | official_statement | blueprint | 模板与常见问题 | official-only |
| F-042 | Ollama 官方兼容文档的本地示例使用 localhost:11434/v1/，客户端 Key 值 required but ignored | official_statement | ollama | Local server usage | independent-official |
| F-043 | Ollama 官方文档声明支持 OpenAI API 的一个子集 | official_statement | ollama | 开头兼容声明 | independent-official |
| F-044 | 官网称支持参考文本、全文检索、风格提取以及批量章节创作与恢复 | official_statement | official | 核心能力 5 至 6 | official-only |
