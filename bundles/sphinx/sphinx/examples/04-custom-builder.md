---
type: "example"
title: "自定义Builder输出Markdown"
description: "实战——创建自定义Builder将Sphinx文档输出为Markdown格式，实现init/write_doc/finish方法、自定义Translator将doctree转为Markdown"
tags: [example, builder, custom-output, markdown, translator]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: builder-base
    resource: /references/builder-base.md
    title: "Builder基类核心方法"
  - id: builder-system
    resource: /concepts/10-builder-system.md
    title: "Builder构建器体系概念"
---

# 自定义Builder输出Markdown

本示例演示如何创建一个自定义Builder，将Sphinx文档输出为Markdown格式。虽然Sphinx有 `sphinx-markdown-builder` 等第三方包，但理解如何从零创建Builder是掌握Sphinx架构的最佳方式。

## 前置知识

- 阅读 [Builder 构建器体系](../concepts/10-builder-system.md)
- 阅读 [项目管理与 Docutils 集成](../concepts/08-project-and-docutils.md)
- 了解Visitor模式（docutils NodeVisitor）

## 核心思路

Builder的职责是：
1. **初始化**：准备输出目录和Writer
2. **读取**：使用基类的文档读取流程
3. **写入**：通过Translator遍历doctree生成目标格式
4. **完成**：生成索引/复制静态文件/清理

我们需要实现：
1. `MarkdownBuilder`：Builder子类
2. `MarkdownTranslator`：NodeVisitor子类，将节点转为Markdown文本
3. `MarkdownWriter`：docutils Writer子类，连接Translator

## 完整实现

```python
# _ext/markdown_builder.py
"""A Sphinx builder that outputs Markdown files."""

from __future__ import annotations

import os
from os import path
from pathlib import Path
from typing import Any

from docutils import nodes
from docutils.io import StringOutput
from sphinx.builders import Builder
from sphinx.util import logging
from sphinx.util.osutil import ensuredir

logger = logging.getLogger(__name__)


class MarkdownTranslator(nodes.NodeVisitor):
    """将docutils节点树翻译为Markdown文本。"""

    def __init__(self, document, builder):
        super().__init__(document)
        self.builder = builder
        self.body = []          # 输出文本片段
        self.section_level = 0  # 当前章节层级
        self.list_level = 0     # 列表嵌套层级
        self.in_code = False    # 是否在代码块中
        self.in_table = False   # 是否在表格中
        self.table_rows = []    # 表格行
        self.table_header = []  # 表头
        self._list_type = []    # 列表类型栈

    # ========== 辅助方法 ==========

    def add(self, text: str) -> None:
        """添加文本到输出"""
        self.body.append(text)

    def ensure_newline(self) -> None:
        """确保当前以换行结尾"""
        if self.body and not self.body[-1].endswith('\n'):
            self.body.append('\n')

    def astext(self) -> str:
        """获取最终输出文本"""
        return ''.join(self.body)

    # ========== 文档结构 ==========

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        self.ensure_newline()

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1
        self.ensure_newline()

    def visit_title(self, node):
        level = min(self.section_level, 6)
        self.add('#' * level + ' ')

    def depart_title(self, node):
        self.add('\n\n')
        raise nodes.SkipNode  # 标题节点自行处理子内容

    # ========== 段落和文本 ==========

    def visit_paragraph(self, node):
        pass

    def depart_paragraph(self, node):
        self.add('\n\n')

    def visit_Text(self, node):
        self.add(node.astext())

    def depart_Text(self, node):
        pass

    def visit_emphasis(self, node):
        self.add('*')

    def depart_emphasis(self, node):
        self.add('*')

    def visit_strong(self, node):
        self.add('**')

    def depart_strong(self, node):
        self.add('**')

    def visit_literal(self, node):
        self.add('`')

    def depart_literal(self, node):
        self.add('`')

    # ========== 代码块 ==========

    def visit_literal_block(self, node):
        language = node.get('language', '')
        self.add(f'```{language}\n')
        self.in_code = True

    def depart_literal_block(self, node):
        self.add('\n```\n\n')
        self.in_code = False

    # ========== 列表 ==========

    def visit_bullet_list(self, node):
        self._list_type.append('bullet')
        self.list_level += 1

    def depart_bullet_list(self, node):
        self._list_type.pop()
        self.list_level -= 1
        self.ensure_newline()

    def visit_enumerated_list(self, node):
        self._list_type.append('enumerated')
        self.list_level += 1
        self._enum_counter = 0

    def depart_enumerated_list(self, node):
        self._list_type.pop()
        self.list_level -= 1
        self.ensure_newline()

    def visit_list_item(self, node):
        indent = '  ' * (self.list_level - 1)
        if self._list_type and self._list_type[-1] == 'bullet':
            self.add(f'{indent}- ')
        else:
            self._enum_counter = getattr(self, '_enum_counter', 0) + 1
            self.add(f'{indent}{self._enum_counter}. ')

    def depart_list_item(self, node):
        if not self.body[-1].endswith('\n'):
            self.add('\n')

    # ========== 链接和引用 ==========

    def visit_reference(self, node):
        uri = node.get('refuri', node.get('refid', ''))
        if uri.startswith('#'):
            self.add('[')
            self._ref_uri = uri
        else:
            self.add('[')
            self._ref_uri = uri

    def depart_reference(self, node):
        uri = getattr(self, '_ref_uri', '')
        self.add(f']({uri})')

    # ========== 图片 ==========

    def visit_image(self, node):
        uri = node.get('uri', '')
        alt = node.get('alt', '')
        self.add(f'![{alt}]({uri})')
        raise nodes.SkipNode

    # ========== 表格 ==========

    def visit_table(self, node):
        self.in_table = True
        self.table_rows = []
        self.table_header = []

    def depart_table(self, node):
        # 输出表格
        if self.table_header:
            self.add('| ' + ' | '.join(self.table_header) + ' |\n')
            self.add('| ' + ' | '.join(['---'] * len(self.table_header)) + ' |\n')
        for row in self.table_rows:
            self.add('| ' + ' | '.join(row) + ' |\n')
        self.add('\n')
        self.in_table = False

    def visit_tgroup(self, node):
        pass

    def depart_tgroup(self, node):
        pass

    def visit_colspec(self, node):
        pass

    def depart_colspec(self, node):
        pass

    def visit_thead(self, node):
        self._in_table_header = True

    def depart_thead(self, node):
        self._in_table_header = False

    def visit_tbody(self, node):
        self._in_table_header = False

    def depart_tbody(self, node):
        pass

    def visit_row(self, node):
        self._current_row = []

    def depart_row(self, node):
        if hasattr(self, '_in_table_header') and self._in_table_header:
            pass  # 标题行在entry中处理
        else:
            self.table_rows.append(self._current_row)

    def visit_entry(self, node):
        self._cell_content = []

    def depart_entry(self, node):
        cell_text = ''.join(self._cell_content).strip()
        if hasattr(self, '_in_table_header') and self._in_table_header:
            self.table_header.append(cell_text)
        else:
            self._current_row.append(cell_text)

    # ========== Sphinx特定节点（简化处理） ==========

    def visit_note(self, node):
        self.add('> **Note**\n> ')

    def depart_note(self, node):
        self.add('\n\n')

    def visit_warning(self, node):
        self.add('> **Warning**\n> ')

    def depart_warning(self, node):
        self.add('\n\n')

    def visit_topic(self, node):
        pass

    def depart_topic(self, node):
        self.ensure_newline()

    def visit_compound(self, node):
        pass

    def depart_compound(self, node):
        pass

    # ========== 未知节点 ==========

    def unknown_visit(self, node):
        """对于不认识的节点，尝试只输出其文本内容"""
        if not isinstance(node, (nodes.container, nodes.generated)):
            pass  # 静默跳过未知节点

    def unknown_departure(self, node):
        pass


class MarkdownWriter:
    """Markdown Writer（docutils接口）"""

    def __init__(self, builder):
        self.builder = builder
        self.output = None
        self.translator_class = MarkdownTranslator

    def translate(self):
        visitor = self.translator_class(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


class MarkdownBuilder(Builder):
    """输出Markdown文件的Builder。"""
    name = 'markdown'
    format = 'markdown'
    epilog = 'Markdown files are in %(outdir)s.'
    out_suffix = '.md'
    allow_parallel = True

    # 默认Translator（用于init阶段）
    default_translator_class = MarkdownTranslator

    def init(self) -> None:
        """Builder初始化"""
        self.output = None
        self.writer = MarkdownWriter(self)

    def get_outdated_docs(self) -> set[str]:
        """返回过时的文档。简单实现：返回所有文档。"""
        return self.env.found_docs

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        """获取文档的目标URI（用于生成链接）"""
        return docname + self.out_suffix

    def prepare_writing(self, docnames: set[str]) -> None:
        """写入前准备"""
        pass

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        """将单个文档写入Markdown文件"""
        # 设置writer的document
        self.writer.document = doctree
        self.writer.translate()
        output = self.writer.output

        # 计算输出路径
        outfilename = path.join(self.outdir, docname + self.out_suffix)
        ensuredir(path.dirname(outfilename))

        # 写入文件
        try:
            with open(outfilename, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.debug(f'Wrote {outfilename}')
        except OSError as e:
            logger.warning(f"Cannot write Markdown file {outfilename}: {e}")

    def finish(self) -> None:
        """构建完成：生成索引文件"""
        # 生成一个简单的index
        index_path = path.join(self.outdir, 'INDEX.md')
        lines = ['# Documentation Index\n\n']

        # 从toctree收集文档列表
        for docname in sorted(self.env.all_docs):
            if docname == 'index':
                title = self.env.titles.get(docname)
                title_text = title.astext() if title else 'Home'
                lines.append(f'- [{title_text}]({docname}{self.out_suffix})\n')
            else:
                title = self.env.titles.get(docname, docname)
                title_text = title.astext() if hasattr(title, 'astext') else title
                lines.append(f'- [{title_text}]({docname}{self.out_suffix})\n')

        with open(index_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        logger.info(f'Markdown index: {index_path}')


def setup(app):
    app.add_builder(MarkdownBuilder)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

## 使用方法

### 1. 启用扩展

在conf.py中添加：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '_ext'))

extensions = ['markdown_builder']
```

### 2. 构建Markdown

```bash
sphinx-build -b markdown docs docs/_build/markdown
```

输出将在 `docs/_build/markdown/` 目录下，每个 `.rst` 文件对应一个 `.md` 文件。

## 扩展与改进

这个示例MarkdownBuilder是一个简化实现。生产环境中你可能需要：

1. **处理更多节点类型**：`note`/`warning`等Sphinx特殊节点、`only`、`deprecated`等指令节点
2. **处理交叉引用**：将内部 `:py:func:\`x\`` 等引用转换为Markdown链接
3. **支持toctree**：将toctree转换为Markdown链接列表
4. **处理Sphinx特定节点**：`desc`、`desc_signature`等描述块节点
5. **复制图片**：在finish()中将图片文件复制到输出目录
6. **更好的表格处理**：对齐信息、合并单元格
7. **目录生成**：支持生成Markdown目录列表

### 复制图片示例

```python
def finish(self):
    # 复制图片文件
    from sphinx.util.console import bold
    logger.info(bold('Copying images...'))
    import shutil
    for src_path, candidates in self.env.images.items():
        for candidate in candidates:
            src = Path(self.srcdir) / candidate
            if src.exists():
                dst = Path(self.outdir) / '_images' / Path(candidate).name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
```

## 关键Builder方法回顾

| 方法 | 必须实现 | 作用 |
|------|---------|------|
| `init()` | ✅ | 初始化Writer、路径等 |
| `get_outdated_docs()` | ✅ | 返回需要构建的文档集合 |
| `get_target_uri()` | ✅ | 生成文档间链接的URI |
| `prepare_writing()` | ✅ | 写入前准备 |
| `write_doc()` | ✅ | 输出单个文档 |
| `finish()` | ✅ | 构建完成（索引、资源复制等） |
| `write_doc_serialized()` | 并行构建需要 | 序列化文档数据（子进程写入主进程合并） |

## 现有第三方Markdown Builders

如果你需要生产级Markdown输出，可以使用：
- `sphinx-markdown-builder`：pip install sphinx-markdown-builder
- `MyST-NB`/`MyST-Parser`：Markdown-first方案，使用Markdown作为源格式
- `sphinxcontrib-mermaid`等扩展补充特定功能

## 相关资源

- [Builder 构建器体系](../concepts/10-builder-system.md)
- [项目管理与 Docutils 集成](../concepts/08-project-and-docutils.md)
- [扩展开发详解](../concepts/15-extension-development.md)
