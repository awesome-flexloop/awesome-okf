# 核心概念文档

本目录包含 Rattler 的核心概念文档，按学习路径排列。建议按编号顺序阅读。

## 入门篇

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [Rattler 简介](00-introduction.md) | Rattler 是什么、与 conda/mamba/pixi 的关系、核心能力概览 |
| 01 | [5分钟快速上手](01-getting-started.md) | 四种使用方式：CLI体验、Rust库集成、Python绑定、JS绑定 |

## 架构篇

| 编号 | 文档 | 说明 |
|------|------|------|
| 02 | [Crates 分层架构](02-crates-architecture.md) | 30个crate的四层架构图、各层职责、依赖方向规则 |

## 数据模型篇

| 编号 | 文档 | 说明 |
|------|------|------|
| 03 | [基础类型系统](03-conda-types-foundation.md) | PackageName/Platform/Version/Channel 等核心数据类型 |
| 04 | [MatchSpec 查询语言与版本约束](04-matchspec-and-versionspec.md) | MatchSpec 语法、VersionSpec/StringMatcher/BuildNumberSpec |
| 05 | [包记录与 RepoData](05-package-records-and-repodata.md) | PackageRecord/RepoDataRecord/PrefixRecord/Sharded Repodata |

## 核心业务篇

| 编号 | 文档 | 说明 |
|------|------|------|
| 06 | [依赖求解](06-solving-dependencies.md) | SolverImpl trait、libsolv_c/resolvo 两种后端、求解配置 |
| 07 | [Repodata 网关](07-repodata-gateway.md) | Gateway API、缓存机制、分片repodata、增量更新 |
| 08 | [包流式处理](08-package-streaming.md) | .conda/.tar.bz2 格式、异步下载、哈希校验 |
| 09 | [安装事务](09-install-and-transaction.md) | Transaction/Installer、文件链接、entry points、clobber处理 |
| 10 | [Shell 激活与环境执行](10-shell-activation.md) | 多shell激活脚本生成、在环境中执行命令、嵌套激活 |

## 系统能力篇

| 编号 | 文档 | 说明 |
|------|------|------|
| 11 | [虚拟包检测](11-virtual-packages.md) | OS/CUDA/glibc/CPU 微架构检测、环境变量覆盖、交叉编译 |
| 12 | [网络/缓存/配置](12-networking-cache-config.md) | HTTP中间件栈、多级缓存、.condarc兼容配置 |
| 13 | [锁文件与多语言绑定](13-lock-files-and-bindings.md) | LockFile格式、Python/JS绑定、CLI工具、包上传 |

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-crates-architecture
03-conda-types-foundation
04-matchspec-and-versionspec
05-package-records-and-repodata
06-solving-dependencies
07-repodata-gateway
08-package-streaming
09-install-and-transaction
10-shell-activation
11-virtual-packages
12-networking-cache-config
13-lock-files-and-bindings
```
