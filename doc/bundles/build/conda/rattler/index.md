---
okf_version: "0.2"
---

# Rattler 学习文档

> Rust 编写的高性能 conda 包管理库集合

本 bundle 提供 [Rattler](https://github.com/conda/rattler) 的系统化学习文档。Rattler 是一组 Rust 库，为 conda 生态系统提供包管理能力——依赖求解、包下载与安装、环境激活、虚拟包检测等。它是 pixi、rattler-build 和 prefix.dev 的核心引擎，同时提供 Python 和 JavaScript/WASM 绑定。

## 学习路径

### 🚀 快速开始

| 文档 | 说明 |
|------|------|
| [Rattler 简介](concepts/00-introduction.md) | Rattler 是什么、与 conda/mamba/pixi 的关系、核心能力概览 |
| [5分钟快速上手](concepts/01-getting-started.md) | CLI/Rust/Python/JS 四种使用方式，含完整示例代码 |

### 🏗️ 架构理解

| 文档 | 说明 |
|------|------|
| [Crates 分层架构](concepts/02-crates-architecture.md) | 30个crate的四层架构（基础类型→网络I/O→核心业务→高层集成），含Mermaid架构图 |

### 📊 数据模型

| 文档 | 说明 |
|------|------|
| [基础类型系统](concepts/03-conda-types-foundation.md) | Version/Platform/PackageName/Channel 等核心数据类型 |
| [MatchSpec 查询语言与版本约束](concepts/04-matchspec-and-versionspec.md) | 包匹配语法、版本约束、StringMatcher 通配符 |
| [包记录与 RepoData](concepts/05-package-records-and-repodata.md) | PackageRecord/RepoData/PrefixRecord、sharded repodata 分片机制 |

### ⚙️ 核心业务逻辑

| 文档 | 说明 |
|------|------|
| [依赖求解](concepts/06-solving-dependencies.md) | SolverImpl trait、libsolv C后端与resolvo Rust后端、channel priority、ExcludeNewer安全策略 |
| [Repodata 网关](concepts/07-repodata-gateway.md) | Gateway高级API、多级缓存、分片加载、zstd增量补丁、进度报告 |
| [包流式处理](concepts/08-package-streaming.md) | .conda/.tar.bz2双格式支持、异步下载、Range请求、哈希校验 |
| [安装事务](concepts/09-install-and-transaction.md) | Transaction规划、hardlink/symlink/copy链接、Python entry points、Apple codesign |
| [Shell 激活与环境执行](concepts/10-shell-activation.md) | Bash/Zsh/Fish/PowerShell/CmdExe多shell支持、嵌套激活、run_in_environment |

### 🔧 系统能力

| 文档 | 说明 |
|------|------|
| [虚拟包检测](concepts/11-virtual-packages.md) | __cuda/__glibc/__linux/__archspec等系统能力检测、环境变量覆盖、交叉编译场景 |
| [网络/缓存/配置](concepts/12-networking-cache-config.md) | OAuth认证/S3/GCS中间件、重试策略、包缓存、.condarc兼容配置 |
| [锁文件与多语言绑定](concepts/13-lock-files-and-bindings.md) | conda-lock格式v3-v7、py-rattler异步API、@conda-org/rattler WASM绑定、CLI命令 |

## 实用示例

| 示例 | 难度 | 说明 |
|------|------|------|
| [基础求解与安装](examples/basic-solve-install.md) | ⭐⭐ | 从零创建Python环境的完整Rust代码，含Cargo.toml和Python等效版本 |
| [虚拟包检测](examples/virtual-package-detection.md) | ⭐ | 自动检测、环境变量覆盖、交叉编译自定义、CUDA缓存 |
| [Repodata 获取与缓存](examples/repodata-fetch-cache.md) | ⭐⭐ | Gateway查询、缓存管理、进度报告 |

## 信源登记

| 信源 | 说明 |
|------|------|
| [Rattler 源码结构参考](references/rattler-source.md) | 仓库目录结构、30个crate分层列表、Python/JS绑定目录、开发命令 |

## 适合人群

- **包管理工具开发者**：想在Rust/Python/JS程序中集成conda包管理能力
- **pixi/rattler-build 贡献者**：理解底层库的架构和API设计
- **conda 生态研究者**：对比Rust实现与Python版conda的架构差异
- **Rust 学习者**：学习大型Rust workspace项目的组织方式和最佳实践

## 前置知识

- conda 基本概念（channel、package、environment、prefix）
- Rust 基础语法（阅读Rust API示例时）
- Python asyncio（使用Python绑定时）

```{toctree}
:hidden:

concepts/index
examples/index
references/index
```
