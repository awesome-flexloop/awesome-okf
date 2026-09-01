---
type: concept
scope: omlmd
name: helpers-listener
version: "0.1.6"
source: https://github.com/containers/omlmd/blob/main/omlmd/helpers.py
description: Helper 类与 Listener 观察者模式
---

# Helper 类与 Listener 观察者模式

`Helper` 是 omlmd 的高层 API 门面类，封装了底层 Registry 的复杂操作，提供简洁的推送、拉取、元数据获取和爬取接口。同时通过 `Listener` 观察者模式支持事件监听与扩展。

## Helper 类

### 类定义

```python
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Sequence

@dataclass
class Helper:
    _registry: OMLMDRegistry = field(
        default_factory=lambda: OMLMDRegistry(insecure=True)
    )
    _listeners: list[Listener] = field(default_factory=list)
```

Helper 是一个 dataclass，包含两个内部字段：
- `_registry`：底层 OMLMDRegistry 实例，默认使用 `insecure=True`（允许 HTTP 连接）
- `_listeners`：监听器列表，用于观察者模式

### 工厂方法

```python
@classmethod
def from_default_registry(cls, insecure: bool):
    return cls(OMLMDRegistry(insecure=insecure))
```

通过 `from_default_registry()` 类方法可以创建指定安全模式的 Helper 实例，CLI 内部使用此方法。

## push() 方法

`push()` 是最核心的方法，负责将模型文件和元数据推送到 OCI 注册表。

### 方法签名

```python
def push(
    self,
    target: str,
    path: Path | str,
    name: str | None = None,
    description: str | None = None,
    author: str | None = None,
    model_format_name: str | None = None,
    model_format_version: str | None = None,
    **kwargs,
):
```

**参数说明**：
- `target`：目标 OCI 引用（如 `localhost:8080/user/model:v1`）
- `path`：本地模型文件路径
- `name`、`description`、`author`：标准元数据字段
- `model_format_name`、`model_format_version`：模型格式信息
- `**kwargs`：任意额外关键字参数，自动归入 `customProperties`

### 工作流程

```
1. 分离 kwargs 中标准字段和自定义属性
2. 构建 ModelMetadata 实例
3. 确定临时元数据文件路径
4. 判断元数据处理策略：
   ├─ 元数据为空且目录中已有 .json/.yaml 文件 → 复用现有文件
   ├─ 元数据非空但目录中存在冲突文件 → 抛出 RuntimeError
   └─ 否则 → 自动生成临时元数据文件
5. 构建 files 列表（模型 + JSON 元数据 + YAML 元数据）
6. 调用 registry.push() 推送到注册表
7. 触发 PushEvent 通知监听器
8. finally 块清理临时文件（如果是自动生成的）
```

### 临时文件管理

push 过程中会在模型文件同目录生成两个临时元数据文件：
- `model_metadata.omlmd.json`
- `model_metadata.omlmd.yaml`

使用 `try-finally` 确保推送完成后（无论成功失败）自动清理临时文件，避免污染工作目录。

## pull() 方法

拉取 OCI Artifact 到本地目录：

```python
def pull(
    self, target: str, outdir: Path | str, media_types: Sequence[str] | None = None
):
    self._registry.download_layers(target, outdir, media_types)
```

**参数说明**：
- `target`：源 OCI 引用
- `outdir`：输出目录
- `media_types`：可选的媒体类型过滤列表

通过 `media_types` 参数可以选择性拉取：
- `["application/x-mlmodel"]`：仅拉取模型文件
- `["application/x-config"]`：仅拉取元数据
- `None` 或空列表：拉取所有内容

## get_config() 方法

获取 Artifact 的配置层（元数据）：

```python
def get_config(self, target: str) -> str:
    return f'{{"reference":"{target}", "config": {self._registry.get_config(target)} }}'
```

返回包装后的 JSON 字符串，包含 reference 和 config 两个字段，方便后续批处理。

## crawl() 方法

批量爬取多个 Artifact 的元数据：

```python
def crawl(self, targets: Sequence[str]) -> str:
    configs = map(self.get_config, targets)
    joined = "[" + ", ".join(configs) + "]"
    return joined
```

接受多个目标引用，依次调用 `get_config()`，返回 JSON 数组格式的结果。可配合 jq 等工具进行查询和筛选。

**示例**：

```python
result = omlmd.crawl([
    "localhost:8080/model:v1",
    "localhost:8080/model:v2",
    "localhost:8080/model:v3",
])
```

## Listener 观察者模式

OMLMD 实现了经典的观察者模式，允许在推送等操作发生时触发自定义逻辑。

### Listener 抽象基类

```python
from abc import ABC, abstractmethod
import typing as t

class Listener(ABC):
    @abstractmethod
    def update(self, source: t.Any, event: Event) -> None:
        """Receive update event."""
        pass
```

自定义监听器需要继承 `Listener` 并实现 `update()` 方法。

### Event 体系

```python
class Event(ABC):
    pass

@dataclass
class PushEvent(Event):
    digest: str
    target: str
    metadata: ModelMetadata

    @classmethod
    def from_response(
        cls, response: requests.Response, target: str, metadata: ModelMetadata
    ) -> "PushEvent":
        return cls(response.headers["Docker-Content-Digest"], target, metadata)
```

- `Event`：所有事件的抽象基类
- `PushEvent`：推送完成事件，包含：
  - `digest`：推送内容的 Docker-Content-Digest
  - `target`：目标引用
  - `metadata`：推送的元数据对象

### 监听器管理方法

```python
def add_listener(self, listener: Listener) -> None:
    self._listeners.append(listener)

def remove_listener(self, listener: Listener) -> None:
    self._listeners.remove(listener)

def notify_listeners(self, event: Event) -> None:
    for listener in self._listeners:
        listener.update(self, event)
```

- `add_listener()`：注册监听器
- `remove_listener()`：移除监听器
- `notify_listeners()`：通知所有监听器（在 push 成功后自动调用）

### 自定义监听器示例

```python
from omlmd.helpers import Helper
from omlmd.listener import Listener, PushEvent

class LoggingListener(Listener):
    def update(self, source, event):
        if isinstance(event, PushEvent):
            print(f"Pushed to {event.target}")
            print(f"Digest: {event.digest}")
            print(f"Model: {event.metadata.name}")

helper = Helper()
helper.add_listener(LoggingListener())
helper.push("localhost:8080/model:v1", "model.joblib", name="My Model")
```

## download_file() 辅助函数

Helper 模块还提供了一个简单的 HTTP 文件下载工具：

```python
def download_file(uri: str):
    file_name = os.path.basename(uri)
    urllib.request.urlretrieve(uri, file_name)
    return file_name
```

从 URI 下载文件到当前目录，返回文件名。

## 模块依赖关系

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    CLI      │────▶│   Helper    │────▶│    Model    │
│  (cli.py)   │     │ (helpers.py)│     │  Metadata   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ├─────────────┐
                           ▼             ▼
                    ┌─────────────┐ ┌─────────────┐
                    │ OMLMDRegistry│ │  Listener   │
                    │ (provider.py)│ │(listener.py)│
                    └─────────────┘ └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  oras-py    │
                    │ (外部依赖)   │
                    └─────────────┘
```

Helper 作为门面模式（Facade）的应用，简化了底层 oras-py 的使用复杂度，同时通过 Listener 模式提供了良好的可扩展性。
