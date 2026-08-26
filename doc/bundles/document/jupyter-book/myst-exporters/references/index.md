# myst-exporters 信源参考

本目录包含从源码直接提取的导出符号、API 清单和源码结构文档，用于验证概念文档的 API 真实性。

| 信源 | 说明 |
|------|------|
| [导出器入口导出表](exporter-entrypoints.md) | 各导出器包入口文件导出的公共 API（Plugin、Serializer、类型、工具函数）|
| [jtex 模板引擎源码](jtex-template-engine.md) | renderTemplate 函数、Nunjucks 配置、LaTeX/Typst imports 渲染 |
| [构建编排与导入器](build-orchestration.md) | myst-cli build 层多格式编排、jats-to-myst/tex-to-myst 入口 |

```{toctree}
:maxdepth: 7

build-orchestration
exporter-entrypoints
jtex-template-engine
```
