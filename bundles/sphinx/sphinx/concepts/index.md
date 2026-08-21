# 概念文档（concepts/）

本目录包含25篇从入门到进阶的Sphinx概念文档，按学习路径分为五篇。

## 入门篇（00-02）

* [00. Sphinx 简介](00-introduction.md) — Sphinx是什么、核心能力、多格式输出、与其他文档工具对比。
* [01. 5分钟快速上手](01-getting-started.md) — 安装（pip/conda/Docker）、sphinx-quickstart初始化、sphinx-build构建、conf.py配置、Markdown支持、Python API快速体验。
* [02. 架构总览](02-architecture-overview.md) — Application-Centric架构、核心类关系图、初始化流程、构建管线（READING→WRITING→FINISHING）。

## 核心架构篇（03-08）

* [03. Sphinx应用类](03-application-class.md) — Sphinx主类详解：目录属性、build方法、扩展API（add_*/connect/emit）、TemplateBridge。
* [04. 配置系统](04-config-system.md) — _Opt配置选项、_ConfigRebuild重建级别、conf.py执行机制、add_config_value扩展API、ENUM枚举约束。
* [05. 事件系统](05-event-system.md) — EventManager订阅/发射、16个核心事件生命周期、priority优先级、connect/emit/emit_firstresult API。
* [06. 组件注册中心](06-registry.md) — SphinxComponentRegistry详解：builders/domains/directives/roles/transforms注册、load_extension扩展加载、entry points发现。
* [07. 构建环境](07-build-environment.md) — BuildEnvironment：all_docs/dependencies/included索引、doctree pickle缓存、domaindata、TOC数据、增量构建机制。
* [08. 项目管理与Docutils集成](08-project-and-docutils.md) — Project类源文件发现、Parser/Transform/Writer/Translator、addnodes自定义节点、SphinxTransform两阶段处理。

## 域输出篇（09-14）

* [09. Domain域系统](09-domain-system.md) — Domain基类、6大内置域（py/c/cpp/js/rst/std）、ObjType对象类型、resolve_xref交叉引用解析、get_objects搜索索引。
* [10. Builder构建器体系](10-builder-system.md) — Builder基类、13种内置Builder、构建三阶段、build_all/build_update/build_specific模式、parallel并行构建。
* [11. HTML构建器详解](11-html-builder.md) — StandaloneHTMLBuilder、Jinja2模板渲染、静态文件处理、全局页面（genindex/search）、html-collect-pages事件。
* [12. Autodoc自动文档生成](12-autodoc.md) — sphinx.ext.autodoc：autoclass/automodule指令、Documenter体系、napoleon Google/NumPy风格、sphinx-apidoc。
* [13. 主题系统](13-theme-system.md) — Theme加载与继承、theme.toml配置、内置13个主题、第三方主题（Furo/RTD等）、HTMLTranslator定制。
* [14. Intersphinx跨项目引用](14-intersphinx.md) — sphinx.ext.intersphinx：objects.inv清单格式、intersphinx_mapping配置、external+前缀语法。

## 高级篇（15-17）

* [15. 扩展开发详解](15-extension-development.md) — 扩展开发完整指南：setup函数规范、add_*注册API、自定义Directive/Role/Node/Transform/Domain/Builder。
* [16. 国际化与本地化](16-i18n.md) — gettext POT/PO/MO工作流、GettextBuilder、language配置、locale_dirs、smartquotes智能引号。
* [17. 搜索系统](17-search-system.md) — 内置全文搜索：searchindex.js索引格式、snowball词干提取、searchtools.js客户端搜索、CJK bigram策略。

## 用户指南篇（18-25）

* [18. reStructuredText基础语法](18-rest-primer.md) — reST完整入门：段落/行内标记、列表/表格、代码块、指令/角色、目录树toctree、图片/链接、替换/脚注/引用。
* [19. Markdown与MyST支持](19-markdown-and-myst.md) — MyST-Parser安装配置、Markdown中使用指令/角色、GFM扩展、reST与MyST互操作、MyST-NB Notebook集成。
* [20. 交叉引用完全指南](20-cross-references-guide.md) — :ref:/:doc:/:numref:引用、域角色（py/cpp/js等）、intersphinx跨项目引用、显式标题覆盖、autosectionlabel自动标签、缺失引用处理。
* [21. 部署到线上](21-deployment.md) — Read the Docs/GitHub Pages/GitLab Pages/Netlify部署方案、GitHub Actions CI/CD配置、版本管理、.readthedocs.yaml配置。
* [22. 内置扩展完整参考](22-builtin-extensions.md) — 19个内置扩展详解：autodoc/napoleon/intersphinx/todo/viewcode/doctest/coverage/extlinks/autosectionlabel等。
* [23. LaTeX与PDF输出定制](23-latex-and-pdf.md) — latex_engine选择（xelatex/pdflatex）、latex_elements配置、sphinxsetup键、中文PDF支持、字体/页眉/封面定制、Docker构建环境。
* [24. 常见问题与故障排查](24-faq-troubleshooting.md) — 安装/构建/主题/扩展/交叉引用/中文/PDF/性能常见问题、诊断命令、获取帮助渠道。
* [25. 术语表](25-glossary.md) — Builder/Domain/Directive/Role/Environment/Extension/doctree/toctree等核心术语定义与快速参考。
