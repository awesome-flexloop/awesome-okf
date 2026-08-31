---
type: Reference
title: 在线门户导航
description: Project Gutenberg、Internet Archive、美国国会图书馆、HathiTrust、UPenn、Wikisource、Nobel、SEP、爱因斯坦全集等物理经典在线获取门户的使用要点
tags: [reference, 在线门户, Gutenberg, Internet Archive, 数字图书馆]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T10:30:00+08:00" }
verified: { by: "process:seven-concepts-r", at: "2026-08-30T10:30:00+08:00" }
status: stable
stale_after: 2027-08-30
sources:
  - id: facts
    resource: /facts.md
    title: 事实清单（URL 核验表）
  - id: primary
    resource: /references/01-primary-sources.md
    title: 核心元典原文信源总表
---

# 在线门户导航

本页登记获取物理学经典原文的主要门户，含每个门户的收录范围、使用要点与本 bundle 实测条目。URL 实测状态见 [事实清单 URL 核验表](../facts.md)。

## 一、公有领域全文门户

### Project Gutenberg（gutenberg.org）

- **收录范围**：美国公有领域电子书，提供 HTML/EPUB/Kindle/纯文本，部分含 TeX 源。
- **使用要点**：著录页明确标注版权状态（"Public domain in the USA"）；同一著作可能有多个条目（原文版与译本分开）；搜索时用英文原名或作者拉丁名。
- **本 bundle 实测条目**：[#28233 牛顿拉丁原版](https://www.gutenberg.org/ebooks/28233)、[#76404 牛顿 Motte 英译](https://www.gutenberg.org/ebooks/76404)、[#66944 相对论论文集（Saha/Bose 译）](https://www.gutenberg.org/ebooks/66944)、[#72787 玻尔三部曲](https://www.gutenberg.org/ebooks/72787)。

### Internet Archive（archive.org）

- **收录范围**：全球图书馆扫描件，含 Google 扫描、DLI（印度数字图书馆）扫描与用户上传件；提供借阅（lending）与下载两种模式。
- **使用要点**：① 条目页版权字段可能标 "NOT_IN_COPYRIGHT"（可全文下载）或仅可借阅；② 用户上传件的 CC 许可是上传者声明，不等于原著/译本版权状态（典型：玻尔兹曼 Brush 译本件标 CC BY-NC-ND，但译本 1964 年出版，在版权）；③ 扫描件保留原书页码，引用标页码；④ 部分条目对自动化抓取不友好（超时），可改用浏览器或镜像。
- **本 bundle 实测条目**：[吉布斯 1902](https://archive.org/details/elementaryprinc00gibbgoog)、[伽利略 1914 译本](https://archive.org/details/in.ernet.dli.2015.203974)、[薛定谔 1928 英译本](https://archive.org/details/in.ernet.dli.2015.211600)、[玻尔兹曼 Brush 译本（在版权）](https://archive.org/details/lectures-on-gas-theory-ludwig-boltzmann)、[朗道十卷合集（在版权）](https://archive.org/details/landau-and-lifshitz-physics-textbooks-series)、[van der Waerden 汇编（在版权）](https://archive.org/details/SourcesOfQuantumMechanics)。

### 美国国会图书馆数字馆藏（loc.gov）

- **收录范围**：LoC 藏书的官方数字化，著录权威（含 LCCN、索书号）。
- **使用要点**：扫描质量高、元数据最可靠，适合核对版本信息；PDF 为图像型。
- **本 bundle 实测条目**：[麦克斯韦《电磁通论》1873 两卷本](https://www.loc.gov/item/03015568/)。

### HathiTrust 数字图书馆（hathitrust.org）

- **收录范围**：研究图书馆联盟扫描件，著录规范（Record 编号）。
- **使用要点**：美国境内可阅公有领域全文，其他地区多为著录检索；著录页适合核对版本与馆藏。
- **相关记录**：Motte 1729 英译本 Record 009343903（经 [UPenn 聚合页](https://onlinebooks.library.upenn.edu/) 登记）；薛定谔英译本 Record 001477728。

### Wikisource（wikisource.org）

- **收录范围**：志愿者校对的公版全文，多语言版本并列。
- **使用要点**：适合检索单篇论文（如麦克斯韦 1865、爱因斯坦 1905 英译）；文本为 HTML 重排，不保留原页码，学术引用以扫描件为准。

## 二、机构权威门户

### 爱因斯坦全集数字版（einsteinpapers.press.princeton.edu）

- **收录范围**：普林斯顿大学出版社《爱因斯坦全集》德文原文与英译对照，含编者注。
- **使用要点**：旧卷次 URL（如 `/vol2-trans/`、`/vol6-trans/`）免费开放；Einstein Portal 订阅数据库预告 2026-09-30 上线（截至 2026-08 核验旧站仍为唯一全文入口）；旧卷次入口免费。引用文档用 Doc 编号（如 Doc 30）。
- **实测**：[vol2-trans（1900-1909）](https://einsteinpapers.press.princeton.edu/vol2-trans/)、[vol6-trans（1914-1917）](https://einsteinpapers.press.princeton.edu/vol6-trans/)。

### NobelPrize.org

- **收录范围**：历年诺奖获奖演讲、传略与颁奖词全文/PDF。
- **使用要点**：演讲文本为官方版本，© Nobel Foundation，个人学习可免费阅读；本 bundle 用于狄拉克 1933、费曼 1965 演讲定位。

### 大学课程与专题站点

- **弗吉尼亚大学 Galileo and Einstein**（galileoandeinstein.physics.virginia.edu）：M. Fowler 维护，含《两门新科学》Crew-de Salvio 译本 HTML 全文与物理史讲义。
- **匹兹堡大学 Norton 课程页**（sites.pitt.edu/~jdnorton/）：HPS 课程提供相对论原始论文 PDF 与导读。
- **Caltech 费曼讲义**（feynmanlectures.caltech.edu）：官方授权免费全文；站点启用 Cloudflare 验证，浏览器访问正常。
- **俄罗斯科学院 IHEP**（web.ihep.su/dbserv/compas/）：量子力学经典论文摘引库。

## 三、导航与检索策略

1. **找公版全文**：先查 Gutenberg（精校文本）→ 再查 archive.org/LOC（扫描件）→ UPenn Online Books Page 做主题聚合导航。
2. **核对版本**：以 LOC 著录、HathiTrust Record、出版社页为准；archive.org 条目标题中的 "00gibbgoog" 类后缀为索书号片段，可用于追溯馆藏。
3. **找在版权书**：用 archive.org 借阅、图书馆馆配、出版社官方在线版（如费曼讲义）；不要依赖用户上传件的 CC 标注判断版权。
4. **找中译本**：查北京大学出版社"科学元典丛书"、高等教育出版社、上海科学技术出版社、科学出版社官网与 ISBN 检索。
5. **自动化抓取受限的站点**（Cloudflare/超时）：改用浏览器访问，或用同书的替代信源（如费曼讲义用出版社页做中译本核验、用 Nobel 演讲做费曼文本定位）。