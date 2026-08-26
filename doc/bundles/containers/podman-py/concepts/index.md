# 核心概念

本目录按学习路径组织 podman-py 的核心概念文档，从快速入门到连接配置，再到管理器架构与各类资源操作。

* [00 - 快速入门与 Docker SDK 兼容性](00-introduction.md) — Python 版本要求、安装、第一个程序、Docker 兼容性别名、环境变量兼容、Manager API 对齐、不支持的 Swarm 功能、核心依赖。
* [01 - 连接配置（UDS/SSH/TCP）](01-connection.md) — 连接配置优先级、本地 Unix Socket、SSH 远程隧道、TCP 网络连接、from_env() 环境变量自动检测、containers.conf 命名连接、连接池配置、上下文管理器。
* [02 - 资源管理器架构](02-managers.md) — Manager 模式、@cached_property 懒加载、Manager 基类、9 个资源管理器总览、Mixin 组合模式、领域目录结构、资源模型对象。
* [03 - 容器生命周期操作](03-containers.md) — 容器状态机、list 过滤查询、get 获取单个容器、create/run 创建启动、start/stop/kill/restart/pause 状态控制、remove/prune 删除清理、logs 日志获取、exec_run 命令执行、reload 属性刷新。
* [04 - 镜像管理与构建](04-images.md) — 镜像列表与查询、pull 拉取与进度条、push 推送与认证、build 从 Containerfile 构建、remove/prune 删除清理、search 镜像搜索、load/save 加载保存、tag 标签管理、login registry 登录、scp 跨主机复制。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-connection
02-managers
03-containers
04-images
```
