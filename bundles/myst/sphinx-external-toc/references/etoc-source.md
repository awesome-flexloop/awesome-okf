---
type: Reference
title: sphinx-external-toc 源码路径映射
description: sphinx-external-toc 核心源文件路径、数据模型与配置选项索引
tags: [sphinx, sphinx-extension, toctree, navigation, source, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:05:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: etoc-repo
    resource: https://github.com/executablebooks/sphinx-external-toc
    title: sphinx-external-toc GitHub Repository
---

# sphinx-external-toc 源码路径映射

本文档为 sphinx-external-toc 源码的文件级索引，标注每个核心文件的路径、职责和关键代码。源路径相对于 `external/libs/ai/executablebooks/sphinx-external-toc/`。

## 核心文件清单

| 文件 | 行数 | 职责 | 关键代码 |
|------|------|------|---------|
| `sphinx_external_toc/__init__.py` | 51 行 | 扩展入口、配置注册、事件/指令/Transform 注册 | `setup()` L11-51 |
| `sphinx_external_toc/api.py` | 264 行 | 数据模型定义（SiteMap/Document/TocTree/UrlItem/FileItem/GlobItem） | `SiteMap` L124-264、`TocTree` L47-92、`Document` L95-121 |
| `sphinx_external_toc/parsing.py` | 450 行 | YAML 解析与序列化、FileFormat 定义、MalformedError | `parse_toc_yaml()` L84-93、`parse_toc_data()` L96-130、`FILE_FORMATS` L65-77 |
| `sphinx_external_toc/events.py` | 344 行 | Sphinx 事件钩子、tableofcontents 指令、InsertToctrees Transform | `parse_toc_to_env()` L59-124、`insert_toctrees()` L164-302、`InsertToctrees` L305-315 |
| `sphinx_external_toc/collectors.py` | 253 行 | 自定义 TocTreeCollector（编号样式支持）、禁用内置 Collector | `disable_builtin_toctree_collector()` L8-19、`TocTreeCollectorWithStyles` L22-253 |
| `sphinx_external_toc/cli.py` | ~120 行 | CLI 命令行工具（parse/to-project 等子命令） | `main()` L19-22、`parse_toc()` L25-30 |
| `sphinx_external_toc/tools.py` | 工具函数 | 创建站点、从路径生成 sitemap、Jupyter Book 迁移 | — |
| `sphinx_external_toc/_compat.py` | 兼容层 | 跨版本 dataclass/typing 兼容 | — |

## 数据模型层级

```
SiteMap (MutableMapping)
├── root: Document
├── meta: Dict
├── file_format: str
└── _docs: Dict[str, Document]
    └── Document
        ├── docname: str
        ├── title: Optional[str]
        └── subtrees: List[TocTree]
            └── TocTree
                ├── items: List[FileItem | GlobItem | UrlItem]
                ├── caption: Optional[str]
                ├── hidden: bool = True
                ├── maxdepth: int = -1
                ├── numbered: bool | int = False
                ├── reversed: bool = False
                ├── titlesonly: bool = False
                ├── style: str | List[str] = "numerical"
                └── restart_numbering: Optional[bool] = None
```

## 配置项速查表

| 配置项 | 类型 | 默认值 | 重建条件 | 说明 |
|--------|------|--------|---------|------|
| `external_toc_path` | str | `"_toc.yml"` | env | 外部 ToC 文件路径（相对于源目录） |
| `external_toc_exclude_missing` | bool | `False` | env | 是否将不在 ToC 中的文件加入排除列表 |
| `use_multitoc_numbering` | bool | `True` | env | 多 toctree 间是否连续编号 |

## setup() 函数源码参考

```python
def setup(app: "Sphinx") -> dict:
    app.setup_extension("sphinx_multitoc_numbering")
    
    from .collectors import TocTreeCollectorWithStyles, disable_builtin_toctree_collector
    from .events import InsertToctrees, TableofContents, add_changed_toctrees, ensure_index_file, parse_toc_to_env
    
    # 禁用内置 collector，注册自定义 collector
    disable_builtin_toctree_collector(app)
    app.add_env_collector(TocTreeCollectorWithStyles)
    
    # 配置项
    app.add_config_value("external_toc_path", "_toc.yml", "env")
    app.add_config_value("external_toc_exclude_missing", False, "env")
    try:
        app.add_config_value("use_multitoc_numbering", True, "env")
    except Exception:
        pass
    
    # 事件钩子
    app.connect("config-inited", parse_toc_to_env, priority=900)
    app.connect("env-get-outdated", add_changed_toctrees)
    app.add_directive("tableofcontents", TableofContents)
    app.add_transform(InsertToctrees)
    app.connect("build-finished", ensure_index_file)
    
    return {"version": __version__, "parallel_read_safe": True}
```

## _toc.yml 格式速查

### default 格式

```yaml
root: index
defaults:
  titlesonly: true
subtrees:
  - caption: 章节标题
    entries:
      - file: doc1
      - file: doc2
        entries:
          - file: doc2a
          - file: doc2b
      - glob: pattern/*
      - url: https://example.com
        title: 外部链接
```

### Shorthand 语法（单 subtree）

```yaml
root: index
options:
  caption: 章节标题
entries:
  - file: doc1
  - file: doc2
```

### jb-book 格式

```yaml
format: jb-book
root: index
parts:
  - caption: 第一部分
    chapters:
      - file: chapter1
      - file: chapter2
        sections:
          - file: chapter2a
```

## 相关概念

- [_toc.yml 语法详解](/concepts/02-toc-yaml-syntax.md)
- [扩展工作机制](/concepts/03-extension-mechanism.md)
- [高级功能](/concepts/04-advanced-features.md)
