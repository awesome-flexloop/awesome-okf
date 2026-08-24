# 信源登记簿（References）

本目录记录 jupyterlab-demo OKF Wiki 教程中所有引用的源码信源，用于溯源验证。

## 信源清单

| 信源文件 | 对应源码 | 说明 |
|---------|---------|------|
| [repo-readme.md](repo-readme.md) | README.md | 仓库说明、安装指南、外部仓库许可证 |
| [build-py-source.md](build-py-source.md) | build.py | 构建脚本：setup_demofiles、setup_talks 函数 |
| [binder-config-source.md](binder-config-source.md) | .binder/*.{yml,json,sh} | Binder环境配置三要素 |
| [talks-yml-source.md](talks-yml-source.md) | talks.yml | 四种演讲场景的文件配置 |
| [narrative-source.md](narrative-source.md) | narrative/*.md | 四份演示脚本内容 |
| [ci-workflow-source.md](ci-workflow-source.md) | .github/workflows/*.yml, jupyter_notebook_config.py | CI工作流与Jupyter配置 |

```{toctree}
:hidden:

binder-config-source
build-py-source
ci-workflow-source
narrative-source
repo-readme
talks-yml-source
```
