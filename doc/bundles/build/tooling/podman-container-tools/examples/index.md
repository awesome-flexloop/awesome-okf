# 实战示例

* [基础容器操作](basic-container.md) — 从镜像搜索、拉取、运行、日志查看、进入容器到停止删除的完整入门流程。
* [Pod 与 Kubernetes YAML 实战](pod-deployment.md) — 创建Pod管理多容器、kube generate生成YAML、kube play部署、nginx+redis sidecar模式示例。
* [无 Root 部署 Nginx](rootless-nginx.md) — rootless模式验证、非root容器运行、systemd用户服务生成与管理、linger配置实现开机自启。
* [远程连接与 API 使用](remote-client.md) — 远程Podman服务启动、system connection配置、REST API调用（Docker兼容+原生libpod）、Go bindings示例。

```{toctree}
:hidden:
:maxdepth: 7

basic-container
pod-deployment
rootless-nginx
remote-client
```
