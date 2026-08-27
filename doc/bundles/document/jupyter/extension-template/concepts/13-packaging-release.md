---
type: Concept
title: 打包与发布
description: 掌握手动发布流程、Jupyter Releaser 自动化发布、版本管理、双包同步发布到 PyPI 和 NPM 的完整流程。
tags: [packaging, release, pypi, npm, jupyter-releaser, hatch, twine, distribution]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: release-md
    location: template/RELEASE.md.jinja
    lines: "1-88"
  - id: pyproject
    resource: /references/pyproject-source.md
    title: pyproject.toml 模板字段解析
---

## 打包与发布

JupyterLab 扩展采用双包发布模式：Python wheel 包发布到 PyPI，NPM 包发布到 npmjs.com。模板支持两种发布方式：手动发布和 Jupyter Releaser 自动化发布。

## 版本管理

### 版本真值

`package.json` 的 `version` 字段是版本号的唯一真值。通过 `hatch-nodejs-version` 插件，Python 包的版本自动从 package.json 同步：

```json
// package.json
{ "version": "0.1.0" }
```

```toml
# pyproject.toml
[tool.hatch.version]
source = "nodejs"  # 从 package.json 读取版本
```

**不要手动编辑 pyproject.toml 中的版本号**——始终修改 package.json。

### 更新版本

使用 `hatch version` 命令更新版本：

```bash
# 自动递增（基于 semver）
hatch version minor    # 0.1.0 → 0.2.0
hatch version major    # 0.1.0 → 1.0.0
hatch version patch    # 0.1.0 → 0.1.1

# 指定具体版本
hatch version 1.0.0
```

默认情况下，`hatch version` 会创建一个 Git tag。

## 手动发布

### 准备工作

```bash
pip install build twine hatch
```

确保你有 PyPI 和 NPM 的发布账号和权限。

### 步骤 1：更新版本

```bash
hatch version <new-version>
```

### 步骤 2：清理构建产物

```bash
jlpm clean:all
# 可选：清理所有未跟踪文件
git clean -dfX
```

### 步骤 3：构建 Python 包

```bash
python -m build
```

这会在 `dist/` 目录生成两个文件：
- `myextension-0.1.0.tar.gz`：源码包（sdist）
- `myextension-0.1.0-py3-none-any.whl`：纯 Python wheel 包（binary）

> 注意：`python setup.py sdist bdist_wheel` 已废弃，不适用于此项目。必须使用 `python -m build`。

### 步骤 4：上传到 PyPI

```bash
twine upload dist/*
```

需要提供 PyPI 用户名和密码（或 API token）。

### 步骤 5：发布 NPM 包

```bash
npm login
npm publish --access public
```

`--access public` 是必须的，因为 scoped package（如 `@myorg/myextension`）默认是私有的。

### 步骤 6：创建 GitHub Release

1. 将版本更新提交推送到 GitHub
2. 在 GitHub Releases 页面创建新 release
3. 使用版本号作为 tag 和标题
4. 粘贴 CHANGELOG 中对应版本的条目
5. 上传 dist/ 中的 wheel 和 sdist 文件

## Jupyter Releaser 自动化发布

Jupyter Releaser 是 Jupyter 生态推荐的发布工具，自动化版本管理、CHANGELOG 生成、双包发布和 GitHub Release 创建。

### 一次性设置

1. 安装 [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser) GitHub App 到你的仓库
2. 在仓库 Settings 中：
   - 创建 `release` environment
   - 添加 `APP_ID` 作为 repository variable（GitHub App ID）
   - 添加 `APP_PRIVATE_KEY` 作为 repository secret（GitHub App 私钥）
   - 可选：添加 `NPM_TOKEN` secret（不使用 trusted publishing 时）
3. 在 PyPI 上配置 [trusted publishing](https://docs.pypi.org/trusted-publishers/)（推荐）
4. 在 NPM 上配置 [trusted publishing](https://docs.npmjs.com/trusted-publishers)（推荐）

### 发布流程

#### Step 1：准备发布

1. 前往 GitHub Actions 页面
2. 选择 "Step 1: Prep Release" workflow
3. 点击 "Run workflow"
4. 填写参数：
   - **version_spec**：版本规则（默认 "next" 自动选择，或 "minor"/"major"/"patch"/具体版本号）
   - **branch**：目标分支（默认 main）
   - **since_last_stable**：勾选后从上个稳定版本开始收集 PR
5. 等待工作流完成
6. 查看生成的 draft GitHub Release，检查 CHANGELOG 是否正确

#### Step 2：审核并发布

1. 审核 draft release 的 CHANGELOG 和产物
2. 选择 "Step 2: Publish Release" workflow
3. 点击 "Run workflow"
4. 输入 draft release 的 URL
5. 如果配置了 `release` environment 的审批规则，等待审批
6. 工作流自动完成：
   - 发布到 PyPI
   - 发布到 NPM
   - 发布 GitHub Release
   - 创建 Git tag
   - 更新到下一个开发版本

### Jupyter Releaser 与 PR 标签

Jupyter Releaser 根据 PR 标签自动分类 CHANGELOG 条目：

| 标签 | CHANGELOG 分类 |
|------|---------------|
| `enhancement` | New Features |
| `bug` | Bug Fixes |
| `maintenance` | Maintenance |
| `documentation` | Documentation |
| `breaking` | Breaking Changes（前缀 BREAKING CHANGE） |

这就是 `enforce-label.yml` 工作流强制 PR 必须有标签的原因。

## conda-forge 发布

发布到 PyPI 后，可以通过 conda-forge 分发：

1. 如果包尚未在 conda-forge 上，按照 [adding packages](https://conda-forge.org/docs/maintainer/adding_pkgs.html) 指南添加
2. 如果已在 conda-forge 上，conda-forge 的 bot 会自动检测 PyPI 新版本并创建更新 PR
3. 审核并合并 bot 创建的 PR

## 发布检查清单

发布前确认以下事项：

- [ ] 所有测试通过（`jlpm run test && pytest`）
- [ ] Lint 通过（`jlpm run lint:check`）
- [ ] CHANGELOG.md 已更新（自动化发布由 Releaser 处理）
- [ ] 版本号正确（`hatch version` 检查）
- [ ] `jlpm clean:all && python -m build` 本地构建成功
- [ ] wheel 包安装后扩展正常工作（本地验证）
- [ ] 前端扩展注册成功（`jupyter labextension list` 显示 OK）
- [ ] 后端扩展注册成功（frontend-and-server 类型，`jupyter server extension list` 显示 OK）

## 包的安装验证

用户安装后可以通过以下命令验证：

```bash
# 验证前端扩展
jupyter labextension list
# 应显示：myextension v0.1.0 enabled OK

# 验证后端扩展（frontend-and-server 类型）
jupyter server extension list
# 应显示：myextension enabled OK

# 启动 JupyterLab
jupyter lab
# 检查浏览器控制台没有错误
```

## 相关概念

- [CI/CD 工作流详解](12-ci-workflows.md)
- [双包构建系统](05-build-system.md)
- [pyproject.toml 模板解析](../references/pyproject-source.md)
- [package.json 模板解析](../references/package-json-source.md)
