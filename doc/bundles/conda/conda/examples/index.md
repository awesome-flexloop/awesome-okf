# 实战示例

本目录包含 5 个完整的可运行 Python 示例，每个示例对应一个或多个核心概念，提供从简单到复杂的渐进式学习路径。

* [程序化创建 Conda 环境](basic-env-create.md) — 使用 conda.api.Solver 初始化→solve_for_transaction()→UnlinkLinkTransaction 执行，实现完整的环境创建流程。对应概念：[Solver 求解器与 SAT 算法](../concepts/09-solver-and-resolve.md)、[公开 Python API](../concepts/17-public-api.md)。
* [MatchSpec 查询示例](matchspec-queries.md) — 7 种 MatchSpec 构造方式、版本约束语法、SubdirData 查询、6 种常见查询场景。对应概念：[MatchSpec 包查询语言](../concepts/04-matchspec.md)、[Channel 与 Subdir](../concepts/03-channel-subdir.md)。
* [查询已安装包和包缓存](query-installed-packages.md) — PrefixData 查询环境包、PackageCacheData 浏览本地缓存、SubdirData.query_all() 全通道搜索、三级记录对比。对应概念：[三级包记录模型](../concepts/06-package-records.md)、[Index 与 Repodata](../concepts/08-index-and-repodata.md)、[公开 Python API](../concepts/17-public-api.md)。
* [自定义求解器插件](custom-solver-plugin.md) — 继承 classic Solver 实现 LoggingSolver、@plugins.hookimpl 注册 conda_solvers 钩子、pyproject.toml 入口点配置。对应概念：[插件系统](../concepts/15-plugin-system.md)、[Solver 求解器与 SAT 算法](../concepts/09-solver-and-resolve.md)。
* [虚拟包检测与使用](virtual-packages.md) — 9 种内置虚拟包（__cuda/__glibc/__archspec 等）详解、环境变量覆盖机制、PackageRecord.virtual_package() 工厂方法、自定义虚拟包插件。对应概念：[三级包记录模型](../concepts/06-package-records.md)、[插件系统](../concepts/15-plugin-system.md)。
