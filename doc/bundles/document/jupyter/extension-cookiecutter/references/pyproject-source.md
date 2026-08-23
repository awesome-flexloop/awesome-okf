---
type: Reference
title: pyproject.toml 模板字段全解析
description: 逐节解析模板生成的 pyproject.toml 所有配置段，包括构建系统、项目元数据、依赖声明、工具配置（hatch/pytest/mypy/black/ruff）。
tags: [reference, pyproject, hatchling, build-system, packaging]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject-toml
    resource: https://github.com/jupyter-server/extension-cookiecutter/blob/main/%7B%7Bcookiecutter.package_name%7D%7D/pyproject.toml
    title: pyproject.toml 模板源码
---

## [build-system] 段

```toml
[build-system]
requires = ["hatchling>=1.5"]
build-backend = "hatchling.build"
```

| 字段 | 值 | 说明 |
|------|------|------|
| `requires` | `["hatchling>=1.5"]` | 构建时依赖，使用 [Hatchling](https://hatch.pypa.io/latest/) 作为构建后端，最低版本 1.5 |
| `build-backend` | `"hatchling.build"` | 构建后端入口点，符合 PEP 517 标准 |

Hatchling 是现代 Python 构建后端，替代 setuptools。它原生支持 PEP 621 元数据、自动发现包、wheel shared-data 等特性。

## [project] 段（PEP 621 元数据）

```toml
[project]
name = "{{cookiecutter.package_name}}"
authors = [{name = "{{cookiecutter.author_name}}", email = "{{cookiecutter.author_email}}"}]
dynamic = ["version"]
readme = "README.md"
requires-python = ">=3.8"
keywords = ["Jupyter", "Extension"]
classifiers = [
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Framework :: Jupyter",
]
dependencies = ["jupyter_server>=1.6,<3"]
```

| 字段 | 值 | 说明 |
|------|------|------|
| `name` | 包名变量 | 分发包名（PyPI 上的名称） |
| `authors` | 模板变量 | 作者信息列表，包含 name 和 email |
| `dynamic` | `["version"]` | 声明 version 字段动态获取（从代码中读取，非静态声明） |
| `readme` | `"README.md"` | README 文件路径，自动包含在分发包中 |
| `requires-python` | `">=3.8"` | 支持 Python 3.8+，涵盖 3.8-3.11 |
| `keywords` | `["Jupyter", "Extension"]` | PyPI 搜索关键词 |
| `classifiers` | Trove 分类器列表 | PyPI 分类标签，声明许可证、Python 版本、框架 |
| `dependencies` | `["jupyter_server>=1.6,<3"]` | 核心运行时依赖：Jupyter Server 1.6 以上、3.0 以下 |

### 核心依赖版本约束

`jupyter_server>=1.6,<3` 是关键约束：
- `>=1.6`：需要 ExtensionApp 机制和现代 API
- `<3`：排除可能引入 breaking changes 的 Jupyter Server 3.0

## [project.optional-dependencies] 段

```toml
[project.optional-dependencies]
test = [
  "pytest>=7.0",
  "pytest-jupyter[server]>=0.6"
]
lint = [
  "black>=22.6.0",
  "mdformat>0.7",
  "mdformat-gfm>=0.3.5",
  "ruff>=0.0.156"
]
typing = ["mypy>=0.990"]
```

三组可选依赖：

| 组名 | 包含 | 安装方式 |
|------|------|---------|
| `test` | pytest 7+、pytest-jupyter[server] 0.6+ | `pip install -e ".[test]"` |
| `lint` | black、mdformat（含 GFM 插件）、ruff | `pip install -e ".[lint]"` |
| `typing` | mypy 0.990+ | `pip install -e ".[typing]"` |

同时安装多组：`pip install -e ".[test,lint,typing]"`，这也是 lint.sh 脚本使用的方式。

## [project.license] 段

```toml
[project.license]
file="LICENSE"
```

声明许可证文件路径为根目录的 LICENSE（BSD 3-Clause）。

## [project.urls] 段

```toml
[project.urls]
Home = "{{cookiecutter.repository}}"
```

项目主页 URL，指向 cookiecutter.json 中填写的仓库地址。

## [tool.hatch.version] 段

```toml
[tool.hatch.version]
path = "{{ cookiecutter.package_name }}/__init__.py"
```

Hatchling 的版本源配置：从 `__init__.py` 文件中读取 `__version__` 变量作为包版本。模板中 `__init__.py` 包含 `__version__ = "0.1.0"`。

## [tool.hatch.build.targets.wheel.shared-data] 段（关键！）

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyter-config" = "etc/jupyter"
```

这是 Jupyter Server 扩展的**关键配置**：将源目录的 `jupyter-config/` 映射到安装后的 `etc/jupyter/`。

- 源路径：包根目录下的 `jupyter-config/`（包含 `jupyter_server_config.d/{package_name}.json`）
- 目标路径：`{sys.prefix}/etc/jupyter/`
- 效果：`pip install` 时，配置文件自动安装到 Jupyter 的配置发现目录，实现扩展的自动启用

这是 Jupyter 扩展自动发现机制的核心——不通过代码注册，而是通过配置文件。

## [tool.pytest.ini_options] 段

```toml
[tool.pytest.ini_options]
filterwarnings = [
  "error",
  "ignore:There is no current event loop:DeprecationWarning",
  "module:make_current is deprecated:DeprecationWarning",
  "module:clear_current is deprecated:DeprecationWarning",
  "module:Jupyter is migrating its paths to use standard platformdirs:DeprecationWarning",
]
```

pytest 配置：
- `"error"`：将所有警告视为错误（严格模式，防止隐藏的废弃警告）
- 后面四条忽略特定已知的 DeprecationWarning，这些是 Jupyter 生态中正在进行的迁移产生的

## [tool.mypy] 段

```toml
[tool.mypy]
check_untyped_defs = true
disallow_incomplete_defs = true
no_implicit_optional = true
pretty = true
show_error_context = true
show_error_codes = true
strict_equality = true
warn_unused_configs = true
warn_unused_ignores = true
warn_redundant_casts = true
```

mypy 严格模式配置：

| 选项 | 作用 |
|------|------|
| `check_untyped_defs` | 检查没有类型注解的函数体 |
| `disallow_incomplete_defs` | 禁止类型注解不完整的函数 |
| `no_implicit_optional` | 不隐式将有默认值 None 的参数视为 Optional |
| `strict_equality` | 警告可能的类型错误比较 |
| `warn_unused_ignores` | 警告不必要的 `# type: ignore` |
| `warn_redundant_casts` | 警告冗余的 `cast()` 调用 |

## [tool.black] 段

```toml
[tool.black]
line-length = 100
target-version = ["py38"]
skip-string-normalization = true
```

Black 格式化配置：
- 行宽 100（而非默认的 88）
- 目标 Python 3.8
- `skip-string-normalization = true`：保留字符串引号风格（不强制双引号），这是 Jupyter 生态的惯例

## [tool.ruff] 段

```toml
[tool.ruff]
target-version = "py38"
line-length = 100
select = [
  "A", "B", "C", "E", "F", "FBT", "I", "N", "Q", "RUF", "S", "T",
  "UP", "W", "YTT",
]
ignore = [
  "Q000",
  "FBT001", "FBT002", "FBT003",
  "C901",
]

[tool.ruff.per-file-ignores]
"{{cookiecutter.package_name}}/tests/*" = ["S101"]
```

Ruff linter 配置：

**启用的规则集**（select）：
- `A`：builtins 阴影警告
- `B`：bugbear（常见错误模式）
- `C`：mccabe 复杂度
- `E`/`W`：pycodestyle 错误/警告
- `F`：Pyflakes
- `FBT`：boolean 陷阱
- `I`：isort（导入排序）
- `N`：pep8-naming
- `Q`：quote 风格
- `RUF`：Ruff 特定规则
- `S`：bandit 安全检查
- `T`：type hint import
- `UP`：pyupgrade（自动升级语法）
- `W`：pycodestyle 警告
- `YTT`：sys.version 比较

**忽略的规则**：
- `Q000`：单引号使用（因为 black 已设 skip-string-normalization）
- `FBT001-003`：Boolean 位置参数警告（Tornado API 风格兼容）
- `C901`：函数复杂度过高警告

**per-file-ignores**：
- 测试文件忽略 `S101`（assert 使用——测试中 assert 是正常的）

## 相关概念

- [构建系统详解](/concepts/08-build-system.md)
- [代码质量工具](/concepts/11-code-quality.md)
- [打包发布指南](/concepts/12-packaging-release.md)
