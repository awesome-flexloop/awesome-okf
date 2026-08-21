---
type: "concept"
title: "术语表"
description: "Sphinx/docutils/reST生态核心术语定义——Builder、Domain、Directive、Role、Environment、Extension、doctree等关键概念"
tags: [glossary, terminology, definitions, concepts]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T11:05:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T11:05:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: official-glossary
    resource: /references/official-docs.md
    title: "Sphinx 官方文档 Glossary"
---

# 术语表

本章定义 Sphinx/docutils/reST 生态中的核心术语，帮助理解文档中出现的专业概念。

## B

### Builder（构建器）

Builder 是继承自 `sphinx.builders.Builder` 的类，接收解析后的文档树（doctree）并执行输出操作。通常Builder将文档转换为特定输出格式（HTML/LaTeX/EPUB等），也有不产生输出的Builder（如linkcheck检查链接有效性、coverage统计文档覆盖率）。

每个构建器对应一种输出格式或处理任务，通过 `-b` 命令行选项选择：`sphinx-build -b html`。

→ 参见 [Builder构建器体系](10-builder-system.md)

### BuildEnvironment（构建环境）

BuildEnvironment 是Sphinx的核心数据结构，存储源目录下所有文档的元信息——文档索引（all_docs）、依赖关系（dependencies）、包含文件（included）、各Domain数据（domaindata）等。构建环境在解析阶段后被pickle序列化到磁盘（`environment.pickle`），后续增量构建时直接加载，只重新解析变更的文档。

`ENV_VERSION` 控制环境缓存版本，Sphinx版本升级时会自动失效旧缓存。

→ 参见 [构建环境](07-build-environment.md)

## C

### conf.py（配置文件）

Sphinx项目的配置文件，是一个Python文件。Sphinx在构建时执行它来加载配置项（project/author/release/extensions/html_theme等）。`conf.py` 本身也可以作为扩展使用——通过定义 `setup(app)` 函数注册自定义指令、角色和事件回调。

→ 参见 [5分钟快速上手](01-getting-started.md)、[配置系统](04-config-system.md)

### Configuration Directory（配置目录）

包含 `conf.py` 的目录。默认与源目录（source directory）相同，可通过 `-c` 命令行选项指定不同的配置目录。

## D

### Directive（指令）

指令是reStructuredText的块级标记元素，用于标记一段内容具有特殊含义。指令不仅由docutils提供，Sphinx和自定义扩展也可以添加指令。基本语法：

```rst
.. directive-name:: 参数
   :option: 值

   指令内容
```

常见指令：`toctree`（目录树）、`code-block`（代码块）、`note`/`warning`（提示框）、`automodule`（自动文档）、`figure`（图片）等。

→ 参见 [reStructuredText基础语法](18-rest-primer.md)

### Document Name（文档名）

Sphinx对源文件的抽象表示。由于不同操作系统路径分隔符不同、源文件可有不同扩展名（`.rst`/`.md`/`.txt`），Sphinx统一使用文档名：相对于源目录、无扩展名、使用正斜杠分隔。例如 `docs/source/tutorial/install.rst` 的文档名是 `tutorial/install`。

所有引用"文档"的配置值和API都期望文档名格式（无开头/结尾斜杠）。

### doctree（文档树）

docutils解析reST/Markdown源文件后生成的树状数据结构，由docutils Node对象组成。doctree是Sphinx处理管线的中间表示——Transform修改doctree，Builder通过Translator/Writer将doctree序列化为输出格式。

doctree在READING阶段生成，经Transform处理后pickle序列化到磁盘，WRITING阶段加载后经PostTransform处理，最终输出。

### Domain（域）

Domain是一组描述和链接特定知识域对象的指令和角色的集合。最典型的是编程语言域——Python域（`py`）提供 `:py:func:`、`:py:class:` 等角色和 `.. py:function::` 等指令来描述Python代码对象。其他域包括C（`c`）、C++（`cpp`）、JavaScript（`js`）、reST（`rst`）和标准域（`std`）。

域的存在避免了不同语言的命名冲突，也使得支持新语言的扩展更容易编写。

→ 参见 [Domain领域系统](09-domain-system.md)

## E

### Environment

见 **BuildEnvironment**。

### Extension（扩展）

扩展是一个Python模块，通过 `setup(app)` 函数向Sphinx注册功能（指令、角色、Builder、Domain、事件回调、配置值等）。Sphinx的几乎所有功能都可以通过扩展添加或修改——内置功能（autodoc/intersphinx等）本身也是作为扩展实现的（builtin_extensions）。

第三方扩展发布在PyPI上，通过pip安装后在 `extensions` 配置中启用。

→ 参见 [扩展开发详解](15-extension-development.md)、[内置扩展完整参考](22-builtin-extensions.md)

## I

### Intersphinx

Sphinx内置扩展，允许链接到其他Sphinx项目的文档。通过下载其他项目的 `objects.inv` 清单文件，Intersphinx可以解析跨项目的交叉引用（如Python标准库、Django、Flask等）。

→ 参见 [Intersphinx跨项目引用](14-intersphinx.md)

## M

### Master Document / Root Document（主文档/根文档）

包含根 `toctree` 指令的文档，默认为 `index`（即 `index.rst`/`index.md`）。主文档是Sphinx构建的入口点，通过它递归发现所有需要构建的文档。

可通过 `root_doc`（旧称 `master_doc`）配置项修改。

## O

### Object（对象）

Sphinx文档的基本构建块。每个"对象指令"（如 `.. py:function::`、`.. cpp:class::`、`.. js:module::`）创建一个对象块，记录代码实体的信息（名称、签名、参数、描述等）。大多数对象可以通过对应的角色交叉引用（如 `:py:func:` 引用 `.. py:function::` 定义的函数）。

→ 参见 [Autodoc自动文档](12-autodoc.md)、[Domain领域系统](09-domain-system.md)

## R

### Role（角色）

角色是reStructuredText的行内标记元素，用于标记一段文本具有特殊含义。与指令（块级）对应，角色在行内使用，语法为 `` :rolename:`content` ``。

常见角色：`:ref:`（交叉引用）、`:py:func:`（Python函数引用）、`:doc:`（文档引用）、`:file:`（文件路径）、`:command:`（命令名）。Sphinx和扩展可以添加自定义角色。

→ 参见 [reStructuredText基础语法](18-rest-primer.md)、[交叉引用完全指南](20-cross-references-guide.md)

### reStructuredText（reST）

Sphinx默认的轻量级标记语言，由docutils项目开发。reST设计为"易读的纯文本"——源文件即使不渲染也具有良好可读性。通过Directive（块级）和Role（行内）两种扩展机制支持丰富语义标记。Sphinx也支持通过MyST-Parser使用Markdown。

→ 参见 [reStructuredText基础语法](18-rest-primer.md)

## S

### Source Directory（源目录）

包含所有文档源文件（.rst/.md等）的顶级目录，及其所有子目录。Sphinx在此目录下发现和解析文档。

### Sphinx Application（Sphinx应用）

`sphinx.application.Sphinx` 类的实例，是Sphinx的中枢对象。它持有所有核心组件（Config、EventManager、BuildEnvironment、Builder、Registry）的引用，提供 `add_directive()`、`add_role()`、`add_config_value()`、`connect()` 等扩展API，驱动构建流程。

→ 参见 [Sphinx应用类](03-application-class.md)

## T

### toctree（目录树）

Table of Contents tree的缩写，是Sphinx组织文档层次结构的核心指令。toctree定义了文档之间的父子关系，形成树状结构，用于生成侧边栏导航、上/下一页链接、面包屑等。每个Sphinx项目有一个根toctree（在主文档中），子文档可以包含子toctree形成多级层次。

```rst
.. toctree::
   :maxdepth: 2
   :caption: 入门

   install
   quickstart
```

→ 参见 [reStructuredText基础语法](18-rest-primer.md)

### Transform（转换）

Transform是docutils/Sphinx提供的文档树后处理机制，在解析完成后、写入输出前对doctree进行修改。SphinxTransform按优先级排序执行，常见的Transform包括：交叉引用解析（XRefRole）、脚注处理、引用替换、默认域处理等。

Transform分为两类：
- **默认Transform**：READING阶段应用（处理doctree）
- **PostTransform**：WRITING阶段应用（每个Builder可以有自己的PostTransform）

→ 参见 [架构总览](02-architecture-overview.md)

### Translator（翻译器）

Translator是docutils的Visitor模式组件，遍历doctree节点并调用对应方法生成输出。每个Builder通常有一个对应的Translator（如HTMLTranslator生成HTML标签、LaTeXTranslator生成LaTeX命令）。Translator配合Writer完成doctree到输出格式的序列化。

## 相关概念

- [架构总览](02-architecture-overview.md)
- [Sphinx应用类](03-application-class.md)
- [Builder构建器体系](10-builder-system.md)
- [Domain领域系统](09-domain-system.md)
- [扩展开发详解](15-extension-development.md)
