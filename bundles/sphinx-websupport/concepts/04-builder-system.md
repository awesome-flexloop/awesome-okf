---
okf_version: "0.2"
type: "concept"
title: Builder系统
description: WebSupportBuilder的工作机制——继承PickleHTMLBuilder、文档序列化流程、pickle输出格式、静态资源管理
tags: [sphinx-websupport, builder, picklehtmlbuilder, serialization, pickles]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-source
    resource: /references/websupport-source.md
---

# Builder系统

Builder系统是sphinxcontrib-websupport在Sphinx构建阶段的核心组件，负责将reST文档序列化为Web应用可消费的pickle数据格式。

## WebSupportBuilder 类

`WebSupportBuilder` 定义在 `sphinxcontrib.websupport.builder` 模块，继承自 `sphinxcontrib.serializinghtml.PickleHTMLBuilder`。

### 类属性

| 属性 | 值 | 说明 |
|------|-----|------|
| `name` | `'websupport'` | Builder注册名，通过entry point注册到Sphinx |
| `default_translator_class` | `WebSupportTranslator` | 默认使用的文档树翻译器 |
| `versioning_compare` | `True` | 启用版本比较，确保commentable节点的uuid稳定 |

### versioning_method 属性

```python
@property
def versioning_method(self):
    return is_commentable
```

versioning_method 返回 `is_commentable` 函数，告诉Sphinx的版本比较机制：只有可评论的节点（段落）需要保持UUID稳定性。这确保了文档修改后，已有的评论仍能关联到正确的段落。

## 初始化流程（init）

```python
def init(self):
    super().init()
    self.init_templates()
    if not isinstance(self.templates, BuiltinTemplateLoader):
        raise RuntimeError('websupport builder must be used with the builtin templates')
    self.add_js_file('websupport.js')
```

Builder初始化时做了三件额外的事：
1. 调用父类 `PickleHTMLBuilder.init()` 完成基础初始化
2. 初始化模板系统（serializing builder默认不初始化模板，websupport需要模板来渲染sidebar/relbar等部分）
3. 验证使用的是内置模板加载器（BuiltinTemplateLoader），否则抛异常
4. 添加 `websupport.js` 到页面JS文件列表

## set_webinfo 方法

```python
def set_webinfo(self, staticdir, virtual_staticdir, search, storage):
    self.staticdir = staticdir
    self.virtual_staticdir = virtual_staticdir
    self.search = search
    self.storage = storage
```

在构建开始前由 `WebSupport.build()` 调用，将运行时需要的四个关键对象注入builder：
- `staticdir`：静态文件物理输出目录
- `virtual_staticdir`：静态文件Web虚拟路径
- `search`：搜索适配器实例
- `storage`：存储后端实例

## 文档写入流程

### write_doc(docname, doctree)

这是Builder的核心方法，处理单个文档的序列化：

```python
def write_doc(self, docname, doctree):
    destination = StringOutput(encoding='utf-8')
    doctree.settings = self.docsettings
    self.secnumbers = self.env.toc_secnumbers.get(docname, {})
    self.fignumbers = self.env.toc_fignumbers.get(docname, {})
    self.imgpath = '/' + posixpath.join(self.virtual_staticdir, self.imagedir)
    self.dlpath = '/' + posixpath.join(self.virtual_staticdir, '_downloads')
    self.current_docname = docname
    self.docwriter.write(doctree, destination)
    self.docwriter.assemble_parts()
    body = self.docwriter.parts['fragment']
    metatags = self.docwriter.clean_meta
    ctx = self.get_doc_context(docname, body, metatags)
    self.handle_page(docname, ctx, event_arg=doctree)
```

流程步骤：
1. 设置section编号和figure编号（从Sphinx环境获取）
2. 设置图片路径和下载路径为虚拟静态路径（绝对URL格式）
3. 用WebSupportTranslator将doctree翻译为HTML片段
4. 调用 `get_doc_context()` 获取文档上下文（包含body、metatags等）
5. 调用 `handle_page()` 序列化并保存

### _render_page(pagename, addctx, templatename, event_arg)

这是Builder最关键的方法，负责渲染模板并创建pickle字典：

```python
def _render_page(self, pagename, addctx, templatename, event_arg=None):
    ctx = self.globalcontext.copy()
    ctx['pagename'] = pagename
    # 注入pathto、hasdoc、toctree等模板辅助函数
    ctx['pathto'] = pathto  # 自定义路径函数，区分resource和普通链接
    ctx['hasdoc'] = lambda name: name in self.env.all_docs
    ctx['css_tag'] = css_tag  # 生成<link>标签
    ctx['js_tag'] = js_tag    # 生成<script>标签
    # ... 添加sidebars、更新addctx ...
    
    # 创建pickle字典
    doc_ctx = {
        'body': ctx.get('body', ''),
        'title': ctx.get('title', ''),
        'css': ctx.get('css', ''),
        'script': ctx.get('script', ''),
    }
    # 部分渲染模板获取sidebar/relbar/script/css
    template = self.templates.environment.get_template(templatename)
    template_module = template.make_module(ctx)
    for item in ['sidebar', 'relbar', 'script', 'css']:
        if hasattr(template_module, item):
            doc_ctx[item] = getattr(template_module, item)()
    return ctx, doc_ctx
```

**pathto函数的特殊处理**：
- 普通文档链接：使用 `relative_uri(baseuri, otheruri)` 生成相对路径
- 资源文件（CSS/JS/图片）：生成 `/{virtual_staticdir}/{filename}` 绝对路径

### handle_page(pagename, addctx, templatename='page.html', outfilename=None, event_arg)

```python
def handle_page(self, pagename, addctx, templatename='page.html', outfilename=None, event_arg=None):
    ctx, doc_ctx = self._render_page(pagename, addctx, templatename, event_arg)
    if not outfilename:
        outfilename = path.join(self.outdir, 'pickles', os_path(pagename) + self.out_suffix)
    ensuredir(path.dirname(outfilename))
    self.dump_context(doc_ctx, outfilename)
    # 拷贝源文件到staticdir/_sources/
    if ctx.get('sourcename'):
        source_name = path.join(self.staticdir, '_sources', os_path(ctx['sourcename']))
        ensuredir(path.dirname(source_name))
        copyfile(self.env.doc2path(pagename), source_name)
```

`out_suffix` 为 `.fpickle`，每个文档被序列化为 `pickles/{docname}.fpickle`。如果文档有对应的源文件（.rst），拷贝到 `_sources/` 目录用于"显示源码"功能。

## 搜索索引

### load_indexer(docnames)

```python
def load_indexer(self, docnames):
    self.indexer = self.search
    self.indexer.init_indexing(changed=list(docnames))
```

覆盖PickleHTMLBuilder的方法，将Sphinx的默认indexer替换为websupport配置的search适配器。

### write_doc_serialized(docname, doctree)

```python
def write_doc_serialized(self, docname, doctree):
    self.imgpath = '/' + posixpath.join(self.virtual_staticdir, self.imagedir)
    self.post_process_images(doctree)
    title_node = self.env.longtitles.get(docname)
    title = title_node and self.render_partial(title_node)['title'] or ''
    self.index_page(docname, doctree, title)
```

序列化文档后处理图片路径并建立搜索索引。`index_page()` 最终调用 `self.search.feed()` 将文档文本加入搜索索引。

### dump_search_index()

```python
def dump_search_index(self):
    self.indexer.finish_indexing()
```

构建完成时调用，通知搜索适配器完成索引（Whoosh提交写入，Xapian释放数据库锁）。

## 收尾处理（handle_finish）

```python
def handle_finish(self):
    # 获取全局CSS/JS（从空页面渲染提取）
    _, doc_ctx = self._render_page('tmp', {}, 'page.html')
    self.globalcontext['css'] = doc_ctx['css']
    self.globalcontext['script'] = doc_ctx['script']
    super().handle_finish()
    # 移动静态文件到staticdir
    directories = [self.imagedir, '_static']
    for directory in directories:
        src = path.join(self.outdir, directory)
        dst = path.join(self.staticdir, directory)
        if path.isdir(src):
            if path.isdir(dst):
                shutil.rmtree(dst)
            shutil.move(src, dst)
    self.copy_resources()
```

收尾阶段做三件事：
1. 渲染一个空页面提取全局CSS和JS链接，存入globalcontext
2. 调用父类handle_finish完成基础收尾
3. 将 `data/` 下的图片和静态文件目录移动到 `static/` 目录
4. 调用 `copy_resources()` 拷贝websupport自带的资源文件

## 静态资源拷贝

### copy_resources()

```python
RESOURCES = [
    'ajax-loader.gif', 'comment-bright.png', 'comment-close.png', 'comment.png',
    'down-pressed.png', 'down.png', 'up-pressed.png', 'up.png', 'websupport.js',
]

def copy_resources(self):
    dst = path.join(self.staticdir, '_static')
    if path.isdir(dst):
        for resource in RESOURCES:
            src = path.join(package_dir, 'files', resource)
            shutil.copy(src, dst)
```

将websupport包内 `files/` 目录下的9个资源文件（8个图片+1个JS）拷贝到静态文件目录。

## setup函数

```python
def setup(app):
    app.add_builder(WebSupportBuilder)
    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

Sphinx扩展入口函数，注册WebSupportBuilder，声明并行读写安全。

## Pickle输出格式

每个 `.fpickle` 文件包含一个Python字典（通过pickle序列化），结构如下：

```python
{
    'body': '<div class="document">...文档主体HTML...</div>',
    'title': '文档标题',
    'css': '<link rel="stylesheet" href="/static/_static/basic.css" />...',
    'script': '<script src="/static/_static/websupport.js"></script>...',
    'sidebar': '<div class="sphinxsidebar">...侧边栏HTML...</div>',
    'relbar': '<div class="related">...导航栏HTML...</div>',
}
```

`globalcontext.pickle` 包含全局的 `css` 和 `script` 字段（不包含body/title/sidebar/relbar），用于搜索结果页等没有pickle文件的页面。

## 相关概念

- [架构总览](02-architecture-overview.md)
- [WebSupport API 详解](03-websupport-api.md)
- [评论系统](05-comment-system.md)
- [前端集成](08-frontend-integration.md)
