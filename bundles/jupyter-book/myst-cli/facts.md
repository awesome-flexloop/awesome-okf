---
type: reference
title: "myst-cli 事实清单"
description: "myst-cli 命令行工具的源码事实提取，涵盖CLI架构、命令注册、build管线、session/store、项目加载、模板管理、迁移等"
tags: [myst-cli, facts, cli, build, session]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/index.ts"
    facts: [F-001, F-002]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/build.ts"
    facts: [F-003, F-004]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/start.ts"
    facts: [F-005]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/clean.ts"
    facts: [F-006]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/cli/options.ts"
    facts: [F-007, F-008, F-009]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/build.ts"
    facts: [F-010, F-011, F-012, F-013, F-014, F-015]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/session.ts"
    facts: [F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/cache.ts"
    facts: [F-024, F-025, F-026, F-027]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/types.ts"
    facts: [F-028, F-029]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/project/load.ts"
    facts: [F-030, F-031, F-032, F-033, F-034]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/project/types.ts"
    facts: [F-035, F-036, F-037]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/project/fromPath.ts"
    facts: [F-038]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/init/init.ts"
    facts: [F-039, F-040, F-041, F-042, F-043]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/process/myst.ts"
    facts: [F-044, F-045, F-046]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/store/reducers.ts"
    facts: [F-047, F-048, F-049]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/store/types.ts"
    facts: [F-050, F-051]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/transforms/index.ts"
    facts: [F-052]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/config.ts"
    facts: [F-053, F-054]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/plugins.ts"
    facts: [F-055, F-056, F-057]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/clean.ts"
    facts: [F-058, F-059, F-060]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/build/site/start.ts"
    facts: [F-061, F-062, F-063]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/index.ts"
    facts: [F-064]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/spec-version.ts"
    facts: [F-065]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-migrate/src/index.ts"
    facts: [F-066, F-067]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-migrate/src/migrations.ts"
    facts: [F-068]
---

# myst-cli 事实清单

本文档从 myst-cli 及相关包源码中提取编号事实（F-001 ~ F-068），作为概念文档和示例文档的溯源依据。

## CLI 架构与命令注册

- **F-001**: CLI 入口 `cli/index.ts` 使用 `commander` 库的 `Command` 类构建命令树，通过 `makeBuildCommand()`、`makeCleanCommand()`、`makeStartCommand()` 工厂函数分别创建 build、clean、start 子命令，并导出 options 工具函数。
- **F-002**: CLI 模块重新导出四个子模块：`build.js`（build 命令）、`clean.js`（clean 命令）、`options.js`（选项工厂）、`start.js`（start 命令）。
- **F-003**: `makeBuildCommand()` 创建 `build` 命令，描述为 "Build PDF, LaTeX, Word and website exports from MyST files"，接受可选文件列表参数 `[files...]`。
- **F-004**: build 命令支持的导出格式选项包括：`--pdf`、`--tex`、`--typst`、`--word/--docx`、`--md`、`--jats/--xml`、`--meca`、`--cff`、`--site`、`--html`、`--all`，以及 `--doi-bib`、`--watch`、`-o/--output`、`--force`、`--check-links`、`--strict`、`--ci`、`--max-size-webp`、`--keep-host`、`--port`、`--execute`、`--execute-parallel <n>`。
- **F-005**: `makeStartCommand()` 创建 `start` 命令，描述为 "Start the current project as a website"，支持选项：`--execute`、`--keep-host`、`--headless`、`--port`、`--server-port`、`--template`、`--max-size-webp`。
- **F-006**: `makeCleanCommand()` 创建 `clean` 命令，描述为 "Remove exports, temp files and installed templates"，接受可选文件列表 `[files...]`，支持 `--pdf/--tex/--typst/--docx/--md/--jats/--meca/--cff/--site/--html` 指定清理类型，以及 `--temp`、`--logs`、`--cache`、`--exports`、`--templates`、`--execute`、`-a/--all`、`-y/--yes`。
- **F-007**: `options.ts` 中所有选项均通过工厂函数创建，返回 commander `Option` 实例。布尔标志默认 `false`，`--execute-parallel` 默认并行度为 `cpus().length - 1`（至少 1）。
- **F-008**: `--max-size-webp` 接受 MB 数值（默认 1.5），内部转换为字节（`value * 1024 * 1024`）。`--port` 从 `PORT` 环境变量读取默认值，`--server-port` 从 `SERVER_PORT` 读取。
- **F-009**: DOI 引用 BibTeX 文件名常量为 `MYST_DOI_BIB_FILE = 'myst.doi.bib'`。

## Build 管线

- **F-010**: `build/build.ts` 定义 `BuildOpts` 类型，合并 `FormatBuildOpts`（格式选项）、`CollectionOptions`、`RunExportOptions`、`StartOptions`。
- **F-011**: `getAllowedExportFormats()` 根据 CLI 选项确定允许的导出格式列表：当 `--all` 或显式指定文件但无格式标志时启用全格式（docx/pdf/pdftex/typst/tex/xml/md/meca/cff），否则只启用显式请求的格式。
- **F-012**: `collectAllBuildExportOptions()` 是 build 管线的核心收集函数：解析文件参数 → 查找/加载项目 → 收集导出选项 → 解析输出路径，返回 `ExportWithInputOutput[]`。支持三种模式：`-o` 单文件命名输出、显式文件列表、无文件参数（项目模式，加载所有项目页面）。
- **F-013**: `build()` 函数是 build 命令主入口：收集导出选项 → 执行 `localArticleExport()` 单文件导出 → 如需要则执行 `buildSite()` 或 `buildHtml()` 站点构建 → 写入 `myst.build.json` 日志 → 调用 `session.dispose()`。
- **F-014**: `exportSite()` 判断是否执行站点构建：当 `--site`、`--html`、`--all` 选项存在，或存在 site 配置且无 `--force` 和显式导出格式时，返回 true。
- **F-015**: 构建输出目录结构：`_build/` 为构建根目录，下含 `site/`（站点内容）、`exports/`（导出文件）、`temp/`（临时文件）、`cache/`（缓存）、`templates/`（下载的模板）、`logs/`（日志）、`html/`（静态 HTML）、`execute/`（执行缓存）。
- **F-016**: build 模块 `build/index.ts` 重新导出：build、clean、docx、pdf、site、tex、types、utils、html、meca、jats、typst、legacy 子模块。

## Session 会话系统

- **F-017**: `Session` 类实现 `ISession` 接口，构造函数初始化：Redux store（`createStore(rootReducer)`）、chalk 日志器（默认 info 级别）、DOI 请求限流器（p-limit 并发 3）、Notebook 执行信号量（`cpus().length - 1`）、HTTPS 代理支持（从 `HTTPS_PROXY` 环境变量）。
- **F-018**: Session 默认 API URL 为 `https://api.mystmd.org`，可通过 `API_URL` 环境变量覆盖。配置文件名默认为 `['myst.yml', 'myst.yaml']`。
- **F-019**: Session 构造时异步检查 npm 最新版本（`latestVersion('mystmd')`），首次日志输出时通过 `showUpgradeNotice()` 显示 boxen 样式的升级提示框。
- **F-020**: Session 提供路径方法：`sourcePath()` 返回项目/站点根目录，`buildPath()` 返回 `_build` 目录，`sitePath()` 返回 `_build/site`，`contentPath()` 返回 `_build/site/content`，`publicPath()` 返回 `_build/site/public`。
- **F-021**: Session 支持 `clone()` 方法创建克隆会话（共享 logger、限流器、信号量、Jupyter 管理器），`reload()` 方法重新加载项目和站点配置。
- **F-022**: Session 内置 `fetch()` 方法，自动处理代理（排除 localhost）和超时日志（5秒无响应时打印等待信息）。
- **F-023**: Session 通过 `jupyterSessionManager()` 懒加载 Jupyter SessionManager：优先使用 `JUPYTER_BASE_URL`/`JUPYTER_TOKEN` 环境变量连接已有服务器，否则通过 `launchJupyterServer()` 启动新服务器。
- **F-024**: Session 通过 `loadPlugins()` 加载用户插件，支持 `executable` 和 `javascript`（.mjs）两种插件类型。
- **F-025**: `dispose()` 方法清理所有克隆会话和 Jupyter SessionManager。

## Session 缓存

- **F-026**: `castSession()` 将 ISession 转换为 ISessionWithCache，在 session 对象上挂载内存缓存：`$citationRenderers`（引用渲染器，按路径索引）、`$doiRenderers`（DOI 渲染器，按 DOI 索引）、`$externalReferences`（外部引用，按 ID 索引）、`$mdast`（MDAST 树缓存，按绝对路径索引）、`$outputs`（输出缓存）、`$siteTemplate`（站点模板）。
- **F-027**: 磁盘缓存位于 `_build/cache/` 目录，提供 `writeToCache()`、`checkCache()`（支持 maxAge 天数过期检查）、`loadFromCache()` 三个函数。
- **F-028**: ISessionWithCache 接口提供 `$getMdast(file)` 和 `$setMdast(file, data)` 方法，使用标准化路径（`path.resolve`）作为键。

## ISession 接口

- **F-029**: ISession 接口定义核心属性和方法：`API_URL`、`configFiles`、`store`（Redux Store）、`log`（Logger）、`doiLimiter`（p-limit Limit）、`executionSemaphore`（Semaphore）、`reload()`、`clone()`、路径方法、`showUpgradeNotice()`、`plugins`、`loadPlugins()`、`getAllWarnings()`、`jupyterSessionManager()`、`dispose()`、`fetch()`。

## 项目加载与 TOC

- **F-030**: `loadProjectFromDisk()` 是项目加载的核心函数，加载流程：检查缓存 → `loadConfig()` 加载配置 → 按优先级确定 TOC 来源（myst.yml toc > legacy _toc.yml > 文件系统遍历）→ 加载 BibTeX 文件 → dispatch 到 Redux store → 合并引用渲染器。
- **F-031**: TOC 三种来源优先级：1) myst.yml 中的 `project.toc` 字段（`projectFromTOC`）；2)  legacy Jupyter Book `_toc.yml`（`projectFromSphinxTOC`）；3) 文件系统自动发现（`projectFromPath`，遍历 md/ipynb 文件）。
- **F-032**: 当检测到 legacy `_config.yml` 时，init 命令会提示用户升级 Jupyter Book 配置（通过 `upgradeJupyterBook()`），包括术语表迁移、admonition 名称小写化、配置迁移等。
- **F-033**: `filterPages()` 将 LocalProject 展开为扁平的 LocalProjectPage 列表（首页 + pages 中有 file 属性的页面）。
- **F-034**: `findProjectsOnPath()` 递归扫描目录树查找包含 myst.yml 的子项目。

## 项目类型

- **F-035**: `LocalProject` 类型包含 `path`、`file`（索引文件路径）、`index`（首页 slug）、`implicitIndex`、`bibliography`（BibTeX 文件列表）、`pages`（页面/文件夹/外部URL混合数组）。
- **F-036**: `LocalProjectPage` 类型：`file`、`slug`、`level`（-1~6 的标题级别，-1=part, 0=chapter）、`title`、`implicit`。
- **F-037**: `LocalProjectFolder` 类型：`title`、`level`；`ExternalURL` 类型：`url`、`title`、`level`、`open_in_same_tab`。
- **F-038**: `projectFromPath()` 递归遍历目录，发现 md/ipynb 等有效文件（排除 `_build`、隐藏文件等），按文件名排序生成隐式 TOC。遇到子目录中的 myst.yml 或 _toc.yml 时停止递归。

## Init 初始化

- **F-039**: `init()` 命令交互流程：打印欢迎信息 → 写入 .gitignore（添加 `_build`） → 加载现有配置 → 无配置时检测 Jupyter Book legacy → 生成 myst.yml（含 `version: 1`、project 配置和/或 site 配置） → 可选 `--write-toc` 生成 TOC → 交互式询问是否启动开发服务器。
- **F-040**: 默认项目配置包含 UUID 格式的 `project.id`（使用 uuid v4 生成），可选 title/description/keywords/authors/github 字段。
- **F-041**: 默认站点配置使用 `template: book-theme`，支持 favicon/logo 选项。
- **F-042**: init 支持 `--gh-pages`、`--gh-curvenote`、`--readthedocs` 生成对应 CI/CD 配置文件。
- **F-043**: init 自动检测 Git 仓库并更新 .gitignore 添加 `_build` 忽略规则。

## Process 处理管线

- **F-044**: `parseMyst()` 是核心解析函数，使用 myst-parser 的 `mystParse()` 将 Markdown 内容解析为 MDAST 树，自动注册内置指令（card、grid、proof、exercise、tab）和角色（button），并通过 VFile 收集解析消息。
- **F-045**: `getMystParserOptions()` 构建解析器选项：启用 linkify、注册指令列表（内置 + session.plugins.directives）、启用 frontmatter 和 math 扩展（可通过 project.settings.parser.dollarmath 禁用 $ 公式）、注册角色列表（button + session.plugins.roles）。
- **F-046**: process 模块导出：citations、file、loadReferences、mdast、myst、notebook、site 子模块。

## Redux Store 状态管理

- **F-047**: Store 使用 Redux Toolkit 的 `createSlice` 创建三个 slice：`projects`（LocalProject 按路径存储）、`affiliations`（机构 ID→名称映射）、`config`（原始配置、验证配置、路径信息）。
- **F-048**: config slice 管理：`currentProjectPath`、`currentSitePath`、`rawConfigs`（按路径）、`projects`（验证后配置）、`projectParts`/`fileParts`（文件分块）、`sites`（站点配置）、`filenames`、`configExtensions`。
- **F-049**: projects slice 提供 `receive` action 将 LocalProject 存储到按绝对路径索引的 Record 中。
- **F-050**: `BuildWarning` 类型包含 `message`、`kind`（error/warn/info/debug）、`note`、`url`、`position`、`ruleId`。
- **F-051**: `WarningKind` 类型为 `'error' | 'warn' | 'info' | 'debug'`；`ExternalLinkResult` 记录链接检查结果（url/ok/skipped/status/statusText）。

## Transforms 转换管线

- **F-052**: transforms 模块导出12种转换器：anywidgets、citations、code、crossReferences、dois、ror、embed、images、include、links、mdast、outputs、inlineExpressions。

## 配置系统

- **F-053**: 配置系统支持 myst.yml 和 myst.yaml 两种文件名，通过 `js-yaml` 解析，使用 `myst-config` 包的 `validateProjectConfig`/`validateSiteConfig` 进行验证。
- **F-054**: 当前配置版本号为 `VERSION = 1`（在 config.ts 中定义），`SPEC_VERSION = 3`（在 spec-version.ts 中定义，为 MDAST 规范版本）。

## 插件系统

- **F-055**: 插件支持两种类型：`executable`（可执行文件，通过 stdin/stdout 通信获取插件规范）和 `javascript`（.mjs ES 模块，通过动态 import 加载）。
- **F-056**: 插件可导出 `directives`、`roles`、`transforms` 数组扩展 MyST 语法能力，以及可选的 `name` 字段标识插件。
- **F-057**: 插件加载时按路径去重，已加载的插件不会重复加载。加载日志显示插件名称、指令数、角色数、转换器数。

## Clean 清理

- **F-058**: `clean()` 函数支持选择性清理构建产物，`CleanOptions` 包含所有导出格式和构建目录的开关。默认清理选项（DEFAULT_OPTS）包括所有导出格式 + temp + logs + exports + execute，但不包括 cache 和 templates。
- **F-059**: `--all` 选项清理所有内容（ALL_OPTS 包含 cache + templates）。无选项时使用 DEFAULT_OPTS。
- **F-060**: 清理流程：收集导出输出路径 → 按选项收集 _build 子目录 → 去重（子路径被父路径包含时移除子路径） → 用户确认 → 删除路径 → 删除空的 _build 目录。

## 开发服务器（Start）

- **F-061**: `startContentServer()` 创建 Express 应用，启用 CORS，提供 `/` 端点返回版本和配置链接，默认端口范围 3100-3200（通过 get-port 查找空闲端口）。
- **F-062**: 开发服务器包含 WebSocket 服务器用于实时日志推送和热重载，通过 `watchContent()` 监视文件变化。
- **F-063**: start 命令默认同时启动内容服务器和应用服务器，`--headless` 模式只启动内容服务器。`--keep-host` 保留原始 HOST 环境变量（默认改为 localhost）。

## 包导出

- **F-064**: myst-cli 主入口 `src/index.ts` 导出：build、cli、config、init、frontmatter、plugins、process、project、session、store、transforms、utils、spec-version 子模块，以及默认导出 version 字符串。
- **F-065**: `SPEC_VERSION = 3` 表示当前 MDAST 规范版本。

## 版本迁移（myst-migrate）

- **F-066**: `migrate()` 函数接受 IFile（含 version 字段）和目标版本选项，通过按版本顺序应用 migration 升级/降级。MIGRATIONS 数组按顺序存储各版本迁移。
- **F-067**: 迁移支持双向：version < to 时依次执行 upgrade，version > to 时依次执行 downgrade。
- **F-068**: 当前有3个迁移：v1（footnotes 脚注迁移）、v2（blockClasses 块类名迁移）、v3（outputs 输出迁移），对应 MIGRATIONS 数组长度为3。
