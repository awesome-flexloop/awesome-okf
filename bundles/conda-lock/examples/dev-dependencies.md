---
okf_version: "0.2"
type: "example"
title: "开发依赖与 category 过滤"
sources:
  - "conda_lock/lockfile/__init__.py"
  - "conda_lock/models/lock_spec.py"
  - "conda_lock/src_parser/environment_yaml.py"
---

# 开发依赖与 category 过滤

本示例演示如何使用 conda-lock 的依赖类别（category）功能区分生产依赖和开发依赖（测试、lint、文档等），实现一次锁定、选择性安装。核心机制是 `category` 字段标记和 `apply_categories()` BFS 传播算法。

相关概念：[依赖类别与传播](../concepts/14-categories-and-deps.md)、[锁文件 v1/v2 格式](../concepts/06-lockfile-formats.md)、[源文件解析](../concepts/07-source-parsers.md)。

## 完整示例

### 步骤 1：创建带 category 的 environment.yml

```yaml
# environment.yml
name: my-project
channels:
  - conda-forge
dependencies:
  # ===== 生产依赖（main category，默认）=====
  - python=3.10
  - numpy>=1.24
  - pandas>=2.0
  - pydantic>=2.0

  # ===== 开发依赖（dev category）=====
  - pytest:
      category: dev
  - pytest-cov:
      category: dev
  - black:
      category: dev
  - ruff:
      category: dev
  - ipython:
      category: dev

  # ===== 文档依赖（docs category）=====
  - sphinx:
      category: docs
  - sphinx-rtd-theme:
      category: docs
  - myst-parser:
      category: docs

  # ===== 测试依赖（test category）=====
  - pytest-xdist:
      category: test
  - hypothesis:
      category: test

  # ===== pip 依赖（也支持 category）=====
  - pip:
      - requests>=2.28           # main
      - pytest-mock>=3.10:      # dev
          category: dev
      - sphinx-autobuild:       # docs
          category: docs

platforms:
  - linux-64
  - osx-arm64
```

引用事实：
- [F-001] `category: dev` 是 conda-lock 对 environment.yml 的扩展语法
- [F-002] 不指定 category 的依赖默认为 main category
- [F-003] pip 子段中的依赖也支持 category 标记
- [F-004] 用户可以创建任意自定义 category（dev/docs/test/gpu 等）

### 步骤 2：生成包含所有类别的锁文件

```bash
# 锁定所有依赖（包含所有 category）
conda-lock lock -f environment.yml --dev-dependencies --extras docs --extras test --mamba
```

> 注意：`lock` 命令默认只锁定 main category。要包含 dev 和其他自定义 category，
> 需要显式使用 `--dev-dependencies` 和 `--extras` 指定。

或者使用更简洁的方式锁定全部：

```bash
# 如果环境文件中明确指定了 platforms 和所有依赖（含 dev），
# 不使用 --dev-dependencies/--extras 时仅锁定 main。
# 要锁定所有 category 的依赖，需要包含它们：
conda-lock lock -f environment.yml --dev-dependencies --extras docs --extras test
```

引用事实：
- [F-005] `--dev-dependencies` 选项在锁定时包含 dev category
- [F-006] `--extras <category>` 添加额外的自定义 category
- [F-007] make_lock_spec() 通过 filtered_categories 参数过滤要包含的依赖

### 步骤 3：查看锁文件中的 categories

```bash
# 查看 main category 的包
echo "=== 生产依赖 (main) ==="
grep -B10 "categories:" conda-lock.yml | grep -B10 "\- main" | grep "name:" | head -10

# 查看 dev category 的包
echo ""
echo "=== 开发依赖 (dev) ==="
grep -B10 "dev" conda-lock.yml | grep "name:" | head -10

# 查看 docs category 的包
echo ""
echo "=== 文档依赖 (docs) ==="
grep -B10 "docs" conda-lock.yml | grep "name:" | head -5
```

你会发现：
- `numpy`/`pandas`/`python` 等核心包的 `categories` 只有 `main`
- `pytest`/`black`/`ruff` 的 `categories` 包含 `dev`
- `sphinx` 的 `categories` 包含 `docs`
- pytest 的传递依赖（如 `packaging`、`iniconfig`、`pluggy`）的 `categories` 包含 `dev`（通过 BFS 传播）

引用事实：
- [F-008] apply_categories() 使用 BFS 从显式依赖向传递依赖传播 category
- [F-009] _truncate_main_category() 规则：属于 main 的包移除其他 category

### 步骤 4：不同场景的安装命令

**生产环境（仅 main）：**
```bash
conda-lock install --name my-project conda-lock.yml
# 不使用 --dev/--extras，默认只安装 main
```

**开发环境（main + dev）：**
```bash
conda-lock install --name my-project-dev --dev conda-lock.yml
# --dev 等价于 categories={"main", "dev"}
```

**文档构建环境（main + docs）：**
```bash
conda-lock install --name my-project-docs --extras docs conda-lock.yml
# --extras docs 等价于 categories={"main", "docs"}
```

**CI 测试环境（main + dev + test）：**
```bash
conda-lock install --name my-project-ci --dev --extras test conda-lock.yml
# --dev --extras test 等价于 categories={"main", "dev", "test"}
```

**完整开发环境（所有 category）：**
```bash
conda-lock install --name my-project-full --dev --extras docs --extras test conda-lock.yml
# categories={"main", "dev", "docs", "test"}
```

引用事实：
- [F-010] install 命令的 --dev 标志添加 dev category
- [F-011] --extras 可多次指定添加多个自定义 category
- [F-012] 安装时过滤条件是 categories ∩ selected_categories 非空

### 步骤 5：在不同环境中验证

```bash
# 生产环境：应该只有 numpy/pandas/requests 等，没有 pytest/black/sphinx
conda activate my-project
python -c "import numpy, pandas, requests; print('生产包 OK')"
python -c "import pytest" 2>&1 | grep -q "No module" && echo "pytest 未安装 ✓"

# 开发环境：包含 pytest/black 等
conda activate my-project-dev
python -c "import pytest, black, ruff; print('开发包 OK')"
pytest --version
black --version

# 文档环境：包含 sphinx
conda activate my-project-docs
python -c "import sphinx; print('文档包 OK')"
sphinx-build --version
```

## 使用 pyproject.toml 的 optional-dependencies

如果使用 pyproject.toml，PEP 621 的 optional-dependencies 自动映射到 category：

```toml
# pyproject.toml
[project]
name = "my-project"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.24",
    "pandas>=2.0",
    "pydantic>=2.0",
    "requests>=2.28",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1",
]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=1.3",
    "myst-parser>=2.0",
]
test = [
    "pytest-xdist>=3.0",
    "hypothesis>=6.0",
]
```

```bash
# 锁定（使用 pyproject.toml）
conda-lock lock -f pyproject.toml --dev-dependencies --extras docs --extras test --mamba

# 安装方式与 environment.yml 完全相同
conda-lock install --name my-project --dev conda-lock.yml
```

引用事实：
- [F-013] pyproject_toml.py 将 optional-dependencies 的 key 映射为 category 名称
- [F-014] Poetry 的 dev-dependencies 组也映射为 dev category

## 理解 BFS 传播机制

以以下依赖关系为例：

```
pytest (dev)
  ├── iniconfig
  ├── packaging  ← 同时被 numpy (main) 依赖
  ├── pluggy
  └── tomli

numpy (main)
  ├── libgcc-ng (main)
  └── packaging (main/dev 重叠)
```

BFS 传播过程：
1. 初始：`pytest={dev}`, `numpy={main}`
2. 传播 pytest 的 dev 到：`iniconfig={dev}`, `packaging={dev}`, `pluggy={dev}`, `tomli={dev}`
3. 传播 numpy 的 main 到：`libgcc-ng={main}`, `packaging={main, dev}`
4. `_truncate_main_category()` 截断：`packaging.categories = {main}`（因为 main 优先）

最终结果：
- `numpy`: {main}
- `pytest`: {dev}
- `packaging`: {main}（main 优先截断）
- `iniconfig`: {dev}
- `pluggy`: {dev}
- `tomli`: {dev}
- `libgcc-ng`: {main}

引用事实：
- [F-015] main 截断规则确保生产依赖不被标记为其他 category

## render 命令中的 category 过滤

渲染 explicit 文件时也可以按 category 过滤（render 使用 `--dev-dependencies/--no-dev-dependencies` 标志，与 lock 一致）：

```bash
# 仅渲染 main 的 explicit 文件
conda-lock render --kind explicit

# 渲染 main + dev 的 explicit 文件
conda-lock render --kind explicit --dev-dependencies

# 渲染 main + docs 的 explicit 文件
conda-lock render --kind explicit --extras docs
```

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| dev 依赖未包含在锁文件中 | 锁定时未使用 --dev-dependencies | 添加 --dev-dependencies 选项 |
| 自定义 category 缺失 | 未使用 --extras 指定 | 添加 --extras <category> |
| 传递依赖未获得正确 category | BFS 传播前 categories 未正确初始化 | 确保显式依赖正确标记 category |
| 安装了不需要的包 | categories 过滤不正确 | 检查 --dev/--extras 参数 |
| 包同时是 main 和 dev | main 截断规则生效 | 这是正常行为，main 优先 |

## 最佳实践

1. **默认只锁定 main**：CI 生产环境只需要 main，dev 依赖会增加锁定时间
2. **开发时锁定全部**：`--dev-dependencies --extras docs --extras test`
3. **category 命名一致**：使用通用的 dev/docs/test 名称，避免自定义太多个性化 category
4. **提交锁文件**：conda-lock.yml 应提交到版本控制，包含所有 category 的锁定结果
5. **CI 缓存锁文件**：使用 `--check-input-hash` 避免不必要的重新锁定

## 相关概念

- [依赖类别与传播](../concepts/14-categories-and-deps.md)
- [锁文件 v1/v2 格式](../concepts/06-lockfile-formats.md)
- [CLI 命令体系](../concepts/11-cli-commands.md)
- [源文件解析](../concepts/07-source-parsers.md)
- [基础锁定工作流](basic-lock-workflow.md)
