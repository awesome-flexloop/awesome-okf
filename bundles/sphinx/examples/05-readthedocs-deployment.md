# 部署到 Read the Docs 全流程

本示例演示将Sphinx文档部署到 [Read the Docs](https://readthedocs.org/)（RTD）的完整流程，包括配置文件、多版本管理、私有依赖处理。

## 步骤一：准备仓库结构

确保项目根目录有以下文件：

```
myproject/
├── docs/
│   ├── conf.py
│   ├── index.rst
│   ├── requirements.txt      # 文档构建依赖
│   ├── _static/
│   └── _templates/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── ...
├── pyproject.toml
└── .readthedocs.yaml         # RTD配置文件
```

## 步骤二：创建 requirements.txt

在 `docs/` 目录下创建文档构建依赖：

```txt
# docs/requirements.txt
sphinx>=8.0
furo>=2024.0
myst-parser>=4.0
sphinx-copybutton>=0.5
sphinx-autobuild>=2024.0
# 如果项目本身需要被autodoc导入
-e ..[docs]
```

## 步骤三：配置 conf.py

确保 `docs/conf.py` 正确配置路径和扩展：

```python
# docs/conf.py
import sys
from pathlib import Path

# 将src目录加入Python路径，让autodoc可以导入项目
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

project = "My Project"
copyright = "2026, Author"
author = "Author"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_copybutton",
]

# 支持Markdown和reST
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]

# intersphinx映射
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Napoleon配置（Google风格docstring）
napoleon_google_docstring = True
napoleon_numpy_docstring = False
```

## 步骤四：创建 .readthedocs.yaml

这是RTD的核心配置文件，必须放在仓库根目录：

```yaml
# .readthedocs.yaml — Read the Docs配置文件
# 参见 https://docs.readthedocs.io/en/stable/config-file/v2.html

version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.12"
  jobs:
    post_create_environment:
      # 安装项目本身（让autodoc可以导入）
      - pip install -e .[docs]
    post_install:
      # 安装文档依赖
      - pip install -r docs/requirements.txt

# 构建配置
sphinx:
  configuration: docs/conf.py
  fail_on_warning: true    # 警告视为错误，强制文档质量

# 构建格式
formats:
  - pdf      # 构建PDF
  - epub     # 构建EPUB
  - htmlzip  # 打包HTML

# 版本配置
versioning:
  # 默认版本
  default: latest
  # 哪些版本构建文档
  # 默认：所有tag、所有分支（可按需配置）
```

### 最小化配置（最常用）

```yaml
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: "3.12"
sphinx:
  configuration: docs/conf.py
```

### 使用conda环境（有复杂C依赖时）

```yaml
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: "miniconda3-4.7"
conda:
  environment: environment.yml
sphinx:
  configuration: docs/conf.py
```

`environment.yml`：

```yaml
name: docs
channels:
  - conda-forge
dependencies:
  - python=3.12
  - sphinx
  - furo
  - myst-parser
  - numpy
  - pandas
  - pip:
    - sphinx-copybutton
```

## 步骤五：推送到 GitHub 并导入 RTD

1. 将代码推送到 GitHub/GitLab/Bitbucket
2. 在 [readthedocs.org](https://readthedocs.org/) 注册账号并连接Git平台
3. 点击"Import a Project"，选择你的仓库
4. 点击"Build version"触发首次构建

构建成功后文档将发布在 `https://<project-name>.readthedocs.io/`。

## 多版本管理

RTD自动为每个Git tag/branch构建文档版本：

```yaml
# .readthedocs.yaml
versioning:
  default: stable
  # 只构建特定版本
  # 也可以在RTD后台的"Versions"页面管理
```

- `latest`：默认分支（通常是main/master）的最新构建
- `stable`：最新的tag版本（自动选择最高语义版本号）
- `v1.x`、`v2.0`等：每个tag对应的版本

在文档中通过 `conf.py` 配置版本切换器：

```python
html_theme_options = {
    "announcement": "这是开发版文档，<a href='/en/stable/'>查看稳定版</a>",
}
```

## 私有依赖处理

如果项目依赖私有GitHub仓库：

1. 在RTD项目设置 → Admin → Environment Variables 添加 `GITHUB_TOKEN`
2. 在 `requirements.txt` 中使用token引用：

```txt
git+https://${GITHUB_TOKEN}@github.com/yourname/private-repo.git@main#egg=private-package
```

## 本地测试RTD构建

使用RTD的Docker镜像本地复现构建环境：

```bash
docker pull readthedocs/build:latest
docker run -it --rm -v $(pwd):/home/docs/checkouts/readthedocs.org/user_builds/myproject/checkouts/latest \
  readthedocs/build:latest \
  bash -c "cd /home/docs/checkouts/readthedocs.org/user_builds/myproject/checkouts/latest && \
           pip install -r docs/requirements.txt && \
           sphinx-build -b html docs/ docs/_build/html"
```

## 常见RTD问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 构建超时 | 依赖安装或autodoc导入太慢 | 增加 `build.jobs.post_install` 超时，或减少依赖 |
| autodoc导入失败 | Python路径未配置 | 在conf.py添加 `sys.path.insert`，或用 `pip install -e .` |
| PDF构建失败 | LaTeX包缺失 | 在build.jobs中安装texlive包，或禁用pdf格式 |
| 搜索不工作 | 构建失败或语言配置错误 | 检查构建日志，确保 `html_search_language` 正确 |
| 版本不显示 | tag未推送或未激活 | 在RTD后台Versions页面激活版本 |

## 相关概念

- [部署到线上](../concepts/21-deployment.md)
- [5分钟快速上手](../concepts/01-getting-started.md)
- [Autodoc自动文档](../concepts/12-autodoc.md)
- [内置扩展完整参考](../concepts/22-builtin-extensions.md)
