---
type: bundle
title: "myst-cli 命令行工具"
okf_version: "0.2"
---

# myst-cli 命令行工具知识库

本知识包是 [MyST Markdown](https://mystmd.org) 生态的命令行工具 myst-cli 的系统化中文文档，基于 mystmd 源码（`mystmd/packages/myst-cli/`、`mystmd/packages/myst-migrate/`、`mystmd/packages/myst-directives/`、`mystmd/packages/myst-roles/` 等目录）深度阅读生成，覆盖从 CLI 架构、项目初始化、构建管线、开发服务器到模板系统、版本迁移的完整工具链知识体系。所有内容均溯源至源码，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 核心概念（concepts/）

* [CLI 架构](concepts/00-cli-architecture.md) — 基于 commander 的命令注册、Session 依赖注入容器、Redux 状态管理、build/start/init/clean 四大核心命令、插件加载机制、Sphinx/Roam 兼容模式。
* [Build 管线](concepts/01-build-pipeline.md) — 多格式导出架构、collectAllBuildExportOptions 分发机制、BuildExportOption 类型、12种导出格式（PDF/LaTeX/Typst/DOCX/MD/JATS/MECA/CFF/MEI/site/HTML/all）、localArticleExport/siteBuild 双轨流程、--watch 热构建。
* [Start 开发服务器](concepts/02-start-dev-server.md) — 双服务器架构（内容服务器+应用服务器）、双端口绑定策略（keep-host 机制）、watchContent 热重载、WebSocket 实时通信、文件变化去抖、模板安装流程。
* [Init 项目初始化](concepts/03-init-project.md) — 项目初始化全流程、myst.yml 配置生成、自动 UUID 生成、.gitignore 更新、TOC 三级来源（myst.yml/_toc.yml/文件系统）、--write-toc 自动生成、Jupyter Book 1.x 升级、GitHub Pages 工作流生成。
* [Clean 命令](concepts/04-clean-command.md) — 16种清理目标、默认清理与全清理差异、路径去重机制（isSubpath）、导出文件精确清理、用户交互确认（-y 跳过）。
* [项目加载与TOC](concepts/05-project-load-toc.md) — loadProjectFromDisk 流程、TOC 三级优先级（project.toc > _toc.yml > 自动发现）、LocalProject/LocalProjectPage/LocalProjectFolder/ExternalURL 类型、Bibliography 自动发现与声明、多项目支持、缓存机制。
* [模板系统](concepts/06-template-system.md) — 站点模板（book-theme/article-theme）、导出模板（各格式排版控制）、模板缓存（_build/templates/）、MystTemplate 类型、命令行 --template 覆盖、模板下载与安装。
* [版本迁移](concepts/07-migration.md) — myst-migrate 链式迁移架构、Migration.upgrade/downgrade 双向支持、MIGRATIONS 数组（v0→v1 脚注、v1→v2 块类名、v2→v3 Notebook输出）、SPEC_VERSION=3、IFile 版本跟踪、Jupyter Book 1.x 配置迁移。
* [会话与缓存](concepts/08-session-cache.md) — Session 依赖注入容器、Redux Store/Logger/p-limit并发控制/HTTPS代理、路径体系（sourcePath→buildPath→sitePath）、Clone 会话机制、双层缓存策略（内存$mdast/$doiRenderers + 磁盘_build/cache）、Jupyter SessionManager 单例、版本升级提示。
* [Store 状态管理](concepts/09-store-state.md) — Redux Toolkit Slice 设计、projects/affiliations/config/watchedFiles 四个 Slice、RootState 结构、selectors 查询模式、BuildWarning 类型系统、ExternalLinkResult 链接检查。

## 实战示例（examples/）

* [初始化MyST项目](examples/01-init-project.md) — 创建项目目录、运行 myst init、自动生成 myst.yml、--write-toc 目录生成、--gh-pages 部署配置、Jupyter Book 1.x 迁移提示、常用配置项说明。
* [构建站点和导出](examples/02-build-site.md) --site/--html/--all 站点构建、PDF/DOCX/LaTeX/Typst/MD/JATS/MECA/CFF 多格式导出、frontmatter exports 声明、--execute Notebook 执行、--check-links 链接检查、--strict/--ci 模式、单文件/多文件构建。
* [启动开发服务器](examples/03-dev-server.md) — myst start 基本使用、--port/--server-port 端口配置、--headless 仅API模式、--execute Notebook执行、双服务器架构、热重载机制、Docker 容器 --keep-host、与 build --watch 对比、故障排查。
* [迁移现有项目](examples/04-migrate-project.md) — Jupyter Book 1.x 自动检测与升级、upgradeJupyterBook 四步迁移、myst-migrate API 使用（migrate() 升级/降级）、v0-v3 各版本变更、迁移检查清单、回滚策略。

## 信源登记簿（references/）

* [CLI 命令索引](references/cli-index.md) — `myst-cli/src/cli/index.ts` 命令注册入口、init/build/start/clean/validate/extensions 六大命令工厂、版本号定义、Sphinx/Roam 兼容模式全局标志。
* [Build 命令实现](references/build-build.md) — `myst-cli/src/cli/build.ts` makeBuildCommand 工厂、18个命令选项定义（execute/pdf/tex/typst/docx/md/jats/meca/cff/site/html/all/doi-bib/watch/output/force/check-links/strict/ci/max-size-webp/keep-host/port）。
* [项目加载源码](references/project-load.md) — `myst-cli/src/project/load.ts` loadProjectFromDisk 函数、BibTeX 文件发现、TOC 解析三种来源、LocalProject 数据结构、implicit 隐式页面标记、多项目扫描（findProjectsOnPath）。
* [Session 类源码](references/session-session.md) — `myst-cli/src/session/session.ts` Session 类实现、依赖注入容器属性、路径方法体系（sourcePath/buildPath/sitePath/contentPath/publicPath）、clone 方法、dispose 清理、版本升级检查、fetch 方法代理注入。
* [MyST 处理管线](references/process-myst.md) — `myst-cli/src/process/myst.ts` processFile 处理流程、文件加载→frontmatter解析→插件扩展→MDAST转换→引用解析→导出分发、transforms 管线、插件 transforms 注入点。

## 事实与洞察

* [事实提取](facts.md) — 75个编号源码事实（F-001 ~ F-075），覆盖命令定义、Session 类、Build 管线、Start 服务器、Init 流程、Clean 策略、Store 结构、Cache 机制、模板系统、版本迁移、指令/角色默认列表。
* [关键洞察](insights.md) — 从源码阅读中提炼的架构洞察，包括依赖注入设计、双服务器架构考量、多格式导出分发模式、链式迁移设计、双层缓存策略、TOC 三级回退机制、Redux 在 CLI 中的应用。

## 学习路径建议

1. **快速上手**：00-cli-architecture → 03-init-project → 运行 examples/01-init-project.md → examples/03-dev-server.md
2. **构建与发布**：01-build-pipeline → 04-clean-command → 06-template-system → 运行 examples/02-build-site.md
3. **深入理解**：08-session-cache → 09-store-state → 05-project-load-toc → 阅读 facts.md
4. **迁移与升级**：07-migration → 运行 examples/04-migrate-project.md
5. **源码溯源**：阅读 references/ 中的信源文档，理解各命令的底层实现机制

## 信任与生命周期说明

* **status 判定依据**：全部 21 个内容文档（10 个概念 + 4 个示例 + 5 个信源登记）+ facts.md + insights.md + 根 index.md，非 index/log 文件均 `status: stable`。内容基于对 mystmd 源码（`external/libs/ai/jupyter-book/mystmd/packages/` 目录）myst-cli/myst-migrate/myst-directives/myst-roles/myst-config/myst-templates/myst-common 等包的逐模块阅读与事实提取（75个编号源码事实 F-001 ~ F-075）。
* **stale_after 解释**：统一设置为 `2027-12-31`。MyST CLI 核心架构（commander 命令注册、Session DI 容器、Redux 状态管理、多格式导出管线）在 mystmd 1.x 中保持稳定，该日期作为对未来大版本变化的保守重新评估节点。
* **核验链路**：`generated` 记录原始生成时刻（2026-08-23）；`verified: true` 记录过程核验，所有类名、函数名、参数名均通过源码 Read/Grep 验证。
* **覆盖范围**：覆盖 myst-cli 的 init/build/start/clean 四大核心命令、Session 依赖注入容器、Redux Store 状态管理、双层缓存策略、模板系统、版本迁移机制、项目加载与TOC解析；覆盖 myst-directives 默认指令列表（28个）和 myst-roles 默认角色列表（25个）；未覆盖 myst-common 解析器内部实现、myst-transforms 详细转换逻辑、myst-templates 模板渲染细节。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
facts
insights
log
```
