# 使用示例

本目录提供 podman-py 的实战示例代码，覆盖从 docker-py 迁移到完整容器生命周期操作的常见场景。

* [01 - 从 docker-py 迁移到 podman-py](01-migration.md) — 导入替换、客户端初始化、容器/镜像/网络操作对比、5 个常见差异（Swarm 不支持、sparse 模式、Socket 路径、Containerfile 命名）、完整迁移前后代码对比、迁移验证脚本。
* [02 - 容器创建、启动、停止完整操作](02-container-ops.md) — 前置条件检查、12 步完整生命周期脚本（连接→拉镜像→清理→创建→启动→列表→exec_run→日志→停止→删除→prune）、run() 快捷方式、批量启动/停止/删除容器示例。

```{toctree}
:hidden:
:maxdepth: 7

01-migration
02-container-ops
```
