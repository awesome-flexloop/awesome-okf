---
type: Facts
okf_version: "0.2"
title: "language-packs 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, language-packs, i18n, localization, crowdin]
sources:
  - ../../../../../external/libs/jupyter/language-packs/README.md
  - ../../../../../external/libs/jupyter/language-packs/crowdin.yml
  - ../../../../../external/libs/jupyter/language-packs/repository-map.yml
  - ../../../../../external/libs/jupyter/language-packs/requirements.txt
  - ../../../../../external/libs/jupyter/language-packs/scripts/01_check_releases.py
  - ../../../../../external/libs/jupyter/language-packs/scripts/02_update_catalogs.py
  - ../../../../../external/libs/jupyter/language-packs/scripts/03_prepare_release.py
  - ../../../../../external/libs/jupyter/language-packs/scripts/04_check_version.py
  - ../../../../../external/libs/jupyter/language-packs/scripts/github_ql.py
  - ../../../../../external/libs/jupyter/language-packs/language-packs/jupyterlab-language-pack-de-DE/pyproject.toml
  - ../../../../../external/libs/jupyter/language-packs/language-packs/jupyterlab-language-pack-ach-UG/pyproject.toml
  - ../../../../../external/libs/jupyter/language-packs/.github/workflows/update_pot.yml
  - ../../../../../external/libs/jupyter/language-packs/.github/workflows/crowdin.yml
  - ../../../../../external/libs/jupyter/language-packs/.github/workflows/check_releases.yml
  - ../../../../../external/libs/jupyter/language-packs/.github/workflows/release_publish.yml
---
# language-packs 源码事实清单

## 项目元数据与顶层结构

- F-001: README.md:1-3 — 仓库标题 "Jupyterlab Language Packs"，徽章指向 crowdin.com/project/jupyterlab
- F-002: README.md:11-14 — WARNING 说明 `jupyterlab-language-pack-ach-UG` 仅用于通过 Crowdin in-context 功能在 JupyterLab 内直接翻译字符串，不应显式安装
- F-003: README.md:66-69 — 仓库末尾重申 Acholi (ach-UG) 为伪语言包（pseudo-language），服务于 in-context Crowdin 翻译
- F-004: jupyterlab/locale/jupyterlab.pot:4 — JupyterLab core 的源字符串 catalog，`Project-Id-Version: jupyterlab 0.0.0`
- F-005: extensions/ 目录下共 16 个扩展 .pot 文件（dask_labextension、jupyter_archive、jupyter_collaboration、jupyter_resource_usage、jupyterlab_git、jupyterlab_lsp、jupyterlab_recents、jupyterlab_search_replace、jupyterlab_spreadsheet_editor、jupyterlab_tour、jupyterlab_widgets、jupytext、nbdime、notebook、retrolab、spellchecker）

## repository-map.yml 包清单

- F-006: repository-map.yml:1-4 — 条目格式为「包名 → current-version-tag / supported-versions / url」三项
- F-007: repository-map.yml:1-68 — 共 17 个包条目，覆盖 JupyterLab 核心与第三方扩展
- F-008: repository-map.yml:21-24 — jupyterlab：current-version-tag `v4.6.1`，supported-versions `>=4.3`
- F-009: repository-map.yml:33-36 — jupyterlab-recents 的键为单数 `supported-version`，与其它条目的 `supported-versions` 不一致
- F-010: repository-map.yml:9-12 — jupyter-chat 在 map 中（v0.22.1），但 extensions/ 下无 jupyter_chat.pot（尚未生成 catalog）
- F-011: repository-map.yml:29-32 — jupyterlab-lsp 的 supported-versions 为多段范围 `>=3.8.0 <3.9.2 || >=3.9.3`（NpmSpec 语法）

## crowdin.yml 同步配置

- F-012: crowdin.yml:2-3 — `append_commit_message: false`，`commit_message: '[ci skip] New %language% translation from Crowdin'`
- F-013: crowdin.yml:4-5 — 首个 source 为 `/jupyterlab/locale/jupyterlab.pot`，translation 模板为 `/language-packs/jupyterlab-language-pack-%locale%/jupyterlab_language_pack_%locale_with_underscore%/locale/%locale_with_underscore%/LC_MESSAGES/%file_name%.po`
- F-014: crowdin.yml:3-35 — 每个扩展各一条 source→translation 映射，共 16 条 files 条目（1 个 jupyterlab + 15 个扩展）
- F-015: crowdin.yml 的 translation 模板使用 `%locale%`（如 de-DE）、`%locale_with_underscore%`（如 de_DE）、`%file_name%`（如 jupyterlab）三个 Crowdin 占位符

## 语言包目录结构与打包

- F-016: language-packs/README.md:1-3 — language-packs/ 目录下每个文件夹对应一个语言包的独立 python 包
- F-017: language-packs/ 目录下共 31 个 `jupyterlab-language-pack-*` 包目录（ach-UG、ar-SA、ca-ES、cs-CZ、da-DK、de-DE、el-GR、es-ES、et-EE、fi-FI、fr-FR、he-IL、hu-HU、hy-AM、id-ID、it-IT、ja-JP、ko-KR、lt-LT、nl-NL、no-NO、pl-PL、pt-BR、ro-RO、ru-RU、si-LK、tr-TR、uk-UA、vi-VN、zh-CN、zh-TW）
- F-018: language-packs/jupyterlab-language-pack-de-DE/pyproject.toml:6-7 — 普通语言包包名 `jupyterlab-language-pack-de-DE`，描述 "JupyterLab German (Germany) Language Pack"
- F-019: language-packs/jupyterlab-language-pack-de-DE/pyproject.toml:23-24 — entry-points 段 `[project.entry-points."jupyterlab.languagepack"]` 注册 `de_DE = "jupyterlab_language_pack_de_DE"`
- F-020: language-packs/jupyterlab-language-pack-de-DE/pyproject.toml:34-35 — hatch build hook `jupyter-translate` 依赖 `jupyterlab-translate>=1.2.0`
- F-021: language-packs/jupyterlab-language-pack-de-DE/pyproject.toml:37-44 — wheel 打包 artifacts 仅含 `**/*.json` 与 `**/*.mo`，显式排除 `**/*.po`
- F-022: language-packs/jupyterlab-language-pack-de-DE/.copier-answers.yml:2-3 — 语言包由 Copier 模板生成：`_commit: v1.1.3`、`_src_path` 指向 jupyterlab-language-pack-cookiecutter
- F-023: language-packs/jupyterlab-language-pack-de-DE/.copier-answers.yml:4-6 — 模板变量 language/locale/version（de-DE 当前 version `4.0.post0`）
- F-024: language-packs/jupyterlab-language-pack-de-DE/jupyterlab_language_pack_de_DE/__init__.py:4 — 各语言包版本为 `X.Y.postZ` 格式，de-DE 为 `4.5.post3`
- F-025: language-packs/jupyterlab-language-pack-ach-UG/pyproject.toml:6 — ach-UG 伪语言包包名特殊，为 `jupyterlab-pseudo-language-pack`
- F-026: language-packs/jupyterlab-language-pack-ach-UG/pyproject.toml:23-24 — ach-UG 同样注册 entry-point `ach_UG = "jupyterlab_language_pack_ach_UG"`
- F-027: language-packs/jupyterlab-language-pack-de-DE/jupyterlab_language_pack_de_DE/locale/de_DE/LC_MESSAGES/jupyter_resource_usage.po:8-15 — .po 文件头含 `X-Crowdin-Project: jupyterlab`、`X-Crowdin-Project-ID: 409874`、`X-Crowdin-Language: de`、`X-Crowdin-File: /main/extensions/jupyter_resource_usage/locale/jupyter_resource_usage.pot`、`X-Crowdin-File-ID: 219`、`Language: de_DE` 与 `PO-Revision-Date`
- F-028: 各语言包 LC_MESSAGES/ 目录下 .po 文件集合不完全一致：ach-UG 无 jupyterlab_spreadsheet_editor.po，部分包（如 ar-SA、de-DE）含 retrolab.po

## scripts/ 自动化脚本

- F-029: scripts/01_check_releases.py:4-7 — 脚本职责为获取所有包的最新 tag 并更新 repository-map.yml
- F-030: scripts/01_check_releases.py:74-75 — 经 `github_ql.get_tags`（github_ql.py:33-58 按 `TAG_COMMIT_DATE DESC` 取 `min(100, n)` 个 tag）请求 100 个 tag（按 commit date 降序）
- F-031: scripts/01_check_releases.py:89-108 — 仅当 tag 非 devrelease/prerelease 且 version > current 时更新 current-version-tag；新版本超出 supported-versions 范围则记入 errors 并在最后 raise
- F-032: scripts/02_update_catalogs.py:4-15 — 脚本职责：校验 repository-map.yml url、同步 crowdin.yml、clone/fetch 仓库、checkout 版本、用 jupyterlab-translate 创建/更新 .pot
- F-033: scripts/02_update_catalogs.py:70-93 — `update_crowdin_config()` 固定 jupyterlab 的 source 条目，再按排序后的 repository-map.yml 逐包追加 `/extensions/<name>/locale/<name>.pot` 条目并重写 crowdin.yml
- F-034: scripts/02_update_catalogs.py:145-153 — `update_catalog` 调用 `jupyterlab_translate.api.extract_language_pack(package_repo_dir, REPO_ROOT, package_name, merge)` 生成/合并 .pot
- F-035: scripts/02_update_catalogs.py:206-250 — 遍历 supported-versions 范围内的所有 tag，逐个 `update_repo` + `update_catalog` 并置 `should_merge=True` 实现多版本合并提取
- F-036: scripts/03_prepare_release.py:57-97 — 遍历 `LANG_PACKS_PATH.iterdir()` 所有语言包，存在 pyproject.toml 时用 `copier --force --vcs-ref HEAD --data version=... update` 更新模板，否则用 `api.create_new_language_pack` 创建
- F-037: scripts/03_prepare_release.py:99-106 — 通过 `contributors.get_contributors_report(locale, crowdin_key)` 从 Crowdin 生成 CONTRIBUTORS.md 并写入
- F-038: scripts/04_check_version.py:4-6 — 校验所有语言包版本号一致
- F-039: scripts/04_check_version.py:24-29 — 用 `python -m hatch version` 读取每个包版本，以第一个包为参照
- F-040: scripts/04_check_version.py:39-47 — 存在版本不一致或 hatch 报错时打印清单并 `raise ValueError("Language packages do not have homogeneous version.")`

## jupyterlab-translate 集成

- F-041: requirements.txt:1-13 — 完整依赖列表：build、copier>=9.2.0、pydantic、crowdin-api-client、hatch>=1.5.0、jupyterlab-translate>=1.3.1、packaging、pip、polib、pyyaml、requests、semantic_version、twine
- F-042: scripts/02_update_catalogs.py:25 与 scripts/03_prepare_release.py:20 — 分别导入 `jupyterlab_translate.api` 与 `from jupyterlab_translate import api, contributors`
- F-043: language-packs/jupyterlab-language-pack-de-DE/pyproject.toml:34-35 — 每个语言包通过 hatch hook `jupyter-translate` 在构建时调用 jupyterlab-translate 编译

## GitHub Actions CI/CD

- F-044: .github/workflows/update_pot.yml:1-8 — "Update source strings"：push main 且路径含 repository-map.yml 时触发
- F-045: .github/workflows/update_pot.yml:34-55 — 检测到 `*.pot crowdin.yml` 有变更时创建 `pot-update-<sha>` 分支、提交并以 `gh pr create` 开 PR
- F-046: .github/workflows/crowdin.yml:1-11 — "Sync with Crowdin"：push 含 `**.pot` 或每日 cron `'45 1 * * *'` 触发
- F-047: .github/workflows/crowdin.yml:25-39 — 使用 `crowdin/github-action@v2`：upload_sources 与 download_translations，localization_branch_name 为 `l10n_crowdin_translations`，create_pull_request: true
- F-048: .github/workflows/crowdin.yml:40-44 — 需要 `CROWDIN_PROJECT_ID` 与 `CROWDIN_TOKEN` 两个 secrets
- F-049: .github/workflows/check_releases.yml:4-6 — cron `'42 2 * * *'` 每日检查各仓库新 tag 并开 PR
- F-050: .github/workflows/release_publish.yml:42-74 — build-artifacts 的 matrix.locale 显式列出 30 个发布 locale（ach-UG 至 zh-TW，不含 si-LK）
- F-051: .github/workflows/release_publish.yml:117-133 — publish 阶段用 `pypa/gh-action-pypi-publish` 将全部产物发布到 PyPI（skip-existing: true）
