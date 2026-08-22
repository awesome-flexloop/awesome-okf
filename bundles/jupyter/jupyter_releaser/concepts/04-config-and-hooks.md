---
type: Concept
title: "配置与 Hooks 系统"
description: "三源配置优先级、hooks 机制（before/after）、skip 跳过机制、options 参数覆盖、JSON Schema 校验"
tags: [config, hooks, toml, schema, skip]
stage: "核心"
prerequisites: ["03-cli-commands.md"]
sources:
  - /references/cli-source.md#核心类releasehelpergroup
  - /references/util-source.md#配置与环境
---

# 配置与 Hooks 系统

jupyter_releaser 的配置系统提供三种扩展机制：hooks（命令钩子）、skip（跳过步骤）、options（参数默认值覆盖），且通过 JSON Schema 校验配置合法性。

## 三源配置优先级

配置可以写在三个位置，优先级从高到低：

1. **`.jupyter-releaser.toml`**（项目根目录）—— 最高优先级，专属配置文件
2. **`pyproject.toml`** 中的 `[tool.jupyter-releaser]` 表 —— Python 项目推荐
3. **`package.json`** 中的 `"jupyter-releaser"` 字段 —— npm 项目使用

三个位置的配置会合并，高优先级覆盖低优先级。

### 配置结构

```toml
# .jupyter-releaser.toml 或 pyproject.toml [tool.jupyter-releaser]
[tool.jupyter-releaser.hooks]
before-<command-name> = ["shell command 1", "shell command 2"]
after-<command-name> = "shell command"

[tool.jupyter-releaser.options]
<command-name> = { option-name = "value" }

[tool.jupyter-releaser.skip]
<command-name> = ["step-name-1", "step-name-2"]
```

```jsonc
// package.json
{
  "jupyter-releaser": {
    "hooks": {
      "before-build-python": ["npm run build"]
    },
    "options": {
      "tag-release": { "tag_message": "Release {version}" }
    },
    "skip": ["check-links"]
  }
}
```

## Hooks 机制

### Hook 命名规则

hooks 按命令名匹配，格式为 `before-<command>` 和 `after-<command>`：

| Hook 名 | 触发时机 |
|---------|---------|
| `before-prep-git` | prep-git 命令执行前 |
| `after-build-python` | build-python 命令执行后 |
| `before-tag-release` | tag-release 命令执行前 |
| `after-populate-release` | populate-release 命令执行后 |

特殊情况：`prep-git` 和 `extract-release` 执行后会**重新读取配置**——这是因为这两个命令可能从远程获取了新的配置文件（如 bump-version 后 pull 的新版本）。因此 after 这两个命令的 hook 使用新配置。

### Hook 执行方式

hooks 是**shell 命令字符串**（或字符串列表），在 checkout 目录中通过 `util.run()` 执行：

```toml
[tool.jupyter-releaser.hooks]
before-build-python = "npm run build:prod"
after-tag-release = [
    "git push origin main --tags",
    "python scripts/post_tag.py"
]
```

**重要特性**：
- hooks 不是 Python 插件，不共享 Python 上下文
- hooks 中可以使用所有 `RH_*` 环境变量
- hooks 的 cwd 是 checkout 目录（`.jupyter_releaser_checkout/`）
- hook 命令失败会中断整个流程（非零退出码）

### 常用 Hook 示例

| Hook | 用途 |
|------|------|
| `before-build-python` | 在 Python 构建前执行编译/转译步骤 |
| `before-build-npm` | 在 npm 构建前执行前端构建 |
| `after-bump-version` | 版本提升后更新其他文件 |
| `after-tag-release` | tag 创建后执行额外操作（如通知、更新文档） |
| `after-populate-release` | 资产上传后的后处理 |
| `after-publish-assets` | 发布后通知（Slack、邮件等） |

## Skip 机制

### 跳过列表

`skip` 是一个字符串列表，指定要跳过的步骤名称。skip 项与命令名对应：

```toml
[tool.jupyter-releaser.skip]
prep-git = ["check-links"]
build-python = ["twine-check"]
```

或全局 skip（不指定命令的列表形式）：

```toml
skip = ["check-links"]  # 全局跳过 link 检查
```

### --force 参数

CLI 的 `--force` 标志会清空所有 skip 列表，强制执行所有步骤。用于确认无误后跳过安全检查。

### RH_STEPS_TO_SKIP 环境变量

环境变量 `RH_STEPS_TO_SKIP` 可以追加跳过步骤，以逗号分隔：

```bash
RH_STEPS_TO_SKIP=check-links,piplite-check jupyter-releaser build-python
```

## Options 参数覆盖

options 配置为 CLI 参数提供默认值覆盖。配置格式为：

```toml
[tool.jupyter-releaser.options.<command-name>]
<option-name-with-dashes> = value
```

例如：

```toml
[tool.jupyter-releaser.options.tag-release]
tag_message = "Release v{version}"
no_git_tag_workspace = true

[tool.jupyter-releaser.options.draft-changelog]
since_last_stable = true
silent = false
```

**优先级提醒**：options 中的值被 CLI 参数和环境变量覆盖（参见三层优先级）。

## JSON Schema 校验

jupyter_releaser 内置了 `schema.json`，在 `read_config()` 时对配置进行校验：

- `skip`：必须是字符串列表
- `options`：键为命令名，值为对象（选项名→值）
- `hooks`：键为 hook 名，值为字符串或字符串列表

校验失败时抛出明确错误，提示配置格式问题。

## 典型配置场景

### 场景1：纯 Python 项目

```toml
# pyproject.toml
[tool.jupyter-releaser.options]
draft-changelog = { since_last_stable = true }

[tool.jupyter-releaser.hooks]
after-tag-release = "python scripts/update_version_in_docs.py"
```

### 场景2：Jupyter Lab Extension（Python + npm 混合）

```toml
[tool.jupyter-releaser.hooks]
before-build-npm = "jlpm run build:lib"
before-build-python = "jlpm run build:prod"
after-build-python = "pip install check-manifest && check-manifest -v"

[tool.jupyter-releaser.options]
draft-changelog = { branch = "main", since_last_stable = true }
```

### 场景3：只发布 npm 包

```jsonc
// package.json
{
  "name": "my-npm-package",
  "version": "1.0.0",
  "jupyter-releaser": {
    "skip": ["build-python", "check-python", "publish-assets-python"],
    "options": {
      "build-npm": { "python_packages": [] }
    }
  }
}
```

### 场景4：Monorepo（多 npm workspace）

```toml
[tool.jupyter-releaser.options.tag-release]
no_git_tag_workspace = false  # 对每个 workspace package 执行 npm dist-tag

[tool.jupyter-releaser.options.populate-release]
python_packages = ["./packages/pkg1:pkg1", "./packages/pkg2:pkg2"]
```

## 相关文档

- [CLI命令详解](03-cli-commands.md)
- [发布流水线详解](05-release-pipeline.md)
- [Python与npm双生态发布](06-python-npm-dual.md)
