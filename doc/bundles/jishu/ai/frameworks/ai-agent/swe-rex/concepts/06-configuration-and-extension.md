---
type: Concept
title: "配置与扩展：Pydantic 配置、from_config 与新增部署"
description: "SWE-ReX 的配置体系：7 个部署配置与 3 个运行时配置、discriminated union、extra=forbid、from_config 工厂、hook 扩展点、日志环境变量与 AWS 清理工具"
tags: [swe-rex, configuration, pydantic, extension, hooks, logging]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:44:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-023 ~ F-038、F-071、F-091 ~ F-093"
---

# 配置与扩展：Pydantic 配置、from_config 与新增部署

SWE-ReX 的配置层很薄，但有几个设计选择值得学：所有配置都是 Pydantic 模型、都以 `type` 字段做判别、都禁止额外字段、都通过 `from_config` 工厂创建实例。扩展一个新部署，本质上是加一个配置类 + 一个部署类 + 一行联合类型。

## 配置体系总览

| 配置类 | `type` 值 | 对应实现 | 关键默认值 | 事实 |
|---|---|---|---|---|
| `LocalDeploymentConfig` | `local` | `LocalDeployment` | — | F-035 |
| `DockerDeploymentConfig` | `docker` | `DockerDeployment` | `image="python:3.11"`, `startup_timeout=180` | F-023 |
| `ModalDeploymentConfig` | `modal` | `ModalDeployment` | `runtime_timeout=60`, `deployment_timeout=3600` | F-026 |
| `FargateDeploymentConfig` | `fargate` | `FargateDeployment` | `port=8880`, `container_timeout=900` | F-028 |
| `RemoteDeploymentConfig` | `remote` | `RemoteDeployment` | `host="http://127.0.0.1"`, `timeout=0.15` | F-071 |
| `DummyDeploymentConfig` | `dummy` | `DummyDeployment` | — | F-035 |
| `DaytonaDeploymentConfig` | （无 Literal） | `DaytonaDeployment` | `target="us"`, `port=8000` | F-032 |

> `DaytonaDeploymentConfig` 是唯一没有 `type: Literal[...]` 的配置类（F-032）。它仍可 `get_deployment()`，但与其余 6 个配置不一致，放进 `DeploymentConfig` 联合做判别反序列化时可能产生歧义；建议显式构造该配置类。

运行时配置（F-071）：

| 配置类 | `type` | 对应实现 | 关键字段 |
|---|---|---|---|
| `LocalRuntimeConfig` | `local` | `LocalRuntime` | — |
| `RemoteRuntimeConfig` | `remote` | `RemoteRuntime` | `auth_token` 必填、`host`、`port`、`timeout=0.15` |
| `DummyRuntimeConfig` | `dummy` | `DummyRuntime` | — |

## 三个统一约定

### 1. `extra="forbid"`

所有配置类都设置 `model_config = ConfigDict(extra="forbid")`（F-036）。拼错字段立即报 `ValidationError`，不会静默忽略。这对跨环境部署很重要：`startup_timeout` 写成 `startup-timeout` 会直接失败，而不是等到超时才发现。

### 2. `type` 判别字段

`DeploymentConfig` 是 7 个类的联合（F-035）；`RuntimeConfig` 是 3 个类的联合（F-071）。判别字段让“从 JSON/YAML 还原配置”成为可能：

```python
from swerex.deployment.config import DeploymentConfig, get_deployment
from pydantic import TypeAdapter

config = TypeAdapter(DeploymentConfig).validate_python({
    "type": "docker",
    "image": "python:3.12",
})
deployment = get_deployment(config)
```

### 3. `from_config` 工厂

每个部署/运行时类都有：

```python
@classmethod
def from_config(cls, config: XxxConfig) -> Self:
    return cls(**config.model_dump())
```

（F-019、F-020、F-025、F-030、F-031、F-033、F-034）这让“配置对象 → 实例”的路径统一，也方便测试用配置构造。

## 新增一个部署：五步

以假想的 `KubernetesDeployment` 为例：

### 第一步：写配置类

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict
from swerex.deployment.abstract import AbstractDeployment

class KubernetesDeploymentConfig(BaseModel):
    type: Literal["kubernetes"] = "kubernetes"
    image: str = "python:3.11"
    namespace: str = "default"
    startup_timeout: float = 180.0

    model_config = ConfigDict(extra="forbid")

    def get_deployment(self) -> AbstractDeployment:
        from swerex.deployment.kubernetes import KubernetesDeployment
        return KubernetesDeployment.from_config(self)
```

### 第二步：写部署类

实现 `add_hook`、`is_alive`、`start`、`stop`、`runtime`。`start()` 的关键是：

1. 创建 Pod/Job。
2. 等就绪。
3. 端口转发或 Service URL。
4. 生成 token。
5. `RemoteRuntime(host=..., port=..., auth_token=token)`。
6. `await _wait_until_alive(...)`。

可以直接复用 `swerex.utils.wait._wait_until_alive`（F-089）与 `swerex.utils.free_port.find_free_port`（F-090）。

### 第三步：加入联合类型

```python
DeploymentConfig = (
    LocalDeploymentConfig
    | DockerDeploymentConfig
    | ...
    | KubernetesDeploymentConfig
)
```

### 第四步：加测试

参考 `tests/test_get_deployment.py`（F-111）：断言 `get_deployment(KubernetesDeploymentConfig(...))` 返回正确类型。

### 第五步：更新文档导航

`mkdocs.yml` 的 Deployment 列表 + `docs/api/deployments/` 页面。Daytona 就是漏了这一步的现成反例（F-106）。

## Hook 扩展点

`DeploymentHook` 只有一个回调（F-037）：

```python
class DeploymentHook:
    def on_custom_step(self, message: str): ...
```

`CombinedDeploymentHook` 把多个 hook 串起来；`SetStatusDeploymentHook` 把消息转给 `callable(id, message)`（F-038）。Docker/Modal/Fargate/Daytona 在关键步骤调用 `self._hooks.on_custom_step(...)`，例如：

- `"Pulling container image"`
- `"Starting runtime"`
- `"Starting modal sandbox"`

用途：把部署进度接到 UI/日志/进度条。注意 hook 是同步回调，不要在里面做长时间阻塞操作。

## 日志配置

`utils/log.py`（F-091）：

| 环境变量 | 作用 | 默认 |
|---|---|---|
| `SWE_REX_LOG_STREAM_LEVEL` | 日志级别（名字或数字） | `DEBUG` |
| `SWE_AGENT_LOG_TIME` | 是否显示时间 | 不显示 |

`get_logger(name, emoji="🦖")` 使用 rich handler，按线程名加后缀。日志格式示例（`docs/usage.md` 第67行）：

```text
🦖 INFO     Pulling image 'python:3.12'
🦖 INFO     Starting runtime at 59647
🦖 INFO     Runtime started in 18.78s
```

## AWS 清理工具

Fargate 部署会创建 ECS cluster、task definition、IAM role、security group（F-030）。`utils/aws_teardown.py` 提供清理入口（F-093）：

| 函数 | 作用 |
|---|---|
| `get_confirmation(message)` | 交互确认 |
| `has_target_tag(tags)` | 判断是否 `swe-rex` 目标资源 |
| `delete_iam_roles()` | 删除 execution role |
| `delete_task_definitions()` | 注销 task definition |
| `delete_ecs_clusters()` | 删除 cluster |
| `delete_security_groups()` | 删除安全组 |
| `main()` | 串联上述步骤 |

运行方式：

```bash
python -m swerex.utils.aws_teardown
```

它会要求确认，避免误删共享资源。

## 打包层面的两个注意点

1. `aiohttp` 与 `typing_extensions` 被源码导入，但不在 `pyproject.toml` 运行时依赖中（F-014、F-015）。安装时通常由 `modal`/`fastapi` 等间接带入；精简环境可能缺包。自建镜像时建议显式安装。
2. `requests` 在依赖里，但 `src/` 无调用（F-016），只用于测试。若做最小运行时镜像，可以省掉。

## 相关概念

- [部署矩阵](/concepts/04-deployments.md)
- [运行时与执行语义](/concepts/05-runtimes-and-execution.md)
- [源码地图](/concepts/08-source-map.md)
- [验证报告](/references/verification.md)
