---
type: Example
title: "Dry-Run 本地测试"
description: "在本地使用 dry-run 模式完整测试发布流程，不触碰任何真实服务"
tags: [dry-run, testing, local, mock]
stage: "进阶"
prerequisites:
  - "/concepts/08-dry-run-and-mock.md"
  - "/concepts/01-getting-started.md"
sources:
  - /facts.md
---

# Dry-Run 本地测试

使用 dry-run 模式在本地完整测试发布流程，所有外部 API 调用都被重定向到本地 Mock 服务器。

## 环境准备

### 安装 jupyter-releaser

```bash
pip install jupyter-releaser
# 或使用 pipx（推荐）
pipx install jupyter-releaser
```

验证安装：
```bash
jupyter-releaser --help
```

### 准备测试项目

```bash
# 克隆你的项目
git clone https://github.com/your-username/your-project.git
cd your-project

# 确保有 CHANGELOG.md 标记
grep -n "START NEW CHANGELOG ENTRY" CHANGELOG.md
```

如果没有标记，在 CHANGELOG.md 顶部添加：
```markdown
# Changelog

<!-- <START NEW CHANGELOG ENTRY> -->

<!-- <END NEW CHANGELOG ENTRY> -->
```

### 设置环境变量

```bash
# 启用 dry-run
export RH_DRY_RUN=true

# Mock 模式下 token 可以是任意值
export GITHUB_ACCESS_TOKEN=fake-token-for-testing
export GITHUB_ACTOR=your-username

# 目标仓库信息
export RH_REPOSITORY=your-username/your-project
export RH_BRANCH=main
```

Windows PowerShell：
```powershell
$env:RH_DRY_RUN = "true"
$env:GITHUB_ACCESS_TOKEN = "fake-token-for-testing"
$env:GITHUB_ACTOR = "your-username"
$env:RH_REPOSITORY = "your-username/your-project"
$env:RH_BRANCH = "main"
```

## 测试 Prep 阶段

```bash
# Step 1: 准备 git 环境
jupyter-releaser prep-git

# Step 2: 提升版本号（使用 next 便捷指定符）
jupyter-releaser bump-version --version-spec next

# Step 3: 构建 changelog entry
jupyter-releaser build-changelog --since-last-stable

# Step 4: 创建 draft release（在 Mock GitHub 服务器上）
jupyter-releaser draft-changelog
```

### 验证 Prep 结果

1. 检查版本文件是否被更新（pyproject.toml、package.json、_version.py 等）
2. 检查 CHANGELOG.md 是否插入了新的版本条目
3. Mock GitHub 服务器上应该有一个 draft release

查看 Mock 数据目录（如果设置了保留）：
```bash
# Mock 数据在临时目录中，可以通过 Python 查看
python -c "
from jupyter_releaser.util import ensure_mock_github
import os, json, glob
tmpdir = os.environ.get('JUPYTER_RELEASER_MOCK_DIR', '/tmp')
for f in glob.glob(f'{tmpdir}/jupyter_releaser_mock*/*.json'):
    print(f'=== {f} ===')
    with open(f) as fp:
        print(json.dumps(json.load(fp), indent=2)[:500])
"
```

## 测试 Populate 阶段

首先获取 draft release 的 URL（从 draft-changelog 的输出中，或通过 Mock API）：

```bash
# 设置 release URL（dry-run 中是 localhost URL）
# 查看 prep 阶段输出中的 release_url，通常类似：
# http://127.0.0.1:8000/your-username/your-project/releases/1
export RH_RELEASE_URL=http://127.0.0.1:8000/your-username/your-project/releases/1

# Step 1: 准备 git
jupyter-releaser prep-git

# Step 2: 验证 SHA
jupyter-releaser ensure-sha

# Step 3: 确认版本
jupyter-releaser bump-version

# Step 4: 提取 changelog（从 draft release body）
jupyter-releaser extract-changelog

# Step 5: 构建 npm 包（如果有 package.json）
jupyter-releaser build-npm

# Step 6: 检查 npm 包
jupyter-releaser check-npm

# Step 7: 构建 Python 包
jupyter-releaser build-python

# Step 8: 检查 Python 包
jupyter-releaser check-python

# Step 9: 创建 release commit 和 tag
jupyter-releaser tag-release

# Step 10: 再次验证 SHA
jupyter-releaser ensure-sha

# Step 11: 推送 commit/tag 并上传资产
jupyter-releaser populate-release
```

### 验证 Populate 结果

1. 检查 `dist/` 目录中是否有构建产物（.whl、.tar.gz、.tgz）
2. 检查 git log 是否有 release commit（包含 SHA256 hashes）
3. 检查 git tag 是否已创建
4. Mock 服务器上的 draft release 应该有资产上传

```bash
# 查看 dist 目录
ls -la dist/

# 查看 tags
git tag -l

# 查看最新 commit
git log --oneline -3
```

## 测试 Finalize 阶段

```bash
# Step 1: 下载并验证资产
jupyter-releaser extract-release

# Step 2: 发布资产（本地 PyPI 服务器 + npm --dry-run）
jupyter-releaser publish-assets

# Step 3: 前向移植 changelog
jupyter-releaser forwardport-changelog

# Step 4: 发布 release（在 Mock 服务器上从 draft 转为 published）
jupyter-releaser publish-release
```

### 验证 Finalize 结果

1. dist/ 目录中的资产应该已被验证（SHA256 匹配）
2. 本地 PyPI 服务器（端口 8081）应该收到了包
3. Mock GitHub 上的 release 应该被 published（不再是 draft）
4. 应该有一个 forwardport PR 被创建

```bash
# 检查本地 PyPI 服务器（如果还在运行）
curl http://localhost:8081/simple/
```

## 一行命令测试整个流程

也可以通过 `check-release` action 模拟完整流程，但本地直接调用 CLI 命令更灵活：

```bash
# 重置环境（清理之前的 mock 数据和 checkout 目录）
rm -rf .jupyter_releaser_checkout dist
# Windows: Remove-Item -Recurse -Force .jupyter_releaser_checkout, dist -ErrorAction SilentlyContinue

# 完整流程
set -e  # bash: 遇到错误立即退出
jupyter-releaser prep-git
jupyter-releaser bump-version --version-spec next
jupyter-releaser build-changelog --since-last-stable
jupyter-releaser draft-changelog
# ... 获取 release_url 后继续 populate 和 finalize
```

## 常见测试问题

### Mock 服务器启动失败

```
问题: "Address already in use" 或端口 8000 被占用
解决:
1. 找到占用进程: lsof -i :8000  (Linux/Mac) 或 netstat -ano | findstr :8000 (Windows)
2. 终止进程或设置 JUPYTER_RELEASER_MOCK_PORT 环境变量使用其他端口
```

### bump-version 找不到版本工具

```
问题: "No version tool found"
解决:
1. 确保项目有 tbump.toml、hatch 配置、bumpversion.cfg 或 package.json 之一
2. 或使用 --version-cmd 指定自定义命令
```

### build-python 失败

```
问题: 构建后端未正确配置
解决:
1. 检查 pyproject.toml 中有 [build-system] 配置
2. 检查 build 依赖已安装: pip install build twine hatchling
```

### Windows 兼容性

```
问题: tee.py 在 Windows 上使用 _run_win 而非 tee
解决: 确保使用最新版本的 jupyter-releaser，Windows 兼容性已处理
```

## CI 中的 Dry-Run 检查

在 GitHub Actions 中，每次 PR 和 push 都自动运行 dry-run 检查：

```yaml
name: Check Release
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  check_release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jupyter-server/jupyter_releaser/.github/actions/check-release@v2
        with:
          version_spec: next
        env:
          ADMIN_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

这确保发布配置在代码变更时被持续验证。
