---
type: Example
title: 基础重定向配置
description: 从零开始配置sphinxext-rediraffe，包括dict方式和文件方式、链式重定向、嵌套目录重定向
tags: [sphinxext-rediraffe, basic-usage, redirects, dict, file-config]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# 基础重定向配置

本示例演示 sphinxext-rediraffe 的基础使用方式，覆盖最常见的重定向场景。

## 前置条件

- Python >= 3.9
- Sphinx >= 6.0
- 已有一个可正常构建的Sphinx文档项目

## 示例1：dict方式配置（快速上手）

适用于重定向数量较少的场景。

### conf.py

```python
# conf.py
extensions = [
    'sphinxext.rediraffe',
]

# 简单的重定向映射
rediraffe_redirects = {
    'old-quickstart.rst': 'getting-started.rst',
    'tutorials/basic.rst': 'tutorials/first-steps.rst',
    'api/old-module.rst': 'api/new-module.rst',
}
```

### 构建验证

```bash
sphinx-build -b html . _build/html
```

构建日志中应该能看到：

```
(good) old-quickstart.html --> getting-started.html
(good) tutorials/basic.html --> tutorials/first-steps.html
(good) api/old-module.html --> api/new-module.html
```

### 验证重定向

```bash
# 检查重定向文件是否生成
ls _build/html/old-quickstart.html

# 用curl检查meta refresh标签
grep -o 'http-equiv="refresh".*url=[^"]*' _build/html/old-quickstart.html
# 输出: http-equiv="refresh" content="0; url=getting-started.html"
```

## 示例2：文件方式配置（推荐）

适用于重定向数量较多或需要被自动追加（writediff）的场景。

### conf.py

```python
# conf.py
extensions = [
    'sphinxext.rediraffe',
]

rediraffe_redirects = 'redirects.txt'
```

### redirects.txt

在 `conf.py` 同级目录创建 `redirects.txt`：

```text
# 简单重定向
old-quickstart.rst getting-started.rst
tutorials/basic.rst tutorials/first-steps.rst

# 路径含空格，使用引号
"old tutorial.rst" "tutorials/first steps.rst"
'old guide.rst' 'guides/main guide.rst'

# 嵌套目录
legacy/v1/intro.rst guide/v1/introduction.rst
legacy/v2/intro.rst guide/v2/introduction.rst

# 含特殊字符的路径
"what's new.rst" changelog.rst
"q&a.rst" faq.rst
```

### 文件格式规则

- 每行格式：`源路径 目标路径`
- 空白字符（空格、Tab）均可作为分隔符
- 多个连续空白字符等同于一个
- `#` 开头的行为注释
- 路径含空格时必须用单引号或双引号包裹
- 引号内的路径可以包含另一种引号（如 `"it's file.rst"`）

### 构建验证

```bash
sphinx-build -b html . _build/html
```

## 示例3：链式重定向（自动压缩）

rediraffe 自动处理链式重定向，确保用户只跳转一次。

### redirects.txt

```text
# 链式重定向：a → b → c → d（最终页）
a.rst b.rst
b.rst c.rst
c.rst d.rst

# 单跳重定向
e.rst f.rst
```

### 构建结果

构建后，三个源页面都直接跳转到 `d.html`：

```
(good) a.html --> d.html
(good) b.html --> d.html
(good) c.html --> d.html
(good) e.html --> f.html
```

用户访问 `a.html` 时不会经历 a→b→c→d 三次跳转，而是直接跳转到 d.html。

### 验证链式压缩

```python
# 可以通过Python直接验证 create_simple_redirects 的行为
from sphinxext.rediraffe import create_simple_redirects

graph = {'a.rst': 'b.rst', 'b.rst': 'c.rst', 'c.rst': 'd.rst'}
result = create_simple_redirects(graph)
# result = {'a.rst': 'd.rst', 'b.rst': 'd.rst', 'c.rst': 'd.rst'}
```

## 示例4：嵌套目录重定向

处理多级目录中的页面移动。

### 场景描述

原始目录结构：
```
docs/
├── index.rst
├── old-section/
│   ├── page1.rst
│   └── page2.rst
└── guides/
    └── old-guide.rst
```

重构后的目录结构：
```
docs/
├── index.rst
├── tutorials/
│   ├── lesson1.rst
│   └── lesson2.rst
└── howto/
    └── main-guide.rst
```

### redirects.txt

```text
old-section/page1.rst tutorials/lesson1.rst
old-section/page2.rst tutorials/lesson2.rst
guides/old-guide.rst howto/main-guide.rst
```

### dirhtml构建器的注意事项

使用 dirhtml 构建器时，重定向文件会生成为目录形式：

```bash
sphinx-build -b dirhtml . _build/dirhtml

# 生成的重定向结构：
# _build/dirhtml/old-section/page1/index.html → 跳转到 ../../tutorials/lesson1/index.html
```

rediraffe 自动计算正确的相对路径，无需手动调整。

## 示例5：dict方式配置链式重定向

dict配置同样支持链式压缩：

```python
# conf.py
rediraffe_redirects = {
    'v1/quickstart.rst': 'v2/quickstart.rst',
    'v2/quickstart.rst': 'getting-started.rst',
    'install.rst': 'getting-started.rst',
}
```

构建后：
- `v1/quickstart.html` → `getting-started.html`（链式压缩）
- `v2/quickstart.html` → `getting-started.html`（链式压缩）
- `install.html` → `getting-started.html`

## 常见错误与排查

### 错误：循环重定向

```python
# ❌ 错误配置
rediraffe_redirects = {
    'a.rst': 'b.rst',
    'b.rst': 'a.rst',
}
```

构建报错：
```
rediraffe: A circular redirect exists. Links involved: a -> b -> a
Extension error...
```

解决：确保重定向链最终指向一个不在key中的页面。

### 错误：目标不存在

```python
# ❌ 目标路径拼写错误
rediraffe_redirects = {
    'old.rst': 'new-page-typo.rst',
}
```

构建警告：
```
(broken) old.html redirects to new-page-typo.html but _build/html/new-page-typo.html does not exist!
```

解决：检查目标文件是否存在且未被 `exclude_patterns` 排除。

### 错误：源文件已存在

```python
# ❌ old-page.rst 仍然存在于源目录中
rediraffe_redirects = {
    'old-page.rst': 'new-page.rst',
}
```

构建警告：
```
(broken) old-page.html redirects to new-page.html but _build/html/old-page.html already exists!
```

解决：重定向源页面必须被删除或重命名，不能仍然存在于源目录中。

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [重定向图模型](/concepts/03-redirect-graph.md)
- [配置项详解](/concepts/04-configuration.md)
- [路径处理与跨平台兼容](/concepts/07-path-and-cross-platform.md)
- [CI Diff检查集成](/examples/diff-checker-ci.md)
