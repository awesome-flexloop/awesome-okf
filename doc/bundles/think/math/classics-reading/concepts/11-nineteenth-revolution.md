---
type: Concept
title: 19 世纪革命——非欧几何、黎曼、伽罗瓦
description: 19 世纪上半叶三大观念地震的思想解读：非欧几何（罗巴切夫斯基1829/鲍耶1832）打破平行公理、黎曼1854演讲发明流形与曲率、伽罗瓦理论以群置换方程可解性
tags: [concept, 19世纪, 非欧几何, 罗巴切夫斯基, 鲍耶, 黎曼, 流形, 伽罗瓦, 群论]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T11:04:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-30T11:04:00+08:00" }
status: draft
stale_after: 2027-08-30
sources:
  - id: original-sources
    resource: /references/original-sources.md
    title: 原著原文信源
  - id: translations-commentaries
    resource: /references/translations-commentaries.md
    title: 译本与注本信源
  - id: modern-expositions
    resource: /references/modern-expositions.md
    title: 现代解读信源
---

# 19 世纪革命：空间与方程的重新定义

1800 年前后，数学的对象还是"数"与"欧氏空间中的图形"；到 1860 年，空间有了多种几何，方程理论被群取代，函数与连续成为独立研究对象。本篇覆盖两场地震（第三场严格化见 [概念 12](12-rigor-and-foundations.md)）。

## 一、非欧几何：平行公理的倒塌

### 思想脉络

自欧几里得起，第五公设（平行公理）因不够"自明"引发 2000 年证明尝试。前驱 Saccheri（1697）、Lambert（1766）已从否定公设推出大批"怪异"定理却未承认新几何；Playfair 公理（1795）给出通行等价表述。突破者三人：

1. **罗巴切夫斯基**（Nikolai Lobachevsky，1792–1856，喀山大学）：1829 年在俄文《Kazan Messenger》发表《On the Principles of Geometry》（首发于地方刊物，长期无人问津）；1840 年出德文专著《Geometrical Investigations on the Theory of Parallels》（61 页，思想的成熟表述）。
2. **鲍耶·亚诺什**（Janos Bolyai，1802–1860，匈牙利）：非欧几何作为其父著作《Tentamen》附录出版于 1832 年（通称 Appendix，24 页），自称"从虚无中创造了一个新世界"。
3. **高斯**：私下研究数十年，从未发表（称怕"波奥提亚人的叫嚷"），仅在书信中肯定鲍耶与罗巴切夫斯基。

核心构造：在双曲几何（罗氏几何）中，过直线外一点可作无穷多条平行线，三角形内角和小于 180°，相似形必全等。

### 黎曼的重构

**黎曼就职演讲**（1854 年 6 月 10 日，格丁根，题为《论作为几何基础的假设》）把问题从"第五公设是否成立"提升到"空间本身有哪些可能"：n 维流形（Mannigfaltigkeit）作为一般研究对象；度规由局部二次型给出；曲率张量刻画几何（二维曲率 1 个数、三维 6 个、四维 20 个）。双曲几何（负曲率）、欧氏（零曲率）、椭圆/球面几何（正曲率，1868 年演讲出版后由 Beltrami、Helmholtz 等扩展）成为同一理论的特例。演讲身后出版，Clifford 英译载《Nature》8（1873）pp.14–17、36–37（PDF：emis.de/classics）。

### 三要素

- 罗巴切夫斯基：1840 德文版扫描见 Internet Archive；Halsted 英译（1892）；Bonola《非欧几何》（1906）Carslaw 英译（Open Court 1912，Dover 重印）附录含罗氏 1840 与鲍耶 1832 两家译文，一卷在手。
- 黎曼：Clifford 英译 PDF 免费；德文全集 Springer 版权。
- 解读：Bonola 书本身就是最佳史书；MacTutor 三人传记；SEP"non-Euclidean geometry"条。

### 读法要点

- 罗氏 1840 小书（61 页）极清晰，从"平行线"新定义一步步推，适合直接读。
- 黎曼演讲是哲学-数学文本，论证概念化而非公式化，慢读；配 Bonola 最后一章。

## 二、伽罗瓦：方程理论的终结与开端

### 思想事件

五次方程求根公式问题：1799 年鲁菲尼、1824 年阿贝尔证明一般五次方程无根式解（阿贝尔 1826 自费出版）。伽罗瓦（Evariste Galois，1811-10-25 生）回答了更深刻的问题：**哪些方程可根式求解？** 他的答案：把方程每个根的置换（permutation）组成群（group），方程可根式解当且仅当其群可解（可分解为阿贝尔群链）。方程问题转化为群结构问题——现代代数的研究对象（群、域、环）由此浮现。

### 传奇版本史（本身是方法论教材）

- Premier Memoire 1831 年 1 月提交法国科学院，Poisson 与 Lacroix 评审后退稿（评语"不可理解"）；
- 1832 年 5 月 29 日（决斗前夜）致 Chevalier 绝笔信，匆忙概述全部理论，9 月发表于百科评论杂志；
- 1832 年 5 月 30 日决斗、31 日卒，年仅 20 岁；
- 手稿沉睡 14 年，Liouville 1846 年在《Journal de Mathematiques Pures et Appliquees》第 11 卷 pp.381–444 出版并加注，数学界才消化其思想；
- 权威本：Bourgne & Azra《Ecrits et memoires...》（Gauthier-Villars 1962，法文全集定本）；Peter M. Neumann《The Mathematical Writings of Evariste Galois》（EMS 2011，英法双语，当代标准）；Edwards《Galois Theory》（Springer 1984）含 Premier Memoire 英译与逐节讲解，入门最佳。
- IHP 书目页：galois.ihp.fr。

### 读法要点

- 不要从原文直接读群论！先学现代群论基础（任何近世代数教材：群、正规子群、商群），再读 Edwards 的英译与讲解，最后看 Neumann 双语本核对。
- 绝笔信是理解伽罗瓦"问题观"的最好文本（短）。
- 与高斯《算术研究》第七节对读：分圆方程可解性正是伽罗瓦理论的第一个应用范例。

## 三、两场革命的共同结构

| | 非欧几何 | 伽罗瓦理论 |
|---|---|---|
| 被放弃的旧假设 | 平行公理（空间唯一） | 求根公式（方程用根式解） |
| 新对象 | 流形、曲率 | 群、域 |
| 方法特征 | 把"必然真理"降为"一种可能" | 把"解方程"转为"研究结构" |
| 后续 | 黎曼几何 → 爱因斯坦广义相对论 | 抽象代数 → 20 世纪数学主语 |

两场革命都完成了同一种动作：**从研究对象内部的性质，转向研究对象之间的结构关系**。这是 19 世纪数学的总转向。

## 初学者建议

非欧线：罗氏 1840（Halsted/Bonola 附录，61 页）→ Bonola 史书 → 黎曼演讲（慢读）。伽罗瓦线：现代近世代数教材群论章 → Edwards 书逐节 → Neumann 本绝笔信。两条线都建议在有微积分与线性代数基础后再进入。

相关概念：[世纪之交：高斯](10-gauss-turn.md) · [严格化与基础](12-rigor-and-foundations.md) · [20 世纪公理化](13-twentieth-foundations.md)