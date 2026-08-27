---
type: "concept"
title: "事件系统"
description: "EventManager订阅/发射机制、16个核心事件生命周期、priority优先级排序、connect/emit/emit_firstresult API、Builder专用事件"
tags: [core, events, lifecycle, EventManager, hooks]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: events
    resource: /references/event-lifecycle.md
    title: "核心事件列表与触发时机"
  - id: app-init
    resource: /references/sphinx-app-init.md
    title: "Sphinx应用初始化源码"
---

# 事件系统

Sphinx 的事件系统是其扩展机制的核心，定义在 sphinx/events.py。扩展通过 `app.connect(event, callback, priority)` 订阅事件，在构建流程的特定时机插入自定义逻辑，而不需要修改 Sphinx 源码。

## EventManager 类

`EventManager` 管理事件的注册、订阅和发射 [F-021]：

```python
class EventManager:
    def __init__(self) -> None:
        self._events: dict[str, list[EventListener]] = {}

    def add(self, name: str) -> None:
        """注册一个新事件"""

    def connect(self, name: str, callback: Callable, priority: int) -> EventListener:
        """订阅事件，返回监听器ID"""

    def disconnect(self, listener_id: int) -> None:
        """通过ID断开监听器"""

    def emit(self, name: str, *args: Any,
             allowed_exceptions: tuple[type[Exception], ...] = ()) -> list[Any]:
        """发射事件，按priority顺序调用所有监听器，返回结果列表"""

    def emit_firstresult(self, name: str, *args: Any,
                         allowed_exceptions: tuple[type[Exception], ...] = ()) -> Any:
        """发射事件，返回第一个非None的结果"""
```

每个事件监听器由 `EventListener` NamedTuple 表示：

```python
class EventListener(NamedTuple):
    id: int          # 唯一监听器ID（自增计数器）
    handler: Callable  # 回调函数
    priority: int      # 优先级（越小越先执行）
```

## 优先级排序

事件监听器按 `priority` 值从小到大排序执行，默认优先级为 **500**。Sphinx 内部和扩展可以利用优先级控制回调执行顺序：

- **低数值（如100-300）**：更早执行，适合预处理、数据收集
- **默认值500**：大多数扩展使用
- **高数值（如700-900）**：更晚执行，适合后处理、最终输出

当优先级相同时，按注册顺序（connect调用顺序）执行。

## 16个核心事件

Sphinx 预定义了16个核心事件，覆盖了从初始化到构建完成的完整生命周期。按触发顺序排列 [F-022]：

### 初始化阶段

| 事件 | 回调签名 | 触发时机 |
|------|---------|---------|
| `config-inited` | `(app, config)` | 配置加载完成后。这是扩展注册后第一个触发的事件，适合验证配置、调整设置 |
| `builder-inited` | `(app)` | Builder初始化完成后（`builder.init()`之后）。Builder相关的设置和准备工作在此完成 |

### 环境准备阶段

| 事件 | 回调签名 | 触发时机 |
|------|---------|---------|
| `env-get-outdated` | `(app, env, added, changed, removed) → list[str]` | 判断哪些文档需要重建。回调返回需要额外标记为过时的文档名列表 |
| `env-before-read-docs` | `(app, env, docnames)` | 即将读取文档之前。docnames列表可以被回调修改（原地修改）以控制读取哪些文档 |

### 文档读取阶段

| 事件 | 回调签名 | 触发时机 |
|------|---------|---------|
| `source-read` | `(app, docname, source) → None` | 源文件读取后、解析前。`source[0]`是源文本字符串（通过list传递以便修改） |
| `include-read` | `(app, relative_path, parent_docname, content) → None` | include指令读取被包含文件后 |
| `doctree-read` | `(app, doctree)` | 单个文档解析+SphinxTransforms应用后。doctree已完成初步处理 |
| `env-updated` | `(app, env)` | 所有文档读取完毕、环境更新后 |
| `env-get-updated` | `(app, env) → list[str]` | 与env-updated类似，但回调返回新产生的过时文档列表，触发额外的更新迭代 |
| `env-check-consistency` | `(app, env)` | 一致性检查阶段。用于检测跨文档引用问题等 |

### 写入阶段

| 事件 | 回调签名 | 触发时机 |
|------|---------|---------|
| `write-started` | `(app, builder)` | Builder即将开始写入文档。适合写入前的准备工作 |
| `doctree-resolved` | `(app, doctree, docname)` | 单个文档PostTransforms应用后、resolve阶段后。doctree已经完成所有处理，即将交给Writer输出 |
| `missing-reference` | `(app, env, node, contnode) → nodes.reference \| None` | 遇到无法解析的交叉引用时。回调返回一个reference节点即可"修复"该引用，返回None则标记为警告 |

### 完成阶段

| 事件 | 回调签名 | 触发时机 |
|------|---------|---------|
| `build-finished` | `(app, exception)` | 构建完成（无论成功或失败）。exception为None表示成功，否则为异常对象 |

## Builder 专用事件

除了核心事件外，特定Builder还会触发自己的事件：

| 事件 | Builder | 回调签名 | 触发时机 |
|------|---------|---------|---------|
| `html-collect-pages` | HTML Builder | `(app) → list[tuple[str, dict, str]]` | 收集额外的HTML页面（如搜索页、genindex）。返回 `(pagename, context, templatename)` 元组列表 |
| `html-page-context` | HTML Builder | `(app, pagename, templatename, context, doctree) → str \| None` | 渲染HTML页面前。可以修改context字典，返回新的模板名 |
| `linkcheck-process-uri` | LinkCheck Builder | `(app, uri) → str \| None` | 链接检查时处理URI。返回修改后的URI或None跳过 |

## emit vs emit_firstresult

### emit()

`emit()` 按优先级顺序调用所有监听器，收集所有返回值到列表中：

```python
results = app.events.emit('env-get-outdated', app.env, added, changed, removed)
# results 是所有回调返回的列表（每个回调返回一个list[str]）
# Sphinx会将所有结果合并到extra_outdated中
```

### emit_firstresult()

`emit_firstresult()` 在按优先级调用监听器时，一旦某个回调返回非None值，立即返回该值，停止调用后续监听器：

```python
result = app.events.emit_firstresult('missing-reference', app.env, node, contnode)
# 第一个成功解析引用的回调"获胜"，后续回调不再执行
# 这使得扩展可以覆盖默认的引用解析行为
```

## connect 与 disconnect

### connect：订阅事件

```python
def on_config_inited(app, config):
    if not config.language:
        config.language = 'en'

# 订阅事件，获取listener_id
listener_id = app.connect('config-inited', on_config_inited, priority=500)
```

Sphinx在 `application.py` 中为每个核心事件提供了 `@overload` 类型注解，确保回调签名的类型安全：

```python
@overload
def connect(self, event: Literal['config-inited'],
            callback: Callable[[Sphinx, Config], None],
            priority: int = 500) -> int: ...
@overload
def connect(self, event: Literal['builder-inited'],
            callback: Callable[[Sphinx], None],
            priority: int = 500) -> int: ...
# ... 为每个核心事件都有对应的overload
```

### disconnect：取消订阅

```python
app.disconnect(listener_id)
```

## 常见事件使用模式

### 模式1：构建开始时初始化资源

```python
def setup(app):
    app.connect('builder-inited', on_builder_inited)
    return {'version': '1.0', 'parallel_read_safe': True}

def on_builder_inited(app):
    # 初始化数据库连接、加载数据等
    app._my_data = load_data()
```

### 模式2：修改源文件内容

```python
def on_source_read(app, docname, source):
    # source是一个单元素列表，source[0]是源文本
    # 可以修改它来动态替换内容
    source[0] = source[0].replace('{{VERSION}}', app.config.release)

app.connect('source-read', on_source_read)
```

### 模式3：自定义引用解析

```python
def on_missing_reference(app, env, node, contnode):
    target = node['reftarget']
    if target.startswith('my-'):
        # 创建一个引用节点
        from docutils import nodes
        refnode = nodes.reference('', '', internal=False,
                                  refuri=f'https://example.com/{target}')
        refnode.append(contnode)
        return refnode
    return None  # 让其他处理器处理

app.connect('missing-reference', on_missing_reference)
```

### 模式4：构建完成后清理

```python
def on_build_finished(app, exception):
    if exception is None:
        # 构建成功时执行
        post_process(app.outdir)
    else:
        # 构建失败时
        cleanup_temp_files()

app.connect('build-finished', on_build_finished)
```

### 模式5：添加额外HTML页面

```python
def html_collect_pages(app):
    # 返回额外页面列表：(pagename, context, template)
    yield ('my-custom-page', {'title': 'Custom Page'}, 'custom.html')

app.connect('html-collect-pages', html_collect_pages)
```

## allowed_exceptions

`emit()` 和 `emit_firstresult()` 都接受 `allowed_exceptions` 参数，允许指定哪些异常类型不应被捕获和报告：

```python
# 默认情况下，回调中的异常会被捕获并作为警告报告
# 指定allowed_exceptions可以让特定异常正常传播
app.events.emit('my-event', arg, allowed_exceptions=(NoUri,))
```

## 事件系统设计洞察

1. **钩子而非继承**：Sphinx 没有使用继承/重写来实现扩展，而是通过事件钩子。这使得多个扩展可以同时对同一个构建阶段添加逻辑。

2. **优先级排序**：priority机制解决了多扩展竞争同一事件的问题，数值化的优先级提供了确定性的执行顺序。

3. **mutable参数模式**：某些事件（如source-read、env-before-read-docs）通过可变对象（list、dict）传递数据，回调可以原地修改参数来改变行为。这是一种轻量级的拦截器模式。

4. **first-result短路**：`emit_firstresult` 实现了责任链模式，第一个能处理的回调"获胜"。这在 missing-reference 等解析类事件中特别有用。

5. **类型安全**：通过Python的@overload机制，connect方法为每个事件提供了精确的回调签名类型提示。

## 相关概念

- [Sphinx应用类](03-application-class.md)
- [构建流程与生命周期](08-project-and-docutils.md)
- [编写第一个Sphinx扩展](../examples/01-first-extension.md)
