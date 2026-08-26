# /references — 信源参考

本目录包含 fuse-overlayfs 源码的 API 参考文档，所有事实均可追溯到具体源码文件和行号。

## 信源索引

| 文档 | 对应源码 | 核心内容 |
|------|---------|---------|
| [readme-source](readme-source.md) | README.md / Cargo.toml / Makefile / man page | 项目定位、版本依赖、编译安装、命令行选项、开发规则 |
| [overlay-source](overlay-source.md) | src/overlay.rs | OverlayFs、OverlayInner 核心结构体、FUSE Filesystem trait 实现、能力协商、whiteout 检测 |
| [node-source](node-source.md) | src/node.rs | NodeArena、OvlNode、InodeTable、OvlIno、NodeId、InodeKey、DirState、FNV-1a 哈希 |
| [copyup-source](copyup-source.md) | src/copyup.rs | copy-up 三级优化策略（reflink→sendfile→read/write）、copy_xattr、create_node_directory、完整 copyup 流程 |

## 源码文件一览

fuse-overlayfs 源码结构（`src/` 目录）：

| 文件 | 模块 | 说明 |
|------|------|------|
| `main.rs` | 主入口 | 命令行解析、挂载配置、daemonize、信号处理 |
| `overlay.rs` | 核心文件系统 | OverlayFs 结构体、FUSE 回调实现 |
| `node.rs` | 节点/inode 管理 | NodeArena、OvlNode、InodeTable、OvlIno |
| `copyup.rs` | Copy-up 机制 | 数据复制、目录创建、原子 rename |
| `config.rs` | 配置解析 | OverlayConfig、命令行参数解析、lowerdir 解析 |
| `layer.rs` | 层管理 | OvlLayer、init_layers、DataSource 初始化 |
| `datasource.rs` | 数据源 trait | DataSource、DirIterator trait 定义 |
| `direct.rs` | 直接访问 | DirectAccess 实现（openat2、statx、NFS FH） |
| `whiteout.rs` | Whiteout 处理 | whiteout 检测与应用 |
| `xattr.rs` | 扩展属性 | xattr 常量与辅助函数 |
| `mapping.rs` | UID/GID 映射 | 用户命名空间 ID 映射 |
| `error.rs` | 错误类型 | FsResult、错误定义 |
| `sys/` | 系统抽象 | 平台相关 unsafe 代码封装 |
