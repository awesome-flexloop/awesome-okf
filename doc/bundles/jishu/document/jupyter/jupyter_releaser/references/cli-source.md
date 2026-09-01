---
type: Reference
title: "cli.py 源码信源"
description: "jupyter_releaser CLI 层源码：ReleaseHelperGroup 命令组、19个子命令定义、公共选项工厂函数"
tags: [cli, click, commands, options]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-grep", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: cli-source
    resource: /references/cli-source.md
    title: "cli.py Source Code Reference"
---

# cli.py 源码信源

## 文件位置

`jupyter_releaser/cli.py`（约 750 行）

## 模块职责

CLI 层基于 Click 框架实现，提供 `jupyter-releaser` 命令行工具。核心类是 `ReleaseHelperGroup`，它扩展了 `click.Group`，在命令调用前后自动处理配置加载、参数覆盖、hooks 执行和工作目录切换。

## 核心类：ReleaseHelperGroup

| 成员 | 类型 | 说明 |
|------|------|------|
| `_needs_checkout_dir` | `Dict[str, bool]` | 类变量，记录哪些命令需要 checkout 目录 |
| `invoke(ctx)` | 方法 | 重写 click.Group.invoke，处理配置/hooks/参数优先级/checkout目录 |
| `list_commands(ctx)` | 方法 | 返回命令键，保持插入顺序 |

### invoke 方法执行流程

1. 处理 `list-envvars` 特殊命令（遍历所有命令参数收集 envvar）
2. 检查需要 checkout 目录的命令，切换工作目录
3. 读取配置（`util.read_config()`）：hooks、options、skip
4. 处理 `--force` 参数清空 skip 列表
5. 从 `RH_STEPS_TO_SKIP` 环境变量追加跳过步骤
6. 参数值三层优先级：env var > CLI arg > options config > default
7. 执行 `before-{cmd_name}` hooks
8. 调用 `super().invoke(ctx)` 执行实际命令
9. 对 prep-git/extract-release 重新读取配置
10. 执行 `after-{cmd_name}` hooks
11. 切回原工作目录

## 装饰器工厂函数

| 函数 | 说明 |
|------|------|
| `add_options(options)` | 批量添加 click option 到命令（reversed 顺序） |
| `use_checkout_dir()` | 标记命令需要 checkout 目录，注册到 `_needs_checkout_dir` |

## CLI 命令清单

| 命令 | 对应函数 | 需要checkout | 主要功能 |
|------|---------|:---:|------|
| `list-envvars` | `list_envvars` | 否 | 列出所有环境变量 |
| `prep-git` | `prep_git` | 否 | 准备 git 仓库和环境 |
| `bump-version` | `bump_version` | 是 | 提升版本号 |
| `extract-changelog` | `extract_changelog` | 是 | 从 draft release 提取 changelog |
| `build-changelog` | `build_changelog` | 是 | 构建 changelog entry |
| `draft-changelog` | `draft_changelog` | 是 | 创建 changelog draft PR |
| `build-python` | `build_python` | 是 | 构建 Python 分发包 |
| `check-python` | `check_python` | 是 | 检查 Python 分发包 |
| `build-npm` | `build_npm` | 是 | 构建 npm 包 |
| `check-npm` | `check_npm` | 是 | 检查 npm 包 |
| `tag-release` | `tag_release` | 是 | 创建 release commit 和 tag |
| `populate-release` | `populate_release` | 是 | 填充 release 资产并推送 |
| `delete-release` | `delete_release` | 是 | 删除 draft release |
| `extract-release` | `extract_release` | 否 | 下载并验证 release 资产 |
| `publish-assets` | `publish_assets` | 是 | 发布资产到 PyPI/npm |
| `publish-release` | `publish_release` | 是 | 发布 GitHub release |
| `ensure-sha` | `ensure_sha` | 是 | 确保分支 SHA 未变 |
| `forwardport-changelog` | `forwardport_changelog` | 是 | 前向移植 changelog |
| `publish-changelog` | `publish_changelog` | 是 | 移除 changelog 占位符 |

## 公共选项列表

| 选项列表名 | 包含选项 | 对应环境变量 |
|-----------|---------|------------|
| `version_spec_options` | `--version-spec` | `RH_VERSION_SPEC` |
| `post_version_spec_options` | `--post-version-spec`, `--post-version-message` | `RH_POST_VERSION_SPEC`, `RH_POST_VERSION_MESSAGE` |
| `version_cmd_options` | `--version-cmd` | `RH_VERSION_COMMAND` |
| `repo_options` | `--repo` | `RH_REPOSITORY` |
| `branch_options` | `--ref`, `--branch`, `--repo` | `RH_REF`, `RH_BRANCH`, `RH_REPOSITORY` |
| `auth_options` | `--auth` | `GITHUB_ACCESS_TOKEN` |
| `username_options` | `--username` | `GITHUB_ACTOR` |
| `dist_dir_options` | `--dist-dir`（默认"dist"） | `RH_DIST_DIR` |
| `python_packages_options` | `--python-packages`（默认["."]） | `RH_PYTHON_PACKAGES` |
| `dry_run_options` | `--dry-run`（flag） | `RH_DRY_RUN` |
| `release_url_options` | `--release-url` | `RH_RELEASE_URL` |
| `changelog_path_options` | `--changelog-path`（默认"CHANGELOG.md"） | `RH_CHANGELOG` |
| `silent_option` | `--silent` | `RH_SILENT` |
| `since_options` | `--since`, `--since-last-stable` | `RH_SINCE`, `RH_SINCE_LAST_STABLE` |
| `tag_format_options` | `--tag-format`（默认"v{version}"） | `RH_TAG_FORMAT` |

## 相关概念

- [架构总览](../concepts/02-architecture-overview.md)
- [CLI命令详解](../concepts/03-cli-commands.md)
- [配置与Hooks系统](../concepts/04-config-and-hooks.md)
