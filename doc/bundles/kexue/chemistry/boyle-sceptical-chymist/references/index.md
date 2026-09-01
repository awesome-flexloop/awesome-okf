# 信源参考索引

本目录登记"波义耳《怀疑的化学家》阅读教程"所依据的文献信源，供概念文档溯源引用。所有外部 URL 均于 2026-08-30 实测可达。

| 信源文件 | 内容 | 对应文档类型 |
|---------|------|------------|
| [original-sources.md](original-sources.md) | 公版原文：1661 年初版（Project Gutenberg 转录本）、1680 年第二版扫描（Internet Archive）、原著书目与中译本信息 | 一级文献（原著） |
| [modern-scholarship.md](modern-scholarship.md) | 权威解读：大英百科（Principe 撰）、斯坦福哲学百科、Giunta 经典化学选读、JRSM 同行评议论文、Principe 炼金术考证 | 二级文献（研究） |

## 信源使用说明

- 概念文档通过 frontmatter 的 `sources` 字段引用信源，引用格式使用 bundle 相对绝对路径（`/references/xxx.md`）。
- 正文中的关键事实以 Markdown 脚注（`[^1]` 形式）逐处归因，脚注文末集中列出，指向信源文档或实测 URL。
- 原著为公版（17 世纪出版），英文引文每段不超过 40 词并标注出处；现代中译本为版权出版物，本知识包不引用其译文，所有今译均为自撰。
- 百科条目仅作线索，关键事实均经两条以上独立信源交叉验证。

```{toctree}
:hidden:
:maxdepth: 7

modern-scholarship
original-sources
```