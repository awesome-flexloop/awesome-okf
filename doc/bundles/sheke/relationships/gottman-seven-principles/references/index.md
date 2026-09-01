# 信源文档索引

本目录登记知识包所依据的信源与延伸材料。所有关键事实均以脚注（footnote，行内标记形如 `[^editions]`）在概念文档中逐处归因，frontmatter 的 `sources` 字段与脚注标签一一对应。

| 序号 | 文档 | 内容 |
|------|------|------|
| 01 | [版本信息](01-editions.md) | 英文三版（1999 精装 / 2000 Three Rivers 平装 / 2015 Harmony 修订版）与四个中文译本（2003 四川人民、2010 万卷、2014 浙江人民、2024 浙江科技）的出版信息、ISBN 与正规获取渠道 |
| 02 | [延伸阅读与学界讨论](02-further-reading.md) | 戈特曼著作体系、健康关系之屋与戈特曼方法疗法、Levenson 合作与 SPAFF 学术脉络、Heyman & Smith Slep (2001) 交叉验证批评 |

## 信源使用说明

- 概念/实践文档 frontmatter 的 `sources[].resource` 字段有三种指向：
  1. 外部信源直链（如 `https://www.gottman.com/...`）；
  2. bundle 相对绝对路径（如 `/references/01-editions.md`）；
  3. 标准相对路径（如 `../concepts/00-gottman-love-lab.md`）。
- 正文中关键事实以 Markdown 脚注 `[^id]` 标注，脚注定义位于每篇文档末尾，`id` 与 `sources[].id` 对应。
- 本知识包的事实底账为 [facts.md](../facts.md)（45 条，含全部信源编号与 URL）；引用本包数据时请回到该文件核对口径。
- 所有信源均为公开可访问的正规渠道（研究机构官网、出版社页面、大学图书馆馆藏、PubMed Central、正版图书平台条目），不含任何盗版资源链接。

## 信源可信度说明

- **官方/一手**：戈特曼研究所官网（gottman.com）、戈特曼个人站（johngottman.net）、Penguin Random House 出版社页面、大学图书馆馆藏版权页；
- **同行评审**：Heyman & Smith Slep (2001, JMF)、Gottman et al. (1998, JMF)；
- **二手综述**：psychology.com、therapyexplained、heyberries 等临床/科普站点，仅用于辅助交叉印证，不作为孤证；
- **中文出版信息**：豆瓣读书正版条目、头条百科、图书 CIP 数据页。

```{toctree}
:hidden:
:maxdepth: 7

01-editions
02-further-reading
```