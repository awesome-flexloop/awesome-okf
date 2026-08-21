# Bundle Update Log

## 2026-08-21

* **Creation**: 建立 sphinxcontrib-websupport 知识包脚手架（concepts/examples/references 三目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 sphinxcontrib-websupport v2.0.0 源码核心模块（`__init__.py`, `core.py`, `builder.py`, `errors.py`, `storage/__init__.py`, `storage/sqlalchemystorage.py`, `storage/sqlalchemy_db.py`, `storage/differ.py`, `search/__init__.py`, `search/nullsearch.py`, `search/whooshsearch.py`, `search/xapiansearch.py`(可选), `tests/test_websupport.py`, `pyproject.toml`），提取核心源码事实，覆盖包入口/WebSupport API/Builder 系统/存储后端/搜索适配器/评论系统/物化路径/前端集成等模块。
* **Add**: I阶段完成——提炼 5 个核心架构洞察（双阶段构建/运行架构/StorageBackend 可插拔抽象/物化路径评论树/Builder 节点标注机制/搜索适配器注册表），设计知识地图（入门3篇→核心API 2篇→评论存储3篇→前端扩展2篇，共10概念+4示例+1信源）。
* **Add**: E阶段完成——concepts/ 下 10 个概念文档（00-introduction ~ 09-search-adapters），examples/ 下 4 个实战示例（basic-build-and-serve/flask-integration/custom-storage-backend/comment-moderation-workflow），references/ 下 1 个信源登记（websupport-source），加上 3 个 index.md 导航文件和根 index.md、log.md。
* **Fix**: 修复 10 个概念文档中的绝对路径链接（`/concepts/...`、`/examples/...`、`/references/...`），统一改为 Markdown 相对路径格式（同目录直接文件名、跨目录使用`../`前缀）；修复概念文档 frontmatter 的 type 字段大小写不一致问题（`Concept`→`"concept"`），补充缺失的 `okf_version: "0.2"` 字段；为 concepts/index.md 和 examples/index.md 添加 YAML frontmatter。
* **Verify**: V阶段对抗审查完成——结构检查（20个文件：10概念+4示例+1信源+3子目录index+根index+log），frontmatter验证（所有15个内容文档含okf_version/type/title/sources字段），Grep级API真实性验证（WebSupport/WebSupportBuilder/StorageBackend/SQLAlchemyStorage/BaseSearch/NullSearch/WhooshSearch/CombinedHtmlDiff/DocumentNotFoundError/UserNotAuthorizedError/CommentNotAllowedError/SEARCH_ADAPTERS共12个核心类/常量全部在源码中验证存在），链接有效性检查（93个Markdown链接全部有效，0个file:///绝对路径违规）。
