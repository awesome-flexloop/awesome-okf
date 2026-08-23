---
type: "concept"
title: 组件注册表
description: SphinxComponentRegistry的统一组件注册机制，管理Builder、Domain、Directive、Role、Transform等所有可扩展组件。
tags: [sphinx, registry, components, extensibility]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /spec/facts.md
    title: Sphinx源码事实清单
  - id: registry-api
    resource: /references/registry-api.md
    title: 组件注册表API参考
---
# 组件注册表

`SphinxComponentRegistry`（`sphinx/registry.py`）是 Sphinx 的组件注册中心，统一管理所有可扩展组件的注册、查找和去重（见核心洞察 [I-003](/spec/insights.md)）。

## 为什么需要统一注册表

在Sphinx早期版本中，各类组件使用不同的注册机制：
- Builder直接挂在application上
- Domain通过domain dict管理
- Directive/Role走docutils的指令注册
- Transform在不同位置注册

统一注册表解决了以下问题：
- **组件重复注册检测**：避免同名组件被多次注册
- **统一注册入口**：所有add_*方法最终都委托给registry
- **延迟覆盖支持**：允许组件被override，且检测冲突
- **统一查询接口**：通过registry查询所有已注册组件

## 核心数据结构

```python
class SphinxComponentRegistry:
    def __init__(self):
        self.builders: dict[str, type[Builder]] = {}       # 构建器
        self.domains: dict[str, type[Domain]] = {}         # 语言领域
        self.source_inputs: dict[str, SourceInput] = {}    # 源文件输入
        self.source_suffixes: dict[str, str] = {}          # 源文件后缀→解析器
        self.translators: dict[type[Builder], type[nodes.NodeVisitor]] = {}
        self.transforms: list[Transform] = []              # 文档转换器
        self.handlers: dict[str, dict[type, Any]] = {}     # 域处理器
        self.labels: dict[str, str] = {}                   # 标签
        self.anonlabels: dict[str, str] = {}               # 匿名标签
        self.post_transforms: list[Transform] = []         # 后置转换器
        self.app = None  # 创建时绑定，在Sphinx.__init__中设置
```

## 可注册的组件类型

| 组件类型 | 注册方法 | 说明 |
|---------|---------|------|
| Builder | `add_builder(builder, override=False)` | 构建器类，决定输出格式 |
| Domain | `add_domain(domain, override=False)` | 语言领域（Python/C/C++/JS等） |
| Directive | `add_directive(name, directive, override=False)` | reST指令 |
| Role | `add_role(name, role, override=False)` | reST角色（内联标记） |
| Transform | `add_transform(transform)` | 文档转换器（解析后对doctree的变换） |
| PostTransform | `add_post_transform(transform)` | 后置转换器（引用解析后） |
| SourceParser | `add_source_parser(parser, override=False)` | 源文件解析器 |
| SourceSuffix | `add_source_suffix(suffix, filetype)` | 源文件后缀映射 |
| Translator | `add_translator(builder, translator)` | 输出翻译器（visit/depart方法） |
| NodeVisitor | `add_node(node, visitors)` | 节点类型→visit/depart方法映射 |
| CSS/JS | `add_css_file(filename)` / `add_js_file(filename)` | 静态资源 |
| Lexer | `add_lexer(alias, lexer)` | Pygments语法高亮lexer |
| Autodoc | `add_autodocumenter(cls)` | autodoc文档生成器 |
| ObjectDescription | `add_objectdescription(cls)` | 对象描述 |
| Index | `add_index(index)` | 自定义索引 |
| Search | `add_search_language(language)` | 搜索语言支持 |

### override 参数

注册方法大多支持 `override` 参数：
- `False`（默认）：如果组件名已存在，抛 `ExtensionError`（防重复注册）
- `True`：允许覆盖已存在的组件，Sphinx会发出 `RemovedInSphinxWarning` 警告

这是Sphinx防止扩展冲突的重要机制。

## add_node：节点类型的细粒度注册

`add_node` 方法支持按Builder类型注册不同的visitor方法：

```python
app.add_node(mynode,
             html=(visit_mynode_html, depart_mynode_html),
             latex=(visit_mynode_latex, depart_mynode_latex),
             text=(visit_mynode_text, None))
```

这意味着同一个节点类型在不同输出格式下可以有完全不同的渲染逻辑——这是Sphinx支持多输出格式的核心机制之一。

## 注册冲突检测

SphinxComponentRegistry 在注册时执行去重检测：

```python
def add_directive(self, name, directive, override=False):
    if not override and name in self._directives:
        logger.warning('...')  # 或抛异常
    self._directives[name] = directive
```

对于 Directive 和 Role，由于 docutils 本身不支持重名检测，Sphinx 通过 registry 做了额外的冲突检查。

## 扩展开发中的注册

扩展的 `setup(app)` 函数中，所有 `app.add_*` 调用最终都委托给 `app.registry`：

```python
def setup(app):
    # 这些方法都委托给 app.registry
    app.add_builder(MyBuilder)
    app.add_domain(MyDomain)
    app.add_directive('mydirective', MyDirective)
    app.add_role('myrole', my_role_fn)
    app.add_config_value('myext_value', 0, 'html')
    app.connect('build-finished', on_finished)
```

## 相关概念

- [02-应用类](02-application.md) — app.add_*方法的入口
- [08-构建器](08-builders.md) — Builder注册和选择
- [09-Domain机制](09-domains.md) — Domain注册和语义抽象
- [07-扩展开发](07-extension-dev.md) — 扩展中的组件注册模式
