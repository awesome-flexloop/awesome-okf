---
type: reference
scope: omlmd
name: readme-source
version: "0.1.6"
source: https://github.com/containers/omlmd
description: OMLMD 项目 README 原始参考
---

# README 原始参考

OMLMD 是一个利用 OCI Artifact 和容器来处理 ML 模型和元数据的蓝图、模式和工具链集合，提供 Python SDK 和 CLI 两种形式。

## 安装

```bash
pip install omlmd
```

## 推送模型

```python
from omlmd.helpers import Helper

omlmd = Helper()
omlmd.push("localhost:8080/matteo/ml-artifact:latest", "model.joblib", name="Model Example", author="John Doe", license="Apache-2.0", accuracy=9.876543210)
```

## 拉取模型

拉取所有内容：

```python
omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b")
```

仅拉取 ML 模型资产：

```python
omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b", media_types=["application/x-mlmodel"])
```

## 获取元数据

```python
md = omlmd.get_config(target="localhost:8080/matteo/ml-artifact:latest")
print(md)
```

## 爬取元数据

```python
crawl_result = omlmd.crawl([
    "localhost:8080/matteo/ml-artifact:v1",
    "localhost:8080/matteo/ml-artifact:v2",
    "localhost:8080/matteo/ml-artifact:v3"
])
```

## jQ 查询示例

```python
import jq
jq.compile("max_by(.config.customProperties.accuracy).reference").input_text(crawl_result).first()
```

## 项目信息

- **版本**：0.1.6
- **作者**：Matteo Mortari (matteo.mortari@gmail.com)
- **许可证**：Apache-2.0
- **Python 版本**：3.9、3.10、3.11、3.12
- **核心依赖**：oras >= 0.2.23, < 0.3.0、pyyaml ^6.0.1、click ^8.1.7、cloup ^3.0.5
- **文档**：https://containers.github.io/omlmd
- **PyPI**：https://pypi.org/project/omlmd
