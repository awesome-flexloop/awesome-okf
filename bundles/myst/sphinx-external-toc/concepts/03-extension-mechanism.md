---
type: Concept
title: 扩展工作机制
description: sphinx-external-toc 如何接管 Sphinx 导航——禁用内置 Collector、SiteMap 数据模型、Transform 注入 toctree 节点
tags: [sphinx, sphinx-extension, toctree, architecture, transform, collector, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:05:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: etoc-source
    resource: /references/etoc-source.md
    title: sphinx-external-toc 源码路径映射
---

# 扩展工作机制

本文档深入解析 sphinx-external-toc 如何与 Sphinx 集成，理解其工作机制有助于排查问题和进行高级定制。

## 整体工作流程

sphinx-external-toc 在 Sphinx 构建过程中的执行流程如下：

```
1. builder-inited（构建初始化）
   └── 禁用内置 TocTreeCollector

2. config-inited [priority=900]（配置初始化）
   └── parse_toc_to_env()：
       ├── 解析 _toc.yml 为 SiteMap 对象
       ├── 修改 master_doc 为根文档
       └── （可选）排除不在 ToC 中的文件

3. 文档读取阶段（source-read → doctree-read）
   └── InsertToctrees Transform [priority=100]：
       ├── 查找文档中的 .. tableofcontents:: 占位符
       ├── 根据 SiteMap 创建标准 toctree 节点
       └── 将 toctree 节点插入文档树

4. env-get-outdated（增量构建）
   └── add_changed_toctrees()：对比新旧 SiteMap，标记变更文档

5. TocTreeCollectorWithStyles 处理
   └── 像处理原生 toctree 一样处理注入的节点
       └── 支持扩展编号样式（罗马数字、字母等）

6. build-finished（构建完成）
   └── ensure_index_file()：生成 index.html 重定向（如需要）
```

## 第一步：禁用内置 TocTreeCollector

Sphinx 内置的 `TocTreeCollector` 负责从文档中收集 `.. toctree::` 指令并构建导航树。sphinx-external-toc 必须禁用它，否则会产生冲突。

```python
def disable_builtin_toctree_collector(app):
    for obj in gc.get_objects():
        if not isinstance(obj, TocTreeCollector):
            continue
        if obj.listener_ids is None:
            continue  # 已禁用
        obj.disable(app)
```

这个函数通过 `gc.get_objects()` 遍历 Python 垃圾回收器追踪的所有对象，找到 `TocTreeCollector` 实例并调用其 `disable()` 方法取消注册事件监听。检查 `listener_ids is None` 是为了避免在 sphinx-autobuild 等自动重载场景中重复禁用。

然后注册自定义的 collector：

```python
app.add_env_collector(TocTreeCollectorWithStyles)
```

## 第二步：解析 _toc.yml 到 SiteMap

在 `config-inited` 事件（priority=900，在 `merge_source_suffix` priority=800 之后），`parse_toc_to_env()` 函数执行：

1. **读取并解析 YAML**：使用 `yaml.safe_load()` 读取 `_toc.yml`
2. **构建 SiteMap**：递归解析为 `SiteMap → Document → TocTree → items` 的树形结构
3. **验证**：检测格式错误、重复文档、不兼容的键组合等
4. **更新 master_doc**：将 Sphinx 的 `master_doc` 配置设为 ToC 根文档
5. **排除未引用文件**（可选）：如果 `external_toc_exclude_missing=True`，扫描源目录，将不在 ToC 中的文件加入 `exclude_patterns`

### 为什么 priority=900？

事件优先级数字越小越早执行。`merge_source_suffix` 事件（priority=800）负责合并源文件后缀列表（`.rst`、`.md` 等）。解析 ToC 时需要知道哪些后缀是有效的源文件后缀，因此必须在其后执行。

## 第三步：Transform 注入 toctree 节点

这是扩展的核心步骤。`InsertToctrees` 是一个 `SphinxTransform`，默认 priority=100，在每个文档被解析后执行。

### Transform 优先级

Sphinx Transform 的执行顺序很关键：

| Priority | Transform | 作用 |
|----------|-----------|------|
| 100 | InsertToctrees | 注入 toctree 节点 |
| 500 | TocTreeCollector.process_doc | 收集 toctree 信息（必须在注入之后） |
| 880 | DoctreeReadEvent | 触发文档读取完成事件 |

InsertToctrees priority=100 确保了 toctree 节点在 Collector 处理之前就已存在于文档树中。

### 注入逻辑

`insert_toctrees()` 函数的核心逻辑：

1. **检测原生 toctree**：遍历文档树，如果发现标准 `.. toctree::` 指令生成的节点，发出警告（因为两者互斥）
2. **查找占位符**：查找 `.. tableofcontents::` 指令生成的 `TableOfContentsNode` 占位节点
3. **获取当前文档的子树**：从 SiteMap 中查找当前文档对应的 Document 对象及其 subtrees
4. **创建 toctree 节点**：为每个 TocTree 创建标准 `toctree` 节点（`sphinx.addnodes.toctree`），设置 entries、caption、maxdepth、numbered、glob 等属性
5. **处理条目**：
   - FileItem：添加到 entries 和 includefiles
   - GlobItem：使用 `patfilter()` 匹配文档
   - UrlItem：作为外部链接添加（不加入 includefiles）
6. **插入位置**：如果有占位符，替换占位符；否则追加到文档最后一个 section 末尾

### 为什么能与主题兼容？

因为注入的是**标准 Sphinx `toctree` 节点**，与 `.. toctree::` 指令生成的节点完全相同。主题模板和 Sphinx 后续处理流程无法区分"原生 toctree"和"注入的 toctree"，因此不需要任何修改即可正常工作。

## 第四步：增量构建支持

`env-get-outdated` 事件用于增量构建——判断哪些文档需要重新构建。`add_changed_toctrees()` 函数对比新旧 SiteMap：

```python
def add_changed_toctrees(app, env, added, changed, removed):
    previous_map = getattr(app.env, "external_site_map", None)
    app.env.external_site_map = app.config.external_site_map
    if not previous_map:
        return set()
    filenames = site_map.get_changed(previous_map)
    return {remove_suffix(name, app.config.source_suffix) for name in filenames}
```

`SiteMap.get_changed()` 方法对比两个 SiteMap，返回新增、删除或内容变更的文档集合。

## 第五步：编号样式处理

`TocTreeCollectorWithStyles` 继承自 `TocTreeCollector`，覆写了 `assign_section_numbers()` 方法，在标准编号之后将数字转换为指定样式：

```python
def assign_section_numbers(self, env):
    result = super().assign_section_numbers(env)  # 先做标准编号
    # 然后根据 style 转换编号格式
    for toctree in doctree.findall(sphinxnodes.toctree):
        style = toctree.get("style", "numerical")
        # ...转换为罗马数字/字母等
```

支持的编号样式：

| style 值 | 样式 | 示例 |
|----------|------|------|
| `numerical` | 阿拉伯数字（默认） | 1, 2, 3... |
| `romanupper` | 大写罗马数字 | I, II, III... |
| `romanlower` | 小写罗马数字 | i, ii, iii... |
| `alphaupper` | 大写字母 | A, B, C... |
| `alphalower` | 小写字母 | a, b, c... |

`restart_numbering` 选项控制是否在每个 toctree 开始时重置计数器。`use_multitoc_numbering` 配置控制多个 toctree 之间是否连续编号。

## 第六步：index.html 重定向

在 `build-finished` 事件中，如果根文档不是 `index`（比如叫 `intro` 或 `welcome`），Sphinx 不会生成根目录的 `index.html`。`ensure_index_file()` 创建一个 meta refresh 重定向页面：

```html
<meta http-equiv="Refresh" content="0; url=intro.html" />
```

这确保用户访问站点根 URL 时能正确跳转到首页。

## 关键设计决策

### 为什么用 Transform 而不是 doctree-resolved 事件？

Transform 在文档解析后立即执行，此时文档树结构已经确定但还未被后续处理。使用 Transform 而非事件钩子可以确保 toctree 节点成为文档树的一部分，被 Sphinx 标准流程处理。

### 为什么通过 gc.get_objects() 禁用 Collector？

Sphinx 没有提供官方的"注销 collector"或"替换 collector"API。`TocTreeCollector` 在 `sphinx.environment` 初始化时自动实例化并注册事件。通过 gc 遍历找到实例并调用 `disable()` 是实际可行的方案。

### 为什么 hidden 默认值为 True？

Sphinx 原生 `.. toctree::` 默认 `:hidden: false`（在文档正文中显示目录列表），但 sphinx-external-toc 默认 `hidden: true`。这是因为 Jupyter Book 等使用场景中，导航通过侧边栏展示，文档正文中通常不需要重复显示目录列表。用户可通过显式设置 `hidden: false` 改变此行为。

## 相关概念

- [_toc.yml 语法详解](/concepts/02-toc-yaml-syntax.md)
- [高级功能](/concepts/04-advanced-features.md)
- [sphinx-external-toc 源码路径映射](/references/etoc-source.md)
