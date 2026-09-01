---
type: Example
title: 八周通读计划——从零到通读算经的路线图
description: 配套概念文档与七篇算题实战的八周自学计划，含每周原典阅读量、做题任务、自测清单与工具使用法
tags: [example, 阅读计划, 自学路线, 八周, 方法论]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-30T12:45:00+08:00" }
status: stable
stale_after: 2027-08-30
sources:
  - id: online-sources
    resource: /references/online-sources.md
    title: 在线原典信源
  - id: core-editions
    resource: /references/core-editions.md
    title: 核心点校本与出土文献
---

# 八周通读计划——从零到通读算经的路线图

## 前置准备

- **文本**：打开 ctext.org 的《孙子算经》《周髀算经》《九章算术》《海岛算经》全文（见 [references/online-sources.md](../references/online-sources.md)）；纸本备郭书春、刘钝《算经十书》（辽宁教育出版社 1998）或白尚恕《〈九章算术〉注释》。
- **工具**：纸和笔（布筹用表格代替即可）；可选 Python + SymPy 验算（参考 [references/cross-ref.md](../references/cross-ref.md)）。
- **时间**：每周约 4–5 小时（读原文 2h、做题 2h、读概念文档 1h）。

## 每周安排

| 周次 | 原典任务（在线全文） | 配套本包文档 | 做题产出 |
|------|--------------------|-------------|---------|
| 第 1 周 | 《孙子算经》上卷（记数、度量衡）+ 序 | [concepts/02](../concepts/02-chousuan-numeration.md)、[examples/05](05-wuwuzhishu-crt.md) | 用纵橫两式写出 3 个多位数；复算物不知数 |
| 第 2 周 | 《孙子算经》中卷选读 + 《周髀》商高、陈子篇 | [concepts/06](../concepts/06-zhoubi-suanjing.md)、[examples/04](04-gougu-pythagoras.md) | 画弦图证明勾股；复算 3-4-5 类测望题 2 道 |
| 第 3 周 | 《九章·方田》前 15 题 + 合分、减分、乘分诸术 | [concepts/03](../concepts/03-jiuzhang-structure.md)、[04](../concepts/04-jiuzhang-key-methods.md)、[examples/01](01-fangtian-fractions.md) | 复算分数题 5 道；用更相减损求 3 组最大公约数 |
| 第 4 周 | 《九章·粟米》今有术 + 《少广》开方术选读 | [concepts/04](../concepts/04-jiuzhang-key-methods.md) | 做今有术题 3 道；手写开平方程序求 $\sqrt{2}$ 到两位小数 |
| 第 5 周 | 《九章·盈不足》前 8 题 | [examples/02](02-yingbuzu-double-false.md) | 复算共买物题；把 1 道非线性盈不足题与现代插值对照 |
| 第 6 周 | 《九章·方程》前 5 题 + 正负术 | [examples/03](03-fangcheng-negative.md)、[concepts/02](../concepts/02-chousuan-numeration.md) | 布矩阵复算三禾题；自拟 1 题含负系数 |
| 第 7 周 | 刘徽注割圆术段落 + 《海岛算经》望海岛题 | [concepts/05](../concepts/05-liuhui-commentary.md)、[07](../concepts/07-suanjing-shishu.md)、[examples/07](07-geyuan-pi.md) | 倍边迭代到 48 觚；复算岛高四里五十五步 |
| 第 8 周 | 《张丘建·百鸡》+ 《数书九章》大衍类序选读；浏览《算法统宗》《几何原本》中译史料 | [examples/06](06-baiji-weng.md)、[concepts/09~11](../concepts/09-song-yuan-peak.md) | 复算百鸡三解；写一篇 500 字中西算法对照笔记 |

## 每周固定流程

1. **读原文**（2h）：先不看注，逐句读术文，把不懂的字词标出；
2. **做题**（2h）：照术文程序亲手演算当周题目，至少完整复算本包 examples 对应一篇；
3. **读注与解读**（1h）：读刘徽注或本包概念文档，核对自己的理解，修正对术文的误读；
4. **写术语卡片**（随做随记）：每张卡片记一个术语（如"实/法""齐同""直除"），写清程序含义与现代对应。

## 结营自测清单

- [ ] 能不看资料说出《九章》九章名目与各自主题；
- [ ] 能在纸上用纵橫筹式布列一个六位数；
- [ ] 能复算七道名题：合分、盈不足、三禾方程、句股求弦、物不知数、百鸡、割圆到 48 觚；
- [ ] 能讲清"方程术遍乘直除"与高斯消元的对应关系；
- [ ] 能说出大衍求一术与扩展欧几里得算法为何同构，以及秦九韶多做了哪一步（非互素化约）；
- [ ] 能讲清刘徽割圆术的误差界论证；
- [ ] 能就"算法传统与演绎传统"写出三点比较，且不使用"古已有之"式表述。

## 进阶方向

- 通读钱宝琮《中国数学史》或 Martzloff *A History of Chinese Mathematics*（书单见 [concepts/13](../concepts/13-reading-path.md)）；
- 专题：李冶《测圆海镜》圆城图式、朱世杰垛积术、和算对天元术的继承；
- 用代码把各"术"实现为可运行的算法库（盈不足、消元、求一术、增乘开方），对照 [data/pydata/sympy](../../../../jishu/data/pydata/sympy/index.md) 的现代实现。