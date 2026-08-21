# 代码示例（examples/）

本目录提供可直接运行的实战示例，帮助你快速上手Sphinx开发。

## 入门示例

* [编写第一个Sphinx扩展](01-first-extension.md) — 从零创建Hello World扩展，包含setup函数、配置注册、事件订阅、简单指令的完整流程。

## 中级示例

* [自定义指令和角色](02-custom-directive.md) — 创建带选项和内容的自定义Directive、XRefRole交叉引用角色、自定义节点及多格式输出支持。

* [使用Autodoc生成API文档](03-autodoc-api.md) — 配置autodoc/napoleon扩展、Google风格docstring、autodoc事件钩子定制输出、sphinx-apidoc自动生成骨架。

## 高级示例

* [自定义Builder输出Markdown](04-custom-builder.md) — 创建自定义Builder将Sphinx文档输出为Markdown格式，实现MarkdownTranslator和MarkdownWriter。
