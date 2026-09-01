---
type: Example
title: "创建自定义数据科学镜像"
description: "从零开始使用cookiecutter创建一个基于scipy-notebook的自定义数据科学镜像，安装额外包、添加配置、编写测试"
tags: [example, custom-image, scipy, dockerfile, getting-started]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-files, resource: "/references/template-files.md", title: "模板文件源码索引" }
  - { id: src-tests, resource: "/references/tests-source.md", title: "测试框架源码索引" }
---

# 创建自定义数据科学镜像

本示例演示如何使用 cookiecutter-docker-stacks 创建一个基于 scipy-notebook 的自定义数据科学镜像，添加 Polars、DuckDB、XGBoost 等额外包，并编写测试验证。

## 完整流程

### 步骤1：生成项目

```bash
pip install cookiecutter
cookiecutter https://github.com/jupyter/cookiecutter-docker-stacks \
  --config-file configs/scipy.yaml \
  --no-input
```

如果使用交互式模式：
- stack_name: `my-datascience-stack`
- stack_org: `myusername`
- stack_base_image: 选择 `quay.io/jupyter/scipy-notebook`（编号4）
- stack_description: 回车使用默认值

### 步骤2：编写 Dockerfile

编辑 `my-datascience-stack/image/Dockerfile`：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:latest

LABEL maintainer="Your Name <your@email.com>"
LABEL description="Custom data science stack with Polars, DuckDB, and ML tools"

# 安装额外的Python数据科学包（以jovyan用户安装）
RUN pip install --no-cache-dir \
    'polars>=1.0' \
    'duckdb>=1.0' \
    'seaborn' \
    'xgboost' \
    'lightgbm' \
    'optuna' \
    'shap' \
    'plotly' \
    'statsmodels'

# 切换到root安装系统工具
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        vim \
        htop \
        tree \
        jq \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 切回非特权用户
USER ${NB_UID}
```

### 步骤3：添加自定义测试

创建 `my-datascience-stack/tests/test_packages.py`：

```python
"""测试额外安装的包是否可用"""
import pytest
from tests.utils.tracked_container import TrackedContainer


def test_polars_importable(container: TrackedContainer):
    """验证Polars可以导入"""
    container.run_detached()
    output = container.exec_cmd("python -c 'import polars; print(polars.__version__)'")
    assert output.strip() != ""
    assert "." in output.strip()


def test_duckdb_importable(container: TrackedContainer):
    """验证DuckDB可以导入"""
    container.run_detached()
    output = container.exec_cmd("python -c 'import duckdb; print(duckdb.__version__)'")
    assert output.strip() != ""


def test_xgboost_importable(container: TrackedContainer):
    """验证XGBoost可以导入"""
    container.run_detached()
    output = container.exec_cmd("python -c 'import xgboost; print(xgboost.__version__)'")
    assert output.strip() != ""


def test_runs_as_non_root(container: TrackedContainer):
    """验证容器以非root用户运行"""
    container.run_detached()
    uid = container.exec_cmd("id -u").strip()
    assert uid == "1000", f"Expected UID 1000 (jovyan), got {uid}"


def test_system_tools_available(container: TrackedContainer):
    """验证安装的系统工具可用"""
    container.run_detached()
    for tool in ["vim", "htop", "jq"]:
        output = container.exec_cmd(f"which {tool}")
        assert output.strip() != "", f"Tool '{tool}' not found"
```

### 步骤4：构建并测试

```bash
cd my-datascience-stack

# 安装测试依赖
pip install -r requirements-dev.txt

# 构建镜像
docker build --rm --force-rm -t myusername/my-datascience-stack image/

# 运行所有测试
TEST_IMAGE=myusername/my-datascience-stack pytest tests/ -v
```

预期输出：

```
collected 6 items

tests/test_notebook.py::test_secured_server PASSED
tests/test_packages.py::test_polars_importable PASSED
tests/test_packages.py::test_duckdb_importable PASSED
tests/test_packages.py::test_xgboost_importable PASSED
tests/test_packages.py::test_runs_as_non_root PASSED
tests/test_packages.py::test_system_tools_available PASSED
```

### 步骤5：运行容器

```bash
docker run -it --rm -p 8888:8888 \
    -v "${PWD}":/home/jovyan/work \
    myusername/my-datascience-stack
```

在浏览器中打开带token的URL，即可使用包含额外包的JupyterLab环境。

### 步骤6：验证包安装

在Jupyter Notebook中运行：

```python
import polars as pl
import duckdb
import xgboost as xgb
import shap
import plotly.express as px

print(f"Polars: {pl.__version__}")
print(f"DuckDB: {duckdb.__version__}")
print(f"XGBoost: {xgb.__version__}")
print(f"SHAP: {shap.__version__}")
```

## 关键要点总结

1. **Python包以jovyan安装**：不需要USER root，直接在FROM后RUN pip install
2. **系统包切换root**：安装后必须切回USER ${NB_UID}
3. **清理apt缓存**：`apt-get clean && rm -rf /var/lib/apt/lists/*`
4. **编写测试验证每个额外包**：确保镜像构建正确
5. **挂载工作目录**：使用 `-v` 将主机目录挂载到 `/home/jovyan/work`

## 相关示例

- [GPU/CUDA深度学习镜像](02-gpu-image.md)
- [高级测试编写](03-advanced-testing.md)

## 相关概念

- [Dockerfile模板与编写指南](../concepts/04-dockerfile-template.md)
- [测试框架详解](../concepts/05-testing-framework.md)
- [最佳实践](../concepts/09-best-practices.md)
