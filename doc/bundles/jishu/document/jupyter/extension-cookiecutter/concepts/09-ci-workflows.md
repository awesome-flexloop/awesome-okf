---
type: Concept
title: CI/CD 工作流
description: 理解模板生成的 GitHub Actions CI/CD 配置，包括多平台矩阵构建、链接检查、Lint、Jupyter Releaser 发布检查，以及模板自身的 CI 测试机制。
tags: [ci-cd, github-actions, build-matrix, jupyter-releaser, automation]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ci-source
    resource: /references/ci-workflow-source.md
    title: CI/CD 工作流源码解析
---

## 两套 CI 体系

extension-cookiecutter 项目维护两套 CI：

| CI | 文件 | 作用 |
|----|------|------|
| **模板 CI** | `.github/workflows/main.yml`（模板仓库） | 测试模板本身能正确生成项目 |
| **项目 CI** | `.github/workflows/build.yml`（生成的项目） | 生成的扩展自己的 CI |

两套 CI 都使用 [jupyterlab/maintainer-tools](https://github.com/jupyterlab/maintainer-tools) 提供的共享复合 Action，避免重复配置。

## 生成项目的 CI（build.yml）

生成的项目包含 `.github/workflows/build.yml`，定义了 5 个并行 Job。

### 触发条件

```yaml
on:
  push:
    branches: ["main"]
  pull_request:
  schedule:
    - cron: "0 0 * * *"
```

- **push to main**：代码合并到主分支时运行
- **pull_request**：所有 PR 运行
- **schedule**：每天 UTC 0:00 定时运行（检测依赖更新导致的破坏）

所有 Job 使用 `bash -eux {0}` 作为默认 shell：
- `-e`：命令失败立即退出
- `-u`：未定义变量报错
- `-x`：打印执行的命令（便于调试）

### Job 1：build（矩阵构建+安装测试）

```yaml
build:
  runs-on: ubuntu-latest
  strategy:
    fail-fast: false
    matrix:
      os: [ubuntu-latest, macos-latest, windows-latest]
      python-version: ['3.8', '3.9', '3.10', '3.11']
```

- **3 个操作系统**：Ubuntu（Linux）、macOS、Windows
- **4 个 Python 版本**：3.8、3.9、3.10、3.11
- 共 12 个并行构建
- `fail-fast: false`：一个组合失败不取消其他组合，确保所有平台都被测试

构建步骤：
1. 安装 Jupyter Server
2. `pip install .` 安装扩展
3. 验证 `jupyter server extension list` 显示扩展 OK
4. 构建 sdist
5. 上传 sdist 为 artifact

关键验证命令：
```bash
jupyter server extension list 2>&1 | grep -ie "my_server_extension.*OK"
```
使用 grep 检查扩展状态包含 "OK"，如果扩展未正确加载，grep 返回非零退出码导致 CI 失败。

### Job 2：check_links（链接检查）

```yaml
check_links:
  uses: jupyterlab/maintainer-tools/.github/actions/check-links@v1
```

使用 Jupyter 维护者工具检查 README 和文档中的所有链接是否有效。死链会导致 CI 失败。

### Job 3：test_lint（代码检查）

```yaml
test_lint:
  run: bash ./.github/workflows/lint.sh
```

运行 lint.sh 脚本，执行完整的代码质量检查（mypy、ruff、black、mdformat、validate-pyproject）。

### Job 4：check_release（发布检查）

```yaml
check_release:
  uses: jupyter-server/jupyter_releaser/.github/actions/check-release@v2
```

使用 [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser) 检查项目是否满足发布条件：
- CHANGELOG.md 格式正确
- 版本号一致
- 构建产物有效
- 无遗漏文件

这是正式发布前的"预演"检查，确保发布过程不会出错。

### Job 5：test_sdist（sdist 安装测试）

```yaml
test_sdist:
  needs: build
```

- `needs: build`：依赖 build Job 完成后才运行
- 下载 build Job 上传的 sdist artifact
- 在干净环境中从 sdist 安装
- 验证扩展正确加载

这个 Job 确保源码分发包（sdist）可以独立正确安装，而不仅仅是 git checkout 安装。

## Lint 脚本（lint.sh）

`.github/workflows/lint.sh` 是 CI 中执行的 Lint 检查脚本：

```bash
#!/usr/bin/env bash
pip install -e ".[test,lint]"
mypy --install-types --non-interactive .
ruff .
black --check --diff .
mdformat --check *.md
pipx run 'validate-pyproject[all]' pyproject.toml
```

| 步骤 | 工具 | 检查内容 |
|------|------|---------|
| 1 | pip | 安装所有依赖（test + lint） |
| 2 | mypy | 类型检查，自动安装缺失的类型 stubs |
| 3 | ruff | 快速 Linter，检查代码质量问题 |
| 4 | black | 代码格式化检查（`--check` 只报告不修改，`--diff` 显示差异） |
| 5 | mdformat | Markdown 文件格式化检查 |
| 6 | validate-pyproject | pyproject.toml 格式验证 |

本地运行 lint：
```bash
bash .github/workflows/lint.sh
```

## 模板自身的 CI（main.yml）

模板仓库的 CI（main.yml）测试 cookiecutter 模板能正确生成项目。它使用一个 Python 技巧来非交互式生成项目：

```python
python -c "from cookiecutter.main import cookiecutter; import json; f=open('cookiecutter.json'); d=json.load(f); f.close(); d['author_name']='foo'; d['author_email']='bar@foo.com'; cookiecutter('.', extra_context=d, no_input=True)"
```

这个脚本：
1. 以编程方式调用 cookiecutter API（不是命令行）
2. 读取 cookiecutter.json 默认值
3. 覆盖 author_name 和 author_email 为测试值
4. `no_input=True` 非交互式生成
5. cookiecutter('.') 使用当前目录作为模板源

模板 CI 覆盖四种场景：
1. **普通安装**：`pip install ".[test]"` → pytest → 卸载验证
2. **可编辑安装**：`pip install -e .` → pre-commit 检查 → 卸载验证
3. **Sdist 安装**：`python -m build --sdist` → 从 tar.gz 安装 → 测试
4. **Lint 检查**：运行 lint.sh

每个场景都包含"卸载后验证扩展消失"的步骤，确保卸载干净。

## Dependabot 配置

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

Dependabot 每周自动检查两类依赖更新：
- GitHub Actions 的版本更新
- pip 依赖的版本更新

更新会自动创建 PR，CI 运行测试确保更新不破坏功能。

## Binder PR 工作流

当 `has_binder=y` 时，生成的项目包含 `binder-on-pr.yml`：

```yaml
name: Binder Badge
on:
  pull_request_target:
    types: [opened]
```

当 PR 打开时，自动在 PR 中评论一个 Binder 链接，评审者可以点击链接在 Binder 云端环境中测试 PR 改动。

使用 `pull_request_target`（而非 `pull_request`）事件，因为这个事件拥有目标仓库的写权限（可以评论）。

## 本地 CI 调试

在本地运行 CI 等价检查：

```bash
# 运行测试
pytest

# 运行 lint
bash .github/workflows/lint.sh

# 构建并检查 sdist
pip install build
python -m build --sdist
pip install dist/*.tar.gz
jupyter server extension list
```

## Jupyter Releaser 集成

check_release Job 集成了 Jupyter Releaser，支持自动化发布流程：

1. 在 GitHub Actions 中运行 "Draft Changelog" 工作流
2. 合并 CHANGELOG PR
3. 运行 "Draft Release" 工作流
4. 运行 "Publish Release" 工作流——自动发布到 PyPI 和 NPM

Jupyter Releaser 还自动处理：
- 版本号升级
- Git tag 创建
- GitHub Release 生成
- PyPI 上传
- CHANGELOG 更新

详细发布步骤参见 [RELEASE.md](12-packaging-release.md)。

## 相关概念

- [打包发布指南](12-packaging-release.md)
- [代码质量工具](11-code-quality.md)
- [构建系统详解](08-build-system.md)
- [CI/CD 工作流源码解析](../references/ci-workflow-source.md)
