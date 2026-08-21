---
type: "concept"
title: "Rattler 简介"
sources:
  - id: rattler-readme
    resource: /references/rattler-source.md
    title: "Rattler README & Crates 结构"
---

# Rattler 简介

## 什么是 Rattler

Rattler 是一个使用 **Rust** 编写的高性能 conda 包管理库集合 [F-001]。它提供了 conda 生态系统中常见功能的 Rust 实现，目标是让非 Python 程序也能方便地与 conda 生态交互 [F-002]。Rattler 采用 BSD-3-Clause 开源许可证，由 prefix.dev 团队主导开发，是 [pixi](https://github.com/prefix-dev/pixi)、[rattler-build](https://github.com/prefix-dev/rattler-build) 和 [prefix.dev](https://prefix.dev) 后端的核心引擎 [F-003]。

Rattler 的核心定位可以概括为三点：

1. **Rust 原生 conda 库**：Rattler 不是 conda 的重写（rewrite），而是一组可复用的 Rust 库，提供 conda 生态的核心能力——依赖求解、包下载/安装、环境激活、虚拟包检测等 [F-002]。与 Python 版 conda 不同，Rattler 从一开始就设计为"库优先"（library-first），便于嵌入其他工具。

2. **多语言绑定**：除了 Rust 原生 API，Rattler 还提供了 **Python 绑定**（py-rattler，通过 PyO3）和 **JavaScript/WASM 绑定**（@conda-org/rattler，通过 wasm-bindgen），使得 Python 和 Node.js/浏览器环境也能使用 Rattler 的能力 [F-004]。

3. **高性能**：使用 Rust 编写带来了内存安全和并发性能优势。依赖求解支持两种后端：libsolv（C 库，通过 FFI 调用，与 mamba 使用同一求解器）和 resolvo（Rust 原生求解器，支持取消令牌）[F-005]。

## 与 conda / mamba / pixi 的关系

| 工具 | 语言 | 定位 | 与 Rattler 的关系 |
|------|------|------|------------------|
| **conda** | Python | 通用包管理器+环境管理器 | Rattler 不替代 conda，而是提供与 conda 兼容的库能力 |
| **mamba** | C++/Python | conda 的 C++ 高性能 drop-in 替代 | 两者都使用 libsolv 求解器，但 Rattler 是纯 Rust 实现（libsolv 通过 FFI 调用） |
| **pixi** | Rust | 跨语言包管理工具（类似 cargo/npm for conda） | pixi 是 Rattler 的主要用户，直接依赖 rattler 系列 crates |
| **rattler-build** | Rust | conda 包构建工具 | 使用 rattler 库处理包的解析和依赖 |

**关键区分**：conda 是一个完整的包管理**工具**，而 Rattler 是一组**库**（library），专门用于在其他工具中集成 conda 生态功能 [F-002]。

## 核心能力概览

Rattler 通过多个专项 crate 提供以下核心能力：

- **数据类型**（rattler_conda_types）：Version、Platform、MatchSpec、Channel、PackageRecord、RepoData 等 conda 核心数据模型的解析和序列化 [F-006]
- **依赖求解**（rattler_solve）：SolverImpl trait，支持 libsolv_c 和 resolvo 两种后端，支持取消令牌和排除新包安全策略 [F-005]
- **包流式处理**（rattler_package_streaming）：conda 包（.conda/.tar.bz2 格式）的下载、解压、读取和创建，含哈希校验 [F-007]
- **Repodata 网关**（rattler_repodata_gateway）：repodata.json 的下载、缓存、分片（sharded repodata），高级 Gateway API 支持多 channel 并发 [F-008]
- **环境激活**（rattler_shell）：为不同 shell（bash/zsh/fish/cmd.exe/PowerShell）生成激活脚本，在指定环境中执行命令 [F-009]
- **虚拟包检测**（rattler_virtual_packages）：自动检测系统能力（CUDA 版本、glibc 版本、OS 版本、CPU 微架构等）[F-010]
- **网络层**（rattler_networking）：OAuth 认证、S3/GCS/OCI 中间件、重试策略、镜像支持 [F-011]
- **锁文件**（rattler_lock）：conda 环境 lockfile 的解析和生成（支持 v3/v5/v6/v7 多种格式版本）[F-012]
- **安装事务**（rattler）：高层安装 API，支持 hardlink/symlink/copy 链接策略、Python entry points 生成、Apple codesign [F-013]

## Python 绑定快速示例

py-rattler 提供了基于 asyncio 的异步 API，以下是求解并安装环境的最小示例：

```python
import asyncio
import tempfile
from rattler import solve, install, VirtualPackage

async def main() -> None:
    # 求解环境
    solved_records = await solve(
        channels=["conda-forge"],
        specs=["python ~=3.12.0", "pip", "requests 2.31.0"],
        virtual_packages=VirtualPackage.detect(),
    )

    # 安装到临时目录
    env_path = tempfile.mkdtemp()
    await install(
        records=solved_records,
        target_prefix=env_path,
    )
    print(f"环境已创建: {env_path}")

asyncio.run(main())
```

这个示例展示了 Rattler 的核心工作流：**虚拟包检测 → 依赖求解 → 安装到前缀**，三个核心 API 调用即可从零创建一个可用的 conda 环境。

## 开源许可证

Rattler 采用 **BSD-3-Clause** 许可证发布，项目托管于 GitHub（https://github.com/conda/rattler）。

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [Crates 分层架构](02-crates-architecture.md)
- [基础类型系统](03-conda-types-foundation.md)
