# 示例索引

本目录包含 Enterprise Gateway 的3个实战示例，覆盖本地开发、自定义扩展和生产部署场景。

## 示例清单

* [本地启动EG并执行代码](01-start-eg-locally.md) — 从零开始：安装EG、本地启动、通过REST API创建Python内核、使用WebSocket发送代码执行请求并接收结果。
* [编写自定义ProcessProxy](02-custom-process-proxy.md) — 完整的自定义ProcessProxy实现示例，包含launch_process/confirm_remote_startup/poll/kill等核心方法，以及kernelspec配置方法。
* [Kubernetes部署EG](03-kubernetes-deployment.md) — K8s集群部署EG完整指南，包含RBAC配置、Helm部署、手动YAML部署、内核Pod创建测试、生产环境建议。

```{toctree}
:hidden:
:maxdepth: 7

01-start-eg-locally
02-custom-process-proxy
03-kubernetes-deployment
```
