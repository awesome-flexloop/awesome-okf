---
okf_version: "0.2"
type: "example"
title: "自定义虚拟包"
sources:
  - "conda_lock/virtual_package.py"
  - "conda_lock/content_hash.py"
---

# 自定义虚拟包

本示例演示如何通过 `--virtual-package-spec` 选项和 `virtual-packages.yaml` 配置文件来自定义虚拟包，精确控制 CUDA 版本、glibc 版本、macOS 版本等系统依赖约束，确保锁文件与目标运行环境匹配。

相关概念：[虚拟包系统](../concepts/10-virtual-packages.md)、[跨平台锁定策略](../concepts/15-cross-platform-locking.md)、[内容哈希机制](../concepts/12-content-hash.md)。

## 场景说明

不同运行环境有不同的系统级约束：

| 场景 | 关键虚拟包 | 默认值 | 需要自定义的原因 |
|------|-----------|--------|----------------|
| GPU 服务器 | __cuda | 无 | CUDA 版本决定 GPU 包版本 |
| Ubuntu 22.04 | __glibc | 2.17 | 系统 glibc 2.35，可用更新的包 |
| CentOS 7 | __glibc | 2.17 | 默认值即可（2.17 = CentOS 7） |
| macOS Ventura | __osx | 11.0 | 需要 __osx>=13.0 的包 |
| AWS Graviton | __archspec | x86_64 | 需要 aarch64/arm64 架构 |

## 完整示例

### 示例 1：锁定 CUDA 版本（GPU 环境）

创建虚拟包配置文件锁定 CUDA 12.1：

```yaml
# virtual-packages-cuda.yaml
subdirs:
  linux-64:
    packages:
      __unix:
        version: "0"
        build_string: "0"
      __linux:
        version: "0"
        build_string: "0"
      __glibc:
        version: "2.28"
        build_string: "0"
      __archspec:
        version: "1"
        build_string: "x86_64"
      __cuda:
        version: "12.1"
        build_string: "0"
```

创建环境文件：

```yaml
# gpu-env.yml
channels:
  - conda-forge
  - nvidia
dependencies:
  - python=3.10
  - pytorch
  - pytorch-cuda=12.1
  - torchvision
  - pip
  - pip:
      - transformers>=4.30
platforms:
  - linux-64
```

执行锁定：

```bash
conda-lock lock -f gpu-env.yml \
  --virtual-package-spec virtual-packages-cuda.yaml \
  --mamba
```

引用事实：
- [F-001] __cuda 虚拟包告知 conda 求解器目标系统的 CUDA 版本
- [F-002] conda-forge 的 pytorch 包根据 __cuda 版本选择正确的 CUDA 变体
- [F-003] virtual_package_repo_from_specification() 从 YAML 文件加载虚拟包配置

验证 CUDA 版本：

```bash
# 查看锁文件中是否包含 CUDA 相关包
grep -i "cuda\|cudnn\|nccl" conda-lock.yml | head -20

# 确认 pytorch 的 CUDA 变体
grep -A5 "name: pytorch" conda-lock.yml | grep "version\|build"
```

### 示例 2：为旧系统保守锁定（CentOS 7）

CentOS 7 的 glibc 版本是 2.17（conda-lock 默认值），如果需要确保在更旧系统上运行，可以显式声明：

```yaml
# virtual-packages-centos7.yaml
subdirs:
  linux-64:
    packages:
      __unix:
        version: "0"
      __linux:
        version: "0"
      __glibc:
        version: "2.17"      # CentOS 7 自带 glibc 2.17
      __archspec:
        version: "1"
        build_string: "x86_64"
```

```bash
# 保守锁定，确保兼容 CentOS 7
conda-lock lock -f environment.yml \
  --virtual-package-spec virtual-packages-centos7.yaml
```

引用事实：
- [F-004] 默认 __glibc=2.17 就是面向 CentOS 7 兼容性的保守选择
- [F-005] 更低版本的 glibc 限制了可用的包版本（某些新包需要 glibc>=2.28）

### 示例 3：为现代 Linux 系统锁定（Ubuntu 22.04）

Ubuntu 22.04 使用 glibc 2.35，可以使用更新的包：

```yaml
# virtual-packages-ubuntu2204.yaml
subdirs:
  linux-64:
    packages:
      __unix:
        version: "0"
      __linux:
        version: "0"
      __glibc:
        version: "2.35"      # Ubuntu 22.04
      __archspec:
        version: "1"
        build_string: "x86_64"
  linux-aarch64:
    packages:
      __unix:
        version: "0"
      __linux:
        version: "0"
      __glibc:
        version: "2.35"
      __archspec:
        version: "1"
        build_string: "aarch64"  # ARM64 服务器（如 AWS Graviton）
```

```bash
# 面向 Ubuntu 22.04 锁定（x86_64 + ARM64）
conda-lock lock -f environment.yml \
  --virtual-package-spec virtual-packages-ubuntu2204.yaml \
  -p linux-64 -p linux-aarch64 \
  --mamba
```

引用事实：
- [F-006] __glibc=2.35 允许选择需要更新 glibc 的包版本
- [F-007] linux-aarch64 平台的 __archspec build_string 必须是 "aarch64"

### 示例 4：macOS 版本控制

```yaml
# virtual-packages-macos.yaml
subdirs:
  osx-64:
    packages:
      __unix:
        version: "0"
      __osx:
        version: "10.15"     # Catalina 兼容
      __archspec:
        version: "1"
        build_string: "x86_64"
  osx-arm64:
    packages:
      __unix:
        version: "0"
      __osx:
        version: "13.0"     # Ventura（Apple Silicon 最低 11.0）
      __archspec:
        version: "1"
        build_string: "arm64"
```

引用事实：
- [F-008] __osx 版本控制 macOS 包的最低系统版本要求
- [F-009] osx-arm64（Apple Silicon）的 __osx 最低版本通常是 11.0 (Big Sur)

### 示例 5：组合场景（多平台多 CUDA）

```yaml
# virtual-packages-full.yaml
subdirs:
  # Linux x86_64 + CUDA 12.1
  linux-64:
    packages:
      __unix:
        version: "0"
      __linux:
        version: "0"
      __glibc:
        version: "2.28"
      __archspec:
        version: "1"
        build_string: "x86_64"
      __cuda:
        version: "12.1"

  # Linux ARM64（无 GPU，如 AWS Graviton）
  linux-aarch64:
    packages:
      __unix:
        version: "0"
      __linux:
        version: "0"
      __glibc:
        version: "2.28"
      __archspec:
        version: "1"
        build_string: "aarch64"

  # macOS Apple Silicon
  osx-arm64:
    packages:
      __unix:
        version: "0"
      __osx:
        version: "12.0"
      __archspec:
        version: "1"
        build_string: "arm64"

  # Windows
  win-64:
    packages:
      __win:
        version: "0"
      __archspec:
        version: "1"
        build_string: "x86_64"
```

```bash
conda-lock lock -f environment.yml \
  --virtual-package-spec virtual-packages-full.yaml \
  -p linux-64 -p linux-aarch64 -p osx-arm64 -p win-64 \
  --mamba
```

## 虚拟包参考

### 支持的虚拟包列表

| 虚拟包名 | 平台 | 典型值 | 说明 |
|---------|------|--------|------|
| `__unix` | Linux/macOS | `"0"` | Unix 系操作系统标记 |
| `__linux` | Linux | `"0"` | Linux 内核标记 |
| `__osx` | macOS | `"10.15"`, `"11.0"`, `"12.0"`, `"13.0"` | macOS 版本 |
| `__win` | Windows | `"0"` | Windows 标记 |
| `__glibc` | Linux | `"2.17"`, `"2.28"`, `"2.35"` | glibc 版本 |
| `__cuda` | Linux (GPU) | `"11.8"`, `"12.1"`, `"12.3"` | CUDA 版本 |
| `__archspec` | 所有平台 | 见下 | CPU 架构 |

[F-010]

### __archspec build_string 值

| 架构 | build_string | 平台 |
|------|-------------|------|
| x86_64 / AMD64 | `"x86_64"` | linux-64, osx-64, win-64 |
| ARM64 / aarch64 | `"aarch64"` | linux-aarch64 |
| Apple Silicon | `"arm64"` | osx-arm64 |
| POWER9/10 | `"ppc64le"` | linux-ppc64le |

## 验证虚拟包效果

使用 Python API 验证虚拟包配置：

```python
"""
验证虚拟包配置生成的 FakeRepoData。

引用事实：
[F-011] virtual_package_repo_from_specification() 加载 YAML 配置
[F-012] FakeRepoData.url 返回 file:// URL 作为额外通道
[F-013] 上下文管理器自动设置/清理 CONDA_OVERRIDE_* 环境变量
"""

from conda_lock.virtual_package import virtual_package_repo_from_specification

with virtual_package_repo_from_specification("virtual-packages-cuda.yaml") as repo:
    print(f"Fake repo URL: {repo.url}")
    print(f"Virtual packages:")
    for pkg in repo.virtual_packages:
        print(f"  {pkg.subdir}: {pkg.name}={pkg.version}={pkg.build_string}")

    # 检查环境变量是否设置
    import os
    print(f"\nCONDA_OVERRIDE_CUDA = {os.environ.get('CONDA_OVERRIDE_CUDA', 'NOT SET')}")
    print(f"CONDA_OVERRIDE_GLIBC = {os.environ.get('CONDA_OVERRIDE_GLIBC', 'NOT SET')}")
```

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| CUDA 包版本不对 | 未设置 __cuda 或版本不匹配 | 设置正确的 __cuda 版本 |
| 包安装后 GLIBC 报错 | __glibc 版本高于目标系统 | 降低 __glibc 版本到目标系统值 |
| osx-arm64 包缺失 | __osx 版本过高/过低 | 调整 __osx 版本（Apple Silicon 最低 11.0） |
| 虚拟包不生效 | YAML 格式错误 | 检查缩进、subdirs 名称、version 是字符串 |
| 内容哈希变化 | 修改虚拟包配置后哈希改变 | 这是正常的，需要提交新锁文件 |

引用事实：
- [F-014] 修改虚拟包配置会改变内容哈希，因为虚拟包参与哈希计算
- [F-015] FakeRepoData 作为额外 --channel file:// URL 传给 conda

## 相关概念

- [虚拟包系统](../concepts/10-virtual-packages.md)
- [跨平台锁定策略](../concepts/15-cross-platform-locking.md)
- [内容哈希机制](../concepts/12-content-hash.md)
- [Conda 求解器](../concepts/08-conda-solver.md)
- [多平台锁定示例](multi-platform-lock.md)
