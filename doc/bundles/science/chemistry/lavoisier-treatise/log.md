# 更新日志

## 2026-08-30

### 创建

- 新建拉瓦锡《化学基础论》阅读教程知识包（OKF v0.2，status: draft）
- 完成 R 阶段事实采集：下载 Project Gutenberg 公版全文（1789 法文原版 eBook #52489、1790 克尔英译本 eBook #30775）做本地全文检索核校；9 个信源 URL 经 WebFetch 实测可达后登记
- 完成 I 阶段洞察萃取：4 条四元组洞察（定量方法、元素操作定义、命名法先行、热质说残留）
- 完成 E 阶段批量生成：facts（48 条）、insights、概念文档 6 篇、示例 2 篇、信源 2 篇

### 结构

- 束目录：`doc/bundles/science/chemistry/lavoisier-treatise/`
- 概念 6 篇：00 为什么读 / 01 化学革命与燃素说危机 / 02 氧化学说 / 03 质量守恒与定量方法 / 04 命名法与元素表 / 05 关键段落精读
- 示例 2 篇：燃烧段落逐句精读 / 三档阅读路线
- 信源 2 篇：公版原始文献（4 条）/ 现代研究资料（5 条）

### 核校记录

- 原著引句逐字核校：质量守恒名言（英法双版）、葡萄汁化学方程式、元素定义、燃烧定义、Condillac 引文、1787 命名法记载、33 项元素表四类构成、汞煅烧 12 天实验数据、水 85/15 重量比、hydrogène 词源、英法版出版页
- 未通过实测的 URL（fr.wikisource、en.wikisource、archive.org 1789 扫描件）一律未登记；以 Gutenberg 英法双版作为公版原文主信源

### 会话

- session：sc-20260830-lavoisier-okf
- 方法论：seven-concepts（R 事实采集 → I 洞察 → E 萃取）
- 生产者：agent:seven-concepts-r-e