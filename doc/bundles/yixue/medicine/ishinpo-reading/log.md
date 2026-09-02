---
type: OKF
title: 《医心方》阅读教程·工作日志
description: 本知识包的创建与维护日志
tags: [log, ishinpo, 医心方]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-31T18:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-31T18:30:00+08:00" }
status: stable
stale_after: 2027-08-31
okf_version: "0.2"
---

# 工作日志

## 2026-09-02

### 视觉增强（事实内容零变更）
- 新增 9 张 AI 生成水墨意境插图：束首页 index.md（hero-heian-scroll-library）、概念 00-05（lost-scroll-fragments-rejoined、tanba-yasuyori-writing-scroll、qing-scholar-reconstructing-fragments、manuscripts-crossing-the-sea、edo-igakkan-scholars-collating、modern-desk-collated-editions）与示例 01-02（close-reading-with-vermilion-brush、reading-path-unrolling-scrolls）；图片存放于 doc/_static/bundles/yixue/medicine/ishinpo-reading/images/，以站点绝对路径 /_static/bundles/yixue/medicine/ishinpo-reading/images/ 引用，统一配图注"AI 生成意境图，非历史图像，仅作阅读氛围辅助"；插图位置均在各页开篇引言之后、第一个小节之前，风格统一为暖米色宣纸底、水墨淡彩、古典书斋氛围。
- 新增 5 张 Mermaid 图表：概念 01（三十卷结构分组图）、概念 02（亡佚→保存→辑佚链路图）、概念 03（版本流传谱系图）、概念 04（研究史时间线图）、示例 02（四阶段阅读路线图）；图表事实锚定本束 facts.md，遵循 Mermaid 安全编码规则（节点标签引号包裹、边标签 `-->|"标签"|` 无空格、无特殊字符）。
- 以上均为视觉增强：正文事实文字、交叉链接、frontmatter、toctree、表格与引用块零变更。

## 2026-08-31

- 创建知识包：基于 Web 公开信源三路并行调研（本体/亡佚引书/版本研究史），按 seven-concepts 场景 4（知识沉淀）链路 R→I→E→V 产出
- 结构对齐 `think/yangsheng/yangsheng-classics-reading` 范本
- 调研中间产物存 SpecWeave `.temp/`，完成后清理
- 信源分歧处理原则：诸说并存处并列标注不裁断（撰成年代 982/984、御本下赐年代、引书数 204/280、现存写本数 52/53 等）
- facts.md 登记零推测事实 79 条（信源 URL 逐条内嵌）；insights.md 四元组洞察 4 条；概念文档 6 篇；示例文档 2 篇；信源登记 3 篇
