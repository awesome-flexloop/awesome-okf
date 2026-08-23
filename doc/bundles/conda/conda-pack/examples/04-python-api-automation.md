---
type: "example"
title: "Python API 编程与自动化"
description: 在 Python 脚本中使用 conda-pack API，集成到 CI/CD 流水线、自动化部署脚本、环境备份工具中。
tags: [conda-pack, python-api, automation, ci-cd, scripting]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
---

# Python API 编程与自动化

conda-pack 不仅是一个命令行工具，也提供完整的 Python API，可以集成到自动化脚本和 CI/CD 流水线中。

## pack() 函数快速参考

```python
from conda_pack import pack, CondaPackException

pack(
    # 环境选择（三选一）
    name=None,          # 环境名称
    prefix=None,        # 环境路径
    # 以上都不传则使用当前激活环境

    # 输出配置
    output=None,        # 输出路径，None 则自动生成
    format=None,        # 归档格式
    force=False,        # 覆盖已存在文件
    arcroot="",         # 归档内根路径

    # 压缩配置
    compress_level=4,   # 压缩级别
    n_threads=1,        # 压缩线程数，-1 表示所有核心

    # 路径配置
    dest_prefix=None,   # 预指定部署路径
    zip_symlinks=False, # ZIP 中保留符号链接
    zip_64=True,        # 启用 ZIP64

    # Parcel 配置
    parcel_root=None,
    parcel_name=None,
    parcel_version=None,
    parcel_distro=None,

    # 过滤与容错
    filters=None,       # [(action, pattern), ...]
    ignore_editable_packages=False,
    ignore_missing_files=False,

    # 输出控制
    verbose=False,      # 显示进度
)
```

## 示例

### 自动化环境打包脚本

```python
#!/usr/bin/env python
"""CI/CD 流水线中的环境打包脚本"""
import os
import sys
import datetime
from conda_pack import pack, CondaPackException

def package_environment(env_name, output_dir, dest_prefix=None):
    """打包 conda 环境到指定目录"""
    date_str = datetime.date.today().strftime("%Y%m%d")
    output = os.path.join(output_dir, f"{env_name}-{date_str}.tar.gz")

    try:
        pack(
            name=env_name,
            output=output,
            format="tar.gz",
            compress_level=6,
            n_threads=-1,
            dest_prefix=dest_prefix,
            verbose=True,
            filters=[
                ("exclude", "*.pyc"),
                ("exclude", "__pycache__"),
                ("exclude", "*/tests/*"),
            ],
        )
        print(f"Successfully packed: {output}")
        return output
    except CondaPackException as e:
        print(f"Packing failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    package_environment(
        env_name="production",
        output_dir="/dist",
        dest_prefix="/opt/production",
    )
```

### 批量打包所有环境

```python
import subprocess
import json
from conda_pack import pack, CondaPackException
import os

def get_all_envs():
    """获取所有 conda 环境"""
    result = subprocess.run(
        ["conda", "env", "list", "--json"],
        capture_output=True, text=True
    )
    info = json.loads(result.stdout)
    return {os.path.basename(p): p for p in info["envs"]}

def backup_all_envs(backup_dir):
    """备份所有 conda 环境"""
    os.makedirs(backup_dir, exist_ok=True)
    envs = get_all_envs()

    for name, prefix in envs.items():
        if name == "base":
            continue  # 跳过 base 环境
        output = os.path.join(backup_dir, f"{name}.tar.gz")
        print(f"Backing up {name} ({prefix})...")
        try:
            pack(
                prefix=prefix,
                output=output,
                n_threads=-1,
                verbose=False,
            )
            print(f"  → {output}")
        except CondaPackException as e:
            print(f"  ✗ Failed: {e}")

backup_all_envs("/tmp/conda-backups")
```

### 环境差异对比

```python
from conda_pack import CondaEnv

def compare_envs(env1_name, env2_name):
    """比较两个环境的包和文件差异"""
    env1 = CondaEnv.from_name(env1_name)
    env2 = CondaEnv.from_name(env2_name)

    # 提取文件名集合
    files1 = {f.target for f in env1.files}
    files2 = {f.target for f in env2.files}

    only_in_1 = files1 - files2
    only_in_2 = files2 - files1

    print(f"Only in {env1_name}: {len(only_in_1)} files")
    print(f"Only in {env2_name}: {len(only_in_2)} files")
    print(f"Common: {len(files1 & files2)} files")

    # 提取包名
    def get_packages(env):
        pkgs = set()
        import json
        import os
        meta_dir = os.path.join(env.prefix, "conda-meta")
        for fname in os.listdir(meta_dir):
            if fname.endswith(".json") and fname != "history":
                with open(os.path.join(meta_dir, fname)) as f:
                    data = json.load(f)
                pkgs.add((data["name"], data["version"]))
        return pkgs

    pkgs1 = get_packages(env1)
    pkgs2 = get_packages(env2)
    print(f"\nPackages only in {env1_name}:")
    for pkg in sorted(pkgs1 - pkgs2):
        print(f"  + {pkg[0]}=={pkg[1]}")
    print(f"\nPackages only in {env2_name}:")
    for pkg in sorted(pkgs2 - pkgs1):
        print(f"  + {pkg[0]}=={pkg[1]}")

compare_envs("dev", "production")
```

### 在内存中创建归档并上传

```python
"""打包环境后直接上传到对象存储"""
import tempfile
import os
from conda_pack import pack
import boto3  # 需要 boto3

def pack_and_upload(env_name, bucket, s3_key):
    """打包环境并上传到 S3"""
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        pack(
            name=env_name,
            output=tmp_path,
            n_threads=-1,
            compress_level=6,
        )

        s3 = boto3.client("s3")
        s3.upload_file(tmp_path, bucket, s3_key)
        print(f"Uploaded s3://{bucket}/{s3_key}")
    finally:
        os.unlink(tmp_path)

pack_and_upload("my_env", "my-bucket", "conda-envs/my_env.tar.gz")
```

### 多环境组合打包

```python
"""将多个环境的核心包组合到一个归档中（高级用法）"""
from conda_pack import CondaEnv, Packer
from conda_pack.formats import archive
import os
import tempfile

def merge_envs(env_names, output_path, format="tar.gz"):
    """将多个环境合并打包（简单实现）"""
    # 收集所有文件
    all_files = []
    seen_targets = set()
    base_prefix = None

    for name in env_names:
        env = CondaEnv.from_name(name)
        if base_prefix is None:
            base_prefix = env.prefix
        # 添加环境特定前缀的文件
        for f in env.files:
            if f.target not in seen_targets:
                all_files.append(f)
                seen_targets.add(f.target)

    # 使用 Packer 打包
    fd, temp_path = tempfile.mkstemp(suffix=f".{format}")
    import shutil

    try:
        with os.fdopen(fd, "wb") as temp_file:
            with archive(temp_file, output_path, "", format,
                        compress_level=6, n_threads=-1,
                        verbose=False, output=output_path) as arc:
                packer = Packer(base_prefix, arc, None, None)
                for f in all_files:
                    packer.add(f)
                packer.finish()
        shutil.move(temp_path, output_path)
    except:
        os.unlink(temp_path)
        raise
```

### 错误处理最佳实践

```python
from conda_pack import pack, CondaPackException

def safe_pack(env_name, output, **kwargs):
    """带完整错误处理的打包函数"""
    try:
        pack(name=env_name, output=output, **kwargs)
        return True, output
    except CondaPackException as e:
        msg = str(e)
        if "editable packages" in msg:
            return False, f"可编辑包冲突: {msg}"
        elif "missing files" in msg:
            return False, f"缺失文件: {msg}"
        elif "not a conda environment" in msg:
            return False, f"路径不是有效 conda 环境: {msg}"
        elif "Environment path" in msg and "doesn't exist" in msg:
            return False, f"环境不存在: {msg}"
        else:
            return False, f"打包错误: {msg}"
    except FileNotFoundError as e:
        return False, f"文件未找到: {e}"
    except PermissionError:
        return False, "权限不足，无法写入输出文件"
    except Exception as e:
        return False, f"未知错误: {type(e).__name__}: {e}"

success, result = safe_pack("my_env", "/tmp/output.tar.gz", n_threads=-1)
if not success:
    print(f"打包失败: {result}")
```

## 与 subprocess 结合

```python
"""在目标机器上自动部署"""
import subprocess
import tarfile
import os

def deploy_env(archive_path, dest_dir):
    """解压并部署打包好的环境"""
    os.makedirs(dest_dir, exist_ok=True)

    # 解压
    print("Extracting...")
    subprocess.run(
        ["tar", "-xzf", archive_path, "-C", dest_dir],
        check=True,
    )

    # 运行 conda-unpack
    conda_unpack = os.path.join(dest_dir, "bin", "conda-unpack")
    if os.path.exists(conda_unpack):
        print("Running conda-unpack...")
        subprocess.run([conda_unpack], check=True)

    print(f"Environment deployed to {dest_dir}")
    print(f"Activate with: source {os.path.join(dest_dir, 'bin/activate')}")
```

## 相关概念

- [CondaEnv 与 File 数据模型](../concepts/03-conda-env-and-file.md)
- [打包流程与 Packer](../concepts/05-packing-process.md)
- [conda-unpack 与部署流程](../concepts/09-conda-unpack.md)
