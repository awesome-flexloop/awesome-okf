---
type: Log
title: 知乎数据开放平台教程更新日志
description: zhihu-open-platform 知识包的创建与变更记录
tags: [zhihu, open-platform, 更新日志]
generated: { by: "process:seven-concepts-cmd+official-docs-to-okf-wiki", at: "2026-10-23T00:00:00+08:00" }
status: stable
stale_after: 2027-04-23
---

# 更新日志

## 2026-10-23

### 创建

- 新建 `zhihu-open-platform` bundle，基于知乎数据开放平台官方文档 **31 篇全量正文**精读生成
- 创建 10 篇概念文档、5 篇示例文档、2 篇参考文档
- 独立成束而非并入既有 `zhihu-cli` 束：后者主线是 **Zhihu CLI 命令行工具**（235 条事实、55 项 P0），本束主线是 **官方 API 文档全集**（120 条官方事实）。两束并存不混写，已在束根与 `references/source-map.md` 写明边界与引用纪律

### 结构

- `concepts/`：00-platform-overview、01-auth-and-quota、02-search-and-hotlist、03-zhida、04-question-discovery、05-creator-capability、06-knowledge-base、07-document-tools、08-user-data-oauth、09-integration-surfaces
- `examples/`：01-first-call-workflow、02-knowledge-rag-workflow、03-creator-analytics-workflow、04-document-tool-workflow、05-quota-governance
- `references/`：source-map（官方 31 篇 ↔ 本束 17 页双向映射三表 + 采集方式 + 与 zhihu-cli 束边界）、facts（F-001~F-120 事实底账 + 11 条文档缺口登记）
- `log.md`：本文件
- 三级目录各配 `index.md` 导航页，与同级束一致

### 采集方式

- 官方文档站为前端渲染 SPA，HTML 无正文；先从前端分块逆向定位到正文数据接口 `GET https://developer.zhihu.com/console/api/v3/docs`，其返回目录树节点携带 `key`/`title`/`type`/`content`/`children`
- 由该接口一次取回 10 栏目 / 31 篇正文（合计约 8.7 万字符），逐篇精读后登记事实；采集日期 2026-10-23
- 全程未使用知乎 Skill CLI 的业务命令：本次是**文档知识沉淀**而非在线数据调用，CLI 首检需用户授权安装，且官方文档 API 已是更完整的一手信源

### 事实校订与缺口处置

- F-001~F-120 连续无缺号，每条标注来源 key 与原文依据位置
- 官方明确未给出的信息不猜测，统一登记在 `references/facts.md`「文档缺口登记」共 **11 条**（接口超时秒数、接口级 QPS、三个 user 接口的 `Limit` 上限、`global_search` 翻页入参、Skill 页错误码、`created` 字段单位、`zhida-agent` 上下文传参、价格表与 APIID 映射、「获取用户信息」接口规格、`expires_in` 之外的刷新撤销、检索片段数上限）
- 命名体例差异不做统一化改写：知识库侧 PascalCase（`KnowledgeBaseID`/`RecallContentID`）与小工具侧 snake_case（`file_id`/`task_id`）并存，按官方原样登记

### 索引对账

- `jishu/ai/frameworks/ai-agent/index.md`：束数 57 → 58，导航表与 toctree 同步新增，正文内容统计 423 → 441 文档（278 概念 + 81 示例 + 80 信源）
- `jishu/ai/frameworks/index.md`：束数同步 +1
- `jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`：ai 域与总索引束数同步，五面对账通过
- 质量门：`check-toctrees.py` 本束 **0 问题**；`check-bundles-index.py` 通过；`check-utf8.py` 通过

### 并发纪律

- 本束提交时仓库工作树存在他会话未提交 WIP（official-skills 束、kanshan-workbench 束、zhihu-ai-science-workshop 束及 4 个共享索引文件），其中 `doc/bundles/index.md`、`jishu/ai/index.md`、`jishu/index.md` 的增量行与本束增量**会落在同一行**
- 提交走 **crafted blob 路线**：暂存区 = HEAD + 仅本束增量，工作区保留混合态供他方自行提交；不对共享索引文件执行 `git add` 整文件
- 计数口径以纯净树实测值为准，不采信工作区混合值
