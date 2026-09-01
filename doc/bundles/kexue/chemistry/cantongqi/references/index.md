# 信源参考索引

本目录登记"《周易参同契》阅读教程"所依据的文献信源，供概念文档溯源引用。所有外部 URL 均于 2026-08-30 实测可达且内容相符。

| 信源文件 | 内容 | 对应文档类型 |
|---------|------|------------|
| [original-sources.md](original-sources.md) | 公版原文：ctext.org 藏彭晓分章 35 章本《周易参同契》全文、朱熹《周易参同契考异》、彭晓《周易参同契分章通真义》 | 一级文献（原著与古注） |
| [modern-scholarship.md](modern-scholarship.md) | 现代研究：Pregadio 主持 Golden Elixir 网站的《参同契》系列（索引、炼丹模型、魏伯阳传记、第一篇译注、专著书目）与 PMC 同行评议汞制剂论文 | 二级文献（研究与科学背景） |

## 信源使用说明

- 概念文档与实践示例通过 frontmatter 的 `sources` 字段引用信源，引用格式使用 bundle 相对绝对路径（`/references/xxx.md`）。
- 正文中的关键事实以 Markdown 脚注（`[^1]` 形式）逐处归因，脚注在文末集中列出，指向信源文档编号（O-x 为原文/古注，M-x 为现代研究）。
- 原著为公版（公元 2 世纪成篇），古文引文每段不超过 80 字并标注篇/章；引文保留 ctext 繁体用字，正文用简体。
- 所有白话今译均为自撰并明确标注，不照抄现代版权注本译文；Pregadio 英文译文只转述大意，不直接引用。
- 维基文库、维基百科、Internet Archive、大英百科、百度百科等线索在调研日或不可达、或返回反爬/403/404 页面，均未登记，详见 [modern-scholarship.md](modern-scholarship.md) "未采用的线索"一节。

```{toctree}
:hidden:
:maxdepth: 7

modern-scholarship
original-sources
```