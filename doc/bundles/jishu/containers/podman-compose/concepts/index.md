# 概念文档索引

本目录包含 podman-compose 的核心概念文档，按学习路径顺序排列。

## 概念列表

| 序号 | 文档 | 描述 | 前置依赖 |
|------|------|------|---------|
| 00 | [00-introduction.md](00-introduction.md) | 快速上手与 Compose Spec 兼容：项目介绍、安装方法、兼容性说明 | 无 |
| 01 | [01-daemonless-arch.md](01-daemonless-arch.md) | daemon-less 架构：无守护进程设计与直接调用 podman CLI 的实现 | 00-introduction |
| 02 | [02-rootless.md](02-rootless.md) | rootless 模式下的网络与卷：无根模式的网络配置、卷管理与注意事项 | 00-introduction, 01-daemonless-arch |
| 03 | [03-compose-patterns.md](03-compose-patterns.md) | Compose 文件常见模式：YAML 配置模式与最佳实践 | 00-introduction |
| 04 | [04-source-architecture.md](04-source-architecture.md) | 单文件架构与 asyncio 执行模型：分层结构、命令注册装饰器、子进程调用与并发模型 | 00-introduction, 01-daemonless-arch |
| 05 | [05-cli-translation-layer.md](05-cli-translation-layer.md) | CLI 翻译层与标签状态：service dict 到 podman argv 的映射、标签即数据库 | 04-source-architecture |
| 06 | [06-config-pipeline.md](06-config-pipeline.md) | 配置加载管线：文件发现、插值引擎、归一化、深合并与 extends/include | 04-source-architecture |
| 07 | [07-dependency-lifecycle.md](07-dependency-lifecycle.md) | 依赖图与 up/down 生命周期：条件等待、重建判定、拉取策略与清理顺序 | 05-cli-translation-layer, 06-config-pipeline |
| 08 | [08-x-podman-extensions.md](08-x-podman-extensions.md) | x-podman 扩展字段全解：容器/密钥/网络/Pod 扩展与 Docker Compose 兼容开关 | 00-introduction, 05-cli-translation-layer |
| 09 | [09-version-evolution.md](09-version-evolution.md) | 版本演进与能力矩阵：0.1.x→1.6.0 时间线、版本门槛、未发布变更与 bash 补全 | 00-introduction, 08-x-podman-extensions |
| 10 | [10-compose-vs-podman-py.md](10-compose-vs-podman-py.md) | podman-compose 与 podman-py 对比：声明式 CLI 编排器 vs 命令式 REST SDK，十维对比与选型决策 | 00-introduction, 04-source-architecture |

## 学习路径建议

### 新手路径
1. 先阅读 [00-introduction.md](00-introduction.md) 安装并运行第一个示例
2. 然后阅读 [03-compose-patterns.md](03-compose-patterns.md) 学习配置文件写法
3. 配合 [examples/](../examples/index.md) 中的示例动手实践

### 架构理解路径
1. [00-introduction.md](00-introduction.md) 了解项目定位
2. [01-daemonless-arch.md](01-daemonless-arch.md) 理解无守护进程架构
3. [04-source-architecture.md](04-source-architecture.md) 掌握单文件分层与 asyncio 执行模型
4. [05-cli-translation-layer.md](05-cli-translation-layer.md) 理解 service dict 到 podman argv 的翻译层
5. [06-config-pipeline.md](06-config-pipeline.md) 理解配置加载、插值与合并管线
6. [07-dependency-lifecycle.md](07-dependency-lifecycle.md) 理解依赖图与 up/down 生命周期
7. [08-x-podman-extensions.md](08-x-podman-extensions.md) 掌握 Podman 独有扩展字段与兼容开关
8. [09-version-evolution.md](09-version-evolution.md) 了解版本能力矩阵与升级注意事项
9. [10-compose-vs-podman-py.md](10-compose-vs-podman-py.md) 对比 Python SDK，明确编排器与库的选型边界
10. [02-rootless.md](02-rootless.md) 深入了解 rootless 安全模型

### 生产使用路径
1. [00-introduction.md](00-introduction.md) 安装部署
2. [02-rootless.md](02-rootless.md) 理解安全边界和权限模型
3. [03-compose-patterns.md](03-compose-patterns.md) 掌握配置最佳实践
4. [08-x-podman-extensions.md](08-x-podman-extensions.md) 用 x-podman 字段处理 Podman 特有需求与迁移兼容
5. [09-version-evolution.md](09-version-evolution.md) 升级前核对版本能力门槛
6. 参考 [examples/](../examples/index.md) 中的多容器示例

```{toctree}
:hidden:
:maxdepth: 2

00-introduction
01-daemonless-arch
02-rootless
03-compose-patterns
04-source-architecture
05-cli-translation-layer
06-config-pipeline
07-dependency-lifecycle
08-x-podman-extensions
09-version-evolution
10-compose-vs-podman-py
```
