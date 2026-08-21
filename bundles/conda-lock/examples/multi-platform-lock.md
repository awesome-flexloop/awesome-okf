---
okf_version: "0.2"
type: "example"
title: "多平台锁定"
sources:
  - "conda_lock/conda_solver.py"
  - "conda_lock/virtual_package.py"
  - "conda_lock/invoke_conda.py"
  - "conda_lock/src_parser/selectors.py"
---

# 多平台锁定

本示例演示如何使用 conda-lock 为多个目标平台（Linux、macOS、Windows）生成跨平台锁文件。通过平台选择器处理平台特定依赖，通过虚拟包模拟目标系统属性。

相关概念：[跨平台锁定策略](../concepts/15-cross-platform-locking.md)、[虚拟包系统](../concepts/10-virtual-packages.md)、[Conda 求解器](../concepts/08-conda-solver.md)。

## 完整示例

### 步骤 1：创建含平台特定依赖的 environment.yml

```yaml
# environment.yml
name: cross-platform-app
channels:
  - conda-forge
dependencies:
  # 跨平台通用依赖
  - python=3.10
  - numpy>=1.24
  - pandas>=2.0
  - pip

  # macOS 特定依赖（Accelerate 框架）
  - llvm-openmp  # [osx]

  # Linux 特定依赖（OpenMP 运行时）
  - libgomp      # [linux]

  # Windows 特定依赖
  - pywin32      # [win]
  - m2w64-gcc-libgfortran  # [win]

  # x86_64 特定依赖（Intel MKL）
  - mkl_random   # [x86_64]

  # pip 包（含平台标记）
  - pip:
      - requests>=2.28
      - pydantic>=2.0
      - pywin32>=306; sys_platform == "win32"
      - importlib-metadata; python_version < "3.10"

# 目标平台列表
platforms:
  - linux-64
  - linux-aarch64
  - osx-64
  - osx-arm64
  - win-64
```

引用事实：
- [F-001] `# [osx]`/`# [linux]`/`# [win]` 是 conda-build 风格的平台选择器
- [F-002] `# [x86_64]` 是架构选择器，适用于 linux-64 和 osx-64
- [F-003] pip 依赖的 `sys_platform == "win32"` 是 PEP 508 环境标记
- [F-004] platforms 字段支持 linux-aarch64（ARM64 Linux，如 AWS Graviton）和 osx-arm64（Apple Silicon）

### 步骤 2：执行多平台锁定

```bash
# 方式一：使用 environment.yml 中的 platforms 字段
conda-lock lock -f environment.yml --mamba

# 方式二：命令行覆盖平台列表
conda-lock lock -f environment.yml \
  -p linux-64 -p osx-arm64 -p win-64 \
  --mamba

# 方式三：全平台锁定
conda-lock lock -f environment.yml \
  -p linux-64 -p linux-aarch64 -p osx-64 -p osx-arm64 -p win-64 \
  --mamba
```

执行过程中，conda-lock 会依次为每个平台求解：

```
Locking dependencies for ['linux-64', 'linux-aarch64', 'osx-64', 'osx-arm64', 'win-64']...
  ├─ linux-64: ... done (23 packages)
  ├─ linux-aarch64: ... done (22 packages)
  ├─ osx-64: ... done (24 packages)
  ├─ osx-arm64: ... done (22 packages)
  └─ win-64: ... done (26 packages)
```

引用事实：
- [F-005] 每个平台通过 CONDA_SUBDIR 环境变量覆盖独立求解
- [F-006] 虚拟包系统自动为每个平台注入 __glibc/__osx/__win 等系统依赖
- [F-007] --mamba 使用 mamba 后端，多平台锁定时速度优势更明显

### 步骤 3：验证锁文件中的平台差异

```bash
# 查看每个平台的包数量
echo "=== 各平台包数量 ==="
for plat in linux-64 linux-aarch64 osx-64 osx-arm64 win-64; do
  count=$(grep -A2 "platform: $plat" conda-lock.yml | grep -c "name:")
  echo "  $plat: $count packages"
done

# 查看平台特定包
echo ""
echo "=== Linux 特有包 ==="
grep -B5 "platform: linux-64" conda-lock.yml | grep "name: libgomp" || true

echo "=== macOS 特有包 ==="
grep -B5 "platform: osx-arm64" conda-lock.yml | grep "name: llvm-openmp" || true

echo "=== Windows 特有包 ==="
grep -B5 "platform: win-64" conda-lock.yml | grep "name: pywin32" || true
```

你会发现：
- `libgomp` 仅出现在 linux-* 平台
- `llvm-openmp` 仅出现在 osx-* 平台
- `pywin32` 仅出现在 win-64 平台
- `mkl_random` 仅出现在 linux-64 和 osx-64（x86_64 架构）
- 纯 Python 包（requests/pydantic）在所有平台都有相同版本

引用事实：
- [F-008] platform selectors 在解析阶段按平台过滤，不适用的依赖不会传给求解器
- [F-009] 每个包记录通过 platform 字段标记适用平台

### 步骤 4：在各平台上安装

**在 Linux x86_64 上：**
```bash
conda-lock install --name cross-platform-app conda-lock.yml
# 自动选择 platform: linux-64 的包
```

**在 macOS Apple Silicon 上：**
```bash
conda-lock install --name cross-platform-app conda-lock.yml
# 自动选择 platform: osx-arm64 的包
```

**在 Windows 上（PowerShell）：**
```powershell
conda-lock install --name cross-platform-app conda-lock.yml
# 自动选择 platform: win-64 的包
```

引用事实：
- [F-010] install 命令自动检测当前平台，选择对应 platform 字段的包记录

### 步骤 5：渲染各平台 explicit 文件

```bash
# 渲染所有平台的 explicit 文件
conda-lock render --kind explicit

# 输出：
# conda-linux-64.lock
# conda-linux-aarch64.lock
# conda-osx-64.lock
# conda-osx-arm64.lock
# conda-win-64.lock

# 仅渲染特定平台
conda-lock render --kind explicit -p linux-64 -p osx-arm64
```

explicit 文件可用于 CI/CD 快速创建环境：

```bash
# CI 中使用 explicit 文件
conda create --name ci-env --file conda-linux-64.lock
```

## 使用自定义虚拟包精确控制系统版本

对于需要特定 glibc 版本的场景，使用自定义虚拟包配置：

```yaml
# virtual-packages.yaml
subdirs:
  linux-64:
    packages:
      __unix:
        version: "0"
      __linux:
        version: "0"
      __glibc:
        version: "2.28"     # 要求 glibc >= 2.28（如 Ubuntu 20.04）
      __archspec:
        version: "1"
        build_string: "x86_64"
      __cuda:
        version: "11.8"     # CUDA 11.8
  osx-arm64:
    packages:
      __unix:
        version: "0"
      __osx:
        version: "13.0"     # macOS Ventura 最低版本
      __archspec:
        version: "1"
        build_string: "arm64"
```

```bash
# 使用自定义虚拟包锁定
conda-lock lock -f environment.yml \
  --virtual-package-spec virtual-packages.yaml \
  --mamba
```

引用事实：
- [F-011] --virtual-package-spec 指定自定义虚拟包 YAML 文件
- [F-012] __glibc 版本控制影响 Linux 包的选择（更高版本允许更新的包）
- [F-013] __cuda 版本影响 CUDA 相关包（如 cupy、pytorch）的版本选择

## 验证跨平台一致性

使用以下脚本快速验证锁文件中各平台核心包版本一致：

```bash
#!/bin/bash
# check-cross-platform.sh
echo "检查核心包跨平台版本一致性..."
for pkg in python numpy pandas requests pydantic; do
  versions=$(grep -A2 "name: $pkg$" conda-lock.yml | \
             grep "version:" | awk '{print $2}' | sort -u)
  if [ $(echo "$versions" | wc -l) -eq 1 ]; then
    echo "  ✓ $pkg: $versions (跨平台一致)"
  else
    echo "  ✗ $pkg: 版本不一致"
    echo "$versions" | sed 's/^/      /'
  fi
done
```

## 注意事项

1. **求解时间**：5 个平台约 5 倍单平台时间，使用 `--mamba` 显著加速
2. **网络需求**：需要下载所有平台的 repodata.json，确保网络通畅
3. **glibc 版本**：默认 `__glibc=2.17`（CentOS 7），如果生产环境更新，通过虚拟包指定更高版本
4. **CUDA 包**：CUDA 相关包体积大、版本敏感，建议通过虚拟包明确 CUDA 版本
5. **osx-arm64 兼容性**：部分 conda 包尚未提供 osx-arm64 构建，可通过 osx-64 通过 Rosetta 2 运行
6. **锁文件体积**：5 平台锁文件可能包含数百个包记录，属正常现象

## 相关概念

- [跨平台锁定策略](../concepts/15-cross-platform-locking.md)
- [虚拟包系统](../concepts/10-virtual-packages.md)
- [Conda 调用层](../concepts/13-invoke-conda.md)
- [源文件解析](../concepts/07-source-parsers.md)
- [自定义虚拟包示例](custom-virtual-packages.md)
