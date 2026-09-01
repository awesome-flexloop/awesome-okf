# 实践示例

本目录包含 conmon 的实践示例，从手动命令行使用到与容器管理器的集成。

---

## 示例列表

| 示例 | 难度 | 内容 |
|------|------|------|
| [01-基本命令行使用](01-basic-usage.md) | ⭐ 入门 | 编译安装conmon、准备OCI bundle、手动启动容器、观察日志和退出状态、超时测试 |
| [02-与Podman/CRI-O集成](02-integration.md) | ⭐⭐ 进阶 | Podman调用conmon的参数、管道同步机制、attach流程、窗口大小调整、OOM检测集成 |

---

## 前置知识

阅读示例前建议先了解：

1. [概念文档](../concepts/index.md) 中的核心概念，特别是进程生命周期和事件循环
2. OCI 容器运行时规范（runc/crun 的基本使用）
3. Linux cgroup、进程、信号等基础知识

## 运行示例注意事项

- conmon 仅支持 Linux 操作系统
- 需要 root 权限或正确配置的 rootless 容器环境
- 建议在测试虚拟机或容器中运行示例，避免影响系统
- 手动调用 conmon 需要准备正确的 OCI bundle（config.json + rootfs）

```{toctree}
:maxdepth: 1

01-basic-usage
02-integration
```
