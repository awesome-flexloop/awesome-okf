# 更新日志

## 2026-08-31

### 创建

- 新建 OKF 知识包 `kexue/physics/quantum-papers-reading`：量子力学论文精读。
- 完成 R 阶段信源核验：四篇论文（玻尔 1913、海森堡 1925、薛定谔 1926、狄拉克 1928）的期刊卷期页码与 PD 状态，与姊妹束 facts 交叉核对，登记 20 条事实。
- 产出方法论 2 篇（concepts/）、逐节精读 4 篇（examples/）、信源文档 2 篇（references/）。

### 结构

- concepts/：00 量子论文精读方法论、01 矩阵与波动力学形式对照。
- examples/：玻尔 Part I（英）、海森堡 1925（德）、薛定谔 1926 第一篇（德）、狄拉克 1928（英）。
- references/：01 论文原文信源表、02 译本与辅助资源。
- facts.md：20 条编号事实；insights.md：3 条四元组洞察。

### 方法

- 按 seven-concepts-cmd 方法论执行（session: sc-20260831-physics-okf）。
- 版权合规：van der Waerden 1967 汇编（在版权）零引用；四篇原文均为美国 PD。

### 对抗审查（2026-08-31）

- 物理准确性：期刊卷期页码与姊妹束 facts 交叉核对一致（抽查 Planck h=6.55e-27、Bose DOI、Weinberg PRL 19:1264、de Broglie 1924-11-25 答辩日）。
- 引文真实性：4 处转写大意引文（惠更斯拉丁、普朗克 §1 德文、爱因斯坦 1905 同时性句、吉布斯系综定义）已补注「大意转写非逐字」，零虚构引文。
- frontmatter：10 个 examples 文件 description 弯引号导致的 Malformed YAML 已修复（单引号标量包裹），Sphinx dummy 构建零警告。
- 版权合规：在版权译本（Princeton 惠更斯选译、UBC 普朗克英译、Brush 1964、van der Waerden 1967）零引用。
