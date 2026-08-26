---
type: example
scope: omlmd
name: cli-push
version: "0.1.6"
source: https://github.com/containers/omlmd
description: CLI 推送模型元数据完整流程
---

# CLI 推送模型元数据

本示例演示如何使用 omlmd CLI 命令行工具推送 ML 模型及其元数据到 OCI 注册表。

## 前置条件

1. 安装 omlmd：

```bash
pip install omlmd
```

2. 启动本地 OCI 注册表（可选，用于测试）：

```bash
# 使用 distribution registry
docker run -d -p 5000:5000 --name registry registry:2

# 或使用 zot
docker run -d -p 5000:5000 --name zot ghcr.io/project-zot/zot-linux-amd64:latest
```

## CLI 命令概览

omlmd CLI 基于 Click + Cloup 构建，提供以下子命令：

| 命令 | 功能 |
|---|---|
| `omlmd push` | 推送模型和元数据到注册表 |
| `omlmd pull` | 从注册表拉取模型和元数据 |
| `omlmd get config` | 获取指定 Artifact 的配置（元数据） |
| `omlmd crawl` | 批量爬取多个 Artifact 的元数据 |

## push 命令详解

### 命令语法

```bash
omlmd push [OPTIONS] TARGET PATH
```

### 参数说明

| 参数 | 类型 | 说明 |
|---|---|---|
| `TARGET` | 位置参数（必填） | 目标 OCI 引用，如 `localhost:5000/user/model:v1` |
| `PATH` | 位置参数（必填） | 本地模型文件路径，必须存在 |
| `--plain-http` | 标志 | 允许非 SSL（HTTP）连接，本地测试时使用 |
| `-m, --metadata` | 路径 | 元数据文件路径（JSON 或 YAML 格式） |
| `--empty-metadata` | 标志 | 推送空元数据 |

**注意**：`--metadata` 和 `--empty-metadata` 是互斥选项，必须提供其中一个（除非通过代码方式传递）。

### 准备模型文件

首先训练或准备一个模型文件，以 scikit-learn 为例：

```python
# train_model.py
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from joblib import dump

X, y = load_iris(return_X_y=True)
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

dump(model, "model.joblib")
print(f"Model saved. Accuracy: {model.score(X, y):.4f}")
```

```bash
python train_model.py
```

### 方式一：使用 YAML 元数据文件

创建元数据文件 `metadata.yaml`：

```yaml
name: Iris Random Forest Classifier
description: A random forest classifier trained on the Iris dataset
author: John Doe
model_format_name: sklearn
model_format_version: "1.3.0"
customProperties:
  accuracy: 0.9733
  dataset: iris
  n_estimators: 100
  license: Apache-2.0
```

推送：

```bash
omlmd --plain-http push localhost:5000/ml/iris-rf:v1 model.joblib -m metadata.yaml
```

### 方式二：使用 JSON 元数据文件

创建元数据文件 `metadata.json`：

```json
{
    "name": "Iris Random Forest Classifier",
    "description": "A random forest classifier trained on the Iris dataset",
    "author": "John Doe",
    "model_format_name": "sklearn",
    "model_format_version": "1.3.0",
    "customProperties": {
        "accuracy": 0.9733,
        "dataset": "iris",
        "n_estimators": 100,
        "license": "Apache-2.0"
    }
}
```

推送：

```bash
omlmd push --plain-http localhost:5000/ml/iris-rf:v1 model.joblib -m metadata.json
```

### 方式三：空元数据推送

```bash
omlmd push --plain-http localhost:5000/ml/model:v1 model.joblib --empty-metadata
```

## pull 命令详解

### 命令语法

```bash
omlmd pull [OPTIONS] TARGET
```

### 参数说明

| 参数 | 类型 | 说明 |
|---|---|---|
| `TARGET` | 位置参数（必填） | 源 OCI 引用 |
| `--plain-http` | 标志 | 允许非 SSL 连接 |
| `-o, --output` | 路径 | 输出目录，默认为当前工作目录 |
| `-m, --media-types` | 多值 | 按媒体类型过滤下载 |

### 拉取全部内容

```bash
omlmd pull --plain-http localhost:5000/ml/iris-rf:v1 -o ./downloaded
```

### 仅拉取模型文件

```bash
omlmd pull --plain-http localhost:5000/ml/iris-rf:v1 -o ./models -m application/x-mlmodel
```

### 仅拉取元数据

```bash
omlmd pull --plain-http localhost:5000/ml/iris-rf:v1 -o ./metadata -m application/x-config
```

## get config 命令

获取 Artifact 的元数据配置：

```bash
omlmd get config --plain-http localhost:5000/ml/iris-rf:v1
```

输出示例：

```json
{
  "reference": "localhost:5000/ml/iris-rf:v1",
  "config": {
    "name": "Iris Random Forest Classifier",
    "description": "A random forest classifier trained on the Iris dataset",
    "author": "John Doe",
    "customProperties": {
      "accuracy": 0.9733,
      "dataset": "iris",
      "n_estimators": 100,
      "license": "Apache-2.0"
    },
    "uri": null,
    "model_format_name": "sklearn",
    "model_format_version": "1.3.0"
  }
}
```

## crawl 命令

批量爬取多个模型版本的元数据：

```bash
omlmd crawl --plain-http \
  localhost:5000/ml/iris-rf:v1 \
  localhost:5000/ml/iris-rf:v2 \
  localhost:5000/ml/iris-rf:v3
```

输出为 JSON 数组，可配合 jq 查询：

```bash
# 查找 accuracy 最高的版本
omlmd crawl --plain-http localhost:5000/ml/iris-rf:v1 localhost:5000/ml/iris-rf:v2 | \
  jq 'max_by(.config.customProperties.accuracy).reference'
```

## 完整工作流示例

以下是一个完整的 CLI 工作流：

```bash
# 1. 训练并保存模型
python train_model.py

# 2. 创建元数据文件
cat > metadata.yaml << 'EOF'
name: Iris Classifier
author: Demo User
model_format_name: sklearn
customProperties:
  accuracy: 0.97
  license: MIT
EOF

# 3. 推送到本地注册表
omlmd push --plain-http localhost:5000/demo/iris:v1 model.joblib -m metadata.yaml

# 4. 查看元数据
omlmd get config --plain-http localhost:5000/demo/iris:v1 | jq .

# 5. 拉取到新目录
mkdir -p ./retrieved
omlmd pull --plain-http localhost:5000/demo/iris:v1 -o ./retrieved

# 6. 验证下载的文件
ls -la ./retrieved/
# 应该看到：model.joblib, model_metadata.omlmd.json, model_metadata.omlmd.yaml
```

## 常见问题

### 连接错误：x509: certificate signed by unknown authority

本地测试时注册表使用自签名证书或 HTTP，添加 `--plain-http` 标志：

```bash
omlmd push --plain-http localhost:5000/...
```

### 元数据文件格式错误

确保元数据文件是有效的 JSON 或 YAML。可以先验证：

```bash
# 验证 JSON
python -m json.tool metadata.json

# 验证 YAML
python -c "import yaml; yaml.safe_load(open('metadata.yaml'))"
```

### 文件已存在错误

如果模型文件同目录下已有 `model_metadata.omlmd.json` 或 `model_metadata.omlmd.yaml`，push 时会报错。删除这些文件或在其他目录执行操作。

### 权限错误

确保对输出目录有写入权限，对模型文件有读取权限。
