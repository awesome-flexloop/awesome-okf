---
type: Reference
title: "lib.py 源码信源"
description: "jupyter_releaser 核心库：发布流程各阶段的主要逻辑函数，包括版本提升、changelog 草稿、资产上传、发布等"
tags: [library, core, release, publish]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-grep", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: lib-source
    resource: /references/lib-source.md
    title: "lib.py Source Code Reference"
---

# lib.py 源码信源

## 文件位置

`jupyter_releaser/lib.py`（约 678 行）

## 模块职责

核心库层，包含发布流程各阶段的主要业务逻辑函数。CLI 命令和 action 模块都委托给此模块的函数执行实际操作。

## 函数清单

| 函数 | 签名摘要 | 功能说明 |
|------|---------|---------|
| `bump_version` | `(version_spec, version_cmd, changelog_path, tag_format, package_name=None)` | 调用 `util.bump_version()` 提升版本，验证版本号有效性，检查 tag 是否已存在 |
| `draft_changelog` | `(version_spec, ref, branch, repo, since, since_last_stable, auth, changelog_path, dry_run, post_version_spec, post_version_message, silent, tag_format)` | 创建 draft GitHub release，上传 metadata.json，清理超过1天的非 silent draft |
| `make_changelog_pr` | `(auth, branch, repo, title, commit_message, body, dry_run=False)` | 创建 UUID 后缀分支，提交变更，推送并创建带 "documentation" 标签的 PR |
| `publish_changelog` | `(branch, repo, auth, changelog_path, dry_run)` | 移除 changelog 占位符条目，如有变更则创建 forward-port PR |
| `tag_release` | `(dist_dir, release_message, tag_format, tag_message, no_git_tag_workspace)` | 创建 release commit（含SHA256 hashes），创建 annotated tag，可选标记 npm workspace packages |
| `populate_release` | `(ref, branch, repo, version_cmd, auth, changelog_path, dist_dir, dry_run, release_url, post_version_spec, post_version_message, assets, tag_format, silent=False)` | Bump post version → push commits/tags → 更新 release body → 上传资产 |
| `delete_release` | `(auth, release_url, dry_run=False)` | 删除 draft release 及其所有 assets |
| `extract_release` | `(auth, dist_dir, dry_run, release_url)` | 从 draft release 下载资产，验证 SHA256 校验和 |
| `publish_assets` | `(auth, dist_dir, npm_token, npm_cmd, twine_cmd, npm_registry, twine_repository_url, npm_tag, dry_run, release_url, python_package)` | 发布 .tgz 到 npm、.whl/.gz 到 PyPI；dry-run 时启动本地 PyPI；prerelease 自动设 npm tag 为 next；支持 OIDC trusted publishing |
| `publish_release` | `(auth, dry_run, release_url, silent)` | 将 GitHub release 从 draft 发布（silent 模式保持 draft） |
| `prep_git` | `(ref, branch, repo, auth, username, url)` | 初始化/复用 checkout 目录，配置 remote，fetch tags，checkout 分支，配置 git user |
| `extract_changelog` | `(dry_run, auth, changelog_path, release_url, silent=False)` | 从 GitHub release body 提取 changelog，mdformat 格式化后更新本地文件 |
| `forwardport_changelog` | `(auth, ref, branch, repo, username, changelog_path, dry_run, release_url)` | 将 release tag 上的 changelog entry 前向移植到默认分支并创建 PR |

## 关键数据流

### prep_git → bump_version → build_changelog → draft_changelog 流程

1. `prep_git()` 在 `.jupyter_releaser_checkout/` 中 clone/fetch 目标仓库
2. `bump_version()` 调用 `util.bump_version()` 执行版本号提升
3. `build_changelog()` 调用 `changelog.build_entry()` 生成 changelog entry
4. `draft_changelog()` 在 GitHub 上创建 draft release，附带 metadata.json

### populate_release 流程

1. 可选 bump post version（dev 版本）
2. push commits 和 tags 到 remote
3. 更新 release body 为 changelog 内容
4. 上传 dist 文件和 asset_shas.json

### publish_assets 发布逻辑

- `.whl`/`.gz` 文件：通过 twine 上传到 PyPI，支持三种 token 获取方式（OIDC/PYPI_TOKEN/PYPI_TOKEN_MAP）
- `.tgz` 文件：通过 npm publish 发布，E409/EPUBLISHCONFLICT 错误静默忽略（已发布版本）
- dry-run：启动本地 pypiserver:8081，npm 使用 --dry-run

## 关键常量与依赖

- 使用 `mdformat.text()` 格式化 markdown
- 使用 `packaging.utils.canonicalize_name` 规范化 Python 包名
- 使用 `packaging.version.parse_version` 解析版本号
- 使用 `pkginfo.SDist`/`pkginfo.Wheel` 读取分发包元数据

## 相关概念

- [发布流水线详解](../concepts/05-release-pipeline.md)
- [Python与npm双生态发布](../concepts/06-python-npm-dual.md)
- [Changelog系统](../concepts/07-changelog-system.md)
