# 源码信源索引

本目录登记 jupyterlab-github 扩展所有核心源码文件的 API 与行为细节。

## TypeScript 前端（4 个文件）

| 信源 | 文件 | 行数 | 核心内容 |
|------|------|------|---------|
| [插件入口](index-ts-source.md) | `src/index.ts` | ~171 | 插件注册、activateFileBrowser、设置系统、安全警告对话框 |
| [API 请求层](github-ts-source.md) | `src/github.ts` | ~259 | browserApiRequest、proxiedApiRequest、GitHub API 类型定义 |
| [GitHub Drive](contents-ts-source.md) | `src/contents.ts` | ~800 | GitHubDrive 类、Contents.IDrive 实现、路径解析、API 路由、只读模型 |
| [浏览器 UI](browser-ts-source.md) | `src/browser.ts` | ~396 | GitHubFileBrowser、GitHubUserInput、GitHubErrorPanel、MyBinder 集成 |

## Python 服务端（1 个文件）

| 信源 | 文件 | 行数 | 核心内容 |
|------|------|------|---------|
| [服务端扩展](init-py-source.md) | `jupyterlab_github/__init__.py` | ~168 | GitHubHandler（Tornado代理）、GitHubConfig、认证、分页、扩展注册 |

## 配置与 Schema

| 文件 | 说明 |
|------|------|
| `schema/drive.json` | JupyterLab 设置 Schema（baseUrl、accessToken、defaultRepo） |
| `jupyter-config/jupyter_server_config.d/jupyterlab_github.json` | Jupyter Server 扩展自动启用配置 |
| `jupyter-config/jupyter_notebook_config.d/jupyterlab_github.json` | 旧版 Notebook Server 扩展自动启用配置 |
| `package.json` | npm 包配置、JupyterLab 扩展元数据、依赖声明 |
| `pyproject.toml` | Python 包配置、Hatchling 构建、hatch-jupyter-builder 集成 |
