---
type: Example
title: "自定义 Hooks 和配置"
description: "常见 hook 配置场景：前端构建步骤、版本文件更新、发布后通知等"
tags: [hooks, config, customization, toml]
stage: "核心"
prerequisites:
  - "/concepts/04-config-and-hooks.md"
sources:
  - /facts.md
---

# 自定义 Hooks 和配置

## 场景1：Jupyter Lab Extension 典型配置

Jupyter Lab Extension 同时包含 Python 包和 npm 包，npm 构建产出 Python 包需要的静态资源。

```toml
# pyproject.toml
[tool.jupyter-releaser]
# 跳过默认的 link 检查（labextension 不需要）
skip = ["check-links"]

[tool.jupyter-releaser.hooks]
# npm 构建前：安装依赖并编译前端
before-build-npm = [
    "python -m jupyterlab.labextension build",
    "jlpm install",
    "jlpm run build:lib"
]
# Python 构建前：构建生产版本的 labextension
before-build-python = [
    "jlpm run build:prod",
    "pip install check-manifest && check-manifest -v"
]
# 版本提升后：同步更新其他文件
after-bump-version = [
    "python scripts/update_version.py"
]
# tag 创建后：更新文档
after-tag-release = [
    "python scripts/update_docs_version.py"
]
# 发布后：通知
after-publish-assets = [
    "echo 'Release completed successfully!'"
]

[tool.jupyter-releaser.options.draft-changelog]
since_last_stable = true
branch = "main"

[tool.jupyter-releaser.options.tag-release]
tag_message = "Release {version}"
```

## 场景2：纯 Python 包 + Hatch 版本管理

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-python-package"
version = "1.0.0"

[tool.hatch.version]
source = "vcs"  # 从 git tag 获取版本

[tool.jupyter-releaser.options]
draft-changelog = { since_last_stable = true }

[tool.jupyter-releaser.hooks]
after-build-python = [
    "pip install twine && twine check dist/*"
]
```

## 场景3：多 Python 包 Monorepo

```toml
# .jupyter-releaser.toml
[tool.jupyter-releaser.options.populate-release]
python_packages = [
    "./packages/core:my-core-package",
    "./packages/plugin:my-plugin-package",
    "./packages/cli:my-cli-package"
]

[tool.jupyter-releaser.options.tag-release]
# 不标记 npm workspace（这是纯 Python monorepo）
no_git_tag_workspace = true
```

## 场景4：npm Workspace Monorepo

```jsonc
// package.json（根目录）
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "jupyter-releaser": {
    "skip": ["build-python", "check-python"],
    "hooks": {
      "before-build-npm": [
        "npm run build"
      ]
    },
    "options": {
      "tag-release": {
        "no_git_tag_workspace": false
      }
    }
  }
}
```

```toml
# .jupyter-releaser.toml（补充配置）
[tool.jupyter-releaser.options.draft-changelog]
since_last_stable = true
silent = false
```

## 场景5：使用 Silent Changelog 模式

当 changelog 需要在发布后才能最终确定时（例如需要包含 PyPI 链接）：

```toml
[tool.jupyter-releaser.options.draft-changelog]
silent = true
branch = "main"
since_last_stable = true
```

然后在 finalize 阶段后，单独运行 publish-changelog action：

```yaml
# .github/workflows/publish-changelog.yml
name: Publish Changelog
on:
  release:
    types: [published]

jobs:
  publish_changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: jupyter-server/jupyter_releaser/.github/actions/publish-changelog@v2
        env:
          ADMIN_GITHUB_TOKEN: ${{ secrets.ADMIN_GITHUB_TOKEN }}
```

## 场景6：自定义版本命令

当项目有非标准的版本获取方式时：

```toml
[tool.jupyter-releaser.options]
# 使用自定义命令获取版本
version_cmd = "python -c 'import mypackage; print(mypackage.__version__)'"
```

## 场景7：跳过特定检查步骤

```toml
[tool.jupyter-releaser.skip]
# 全局跳过
"*" = ["piplite-check"]
# 特定命令跳过
build-python = ["twine-check", "pip-install-check"]
check-python = ["piplite-check"]
```

对应的 CLI 方式（使用 --force 不跳过任何步骤）：
```bash
jupyter-releaser --force build-python
```

## 场景8：使用 post version（dev 版本模式）

发布后自动 bump 到 dev 版本继续开发：

通过 workflow_dispatch 输入设置：
```yaml
# prep-release workflow 输入
post_version_spec:
  description: "Post version spec (e.g. dev)"
  required: false
  default: "dev"
```

这会在 release tag 创建后，自动 bump 到下一个 dev 版本（如 `1.2.1.dev0`），并 push 到 main 分支。

## 配置验证

使用 `jupyter-releaser list-envvars` 可以查看所有环境变量和默认值，帮助调试配置：

```bash
jupyter-releaser list-envvars
```

输出包含每个选项的：
- 环境变量名（`RH_*`）
- 默认值
- 帮助文本

这在排查"为什么我的配置没有生效"时很有用——检查环境变量是否被正确设置。
