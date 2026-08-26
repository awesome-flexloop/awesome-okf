# Log

## 2026-08-26

- **Initialization**: 为 fuse-overlayfs v2.0.0 生成 OKF v0.2 Wiki bundle。

  生成内容统计：
  - 4 篇信源参考文档（references/）：readme-source.md、overlay-source.md、node-source.md、copyup-source.md + index.md
  - 5 篇概念文档（concepts/）：00-introduction.md（FUSE与OverlayFS基础）、01-node-inode.md（节点与inode管理）、02-copyup.md（Copy-up三级优化）、03-whiteout.md（whiteout与目录合并）、04-mount-options.md（挂载选项与统计）+ index.md
  - 2 篇实践示例（examples/）：01-basic-mount.md（基本挂载使用）、02-rootless.md（Rootless模式配置）+ index.md
  - 2 篇根文件：index.md（bundle索引）、log.md（本日志）

  总计：18 个 Markdown 文件。

  关键特性覆盖：
  - Rust 2024 + fuser 0.17 技术栈
  - NodeArena 竞技场模式 + InodeTable 双向映射 + DirState 惰性加载
  - Copy-up 三级优化：FICLONE(reflink) O(1) → sendfile 零拷贝 → 1MB read/write 兜底
  - 三种 whiteout 形式 + opaque 目录 + 多层目录合并算法
  - 19 个 FUSE 透传选项 + UID/GID 映射 + SIGUSR1 运行时统计
  - unsafe 隔离（仅 src/sys/）+ 无 panic 错误处理策略
  - Podman/Buildah 无根容器集成配置
