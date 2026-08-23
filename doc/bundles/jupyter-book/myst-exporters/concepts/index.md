# myst-exporters 概念文档

按学习路径编号排列。建议从 [00 统一导出架构](00-exporter-architecture.md) 开始阅读。

| 编号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [统一导出架构](00-exporter-architecture.md) | Serializer+Handler 模式、unified Plugin 模式、输出类型 |
| 01 | [HTML 导出](01-html-export.md) | mdast→hast→rehype 管线、State 编号与引用解析 |
| 02 | [LaTeX 导出](02-latex-export.md) | TexSerializer、Handler 映射、Beamer 支持、导言区 |
| 03 | [PDF 导出](03-pdf-export.md) | LaTeX+latexmk 和 Typst 两条路径、模板整合 |
| 04 | [DOCX 导出](04-docx-export.md) | docx 库 Office XML、Node/Browser 双环境 |
| 05 | [JATS XML 导出](05-jats-export.md) | JatsSerializer 栈式架构、JatsDocument、引用提取 |
| 06 | [Markdown 导出](06-markdown-export.md) | MdSerializer、MyST 角色/指令语法回环 |
| 07 | [Typst 导出](07-typst-export.md) | TypstSerializer、宏收集、与 LaTeX 对称 |
| 08 | [jtex 模板引擎](08-jtex-template-engine.md) | Nunjucks 渲染、imports 合并、模板目录结构 |
| 09 | [导入转换器](09-import-converters.md) | jats-to-myst、tex-to-myst 栈式解析器 |
