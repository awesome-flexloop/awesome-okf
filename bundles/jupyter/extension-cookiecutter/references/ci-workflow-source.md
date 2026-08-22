---
type: Reference
title: CI/CD 工作流源码解析
description: 解析模板项目自身 CI（main.yml）和生成项目的 CI（build.yml）两套 GitHub Actions 工作流，以及 lint.sh、dependabot.yml、binder-on-pr.yml 的配置逻辑。
tags: [reference, ci-cd, github-actions, build-matrix, jupyter-releaser]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: main-yml
    resource: https://github.com/jupyter-server/extension-cookiecutter/blob/main/.github/workflows/main.yml
    title: 模板项目 main.yml CI 源码
  - id: build-yml
    resource: https://github.com/jupyter-server/extension-cookiecutter/blob/main/%7B%7Bcookiecutter.package_name%7D%7D/.github/workflows/build.yml
    title: 生成项目 build.yml CI 源码
---

## 两套 CI 体系

模板项目维护两套 GitHub Actions 工作流：

| 工作流 | 位置 | 用途 |
|--------|------|------|
| `main.yml` | 模板仓库 `.github/workflows/` | 测试模板本身能正确生成项目并通过所有检查 |
| `build.yml` | 生成项目 `.github/workflows/` | 生成的扩展项目自己的 CI（模板渲染后包含） |

此外还有辅助工作流和配置：

| 文件 | 位置 | 用途 |
|------|------|------|
| `binder-on-pr.yml` | 生成项目 `.github/workflows/` | PR 自动评论 Binder 链接（条件包含） |
| `lint.sh` | 生成项目 `.github/workflows/` | Lint 检查脚本 |
| `dependabot.yml` | 生成项目 `.github/` | 依赖自动更新配置 |

## 模板 CI（main.yml）解析

main.yml 测试 cookiecutter 模板本身，确保模板生成的项目能正常工作。

### 触发条件

```yaml
on:
  push:
    branches: ["main"]
  pull_request:
  schedule:
    - cron: "0 0 * * *"
```

- main 分支推送时运行
- 所有 PR 运行
- 每天 UTC 0:00 定时运行（检测依赖更新导致的破坏）

### 测试矩阵

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.8", "3.11"]
```

- 3 个操作系统 × 2 个 Python 版本 = 6 个并行 job
- `fail-fast: false`：一个组合失败不取消其他组合，确保完整测试矩阵

### 关键测试步骤

模板 CI 通过 Python 脚本调用 cookiecutter API（非命令行）来生成项目：

```python
python -c "from cookiecutter.main import cookiecutter; import json; f=open('cookiecutter.json'); d=json.load(f); f.close(); d['author_name']='foo'; d['author_email']='bar@foo.com'; cookiecutter('.', extra_context=d, no_input=True)"
```

- 读取 cookiecutter.json 获取默认值
- 覆盖 author_name 和 author_email 为测试值
- `no_input=True`：非交互模式，不提示用户输入
- cookiecutter('.')：使用当前目录作为模板源

CI 覆盖四种安装场景：

1. **普通安装**：`pip install ".[test]"` → 运行 pytest → 卸载验证
2. **可编辑安装**：`pip install -e .` → 运行 pre-commit 检查 → 卸载验证
3. **Sdist 安装**：`python -m build --sdist` → `pip install dist/*.tar.gz` → 测试 → 卸载
4. **Lint 检查**：运行 `bash ./.github/workflows/lint.sh`

每个场景都包含卸载后验证扩展不再被识别（`grep ... && exit 1`），确保干净卸载。

## 生成项目 CI（build.yml）解析

build.yml 是生成的扩展项目的 CI 配置，包含 5 个并行 job。

### Job 1: build（矩阵构建+安装测试）

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']
```

- 3 OS × 4 Python 版本 = 12 个并行构建
- 安装扩展 → 验证 `jupyter server extension list` 显示 OK → 构建 sdist → 上传为 artifact
- 关键验证命令：`jupyter server extension list 2>&1 | grep -ie "{{ cookiecutter.package_name }}.*OK"`

### Job 2: check_links（链接检查）

```yaml
check_links:
  runs-on: ubuntu-latest
  steps:
    - uses: jupyterlab/maintainer-tools/.github/actions/check-links@v1
```

使用 Jupyter 维护者工具链检查文档中的链接是否有效。

### Job 3: test_lint（代码检查）

```yaml
test_lint:
  runs-on: ubuntu-latest
  steps:
    - run: bash ./.github/workflows/lint.sh
```

运行 lint.sh 脚本执行完整的代码质量检查。

### Job 4: check_release（发布检查）

```yaml
check_release:
  uses: jupyter-server/jupyter_releaser/.github/actions/check-release@v2
```

使用 [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser) 检查项目是否满足发布条件（版本号、CHANGELOG、构建产物等）。

### Job 5: test_sdist（sdist 安装测试）

```yaml
test_sdist:
  needs: build
  runs-on: ubuntu-latest
  steps:
    - uses: actions/download-artifact@v2
      with:
        name: my_server_extension-sdist
    - run: pip install my_server_extension.tar.gz
```

下载 build job 上传的 sdist artifact，验证从源码分发包安装后扩展能正常加载。依赖 `needs: build` 确保 build 完成后才运行。

## lint.sh 脚本解析

```bash
#!/usr/bin/env bash
pip install -e ".[test,lint]"
mypy --install-types --non-interactive .
ruff .
black --check --diff .
mdformat --check *.md
pipx run 'validate-pyproject[all]' pyproject.toml
```

六步检查：

| 步骤 | 命令 | 检查内容 |
|------|------|---------|
| 1 | `pip install -e ".[test,lint]"` | 安装带测试和 lint 依赖的包 |
| 2 | `mypy --install-types --non-interactive .` | 类型检查，自动安装缺失的类型 stubs |
| 3 | `ruff .` | Ruff linter 检查所有 Python 文件 |
| 4 | `black --check --diff .` | Black 格式化检查（不修改文件，只报告差异） |
| 5 | `mdformat --check *.md` | Markdown 格式化检查 |
| 6 | `validate-pyproject[all]` | 验证 pyproject.toml 格式正确性 |

注意最后一步使用 `pipx run` 在隔离环境中运行 validate-pyproject，不污染项目环境。

## binder-on-pr.yml 工作流

```yaml
name: Binder Badge
on:
  pull_request_target:
    types: [opened]
```

当 PR 打开时（`pull_request_target` 事件，使用目标仓库的 token 权限），自动在 PR 中评论一个 Binder 链接，让评审者可以一键在 Binder 上测试 PR 的改动。

```javascript
github.issues.createComment({
  body: `[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/${PR_HEAD_USERREPO}/${PR_HEAD_REF}) :point_left: Launch a Binder on branch _${PR_HEAD_USERREPO}/${PR_HEAD_REF}_`
})
```

## dependabot.yml

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: { interval: "weekly" }
  - package-ecosystem: "pip"
    directory: "/"
    schedule: { interval: "weekly" }
```

Dependabot 每周检查两类依赖更新：
- GitHub Actions 版本更新
- pip 依赖更新

## 共享 Action

两套 CI 都使用 `jupyterlab/maintainer-tools/.github/actions/base-setup@v1` 复合 action，它封装了：
- Python 环境设置
- 缓存配置
- 常用工具安装

这是 Jupyter 生态所有项目共享的 CI 基础设施，避免每个项目重复配置。

## 相关概念

- [CI/CD 工作流详解](/concepts/09-ci-workflows.md)
- [构建系统详解](/concepts/08-build-system.md)
- [代码质量工具](/concepts/11-code-quality.md)
