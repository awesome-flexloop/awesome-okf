# 信源参考索引

本目录登记"帛书《老子》阅读教程"所依据的文献信源，供概念文档溯源引用。

| 信源文件 | 内容 | 对应文档类型 |
|---------|------|------------|
| [core-manuscripts.md](core-manuscripts.md) | 出土原典（帛书甲乙本、郭店楚简、北大汉简）及权威整理本 | 一级文献 |
| [modern-studies.md](modern-studies.md) | 现代注本与普及读物（陈鼓应、高明、秦复观等） | 二级文献 |
| [historical-commentaries.md](historical-commentaries.md) | 历代注本（严遵至民国，含分级阅读表） | 二级/三级文献 |
| [lineage-cross-ref.md](lineage-cross-ref.md) | 关联知识包交叉引用与外部在线资源 | 元数据/导航 |

## 信源使用说明

- 概念文档通过 frontmatter 的 `sources` 字段引用信源
- 引用格式使用 bundle-relative 绝对路径（`/references/xxx.md`）
- 本地PDF文件路径在各信源文档中标注，便于读者直接查阅
- 关联的 laozi-lineage bundle（学术性版本源流）通过 lineage-cross-ref.md 交叉引用

```{toctree}
:hidden:

core-manuscripts
historical-commentaries
lineage-cross-ref
modern-studies
```
