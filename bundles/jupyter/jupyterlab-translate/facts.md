---
type: Facts
okf_version: "0.2"
title: "jupyterlab-translate 源码事实清单"
generated: "2026-08-22"
tags: [jupyterlab, translation, i18n, gettext, localization, hatch]
sources:
  - ../../../../../external/libs/jupyter/jupyterlab-translate/pyproject.toml
  - ../../../../../external/libs/jupyter/jupyterlab-translate/jupyterlab_translate/api.py
  - ../../../../../external/libs/jupyter/jupyterlab-translate/jupyterlab_translate/cli.py
  - ../../../../../external/libs/jupyter/jupyterlab-translate/jupyterlab_translate/constants.py
  - ../../../../../external/libs/jupyter/jupyterlab-translate/jupyterlab_translate/converters.py
  - ../../../../../external/libs/jupyter/jupyterlab-translate/jupyterlab_translate/utils.py
---

# jupyterlab-translate 事实清单

## 项目概况

- F-001: pyproject.toml:6-7 — 包名为 jupyterlab-translate，描述为 "JupyterLab Language Pack Translations Helper"
- F-002: pyproject.toml:9 — 许可证为 BSD License（LICENSE.txt）
- F-003: pyproject.toml:23 — 要求 Python >= 3.7
- F-004: pyproject.toml:2 — 构建系统使用 hatchling >= 1.5.0
- F-005: README.md:10 — 用于为 JupyterLab 生态系统生成 language packs
- F-006: README.md:14-21 — 核心功能：从 *.py/*.ts/*.tsx 提取字符串、从 JSON schema 提取字符串、创建 gettext *.pot 目录、去重、创建 *.po 目录、编译为 *.mo 和 *.json、提供 Hatch Build Hook、从 Crowdin 更新贡献者列表

## CLI 命令行接口

- F-007: pyproject.toml:50-51 — 注册两个 CLI 入口点：jupyterlab-translate（cli:main）、gettext-extract（gettext_extract:main）
- F-008: pyproject.toml:53-54 — 注册 Hatch build hook 入口点：jupyter-translate = hooks
- F-009: cli.py:39-48 — 使用 Click 构建 CLI，主命令组提供 JupyterLab 扩展本地化字符串提取功能
- F-010: cli.py:23-29 — 定义公共参数：language_packs_repo_dir（存在的路径）、package_repo_dir（Path 类型存在路径）、project（项目名）
- F-011: cli.py:34-36 — --locales/-l 选项支持多值（multiple=True）指定目标语言

### 独立包命令

- F-012: cli.py:53-60 — extract 子命令：为单个 JupyterLab 扩展提取可翻译字符串并创建 catalog
- F-013: cli.py:63-71 — update 子命令：更新扩展的语言 catalog 中的字符串
- F-014: cli.py:74-102 — update_contributors 子命令：从 Crowdin 报告更新贡献者列表，需要 CROWDIN_API_KEY 环境变量
- F-015: cli.py:80-86 — 缺少 CROWDIN_API_KEY 时打印错误信息并以退出码 1 退出
- F-016: cli.py:90-92 — 通过 glob 查找 jupyterlab_language_pack_??_?? 格式的 Python 包文件夹获取语言环境名称
- F-017: cli.py:97 — locale_name 从包名末尾 5 个字符提取（如 zh_CN）
- F-018: cli.py:105-111 — compile 子命令：编译扩展的 catalogs

### Language Pack 命令

- F-019: cli.py:116-126 — extract_pack 子命令：为 jupyterlab-language-pack 提取字符串
- F-020: cli.py:129-140 — update_pack 子命令：更新 language pack 的 catalog
- F-021: cli.py:143-150 — compile_pack 子命令：编译 JupyterLab Language Pack 的 catalogs

## 依赖

- F-022: pyproject.toml:25-36 — 核心依赖：babel（国际化）、click（CLI）、copier >=9.2.0（项目模板）、copier-templates-extensions、crowdin-api-client（Crowdin API）、hatchling >=1.5、jinja2-time、polib（PO文件操作）、pydantic、requests
- F-023: pyproject.toml:25 — Python < 3.10 时需要 importlib-metadata >=4.8.3
- F-024: README.md:31 — 需要额外安装 nodejs >= 14
- F-025: pyproject.toml:39-44 — 测试可选依赖：hatch、pre-commit、pytest、pytest-cov

## API 模块

- F-026: api.py:25-38 — check_locales() 验证 locale 列表，无效时抛出 ValueError
- F-027: api.py:41-50 — normalize_project() 将项目名转为小写、横线转下划线
- F-028: api.py:53-66 — extract_package() 为独立包提取翻译：normalize 项目名 → 检查输出目录 → 调用 extract_translations
- F-029: api.py:69-84 — update_package() 更新独立包翻译：验证 locales → normalize → 检查输出目录 → update_translations
- F-030: api.py:87-100 — compile_package() 编译独立包：验证 locales → normalize → compile_translations → 对每个 po 文件转换为 JSON 并编译为 MO
- F-031: api.py:103-121 — extract_language_pack() 为 language pack 提取翻译：JUPYTERLAB 核心包直接输出到 language_packs_repo_dir/jupyterlab，扩展包输出到 extensions/ 子目录
- F-032: api.py:124-141 — update_language_pack() 更新 language pack：与 extract 类似但输出到 jupyterlab_extensions/ 子目录
- F-033: api.py:144-150 — compile_po_file() 原地编译 .PO 为 .MO 和 .JSON，删除已存在的 JSON 文件

## 常量与配置

- F-034: constants.py:11 — TEMPLATE_URL 指向 cookiecutter 模板：https://github.com/jupyterlab/jupyterlab-language-pack-cookiecutter
- F-035: constants.py:12 — TEMPLATE_REF 使用 master 分支
- F-036: constants.py:13-18 — 路径常量：EXTENSIONS_FOLDER="extensions"、JUPYTERLAB="jupyterlab"、LANG_PACKS_FOLDER="language-packs"、LC_MESSAGES="LC_MESSAGES"、LOCALE_FOLDER="locale"、TRANSLATIONS_FOLDER="translations"
- F-037: constants.py:23 — 支持的 gettext 函数调用根：trans、this.trans、this._trans、this.props.trans、props.trans
- F-038: constants.py:24-36 — 支持的 gettext 函数：__、gettext、_n、ngettext、_p、pgettext、_np、npgettext
- F-039: constants.py:25-26 — 简单翻译函数 __/gettext：第0参数为 text
- F-040: constants.py:27-28 — 复数翻译函数 _n/ngettext：第0参数 text，第1参数 textPlural
- F-041: constants.py:29-30 — 上下文翻译函数 _p/pgettext：第0参数 context，第1参数 text
- F-042: constants.py:31-35 — 上下文+复数函数 _np/npgettext：context(0)、text(1)、textPlural(2)
- F-043: constants.py:38-42 — build_parser() 为每个 root 前缀构建 parser，组合 root + "." + func.expression
- F-044: constants.py:46-58 — GETTEXT_CONFIG：JS 解析器配置，glob 模式匹配 **/*.ts*(x)，忽略 examples、*.spec.ts、node_modules，保留其他行首注释作为翻译注释

## Hatch Build Hook

- F-045: hooks.py:1-10 — 注册 hatch build hook：hatch_register_build_hook() 返回 JupyterLanguageBuildHook
- F-046: plugin.py:17 — COMPILATION_THRESHOLD = 0（编译阈值为0%，即所有PO文件都编译）
- F-047: plugin.py:18 — PACKAGE_PREFIX = "jupyterlab_language_pack_"
- F-048: plugin.py:21-24 — JupyterLanguageBuildHook 继承 BuildHookInterface，PLUGIN_NAME = "jupyter-translate"
- F-049: plugin.py:26-41 — _get_locale_name() 通过 glob 查找 jupyterlab_language_pack_??_?? 或 ???_?? 格式的包目录，提取 locale 名称，构建 messages_folder 路径
- F-050: plugin.py:43-55 — clean() 方法：删除 LC_MESSAGES 下所有 .json 和 .mo 文件
- F-051: plugin.py:57-83 — initialize() 方法构建 wheel 时：遍历 .po 文件 → polib 读取 → 检查翻译百分比 → 达到阈值则 compile_po_file()
- F-052: plugin.py:84-97 — sdist/非 wheel 构建时：如有 CROWDIN_API_KEY 则更新 CONTRIBUTORS.md

## 转换器

- F-053: converters.py:9-67 — convert_catalog_to_json() 将 .po 转为 Jed JSON 格式
- F-054: converters.py:25 — 使用 polib.pofile 读取 PO，wrapwidth=100000 禁用列换行
- F-055: converters.py:28-35 — JSON 元数据：domain=项目名、version=Project-Id-Version 末尾版本、language=下划线转横线、plural_forms=Plural-Forms
- F-056: converters.py:38-42 — 如果 JSON 文件已存在，加载并合并（删除旧元数据，保留旧翻译条目）
- F-057: converters.py:44-46 — 跳过 obsolete 条目
- F-058: converters.py:48-51 — 有 msgctxt 时 key 格式为 "{msgctxt}\x04{msgid}"，否则为 msgid
- F-059: converters.py:53-54 — msgstr 非空时输出 [msgstr]
- F-060: converters.py:55-64 — 复数形式：收集非空 msgstr_plural，单复数形式语言添加空字符串 dummy 元素
- F-061: converters.py:66 — JSON 输出：sort_keys=True、indent=4

## 工具函数

- F-062: utils.py:38-89 — get_version() 获取版本号：优先 setup.py --version 或 hatch version → 其次 package.json version → 最后 git describe --tags（去掉v前缀）
- F-063: utils.py:92-125 — create_new_language_pack() 使用 copier 从模板创建新语言包，支持 locale 验证（ach_UG、no_NO 特殊处理）、自动获取语言英文名
- F-064: utils.py:112-113 — no_NO 特殊映射为 nb_NO（Bokmål）
- F-065: utils.py:118 — 新包目录命名格式：jupyterlab-language-pack-{locale-dash}（如 jupyterlab-language-pack-zh-CN）
- F-066: utils.py:128-141 — check_locale() 验证 locale：ach_UG 和 no_NO 为例外，否则用 babel.Locale.parse 验证
- F-067: utils.py:144-161 — find_locales() 在 output_dir/locale 目录下查找有效 locale 子目录
- F-068: utils.py:166-184 — find_packages_source_files() 列出多个包的源文件
- F-069: utils.py:187-219 — find_source_files() 递归查找 .ts/.tsx/.py 文件，跳过 tests/test/node_modules/lib/.git/.ipynb_checkpoints 目录
- F-070: utils.py:224-277 — extract_tsx_strings() 使用 gettext-extract 工具提取 TS/TSX 字符串：临时 POT 文件 → 临时 JSON 配置 → subprocess 调用 gettext-extract → polib 解析结果
- F-071: utils.py:250 — 给 gettext-extract 输出添加 "#, fuzzy\n" 前缀修复格式问题
- F-072: utils.py:301-318 — DEFAULT_SCHEMA_SELECTORS 定义 JSON Schema 中需翻译字段的选择器：title/description（schema上下文）、properties/*/title/description（settings上下文）、jupyter.lab.menus/*/label（menu上下文）、jupyter.lab.toolbars/*/label/caption（toolbar上下文）等

## 贡献者管理

- F-073: contributors.py:17 — CONTRIBUTORS 常量为 "CONTRIBUTORS.md"
- F-074: contributors.py:20-23 — FirstCrowdinClient 继承 CrowdinClient，TOKEN 从 CROWDIN_API_KEY 环境变量获取，PAGE_SIZE=100000
- F-075: contributors.py:28-43 — get_project_data() 获取 Crowdin 项目数据（默认项目 ID 409874）
- F-076: contributors.py:46-64 — get_languages() 从项目数据中提取目标语言列表
- F-077: contributors.py:67-107 — download_data() 生成 top members 报告（按 words 统计）：生成 CSV 报告 → 轮询状态等待（ETA 秒数*2或5秒）→ 下载报告
- F-078: contributors.py:83 — 报告起始日期为 2019-04-01
- F-079: contributors.py:110-167 — format_data() 解析 CSV 报告，生成 Markdown 格式贡献者列表，包含 Crowdin 个人资料链接
- F-080: contributors.py:140-146 — 解析 "Name (username)" 格式分离姓名和用户名
- F-081: contributors.py:170-210 — get_contributors_report() 获取并格式化指定 locale 的贡献者报告，支持临时传入 crowdin_key（使用后恢复原 token）

## 包发现（finder.py）

- F-082: finder.py:16-17 — 定义两个 entry point 组名：jupyterlab.languagepack、jupyterlab.locale
- F-083: finder.py:26-66 — get_installed_packages_locale() 通过 jupyterlab.locale entry point 发现安装的扩展本地化数据，加载对应 locale 的 LC_MESSAGES/{name}.json
- F-084: finder.py:69-81 — get_installed_language_packs() 通过 jupyterlab.languagepack entry point 获取所有已安装语言包列表
- F-085: finder.py:84-101 — get_language_pack() 获取指定 locale 的语言包数据（Jed 格式字典），无效 locale 返回空字典

## gettext-extract 封装

- F-086: gettext_extract.py:8-9 — INDEX_JS 指向同目录的 index.js（ncc 打包的 gettext-extract 单文件）
- F-087: gettext_extract.py:12-14 — main() 将命令行参数转发给 node 执行 index.js
- F-088: README.md:60-63 — gettext-extract 工具来自 @sinedied/gettext-extract，使用 @vercel/ncc 打包为单体 JS 文件内嵌在 Python 包中

## 测试

- F-089: tests/ 目录包含 test_hatch_hook.py、test_utils.py 和 dummy_pkg 测试夹具
- F-090: tests/dummy_pkg/locale/dummy_pkg.pot — 测试用 POT 文件
- F-091: tests/dummy_pkg/src/documentwidget.ts — 测试用 TypeScript 源文件
- F-092: tests/example.json — 测试用 JSON 示例文件

## 版本管理

- F-093: pyproject.toml:56-57 — hatch version 从 jupyterlab_translate/__init__.py 读取
- F-094: pyproject.toml:22 — version 为 dynamic（从 __init__.py 获取）
