---
type: "reference"
title: "Builder 基类核心方法"
description: "Builder 基类的类属性、初始化和核心构建方法源码"
tags: [core, builder, output]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: "builder-base", resource: "sphinx/builders/__init__.py", title: "Builder class" }
---

# Builder 基类核心方法

源码位置：`sphinx/builders/__init__.py`

## Builder 类属性

```python
class Builder:
    name: ClassVar[str] = ''                    # 构建器名称（命令行选择用）
    format: ClassVar[str] = ''                  # 输出格式（文件扩展名）
    epilog: ClassVar[str] = ''                  # 构建成功后的消息模板
    default_translator_class: ClassVar[type]    # 默认Translator类
    versioning_method: ClassVar[str] = 'none'   # 版本化方法
    versioning_compare: ClassVar[bool] = False  # 是否比较版本
    allow_parallel: ClassVar[bool] = False      # 是否支持并行write_doc
    use_message_catalog: ClassVar[bool] = True  # 是否使用消息目录
    supported_image_types: ClassVar[list[str]] = []  # 支持的图片MIME类型
    supported_remote_images: ClassVar[bool] = False
    supported_data_uri_images: ClassVar[bool] = False
    phase: BuildPhase = BuildPhase.INITIALIZATION
```

## Builder 核心方法

### 初始化

```python
def __init__(self, app: Sphinx, env: BuildEnvironment) -> None:
    # 从app复制路径属性
    self.srcdir = app.srcdir
    self.confdir = app.confdir
    self.outdir = app.outdir
    self.doctreedir = app.doctreedir
    self._app = app
    self.env = env
    self.env.set_versioning_method(self.versioning_method, self.versioning_compare)
    self.events = app.events
    self.config = app.config
    self.tags = app.tags
    # 添加format/name/builder_/format_标签
    self.tags.add(self.format)
    self.tags.add(self.name)
    self.tags.add(f'format_{self.format}')
    self.tags.add(f'builder_{self.name}')
```

### 构建入口方法

```python
def build_all(self) -> None:
    """构建所有文档（全量构建）"""

def build_specific(self, filenames: list[Path]) -> None:
    """只构建指定文件"""

def build_update(self) -> None:
    """增量构建——只构建过时的文档"""
```

### 构建阶段方法

```python
def init(self) -> None:
    """Builder初始化，子类必须实现"""

def get_outdated_docs(self) -> Iterator[str]:
    """返回过时文档的迭代器"""

def prepare_writing(self, docnames: set[str]) -> None:
    """写入前准备"""

def write_doc(self, docname: str, doctree: nodes.document) -> None:
    """写入单个文档，子类必须实现"""

def write_doc_serialized(self, docname: str, doctree: nodes.document) -> None:
    """序列化写入部分（用于并行构建）"""

def finish(self) -> None:
    """构建完成后的收尾工作"""

def cleanup(self) -> None:
    """最终清理"""
```

### 构建流程（build方法）

Builder 的构建遵循以下阶段（BuildPhase枚举）：
1. `INITIALIZATION` — 初始化
2. `READING` — 读取源文件（builder.phase设置）
3. `WRITING` — 写入输出
4. `FINISHING` — 收尾

## 内置构建器列表

| 名称 | 格式 | 文件 | 说明 |
|------|------|------|------|
| `html` | html | `builders/html/__init__.py` | HTML输出（主要构建器） |
| `dirhtml` | html | `builders/dirhtml.py` | 目录式HTML（每个文档一个目录/index.html） |
| `singlehtml` | html | `builders/singlehtml.py` | 单页HTML（所有内容合为一页） |
| `latex` | latex | `builders/latex/__init__.py` | LaTeX/PDF输出 |
| `text` | text | `builders/text.py` | 纯文本输出 |
| `man` | man | `builders/manpage.py` | man手册页 |
| `texinfo` | texinfo | `builders/texinfo.py` | Texinfo格式 |
| `epub3` | epub | `builders/epub3.py` | EPUB3电子书 |
| `xml` | xml | `builders/xml.py` | XML输出 |
| `gettext` | gettext | `builders/gettext.py` | gettext POT文件（i18n） |
| `linkcheck` | linkcheck | `builders/linkcheck.py` | 链接检查 |
| `changes` | changes | `builders/changes.py` | 变更日志 |
| `dummy` | dummy | `builders/dummy.py` | 空构建器（用于调试） |
