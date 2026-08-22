---
type: Concept
title: Docutils 独立使用
description: 脱离 Sphinx 使用 mystnb-docutils-* CLI 工具和 Python API 转换 Notebook
tags: [myst-nb, docutils, standalone, cli, api]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## Docutils 独立使用

MyST-NB 同样支持脱离 Sphinx 的 Docutils 独立模式，通过 CLI 工具或 Python API 将 Notebook（.ipynb/.md）直接转换为 HTML/LaTeX/XML 等格式。

## CLI 工具

MyST-NB 提供 5 个 mystnb-docutils-* 命令：

| 命令 | 功能 |
|------|------|
| `mystnb-docutils-html` | Notebook → HTML |
| `mystnb-docutils-html5` | Notebook → HTML5 |
| `mystnb-docutils-latex` | Notebook → LaTeX |
| `mystnb-docutils-xml` | Notebook → Docutils XML |
| `mystnb-docutils-pseudoxml` | Notebook → Pseudo-XML（调试 AST） |

### 基本用法

```bash
# .ipynb → HTML5
mystnb-docutils-html5 notebook.ipynb output.html

# 文本格式 .md → HTML5
mystnb-docutils-html5 notebook.md output.html

# 从 stdin 读取
echo '```{code-cell}\nprint("hi")\n```' | mystnb-docutils-html5
```

### 启用扩展

```bash
mystnb-docutils-html5 \
  --myst-enable-extensions=dollarmath,colon_fence \
  --nb-execution-mode=off \
  notebook.ipynb
```

### 执行模式

```bash
# 不执行（使用已有输出）
mystnb-docutils-html5 --nb-execution-mode=off notebook.ipynb

# 强制执行
mystnb-docutils-html5 --nb-execution-mode=force notebook.ipynb
```

## 其他 CLI 工具

### mystnb-quickstart

创建 MyST-NB 项目模板：

```bash
mystnb-quickstart my-project
cd my-project
sphinx-build -b html . _build/html
```

生成的文件包括：
- `conf.py`（含所有 nb_* 配置注释）
- `index.md`（含 toctree）
- `notebook1.ipynb`（Jupyter Notebook 示例）
- `notebook2.md`（文本格式 Notebook 示例）
- `.gitignore`

### mystnb-to-jupyter

将文本格式 Notebook 转换为 .ipynb：

```bash
mystnb-to-jupyter notebook.md notebook.ipynb

# 覆盖已存在文件
mystnb-to-jupyter -o notebook.md notebook.ipynb

# 自动推断输出路径（notebook.md → notebook.ipynb）
mystnb-to-jupyter notebook.md
```

## Python API

### Docutils 模式解析器

```python
from docutils.core import publish_string
from myst_nb.docutils_ import Parser

output = publish_string(
    open("notebook.md").read(),
    source_path="notebook.md",
    parser=Parser(),
    writer_name="html5",
    settings_overrides={
        "output_encoding": "unicode",
        "nb_execution_mode": "off",
        "myst_enable_extensions": ["dollarmath"],
    },
)
print(output)
```

### DocutilsApp 模拟

Docutils 模式使用 `DocutilsApp` 类模拟 Sphinx app，提供 roles 和 directives 注册：

```python
@dataclass
class DocutilsApp:
    roles: dict[str, Any] = field(default_factory=dict)
    directives: dict[str, Any] = field(default_factory=dict)
```

`get_nb_roles_directives()` 函数（带 `@lru_cache`）一次性加载所有 MyST-NB 指令和角色：
- code-cell、raw-cell → UnexpectedCellDirective
- eval 角色/指令
- glue 系列角色/指令（any/text/md/figure/math）

## 与 Sphinx 模式的差异

| 功能 | Sphinx 模式 | Docutils 模式 |
|------|------------|--------------|
| 多页面/TOC | ✅ toctree | ❌ 单文件 |
| intersphinx | ✅ | ❌ |
| Domain 系统 | ✅ NbGlueDomain | ❌（仅单文档 glue） |
| 跨页面 glue | ✅ | ❌ |
| 主题系统 | ✅ | ❌（默认样式） |
| 自定义格式 | ✅ nb_custom_formats | ❌（标记为 omit） |
| MIME 优先级覆盖 | ✅ | ❌ |
| ipywidgets JS | ✅ 自动加载 | ⚠️ 需手动配置 |
| 图片选项 | ✅ render_image_options | ❌（docutils 限制） |
| figure 选项 | ✅ render_figure_options | ❌（docutils 限制） |
| execution_excludepatterns | ✅ | ❌ |
| output_folder | 自动设置为 jupyter_execute | 默认 build/ |

## 适用场景

- **快速预览**：无需完整 Sphinx 项目即可转换单个 notebook
- **CI/CD 简单转换**：将 notebook 转为 HTML 报告
- **调试 AST**：pseudoxml 输出查看 docutils 节点结构
- **格式转换**：.md（mystnb）→ .ipynb 格式转换
- **嵌入式渲染**：Python 应用中嵌入 notebook 渲染
- **项目脚手架**：quickstart 快速创建项目模板

完整文档站点仍建议使用 Sphinx 模式。

## 相关概念

- [Sphinx 集成机制](10-sphinx-integration.md)
- [CLI 工具](#)
- [快速开始](01-getting-started.md)
- [MyST Notebook 文件格式](02-notebook-format.md)
