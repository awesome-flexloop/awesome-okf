---
type: Concept
title: 代码质量工具
description: 掌握模板预置的代码质量工具链——ruff、black、mypy、mdformat、pre-commit——以及它们的配置和使用方式。
tags: [code-quality, lint, ruff, black, mypy, pre-commit, mdformat]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject
    resource: /references/pyproject-source.md
    title: pyproject.toml 模板字段全解析
  - id: ci-source
    resource: /references/ci-workflow-source.md
    title: CI/CD 工作流源码解析
---

## 工具链概览

模板预置了完整的 Python 代码质量工具链：

| 工具 | 类型 | 作用 | 配置位置 |
|------|------|------|---------|
| **Ruff** | Linter | 快速代码检查，替代 flake8/isort/pyupgrade 等 | pyproject.toml `[tool.ruff]` |
| **Black** | Formatter | 代码格式化（无争议风格） | pyproject.toml `[tool.black]` |
| **mypy** | Type Checker | 静态类型检查 | pyproject.toml `[tool.mypy]` |
| **mdformat** | Markdown Formatter | Markdown 文件格式化 | CLI 参数 + pre-commit |
| **pre-commit** | Git Hook | commit 前自动运行检查 | `.pre-commit-config.yaml` |
| **validate-pyproject** | Validator | pyproject.toml 格式验证 | CI lint.sh |

所有工具通过 `pip install -e ".[lint,typing]"` 安装。

## Ruff——Python Linter

[Ruff](https://github.com/astral-sh/ruff) 是一个用 Rust 编写的超快 Python linter，一个工具替代了传统的 flake8 + isort + pyupgrade + bandit 等多个工具。

### 启用的规则集

```toml
[tool.ruff]
select = [
  "A", "B", "C", "E", "F", "FBT", "I", "N", "Q", "RUF", "S", "T",
  "UP", "W", "YTT",
]
```

| 规则码 | 来源 | 检查内容 |
|--------|------|---------|
| `A` | flake8-builtins | 内置名阴影（如用 `list` 作变量名） |
| `B` | flake8-bugbear | 常见 bug 模式 |
| `C` | mccabe | 圈复杂度 |
| `E`/`W` | pycodestyle | PEP 8 风格/错误 |
| `F` | Pyflakes | 代码错误（未使用导入等） |
| `FBT` | flake8-boolean-trap | 布尔陷阱（布尔位置参数） |
| `I` | isort | 导入排序 |
| `N` | pep8-naming | 命名规范 |
| `Q` | flake8-quotes | 引号风格 |
| `RUF` | Ruff 特定 | Ruff 内置规则 |
| `S` | flake8-bandit | 安全问题 |
| `T` | flake8-type-checking | 类型检查导入 |
| `UP` | pyupgrade | 语法升级（建议使用更新语法） |
| `YTT` | flake8-2020 | sys.version 比较 |

### 忽略的规则

```toml
ignore = [
  "Q000",       # 单引号警告（Black 配置 skip-string-normalization）
  "FBT001", "FBT002", "FBT003",  # Boolean 位置参数（Tornado 框架兼容）
  "C901",       # 函数复杂度过高（Handler 中可能需要复杂逻辑）
]
```

### 测试文件特殊配置

```toml
[tool.ruff.per-file-ignores]
"my_extension/tests/*" = ["S101"]
```

测试文件中忽略 `S101`（assert 使用）——测试中使用 assert 是正常的。

### 运行 Ruff

```bash
# 检查所有文件
ruff .

# 检查并自动修复
ruff . --fix

# 检查特定文件
ruff my_extension/handlers.py
```

CI 中运行 `ruff .`，发现问题时 CI 失败。

## Black——代码格式化

[Black](https://github.com/psf/black) 是 Python 的"无争议"代码格式化工具，统一代码风格。

### 配置

```toml
[tool.black]
line-length = 100
target-version = ["py38"]
skip-string-normalization = true
```

| 配置 | 值 | 说明 |
|------|------|------|
| `line-length` | 100 | 行宽 100（非默认 88，Jupyter 生态惯例） |
| `target-version` | py38 | 目标 Python 3.8 |
| `skip-string-normalization` | true | 不统一引号（保留单/双引号原样） |

`skip-string-normalization = true` 是关键配置——Black 默认将所有字符串归一化为双引号，但 Jupyter 生态保留单引号风格。这也解释了为什么 Ruff 中忽略 Q000。

### 运行 Black

```bash
# 检查格式（不修改）
black --check --diff .

# 自动格式化
black .

# 格式化特定文件
black my_extension/extension.py
```

CI 中运行 `black --check --diff .`，格式不对时 CI 失败并显示差异。

## mypy——静态类型检查

[mypy](https://mypy-lang.org/) 是 Python 的静态类型检查器，在不运行代码的情况下发现类型错误。

### 严格模式配置

```toml
[tool.mypy]
check_untyped_defs = true        # 检查无类型注解的函数
disallow_incomplete_defs = true  # 禁止不完整的类型注解
no_implicit_optional = true      # 不隐式将有 None 默认值的参数视为 Optional
pretty = true                    # 美化错误输出
show_error_context = true        # 显示错误上下文
show_error_codes = true          # 显示错误码
strict_equality = true           # 严格相等检查
warn_unused_configs = true       # 警告未使用的配置
warn_unused_ignores = true       # 警告不必要的 type: ignore
warn_redundant_casts = true      # 警告冗余 cast
```

这些配置构成近似"严格模式"，要求代码有完整的类型注解。

### 运行 mypy

```bash
# 安装类型 stubs 并检查
mypy --install-types --non-interactive .

# 检查特定文件
mypy my_extension/extension.py
```

`--install-types --non-interactive` 自动安装缺失的类型存根（types-tornado、types-jupyter_server 等）。

## mdformat——Markdown 格式化

[mdformat](https://github.com/executablebooks/mdformat) 是 Markdown 文件格式化工具，保持 Markdown 文件风格一致。

模板使用 mdformat 带 GFM（GitHub Flavored Markdown）插件：

```bash
# 检查 Markdown 文件
mdformat --check *.md
# 自动格式化
mdformat *.md
```

CI 中运行 `mdformat --check *.md`。

## pre-commit——Git Hooks

[pre-commit](https://pre-commit.com) 是一个管理 Git pre-commit hooks 的框架，在每次 `git commit` 前自动运行代码检查。

### 配置（.pre-commit-config.yaml）

模板配置了 4 个 hook 仓库：

**1. pre-commit-hooks（通用检查）**：
- `end-of-file-fixer`：文件末尾添加空行
- `check-case-conflict`：检查文件名大小写冲突
- `check-executables-have-shebangs`：可执行文件有 shebang
- `requirements-txt-fixer`：requirements.txt 排序
- `check-added-large-files`：防止提交大文件
- `check-toml`/`check-yaml`：TOML/YAML 语法检查
- `debug-statements`：检测 breakpoint/debug 语句
- `forbid-new-submodules`：禁止添加新 git submodule
- `check-builtin-literals`：推荐使用字面量语法
- `trailing-whitespace`：去除行尾空白

**2. check-jsonschema**：
- `check-github-workflows`：GitHub Actions 工作流 JSON Schema 验证

**3. mdformat**：
- Markdown 格式化（带 gfm、frontmatter、footnote 插件）

**4. Black + Ruff**：
- `black`：Python 代码格式化
- `ruff --fix`：Ruff 自动修复

### 使用 pre-commit

```bash
# 安装 pre-commit
pip install pre-commit

# 安装 git hooks（首次）
pre-commit install

# 手动运行所有 hooks（所有文件）
pre-commit run --all-files

# 手动运行特定 hook
pre-commit run black --all-files
```

安装 hooks 后，每次 `git commit` 会自动运行配置的检查。如果检查失败，commit 被阻止；Black 和 Ruff 会自动修复问题，修复后重新 `git add` 和 `git commit` 即可。

## 一键 Lint 脚本

`.github/workflows/lint.sh` 提供了一键运行所有代码质量检查的脚本：

```bash
#!/usr/bin/env bash
pip install -e ".[test,lint]"
mypy --install-types --non-interactive .
ruff .
black --check --diff .
mdformat --check *.md
pipx run 'validate-pyproject[all]' pyproject.toml
```

本地运行：
```bash
bash .github/workflows/lint.sh
```

这也是 CI 的 test_lint Job 运行的命令。

## 工具选择理由

Jupyter 生态选择这些工具的理由：
- **Ruff** 替代 flake8：速度快 10-100 倍，规则集更全，单一工具维护简单
- **Black**：无争议格式化，消除风格争论
- **mypy**：Python 生态最成熟的类型检查器
- **skip-string-normalization**：Jupyter 代码库传统上使用单引号，保持一致性
- **pre-commit**：在代码进入仓库前拦截问题，减少 CI 失败

## 相关概念

- [CI/CD 工作流](09-ci-workflows.md)
- [构建系统详解](08-build-system.md)
- [pyproject.toml 字段全解析](../references/pyproject-source.md)
