# 源码信源索引

本目录包含 jupyter_releaser 核心模块的源码信源登记文档，为概念文档和示例文档提供溯源依据。

## 信源文件清单

| 文件 | 覆盖模块 | 行数 | 核心内容 |
|------|---------|------|---------|
| [cli-source.md](cli-source.md) | `jupyter_releaser/cli.py` | ~750 | ReleaseHelperGroup 命令组、19个CLI子命令、公共选项、装饰器工厂 |
| [lib-source.md](lib-source.md) | `jupyter_releaser/lib.py` | ~678 | 核心发布逻辑：版本提升、changelog草稿、资产上传、发布、git操作 |
| [util-source.md](util-source.md) | `jupyter_releaser/util.py` | ~753 | 工具基础设施：子进程执行、配置读取、GitHub API封装、版本管理、Mock服务 |
| [actions-source.md](actions-source.md) | `jupyter_releaser/actions/` | ~120 | Actions编排脚本：prep_release、populate_release、finalize_release |

## 其他重要模块（未单独建信源文档，在概念文档中引用）

| 模块 | 位置 | 行数 | 核心内容 |
|------|------|------|---------|
| `changelog.py` | `jupyter_releaser/changelog.py` | ~465 | Changelog标记系统、PR活动生成、backport处理、占位符管理 |
| `python.py` | `jupyter_releaser/python.py` | ~197 | Python分发包构建、检查、PyPI上传、Trusted Publishing、本地PyPI服务器 |
| `npm.py` | `jupyter_releaser/npm.py` | ~244 | npm包构建、检查、发布、workspace支持、.npmrc配置 |
| `tee.py` | `jupyter_releaser/tee.py` | ~162 | 异步tee子进程输出捕获（subprocess-tee修改版） |
| `mock_github.py` | `jupyter_releaser/mock_github.py` | ~276 | FastAPI Mock GitHub API服务器（dry-run模式使用） |
| `schema.json` | `jupyter_releaser/schema.json` | ~49 | 配置文件JSON Schema（skip/options/hooks） |

```{toctree}
:maxdepth: 7

actions-source
cli-source
lib-source
util-source
```
