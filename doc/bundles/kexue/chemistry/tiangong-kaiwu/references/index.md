# 信源参考索引

本目录登记"《天工开物》阅读教程"所依据的文献信源，供概念文档溯源引用。

| 信源文件 | 内容 | 对应文档类型 |
|---------|------|------------|
| [original-sources.md](original-sources.md) | 公版原文：古诗文网《天工开物》全书目录与序、作咸、冶铸、锤锻、燔石、五金、丹青各卷全文（8 项，2026-08-30 实测可达） | 一级文献 |
| [modern-scholarship.md](modern-scholarship.md) | 现代研究：忠县临江二队明代炼锌遗址考古报道 3 篇（中新网/中国文化报、光明日报、人民网/重庆日报）、百科线索 1 项，及现代整理本与李约瑟著作书目信息 | 二级文献/书目线索 |

## 信源使用说明

- 概念文档与示例文档通过 frontmatter 的 `sources` 字段双引两个信源文件，引用格式为 bundle 相对绝对路径（`/references/xxx.md`）。
- 古文引文以 [original-sources.md](original-sources.md) 登记的公版在线原文为准，每段短引不超过 80 字并标注卷名；**今译全部自撰**，不引用任何现代版权译注。
- 现代解读（炼锌化学、考古印证、中西对照）以 [modern-scholarship.md](modern-scholarship.md) 登记的考古报道为依据；现代译注仅登记书目信息作阅读线索。
- 事实登记见 [../facts.md](../facts.md)（F-001—F-042）；未能通过实测的资源在两个信源文件末尾"未能登记的资源"节说明。

```{toctree}
:hidden:
:maxdepth: 7

original-sources
modern-scholarship
```
