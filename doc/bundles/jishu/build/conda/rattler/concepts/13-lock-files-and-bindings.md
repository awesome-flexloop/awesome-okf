---
type: "concept"
title: "锁文件与多语言绑定"
sources:
  - id: rattler-lock-bindings
    resource: /references/rattler-source.md
    title: "Rattler Crates 结构 - rattler_lock/py-rattler/js-rattler"
---

# 锁文件与多语言绑定

本文档覆盖两个主题：`rattler_lock` 锁文件格式，以及 Rattler 的 Python 和 JavaScript 绑定。

## 锁文件（rattler_lock）

锁文件（lockfile）记录了一次成功求解的完整包列表及其精确版本、哈希和来源 URL。与 `repodata.json` 不同，锁文件是确定性的——相同锁文件在任何机器上都能重现完全相同的环境。这对于可复现构建和 CI/CD 至关重要。

### 为什么需要锁文件

- **环境可复现**：确保团队成员、CI 和生产环境使用完全相同的包版本
- **避免"在我机器上能跑"**：`environment.yml` 只声明范围约束（如 `numpy>=1.24`），不同时间求解可能得到不同版本
- **快速安装**：有了锁文件，不需要重新求解，直接下载安装指定版本
- **安全审计**：锁定版本后可以精确审计使用的包和其依赖

### LockFile 格式

Rattler 的锁文件格式与 [conda-lock](https://github.com/conda/conda-lock) 兼容，支持多个版本：

| 版本 | 格式 | 说明 |
|------|------|------|
| v3 | YAML | conda-lock 原始格式 |
| v5 | YAML | 增加元数据 |
| v6 | YAML | Conda 和 PyPI 包统一格式 |
| v7 | YAML/JSON | 最新版本，支持 content hash 和更多元数据 |

锁文件示例（简化）：

```yaml
version: 6
metadata:
  content_hash:
    linux-64: abc123def456...
    osx-arm64: 789abc012def...
  channels:
    - url: https://conda.anaconda.org/conda-forge/
      used_env_vars: []
  platforms:
    - linux-64
    - osx-arm64
package:
  - name: python
    version: "3.12.1"
    manager: conda
    platform: linux-64
    dependencies:
      - libffi >=3.4,<4.0a0
      - libsqlite >=3.44.2,<4.0a0
      - openssl >=3.2.0,<4.0a0
    url: https://conda.anaconda.org/conda-forge/linux-64/python-3.12.1-hab00c5b_1_cpython.conda
    hash:
      md5: abc123...
      sha256: def456...
    category: main
    optional: false
  - name: numpy
    version: "1.26.3"
    manager: conda
    platform: linux-64
    dependencies:
      - libopenblas >=0.3.25,<0.3.26.0a0
      - python >=3.12,<3.13.0a0
      - python_abi 3.12.* *_cp312
    url: https://conda.anaconda.org/conda-forge/linux-64/numpy-1.26.3-py312hb2c83b4_0.conda
    hash:
      md5: xyz789...
      sha256: uvw012...
```

### LockFile API

```rust
use rattler_lock::{LockFile, Channel, Package};

// 从文件加载锁文件
let lock_file = LockFile::from_path("pixi.lock")?;

// 构造锁文件（Builder 模式）
let lock_file = LockFile::builder()
    .with_channels(vec![channel1, channel2])
    .with_platforms(vec![Platform::Linux64, Platform::OsxArm64])
    .with_packages(vec![pkg1, pkg2])
    .build()?;

// 查询特定平台的包
let linux_packages: Vec<_> = lock_file
    .packages(Platform::Linux64)
    .filter(|p| !p.optional)
    .collect();

for pkg in linux_packages {
    println!("{}={} ({})", pkg.name, pkg.version, pkg.url);
}

// 序列化回 YAML/JSON
lock_file.to_path("pixi.lock")?;
```

### Conda 包与 PyPI 包

锁文件支持两种类型的包：
- **Conda 包**（`manager: conda`）：从 conda channel 安装的二进制包
- **PyPI 包**（`manager: pypi`）：从 PyPI 安装的 Python wheel/sdist

这允许 conda 包和 pip 包混合锁定，pixi 等工具使用此特性实现 conda+pip 的统一锁定。

### content_hash

`metadata.content_hash` 是对输入（specs、channels、platforms）的哈希，用于检测输入是否变化。如果 content_hash 变了，说明需要重新求解。

## Python 绑定（py-rattler）

`py-rattler/` 目录包含使用 PyO3 构建的 Python 绑定。

### 主要模块和类

| Rust 类型 | Python 类 | 说明 |
|-----------|----------|------|
| `solve()` | `rattler.solve()` | 一键求解（异步函数） |
| `install()` | `rattler.install()` | 一键安装（异步函数） |
| `Gateway` | `rattler.Gateway` | Repodata 网关 |
| `Channel` | `rattler.Channel` | Channel 表示 |
| `MatchSpec` | `rattler.MatchSpec` | 包匹配规格 |
| `Version` | `rattler.Version` | 版本号 |
| `Platform` | `rattler.Platform` | 平台枚举 |
| `PackageRecord` | `rattler.PackageRecord` | 包元数据 |
| `RepoDataRecord` | `rattler.RepoDataRecord` | 带 URL 的包记录 |
| `VirtualPackage` | `rattler.VirtualPackage` | 虚拟包 |
| `PrefixRecord` | `rattler.PrefixRecord` | 已安装包记录 |
| `Activator` | `rattler.Activator` | Shell 激活器 |

### Python API 设计特点

1. **异步优先**：网络操作（solve、install、load_repodata）都是 async 函数，基于 Python asyncio
2. **类型安全**：PyO3 自动转换 Rust 强类型为 Python 类型
3. **无需手动管理 tokio**：内部使用 pyo3-asyncio 桥接 tokio 和 asyncio
4. **Pythonic 命名**：方法名使用 snake_case（如 `detect()` 而非 `detect` 之外的约定）

### 安装和使用

```bash
# 通过 conda-forge 安装
conda install -c conda-forge py-rattler

# 或通过 pip（从源码构建）
pip install py-rattler
```

```python
import asyncio
from pathlib import Path
from rattler import solve, install, Gateway, Channel, Platform, VirtualPackage, MatchSpec

async def main():
    # 方式1：一键求解+安装
    records = await solve(
        channels=["conda-forge"],
        specs=["python ~=3.12.0", "numpy >=1.24", "pandas"],
        virtual_packages=VirtualPackage.detect(),
    )
    prefix = Path("./myenv")
    await install(records=records, target_prefix=prefix)

    # 方式2：使用 Gateway 精细控制
    gateway = Gateway()
    repodata = await gateway.load_repodata(
        channels=[Channel("conda-forge")],
        platforms=[Platform.current()],
        specs=["scipy"],
    )

asyncio.run(main())
```

### 文档

py-rattler 的文档在 `py-rattler/docs/` 目录下，使用 Markdown 格式，可通过 Sphinx 构建为 HTML。包含：
- 安装指南
- 快速入门教程
- API 参考
- 进阶用法（自定义 channel、认证、虚拟包）

## JavaScript / WASM 绑定（js-rattler）

`js-rattler/` 目录包含使用 wasm-bindgen 构建的 JavaScript/WASM 绑定，npm 包名 `@conda-org/rattler`。

### 支持的功能

由于 WASM 环境的限制（无文件系统、无线程），js-rattler 主要提供：
- 基础类型操作（Version 比较、Platform 枚举、PackageName 解析、MatchSpec 解析）
- 依赖求解（使用 resolvo 后端，纯 Rust WASM）
- Repodata 解析（JSON → 内存模型）

不支持（需要系统能力）：
- 包下载和安装
- 文件系统操作
- Shell 激活
- 虚拟包检测

### 构建产物

js-rattler 使用 Rollup 打包，支持：
- **ESM**（ES Modules）：`<script type="module">` 和 bundler 使用
- **CJS**（CommonJS）：Node.js require() 使用
- **Web bundles**：浏览器 `<script>` 标签直接使用
- **Node.js WASM**：Node.js 环境
- **Web WASM**：浏览器环境

### 使用示例

```javascript
import { Version, Platform, MatchSpec, PackageName } from '@conda-org/rattler';

// 版本比较
const v1 = new Version("1.2.3");
const v2 = new Version("1.2.10");
console.log(v1.compare(v2));  // -1 (1.2.3 < 1.2.10)

// 平台
console.log(Platform.current());  // e.g. "linux-64"

// 包名规范化
const name = new PackageName("My-Package");
console.log(name.as_normalized());  // "my-package"

// MatchSpec 解析
const spec = new MatchSpec("numpy >=1.24,<2.0");
console.log(spec.name);  // "numpy"
```

### 应用场景

js-rattler 被以下项目使用：
- [mambajs](https://github.com/emscripten-forge/mambajs)：在浏览器中求解 emscripten-forge 包
- [Quetz frontend](https://github.com/mamba-org/quetz)：conda channel 前端的依赖解析预览
- 在线包探索工具

## rattler_menuinst：菜单/快捷方式安装

`rattler_menuinst` 跨平台安装开始菜单快捷方式/桌面快捷方式：
- **Windows**：在开始菜单创建快捷方式（.lnk）
- **macOS**：创建 .app bundle
- **Linux**：创建 .desktop 文件（遵循 freedesktop.org 规范）

支持 menuinst v1 和 v2 schema（兼容 conda 的 menuinst 包）。

## rattler_upload：包上传

`rattler_upload` 支持将构建好的 conda 包上传到多个目标：
- **Anaconda.org**（anaconda-client 兼容）
- **Cloudsmith**
- **conda-forge**（通过 cf-staging 流程）
- **S3 bucket**
- **OCI registry**（容器镜像仓库）

支持 OCI attestation（SLSA 供应链安全等级 2+）。

## rattler_index：本地通道索引

`rattler_index` 用于创建本地 conda channel 的索引文件（repodata.json），用于搭建私有 channel：

```rust
use rattler_index::index;

index(
    Path::new("/path/to/channel/linux-64"),
    Some(progress_reporter),
).await?;
```

## rattler-bin：CLI 工具

`rattler-bin` 是使用所有 crate 构建的示例 CLI，提供以下子命令：

| 命令 | 功能 |
|------|------|
| `rattler create <packages>` | 创建新环境并安装包 |
| `rattler install <packages>` | 向现有环境安装包 |
| `rattler solve <specs>` | 求解依赖（不安装） |
| `rattler run -p <prefix> <cmd>` | 在环境中运行命令 |
| `rattler shell-hook` | 输出 shell 激活脚本 |
| `rattler list -p <prefix>` | 列出环境中已安装的包 |
| `rattler search <query>` | 搜索可用包 |
| `rattler auth login <channel>` | 登录私有 channel（OAuth） |

这是学习 rattler 各 crate 如何组合使用的最佳参考——它是 rattler API 的"集成测试"。

## 相关概念

- [Crates 分层架构](02-crates-architecture.md)
- [5分钟快速上手](01-getting-started.md)
- [依赖求解](06-solving-dependencies.md)
- [安装事务](09-install-and-transaction.md)
