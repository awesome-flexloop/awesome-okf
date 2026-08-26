# 源码引用

各源文件的结构化引用文档，包含关键代码片段和接口定义。

| 引用文档 | 对应源文件 | 说明 |
|---------|-----------|------|
| [核心LSP包源码引用](core-plugin-source.md) | packages/lsp/src/{index,plugin,servers,session,tokens}.ts | 核心包的三插件、LanguageServers、Session、Token 定义 |
| [Monkey-patch 源码引用](hacks-source.md) | packages/lsp/src/hacks.ts + dodo.py (task_hack) | ServerConnection hack、MockWebSocket 挂载、构建时 WebSocket 替换 |
| [YAML语言服务器包源码引用](yaml-plugin-source.md) | packages/lsp-yaml/src/{index,plugin,server,tokens,worker}.ts | JSONLanguageServer、Worker 桥接、SPEC 定义 |
| [Python包源码引用](python-source.md) | src/jupyterlite_lsp/{__init__,constants,js}.py + pyproject.toml | Python 包入口、路径解析、flit 配置 |
| [构建系统源码引用](build-source.md) | dodo.py + package.json + lerna.json + .binder/environment.yml | doit 任务、构建脚本、开发环境依赖 |

```{toctree}
:maxdepth: 7

build-source
core-plugin-source
hacks-source
python-source
yaml-plugin-source
```
