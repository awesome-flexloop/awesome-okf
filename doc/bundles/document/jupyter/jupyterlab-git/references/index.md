# 源码信源索引

本目录包含 jupyterlab-git 核心源码文件的分析文档，作为 concepts/ 和 examples/ 中文档的信源引用基础。

## 前端源码（TypeScript/React）

| 信源文档 | 源文件 | 说明 |
|---------|--------|------|
| [插件入口](index-ts-source.md) | `src/index.ts` | 5个JupyterFrontEndPlugin定义、activate生命周期、Diff Provider注册 |
| [Token与类型定义](tokens-ts-source.md) | `src/tokens.ts` | IGitExtension接口、Git命名空间类型、CommandIDs枚举、所有数据接口定义 |
| [GitExtension核心模型](model-ts-source.md) | `src/model.ts` | GitExtension类实现、Poll轮询、TaskHandler、状态管理、Diff Provider注册表 |

## 后端源码（Python/Tornado）

| 信源文档 | 源文件 | 说明 |
|---------|--------|------|
| [Python Git执行引擎](git-py-source.md) | `packages/core/jupyterlab_git_core/git.py` | Git类封装、execute函数、subprocess/pexpect双模式、全局锁、nbdime集成 |
| [Tornado处理器](handlers-py-source.md) | `packages/jupyterlab/jupyterlab_git/handlers.py` | 所有/git/* REST API处理器、GitHandler基类、路由注册 |
| [服务端扩展入口](init-py-source.md) | `packages/jupyterlab/jupyterlab_git/__init__.py` | JupyterLabGit配置类、server extension加载、双包结构说明 |

## 快速参考

- **前端API契约**：以 `tokens.ts` 中的 `IGitExtension` 接口为准
- **后端API路由**：以 `handlers.py` 中的路由表为准
- **Git命令执行**：以 `git.py` 中的 `execute()` 和 `Git.__execute()` 为核心
- **扩展生命周期**：以 `index.ts` 的 `activate()` 函数为入口

```{toctree}
:maxdepth: 7

git-py-source
handlers-py-source
index-ts-source
init-py-source
model-ts-source
tokens-ts-source
```
