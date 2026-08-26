---
type: example
scope: omlmd
name: python-custom
version: "0.1.6"
source: https://github.com/containers/omlmd
description: Python SDK 自定义 Provider 扩展与高级用法
---

# Python SDK 自定义扩展

本示例演示如何使用 omlmd Python SDK 进行高级操作，包括自定义 Provider、监听器扩展、以及与其他工具集成。

## Python SDK 基础

### 安装

```bash
pip install omlmd
```

### 基础使用

```python
from omlmd.helpers import Helper
from pathlib import Path

# 创建 Helper 实例（默认 insecure=True，适合本地测试）
omlmd = Helper()

# 推送模型
omlmd.push(
    target="localhost:5000/ml/model:v1",
    path="model.joblib",
    name="My Model",
    author="Me",
    accuracy=0.95
)

# 拉取模型
omlmd.pull("localhost:5000/ml/model:v1", outdir="./output")

# 获取元数据
config = omlmd.get_config("localhost:5000/ml/model:v1")
print(config)
```

## 使用安全注册表连接

生产环境使用 HTTPS 时，创建非 insecure 模式的 Helper：

```python
from omlmd.helpers import Helper

# 安全连接（不使用 --plain-http）
helper = Helper.from_default_registry(insecure=False)

helper.push(
    target="registry.example.com/ml/model:v1",
    path="model.joblib",
    name="Production Model"
)
```

## 自定义 Listener 监听器

通过实现 `Listener` 接口，可以在推送等操作时触发自定义逻辑，如日志记录、通知、审计等。

### 示例：日志监听器

```python
from omlmd.helpers import Helper
from omlmd.listener import Listener, PushEvent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingListener(Listener):
    """记录推送操作的监听器"""

    def update(self, source, event):
        if isinstance(event, PushEvent):
            logger.info(f"Push successful!")
            logger.info(f"  Target: {event.target}")
            logger.info(f"  Digest: {event.digest}")
            logger.info(f"  Model name: {event.metadata.name}")
            logger.info(f"  Author: {event.metadata.author}")
            if event.metadata.customProperties:
                logger.info(f"  Custom properties: {event.metadata.customProperties}")

# 使用
helper = Helper()
helper.add_listener(LoggingListener())

helper.push(
    "localhost:5000/ml/model:v1",
    "model.joblib",
    name="Logged Model",
    author="Listener Demo",
    accuracy=0.98
)
```

### 示例：指标收集监听器

```python
from omlmd.listener import Listener, PushEvent
from collections import defaultdict
import json
from datetime import datetime

class MetricsListener(Listener):
    """收集推送指标的监听器"""

    def __init__(self, metrics_file="push_metrics.jsonl"):
        self.metrics_file = metrics_file
        self.stats = defaultdict(int)

    def update(self, source, event):
        if isinstance(event, PushEvent):
            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "target": event.target,
                "digest": event.digest,
                "model_name": event.metadata.name,
                "author": event.metadata.author,
                "properties": event.metadata.customProperties
            }

            # 追加到 JSONL 文件
            with open(self.metrics_file, "a") as f:
                f.write(json.dumps(record) + "\n")

            # 更新内存统计
            self.stats["total_pushes"] += 1
            if event.metadata.author:
                self.stats[f"author_{event.metadata.author}"] += 1

            print(f"Metrics recorded. Total pushes: {self.stats['total_pushes']}")

# 使用
metrics_listener = MetricsListener()
helper = Helper()
helper.add_listener(metrics_listener)

# 推送多个模型
for version in ["v1", "v2", "v3"]:
    helper.push(
        f"localhost:5000/ml/model:{version}",
        "model.joblib",
        name=f"Model {version}",
        author="Team A"
    )
```

### 移除监听器

```python
listener = LoggingListener()
helper.add_listener(listener)

# ... 执行操作 ...

helper.remove_listener(listener)
```

## 直接使用 OMLMDRegistry

如需更底层控制，可以直接使用 `OMLMDRegistry` 类。

```python
from omlmd.provider import OMLMDRegistry
from pathlib import Path

# 创建注册表客户端
registry = OMLMDRegistry(insecure=True)

# 按媒体类型下载
layers = registry.download_layers(
    package="localhost:5000/ml/model:v1",
    download_dir="./downloaded",
    media_types=["application/x-mlmodel"]
)
print(f"Downloaded layers: {layers}")

# 获取配置
config_str = registry.get_config("localhost:5000/ml/model:v1")
print(config_str)
```

## 元数据编程式构建

不使用文件，直接在代码中构建元数据：

```python
from omlmd.helpers import Helper
from omlmd.model_metadata import ModelMetadata
import json

# 方式 1：通过 Helper.push() 的关键字参数
helper = Helper()
helper.push(
    "localhost:5000/ml/model:v1",
    "model.joblib",
    name="Programmatic Model",
    description="Model with metadata built in code",
    author="Python SDK",
    model_format_name="pytorch",
    model_format_version="2.0.0",
    accuracy=0.99,
    f1_score=0.98,
    dataset_version="2024.01",
    training_epochs=100
)

# 方式 2：显式构建 ModelMetadata 对象
md = ModelMetadata(
    name="Explicit Metadata Model",
    author="Code Builder",
    customProperties={
        "accuracy": 0.96,
        "tags": ["classification", "tabular"],
        "training_params": {
            "lr": 0.001,
            "batch_size": 32
        }
    }
)

print("JSON:")
print(md.to_json())

print("\nYAML:")
print(md.to_yaml())

print("\nAnnotations dict:")
print(json.dumps(md.to_annotations_dict(), indent=2))
```

## 批量爬取与查询

使用 `crawl()` 配合 jq 进行模型版本筛选：

```python
from omlmd.helpers import Helper
import json

try:
    import jq
    HAS_JQ = True
except ImportError:
    HAS_JQ = False

helper = Helper()

# 爬取多个版本
versions = ["v1", "v2", "v3", "v4", "v5"]
targets = [f"localhost:5000/ml/experiment:{v}" for v in versions]

crawl_result = helper.crawl(targets)
data = json.loads(crawl_result)

print("All models:")
for item in data:
    config = item["config"]
    acc = config.get("customProperties", {}).get("accuracy", "N/A")
    print(f"  {item['reference']}: accuracy={acc}")

# 如果有 jq，可以进行复杂查询
if HAS_JQ:
    # 找到 accuracy 最高的版本
    best = jq.compile(
        "max_by(.config.customProperties.accuracy).reference"
    ).input_text(crawl_result).first()
    print(f"\nBest model: {best}")

    # 筛选 accuracy > 0.95 的模型
    good_models = jq.compile(
        ".[] | select(.config.customProperties.accuracy > 0.95) | .reference"
    ).input_text(crawl_result).all()
    print(f"Models with accuracy > 0.95: {good_models}")
```

## 与 scikit-learn 集成

完整的训练-推送-加载流程：

```python
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from joblib import dump, load
from omlmd.helpers import Helper
import tempfile
import os

# 1. 训练模型
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {acc:.4f}")

# 2. 保存到临时文件并推送
helper = Helper()

with tempfile.TemporaryDirectory() as tmpdir:
    model_path = os.path.join(tmpdir, "model.joblib")
    dump(model, model_path)

    # 推送，附带训练指标
    helper.push(
        target="localhost:5000/ml/iris-sklean:latest",
        path=model_path,
        name="Iris Random Forest",
        description="Trained with scikit-learn",
        author="Python SDK Example",
        model_format_name="sklearn",
        model_format_version="1.3.0",
        accuracy=acc,
        n_estimators=100,
        test_size=0.2
    )

# 3. 拉取并验证
with tempfile.TemporaryDirectory() as outdir:
    helper.pull("localhost:5000/ml/iris-sklean:latest", outdir)

    loaded_model = load(os.path.join(outdir, "model.joblib"))
    loaded_pred = loaded_model.predict(X_test)
    loaded_acc = accuracy_score(y_test, loaded_pred)
    print(f"Loaded model accuracy: {loaded_acc:.4f}")
    assert abs(acc - loaded_acc) < 1e-10, "Accuracy mismatch!"
    print("Model push/pull/load verified successfully!")
```

## 自定义 Provider 扩展

如果需要自定义注册表行为，可以继承 `OMLMDRegistry`：

```python
from omlmd.provider import OMLMDRegistry
from oras.decorator import ensure_container
import logging

logger = logging.getLogger(__name__)

class CustomOMLMDRegistry(OMLMDRegistry):
    """自定义注册表客户端，添加重试和日志"""

    def __init__(self, *args, retries=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.retries = retries

    @ensure_container
    def download_layers(self, package, download_dir, media_types):
        """带重试的层下载"""
        for attempt in range(self.retries):
            try:
                logger.info(f"Download attempt {attempt + 1}/{self.retries}")
                return super().download_layers(package, download_dir, media_types)
            except Exception as e:
                if attempt == self.retries - 1:
                    raise
                logger.warning(f"Download failed: {e}, retrying...")

    @ensure_container
    def get_config(self, package):
        """带缓存的配置获取"""
        if not hasattr(self, '_config_cache'):
            self._config_cache = {}

        if package not in self._config_cache:
            self._config_cache[package] = super().get_config(package)
            logger.info(f"Config cached for {package}")

        return self._config_cache[package]

# 使用自定义 Registry
from omlmd.helpers import Helper

custom_registry = CustomOMLMDRegistry(insecure=True, retries=5)
helper = Helper(_registry=custom_registry)

config = helper.get_config("localhost:5000/ml/model:v1")
print(config)
```

## 最佳实践

1. **使用 Listener 进行审计**：对生产环境的推送操作添加监听器记录日志
2. **临时文件管理**：使用 `tempfile.TemporaryDirectory` 自动清理临时文件
3. **媒体类型过滤**：推理部署时只拉取 `application/x-mlmodel` 减少带宽
4. **元数据规范**：在 `customProperties` 中添加评估指标、数据集版本、训练参数等信息
5. **标签策略**：使用语义化版本标签（v1.0.0）和可变标签（latest、staging）配合
6. **错误处理**：网络操作添加重试逻辑（如自定义 Registry 示例）
