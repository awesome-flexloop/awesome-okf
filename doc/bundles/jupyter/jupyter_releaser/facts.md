---
sources:
- ../../../../../external/libs/jupyter/jupyter_releaser/pyproject.toml
- ../../../../../external/libs/jupyter/jupyter_releaser/README.md
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/__init__.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/__main__.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/actions/__init__.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/actions/common.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/actions/finalize_release.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/actions/generate_changelog.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/actions/populate_release.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/actions/prep_release.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/actions/publish_changelog.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/changelog.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/cli.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/lib.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/mock_github.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/npm.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/python.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/schema.json
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/tee.py
- ../../../../../external/libs/jupyter/jupyter_releaser/jupyter_releaser/util.py
type: Facts
okf_version: '0.2'
title: jupyter_releaser 源码事实清单
generated: '2026-08-22'
tags:
- facts
---

# jupyter_releaser 事实清单（R阶段）

> 本文件记录从源码中提取的可验证事实，编号 F-001 起。所有事实均指向具体源码路径，禁止推测。

## 项目基本信息

- F-001: `__version__ = "1.12.0.dev0"` 定义于 `jupyter_releaser/__init__.py` 第3行
- F-002: 构建系统使用 `hatchling>=1.11`，`build-backend = "hatchling.build"`，定义于 `pyproject.toml` 第2-3行
- F-003: 项目描述为 `"Jupyter Releaser for Python and/or npm packages."`，定义于 `pyproject.toml` 第7行
- F-004: Python 版本要求 `>=3.10`，支持 Python 3.10/3.11/3.12/3.13，定义于 `pyproject.toml` 第17-23行
- F-005: CLI 入口点 `jupyter-releaser = "jupyter_releaser.cli:main"`，定义于 `pyproject.toml` 第70行
- F-006: 核心依赖包括 click<8.2.0、fastcore<2、ghapi<=1.0.4、github-activity>=1.1.1<2、importlib_resources、jsonschema>=4.0.0、mdformat、packaging、pkginfo、pypiserver、pipx、requests、requests_cache、toml~=0.10，定义于 `pyproject.toml` 第25-41行

## CLI 层（cli.py）

- F-007: `ReleaseHelperGroup(click.Group)` 类定义于 `jupyter_releaser/cli.py` 第15行，继承自 `click.Group`
- F-008: `ReleaseHelperGroup._needs_checkout_dir` 是类变量，类型为 `t.Dict[str, bool]`，初始值为空字典，定义于 `cli.py` 第18行
- F-009: `ReleaseHelperGroup.invoke(self, ctx)` 方法重写了 click.Group 的 invoke，实现于 `cli.py` 第20-141行
- F-010: `invoke` 方法处理 `list-envvars` 特殊命令（第27-37行），遍历所有命令参数收集有 envvar 的 Option
- F-011: `invoke` 方法中，若命令名在 `_needs_checkout_dir` 中，检查 `util.CHECKOUT_NAME` 目录是否存在，不存在则抛出 ValueError（第41-45行）
- F-012: `invoke` 方法调用 `util.read_config()` 读取配置，获取 hooks、options、skip 三个键（第48-51行）
- F-013: `invoke` 方法支持 `--force` 参数清空 skip 列表（第53-55行）
- F-014: `invoke` 方法从环境变量 `RH_STEPS_TO_SKIP` 读取额外跳过步骤（第57行）
- F-015: `invoke` 方法处理三层参数优先级：env var > cli arg > options config > default（第70-105行）
- F-016: `invoke` 方法在命令执行前运行 `before-{cmd_name}` hooks，执行后运行 `after-{cmd_name}` hooks（第110-139行）
- F-017: hooks 中的命令字符串通过 `util.run(hook)` 执行（第118行、第139行）
- F-018: `invoke` 方法在 `prep-git` 和 `extract-release` 命令后重新读取配置并切换到 CHECKOUT_NAME 目录（第126-129行）
- F-019: `ReleaseHelperGroup.list_commands(self, ctx)` 返回 `self.commands.keys()` 保持插入顺序，定义于 `cli.py` 第143-145行
- F-020: `main` 是 click group，使用 `cls=ReleaseHelperGroup`，带有 `--force` 选项，定义于 `cli.py` 第148-151行
- F-021: `add_options(options)` 是装饰器工厂函数，用于批量添加 click option，定义于 `cli.py` 第332-341行
- F-022: `use_checkout_dir()` 是装饰器工厂，将被装饰函数名注册到 `ReleaseHelperGroup._needs_checkout_dir`，定义于 `cli.py` 第344-351行
- F-023: CLI 定义了以下公共选项列表：`version_spec_options`、`post_version_spec_options`、`version_cmd_options`、`repo_options`、`branch_options`、`auth_options`、`username_options`、`dist_dir_options`、`python_packages_options`、`check_imports_options`、`dry_run_options`、`git_url_options`、`release_url_options`、`changelog_path_options`、`silent_option`、`since_options`、`changelog_options`、`npm_install_options`、`pydist_check_options`、`tag_format_options`，定义于 `cli.py` 第155-329行
- F-024: CLI 注册的命令有：`list_envvars`、`prep_git`、`bump_version`、`extract_changelog`、`build_changelog`、`draft_changelog`、`build_python`、`check_python`、`build_npm`、`check_npm`、`tag_release`、`populate_release`、`delete_release`、`extract_release`、`publish_assets`、`publish_release`、`ensure_sha`、`forwardport_changelog`、`publish_changelog`，定义于 `cli.py` 第354-746行

## 工具层（util.py）

- F-025: `util.py` 定义了路径常量：`PYPROJECT = Path("pyproject.toml")`、`SETUP_PY = Path("setup.py")`、`SETUP_CFG = Path("setup.cfg")`、`PACKAGE_JSON = Path("package.json")`、`MANIFEST = Path("MANIFEST.in")`、`YARN_LOCK = Path("yarn.lock")`、`JUPYTER_RELEASER_CONFIG = Path(".jupyter-releaser.toml")`、`METADATA_JSON = Path("metadata.json")`，定义于 `util.py` 第35-42行
- F-026: `CHECKOUT_NAME = ".jupyter_releaser_checkout"`，定义于 `util.py` 第47行
- F-027: `TBUMP_CMD = "pipx run tbump --non-interactive --only-patch"`，定义于 `util.py` 第45行
- F-028: `RELEASE_HTML_PATTERN` 和 `RELEASE_API_PATTERN` 是两个正则表达式，用于匹配 GitHub release URL，定义于 `util.py` 第48-53行
- F-029: `SCHEMA` 从 `jupyter_releaser/schema.json` 加载并 JSON 解析，定义于 `util.py` 第55-56行
- F-030: `GIT_FETCH_CMD = "git fetch origin --filter=blob:none --quiet"`，定义于 `util.py` 第58行
- F-031: `run(cmd, **kwargs)` 函数执行子进程命令，在 Windows 上调用 `_run_win`，否则使用 `tee.run`，定义于 `util.py` 第64-94行
- F-032: `_run_win(cmd, **kwargs)` 使用 `subprocess.check_output` 在 Windows 上执行命令，定义于 `util.py` 第97-128行
- F-033: `log(*outputs, **kwargs)` 输出到 stderr，定义于 `util.py` 第131-134行
- F-034: `get_branch()` 执行 `git branch --show-current`，定义于 `util.py` 第137-139行
- F-035: `get_default_branch()` 解析 `git remote show origin` 输出获取 HEAD branch，定义于 `util.py` 第142-148行
- F-036: `get_repo()` 从 `git remote get-url origin` 解析 owner/repo，定义于 `util.py` 第151-159行
- F-037: `get_version()` 版本获取优先级：pyproject.toml 静态 version > hatchling dynamic version（hatch version）> setup.py --version > build wheel 提取 > package.json version，定义于 `util.py` 第162-199行
- F-038: `normalize_path(path)` 将路径分隔符替换为 `/`，定义于 `util.py` 第202-204行
- F-039: `compute_sha256(path)` 以 64KB 缓冲区计算文件 SHA256，定义于 `util.py` 第207-218行
- F-040: `create_release_commit(version, release_message, dist_dir)` 创建包含 SHA256 hashes 的 release commit，定义于 `util.py` 第221-242行
- F-041: `bump_version(version_spec, *, changelog_path, version_cmd)` 函数自动检测版本工具（tbump/hatch/bump2version/npm version），计算版本号并执行 bump，定义于 `util.py` 第251-353行
- F-042: `bump_version` 支持便捷版本指定符：`next`、`patch`、`minor`、`dev`，定义于 `util.py` 第280-348行
- F-043: `is_prerelease(version)` 通过正则匹配判断版本号是否为预发布版本，定义于 `util.py` 第356-361行
- F-044: `release_for_url(gh, url)` 遍历 gh.repos.list_releases() 查找匹配 html_url 或 url 的 release，定义于 `util.py` 第364-373行
- F-045: `latest_draft_release(gh, branch)` 查找最新的 draft release，定义于 `util.py` 第376-398行
- F-046: `actions_output(name, value)` 写入 GITHUB_OUTPUT 环境变量指向的文件，定义于 `util.py` 第401-406行
- F-047: `get_latest_tag(source, since_last_stable)` 获取最近的 tag，`since_last_stable=True` 时只匹配稳定版本号（\d+\.\d+\.\d+$），定义于 `util.py` 第409-425行
- F-048: `get_first_commit(source)` 执行 `git rev-list --max-parents=0 HEAD` 获取初始 commit，定义于 `util.py` 第428-431行
- F-049: `retry(cmd, **kwargs)` 最多重试3次，每次重试前 sleep(attempt) 秒，定义于 `util.py` 第434-445行
- F-050: `read_config()` 从三个位置读取配置（优先级递减）：`.jupyter-releaser.toml` > `pyproject.toml` 的 `[tool.jupyter-releaser]` > `package.json` 的 `"jupyter-releaser"` 键，使用 JSON Schema 验证，定义于 `util.py` 第448-478行
- F-051: `parse_release_url(release_url)` 使用正则解析 release URL，返回 match 对象，包含 owner、repo、tag 命名组，定义于 `util.py` 第481-489行
- F-052: `fetch_release_asset(target_dir, asset, auth)` 使用 requests 流式下载 release asset 到目标目录，定义于 `util.py` 第492-503行
- F-053: `fetch_release_asset_data(asset, auth)` 下载 asset 数据并解析为 JSON，定义于 `util.py` 第506-518行
- F-054: `upload_assets(gh, assets, release, auth)` 上传资产到 release，同时生成 asset_shas.json，定义于 `util.py` 第521-536行
- F-055: `extract_metadata_from_release_url(gh, release_url, auth)` 从 release 的 metadata.json asset 中提取数据，并设置 RH_* 环境变量，定义于 `util.py` 第539-561行
- F-056: `prepare_environment(fetch_draft_release=True)` 设置环境变量（RH_REPOSITORY、RH_REF、RH_BRANCH）、检查管理员权限、dry-run 时启动 mock GitHub、获取最新 draft release 并提取 metadata，定义于 `util.py` 第564-635行
- F-057: `handle_since()` 捕获 RH_SINCE 环境变量，若无则从最新 tag 获取并设置环境变量，定义于 `util.py` 第638-656行
- F-058: `ensure_sha(dry_run, expected_sha, branch)` 验证远程分支 SHA 是否与 expected_sha 一致，定义于 `util.py` 第659-671行
- F-059: `get_gh_object(dry_run, **kwargs)` dry-run 时调用 `ensure_mock_github()`，返回 `ghapi.core.GhApi(**kwargs)`，定义于 `util.py` 第674-679行
- F-060: `get_remote_name(dry_run)` 非 dry-run 返回 "origin"；dry-run 时创建本地 bare git 仓库作为 test remote，定义于 `util.py` 第685-703行
- F-061: `get_mock_github_url()` 返回 `http://127.0.0.1:{MOCK_GITHUB_PORT}`，默认端口 8000，定义于 `util.py` 第706-709行
- F-062: `ensure_mock_github()` 设置 `core.GH_HOST` 为 mock URL，启动 uvicorn 运行 `jupyter_releaser.mock_github:app`，注册 atexit kill，等待服务就绪，定义于 `util.py` 第712-752行

## 核心库层（lib.py）

- F-063: `bump_version(version_spec, version_cmd, changelog_path, tag_format, package_name)` 委托 `util.bump_version()` 执行版本提升，验证版本有效性，检查 tag 是否已存在，定义于 `lib.py` 第26-48行
- F-064: `draft_changelog(...)` 创建 draft GitHub release，上传 metadata.json 作为 asset，清理超过1天的非 silent draft release，输出 release_url，定义于 `lib.py` 第51-143行
- F-065: `make_changelog_pr(auth, branch, repo, title, commit_message, body, dry_run)` 创建带 UUID 后缀的分支，提交变更，推送并创建 PR，添加 "documentation" 标签，定义于 `lib.py` 第145-198行
- F-066: `publish_changelog(branch, repo, auth, changelog_path, dry_run)` 调用 `changelog.remove_placeholder_entries()` 移除占位符，如有变更则调用 `make_changelog_pr()` 创建 forward-port PR，定义于 `lib.py` 第201-214行
- F-067: `tag_release(dist_dir, release_message, tag_format, tag_message, no_git_tag_workspace)` 创建 release commit、annotated tag，可选地为 npm workspace packages 创建 tag，定义于 `lib.py` 第217-232行
- F-068: `populate_release(...)` 执行：bump post version → push commits/tags → 更新 release body → 上传资产，定义于 `lib.py` 第235-296行
- F-069: `delete_release(auth, release_url, dry_run)` 删除 draft release 及其所有 assets，定义于 `lib.py` 第299-313行
- F-070: `extract_release(auth, dist_dir, dry_run, release_url)` 从 draft release 下载资产、验证 SHA256 校验和，定义于 `lib.py` 第316-358行
- F-071: `publish_assets(...)` 发布 npm 包（.tgz）和 Python 包（.whl/.gz）到各自 registry；dry-run 时启动本地 PyPI 服务器；支持 prerelease 自动设置 npm tag 为 "next"；支持 PyPI OIDC trusted publishing，定义于 `lib.py` 第361-474行
- F-072: `publish_release(auth, dry_run, release_url, silent)` 将 GitHub release 从 draft 状态发布（silent 模式保持 draft），定义于 `lib.py` 第477-499行
- F-073: `prep_git(ref, branch, repo, auth, username, url)` 初始化/复用 checkout 目录、配置 remote、fetch tags、checkout 目标分支、配置 git user（默认 GitHub Actions bot），定义于 `lib.py` 第502-586行
- F-074: `extract_changelog(dry_run, auth, changelog_path, release_url, silent)` 从 GitHub release body 提取 changelog 文本，用 mdformat 格式化后更新本地 changelog 文件，定义于 `lib.py` 第589-600行
- F-075: `forwardport_changelog(...)` 将 release tag 上的 changelog entry 前向移植到默认分支，创建 forward-port PR，定义于 `lib.py` 第603-678行

## Changelog 模块（changelog.py）

- F-076: 定义了四个 HTML 注释标记常量：`START_MARKER`、`END_MARKER`、`START_SILENT_MARKER`、`END_SILENT_MARKER`，定义于 `changelog.py` 第14-17行
- F-077: `PR_PREFIX = "Automated Changelog Entry"`、`PRECOMMIT_PREFIX = "[pre-commit.ci] pre-commit autoupdate"`，定义于 `changelog.py` 第18-19行
- F-078: `DEFAULT_IGNORED_CONTRIBUTORS` 列表包含 `dependabot*`、`pre-commit-ci*`、`github-actions*`、`meeseeksmachine*`、`*[[]bot]`，定义于 `changelog.py` 第24-33行
- F-079: `format_pr_entry(target, number, auth, dry_run)` 获取 PR 信息并格式化为 `- {title} [#{number}]({url}) (@{user_name}]({user_url}))` 格式，定义于 `changelog.py` 第36-62行
- F-080: `get_version_entry(ref, branch, repo, version, *, since, since_last_stable, until, auth, resolve_backports, dry_run, ignored_contributors)` 调用 `github_activity.generate_activity_md()` 生成 PR 活动日志，处理 backport PR 替换为原始 PR，过滤自动生成的 changelog PR 和 pre-commit PR，定义于 `changelog.py` 第65-179行
- F-081: `build_entry(ref, branch, repo, auth, changelog_path, since, since_last_stable, resolve_backports)` 获取当前版本，调用 `get_version_entry()` 生成 entry，调用 `update_changelog()` 写入文件，定义于 `changelog.py` 第182-203行
- F-082: `update_changelog(changelog_path, entry, silent)` 在 START_MARKER/END_MARKER 之间插入 entry，验证标记唯一，定义于 `changelog.py` 第206-223行
- F-083: `remove_placeholder_entries(repo, auth, changelog_path, dry_run)` 查找所有 SILENT 标记区间，对已发布的 release 用 release body 替换占位符，返回替换数量，定义于 `changelog.py` 第226-290行
- F-084: `insert_entry(changelog, entry, version, silent)` 将 entry 插入到 changelog 的标记位置；silent 模式插入 SILENT 标记占位；保留已有 PR 条目的格式化，定义于 `changelog.py` 第293-322行
- F-085: `format(changelog)` 清理多余空行，定义于 `changelog.py` 第325-328行
- F-086: `check_entry(...)` 验证 changelog entry 包含所有应有的 PR 编号且不含多余 PR，定义于 `changelog.py` 第331-403行
- F-087: `splice_github_entry(orig_entry, github_entry)` 将 GitHub 自动生成的 release note PR 标题覆盖到原始 entry 中，定义于 `changelog.py` 第406-437行
- F-088: `extract_current(changelog_path)` 提取 START_MARKER 和 END_MARKER 之间的当前 changelog entry，定义于 `changelog.py` 第440-450行
- F-089: `extract_current_version(changelog_path)` 从当前 entry 中提取版本号，定义于 `changelog.py` 第453-456行
- F-090: `_extract_version(entry)` 通过正则 `#+ (\d\S+)` 从 entry 文本中提取版本号，定义于 `changelog.py` 第459-465行

## Python 发布模块（python.py）

- F-091: `build_dist(dist_dir, clean=True)` 使用 `pipx run --spec build pyproject-build --outdir {dest} .` 构建 Python 分发包，定义于 `python.py` 第27-36行
- F-092: `check_dist(dist_file, test_cmd, python_imports, check_cmd, extra_check_cmds, resource_paths)` 在临时 venv 中安装 dist 文件，执行 twine check、validate-pyproject、check-wheel-contents、import 测试和资源路径验证，定义于 `python.py` 第39-102行
- F-093: `fetch_pypi_api_token()` 通过 GitHub OIDC token 交换 PyPI API token（Trusted Publishing），定义于 `python.py` 第105-146行
- F-094: `get_pypi_token(release_url, python_package)` 获取 PyPI token，优先级：OIDC trusted publishing > PYPI_TOKEN 环境变量 > PYPI_TOKEN_MAP 映射，定义于 `python.py` 第149-181行
- F-095: `start_local_pypi()` 启动本地 pypiserver 在 8081 端口用于 dry-run 测试，定义于 `python.py` 第184-197行

## NPM 发布模块（npm.py）

- F-096: `build_dist(package, dist_dir)` 执行 `npm pack` 构建 tarball，处理 public/private 包，支持 npm workspaces，定义于 `npm.py` 第25-62行
- F-097: `extract_dist(dist_dir, target, repo)` 从 tarball 中提取包内容到目标目录，验证 repository URL 匹配，定义于 `npm.py` 第65-116行
- F-098: `check_dist(dist_dir, install_options, repo)` 在临时目录中 `npm init -y` 后 `npm install` 提取的包进行验证，定义于 `npm.py` 第119-132行
- F-099: `extract_package(path)` 从 tarball 的 package/package.json 中提取并解析 JSON 元数据，定义于 `npm.py` 第135-144行
- F-100: `handle_npm_config(npm_token)` 写入 ~/.npmrc 配置：registry、_authToken、provenance（id-token 权限时），定义于 `npm.py` 第147-178行
- F-101: `get_package_versions(version)` 对比 Python 版本与 npm 版本，列出 workspace 包版本，定义于 `npm.py` 第181-195行
- F-102: `tag_workspace_packages()` 为 npm workspace 中的公开包创建 git tag（格式 `name@version`），定义于 `npm.py` 第198-221行
- F-103: `_get_workspace_packages(data)` 解析 package.json 的 workspaces 字段（支持数组和对象格式），glob 匹配并返回包含 package.json 的子目录路径，定义于 `npm.py` 第224-244行

## TEE 模块（tee.py）

- F-104: `tee.py` 是 subprocess-tee 的修改版本，提供类 tee 的子进程输出捕获，定义于 `tee.py` 第1-22行
- F-105: `STREAM_LIMIT = 2**23`（8MB），定义于 `tee.py` 第43行
- F-106: `_read_stream(stream, callback)` 异步逐行读取流并调用 callback，定义于 `tee.py` 第46-52行
- F-107: `_stream_subprocess(args, **kwargs)` 使用 `asyncio.create_subprocess_shell` 创建子进程，异步读取 stdout/stderr，tee 输出到 stderr 同时收集，定义于 `tee.py` 第55-130行
- F-108: `run(args, **kwargs)` 是对外入口，处理 str/list 参数转换，在事件循环中运行 `_stream_subprocess`，check=True 时抛出 CalledProcessError，定义于 `tee.py` 第133-162行

## Actions 层（actions/）

- F-109: `actions/common.py` 提供 `make_group(name)` 上下文管理器（输出 `::group::`/`::endgroup::` GitHub Actions 日志分组）、`setup(fetch_draft_release)` 调用 `prepare_environment`、`run_action(target, *args, **kwargs)` 在日志组中执行命令，定义于 `actions/common.py` 第8-25行
- F-110: `actions/prep_release.py` 执行流程：setup(False) → prep-git → 获取默认分支 → handle_since → bump-version → build-changelog → draft-changelog，定义于 `actions/prep_release.py` 第9-27行
- F-111: `actions/populate_release.py` 执行流程：setup() → 检查是否已有 asset_shas（跳过则退出）→ prep-git → ensure-sha → bump-version → extract-changelog → build-npm → check-npm → build-python → check-python → tag-release → ensure-sha → populate-release，定义于 `actions/populate_release.py` 第11-43行
- F-112: `actions/finalize_release.py` 执行流程：setup() → extract-release（如果有 release_url）→ publish-assets → forwardport-changelog（如果有 release_url）→ publish-release（如果有 release_url），定义于 `actions/finalize_release.py` 第8-19行
- F-113: `actions/generate_changelog.py` 独立生成 changelog entry 到 CHANGELOG_ENTRY.md 文件，可选转换为 RST，定义于 `actions/generate_changelog.py` 第9-37行
- F-114: `actions/publish_changelog.py` 执行流程：setup(False) → prep-git → 获取默认分支 → publish-changelog，定义于 `actions/publish_changelog.py` 第9-20行

## Mock GitHub（mock_github.py）

- F-115: `mock_github.py` 使用 FastAPI 实现 mock GitHub API，定义于 `mock_github.py` 第16行
- F-116: 定义 Pydantic 模型：`Asset`（id/name/content_type/size/state/url等）、`Release`（assets_url/upload_url/draft/body/id/html_url/tag_name/target_commitish/assets等）、`User`（login/html_url）、`PullRequest`（number/html_url/title/user）、`TagObject`（sha）、`Tag`（ref/object），定义于 `mock_github.py` 第60-128行
- F-117: 实现了以下 API 端点：list_releases、get_release_by_tag、create_a_release、update_a_release、upload_a_release_asset、delete_a_release_asset、delete_a_release、get_a_pull_request、create_a_pull_request、add_labels_to_an_issue、create_tag_ref、list_matching_references，定义于 `mock_github.py` 第136-276行
- F-118: 数据持久化到 RH_GITHUB_STATIC_DIR 目录下的 JSON 文件，定义于 `mock_github.py` 第28-57行

## GitHub Actions 定义（.github/actions/）

- F-119: 提供 5 个 composite actions：check-release、finalize-release、install-releaser、populate-release、prep-release、publish-changelog，位于 `.github/actions/` 目录
- F-120: `install-releaser` action 执行 `.github/scripts/install-releaser.sh` 安装 jupyter-releaser
- F-121: `prep-release` action 设置环境变量后执行 `python -m jupyter_releaser.actions.prep_release`
- F-122: `populate-release` action 设置环境变量后执行 `python -m jupyter_releaser.actions.populate_release`
- F-123: `finalize-release` action 设置环境变量后执行 `python -m jupyter_releaser.actions.finalize_release`
- F-124: `check-release` action 在 dry-run 模式下依次执行 prep_release、populate_release、finalize_release

## 配置 Schema（schema.json）

- F-125: 配置 schema 版本 "0.1.0"，定义三个顶层属性：`skip`（字符串数组）、`options`（对象，值为字符串或字符串数组）、`hooks`（patternProperties 匹配 `^(before|after)-.*$`，值为字符串或字符串数组），定义于 `schema.json`
- F-126: `additionalProperties: false`，即不允许配置中出现 skip/options/hooks 之外的键，定义于 `schema.json` 第47行

## 示例工作流（example-workflows/）

- F-127: `full-release.yml` 展示两阶段发布：prep_release job（手工触发）→ publish_release job（needs prep_release，使用 environment: release，id-token: write 权限），定义于 `example-workflows/full-release.yml`
- F-128: 示例工作流使用 `actions/create-github-app-token` 获取 GitHub App token 用于发布
