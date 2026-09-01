# 更新日志

## 2026-08-31

### 创建
- 初始化 mawangdui-fangzhong-reading bundle（spec：.trae/specs/standards-tools/create-mawangdui-fangzhong-wiki/）
- R 阶段：六维度系统调研（出土背景/文本群/核心概念/整理出版史/研究著作/传世文献关系），采集 127 条带信源事实（F-BG 18 / F-TXT 28 / F-CON 15 / F-PUB 25 / F-RES 25 / F-TR 16），信源登记 S1—S54，G1 质量门通过
- I 阶段：7 条四元组洞察（I-1 正统方技定位 / I-2 文献断层锚点 / I-3 四十年整理滞后 / I-4 七损八益校正传世注疏 / I-5 文献身份识别 / I-6 拟题真实性参差 / I-7 四条研究脉络生态），G2 质量门通过
- 创建 bundle 根 index.md、facts.md、insights.md、log.md 四个工作文档（concepts/、examples/、references/ 子目录文档由后续任务创建）

### 结构
- index.md：OKF v0.2 frontmatter（type OKF、status draft、stale_after 2027-08-31）+ 内容边界声明 + 📚快速导航 + 🚀分读者路径 + 🎯定位对比表（与 classics-reading 通览教程、fangzhong-bajia-reading 八家研读教程分工）+ 📖推荐学习路径 + hidden toctree
- facts.md：127 条事实按六板块分组制表，编号与信源编号保留，文末附 S1—S54 信源登记表；【待核验】条目（F-TXT-024、F-TXT-028）原样保留
- insights.md：7 条四元组洞察 + 知识地图（mermaid）
- log.md：本文件

### 调研来源摘要
- 本地 OKF 知识库：think/sexology/classics-reading（facts.md、references/ancient-china-sources.md、concepts/01-ancient-china.md）作为既有事实底座（信源 S28）
- 机构与博物馆信源：湖南博物院马王堆帛书集粹专题与"天书"揭秘文（S1、S8）、北京中医药大学中医药博物馆（S6）、湖南中医药大学新闻（S5）
- 整理出版信源：复旦古文字中心《集成》修订本出版信息（S10）、中华读书报 2014 年报道（S11）、中华书局悼念裘锡圭文（S54）
- 研究著作信源：李零《中国方术考》第七章全文（S9）、北大中文系李零个人页（S13）、朱越利简历与论文（S46—S49）、李建民中研院页与著作（S44、S50—S53）、周贻谋百科词条与《马王堆医书考注》书影（S33、S34）
- 海外汉学信源：Donald Harper 译著全文（S12）、Vivienne Lo 书评（S29）、Pfister 论文与手册条目（S22、S40）、Li Yunxin 论文（S23）、名和敏光日本研究近况（S41）、东方书店丛书馆藏目录（S42、S43）
- 补充调研（2026-08-31）：新增 29 条事实（F-TXT-021~028、F-PUB-018~025、F-RES-013~025）与信源 S33—S54，覆盖周贻谋著作、各篇拟题问题、日本东方书店译注丛书、朱越利与李建民研究

### 方法说明
- 七概念链路：场景4 知识沉淀 R（调研）→ I（洞察）→ E（落地本 bundle）→ V（独立对抗评审）→ C（文件落盘收尾）
- 事实描述纯客观登记，不含因果推断词；争议条目（墓主身份、帛书种数口径、《集成》篇数 54/56、竹简定名异说）如实并列两说
- 未获权威信源确认者（F-TXT-024《黄帝问于左神》异名、F-TXT-028 篇数口径差异）保留【待核验】标注，未作断言
- 原文引用遵守学术引介尺度：仅引篇名、核心命题与少量代表性短句，无露骨描写