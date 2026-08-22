---
type: Reference
title: "actions 目录源码信源"
description: "jupyter_releaser 的 GitHub Actions action 模块：prep_release、populate_release、finalize_release 等编排脚本"
tags: [actions, github-actions, orchestration, workflow]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-grep", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: actions-source
    resource: /references/actions-source.md
    title: "actions/ Source Code Reference"
---

# actions 目录源码信源

## 目录位置

`jupyter_releaser/actions/`（5个 Python 文件 + common.py）

## common.py — Action 公共工具

| 成员 | 类型 | 说明 |
|------|------|------|
| `make_group(name)` | 上下文管理器 | 输出 GitHub Actions 日志分组标记 `::group::{name}` / `::endgroup::` |
| `setup(fetch_draft_release=True)` | 函数 | 调用 `util.prepare_environment()` 准备环境变量和 GitHub 连接 |
| `run_action(target, *args, **kwargs)` | 函数 | 在日志组中执行命令（调用 `util.run`） |

## prep_release.py — 阶段一：准备发布

执行顺序：
1. `setup(False)` — 准备环境（不自动获取 draft release）
2. `jupyter-releaser prep-git` — 准备 git 仓库
3. 若 RH_BRANCH 未设置，获取默认分支
4. `handle_since()` — 捕获 since 变量（在 bump-version 之前）
5. `jupyter-releaser bump-version` — 提升版本号
6. `jupyter-releaser build-changelog` — 构建 changelog entry
7. `jupyter-releaser draft-changelog` — 创建 draft GitHub release

**输出**：`release_url`（draft release 的 URL）

## populate_release.py — 阶段二：填充发布资产

执行顺序：
1. `setup()` — 准备环境（自动获取 draft release）
2. 检查是否已有 `asset_shas.json` 资产，有则跳过
3. `jupyter-releaser prep-git` — 准备 git 仓库
4. `jupyter-releaser ensure-sha` — 确保 SHA 未变
5. `jupyter-releaser bump-version` — 再次确认版本
6. `jupyter-releaser extract-changelog` — 从 draft release 提取 changelog
7. `jupyter-releaser build-npm` — 构建 npm 包（先于 Python！）
8. `jupyter-releaser check-npm` — 检查 npm 包
9. `jupyter-releaser build-python` — 构建 Python 包
10. `jupyter-releaser check-python` — 检查 Python 包
11. `jupyter-releaser tag-release` — 创建 release commit 和 tag
12. `jupyter-releaser ensure-sha` — 再次确保 SHA 未变
13. `jupyter-releaser populate-release` — 推送 commit/tag 并上传资产

**输出**：`release_url`（填充后的 release URL）

## finalize_release.py — 阶段三：完成发布

执行顺序：
1. `setup()` — 准备环境
2. 如果有 `release_url`：`jupyter-releaser extract-release` — 下载并验证资产
3. `jupyter-releaser publish-assets` — 发布资产到 PyPI/npm
4. 如果有 `release_url`：
   - `jupyter-releaser forwardport-changelog` — 前向移植 changelog 到默认分支
   - `jupyter-releaser publish-release` — 发布 GitHub release（从 draft 转为 published）

**输出**：`release_url`、`release_tag`、`pr_url`（forwardport PR URL）

## generate_changelog.py — 独立 Changelog 生成

- 调用 `handle_since()` 获取 since 值
- 执行 `prep-git`
- 调用 `changelog.get_version_entry()` 生成 changelog entry
- 可选转换为 RST 格式（通过 pypandoc）
- 输出到 `CHANGELOG_ENTRY.md`

## publish_changelog.py — 移除 Changelog 占位符

- `setup(False)` — 准备环境
- `prep-git`
- 获取默认分支
- `jupyter-releaser publish-changelog` — 移除 silent 占位符，为已发布 release 填充实际 changelog

## GitHub Composite Actions（.github/actions/）

| Action | 对应 Python 模块 | 用途 |
|--------|----------------|------|
| `prep-release` | `actions.prep_release` | 阶段一：创建 draft release |
| `populate-release` | `actions.populate_release` | 阶段二：构建并上传资产 |
| `finalize-release` | `actions.finalize_release` | 阶段三：发布资产和 release |
| `check-release` | 串联三个模块 | Dry-run 完整流程检查 |
| `publish-changelog` | `actions.publish_changelog` | 移除 changelog 占位符 |
| `install-releaser` | （shell 脚本） | 安装 jupyter-releaser |

## 关键设计要点

- npm 构建必须在 Python 构建之前，因为 npm 可能产出 Python 包需要的文件
- populate_release 中两次 ensure-sha 防止并发修改
- extract-release 在 publish-assets 之前下载资产以验证 SHA256
- forwardport-changelog 在 publish-release 之后执行，将 changelog 同步回默认分支

## 相关概念

- [发布流水线详解](/concepts/05-release-pipeline.md)
- [GitHub Actions集成](/concepts/09-github-actions.md)
- [架构总览](/concepts/02-architecture-overview.md)
