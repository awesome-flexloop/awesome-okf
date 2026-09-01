---
type: Concept
title: Binder 集成
description: 理解 Binder 是什么、模板中的 Binder 配置（environment.yml 和 postBuild）、如何在 PR 中自动生成 Binder 链接，以及 Binder 的适用场景。
tags: [binder, mybinder, environment-yml, post-build, reproducible]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: post-gen-hook
    resource: /references/post-gen-hook-source.md
    title: post_gen_project.py 生成后钩子解析
---

## 什么是 Binder

[Binder](https://mybinder.org) 是一个免费的云服务，可以将 GitHub 仓库中的代码在云端构建为可运行的 Jupyter 环境，任何人通过浏览器即可访问，无需本地安装。

对于 Jupyter 扩展开发者，Binder 的价值：
- **演示扩展**：用户点击链接即可在浏览器中试玩扩展，无需安装
- **PR 评审**：每个 PR 自动生成 Binder 链接，评审者可以直接测试 PR 中的改动
- **可复现教程**：文档中的示例代码可以在 Binder 中直接运行
- **无环境问题**：Binder 使用项目指定的环境配置，避免"在我机器上能跑"的问题

## 模板中的 Binder 配置

当用户在 cookiecutter 问答中将 `has_binder` 设为 `y` 时，生成的项目包含两个 Binder 文件和一个 CI 工作流：

```
my_extension/
├── binder/
│   ├── environment.yml      # Conda 环境定义
│   └── postBuild            # 构建后安装脚本
└── .github/workflows/
    └── binder-on-pr.yml     # PR 自动评论 Binder 链接
```

如果 `has_binder` 为 `n`（默认），这些文件在 post_gen_project 钩子中被删除。

## environment.yml

```yaml
name: my-server-extension-demo

channels:
  - conda-forge

dependencies:
  - python >=3.8,<3.9.0a0
  - jupyterlab >=3,<4.0.0a0
  - pip
  - wheel
  # additional packages for demos
  # - ipywidgets
```

关键配置：

| 字段 | 值 | 说明 |
|------|------|------|
| `name` | `{package_name}-demo` | Conda 环境名称（下划线转连字符） |
| `channels` | `[conda-forge]` | 使用 conda-forge 频道 |
| `python` | `>=3.8,<3.9.0a0` | Python 版本（<3.9 是因为模板生成时的测试基准） |
| `jupyterlab` | `>=3,<4.0.0a0` | JupyterLab 3.x（前端界面） |
| `pip`/`wheel` | 包含 | 用于 postBuild 中的 pip install |

> **注意**：environment.yml 固定了 Python 和 JupyterLab 的版本范围。如果你的扩展需要更新版本的 JupyterLab，需要修改此文件。

## postBuild 脚本

`postBuild` 是一个 Python 脚本，在 Binder 环境创建**之后**执行：

```python
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()

def _(*args, **kwargs):
    print("\n\t", " ".join(args), "\n")
    return_code = subprocess.call(args, **kwargs)
    if return_code != 0:
        print("\nERROR", return_code, " ".join(args))
        sys.exit(return_code)

# 1. 检查环境一致性
_(sys.executable, "-m", "pip", "check")

# 2. 开发模式安装扩展
_(sys.executable, "-m", "pip", "install", "-e", ".")

# 3. 再次检查环境一致性
_(sys.executable, "-m", "pip", "check")

# 4. 列出已安装扩展（验证安装）
_("jupyter", "server", "extension", "list")

print("JupyterLab with my_extension is ready to run with:\n")
print("\tjupyter lab\n")
```

执行流程：
1. **pip check**：验证当前环境没有依赖冲突
2. **pip install -e .**：以可编辑模式安装扩展本身
3. **pip check**：安装后再次检查依赖冲突
4. **jupyter server extension list**：列出扩展，验证扩展被正确发现

每步执行失败（返回码非零）会终止脚本并输出错误。

postBuild 的作用是在 conda 环境（由 environment.yml 定义）之上，安装项目本身及其 pip 依赖。conda 负责系统级依赖（Python、JupyterLab），pip 负责项目本身。

## README 中的 Binder Badge

当 `has_binder=y` 时，README.md 包含 Binder badge：

```markdown
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/{owner}/{repo}/main)
```

用户点击 badge 即可在 Binder 上启动项目的 main 分支。

Binder URL 格式：`https://mybinder.org/v2/gh/{GitHub_owner}/{repo}/{ref}`
- `gh` 表示 GitHub（也支持 `gl` for GitLab、`gist` for Gist）
- `{ref}` 可以是分支名、tag、commit hash

## PR 自动 Binder 链接（binder-on-pr.yml）

当 `has_binder=y` 时，`.github/workflows/binder-on-pr.yml` 配置了一个 GitHub Action：

```yaml
name: Binder Badge
on:
  pull_request_target:
    types: [opened]
```

当 PR 打开时，自动在 PR 中评论：

```
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/{PR_head_user}/{PR_head_ref}) :point_left: Launch a Binder on branch _{owner}/{branch}_
```

这个链接指向 PR 的分支，让评审者一键测试 PR 中的改动。

### 为什么用 pull_request_target

使用 `pull_request_target` 而非 `pull_request` 事件，因为：
- `pull_request` 事件在 PR 分支的上下文中运行，没有目标仓库的写权限
- `pull_request_target` 事件在目标仓库的上下文中运行，有写权限（可以评论 PR）

安全注意：`pull_request_target` 有安全风险（恶意 PR 可以窃取 secrets），但此工作流只执行评论操作，不运行 PR 中的代码。

## 使用 Binder 本地测试

Binder 配置也可以在本地使用（不依赖 mybinder.org）：

```bash
# 使用 conda 从 environment.yml 创建环境
conda env update --file binder/environment.yml
conda activate my-server-extension-demo

# 运行 postBuild
python3 binder/postBuild

# 启动 JupyterLab
jupyter lab
```

这在本地复制 Binder 环境，方便调试环境配置问题。

## Binder 最佳实践

1. **固定版本**：environment.yml 中指定版本范围，确保环境可复现
2. **最小依赖**：只包含运行扩展必须的依赖，减少构建时间
3. **测试 postBuild**：本地运行 postBuild 确保无错误
4. **考虑构建时间**：Binder 免费版有构建时间限制，尽量控制在 10 分钟内
5. **使用 conda-forge**：conda-forge 比 defaults 频道有更多 Jupyter 生态包

## 禁用 Binder

如果不需要 Binder，在生成项目时将 `has_binder` 设为 `n`（默认值）。post_gen_project.py 钩子会自动删除 binder/ 目录和 binder-on-pr.yml。

如果生成后想删除 Binder 集成：
1. 删除 `binder/` 目录
2. 删除 `.github/workflows/binder-on-pr.yml`
3. 从 README.md 中移除 Binder badge 行

## 相关概念

- [快速开始](01-getting-started.md)
- [CI/CD 工作流](09-ci-workflows.md)
- [post_gen_project 钩子解析](../references/post-gen-hook-source.md)
