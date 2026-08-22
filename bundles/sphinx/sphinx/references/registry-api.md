---
type: "reference"
title: Sphinx 组件注册表 API 参考
description: SphinxComponentRegistry的API参考，包括各组件注册方法。
tags: [sphinx, api, registry, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: registry-py
    resource: /references/registry-api.md
    title: sphinx/registry.py 源码
---
# Sphinx 组件注册表 API 参考

组件注册表类`SphinxComponentRegistry`定义在`sphinx/registry.py`，通过`app.registry`访问。通常不直接调用registry方法，而是通过`app.add_*`方法间接调用。

## 注册表属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `builders` | `dict[str, type[Builder]]` | 构建器类注册表 |
| `domains` | `dict[str, type[Domain]]` | Domain类注册表 |
| `domain_directives` | `dict[str, dict[str, type[Directive]]]` | 各Domain的额外指令 |
| `domain_roles` | `dict[str, dict[str, RoleFunction|XRefRole]]` | 各Domain的额外角色 |
| `domain_indices` | `dict[str, list[type[Index]]]` | 各Domain的索引 |
| `domain_object_types` | `dict[str, dict[str, ObjType]]` | 各Domain的对象类型 |
| `source_parsers` | `dict[str, type[Parser]]` | 源文件解析器 |
| `source_suffix` | `dict[str, str]` | 文件后缀→类型映射 |
| `transforms` | `list[type[Transform]]` | 文档转换器 |
| `post_transforms` | `list[type[Transform]]` | 后转换器 |
| `translators` | `dict[str, type[NodeVisitor]]` | 各builder的Translator类 |
| `translation_handlers` | `dict[str, dict[str, tuple[visit, depart]]]` | 节点visit/depart处理器 |
| `css_files` | `list[tuple[str, dict]]` | CSS文件列表 |
| `js_files` | `list[tuple[str|None, dict]]` | JS文件列表 |
| `html_themes` | `dict[str, _StrPath]` | HTML主题路径 |
| `latex_packages` | `list[tuple[str, str|None]]` | LaTeX宏包 |
| `documenters` | `dict[str, type[Documenter]]` | autodoc文档生成器 |
| `enumerable_nodes` | `dict[type[Node], tuple[str, TitleGetter|None]]` | 可编号节点 |
| `autodoc_attrgetters` | `dict[type, Callable]` | autodoc属性获取器 |
| `static_dirs` | `list[Path]` | 扩展注册的静态目录 |

## 关键方法

| 方法 | 说明 |
|------|------|
| `add_builder(builder, override=False)` | 注册构建器，builder必须有name属性 |
| `create_builder(app, name, env) -> Builder` | 实例化指定名称的构建器 |
| `preload_builder(app, name)` | 通过entry_points预加载builder |
| `add_domain(domain, override=False)` | 注册Domain |
| `add_directive(domain, name, cls, override)` | 注册指令 |
| `add_role(domain, name, role, override)` | 注册角色 |
| `add_translator(name, translator_class, override)` | 注册Translator |
| `add_translation_handlers(node, **kwargs)` | 为节点注册各builder的visit/depart处理器 |
| `load_extension(app, extname)` | 加载扩展模块，调用其setup(app) |
