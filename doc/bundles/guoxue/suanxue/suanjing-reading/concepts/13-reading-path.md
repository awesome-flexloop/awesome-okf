---
type: Concept
title: 阅读路径与书单
description: 中国数学典籍的三级书单（入门译注、点校本、研究文献）、在线全文资源使用法，以及配合算题实战的四周阅读路线
tags: [concept, 阅读路径, 书单, 学习方法, 点校本]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-30T12:05:00+08:00" }
status: stable
stale_after: 2027-08-30
sources:
  - id: core-editions
    resource: /references/core-editions.md
    title: 核心点校本与出土文献
  - id: online-sources
    resource: /references/online-sources.md
    title: 在线原典信源
  - id: modern-studies
    resource: /references/modern-studies.md
    title: 现代学术研究文献
---

# 阅读路径与书单

## 三条阅读原则

1. **动手算**：算经是算法书，每个"术"至少布筹（或用笔写表格）演算一遍。纸笔即可，进阶可用 SymPy 验证（见 [references/cross-ref.md](../references/cross-ref.md)）。
2. **原文与解读并读**：先读点校本原文一段，再读译注或现代研究；直接读白话转述会丢失术文的程序结构。
3. **古今对照标边界**：每个现代等价物都写明"同在哪、异在哪"（参照 [12](12-chinese-math-characteristics.md) 的比较表与 [insights 洞察 4](../insights.md)）。

## 第一级：入门（原文 + 现代汉语对照）

| 书 | 用途 |
|----|------|
| 郭书春、刘钝校点《算经十书》，辽宁教育出版社 1998（e-guo-1998，ISBN 9787538251111） | 十书全文点校，繁体横排，入门首选通读本 |
| 白尚恕《〈九章算术〉注释》，科学出版社 1983（e-bai-1983） | 九章逐题白话注释，适合第一遍精读九章 |
| ctext.org 四部算经全文（s-ctext-jiuzhang 等，见 [online-sources](../references/online-sources.md)） | 免费全文 + 影印底本对照，检索方便 |

## 第二级：进阶（点校整理本）

| 书 | 用途 |
|----|------|
| 钱宝琮校点《算经十书》，中华书局 1963（e-qian） | 现代校勘奠基本，附考据，读注文与异文用 |
| 李继闵《九章算术校证》，陕西科技出版社 1993（e-li-1993） | 九章文本校勘集大成 |
| 郭书春主编《中国科学技术典籍通汇·数学卷》（全五册），河南教育出版社 1993（e-guo-tonghui） | 从汉到清主要算书的影印点校汇编，专题查阅 |
| 张家山汉简《算数书》、岳麓秦简《数》整理本（e-zhujian） | 出土文献，理解九章前驱形态 |

## 第三级：研究（学术专著）

| 书 | 用途 |
|----|------|
| 钱宝琮主编《中国数学史》，科学出版社 1964（r-qian-history） | 中文标准通史 |
| 吴文俊主编《中国数学史大系》，北京师范大学出版社 1998–2004（r-wu-daxi） | 多卷本通史，资料详 |
| J.-C. Martzloff, *A History of Chinese Mathematics*, Springer 1997（r-martzloff-1997） | 面向西方读者的审慎通史，优先权表述可直接引用 |
| K. Chemla & Guo Shuchun, *Les Neuf Chapitres*, Dunod 2004（r-chemla-2004） | 九章全文法译与数学思想研究，对"术"的结构分析最深入 |
| V. Katz ed., *The Mathematics of Egypt, Mesopotamia, China, India, and Islam*, Princeton 2007（r-katz-2007） | 比较视野下的中算章节（Dauben 执笔） |
| J. Needham, *Science and Civilisation in China*, Vol.3, Cambridge 1959（r-needham） | 文明史框架中的中算定位 |

## 在线资源使用法

- **ctext.org**：`/nine-chapters`、`/zhou-bi-suan-jing`、`/hai-dao-suan-jing`、`/sunzi-suan-jing` 有全文；影印底本（《四部丛刊》等）以 res 编号链接，引用时可直接定位，见 [online-sources](../references/online-sources.md) 的 res 编号表。
- **汉典古籍、中华文库、国学大师**：提供赵爽/甄鸾注本、排印点校本等不同版本，适合对校。
- **维基文库、维基百科**：作为导航入口与延伸阅读，具体引文以点校本或 ctext 全文为准。

## 四周阅读路线（配合 examples/）

| 周 | 原典 | 本包配套 |
|----|------|---------|
| 第 1 周 | 《孙子算经》全三卷（短、浅）+《周髀》商高篇 | [examples/05](../examples/05-wuwuzhishu-crt.md)、[concepts 06](06-zhoubi-suanjing.md) |
| 第 2 周 | 《九章》方田、粟米、衰分章 | [examples/01](../examples/01-fangtian-fractions.md)、[concepts 02–04](02-chousuan-numeration.md) |
| 第 3 周 | 《九章》盈不足、方程、句股章 | [examples/02](../examples/02-yingbuzu-double-false.md)、[03](../examples/03-fangcheng-negative.md)、[04](../examples/04-gougu-pythagoras.md) |
| 第 4 周 | 《海岛算经》九题 + 《数书九章》大衍类选读 | [examples/07](../examples/07-geyuan-pi.md)、[concepts 05、10](05-liuhui-commentary.md) |

详细日程与自测题见 [examples/08 阅读计划](../examples/08-reading-plan.md)。

## 延伸阅读

- [examples 索引](../examples/index.md)
- [references 索引](../references/index.md)