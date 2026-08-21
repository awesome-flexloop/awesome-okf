---
title: 常用配方集锦
id: ex-05-recipes
version: 0.2.0
okf-spec: v0.2
bundle: jupyter-docker-stacks
category: examples
tags: [recipes, cookbook, dockerfile, ssl, dask, spark, hooks]
sources:
  - references/startup-scripts.md
  - references/dockerfiles.md
prerequisites:
  - concepts/08-hooks-and-customization.md
  - concepts/09-user-permissions.md
  - examples/02-custom-image.md
difficulty: intermediate
estimated-time: 25min
---

# 常用配方集锦

本示例收集了社区贡献的实用 Dockerfile 配方和运行配置，涵盖 SSL、Dask、Spark、自定义环境、数据库连接等常见场景。

## 配方 1：启用 Sudo 权限

需要在容器内安装系统包时：

```bash
docker run -it --rm \
    --user root \
    -e GRANT_SUDO=yes \
    -p 8888:8888 \
    quay.io/jupyter/base-notebook:2026-07-28
```

Dockerfile 方式：

```dockerfile
FROM quay.io/jupyter/base-notebook:2026-07-28

USER root
RUN echo "jovyan ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/jovyan && \
    chmod 0440 /etc/sudoers.d/jovyan
USER ${NB_UID}
```

:::{warning}
仅在可信用户或隔离环境中启用 sudo！公网暴露的容器绝不要开启 sudo。
:::

## 配方 2：添加自定义 Conda 环境 + Kernel

需要不同 Python 版本或隔离的依赖环境：

```dockerfile
FROM quay.io/jupyter/base-notebook:2026-07-28

USER ${NB_UID}

# 创建 Python 3.11 环境并安装 ipykernel
RUN mamba create --yes -p "${CONDA_DIR}/envs/python311" \
    python=3.11 \
    ipykernel \
    ipywidgets && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}"

# 注册为 Jupyter 内核
RUN "${CONDA_DIR}/envs/python311/bin/python" -m ipykernel install \
    --user --name python311 --display-name "Python 3.11" && \
    fix-permissions "/home/${NB_USER}"

# 在新环境中安装包
RUN "${CONDA_DIR}/envs/python311/bin/pip" install --no-cache-dir \
    tensorflow==2.15 && \
    fix-permissions "${CONDA_DIR}"
```

## 配方 3：Dask JupyterLab 扩展

分布式计算环境配置：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

USER ${NB_UID}

# 安装 Dask 和 Dask Lab Extension
RUN mamba install --yes \
    'dask' \
    'distributed' \
    'dask-labextension' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

运行时启动 Dask 集群：

```bash
docker run -it --rm \
    -p 8888:8888 \
    -p 8787:8787 \
    my-dask-image
```

在 Notebook 中使用：

```python
from dask.distributed import Client
client = Client()  # 启动本地 Dask 集群
client  # 点击 Dashboard 链接查看 Dask 监控面板
```

## 配方 4：HTTPS/SSL 配置

### 方式 A：自动生成自签名证书

```bash
docker run -it --rm \
    -p 8888:8888 \
    -e GEN_CERT=yes \
    quay.io/jupyter/base-notebook:2026-07-28
```

### 方式 B：挂载自有证书

```bash
docker run -it --rm \
    -p 8888:8888 \
    -v /path/to/certs:/etc/ssl/notebook \
    quay.io/jupyter/base-notebook:2026-07-28 \
    start-notebook.py \
    --ServerApp.keyfile=/etc/ssl/notebook/notebook.key \
    --ServerApp.certfile=/etc/ssl/notebook/notebook.crt
```

### 方式 C：使用 PEM 文件（证书+密钥合并）

```bash
docker run -it --rm \
    -p 8888:8888 \
    -v /path/to/notebook.pem:/etc/ssl/notebook.pem \
    quay.io/jupyter/base-notebook:2026-07-28 \
    start-notebook.py \
    --ServerApp.certfile=/etc/ssl/notebook.pem
```

## 配方 5：RISE 幻灯片扩展

JupyterLab 中使用 Reveal.js 做演示：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

USER ${NB_UID}

# 安装 RISE 扩展
RUN pip install --no-cache-dir \
    'rise' && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

## 配方 6：Microsoft SQL Server ODBC 驱动

连接 SQL Server 数据库：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

USER root

# 安装 Microsoft ODBC Driver for SQL Server
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    gnupg2 \
    curl \
    unixodbc-dev \
    unixodbc && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/24.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update --yes && \
    ACCEPT_EULA=Y apt-get install --yes --no-install-recommends msodbcsql18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

RUN pip install --no-cache-dir \
    'pyodbc' \
    'sqlalchemy' && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

使用：

```python
import pyodbc
import sqlalchemy

conn_str = "mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+18+for+SQL+Server"
engine = sqlalchemy.create_engine(conn_str)
```

## 配方 7：Oracle Database 连接

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

USER root

# 安装 Oracle Instant Client
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    libaio1 \
    wget \
    unzip && \
    wget -q https://download.oracle.com/otn_software/linux/instantclient/2360000/instantclient-basic-linux.x64-23.6.0.24.10.zip -O /tmp/instantclient.zip && \
    unzip /tmp/instantclient.zip -d /opt/oracle && \
    echo "/opt/oracle/instantclient_23_6" > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig && \
    rm /tmp/instantclient.zip && \
    apt-get purge -y wget unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

RUN pip install --no-cache-dir \
    'oracledb' && \
    fix-permissions "${CONDA_DIR}"
```

## 配方 8：XGBoost 机器学习库

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

USER ${NB_UID}

RUN mamba install --yes \
    'xgboost' \
    'lightgbm' \
    'catboost' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

## 配方 9：使用 Startup Hooks 进行初始化

### 启动前 Hook（start-notebook.d）

创建 `hooks/setup-env.sh`：

```bash
#!/bin/bash
# 在用户配置处理之前执行
# 适合设置环境变量、创建目录等
export MY_PROJECT_HOME=/home/jovyan/my-project
mkdir -p "${MY_PROJECT_HOME}/data"
mkdir -p "${MY_PROJECT_HOME}/models"
echo "Setup hook executed: MY_PROJECT_HOME=${MY_PROJECT_HOME}"
```

### 启动前最后 Hook（before-notebook.d）

创建 `hooks/install-extra.sh`：

```bash
#!/bin/bash
# 在 Jupyter 启动前执行
# 适合安装运行时依赖、启动额外服务
if [ -f "/home/jovyan/work/requirements.txt" ]; then
    echo "Installing requirements from mounted volume..."
    pip install --no-cache-dir -r /home/jovyan/work/requirements.txt
fi
```

Dockerfile 中添加 hooks：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

COPY hooks/setup-env.sh /usr/local/bin/start-notebook.d/
COPY hooks/install-extra.sh /usr/local/bin/before-notebook.d/
USER root
RUN chmod +x /usr/local/bin/start-notebook.d/*.sh \
    /usr/local/bin/before-notebook.d/*.sh
USER ${NB_UID}
```

## 配方 10：自定义用户名和 UID/GID

### 运行时指定（挂载主机目录时很有用）

```bash
docker run -it --rm \
    -p 8888:8888 \
    --user root \
    -e NB_USER="data-scientist" \
    -e NB_UID=$(id -u) \
    -e NB_GID=$(id -g) \
    -e CHOWN_HOME=yes \
    -v "${PWD}":/home/data-scientist/work \
    quay.io/jupyter/scipy-notebook:2026-07-28
```

### Docker 原生方式（推荐）

```bash
docker run -it --rm \
    -p 8888:8888 \
    --user $(id -u):$(id -g) \
    --group-add users \
    -v "${PWD}":/home/jovyan/work \
    quay.io/jupyter/scipy-notebook:2026-07-28
```

## 配方 11：运行非 Jupyter 命令

### IPython 终端

```bash
docker run -it --rm quay.io/jupyter/base-notebook:2026-07-28 ipython
```

### Jupyter Console

```bash
docker run -it --rm quay.io/jupyter/base-notebook:2026-07-28 jupyter console
```

### Bash Shell

```bash
docker run -it --rm quay.io/jupyter/base-notebook:2026-07-28 bash
```

### 自定义 Python 脚本

```bash
docker run -it --rm \
    -v "${PWD}/script.py":/home/jovyan/script.py \
    quay.io/jupyter/base-notebook:2026-07-28 \
    python /home/jovyan/script.py
```

## 配方 12：JupyterHub 单用户镜像

JupyterHub 中使用自定义镜像：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

# 安装 JupyterHub 单用户所需包
USER root
RUN pip install --no-cache-dir \
    jupyterhub==4.* && \
    fix-permissions "${CONDA_DIR}"

USER ${NB_UID}

# 使用 start-singleuser.py 而非 start-notebook.py
# JupyterHub 会自动调用正确的命令
```

指定 JupyterHub 版本：

```dockerfile
FROM quay.io/jupyter/base-notebook:2026-07-28

USER ${NB_UID}

# 安装与 JupyterHub 版本匹配的包
ARG JUPYTERHUB_VERSION=4.1.0
RUN pip install --no-cache-dir \
    jupyterhub==${JUPYTERHUB_VERSION} && \
    fix-permissions "${CONDA_DIR}"
```

## 配方 13：IJavascript JavaScript 内核

```dockerfile
FROM quay.io/jupyter/minimal-notebook:2026-07-28

USER root

# 安装 Node.js 和 IJavascript 依赖
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    nodejs \
    npm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# 安装 IJavascript 内核
RUN npm install -g ijavascript && \
    ijsinstall --spec-path=full && \
    fix-permissions "/home/${NB_USER}"
```

## 配方 14：Spark + Delta Lake

```dockerfile
FROM quay.io/jupyter/pyspark-notebook:2026-07-28

USER ${NB_UID}

# 安装 Delta Lake
RUN mamba install --yes 'delta-spark' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

USER root

# 配置 Spark 默认使用 Delta Lake
RUN cat <<EOF >> "${SPARK_HOME}/conf/spark-defaults.conf"
spark.sql.extensions io.delta.sql.DeltaSparkSessionExtension
spark.sql.catalog.spark_catalog org.apache.spark.sql.delta.catalog.DeltaCatalog
EOF

USER ${NB_UID}
```

## 配方 15：Singularity/Apptainer 运行

HPC 环境常用 Singularity：

```bash
# 基本运行
singularity run \
    --bind "${PWD}:/home/${USER}/work" \
    --containall \
    docker://quay.io/jupyter/datascience-notebook:2026-07-28

# 指定端口
singularity run \
    --bind "${PWD}:/home/${USER}/work" \
    --containall \
    docker://quay.io/jupyter/scipy-notebook:2026-07-28 \
    start-notebook.py --port=8888
```

:::{note}
Singularity 使用主机用户名而非 `jovyan`，所以 bind 路径是 `/home/$USER/work`。使用 `--containall` 避免与主机 Python 环境冲突。
:::

## 配方 16：Docker Compose 完整开发环境

```yaml
# docker-compose.yml
version: '3.8'

services:
  jupyter:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
      - ./data:/home/jovyan/data
    environment:
      - JUPYTER_TOKEN=my-dev-token
      - DOCKER_STACKS_JUPYTER_CMD=lab
      - GRANT_SUDO=yes  # 仅开发环境
    user: root
    restart: unless-stopped

  # 可选：添加 Postgres 数据库服务
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: mysecretpassword
      POSTGRES_USER: jovyan
      POSTGRES_DB: analysis
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## 配方 17：添加 Man Pages（调试用）

默认镜像精简了 man pages，需要时：

```dockerfile
FROM quay.io/jupyter/base-notebook:2026-07-28

USER root

# 重新安装 man pages
RUN sed -i 's/path-exclude=\/usr\/share\/man\/*//' /etc/dpkg/dpkg.cfg.d/excludes && \
    apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    man-db \
    manpages && \
    yes | unminimize && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}
```

## 配方速查表

| 场景 | Dockerfile/命令要点 |
|------|---------------------|
| 安装 pip 包 | `RUN pip install --no-cache-dir <pkg> && fix-permissions` |
| 安装 conda 包 | `RUN mamba install --yes <pkg> && mamba clean && fix-permissions` |
| 安装系统包 | `USER root; RUN apt-get install && apt-get clean` |
| 挂载工作目录 | `-v "${PWD}":/home/jovyan/work` |
| 启用 sudo | `--user root -e GRANT_SUDO=yes` |
| 自定义用户 | `-e NB_USER=xxx -e NB_UID=xxx --user root -e CHOWN_HOME=yes` |
| 禁用 token | `start-notebook.py --IdentityProvider.token=''` |
| 切换前端 | `-e DOCKER_STACKS_JUPYTER_CMD=notebook/nbclassic/server` |
| HTTPS | `-e GEN_CERT=yes` 或挂载证书 |
| 运行 hook | 放脚本到 `/usr/local/bin/start-notebook.d/` |
| GPU 支持 | `--gpus all` + `cuda-`/`cuda12-`/`cuda13-` 前缀镜像 |
| JupyterHub | 安装 jupyterhub 包，使用 start-singleuser 命令 |

## 配方验证方法

每个 Dockerfile 配方构建后，建议进行以下验证：

```bash
# 1. 构建镜像
docker build --rm -t test-recipe .

# 2. 导入测试
docker run --rm test-recipe python -c "import <package>; print('<package> OK')"

# 3. Jupyter 启动测试
docker run -d --name test-jupyter -p 8888:8888 test-recipe
sleep 8
curl -s http://localhost:8888/api | grep -q "version" && echo "Jupyter OK" || echo "Jupyter FAILED"
docker stop test-jupyter && docker rm test-jupyter

# 4. 用户权限测试
docker run --rm test-recipe bash -c "touch /home/jovyan/test.txt && echo 'Permission OK'"
```

## 反模式警示

以下做法应**避免**：

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| `RUN sudo apt-get install` | 不需要 sudo，用 `USER root` 切换 | 先 `USER root` 再安装 |
| `pip install` 不清理缓存 | 镜像体积膨胀 | 使用 `--no-cache-dir` |
| 以 root 用户运行 Jupyter | 安全风险 | 用 `${NB_UID}` 用户运行 |
| 使用 `conda install` | 比 mamba 慢很多 | 使用 `mamba install` |
| 使用 `latest` 标签 | 不可复现 | 使用日期标签如 `2026-07-28` |
| COPY 不加 `--chown` | 文件权限问题 | 使用 `COPY --chown=${NB_UID}:${NB_GID}` |

## 参考资源

- 官方 Recipes 文档：<https://jupyter-docker-stacks.readthedocs.io/en/latest/using/recipes.html>
- 官方 recipe_code 目录：<https://github.com/jupyter/docker-stacks/tree/main/docs/using/recipe_code>
- 社区 Stacks 列表：参考 [selecting.md](../concepts/02-image-hierarchy.md) 中的社区镜像
