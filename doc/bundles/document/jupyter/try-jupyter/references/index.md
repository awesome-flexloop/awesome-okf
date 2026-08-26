# 信源索引

本目录登记 try-jupyter 项目各核心模块的源码信源，所有概念文档中的API描述均可追溯到此处。

## 信源清单

| 信源 | 文件 | 覆盖范围 |
|------|------|---------|
| [pyproject.toml 项目配置](pyproject-source.md) | `pyproject.toml` | 项目元数据、pixi工作区、6个构建任务、完整依赖清单（30+包）、pytest配置 |
| [JupyterLite配置文件](config-source.md) | `jupyter-lite.json`、`jupyter_lite_config.json`、`cockle-config-in.json`、`repl/jupyter-lite.json` | 站点配置、构建配置、终端配置、REPL模式配置 |
| [构建后处理脚本](scripts-source.md) | `scripts/add_plausible.py`、`scripts/filter_xeus_kernels.py` | Plausible分析注入、Xeus内核过滤 |
| [UI测试框架](test-source.md) | `ui-tests/conftest.py`、`ui-tests/test_notebooks.py`、`ui-tests/utils.py` | Pytest fixtures、Playwright自动化、notebook参数化测试、错误检测逻辑 |
| [CI/CD工作流](ci-source.md) | `.github/workflows/deploy.yml`、`.github/workflows/rtd-preview.yml`、`.readthedocs.yml` | GitHub Pages部署流水线、RTD PR预览、ReadTheDocs构建 |

```{toctree}
:maxdepth: 7

ci-source
config-source
pyproject-source
scripts-source
test-source
```
