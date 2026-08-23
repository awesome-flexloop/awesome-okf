---
type: "example"
title: "基础打包与部署"
description: 最基础的 conda-pack 使用场景——打包当前环境、传输到目标机器、解压、运行 conda-unpack、激活使用。
tags: [conda-pack, basic-usage, deployment, tutorial]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
---

# 基础打包与部署

这是最常见的使用场景：在开发机上打包一个 conda 环境，传输到生产服务器上部署使用。

## 前置条件

- 源机器已安装 conda/miniconda/anaconda
- 源环境已创建并安装好所有依赖
- 目标机器不需要安装 conda，但需要相同类型的操作系统和架构

## 完整流程

### 1. 激活要打包的环境（可选）

```bash
conda activate my_env
```

### 2. 打包环境

**方式一：打包当前激活的环境**

```bash
conda-pack
```

**方式二：按名称打包指定环境**

```bash
conda-pack -n my_env
```

**方式三：按路径打包**

```bash
conda-pack -p /home/user/miniconda3/envs/my_env
```

默认输出文件名为 `my_env.tar.gz`，保存在当前目录。

### 3. 传输到目标机器

```bash
scp my_env.tar.gz user@target-server:/opt/
```

### 4. 在目标机器上解压

```bash
mkdir -p /opt/my_env
tar -xzf my_env.tar.gz -C /opt/my_env
```

### 5. 运行 conda-unpack 修复路径

```bash
cd /opt/my_env
./bin/conda-unpack
```

输出示例：
```
Collecting packages...
Packing environment at '/home/user/miniconda3/envs/my_env' to 'my_env.tar.gz'
[########################################] | 100% Completed | 25.3s
```

### 6. 激活并使用环境

```bash
source /opt/my_env/bin/activate

# 验证
python --version
which python
# /opt/my_env/bin/python

python -c "import numpy; print(numpy.__version__)"
```

### 7. 停用环境

```bash
# bash/zsh
deactivate
```

## Python API 方式

```python
from conda_pack import pack

# 打包环境到文件
pack(
    name="my_env",
    output="/tmp/my_env.tar.gz",
)

# 传输后在目标机器部署：
# 1. 解压 tar.gz
# 2. 运行 bin/conda-unpack
# 3. source bin/activate
```

## 常见问题排查

### "Environment path doesn't exist"

确认环境路径正确：
```bash
conda env list
```

### "Path is not a conda environment"

目标目录缺少 `conda-meta/` 子目录，可能不是有效的 conda 环境。

### conda-unpack 报错"Permission denied"

确保对解压目录有写权限：
```bash
chmod -R u+w /opt/my_env
```

### 解压后 Python 无法启动共享库

检查系统 glibc 版本兼容性。conda-pack 不处理系统库依赖，目标机器的 glibc 版本需要不低于打包机器。
