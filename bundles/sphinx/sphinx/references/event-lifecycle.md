---
type: "reference"
title: "核心事件列表与触发时机"
description: "Sphinx 16个核心事件定义、回调签名与触发阶段"
tags: [core, events, lifecycle]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: "events-core", resource: "sphinx/events.py", title: "core_events dict and EventManager" }
---

# 核心事件列表与触发时机

源码位置：`sphinx/events.py` 第51-69行

## 核心事件定义

```python
core_events = {
    'config-inited': 'config',
    'builder-inited': '',
    'env-get-outdated': 'env, added, changed, removed',
    'env-before-read-docs': 'env, docnames',
    'env-purge-doc': 'env, docname',
    'source-read': 'docname, source text',
    'include-read': 'relative path, parent docname, source text',
    'doctree-read': 'the doctree before being pickled',
    'env-merge-info': 'env, read docnames, other env instance',
    'env-updated': 'env',
    'env-get-updated': 'env',
    'env-check-consistency': 'env',
    'write-started': 'builder',
    'doctree-resolved': 'doctree, docname',
    'missing-reference': 'env, node, contnode',
    'warn-missing-reference': 'domain, node',
    'build-finished': 'exception',
}
```

## 事件触发时机与回调签名

| 事件名 | 触发阶段 | 回调签名 | 用途 |
|--------|---------|---------|------|
| `config-inited` | 配置加载完成后 | `(app, config)` | 检查/修改配置值 |
| `builder-inited` | Builder初始化完成 | `(app)` | 初始化扩展资源 |
| `env-get-outdated` | 判断哪些文档需要重新构建 | `(app, env, added, changed, removed) -> list[str]` | 自定义过期判断 |
| `env-before-read-docs` | 开始读取文档前 | `(app, env, docnames)` | 修改待读取文档列表 |
| `env-purge-doc` | 清除单个文档缓存 | `(app, env, docname)` | 清理扩展缓存数据 |
| `source-read` | 源文件读取后 | `(app, docname, source_list)` | 修改源文件内容 |
| `include-read` | include指令读取文件后 | `(app, path, parent_docname, source_list)` | 处理included文件 |
| `doctree-read` | 单个文档解析完成后 | `(app, doctree)` | 处理解析后的doctree |
| `env-merge-info` | 并行构建合并环境 | `(app, env, docnames, other)` | 合并并行环境数据 |
| `env-updated` | 环境更新完成后 | `(app, env) -> str` | 环境更新后的处理 |
| `env-get-updated` | 获取更新文档列表 | `(app, env) -> Iterable[str]` | 返回需要更新的文档 |
| `env-check-consistency` | 一致性检查 | `(app, env)` | 执行一致性检查 |
| `write-started` | 开始写入文档前 | `(app, builder)` | 写入前准备 |
| `doctree-resolved` | doctree解析完成(resolve阶段) | `(app, doctree, docname)` | 处理resolved的doctree |
| `missing-reference` | 交叉引用无法解析时 | `(app, env, node, contnode) -> nodes.reference\|None` | 自定义解析缺失引用 |
| `warn-missing-reference` | 缺失引用警告 | `(app, domain, node) -> bool\|None` | 抑制特定缺失引用警告 |
| `build-finished` | 构建结束(成功或失败) | `(app, exception)` | 清理资源、后处理 |

## Builder/扩展专用事件

| 事件名 | 来源 | 回调签名 |
|--------|------|---------|
| `html-collect-pages` | HTML Builder | `(app) -> Iterable[(pagename, context, templatename)]` |
| `html-page-context` | HTML Builder | `(app, pagename, templatename, context, doctree) -> str\|None` |
| `linkcheck-process-uri` | LinkCheck Builder | `(app, uri) -> str\|None` |
| `object-description-transform` | 内置扩展 | `(app, domain, objtype, contentnode)` |
| `autodoc-process-docstring` | autodoc | `(app, what, name, obj, options, lines)` |
| `autodoc-before-process-signature` | autodoc | `(app, obj, bound_method)` |
| `autodoc-process-signature` | autodoc | `(app, what, name, obj, options, signature, return_annotation)` |
| `autodoc-process-bases` | autodoc | `(app, name, obj, options, bases)` |
| `autodoc-skip-member` | autodoc | `(app, what, name, obj, skip, options) -> bool` |
| `todo-defined` | todo扩展 | `(app, todo_node)` |
| `viewcode-find-source` | viewcode扩展 | `(app, modname) -> (source, tags)` |
| `viewcode-follow-imported` | viewcode扩展 | `(app, modname, attribute) -> str\|None` |

## EventManager关键方法

```python
class EventManager:
    def connect(self, name: str, callback, priority: int = 500) -> int:
        """注册事件监听器，返回listener_id"""
    def disconnect(self, listener_id: int) -> None:
        """通过ID断开监听器"""
    def emit(self, name: str, *args, allowed_exceptions=()) -> list[Any]:
        """发射事件，按priority升序调用所有监听器，返回结果列表"""
    def emit_firstresult(self, name: str, *args, allowed_exceptions=()) -> Any:
        """发射事件，返回第一个非None结果"""
    def add(self, name: str) -> None:
        """注册自定义事件名"""
```

EventListener是NamedTuple：`(id: int, handler: Callable, priority: int)`
