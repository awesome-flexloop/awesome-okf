---
type: Concept
title: 打包发布
description: 掌握 Jupyter Server 扩展的发布流程，包括手动发布（build + twine）、Jupyter Releaser 自动化发布、conda-forge 发布，以及版本管理和 CHANGELOG 维护。
tags: [packaging, release, pypi, jupyter-releaser, conda-forge, twine, publish]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ci-source
    resource: /references/ci-workflow-source.md
    title: CI/CD 工作流源码解析
---

## 发布方式概览

模板支持三种发布方式：

| 方式 | 工具 | 适合场景 | 自动化程度 |
|------|------|---------|-----------|
| **手动发布** | build + twine | 首次发布、小规模项目 | 手动操作 |
| **Jupyter Releaser** | GitHub Actions | Jupyter 生态标准流程 | 全自动 |
| **conda-forge** | conda-forge feedstock | Conda 用户 | PyPI 发布后自动 |

## 发布前检查清单

发布前确保：

- [ ] 所有测试通过（CI 绿色）
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新（`__init__.py` 中的 `__version__`）
- [ ] 本地构建成功（`python -m build`）
- [ ] sdist 安装测试通过
- [ ] 所有 lint 检查通过

## 手动发布

### 步骤 1：安装构建工具

```bash
pip install build twine
```

- `build`：PEP 517 兼容的构建工具，生成 wheel 和 sdist
- `twine`：安全上传包到 PyPI

### 步骤 2：更新版本号

编辑 `my_extension/__init__.py`，更新版本号：

```python
__version__ = "0.2.0"  # 从 0.1.0 更新为新版本
```

遵循 [Semantic Versioning](https://semver.org/)：
- **MAJOR**（主版本）：不兼容的 API 变更
- **MINOR**（次版本）：向后兼容的新功能
- **PATCH**（补丁版本）：向后兼容的 bug 修复

### 步骤 3：构建分发包

```bash
python -m build
```

在 `dist/` 目录生成：
- `my_extension-0.2.0-py3-none-any.whl`（wheel）
- `my_extension-0.2.0.tar.gz`（sdist）

> **注意**：RELEASE.md 明确指出 `python setup.py sdist bdist_wheel` 已弃用，不适用于本项目。必须使用 `python -m build`。

### 步骤 4：测试上传到 TestPyPI（可选但推荐）

```bash
# 上传到 TestPyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ my-extension
```

在 TestPyPI 上验证包可以正确安装和运行。

### 步骤 5：上传到 PyPI

```bash
twine upload dist/*
```

需要 PyPI 账号和 API token。首次上传需要在 PyPI 注册账号并创建 token。

上传成功后，任何人都可以通过 `pip install my-extension` 安装你的扩展。

### 步骤 6：创建 Git Tag

```bash
git tag v0.2.0
git push origin v0.2.0
```

Tag 名称以 `v` 开头，后跟版本号。

### 步骤 7：创建 GitHub Release

在 GitHub 上创建 Release，附上 CHANGELOG 和 dist 文件。

## Jupyter Releaser 自动化发布

[Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser) 是 Jupyter 生态标准的自动化发布工具，通过 GitHub Actions 一键完成所有发布步骤。

### 前置设置

1. **Fork jupyter-releaser 仓库**：
   - 访问 https://github.com/jupyter-server/jupyter_releaser
   - Fork 到你的账号/组织

2. **添加 Secrets**：在 fork 仓库的 Settings → Secrets 中添加：
   - `ADMIN_GITHUB_TOKEN`：具有 repo 权限的 GitHub Personal Access Token
   - `PYPI_TOKEN`：PyPI API token
   - `NPM_TOKEN`：NPM token（纯 Python 扩展不需要）

### 发布流程（三步）

模板 CI 中已配置 `check_release` Job，发布时通过 Jupyter Releaser 的 Actions 面板执行：

**Step 1: Draft Changelog**
- 运行 "Draft Changelog" 工作流
- 输入目标仓库和版本规范
- Jupyter Releaser 自动生成 CHANGELOG PR
- 审查并合并 CHANGELOG PR

**Step 2: Draft Release**
- 运行 "Draft Release" 工作流
- 在目标仓库创建一个 Draft Release
- 自动构建产物、生成发布说明

**Step 3: Publish Release**
- 运行 "Publish Release" 工作流
- 自动发布到 PyPI
- 创建 Git tag
- 发布 GitHub Release

Jupyter Releaser 自动处理：
- ✅ 版本号升级（基于 PR labels）
- ✅ CHANGELOG 生成
- ✅ 构建验证
- ✅ PyPI 上传
- ✅ Git tag 创建
- ✅ GitHub Release 发布
- ✅ NPM 发布（如果有前端）

这是 Jupyter 官方推荐的发布方式，因为它标准化了发布流程，减少了人为错误。

## NPM 包发布（纯后端不需要）

RELEASE.md 提到了 NPM 包发布，但纯 Jupyter Server 扩展（本模板生成的类型）没有前端代码，不需要发布 NPM 包。

只有同时包含 JupyterLab 前端的扩展才需要 NPM 发布，这种情况应使用 [JupyterLab Extension Template](https://github.com/jupyterlab/extension-template) 而非本模板。

## conda-forge 发布

发布到 PyPI 后，可以通过 conda-forge 让 Conda 用户安装：

### 首次添加到 conda-forge

1. 检查 https://conda-forge.org/docs/maintainer/adding_pkgs.html 文档
2. 使用 conda-smithy 创建 feedstock
3. 提交 PR 到 conda-forge/staged-recipes

### 后续版本发布

发布到 PyPI 后，conda-forge 的 bot 会自动检测新版本并在 feedstock 仓库创建 PR。维护者合并 PR 即可发布新版本到 conda-forge。

用户通过 conda 安装：
```bash
conda install -c conda-forge my-extension
```

## CHANGELOG 维护

模板生成的 CHANGELOG.md 包含 Jupyter Releaser 的标记：

```markdown
# Changelog

<!-- <START NEW CHANGELOG ENTRY> -->

<!-- <END NEW CHANGELOG ENTRY> -->
```

Jupyter Releaser 自动在这两个标记之间插入新版本的变更记录。如果手动维护 CHANGELOG，在标记之间添加条目：

```markdown
<!-- <START NEW CHANGELOG ENTRY> -->

## 0.2.0

- Added new endpoint /api/items
- Fixed authentication issue

<!-- <END NEW CHANGELOG ENTRY> -->

## 0.1.0

- Initial release
```

## 版本验证

发布后立即验证：

```bash
# 创建新的虚拟环境
python -m venv /tmp/test-install
source /tmp/test-install/bin/activate  # Windows: /tmp/test-install/Scripts/activate

# 安装
pip install my-extension

# 验证安装
jupyter server extension list
# 应显示 my_extension OK

# 验证 API 工作
jupyter server  # 启动后测试端点
```

## 相关概念

- [CI/CD 工作流](09-ci-workflows.md)
- [构建系统详解](08-build-system.md)
- [快速开始](01-getting-started.md)
