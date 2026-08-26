# 概念文档

- [00 - sphinxcontrib-jsmath 简介](00-introduction.md) — 什么是 jsMath 渲染器、项目定位、与其他数学渲染方案对比。
- [01 - 5分钟快速上手](01-getting-started.md) — 安装、conf.py 配置、编写数学公式、构建 HTML。
- [02 - 扩展注册与 setup 函数](02-setup-and-registration.md) — setup 函数逐行解析、add_html_math_renderer API、扩展元数据返回值。
- [03 - 数学节点访问者](03-math-node-visitors.md) — html_visit_math/html_visit_displaymath 详解、docutils visitor 模式、SkipNode 机制。
- [04 - 智能JS加载机制](04-smart-js-loading.md) — install_jsmath 三重条件检查、env-updated 事件时机、按需资源加载模式。
- [05 - 国际化与并行安全](05-i18n-and-parallel.md) — gettext 消息目录、并行读写安全、mypy 严格类型检查、TYPE_CHECKING 条件导入。

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-setup-and-registration
03-math-node-visitors
04-smart-js-loading
05-i18n-and-parallel
```
