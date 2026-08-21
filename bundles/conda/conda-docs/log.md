# Bundle Update Log

## 2026-08-21

* **Creation**: 建立 conda-docs 知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——分析 conda-docs 仓库结构（`docs/source/conf.py`、`docs/source/index.rst`、`docs/source/user/`、`docs/source/developer/`、`docs/source/community/`、`.readthedocs.yml`、`Makefile`、`requirements.txt`、`README.md`、`CONTRIBUTING.md`、`LICENSE`），采集文档门户架构、Sphinx 构建配置、ReadTheDocs 多项目模式、扩展选型、重定向机制、双发行版策略、生态项目矩阵、贡献流程、社区渠道、许可证等关键事实。
* **Add**: I阶段完成——提炼核心架构洞察：(1) conda-docs 作为文档编排层不承载功能代码；(2) ReadTheDocs subprojects + reredirects 实现多项目聚合；(3) sphinx-design 卡片网格做导航枢纽；(4) "文档靠近代码"的组织原则；(5) Miniconda/Miniforge 双发行版策略。
* **Add**: E阶段完成——concepts/ 下 8 个概念文档（00-introduction ~ 07-license），examples/ 下 2 个实战示例（local-build/doc-portal-template），references/ 下 4 个信源登记（conf-py/index-rst/contributing-rst/help-support-rst），加上 3 个 index.md 导航文件和根 index.md、log.md。
* **Fix**: 统一所有文档 frontmatter 为 OKF v0.2 简洁格式（okf_version/type/title/sources 四字段），匹配现有 conda bundle 风格。
* **Verify**: V阶段独立验证完成——结构检查（17个文件：8概念+2示例+4信源+3子目录index+根index+log），frontmatter验证（所有内容文档含okf_version/type/title/sources字段，子目录index.md不含frontmatter），链接有效性检查（修复1处跨bundle相对路径错误、移除1处file:///绝对路径引用），内容合规检查（无file:///绝对路径）。
