---
type: Concept
title: "专项镜像详解"
description: "R/Julia/PyTorch/TensorFlow/PySpark/All-Spark/DataScience七个专项镜像的构成与区别"
tags: [r-notebook, julia-notebook, pytorch, tensorflow, pyspark, datascience, all-spark, cuda, gpu]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-dockerfiles, resource: "/references/dockerfiles.md", title: "专项镜像Dockerfile" }
---

# 专项镜像详解

scipy-notebook 之上的镜像（L4a/L4b/L5/L6）针对特定语言或计算框架进行扩展。本章逐一介绍七个专项镜像。

## r-notebook（R语言统计分析）

**基础镜像**：minimal-notebook（注意：不是scipy-notebook！）

**OS依赖**：
```
fonts-dejavu, unixodbc, unixodbc-dev, r-cran-rodbc, gfortran, gcc
```

**R包**（通过mamba安装）：
- 核心：r-base, r-irkernel（Jupyter R内核）
- 数据科学：r-tidyverse, r-tidymodels, r-caret, r-randomforest, r-e1071, r-forecast
- 可视化：r-ggplot2(在all-spark中), r-htmlwidgets, r-hexbin
- 文档：r-rmarkdown
- 数据库：r-rodbc, r-rsqlite, RODBC
- Web：r-shiny, r-htmltools
- 网络：r-rcurl
- 数据：r-nycflights13
- 工具：r-crayon, r-devtools

> **关键设计**：r-notebook基于minimal-notebook而非scipy-notebook，使其成为一个**轻量级R镜像**——不包含Python科学计算栈。如果需要Python+R，使用datascience-notebook。

## julia-notebook（Julia科学计算）

**基础镜像**：minimal-notebook

**安装方式**：通过setup-scripts脚本安装（不是conda包）：
1. `/opt/setup-scripts/setup_julia.py`：下载并安装Julia到系统
2. `/opt/setup-scripts/setup-julia-packages.bash`：安装IJulia kernel和常用包

**环境变量**：
```
JULIA_DEPOT_PATH=/opt/julia
JULIA_PKGDIR=/opt/julia
```

Julia包安装在`/opt/julia`（系统级目录），而非用户home目录，所有用户共享。

## datascience-notebook（三语言全栈）

**基础镜像**：scipy-notebook

这是功能最全的镜像，在Python科学计算栈基础上**同时安装R和Julia**：
- R包（同r-notebook但增加了rpy2）
- Julia（通过相同的setup-scripts安装）
- rpy2：Python-R互操作桥接包

datascience-notebook包含了scipy-notebook的所有Python包 + R包 + Julia包，是"一站式"数据科学环境。

## pytorch-notebook（PyTorch深度学习）

**基础镜像**：scipy-notebook

**安装方式**：通过pip（不是conda/mamba）安装：
```dockerfile
RUN pip install -v --no-cache-dir --index-url 'https://download.pytorch.org/whl/cpu' \
    'torch' 'torchaudio' 'torchvision'
```

关键设计点：
1. **pip安装而非conda**：PyTorch官方推荐pip安装方式，可以精确控制CUDA/CPU版本
2. **CPU版默认**：默认镜像从`/whl/cpu`索引安装CPU版PyTorch
3. **独立CUDA变体**：`cuda12/`和`cuda13/`子目录提供GPU版本
4. **详细输出**：`-v`标志输出详细安装日志便于调试

### CUDA变体

| 变体 | 目录 | 说明 |
|------|------|------|
| CUDA 12 | images/pytorch-notebook/cuda12/ | NVIDIA CUDA 12.x + PyTorch with CUDA |
| CUDA 13 | images/pytorch-notebook/cuda13/ | NVIDIA CUDA 13.x + PyTorch with CUDA |

运行GPU镜像需要：
- 主机安装NVIDIA驱动
- Docker安装[nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- 使用`--gpus all`参数运行

```bash
docker run --gpus all -p 8888:8888 quay.io/jupyter/pytorch-notebook:cuda12-2026-07-28
```

## tensorflow-notebook（TensorFlow深度学习）

**基础镜像**：scipy-notebook

**额外安装**：
1. Conda包：jupyter-server-proxy, protobuf>=5.28.3,<6
2. pip包：tensorflow（aarch64）或tensorflow-cpu（x86_64）

```dockerfile
RUN if [ "$(uname -m)" = "x86_64" ]; then \
        TF_POSTFIX="-cpu"; \
    else \
        TF_POSTFIX=""; \
    fi && \
    pip install -v --no-cache-dir "tensorflow${TF_POSTFIX}"
```

**架构差异**：
- x86_64：安装`tensorflow-cpu`（TensorFlow官方将CPU版单独打包）
- aarch64：安装`tensorflow`（ARM版TensorFlow包含CPU支持）

**CUDA变体**：`cuda/`子目录提供GPU版本，包含tensorboard-proxy环境配置脚本（`20tensorboard-proxy-env.sh`，作为before-notebook.d hook安装）。

> **protobuf版本固定**：TensorFlow 2.20对protobuf版本敏感，需要>=5.28.3且<6以避免用户警告。

## pyspark-notebook（Apache Spark大数据处理）

**基础镜像**：scipy-notebook

**OS依赖**：
- openjdk-21-jre-headless（Java 21运行时）
- ca-certificates-java

**构建参数**：

| 参数 | 默认值 | 说明 |
|------|-------|------|
| openjdk_version | 21 | OpenJDK版本 |
| spark_version | (latest) | Spark版本（默认最新） |
| hadoop_version | 3 | Hadoop版本 |
| scala_version | (无) | Scala版本（不设则Spark不带Scala） |
| spark_download_url | https://dlcdn.apache.org/spark/ | Spark下载镜像 |
| derby_version | 10.17.1.0 | Derby数据库版本 |

**安装方式**：通过`/opt/setup-scripts/setup_spark.py`自动下载并配置Spark。

**额外Conda包**：
- pyarrow（Spark DataFrame与Pandas转换）
- pandas（版本由setup_spark.py自动解析与Spark匹配）
- grpcio, grpcio-status

**环境变量**：
```
SPARK_HOME=/usr/local/spark
PATH=${PATH}:${SPARK_HOME}/bin
SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M ..."
```

**端口**：EXPOSE 4040（Spark UI）

**Derby版本替换**：Spark内置的Derby 10.16.1.1存在问题，Dockerfile显式替换为10.17.1.0并验证SHA256校验和。

## all-spark-notebook（Spark + R）

**基础镜像**：pyspark-notebook

在PySpark基础上添加R和Spark R集成：
- r-base, r-irkernel
- r-sparklyr（R的Spark接口）
- r-ggplot2（可视化）
- r-rcurl

**环境变量**：`R_LIBS_USER="${SPARK_HOME}/R/lib"`（将SparkR库路径加入R库路径）

这是支持Python+R+Spark的全能大数据镜像。

## 镜像选择对比表

| 镜像 | Python | R | Julia | PyTorch | TF | Spark | CUDA | 相对体积 |
|------|--------|---|-------|---------|----|-------|------|---------|
| base-notebook | ✅基础 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ★☆☆☆☆ |
| minimal-notebook | ✅基础 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ★★☆☆☆ |
| scipy-notebook | ✅全栈 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ★★★☆☆ |
| r-notebook | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ★★☆☆☆ |
| julia-notebook | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ★★☆☆☆ |
| datascience-notebook | ✅全栈 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ★★★★☆ |
| pytorch-notebook | ✅全栈 | ❌ | ❌ | ✅CPU/GPU | ❌ | ❌ | ✅(变体) | ★★★★☆ |
| tensorflow-notebook | ✅全栈 | ❌ | ❌ | ❌ | ✅CPU/GPU | ❌ | ✅(变体) | ★★★★☆ |
| pyspark-notebook | ✅全栈 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ★★★★☆ |
| all-spark-notebook | ✅全栈 | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ★★★★★ |

## 相关概念

- [镜像层级架构](02-image-hierarchy.md)
- [Minimal到SciPy层](05-minimal-scipy.md)
- [基础启动示例](../examples/01-basic-run.md)
- [GPU/CUDA使用](../examples/04-gpu-cuda.md)
