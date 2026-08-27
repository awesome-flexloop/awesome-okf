# sphinx-demo 信源参考

本文档目录包含 JupyterLite Sphinx Demo 源码学习的信源登记文件，每个文件对应源码中一个核心配置层的完整字段速查。

## 信源文档列表

| 文档 | 对应源码 | 核心内容 |
|------|----------|----------|
| [conf.py配置项速查](conf-py-source.md) | `pyodide-kernel-example/docs/source/conf.py` | 所有配置项类型/默认值/取值说明，含扩展列表、JupyterLite配置、TryExamples配置、主题选项 |
| [JSON配置文件字段速查](json-config-source.md) | `jupyter-lite.json`, `jupyter_lite_config.json`, `overrides.json`, `try_examples.json` | 四个JSON文件的完整字段登记、作用阶段、修改后是否需要重建、四层对比表 |
| [GitHub Actions工作流解析](ci-workflow-source.md) | `.github/workflows/pages.yml` | 触发条件、环境变量、并发控制、矩阵策略、构建步骤、部署权限、站点结构 |

## 信源说明

所有信源基于 sphinx-demo 仓库主分支代码分析，对应 jupyterlite-sphinx 扩展的标准集成模式。Pyodide 和 Xeus 两个示例的配置差异在各信源文档中已标注。

## 相关信源

- 扩展实现源码参考：见 [jupyterlite-sphinx bundle](../../jupyterlite-sphinx/index.md)（同目录下）
- JupyterLite 核心参考：见 [jupyterlite bundle](../../jupyterlite/index.md)

```{toctree}
:hidden:
:maxdepth: 7

ci-workflow-source
conf-py-source
json-config-source
```
