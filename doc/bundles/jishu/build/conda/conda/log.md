# Bundle Update Log

## 2026-09-02

**Migration**: 合并 learning 08/conda-dev-github-wiki（conda 组织 .github 元仓库：仓库结构/工作流/Issue 模板/社区文件/基础设施同步模型/Issue 分拣/运维指南 10 章）。

**Migration**: 合并 learning 08/conda-dev-source-wiki（conda 源码架构/核心模块/CLI 命令/网关插件/关键 API/典型场景/FAQ/最佳实践 10 章）。

## 2026-08-21

* **Creation**: 建立 Conda 知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 Conda v26.7.1（26.7.1-49-gad60271d8）源码核心模块（`__init__.py`, `cli/main.py`, `cli/conda_argparse.py`, `base/context.py`, `base/constants.py`, `common/configuration.py`, `common/logic.py`, `models/channel.py`, `models/match_spec.py`, `models/version.py`, `models/records.py`, `models/enums.py`, `models/prefix_graph.py`, `core/solve.py`, `core/index.py`, `core/subdir_data.py`, `core/link.py`, `core/prefix_data.py`, `core/package_cache_data.py`, `core/envs_manager.py`, `resolve.py`, `api.py`, `plugins/manager.py`, `plugins/hookspec.py`, `plugins/config.py`, `gateways/connection/session.py`, `gateways/subprocess.py`, `activate.py`, `pyproject.toml` 等），提取 80 条源码事实（F-001 ~ F-080），覆盖包入口/CLI入口/全局配置/数据模型/核心业务/SAT求解/高层API/插件系统/网关层/环境激活等全栈模块。
* **Add**: I阶段完成——提炼 5 个核心架构洞察（I-01 七层严格分层架构/I-02 双入口命令模型/I-03 MatchSpec一等公民查询语言/I-04 pluggy驱动插件体系/I-05 三层数据缓存与懒加载），设计知识地图（入门3篇→数据模型4篇→业务逻辑5篇→CLI/Shell3篇→高级3篇，共18概念+5示例+4信源）。
* **Add**: E阶段完成——concepts/ 下 18 个概念文档（00-introduction ~ 17-public-api），examples/ 下 5 个实战示例（basic-env-create/matchspec-queries/query-installed-packages/custom-solver-plugin/virtual-packages），references/ 下 4 个信源登记（cli-main/solver-init/subdir-data-api/plugin-hookspec），加上 3 个 index.md 导航文件和根 index.md、log.md。
* **Verify**: V阶段对抗审查完成——结构检查（32个文件：18概念+5示例+4信源+3子目录index+根index+log），frontmatter验证（所有文档含okf_version/type/title/sources字段），Grep级API真实性验证（Solver/SubdirData/Channel/MatchSpec/CondaPluginManager/CondaSession/UnlinkLinkTransaction/BaseSolver/PrefixData/PackageCacheData/VersionOrder/_Activator 共11个核心类全部在源码中验证存在），链接有效性检查（113个非代码块链接全部有效，修复14处file:///绝对路径违规为行内代码引用）。
* **Fix**: 修复5个概念文档（12-cli-commands/13-shell-activation/14-exceptions/15-plugin-system/16-gateways-io）中的14处`file:///`绝对路径markdown链接，统一改为`` `path#Lx-Ly` ``行内代码引用格式，符合项目Markdown交叉引用规范。
