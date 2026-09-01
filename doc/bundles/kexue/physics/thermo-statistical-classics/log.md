# 更新日志

## 2026-08-31

### 创建

- 新建 OKF 知识包 `kexue/physics/thermo-statistical-classics`：热统经典精读。
- 完成 R 阶段信源核验：卡诺 1824、玻尔兹曼 1872、吉布斯 1902 的原文版次与获取渠道，登记 17 条事实（与姊妹束交叉核对）。
- 产出方法论 2 篇（concepts/）、逐节精读 3 篇（examples/）、信源文档 2 篇（references/）。

### 结构

- concepts/：00 热统经典精读方法论（概念负载/佯谬定位）、01 概率论与统计语言（术语还原）。
- examples/：卡诺 1824 循环论证、玻尔兹曼 1872 H 定理、吉布斯 1902 系综方法。
- references/：01 热统经典信源表、02 解读与译本资源。
- facts.md：17 条编号事实；insights.md：3 条四元组洞察。

### 方法

- 按 seven-concepts-cmd 方法论执行（session: sc-20260831-physics-okf）。
- 版权合规：三部原文均为美国 PD；Brush 1964 译本（在版权）零引用。

### 对抗审查（2026-08-31）

- 物理准确性：期刊卷期页码与姊妹束 facts 交叉核对一致（抽查 Planck h=6.55e-27、Bose DOI、Weinberg PRL 19:1264、de Broglie 1924-11-25 答辩日）。
- 引文真实性：4 处转写大意引文（惠更斯拉丁、普朗克 §1 德文、爱因斯坦 1905 同时性句、吉布斯系综定义）已补注「大意转写非逐字」，零虚构引文。
- frontmatter：10 个 examples 文件 description 弯引号导致的 Malformed YAML 已修复（单引号标量包裹），Sphinx dummy 构建零警告。
- 版权合规：在版权译本（Princeton 惠更斯选译、UBC 普朗克英译、Brush 1964、van der Waerden 1967）零引用。
