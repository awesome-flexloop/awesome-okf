---
okf_version: "0.2"
type: "example"
title: "基础锁定工作流"
sources:
  - "conda_lock/conda_lock.py"
  - "conda_lock/lockfile/__init__.py"
  - "conda_lock/src_parser/environment_yaml.py"
---

# 基础锁定工作流

本示例演示 conda-lock 最基础的使用流程：创建 environment.yml → 生成锁文件 → 从锁文件安装环境。这是日常开发中最常用的工作流。

相关概念：[5分钟快速上手](../concepts/01-getting-started.md)、[CLI 命令体系](../concepts/11-cli-commands.md)、[锁文件 v1/v2 格式](../concepts/06-lockfile-formats.md)。

## 完整流程

### 步骤 1：准备 environment.yml

创建一个标准的 Conda 环境规格文件：

```yaml
# environment.yml
name: data-science
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy>=1.24
  - pandas>=2.0
  - scikit-learn>=1.3
  - matplotlib>=3.7
  - pip:
      - requests>=2.28
      - pydantic>=2.0
platforms:
  - linux-64
  - osx-arm64
  - win-64
```

引用事实：
- [F-001] environment.yml 支持 channels/dependencies/pip 子段等标准字段
- [F-002] platforms 是 conda-lock 扩展字段，指定目标锁定平台
- [F-003] pip 子段中的依赖解析为 manager="pip" 的 VersionedDependency

### 步骤 2：生成锁文件

```bash
# 基础用法（conda-lock 等同于 conda-lock lock）
conda-lock lock --file environment.yml

# 使用 mamba 后端加速求解
conda-lock lock -f environment.yml --mamba

# 指定输出文件路径
conda-lock lock -f environment.yml --lockfile ./locks/prod-env.yml
```

执行过程中，conda-lock 会：
1. 解析 environment.yml，构建 LockSpecification
2. 对每个目标平台调用 conda/mamba dry-run 求解 conda 依赖
3. 使用 Poetry 求解器求解 pip 依赖
4. 计算内容哈希
5. 写入 conda-lock.yml

引用事实：
- [F-004] lock 命令默认输出 conda-lock.yml，可通过 --lockfile 指定
- [F-005] --mamba 是 --conda mamba 的简写，使用更快的 mamba 后端
- [F-006] OrderedGroup 使 lock 成为默认子命令

### 步骤 3：查看生成的锁文件

```bash
# 查看锁文件前几行
head -30 conda-lock.yml

# 查看包含的平台
grep "platform:" conda-lock.yml | sort -u

# 查看包数量
grep -c "^  - name:" conda-lock.yml
```

锁文件结构示例：

```yaml
version: 2
metadata:
  content_hash:
    linux-64: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    osx-arm64: "a1b2c3d4e5f6..."
    win-64: "789abc012def..."
  channels:
    - url: "conda-forge"
  platforms:
    - linux-64
    - osx-arm64
    - win-64
  sources:
    - environment.yml
package:
  - name: python
    version: "3.10.12"
    manager: conda
    platform: linux-64
    dependencies:
      libffi: ">=3.4"
      openssl: ">=3.0"
    url: "https://conda.anaconda.org/conda-forge/linux-64/python-3.10.12-..."
    hash:
      md5: "d41d8cd98f00b204e9800998ecf8427e"
    build: "hd12c33a_0_cpython"
    categories:
      - main
  # ... 更多包
```

引用事实：
- [F-007] v2 格式默认使用 categories 集合
- [F-008] content_hash 按平台记录，用于快速变化检测

### 步骤 4：从锁文件安装环境

```bash
# 创建命名环境
conda-lock install --name data-science conda-lock.yml

# 激活环境
conda activate data-science

# 验证安装
python -c "import numpy, pandas, sklearn, requests, pydantic; print('OK')"

# 查看安装的精确版本
conda list | grep numpy
pip show pydantic
```

引用事实：
- [F-009] install 命令从锁文件读取精确 URL 和哈希安装
- [F-010] 安装时自动选择当前平台的包记录

### 步骤 5：（可选）渲染为其他格式

```bash
# 渲染为 explicit 格式（每个平台一个文件）
conda-lock render --kind explicit

# 生成的文件：
# conda-linux-64.lock
# conda-osx-arm64.lock
# conda-win-64.lock

# 使用 explicit 文件创建环境
conda create --name data-science --file conda-linux-64.lock
```

explicit 文件格式：

```
# platform: linux-64
@EXPLICIT
https://conda.anaconda.org/conda-forge/linux-64/python-3.10.12-hd12c33a_0_cpython.tar.bz2#d41d8cd9...
https://conda.anaconda.org/conda-forge/linux-64/numpy-1.24.4-py310h43ef7f0_0.conda#a1b2c3d4...
...
```

引用事实：
- [F-011] render 命令支持 explicit 和 env 两种输出格式
- [F-012] explicit 格式是 URL 列表，conda create --file 可直接使用

## 一键脚本

将完整工作流整合到 Makefile 或脚本中：

```makefile
# Makefile
LOCKFILE = conda-lock.yml
ENV_NAME = data-science

.PHONY: lock install update clean

lock:
	conda-lock lock -f environment.yml --mamba

install:
	conda-lock install --name $(ENV_NAME) $(LOCKFILE)

update:
	conda-lock lock --update -f environment.yml --mamba

clean:
	rm -f $(LOCKFILE) conda-*.lock
```

```bash
# 使用
make lock      # 生成锁文件
make install   # 安装环境
make update    # 更新依赖
```

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 求解太慢 | 使用 `--mamba` 切换到 mamba 后端，速度提升数倍 |
| 锁文件不在 git 中 | 建议将 `conda-lock.yml` 提交到版本控制，`conda-*.lock` 可 gitignore |
| pip 包版本冲突 | 确保 pip 依赖版本约束与 conda 包兼容；检查是否有 conda 包替代 |
| 需要添加新依赖 | 修改 environment.yml，重新运行 `conda-lock lock`（非 lock --update） |
| 想固定到旧版本 | 在 environment.yml 中使用精确版本号，如 `numpy=1.24.3` |

## 工作流总结

```
environment.yml (编辑)
      │
      ▼
conda-lock lock ──→ conda-lock.yml (提交到 Git)
      │                    │
      │                    ▼
      │            conda-lock install ──→ conda 环境
      │                    │
      │                    ▼
      │            conda-lock render ──→ explicit 文件 (CI/CD)
      │
      ▼ (依赖需要更新时)
conda-lock lock --update ──→ 更新 conda-lock.yml
```
