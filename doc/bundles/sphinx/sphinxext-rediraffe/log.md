# sphinxext-rediraffe Bundle 变更日志

## 2026-08-21 — 初始版本

- 基于 sphinxext-rediraffe 0.3.0 版本源码生成（源码路径：`external/libs/docs/sphinxext-rediraffe/`）
- 收录 8 个概念文档、4 个示例文档、1 个信源登记文档
- 覆盖内容：重定向图模型（create_graph/create_simple_redirects）、build-finished 钩子机制、双 Diff Builder（checkdiff/writediff）、Jinja2 模板系统、跨平台路径处理（PureWindowsPath/PurePosixPath）、4个配置项详解、Git diff 自动重定向写入
- 经 seven-concepts R→I→E→V 四阶段流程验证
- Grep级API验证：所有引用的函数名、配置项、Builder类均在 `sphinxext/rediraffe.py` 中确认存在
- 内部链接检查：67处交叉引用全部指向存在的文件
