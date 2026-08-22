---
type: "reference"
title: Sphinx 核心事件完整列表
description: Sphinx所有核心事件的完整清单，包括事件名、回调签名和触发时机。
tags: [sphinx, api, events, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: events-core
    resource: /references/core-events-list.md
    title: sphinx/events.py + sphinx/application.py 核心事件定义
---
# Sphinx 核心事件完整列表

以下是`sphinx/events.py`中`core_events`字典定义的17个核心事件，按构建生命周期排序。

## 初始化阶段

### config-inited
- **参数**: `(app, config)`
- **触发时机**: 配置初始化完成后，在创建Project和BuildEnvironment之前
- **用途**: 修改配置、注册依赖配置的组件

### builder-inited
- **参数**: `(app)`
- **触发时机**: Builder初始化完成后（builder.init()调用后）
- **用途**: 执行依赖builder的初始化操作

## 环境/读取阶段

### env-get-outdated
- **参数**: `(app, env, added, changed, removed)` → 返回`Sequence[str]`
- **触发时机**: 判断哪些文档需要重新构建时
- **用途**: 自定义过期检测逻辑，返回额外需要重建的文档名
- **注意**: 回调可以修改added/changed/removed集合

### env-before-read-docs
- **参数**: `(app, env, docnames)`
- **触发时机**: 开始读取源文件之前
- **用途**: 修改要读取的文档列表、准备读取环境

### env-purge-doc
- **参数**: `(app, env, docname)`
- **触发时机**: 清除某个文档的缓存信息时（增量构建中重新读取前）
- **用途**: 清除扩展存储在env中与该文档相关的自定义数据

### source-read
- **参数**: `(app, docname, source_text)`
- **触发时机**: 读取源文件内容后、解析之前
- **用途**: 程序化修改源文件内容（source_text是list，可以原地修改）

### include-read
- **参数**: `(app, relative_path, parent_docname, source_text)`
- **触发时机**: 处理include指令读取文件后
- **用途**: 修改被include的文件内容

### doctree-read
- **参数**: `(app, doctree)`
- **触发时机**: 单个文档解析为doctree后、pickle缓存之前
- **用途**: 对doctree进行初次处理

### env-merge-info
- **参数**: `(app, env, read_docnames, other_env)`
- **触发时机**: 并行构建时合并子进程的环境数据
- **用途**: 合并扩展在并行进程中存储的自定义数据

### env-updated
- **参数**: `(app, env)` → 返回`str`
- **触发时机**: 所有文档读取完成、环境更新后
- **用途**: 执行依赖于完整环境的处理（如生成索引），返回消息字符串

### env-get-updated
- **参数**: `(app, env)` → 返回`Iterable[str]`
- **触发时机**: env-updated之后，获取新增/更新的文档列表
- **用途**: 返回因为环境更新而需要重新写入的文档名

### env-check-consistency
- **参数**: `(app, env)`
- **触发时机**: 环境更新完成后、写入开始前
- **用途**: 执行一致性检查、发出警告

## 写入阶段

### write-started
- **参数**: `(app, builder)`
- **触发时机**: 开始写入文档前（builder准备写入后）
- **用途**: 执行写入前的准备工作

### doctree-resolved
- **参数**: `(app, doctree, docname)`
- **触发时机**: 单个doctree解析完成、所有交叉引用已解析后
- **用途**: 对最终doctree进行处理（此时所有xref已解析）

### missing-reference
- **参数**: `(app, env, node, contnode)` → 返回`nodes.reference | None`
- **触发时机**: 交叉引用无法解析时
- **用途**: 自定义缺失引用的解析逻辑，返回创建的reference节点或None

### warn-missing-reference
- **参数**: `(app, domain, node)` → 返回`bool | None`
- **触发时机**: 即将发出"missing reference"警告时
- **用途**: 抑制特定缺失引用的警告，返回True表示已处理不警告

## 完成阶段

### build-finished
- **参数**: `(app, exception)`
- **触发时机**: 构建完成（成功或异常）
- **用途**: 清理资源、生成后处理、复制额外文件。exception为None表示成功，否则为异常对象

## Builder特定事件

### html-collect-pages
- **参数**: `(app)` → 返回`Iterable[tuple[str, dict, str]]`
- **触发时机**: HTML builder收集额外页面时
- **用途**: 添加自定义HTML页面

### html-page-context
- **参数**: `(app, pagename, templatename, context, doctree)` → 返回`str | None`
- **触发时机**: 渲染HTML页面之前
- **用途**: 修改模板上下文或返回自定义模板名

### linkcheck-process-uri
- **参数**: `(app, uri)` → 返回`str | None`
- **触发时机**: linkcheck builder处理URI时
- **用途**: 忽略或修改特定URI的检查

## 扩展事件（部分）

### autodoc-process-docstring
- **参数**: `(app, what, name, obj, options, lines)`
- **用途**: 处理autodoc提取的文档字符串

### autodoc-before-process-signature
- **参数**: `(app, obj, bound_method)`
- **用途**: 在处理签名前修改对象

### autodoc-process-signature
- **参数**: `(app, what, name, obj, options, signature, return_annotation)`
- **用途**: 修改autodoc生成的签名

### autodoc-skip-member
- **参数**: `(app, what, name, obj, skip, options)` → 返回`bool`
- **用途**: 决定是否跳过某个成员
