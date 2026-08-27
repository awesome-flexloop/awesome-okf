---
type: "concept"
title: "Builder 构建器体系"
description: "Builder基类核心方法、13种内置Builder、构建三阶段(READING/WRITING/FINISHING)、build_all/build_update/build_specific模式、parallel并行构建"
tags: [core, builder, output, build-pipeline, formats]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: builder-base
    resource: /references/builder-base.md
    title: "Builder基类核心方法"
  - id: events
    resource: /references/event-lifecycle.md
    title: "核心事件列表与触发时机"
---

# Builder 构建器体系

Builder（构建器）是 Sphinx 中负责将解析后的文档树输出为目标格式的组件，定义在 sphinx/builders/__init__.py。不同的输出格式对应不同的 Builder 子类——HTML、LaTeX、EPUB、纯文本、man手册等。Builder 控制构建流程的执行节奏，是 READING→WRITING→FINISHING 三阶段的驱动者。

## Builder 基类

### 类属性

每个 Builder 子类必须定义以下类属性 [F-043]：

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | Builder名称，用于 `-b` 参数选择（如'html'、'latex'） |
| `format` | `str` | 输出格式标识（如'html'、'latex'、'text'） |
| `epilog` | `str` | 构建完成后打印的消息模板（可使用`{outdir}`等占位符） |
| `allow_parallel` | `bool` | 是否支持并行构建 |
| `default_translator_class` | `type` | 默认的Translator（NodeVisitor）类 |

### 核心属性

```python
class Builder:
    app: Sphinx                    # 应用实例
    env: BuildEnvironment          # 构建环境
    config: Config                 # 配置
    srcdir: str                    # 源目录
    confdir: str                   # 配置目录
    outdir: str                    # 输出目录
    doctreedir: str                # doctree缓存目录
    finish_tasks: dict             # 完成任务
    _events: dict                  # Builder专用事件
```

### 核心方法

Builder 的方法按照构建流程组织 [F-044]：

**初始化阶段**：
| 方法 | 说明 |
|------|------|
| `init()` | Builder初始化（设置路径、初始化数据结构） |
| `get_outdated_docs()` | 返回过时文档列表 |
| `get_asset_paths()` | 返回静态资源路径 |

**READING阶段**：
| 方法 | 说明 |
|------|------|
| `build_all()` | 全量构建（读取所有文档） |
| `build_specific(filenames)` | 构建指定文件 |
| `build_update()` | 增量构建（只读取过时文档） |
| `read_doc(docname)` → `read_documents()` | 读取并解析单个文档 → 批量读取 |

**WRITING阶段**：
| 方法 | 说明 |
|------|------|
| `prepare_writing(docnames)` | 写入前准备（初始化Writer/Translator） |
| `write_doc(docname, doctree)` | 将单个文档写入输出 |
| `write_doc_serialized(docname, doctree)` | 序列化支持（用于并行构建后在主进程写入） |
| `write_doctree(docname, doctree)` | 将doctree写入pickle缓存 |

**FINISHING阶段**：
| 方法 | 说明 |
|------|------|
| `finish()` | 生成索引、搜索页、复制静态文件等收尾工作 |
| `cleanup()` | 清理临时资源 |

**工具方法**：
| 方法 | 说明 |
|------|------|
| `get_target_uri(docname, typ=None)` | 获取文档的目标URI（用于生成链接） |
| `get_relative_uri(from_, to, typ=None)` | 获取两个文档间的相对URI |
| `create_translator()` | 创建Translator实例（委托给registry） |

## 13种内置 Builder

### HTML系列（4种）

| Builder | 模块 | name | 输出说明 |
|---------|------|------|---------|
| **StandaloneHTMLBuilder** | `builders/html/__init__.py` | `html` | 标准HTML网站，每个文档生成独立HTML文件，默认Builder |
| **DirectoryHTMLBuilder** | `builders/dirhtml.py` | `dirhtml` | 目录式HTML：`page.html` → `page/index.html`，URL更"干净" |
| **SingleFileHTMLBuilder** | `builders/singlehtml.py` | `singlehtml` | 所有内容合并到一个HTML文件 |
| **SerializedHTMLBuilder** | `sphinxcontrib.serializinghtml` | `html` | 序列化为JSON/Pickle格式（用于全文搜索、自定义后处理） |

### 文档出版系列（3种）

| Builder | 模块 | name | 输出说明 |
|---------|------|------|---------|
| **LaTeXBuilder** | `builders/latex/__init__.py` | `latex` | 生成LaTeX源文件，可编译为PDF |
| **EPUB3Builder** | `builders/epub3.py` | `epub3` | 生成EPUB3格式电子书 |
| **TexinfoBuilder** | `builders/texinfo.py` | `texinfo` | 生成GNU Texinfo格式（用于Info文档） |

### 文本系列（3种）

| Builder | 模块 | name | 输出说明 |
|---------|------|------|---------|
| **TextBuilder** | `builders/text.py` | `text` | 纯文本输出 |
| **ManualPageBuilder** | `builders/manpage.py` | `manpage` | Unix man手册页格式（groff） |
| **XMLBuilder** | `builders/xml.py` | `xml` | XML格式（docutils原生XML） |

### 工具系列（3种）

| Builder | 模块 | name | 输出说明 |
|---------|------|------|---------|
| **GettextBuilder** | `builders/gettext.py` | `gettext` | 生成POT翻译模板（.pot文件） |
| **CheckExternalLinksBuilder** | `builders/linkcheck.py` | `linkcheck` | 检查所有外部链接的可达性，不生成文档 |
| **DummyBuilder** | `builders/dummy.py` | `dummy` | 解析所有文档但不输出任何文件（用于测试/性能分析） |

### 变更日志Builder

| Builder | 模块 | name | 输出说明 |
|---------|------|------|---------|
| **ChangesBuilder** | `builders/changes.py` | `changes` | 收集所有版本变更指令（versionadded/deprecated等）输出 |

## 构建流程详解

### 构建入口

`Sphinx.build(force_all, filenames)` 选择构建模式并启动 [F-045]：

```python
def build(self, force_all=False, filenames=()):
    self.builder.phase = BuildPhase.READING
    if force_all:
        self.builder.build_all()
    elif filenames:
        self.builder.build_specific(filenames)
    else:
        self.builder.build_update()
    self.builder.phase = BuildPhase.FINISHING
    self.emit('build-finished', None)
```

### BuildPhase

构建过程有三个阶段，由 `Builder.phase` 属性标记：

```python
class BuildPhase(Enum):
    INITIALIZATION = 0
    READING = 1
    WRITING = 2
    FINISHING = 3
```

### build_update()：增量构建流程

增量构建是最常用的模式，其流程为 [F-046]：

1. **环境准备**：
   - 加载/创建 BuildEnvironment（pickle缓存）
   - emit('config-inited')
   - Project.discover() 发现所有源文件

2. **判断过时文档**：
   - 检查config_status（配置/扩展是否变化）
   - emit('env-get-outdated') 获取扩展标记的过时文档
   - 遍历all_docs，比较文件mtime
   - 追踪依赖链（dependencies/files_to_rebuild）
   - 得到 `updated_docnames` 集合

3. **读取文档（READING）**：
   - emit('env-before-read-docs', docnames)
   - 对每个过时docname：
     - 读取源文件内容
     - emit('source-read')
     - Parser.parse() → doctree
     - 应用SphinxTransforms
     - env.process_doc() 收集域数据
     - emit('doctree-read')
     - pickle.dump(doctree)到disk
   - emit('env-updated')
   - emit('env-check-consistency')

4. **写入文档（WRITING）**：
   - emit('write-started', builder)
   - builder.prepare_writing(docnames)
   - 对每个docname（或all_docs）：
     - 反序列化doctree
     - 应用PostTransforms
     - emit('doctree-resolved')
     - 处理missing-reference
     - builder.write_doc(docname, doctree)
   - builder.finish() → 生成索引/搜索/复制静态文件

### build_all()：全量构建

全量构建跳过过时文档判断，直接读取所有文档：
- `env.found_docs` = Project.discover()
- 对所有docname调用read_doc()
- 其余流程与build_update相同

### build_specific()：指定文件构建

只构建用户指定的文件：
- 转换文件路径为docnames
- 只读取这些docname
- 写入所有文档（不仅是指定文件）——因为全局索引/搜索需要完整数据

## 并行构建

Builder 支持通过 `-j N` 参数启用多进程并行构建 [F-047]：

```bash
sphinx-build -j 4 -b html docs _build/html
```

并行构建分为两个阶段：

1. **并行READING**：在 `parallel` 个子进程中并行读取文档，每个子进程有自己的BuildEnvironment副本
2. **串行MERGE**：主进程合并子进程的domaindata（通过 `merge_domaindata()`）
3. **串行WRITING**：写入阶段在主进程中串行执行（或根据Builder实现并行写入）

支持并行的扩展必须在setup()返回值中声明：
```python
return {
    'parallel_read_safe': True,   # 是否支持并行读取
    'parallel_write_safe': True,  # 是否支持并行写入
}
```

`parallel_read_safe=None`（未声明）会触发警告。

## 自定义 Builder

创建自定义Builder需要继承Builder基类或其子类，并实现必要的方法：

```python
from sphinx.builders import Builder
from docutils.io import StringOutput

class MyCustomBuilder(Builder):
    name = 'myformat'
    format = 'myformat'
    epilog = 'Build finished. Output in {outdir}.'

    def init(self):
        self.output = StringOutput(encoding='utf-8')

    def get_outdated_docs(self):
        return self.env.found_docs  # 简单实现：每次全量构建

    def write_doc(self, docname, doctree):
        # 使用自定义Visitor遍历doctree生成输出
        self.writer = MyWriter(self)
        self.writer.write(doctree, self.output)
        # 写入文件
        path = self.outdir / (docname + self.out_suffix)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.output.destination, encoding='utf-8')

    def finish(self):
        self.finish_tasks.add_task(self.copy_static_files)
        # 生成索引等
```

然后通过 `app.add_builder(MyCustomBuilder)` 注册。

## 设计洞察

1. **模板方法模式**：Builder基类定义了构建算法的骨架（init→read→write→finish），子类通过重写具体步骤来实现不同输出格式，而不需要改变构建流程的结构。

2. **增量构建的核心**：BuildEnvironment的pickle缓存 + mtime比较 + 依赖追踪，使得Sphinx在大型项目中仍能保持可接受的构建速度。

3. **Phase状态机**：BuildPhase枚举使得Transform和扩展可以感知当前构建阶段，在不同阶段执行不同逻辑（例如，某些Transform只在READING阶段应用）。

4. **并行构建的"读并行写串行"模式**：读取阶段天然可并行（各文档独立解析），但写入阶段涉及全局数据（索引、搜索、交叉引用），通常需要在主进程合并数据后串行执行。

5. **epilog作为用户反馈**：每个Builder定义自己的epilog消息，在构建完成后告诉用户"HTML页面在xxx目录"、"LaTeX文件在xxx目录"，提供良好的用户体验。

## 相关概念

- [架构总览](02-architecture-overview.md)
- [Sphinx应用类](03-application-class.md)
- [构建环境](07-build-environment.md)
- [HTML 构建器详解](11-html-builder.md)
- [项目管理与 Docutils 集成](08-project-and-docutils.md)
