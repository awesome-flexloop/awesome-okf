---
type: Reference
title: "util.py 源码信源"
description: "jupyter_releaser 工具函数层：子进程执行、配置读取、GitHub API封装、版本管理、Mock服务等基础设施"
tags: [utilities, subprocess, github-api, config, version, mock]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-grep", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: util-source
    resource: /references/util-source.md
    title: "util.py Source Code Reference"
---

# util.py 源码信源

## 文件位置

`jupyter_releaser/util.py`（约 753 行）

## 模块职责

工具函数层，提供整个 jupyter_releaser 的基础设施：子进程执行、路径常量、版本管理、配置读取、GitHub API 操作、Mock 服务管理等。

## 路径常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `PYPROJECT` | `Path("pyproject.toml")` | Python 项目配置文件 |
| `SETUP_PY` | `Path("setup.py")` | 旧式 Python 构建文件 |
| `SETUP_CFG` | `Path("setup.cfg")` | setuptools 配置文件 |
| `PACKAGE_JSON` | `Path("package.json")` | npm 包配置文件 |
| `MANIFEST` | `Path("MANIFEST.in")` | Python 分发包清单 |
| `JUPYTER_RELEASER_CONFIG` | `Path(".jupyter-releaser.toml")` | jupyter-releaser 专属配置文件 |
| `METADATA_JSON` | `Path("metadata.json")` | Release 元数据文件名 |
| `CHECKOUT_NAME` | `".jupyter_releaser_checkout"` | Git checkout 工作目录名 |
| `TBUMP_CMD` | `"pipx run tbump --non-interactive --only-patch"` | tbump 版本提升命令 |
| `GIT_FETCH_CMD` | `"git fetch origin --filter=blob:none --quiet"` | Git fetch 命令（partial clone） |

## 核心函数

### 子进程执行

| 函数 | 说明 |
|------|------|
| `run(cmd, **kwargs)` | 执行子进程，Windows 使用 `_run_win`，Unix 使用 `tee.run`；支持 `echo`/`quiet`/`show_cwd`/`quiet_error` 参数 |
| `_run_win(cmd, **kwargs)` | Windows 平台子进程执行，使用 `subprocess.check_output` |
| `log(*outputs, **kwargs)` | 输出日志到 stderr |

### Git 操作

| 函数 | 说明 |
|------|------|
| `get_branch()` | 获取当前 git 分支名 |
| `get_default_branch()` | 获取远程默认分支名 |
| `get_repo()` | 从 remote URL 解析 owner/repo |
| `normalize_path(path)` | 将路径分隔符统一为 `/` |
| `get_remote_name(dry_run)` | 获取 remote 名（dry-run 时用本地 bare 仓库） |

### 版本管理

| 函数 | 说明 |
|------|------|
| `get_version()` | 多策略获取版本：pyproject.toml 静态版 > hatch version > setup.py --version > build wheel > package.json |
| `bump_version(version_spec, *, changelog_path, version_cmd)` | 自动检测版本工具（tbump/hatch/bump2version/npm version），支持 next/patch/minor/dev 便捷指定符 |
| `is_prerelease(version)` | 正则判断是否为预发布版本 |
| `compute_sha256(path)` | 计算文件 SHA256 哈希 |
| `create_release_commit(version, release_message, dist_dir)` | 创建包含 dist 文件 SHA256 的 release commit |

### GitHub API 操作

| 函数 | 说明 |
|------|------|
| `get_gh_object(dry_run, **kwargs)` | 获取 GhApi 对象，dry-run 时连接 Mock 服务器 |
| `release_for_url(gh, url)` | 根据 URL 查找 release 对象 |
| `latest_draft_release(gh, branch)` | 查找最新的 draft release |
| `parse_release_url(release_url)` | 正则解析 GitHub release URL，提取 owner/repo/tag |
| `upload_assets(gh, assets, release, auth)` | 上传资产到 release，同时生成 asset_shas.json |
| `fetch_release_asset(target_dir, asset, auth)` | 流式下载 release 资产 |
| `fetch_release_asset_data(asset, auth)` | 下载资产数据并解析为 JSON |
| `extract_metadata_from_release_url(gh, release_url, auth)` | 从 metadata.json 提取元数据并设置 RH_* 环境变量 |
| `actions_output(name, value)` | 设置 GitHub Actions output（写入 GITHUB_OUTPUT 文件） |

### 配置与环境

| 函数 | 说明 |
|------|------|
| `read_config()` | 三源读取配置（.jupyter-releaser.toml > pyproject.toml > package.json），JSON Schema 校验 |
| `prepare_environment(fetch_draft_release)` | 准备环境变量、检查管理员权限、dry-run 时启动 Mock、获取最新 draft release |
| `handle_since()` | 捕获/设置 RH_SINCE 环境变量 |
| `ensure_sha(dry_run, expected_sha, branch)` | 验证远程分支 SHA 一致性 |
| `retry(cmd, **kwargs)` | 最多重试3次，指数退避 |

### Mock 服务

| 函数 | 说明 |
|------|------|
| `get_mock_github_url()` | 返回 Mock GitHub URL（http://127.0.0.1:8000） |
| `ensure_mock_github()` | 启动/确认 Mock GitHub 服务器（uvicorn + FastAPI） |

### Changelog 辅助

| 函数 | 说明 |
|------|------|
| `get_latest_tag(source, since_last_stable)` | 获取最近的 tag |
| `get_first_commit(source)` | 获取初始 commit SHA |

## 正则表达式

| 常量 | 用途 |
|------|------|
| `RELEASE_HTML_PATTERN` | 匹配 `https://github.com/owner/repo/releases/tag/tag` 格式 URL |
| `RELEASE_API_PATTERN` | 匹配 `https://api.github.com/repos/owner/repo/releases/tags/tag` 格式 URL |

## 相关概念

- [CLI命令详解](/concepts/03-cli-commands.md)
- [配置与Hooks系统](/concepts/04-config-and-hooks.md)
- [Dry-Run与Mock机制](/concepts/08-dry-run-and-mock.md)
- [认证体系](/concepts/10-authentication.md)
