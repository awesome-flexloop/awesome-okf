---
type: "concept"
title: "conda-unpack 与部署流程"
description: 打包后的部署流程——解压归档、运行 conda-unpack 修复前缀、激活环境，以及 Parcel 特殊部署方式。
tags: [conda-pack, conda-unpack, deployment, activation, parcel]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
  - id: prefixes
    resource: /references/prefixes-source.md
    title: prefixes.py 前缀替换模块源码
---

# conda-unpack 与部署流程

conda-pack 的部署流程是打包流程的逆操作。标准部署需要三个步骤：解压、运行 conda-unpack、激活环境。如果打包时指定了 `dest_prefix`，则可跳过 conda-unpack 步骤。

## 标准部署流程（无 dest_prefix）

### 步骤 1：解压归档

将归档解压到目标目录：

```bash
# tar.gz
mkdir -p /opt/my_env
tar -xzf my_env.tar.gz -C /opt/my_env

# zip
unzip my_env.zip -d /opt/my_env

# tar（无压缩）
mkdir -p /opt/my_env
tar -xf my_env.tar -C /opt/my_env
```

解压后环境目录结构：
```
/opt/my_env/
├── bin/
│   ├── python              # shebang 指向 /usr/bin/env python（已重写）
│   ├── activate            # conda-pack 提供的激活脚本
│   ├── conda               # shebang 仍为占位符，需要修复
│   ├── conda-unpack        # 修复脚本
│   └── conda_unpack_progress.py  # 进度条模块
├── lib/
│   └── python3.10/
│       └── os.py           # 包含占位符路径，需要修复
├── conda-meta/
└── ...
```

此时环境还**不能直接使用**——bin/conda 等文件仍包含占位符路径 `/opt/anaconda1anaconda2anaconda3`。

### 步骤 2：运行 conda-unpack

```bash
cd /opt/my_env
./bin/conda-unpack        # Linux/macOS
# 或
.\Scripts\conda-unpack.exe  # Windows
```

conda-unpack 脚本的执行过程：

```python
# 1. 定位环境根目录
new_prefix = sys.prefix  # 脚本所在目录的父目录

# 2. 遍历所有 _prefix_records
for f, placeholder, mode in _prefix_records:
    # 3. 调用 update_prefix() 修复每个文件
    update_prefix(os.path.join(new_prefix, f), new_prefix,
                  placeholder, mode=mode)
```

关键点：
- 脚本通过 `sys.prefix` 自动检测安装路径，无需手动指定
- `--verbose` 参数显示详细进度；`--version` 输出版本号
- **修复后环境即可正常使用**，无需额外步骤
- conda-unpack 脚本本身在修复完成后可以删除

### 步骤 3：激活环境

使用 conda-pack 自带的激活脚本激活环境：

```bash
# Linux/macOS (bash/zsh)
source /opt/my_env/bin/activate

# fish
source /opt/my_env/bin/activate.fish

# Windows (cmd)
\opt\my_env\Scripts\activate.bat

# 激活后验证
which python
# /opt/my_env/bin/python
python -c "import sys; print(sys.prefix)"
# /opt/my_env
```

> **与 conda activate 的区别**：conda-pack 的 activate 脚本是独立实现的，不需要目标机器安装 conda。它通过修改 PATH、CONDA_PREFIX、PS1 等环境变量实现激活效果。

### 停用环境

```bash
# bash/zsh
conda-unpack 后激活的环境，直接 exit 或 source deactivate
```

## 预指定目标路径部署（dest_prefix）

如果打包时知道确切的部署路径，可以使用 `--dest-prefix` 参数：

```bash
conda-pack -p /home/user/my_env -o /tmp/my_env.tar.gz \
  -d /opt/my_env
```

此时打包时就将所有占位符替换为 `/opt/my_env`，解压后直接可用：

```bash
mkdir -p /opt/my_env
tar -xzf my_env.tar.gz -C /opt/my_env
source /opt/my_env/bin/activate  # 直接激活，无需 conda-unpack
```

**优势**：部署步骤更少，不需要 conda-unpack
**限制**：目标路径必须与打包时指定的完全一致，不能移动

## Parcel 部署流程

Parcel 格式是 Cloudera 管理器专用的部署格式，有特殊的部署机制：

### Parcel 结构

```
parcel_name-parcel_version/
├── meta/
│   ├── parcel.json       # 元数据（名称、版本、依赖、脚本）
│   └── conda_env.sh      # 激活脚本
├── bin/                  # conda 环境文件
├── lib/
└── conda-meta/
```

### parcel.json 关键字段

```json
{
  "schema_version": 1,
  "name": "MY_PACKAGE",
  "version": "2024.01.15",
  "extraVersionInfo": {
    "fullVersion": "2024.01.15-py39_0",
    "baseVersion": "2024.01.15",
    "patchCount": "0"
  },
  "depends": [],
  "scripts": {
    "defines": "conda_env.sh"
  },
  "packages": [
    {"name": "numpy", "version": "1.24.0"},
    ...
  ]
}
```

### 部署步骤

Parcel 由 Cloudera Manager 自动管理：
1. 将 `.parcel` 文件放到 Cloudera 的 parcel 仓库
2. Cloudera Manager 下载、分发、解压到 `--parcel-root`（默认 `/opt/cloudera/parcels/`）
3. 通过 `meta/conda_env.sh` 设置环境变量
4. 无需运行 conda-unpack（因为 `dest_prefix` 已在打包时固定为 parcel 安装路径）

## no-archive 部署

`--format no-archive` 不创建归档，直接复制文件到目标目录，相当于"就地打包"：

```bash
conda-pack -p /home/user/my_env -d /opt/deployed_env \
  -o /opt/deployed_env --format no-archive
```

适用场景：
- 本地部署，不需要归档文件
- 快速复制环境到同机另一目录
- 配合文件系统级快照使用

## SquashFS 部署

SquashFS 是只读压缩文件系统，常用于容器和 Live CD 场景：

```bash
# 打包
conda-pack -p /home/user/my_env -o env.squashfs --format squashfs

# 部署：挂载 squashfs
mount -t squashfs env.squashfs /opt/my_env
source /opt/my_env/bin/activate
```

**优势**：压缩存储、只读（防止意外修改）、可直接挂载使用
**限制**：Linux 内核支持 squashfs；只读；需要 root 挂载或使用 squashfuse

## 部署注意事项

### 可编辑包问题

打包时检测到可编辑包（`pip install -e`）会报错，因为：
- 可编辑包的文件通过符号链接指向源码目录
- 打包只会包含链接，不会包含实际源码
- 部署到目标机器后链接指向不存在的路径

解决方案：
1. 打包前重新安装为非可编辑模式：`pip install .`
2. 使用 `--ignore-editable-packages` 强制打包（可能运行失败）

### 跨平台限制

conda-pack 打包的环境**只能在同类型操作系统上使用**：
- Linux 打包 → Linux 部署（glibc 版本需兼容）
- macOS 打包 → macOS 部署（x86_64 和 arm64 不互通）
- Windows 打包 → Windows 部署

Python 的二进制扩展（C extensions）、系统库依赖是平台相关的，无法跨平台。

### 硬链接与符号链接

- tar/zip 归档默认保留符号链接
- SquashFS 和 no-archive 使用硬链接优化复制性能
- Windows 上 tar 格式使用 `dereference=True` 解引用符号链接（避免 Windows 上的链接问题）

### 激活脚本的环境变量

conda-pack 提供的激活脚本设置以下环境变量：

| 变量 | 值 | 说明 |
|------|-----|------|
| `PATH` | `$ENV_PREFIX/bin` 前置 | 将环境 bin 目录加入 PATH |
| `CONDA_PREFIX` | `$ENV_PREFIX` | conda 环境路径 |
| `CONDA_DEFAULT_ENV` | 环境名 | 兼容 conda 工具链 |
| `PS1` | `(env_name)` 前缀 | bash/zsh 提示符 |

### 部署后清理

conda-unpack 修复完成后，以下文件可以安全删除：
- `bin/conda-unpack` / `Scripts/conda-unpack.exe`
- `bin/conda_unpack_progress.py`
- `bin/conda-unpack-script.py`（Windows）

## 相关概念

- [前缀替换机制](06-prefix-replacement.md)
- [打包流程与 Packer](05-packing-process.md)
- [归档格式体系](07-archive-formats.md)
