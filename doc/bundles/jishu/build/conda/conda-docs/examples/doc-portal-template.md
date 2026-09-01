---
okf_version: "0.2"
type: "example"
title: "搭建类 conda-docs 的多项目文档门户"
sources:
  - docs/source/conf.py
  - docs/source/_static/
  - docs/source/_templates/
  - .readthedocs.yml
  - docs/source/user/
  - docs/source/developer/
  - docs/source/community/
---

# 搭建类 conda-docs 的多项目文档门户

本示例演示如何参照 conda-docs 的架构，为自己的开源项目集搭建统一的 Sphinx 文档门户，实现多项目聚合、品牌统一和导航共享。

## 架构概览

conda-docs 模式的文档门户包含以下要素：
1. **Sphinx + 统一主题**：所有子项目共享品牌主题
2. **门户仓库**：聚合导航 + 跨项目公共内容
3. **ReadTheDocs 多项目配置**：子项目在 RTD 上独立构建，通过 subprojects 关联
4. **重定向映射**：门户内 URL 自动跳转到对应子项目文档

## 模板项目结构

```
my-docs-portal/
├── docs/
│   └── source/
│       ├── conf.py                # Sphinx 配置
│       ├── index.rst              # 门户首页
│       ├── _static/               # 静态资源（CSS/JS/图片）
│       │   └── css/custom.css     # 品牌自定义样式
│       ├── _templates/            # Jinja2 模板覆盖
│       ├── user/                  # 用户文档区
│       │   ├── install.rst
│       │   └── getting-started.rst
│       ├── developer/             # 开发者文档区
│       │   └── contributing.rst
│       ├── community/             # 社区文档区
│       │   └── help.rst
│       └── requirements.txt       # 文档构建依赖
├── .readthedocs.yml               # RTD 构建配置
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

## 关键配置

### conf.py 核心配置

```python
# docs/source/conf.py
import sphinx_reredirects

project = "My Project Docs"
copyright = "2025, My Project Team"
author = "My Project Team"
release = "1.0.0"

# 扩展
extensions = [
    "sphinx_design",           # UI 组件
    "sphinx_reredirects",      # 重定向
    "sphinx_copybutton",       # 代码复制
]

# 主题配置
html_theme = "my_sphinx_theme"  # 使用自定义主题或 conda_sphinx_theme 参考
html_theme_options = {
    "github_url": "https://github.com/my-org",
    "show_prev_next": False,
}

# 静态资源
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

# 重定向映射：将子项目 URL 转发到独立构建的文档
redirects = {
    "subproject-a": "https://my-docs.io/projects/subproject-a/en/stable",
    "subproject-b": "https://my-docs.io/projects/subproject-b/en/stable",
}

# 排除 RST 源码中未使用的文件
exclude_patterns = ["_build"]
```

### requirements.txt

```
sphinx>=7.0
my-sphinx-theme
sphinx-design
sphinx-reredirects
sphinx-copybutton
sphinx-sitemap
```

### .readthedocs.yml

```yaml
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: "3.11"
sphinx:
  configuration: docs/source/conf.py
  fail_on_warning: false
python:
  install:
    - requirements: docs/source/requirements.txt
```

## ReadTheDocs 多项目配置

在 ReadTheDocs 上配置多项目聚合：

1. **创建门户项目**：`my-docs-portal`，绑定根仓库，URL 为 `my-docs.io`
2. **创建子项目**：分别为每个子仓库创建 RTD 项目（`subproject-a`、`subproject-b`）
3. **关联子项目**：在门户项目的 Admin → Subprojects 中添加子项目
4. **配置 CNAME**：所有子项目通过 `my-docs.io/projects/subproject-a/` 路径访问

## 首页模板示例

```rst
.. docs/source/index.rst

My Project Documentation Portal
===============================

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :fas:`download` Installation
      :link: user/install
      :link-type: doc

      Get started with installation guides for all platforms.

   .. grid-item-card:: :fas:`book` Subproject A
      :link: subproject-a/index
      :link-type: doc

      Documentation for Subproject A.

   .. grid-item-card:: :fas:`code` Subproject B
      :link: subproject-b/index
      :link-type: doc

      Documentation for Subproject B.

.. toctree::
   :hidden:
   :maxdepth: 2

   user/index
   developer/index
   community/index
```

## 自定义品牌样式

在 `_static/css/custom.css` 中覆盖主题变量：

```css
/* 品牌色 */
:root {
    --pst-color-primary: #2E7D32;
    --pst-color-secondary: #43A047;
}

/* 隐藏页脚的上一页/下一页 */
.prev-next-area {
    display: none;
}
```

## 部署验证清单

- [ ] `make html` 本地构建无错误
- [ ] 首页卡片正确链接到子项目文档
- [ ] 重定向规则在 RTD 上生效（访问 `/subproject-a/` 正确跳转）
- [ ] 品牌样式（Logo、颜色、字体）正确应用
- [ ] 移动端布局正常（sphinx-design 栅格响应式）
- [ ] 搜索功能跨页面工作
- [ ] 子项目间通过 intersphinx 正确交叉引用

> 📌 **与 conda-docs 模式对比**：conda-docs 更复杂的地方在于：(1) 使用了独立的 conda-sphinx-theme 主题包（需要单独发布到 PyPI）；(2) 子项目数量更多，导航栏需要程序化生成；(3) 有新闻/blog 动态内容模块。对于中小型项目集，上述精简模板即可满足需求。
