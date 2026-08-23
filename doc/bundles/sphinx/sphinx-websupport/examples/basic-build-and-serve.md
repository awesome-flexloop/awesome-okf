---
okf_version: "0.2"
type: "example"
title: "基本构建与文档服务"
sources: ["sphinxcontrib/websupport/core.py", "tests/test_websupport.py"]
---

# 基本构建与文档服务

本示例演示 sphinxcontrib-websupport 最基础的使用流程：初始化 WebSupport 对象、构建文档、获取文档数据。对应概念：[WebSupport API](../concepts/03-websupport-api.md)、[Builder 系统](../concepts/04-builder-system.md)。

## 前置条件

```bash
pip install sphinxcontrib-websupport sphinx
```

需要一个 Sphinx 文档源码目录（包含 `conf.py` 和 `.rst` 文件）。

## 完整示例

```python
"""
sphinxcontrib-websupport 基本构建与文档服务示例。

引用事实：
- WebSupport 是唯一入口类，所有交互通过它完成
- build() 方法执行 Sphinx 构建，生成 pickle 数据和搜索索引
- get_document() 返回文档的 title/body/sidebar/relbar 数据
- 默认使用 SQLite 存储，数据库位于 datadir/db/websupport.db
"""

from sphinxcontrib.websupport import WebSupport


def build_docs(srcdir: str, builddir: str):
    """第一步：构建文档。

    从 srcdir 读取 reStructuredText 源码，构建 pickle 文档数据、
    搜索索引，并将节点信息存入数据库。

    参数:
        srcdir: Sphinx 文档源码目录（含 conf.py）
        builddir: 构建输出目录（data/static/doctrees 子目录将自动创建）
    """
    support = WebSupport(
        srcdir=srcdir,
        builddir=builddir,
        search='null',          # 不启用搜索（也可用 'whoosh'）
        # storage=None,         # 默认使用 SQLite
        # docroot='',           # 文档 URL 前缀
        # staticroot='static',  # 静态文件 URL 前缀
    )
    support.build()
    print(f"文档构建完成，输出目录: {builddir}")
    return support


def serve_document(builddir: str, docname: str = 'contents'):
    """第二步：获取并展示文档数据。

    构建完成后，不需要 srcdir 即可从 builddir 加载文档数据。
    get_document() 返回字典包含：
    - title: 文档标题
    - body: HTML 正文
    - sidebar: 侧边栏 HTML
    - relbar: 导航栏 HTML

    参数:
        builddir: 构建输出目录
        docname: 文档名（不含扩展名），默认为 'contents'
    """
    # 运行阶段不需要 srcdir
    support = WebSupport(
        builddir=builddir,
        search='null',
    )

    # 获取文档数据
    contents = support.get_document(docname)

    print(f"文档标题: {contents['title']}")
    print(f"正文长度: {len(contents['body'])} 字符")
    print(f"侧边栏长度: {len(contents['sidebar'])} 字符")

    return contents


def get_comments(builddir: str, node_id: str, username: str = None):
    """获取指定节点的评论数据。

    get_data() 返回评论树、源文本等数据。
    传入 username 可获取该用户的投票状态。
    传入 moderator=True 可看到待审核和已删除的评论。
    """
    support = WebSupport(builddir=builddir)
    data = support.get_data(node_id, username=username)
    return data


if __name__ == '__main__':
    import tempfile
    import os

    # 使用测试文档目录（Sphinx 自带的测试根目录）
    # 实际使用时替换为你的 Sphinx 文档源码路径
    demo_srcdir = os.path.join(
        os.path.dirname(__file__), 'docs-source'
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        builddir = os.path.join(tmpdir, 'websupport-build')

        # 如果有源码目录则构建，否则仅演示 API 结构
        if os.path.isdir(demo_srcdir):
            support = build_docs(demo_srcdir, builddir)
            contents = serve_document(builddir, 'index')
            print("\n文档加载成功！")
        else:
            print("提示：请将 srcdir 指向你的 Sphinx 文档目录")
            print("典型的 Sphinx 文档目录结构：")
            print("  docs/")
            print("  ├── conf.py")
            print("  ├── index.rst")
            print("  └── ... (其他 .rst 文件)")
```

## 代码说明

1. **构建阶段（build）**：需要 `srcdir`（源码目录），执行 Sphinx 构建流程。WebSupport 内部使用 `websupport` builder，将文档序列化为 pickle 文件，并为每个可评论节点分配唯一 ID 存入数据库。

2. **运行阶段（serve）**：不需要 `srcdir`，仅需 `builddir` 即可加载已构建的数据。这是生产环境的典型模式——构建在 CI/CD 中完成，Web 服务器仅加载构建产物。

3. **get_document() 返回值**：返回的字典包含渲染 HTML 所需的所有片段，Web 应用只需将这些片段嵌入页面模板即可。

4. **默认存储**：不指定 storage 参数时，自动在 `builddir/data/db/websupport.db` 创建 SQLite 数据库。

## 目录结构

构建完成后，`builddir` 目录结构如下：

```
builddir/
├── data/
│   ├── db/
│   │   └── websupport.db      # SQLite 数据库（评论、节点、投票）
│   ├── search/                # 搜索索引（Whoosh/Xapian 时创建）
│   └── *.pickle               # 序列化的文档数据
├── doctrees/                  # Sphinx doctree 缓存
└── static/                    # 静态文件（websupport.js、CSS 等）
```

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `RuntimeError` | build() 时未提供 srcdir | 构建阶段必须设置 srcdir 参数 |
| `DocumentNotFoundError` | 请求的 docname 不存在 | 检查 docname 拼写，确认文档已构建 |
| `ImportError: sqlalchemy` | 未安装 SQLAlchemy | `pip install sqlalchemy whoosh` |
