# 概念文档（concepts/）

本目录包含18篇从入门到进阶的Sphinx概念文档，按学习路径分为四篇。

## 入门篇（00-02）

* [00. Sphinx 简介](00-introduction.md) — Sphinx是什么、核心能力、多格式输出、与其他文档工具对比。
* [01. 5分钟快速上手](01-getting-started.md) — 安装、sphinx-quickstart初始化、sphinx-build构建、conf.py配置、Python API快速体验。
* [02. 架构总览](02-architecture-overview.md) — Application-Centric架构、核心类关系图、初始化流程、构建管线（READING→WRITING→FINISHING）。

## 核心架构篇（03-08）

* [03. Sphinx应用类](03-application-class.md) — Sphinx主类详解：目录属性、build方法、扩展API（add_*/connect/emit）、TemplateBridge。
* [04. 配置系统](04-config-system.md) — _Opt配置选项、_ConfigRebuild重建级别、conf.py执行机制、add_config_value扩展API、ENUM枚举约束。
* [05. 事件系统](05-event-system.md) — EventManager订阅/发射、16个核心事件生命周期、priority优先级、connect/emit/emit_firstresult API。
* [06. 组件注册中心](06-registry.md) — SphinxComponentRegistry详解：builders/domains/directives/roles/transforms注册、load_extension扩展加载、entry points发现。
* [07. 构建环境](07-build-environment.md) — BuildEnvironment：all_docs/dependencies/included索引、doctree pickle缓存、domaindata、TOC数据、增量构建机制。
* [08. 项目管理与Docutils集成](08-project-and-docutils.md) — Project类源文件发现、Parser/Transform/Writer/Translator、addnodes自定义节点、SphinxTransform两阶段处理。

## 领域输出篇（09-14）

* [09. Domain领域系统](09-domain-system.md) — Domain基类、6大内置域（py/c/cpp/js/rst/std）、ObjType对象类型、resolve_xref交叉引用解析、get_objects搜索索引。
* [10. Builder构建器体系](10-builder-system.md) — Builder基类、13种内置Builder、构建三阶段、build_all/build_update/build_specific模式、parallel并行构建。
* [11. HTML构建器详解](11-html-builder.md) — StandaloneHTMLBuilder、Jinja2模板渲染、静态文件处理、全局页面（genindex/search）、html-collect-pages事件。
* [12. Autodoc自动文档生成](12-autodoc.md) — sphinx.ext.autodoc：autoclass/automodule指令、Documenter体系、napoleon Google/NumPy风格、sphinx-apidoc。
* [13. 主题系统](13-theme-system.md) — Theme加载与继承、theme.toml配置、内置13个主题、第三方主题（Furo/RTD等）、HTMLTranslator定制。
* [14. Intersphinx跨项目引用](14-intersphinx.md) — sphinx.ext.intersphinx：objects.inv清单格式、intersphinx_mapping配置、external+前缀语法。

## 高级篇（15-17）

* [15. 扩展开发详解](15-extension-development.md) — 扩展开发完整指南：setup函数规范、add_*注册API、自定义Directive/Role/Node/Transform/Domain/Builder。
* [16. 国际化与本地化](16-i18n.md) — gettext POT/PO/MO工作流、GettextBuilder、language配置、locale_dirs、smartquotes智能引号。
* [17. 搜索系统](17-search-system.md) — 内置全文搜索：searchindex.js索引格式、snowball词干提取、searchtools.js客户端搜索、CJK bigram策略。
