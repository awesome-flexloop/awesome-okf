# 更新日志

## 2026-08-31

### 创建

- 新建 OKF 知识包 `kexue/physics/physics-original-text-reading`：物理学经典原文精读。
- 完成 R 阶段信源核验：6 部精读著作（惠更斯 1673、法拉第 1831/1849、卡诺 1824、普朗克 1901、爱因斯坦 1905、吉布斯 1902）的 PD 底本与扫描件，登记 28 条事实（F-001~F-028）与 9 行 URL 核验表。
- 产出方法论 4 篇（concepts/）、逐段精读示范 6 篇（examples/）、信源文档 2 篇（references/）。

### 结构

- concepts/：00 精读三步法总纲、01 原文校勘、02 符号现代还原、03 历史定位。
- examples/：惠更斯（拉丁）、法拉第（英）、卡诺（法/英）、普朗克（德）、爱因斯坦（德/英）、吉布斯（英）六种语言文体示范。
- references/：01 精读著作原文信源表、02 引用许可与中译示范规则。
- facts.md：28 条编号事实，G1 质量门验证 0 因果词。
- insights.md：3 条四元组洞察 + 语言×文体知识地图。

### 方法

- 按 seven-concepts-cmd 方法论执行 R→I→E→V→C 链路（session: sc-20260831-physics-okf）。
- 版权合规：6 部精读底本全为美国 PD（1929 年前出版）；在版权译本（Princeton 惠更斯选译、UBC 普朗克英译、现代中译本）零引用；中译示范全部原创。

### 对抗审查（2026-08-31）

- 物理准确性：期刊卷期页码与姊妹束 facts 交叉核对一致（抽查 Planck h=6.55e-27、Bose DOI、Weinberg PRL 19:1264、de Broglie 1924-11-25 答辩日）。
- 引文真实性：4 处转写大意引文（惠更斯拉丁、普朗克 §1 德文、爱因斯坦 1905 同时性句、吉布斯系综定义）已补注「大意转写非逐字」，零虚构引文。
- frontmatter：10 个 examples 文件 description 弯引号导致的 Malformed YAML 已修复（单引号标量包裹），Sphinx dummy 构建零警告。
- 版权合规：在版权译本（Princeton 惠更斯选译、UBC 普朗克英译、Brush 1964、van der Waerden 1967）零引用。
