# 信源参考索引

本目录登记《黄帝内经》阅读教程所依据的全部信源，供概念文档与精读示例溯源引用。

| 信源文件 | 内容 | 层级 |
|---------|------|------|
| [editions.md](editions.md) | 版本与底本链：《汉志》著录、王冰次注、林亿新校正、史崧献书、顾从德本/居敬堂本、人卫梅花本 | 一级/二级文献 |
| [commentaries.md](commentaries.md) | 历代注本与类分著作：王冰、杨上善、张介宾《类经》、李中梓《内经知要》、丹波父子《素问识》 | 二级文献 |
| [modern-studies.md](modern-studies.md) | 现代校注语译、院校教材（王洪图《内经选读》）与工具书（《黄帝内经词典》） | 二级/三级文献 |
| [electronic-sources.md](electronic-sources.md) | 电子文本信源分级：ctext 四部丛刊本、古诗文网、《素问悬解》《类经》全文站，含弃用信源警告 | 电子信源 |

## 信源使用说明

- 概念文档与精读示例通过 frontmatter 的 `sources` 字段引用本目录信源
- 八篇精读原文逐字转录自 ctext 四部丛刊本（繁体）或经多源交叉核对的简体网页，每段引文均在文中标注底本
- 现代白话译文受著作权保护，本 bundle 不复制；解读文字为编者自撰
- facts.md 中 S1–S13 信源编号与本目录文档对应

```{toctree}
:hidden:
:maxdepth: 7

editions
commentaries
modern-studies
electronic-sources
```