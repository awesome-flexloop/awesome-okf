---
type: Concept
title: 5分钟快速上手
description: 从零开始使用 sphinxext-rediraffe：安装、配置、构建，3步完成页面重定向设置
tags: [sphinxext-rediraffe, getting-started, quickstart, configuration]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# 5分钟快速上手

## 第1步：安装

使用 pip 安装 sphinxext-rediraffe：

```bash
pip install sphinxext-rediraffe
```

## 第2步：添加扩展并配置

在 Sphinx 项目的 `conf.py` 中进行配置。有两种配置重定向的方式：**dict 方式**和**文件方式**。

### 方式A：dict 方式（简单场景推荐）

在 `conf.py` 中直接用字典定义重定向映射：

```python
# conf.py
extensions = [
    'sphinxext.rediraffe',
    # ... 其他扩展
]

rediraffe_redirects = {
    'old-page.rst': 'new-page.rst',
    'legacy/intro.rst': 'guide/introduction.rst',
    'v1/quickstart.rst': 'getting-started.rst',
}
```

字典的 key 是源文件路径（相对于源目录），value 是目标文件路径。

### 方式B：文件方式（推荐用于大量重定向）

使用外部文本文件管理重定向列表：

```python
# conf.py
extensions = [
    'sphinxext.rediraffe',
]

rediraffe_redirects = 'redirects.txt'
```

然后在源目录（与 `conf.py` 同级）创建 `redirects.txt`：

```text
# 这是注释，以 # 开头
old-page.rst new-page.rst
legacy/intro.rst guide/introduction.rst
v1/quickstart.rst getting-started.rst

# 路径含空格时用引号包裹
"old tutorial.rst" "tutorials/first-steps.rst"
'old guide.rst' 'guides/main.rst'
```

文件格式规则：
- 每行一对 `源路径 目标路径`，以空白分隔
- `#` 开头的行为注释
- 路径含空格时用单引号或双引号包裹
- 支持任意数量的空白字符分隔

## 第3步：构建文档

正常构建 Sphinx 文档即可：

```bash
# HTML 构建
sphinx-build -b html docs docs/_build/html

# 目录HTML构建（dirhtml）
sphinx-build -b dirhtml docs docs/_build/dirhtml
```

构建完成后，rediraffe 会在输出目录中自动生成重定向HTML文件。例如，如果配置了 `old-page.rst → new-page.rst`，则：

- **html 构建器**：生成 `old-page.html`，访问时自动跳转到 `new-page.html`
- **dirhtml 构建器**：生成 `old-page/index.html`，访问时自动跳转到 `new-page/index.html`

### 验证重定向生效

构建完成后，可以在输出目录中看到重定向文件：

```bash
# 查看生成的重定向文件
ls docs/_build/html/old-page.html
# 或浏览器直接打开
# file:///path/to/docs/_build/html/old-page.html
```

打开后页面会立即跳转到 `new-page.html`。

## 链式重定向自动处理

如果配置了链式重定向，rediraffe 会自动压缩：

```python
# conf.py
rediraffe_redirects = {
    'a.rst': 'b.rst',
    'b.rst': 'c.rst',
    'c.rst': 'd.rst',
}
```

构建后，`a.html`、`b.html`、`c.html` 都直接跳转到 `d.html`，不会出现 `a→b→c→d` 的多跳重定向。用户访问任意一个旧URL都只经历一次跳转。

## 快速验证清单

完成配置后，按以下清单验证：

1. ✅ `conf.py` 的 `extensions` 列表包含 `'sphinxext.rediraffe'`
2. ✅ `rediraffe_redirects` 配置为 dict 或存在对应的 `redirects.txt` 文件
3. ✅ 构建过程无红色错误信息（循环重定向、目标不存在等会报错）
4. ✅ 构建输出中可以看到 `(good) old-page.html --> new-page.html` 日志
5. ✅ 在浏览器中打开旧URL能正常跳转到新页面
6. ✅ URL查询参数（`?key=value`）和片段（`#section`）在跳转后保留

## 常见问题

**Q: 构建日志显示 `(broken) xxx.html redirects to yyy.html but yyy.html does not exist!`**

A: 目标文件不存在。检查重定向目标路径是否正确，确保目标文档确实在构建输出中生成。

**Q: 构建报 `A circular redirect exists` 错误**

A: 配置中存在循环重定向（如 A→B→A）。检查重定向链路，确保最终指向一个不存在于重定向key中的页面。

**Q: dirhtml构建器重定向路径看起来不对**

A: dirhtml将非index页面转为目录形式（`page.html` → `page/index.html`），这是正常行为。rediraffe会自动处理这种路径差异。

**Q: 重定向文件中可以使用绝对路径吗？**

A: 不可以。重定向路径必须是相对于Sphinx源目录的相对路径。

## 相关概念

- [sphinxext-rediraffe 简介](/concepts/00-introduction.md)
- [架构概览](/concepts/02-architecture-overview.md)
- [重定向图模型](/concepts/03-redirect-graph.md)
- [配置项详解](/concepts/04-configuration.md)
- [基础重定向示例](/examples/basic-redirects.md)
