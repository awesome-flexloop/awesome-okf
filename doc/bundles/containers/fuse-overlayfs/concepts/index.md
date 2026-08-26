# /concepts — 概念文档

本目录包含 fuse-overlayfs 的核心概念文档，按学习路径从基础到深入排列。

## 概念索引

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| [00](00-introduction.md) | **FUSE 与 OverlayFS 基础** | FUSE 用户空间文件系统原理、OverlayFS 三层结构（lower/upper/workdir）、copy-up 与 whiteout 基本概念、fuse-overlayfs 项目定位、源码架构、开发约束（unsafe 隔离、no panic）、FUSE 能力协商 |
| [01](01-node-inode.md) | **节点与 inode 管理** | NodeId 与 InodeKey 标识、DirState 目录状态（惰性加载、whiteouts）、OvlNode 叠加节点（layer_idx、hidden 临时状态）、NodeArena 竞技场模式、OvlIno 硬链接聚合与 lookup 计数、InodeTable 双向映射、same_device inode 透传、FNV-1a 哈希、路径计算 |
| [02](02-copyup.md) | **Copy-up 三级优化策略** | copy-up 触发时机（惰性、仅修改操作）、三级数据复制（FICLONE reflink O(1) → sendfile 零拷贝 → 1MB read/write 兜底）、copy_xattr 属性过滤、create_node_directory 递归目录、workdir+rename 原子性保证、不同文件类型处理（目录/符号链接/特殊文件/普通文件）、操作顺序原理 |
| [03](03-whiteout.md) | **whiteout 与目录合并** | 删除难题与遮盖原理、三种 whiteout 形式（.wh. 文件/.wh..wh..opq/char 0/0）、trusted.overlay.opaque xattr、多层目录合并算法（上层优先、whiteout 遮盖、opaque 停止）、lookup 路径解析、whiteout 创建时机（unlink/rmdir/rename）、合并目录删除的复杂性 |
| [04](04-mount-options.md) | **挂载选项与运行时统计** | OverlayConfig 完整结构体、核心路径选项（lowerdir/upperdir/workdir）、UID/GID 映射（无根容器核心）、性能缓存选项（timeout/fsync/writeback/threaded）、安全兼容选项（noacl/ino_t_32/static_nlink/volatile_mode）、19 个 FUSE 透传选项、SIGUSR1 运行时统计（STAT_NODES/STAT_INODES/STAT_PASSTHROUGH）、性能调优建议、初始化流程 |

## 推荐学习路径

### 入门路径（理解基本原理）
1. [00 FUSE 与 OverlayFS 基础](00-introduction.md)
2. [04 挂载选项与运行时统计](04-mount-options.md)
3. 配合 [基本挂载使用](../examples/01-basic-mount.md) 示例动手实践

### 源码理解路径（深入实现）
1. [00 FUSE 与 OverlayFS 基础](00-introduction.md)
2. [01 节点与 inode 管理](01-node-inode.md) — 内存数据结构
3. [02 Copy-up 三级优化策略](02-copyup.md) — 写入路径核心
4. [03 whiteout 与目录合并](03-whiteout.md) — 读取与删除路径核心

### 容器场景路径（无根容器）
1. [00 FUSE 与 OverlayFS 基础](00-introduction.md)
2. [04 挂载选项与运行时统计](04-mount-options.md) — uidmap/gidmap 配置
3. [02 rootless 模式配置](../examples/02-rootless.md)
