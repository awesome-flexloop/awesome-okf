# 更新日志

## 2026-08-30

### 创建

- 生成《周易参同契》阅读教程知识包（status: draft，OKF v0.2）。R 事实采集、I 洞察与前 4 篇概念文档、2 篇信源文档先行完成；本次 E 阶段补齐缺失文件并覆盖束首页桩文件。

### 结构

- concepts/：6 篇概念文档（00 为什么读、01 文本与作者、02 易理框架、03 炼丹内容、04 核心段落选读、05 现代化学视角），sources 双引（original-sources + modern-scholarship）。
- examples/：2 篇示例（01 鼎器歌六步精读法、02 注本选用与阅读路线）。
- references/：2 篇信源登记（original-sources 3 项：ctext 彭晓分章本 O-1、朱熹《考异》O-2、彭晓《通真义》O-3；modern-scholarship 6 项：Golden Elixir/Pregadio M-1 至 M-5、PMC 汞制剂综述 M-6）+ 信源索引页。
- facts.md：40 条事实（F-001—F-040），分七类（作者成书、文本结构、易理框架、炼丹内容、注本诠释史、现代化学与毒理、信源与对照）。
- insights.md：4 条四元组洞察（理论化姿态；火候时间编码；中西整合/拆解对照；外丹内丹诠释层累），附知识地图与学习路径。

### 本次补齐的文件

- 新建 [concepts/04-key-passages.md](concepts/04-key-passages.md)：乾坤开篇（F-013）、河上姹女（F-019）、偃月炉（F-017、F-021）三段选文，每段含注释、自撰今译、现代解读与脚注归因。
- 新建 [concepts/05-modern-chemistry-lens.md](concepts/05-modern-chemistry-lens.md)：炼丹设备与升华冷凝、火候时间编码、HgS⇌Hg 体系（F-031）、胡粉还铅（F-035）等经验成就；象征体系非因果理论、服食外推、汞铅中毒风险（F-032、F-033）等局限；与波义耳束及 baopuzi/tiangong-kaiwu 束对照。
- 新建 [examples/01-furnace-passage-reading.md](examples/01-furnace-passage-reading.md)：鼎器歌（F-024，54 字）六步精读。
- 新建 [examples/02-reading-route.md](examples/02-reading-route.md)：注本分级、ctext 在线原文使用法（含 CAPTCHA 提示，F-040）、三阶段计划、姊妹束配合阅读。
- 新建 [examples/index.md](examples/index.md) 与本日志。
- 覆盖 [index.md](index.md) 桩文件：保留桩 frontmatter 字段（type: OKF、title/description/tags、version "1.0.0"、source、generated、status: draft、stale_after、okf_version "0.2"，不写 verified），正文按 OKF 束首页范式重写（快速导航、快速开始、Bundle 定位、推荐学习路径、隐藏 toctree）。

### 方法说明

- 古文引文均取自 ctext 彭晓分章 35 章本（O-1），保留繁体用字，每段 ≤80 字并标注章名；今译全部自撰并标注"今译"，未照抄现代版权注本译文；Pregadio 英文译文只转述大意。
- 化学方程式：HgS + O₂ → Hg + SO₂（焙烧析汞）；Hg + S → HgS（汞硫化合）。
- 立场：经验成就与理论局限并陈；全部文档含安全警示，丹方严禁仿制服食。
- 链接：束内使用相对路径；束间链接指向 ../baopuzi/、../tiangong-kaiwu/、../boyle-sceptical-chymist/ 等已存在知识束；道家思想背景指向 ../../../think/laozi/boshu-reading/（束根）或 ../../../../think/laozi/boshu-reading/（concepts/、examples/ 目录）。
