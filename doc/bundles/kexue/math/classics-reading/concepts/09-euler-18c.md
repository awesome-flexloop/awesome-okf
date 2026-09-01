---
type: Concept
title: 18 世纪分析——欧拉
description: 欧拉三部曲《无穷分析引论》（1748）、《微分学原理》（1755）、《积分学原理》（1768–70）的思想解读：函数中心论、记号体系、形式化方法与分析的扩张
tags: [concept, 18世纪, 欧拉, 无穷分析引论, 微分学, 积分学, 函数, 分析学]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T10:56:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-30T10:56:00+08:00" }
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

# 18 世纪分析：欧拉三部曲

莱布尼茨的微积分在 17 世纪末还是一套几何问题的技巧；欧拉（Leonhard Euler，1707–1783）通过三部曲把它改造为关于**函数**的一般科学，并配齐沿用至今的记号体系。他是全部经典中对现代读者最友好的一位：记号几乎无需翻译。

## 一、《无穷分析引论》（Introductio，E101，1748 两卷）

### 核心思想

本书是"微积分预备知识"的奠基，实际完成了分析学的研究对象转换：

1. **函数（functio）成为中心概念**：变量与常量通过解析表达式组成的量。从曲线到函数的转向，使分析脱离几何独立。
2. **初等函数的系统展开**：指数函数（通过 eˣ 与极限 lim(1+x/n)ⁿ 定义）、对数、三角函数以级数方式统一处理；著名的 e^{iπ}+1=0 关系（1748 年以文字形式给出，e^{ix}=cos x+i sin x）在本书成形。
3. **幂级数作为通用工具**：大量函数被展成级数，形式运算（换元、相乘、待定系数）自由使用——18 世纪的"形式化"风格：算法有效先于严格性。
4. 卷二是解析几何：圆锥曲线与一般曲线的方程分类（笛卡尔纲领的完成）。

## 二、《微分学原理》（Institutiones calculi differentialis，E212，1755）

### 核心思想

- 以函数为对象系统讲授微分：微分定义为"增量的比的极限值"（欧拉使用 evanescent increment 的比值论证——极限观念的早期形态，但未达到 19 世纪严格性）。
- 全书 27 章覆盖：微分法则、高阶微分、级数展开、极值、泰勒公式、差分、微分在数论与几何中的应用。
- Blanton 英译本（Springer 2000）仅译前 9 章；Ian Bruce 网络全译免费。

## 三、《积分学原理》（Institutiones calculi integralis，三卷，1768–1770）

### 核心思想

- 积分作为微分的逆运算被系统组织：换元、分部、有理函数部分分式、级数积分。
- 卷二卷三是**微分方程**的第一次系统处理：一阶常微分方程分类、奇解、二阶方程（含后来的"欧拉方程"）——这是欧拉把微积分从方法推进为学科的关键部分。
- 成书于欧拉视力渐失期（1771 年完全失明），口述完成，展示了他惊人的形式演算能力。

## 三要素

| 书 | 原文入口 | 译本 |
|----|----------|------|
| E101 引论（1748） | Gallica 原版 bpt6k33510；Opera Omnia 影印 bpt6k69587（Ser.1 Vol.8） | Blanton 英译 Springer 1988/1990（版权）；Ian Bruce 全译（免费，17centurymaths.com） |
| E212 微分（1755） | Euler Archive 条目 E212 | Blanton 译前 9 章（Springer 2000）；Bruce 全译 |
| 积分学（1768–70） | Internet Archive（id: institutionescal020326mbp）；Google Books 1768（id: Vg8OAAAAQAAJ） | Ian Bruce 全译；Opera Omnia Ser.1 Vol.11–13 |

解读资源：Sandifer《How Euler Did It》专栏（eulerarchive.maa.org/hedi，每篇重走一个欧拉论证，最佳配套）；Euler Archive 以 Enestrom 编号索引全部著作（E101/E212 等）；Opera Omnia 由瑞士欧拉委员会与 Birkhauser 自 1911 年出版，四系列 86 卷。

## 读法要点

1. **从 E101 开始**，不要从微积分教材顺序硬套：第 1–8 章（函数、多项式因式分解、级数展开）直接可读。
2. **配 Sandifer 专栏做"三遍读法"**：选一篇专栏，先自己读对应 Euler 原文段落，再看 Sandifer 重走。
3. **注意形式化风格的边界**：欧拉对发散级数、无穷小的操作在当时未受严格检验——这些"大胆"正是 19 世纪严格化运动的靶子（柯西、阿贝尔的批评与重构，见 [概念 12](12-rigor-and-foundations.md)）。读时标记"这里如果换我用现代定义会怎么说"。
4. 记号亲切但术语需留意：欧拉的"连续"含义比现代宽；级数收敛讨论分散。

## 谱系定位

```
莱布尼茨算法（1684）→ 伯努利兄弟发展 → 欧拉三部曲：分析成为独立学科
   → 18 世纪算法扩张（拉格朗日、拉普拉斯）
   → 19 世纪严格化（柯西 1821、魏尔斯特拉斯 epsilon-delta）
```

欧拉的形式化直觉走在严格化前面约 80 年；他的结果几乎全部正确，论证方式后来被重写。

## 初学者建议

第一周：E101 第 4 章（e 的定义）+ Sandifer 对应专栏 2 篇；第一个月：E101 前 8 章 + 微分学前 5 章（Bruce 英译免费）。用 SymPy 验证级数展开（见库内 [SymPy 知识包](../../../../jishu/data/pydata/sympy/index.md)）是低成本的正反馈循环。

相关概念：[17 世纪革命](08-early-modern-17c.md) · [世纪之交：高斯](10-gauss-turn.md) · [严格化与基础](12-rigor-and-foundations.md)