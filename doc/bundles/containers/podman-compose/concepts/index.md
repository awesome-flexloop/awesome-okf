# 概念文档索引

本目录包含 podman-compose 的核心概念文档，按学习路径顺序排列。

## 概念列表

| 序号 | 文档 | 描述 | 前置依赖 |
|------|------|------|---------|
| 00 | [00-introduction.md](00-introduction.md) | 快速上手与 Compose Spec 兼容：项目介绍、安装方法、兼容性说明 | 无 |
| 01 | [01-daemonless-arch.md](01-daemonless-arch.md) | daemon-less 架构：无守护进程设计与直接调用 podman CLI 的实现 | 00-introduction |
| 02 | [02-rootless.md](02-rootless.md) | rootless 模式下的网络与卷：无根模式的网络配置、卷管理与注意事项 | 00-introduction, 01-daemonless-arch |
| 03 | [03-compose-patterns.md](03-compose-patterns.md) | Compose 文件常见模式：YAML 配置模式与最佳实践 | 00-introduction |

## 学习路径建议

### 新手路径
1. 先阅读 [00-introduction.md](00-introduction.md) 安装并运行第一个示例
2. 然后阅读 [03-compose-patterns.md](03-compose-patterns.md) 学习配置文件写法
3. 配合 [examples/](../examples/index.md) 中的示例动手实践

### 架构理解路径
1. [00-introduction.md](00-introduction.md) 了解项目定位
2. [01-daemonless-arch.md](01-daemonless-arch.md) 理解无守护进程架构
3. [02-rootless.md](02-rootless.md) 深入了解 rootless 安全模型

### 生产使用路径
1. [00-introduction.md](00-introduction.md) 安装部署
2. [02-rootless.md](02-rootless.md) 理解安全边界和权限模型
3. [03-compose-patterns.md](03-compose-patterns.md) 掌握配置最佳实践
4. 参考 [examples/](../examples/index.md) 中的多容器示例
