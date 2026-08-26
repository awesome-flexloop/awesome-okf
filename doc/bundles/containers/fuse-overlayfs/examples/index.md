# /examples — 实践示例

本目录包含 fuse-overlayfs 的可操作实践示例，从基础挂载到无根容器配置。

## 示例索引

| 序号 | 文档 | 难度 | 核心内容 |
|------|------|------|---------|
| [01](01-basic-mount.md) | **基本挂载使用** | ⭐ 入门 | 编译安装、三层目录准备、基本挂载命令、合并视图验证、copy-up 与 whiteout 直观体验、运行时统计、卸载、多下层/只读/allow_other 变体、常见问题排查 |
| [02](02-rootless.md) | **Rootless 模式配置** | ⭐⭐ 进阶 | 用户命名空间与 UID/GID 映射原理、/etc/subuid 配置、uidmap/gidmap 选项、手动无根挂载、unshare 进入命名空间验证、Podman/Buildah 集成、排障脚本、安全注意事项 |

## 前置知识

- **示例 01** 建议配合阅读 [FUSE 与 OverlayFS 基础](../concepts/00-introduction.md)
- **示例 02** 建议先完成示例 01，并阅读 [挂载选项与运行时统计](../concepts/04-mount-options.md)

## 快速开始

如果你是第一次使用 fuse-overlayfs，从这里开始：

1. 阅读 [01 基本挂载使用](01-basic-mount.md)，动手完成编译、挂载、读写、卸载完整流程
2. 观察 copy-up 如何工作：修改 lower 文件后检查 upper 目录
3. 观察 whiteout 如何工作：删除 lower 文件后检查 upper 中的 `.wh.*` 标记
4. （可选）阅读 [02 Rootless 模式](02-rootless.md) 了解容器场景配置
