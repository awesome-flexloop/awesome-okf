# 信源参考索引

本目录包含 repo2jupyterlite 各核心模块的源码信源登记，每个文件对应一个源码模块的 API 签名、行为和参数说明，作为概念文档和示例文档的事实溯源依据。

## 信源文件列表

| 信源文件 | 对应源码模块 | 说明 |
|---------|------------|------|
| [metasource.md](metasource.md) | setup.py + environment.yml + package.json + webpack.config.js | 项目元数据：版本、依赖、构建配置、目录结构 |
| [cli-source.md](cli-source.md) | repo2jupyterlite/app.py | CLI 入口：main()、fetch()、build() 函数 |
| [github-provider-source.md](github-provider-source.md) | repoproviders/github.py | GitHubRepoProvider：异步API请求、引用解析、缓存、认证 |
| [cache-source.md](cache-source.md) | repoproviders/utils.py | Cache 类：基于OrderedDict的LRU缓存（支持TTL） |
| [binderlite-run-source.md](binderlite-run-source.md) | binderlite/run.py | FastAPI 应用：路由、重定向、构建触发逻辑 |
| [publisher-source.md](publisher-source.md) | binderlite/publish.py | Publisher 抽象基类与 LocalFilesystemPublisher |
| [frontend-source.md](frontend-source.md) | src/App.jsx + src/detectors.js + webpack.config.js | 前端React应用、URL解析器、Webpack配置 |

```{toctree}
:hidden:
:maxdepth: 7

binderlite-run-source
cache-source
cli-source
frontend-source
github-provider-source
metasource
publisher-source
```
