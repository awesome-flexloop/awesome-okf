---
type: Index
title: References 索引
description: jupyter-renderers API 与配置参考文档索引
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# References 参考文档

| 文档 | 内容 | 信源 |
|------|------|------|
| [IRenderMime API 参考](rendermime-interfaces-api.md) | IRendererFactory、IRenderer、IExtension、IRendererOptions、IRendererFactoryOptions、IMimeModel 等核心接口定义 | @jupyterlab/rendermime-interfaces |
| [扩展配置参考](extension-config-reference.md) | package.json 中 mimeExtension/extension 配置、rank、safe、dataType、fileTypes、documentWidgetFactoryOptions、disabledExtensions 字段说明 | packages/*/package.json |
| [Python 入口点参考](python-entrypoint-reference.md) | _jupyter_labextension_paths 函数约定、labextension 目录结构、pyproject.toml 配置、MANIFEST.in 规范 | packages/*/pyproject.toml, packages/*/jupyterlab_*/__init__.py |

```{toctree}
:hidden:
:maxdepth: 7

extension-config-reference
python-entrypoint-reference
rendermime-interfaces-api
```
