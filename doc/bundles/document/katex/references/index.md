# KaTeX 信源登记簿

本目录登记本知识包所有内容据以派生的 KaTeX 信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源条目或外部 URL。

* [KaTeX 源码信源](katex-source.md) — KaTeX v0.18.4 源码仓库（https://github.com/KaTeX/KaTeX）与核心文件索引，覆盖 src/ 主目录、functions/、environments/、contrib/、metrics/ 等，含官网页面对应关系。所有架构机制（Lexer、MacroExpander、Parser、buildTree、domTree、defineFunction 等）溯源至此。
* [KaTeX 官网信源](katex-website.md) — 官网 17 个公开页面登记：首页、Users、Versions、Node、Browser、API、CLI、Auto-render、Extensions & Libraries、Options、Security、Handling Errors、Font、Supported Functions、Support Table、Common Issues、Migration。每页含稳定 ID（如 `web-options`、`web-cli`）、URL、标题、用途与引用提示，是所有配置默认值、安装方式、安全指引的权威信源。

```{toctree}
:hidden:
:maxdepth: 7

katex-source
katex-website
```
