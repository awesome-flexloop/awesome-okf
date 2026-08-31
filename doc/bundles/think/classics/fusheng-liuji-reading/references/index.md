
# 信源参考索引

本目录登记《浮生六记》阅读教程所依据的文献信源，供概念文档与示例文档溯源引用。

| 信源文件 | 内容 | 对应文档类型 |
|---------|------|------------|
| [01-primary-editions.md](01-primary-editions.md) | 原典稿本、清代至民国刊本、现代整理本与公有领域全文获取途径 | 一级文献 |
| [02-scholarship.md](02-scholarship.md) | 版本与辨伪考证、文学与思想研究、普及导读三类研究文献 | 二级文献 |
| [03-translations.md](03-translations.md) | 林语堂英译及多语种译本、海外传播与中文版本谱系 | 二级文献 |
| [04-adaptations.md](04-adaptations.md) | 语文教材、戏曲影视、绘画网络与生活美学衍生传播 | 二级/三级文献 |

## 信源使用说明

- 概念文档与示例文档通过 frontmatter 的 `sources` 字段引用信源
- 引用格式使用 bundle-relative 绝对路径（`/references/xxx.md`）
- 各信源文档中的条目按"作者/题名/载体/要点"或表格形式登记，便于读者直接查阅
- 《浮生六记》为清代公有领域文本，原典全文可在公开古籍站点查阅

```{toctree}
:hidden:
:maxdepth: 7

01-primary-editions
02-scholarship
03-translations
04-adaptations
```