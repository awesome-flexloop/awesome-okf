---
type: Concept
title: 生成的项目结构
description: 详解 cookiecutter 生成的项目目录结构，每个文件和目录的作用，以及文件之间的依赖关系。
tags: [project-structure, directory-layout, file-reference, anatomy]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: extension-source
    resource: /references/extension-app-source.md
    title: ExtensionApp 类源码解析
  - id: handler-source
    resource: /references/handler-source.md
    title: PingHandler 请求处理器源码解析
---

## 完整目录树

以默认包名 `my_server_extension` 为例，生成的项目结构如下（Binder 相关文件在 has_binder=n 时被 post_gen_project 钩子删除）：

```
my_server_extension/
├── .github/
│   ├── dependabot.yml                    # Dependabot 依赖自动更新配置
│   └── workflows/
│       ├── binder-on-pr.yml             # [可选] PR Binder 链接评论（has_binder=y 时保留）
│       ├── build.yml                    # CI 构建工作流
│       └── lint.sh                      # Lint 检查脚本
├── .gitignore                            # Git 忽略规则
├── .pre-commit-config.yaml              # pre-commit 钩子配置
├── binder/                              # [可选] Binder 配置（has_binder=y 时保留）
│   ├── environment.yml                  # Binder conda 环境定义
│   └── postBuild                        # Binder 构建后安装脚本
├── CHANGELOG.md                          # 变更日志（Jupyter Releaser 维护）
├── conftest.py                          # pytest 配置（注册 pytest-jupyter、启用扩展）
├── jupyter-config/                      # Jupyter 配置发现目录
│   └── jupyter_server_config.d/
│       └── my_server_extension.json     # 扩展自动启用配置
├── LICENSE                              # BSD 3-Clause 许可证
├── my_server_extension/                 # Python 包目录
│   ├── __init__.py                      # 包入口（版本号 + 扩展点注册）
│   ├── extension.py                     # ExtensionApp 子类（扩展核心）
│   ├── handlers.py                      # API 请求处理器
│   └── tests/                          # 测试包
│       ├── __init__.py                  # 测试初始化
│       └── test_handlers.py             # Handler 单元测试
├── pyproject.toml                       # 项目配置（构建、依赖、工具配置）
├── README.md                            # 项目说明文档
└── RELEASE.md                          # 发布指南
```

## 根目录文件

### pyproject.toml

项目的核心配置文件，包含：
- **构建系统**：hatchling 后端
- **项目元数据**：名称、作者、依赖、分类器
- **可选依赖组**：test、lint、typing
- **hatch 配置**：版本源路径、shared-data 映射
- **工具配置**：pytest、mypy、black、ruff

详细解析参见 [pyproject.toml 模板字段全解析](/references/pyproject-source.md)。

### conftest.py

pytest 配置文件，为测试环境启用扩展：
- 注册 `jupyter_server.pytest_plugin` 插件（提供 `jp_fetch` 等 fixture）
- 覆盖 `jp_server_config` fixture，在测试服务器中启用当前扩展

### .pre-commit-config.yaml

[pre-commit](https://pre-commit.com) 钩子配置，在 git commit 前自动运行代码检查：
- `pre-commit-hooks`：通用检查（文件尾空行、YAML/TOML 语法、大文件检测等）
- `check-jsonschema`：GitHub Actions 工作流验证
- `mdformat`：Markdown 格式化
- `black`：Python 代码格式化
- `ruff`：Python linter（带自动修复）

### .gitignore

标准 Python .gitignore（基于 gitignore.io 模板），排除 `__pycache__/`、`*.pyc`、`build/`、`dist/`、`.pytest_cache/`、`.mypy_cache/` 等。

### CHANGELOG.md

变更日志模板，包含 Jupyter Releaser 使用的标记注释：
```
<!-- <START NEW CHANGELOG ENTRY> -->
<!-- <END NEW CHANGELOG ENTRY> -->
```
Jupyter Releaser 自动在这两个标记之间插入新版本的变更记录。

### README.md

项目 README，包含：
- CI 和 Binder badge（Binder badge 条件渲染）
- 项目简介
- 安装/卸载说明
- 故障排查
- 开发安装指南（含 `--autoreload` 模式）
- 测试运行说明
- 打包发布链接

### RELEASE.md

发布指南，涵盖三种发布方式：
- **手动发布**：`python -m build` + `twine upload`
- **Jupyter Releaser 自动化**：通过 GitHub Actions 一键发布
- **conda-forge 发布**：PyPI 发布后 bot 自动提 PR

### LICENSE

BSD 3-Clause 许可证，年份通过 Jinja2 `{% now 'utc', '%Y' %}` 动态生成，版权持有人填入作者名。

## Python 包目录（my_server_extension/）

### \_\_init\_\_.py

包入口文件，两个核心作用：

1. **版本号**：`__version__ = "0.1.0"`，被 hatchling 读取作为包版本
2. **扩展点注册**：`_jupyter_server_extension_points()` 函数返回扩展元数据

```python
from .extension import Extension
__version__ = "0.1.0"

def _jupyter_server_extension_points():
    return [{
        "module": "my_server_extension",
        "app": Extension
    }]
```

`_jupyter_server_extension_points()` 是 Jupyter Server 发现扩展的标准入口函数，Jupyter Server 启动时扫描已安装包中包含此函数的模块。

### extension.py

扩展核心类，继承 ExtensionApp：
- 定义 `name`（扩展唯一标识）
- 注册 `handlers`（URL 路由映射）
- 定义可配置 trait（`ping_response`）
- 实现 `initialize_settings()` 注入配置到 settings 字典

详细解析参见 [ExtensionApp 类源码解析](/references/extension-app-source.md)。

### handlers.py

HTTP 请求处理器：
- `PingHandler` 类继承 `ExtensionHandlerMixin` 和 `APIHandler`
- `get()` 方法处理 GET 请求，返回 JSON 响应
- 使用 `@tornado.web.authenticated` 装饰器确保认证

详细解析参见 [PingHandler 请求处理器源码解析](/references/handler-source.md)。

### tests/ 目录

测试包，包含：

| 文件 | 作用 |
|------|------|
| `__init__.py` | 测试包标记，含 docstring |
| `test_handlers.py` | PingHandler 异步测试，使用 `jp_fetch` fixture |

## jupyter-config/ 目录

这是 Jupyter 扩展自动发现机制的关键目录：

```
jupyter-config/
└── jupyter_server_config.d/
    └── my_server_extension.json
```

`my_server_extension.json` 内容：

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "my_server_extension": true
    }
  }
}
```

pyproject.toml 中的 `shared-data` 配置将此目录安装到 `{sys.prefix}/etc/jupyter/`：

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyter-config" = "etc/jupyter"
```

Jupyter Server 启动时自动扫描 `{sys.prefix}/etc/jupyter/jupyter_server_config.d/*.json` 并加载配置，从而**自动启用**扩展，无需用户手动运行 `jupyter server extension enable`。

## .github/ 目录

### workflows/build.yml

CI 工作流，包含 5 个 job：build（矩阵构建）、check_links、test_lint、check_release、test_sdist。

### workflows/lint.sh

Lint 检查脚本，执行 mypy、ruff、black、mdformat、validate-pyproject 五项检查。

### dependabot.yml

Dependabot 配置，每周自动检查 GitHub Actions 和 pip 依赖更新并提 PR。

## binder/ 目录（可选）

当 `has_binder=y` 时保留：

| 文件 | 作用 |
|------|------|
| `environment.yml` | 定义 Binder 的 conda 环境（Python 3.8、JupyterLab 3.x） |
| `postBuild` | Binder 构建后脚本：pip check → pip install -e . → pip check → 列扩展 |

## 文件依赖关系

```
pyproject.toml
  ├── [build-system] → hatchling 构建
  ├── [project] → 包元数据、依赖
  ├── [tool.hatch.build.targets.wheel.shared-data]
  │     └── 安装 jupyter-config/ → etc/jupyter/
  │           └── jupyter_server_config.d/*.json → 自动启用扩展
  ├── [tool.hatch.version] → 读取 __init__.py 中的 __version__
  └── [tool.pytest/mypy/black/ruff] → 开发工具配置

my_server_extension/__init__.py
  ├── __version__ → pyproject.toml version source
  ├── from .extension import Extension → extension.py
  └── _jupyter_server_extension_points()
        └── 返回 Extension 类 → Jupyter Server 加载

my_server_extension/extension.py
  ├── from .handlers import PingHandler → handlers.py
  ├── handlers = [(".../ping", PingHandler)] → URL 路由
  ├── ping_response trait → 配置项
  └── initialize_settings() → self.settings 更新
        └── Handler 通过 self.settings 访问配置

my_server_extension/handlers.py
  ├── ExtensionHandlerMixin + APIHandler → 基类
  └── PingHandler.get() → @tornado.web.authenticated → JSON响应

conftest.py
  ├── pytest_plugins = ["jupyter_server.pytest_plugin"] → jp_fetch 等 fixture
  └── jp_server_config fixture → 启用扩展 → 测试时加载 extension.py

my_server_extension/tests/test_handlers.py
  └── jp_fetch → 请求 extension.py 注册的路由 → PingHandler.get() 响应
```

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [配置发现机制](/concepts/06-config-discovery.md)
- [ExtensionApp 开发](/concepts/04-extension-app.md)
