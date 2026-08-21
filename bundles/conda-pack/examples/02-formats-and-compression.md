---
type: "example"
title: "格式选择与压缩优化"
description: 根据场景选择合适的归档格式和压缩参数，使用多线程并行压缩加速打包过程。
tags: [conda-pack, format, compression, parallel, zip, tar, squashfs]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: formats
    resource: /references/formats-source.md
    title: formats.py 归档格式模块源码
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
---

# 格式选择与压缩优化

conda-pack 支持 9 种归档格式和多线程压缩。选择合适的格式和参数可以显著提升打包速度、减小文件体积、改善部署体验。

## 格式对比

| 格式 | 扩展名 | 压缩 | 跨平台 | 适合场景 |
|------|--------|------|--------|---------|
| `tar.gz` | `.tar.gz`/`.tgz` | gzip | Linux/macOS/Windows | **默认选择**，通用性好 |
| `tar.bz2` | `.tar.bz2`/`.tbz2` | bzip2 | 通用 | 高压缩比，速度较慢 |
| `tar.xz` | `.tar.xz`/`.txz` | xz | 通用 | 最高压缩比，速度最慢 |
| `tar.zst` | `.tar.zst`/`.tzst` | zstd | 需 zstd | 速度快压缩比好，推荐新场景 |
| `tar` | `.tar` | 无压缩 | 通用 | 最快速度，文件大 |
| `zip` | `.zip` | deflate | Windows 友好 | Windows 部署、需要随机访问 |
| `squashfs` | `.squashfs` | zstd/xz | Linux | 容器、只读环境 |
| `no-archive` | 无 | N/A | 本地复制 | 就地部署 |
| `parcel` | `.parcel` | gzip | Cloudera | Cloudera 生态 |

## 示例

### 场景1：快速打包（优先速度）

```bash
# 无压缩 tar，最快速度
conda-pack -n my_env --format tar -o my_env.tar

# zstd 压缩，兼顾速度和体积
conda-pack -n my_env --format tar.zst -o my_env.tar.zst --compress-level 3
```

```python
pack(name="my_env", format="tar", output="/tmp/my_env.tar")
pack(name="my_env", format="tar.zst", compress_level=3, output="/tmp/my_env.tar.zst")
```

### 场景2：最小体积（优先压缩比）

```bash
# xz 最高压缩级别，文件最小但耗时最长
conda-pack -n my_env --format tar.xz --compress-level 9 -j -1
```

```python
pack(name="my_env", format="tar.xz", compress_level=9, n_threads=-1, output="/tmp/my_env.tar.xz")
```

### 场景3：Windows 部署（使用 ZIP）

```bash
conda-pack -n my_env --format zip -o my_env.zip

# 在 ZIP 中保留符号链接（节省空间，但部分解压工具不支持）
conda-pack -n my_env --format zip --zip-symlinks -o my_env.zip

# 禁用 ZIP64（兼容旧版 unzip，但环境超过4GB时会失败）
conda-pack -n my_env --format zip --no-zip-64 -o my_env.zip
```

```python
pack(name="my_env", format="zip", zip_symlinks=True, output="/tmp/my_env.zip")
```

### 场景4：多线程加速

```bash
# 使用所有 CPU 核心（推荐）
conda-pack -n my_env -j -1

# 指定 4 个线程
conda-pack -n my_env -j 4
```

```python
pack(name="my_env", n_threads=-1, output="/tmp/my_env.tar.gz")  # 所有核心
pack(name="my_env", n_threads=4, output="/tmp/my_env.tar.gz")   # 指定线程数
```

**多线程支持的格式**：`tar.gz`、`tar.bz2`、`tar.xz`、`tar.zst`
**单线程格式**：`zip`、`tar`、`squashfs`、`no-archive`、`parcel`

### 场景5：容器只读环境（SquashFS）

```bash
# 需要系统安装 mksquashfs 命令
conda-pack -n my_env --format squashfs -o my_env.squashfs
```

```python
# 确保 mksquashfs 在 PATH 中
pack(name="my_env", format="squashfs", output="/tmp/my_env.squashfs")
```

部署时挂载：
```bash
mount -t squashfs my_env.squashfs /opt/my_env
# 或使用 squashfuse（非 root）
squashfuse my_env.squashfs /opt/my_env
```

### 场景6：预指定目标路径（跳过 conda-unpack）

```bash
# 打包时就确定部署路径为 /opt/production
conda-pack -n my_env -d /opt/production -o production_env.tar.gz
```

```python
pack(name="my_env", dest_prefix="/opt/production", output="/tmp/production_env.tar.gz")
```

部署时直接解压即可，无需运行 conda-unpack：
```bash
mkdir -p /opt/production
tar -xzf production_env.tar.gz -C /opt/production
source /opt/production/bin/activate  # 立即可用
```

### 场景7：自定义归档内目录结构

```bash
# 归档内文件在 env/ 子目录下
conda-pack -n my_env --arcroot env -o my_env.tar.gz
# 解压后结构：env/bin/, env/lib/, ...
```

```python
pack(name="my_env", arcroot="env", output="/tmp/my_env.tar.gz")
```

### 场景8：就地复制（no-archive）

```bash
# 直接复制到目标目录，不生成归档文件
conda-pack -n my_env --format no-archive -o /opt/deployed_env
```

```python
pack(name="my_env", format="no-archive", output="/opt/deployed_env")
```

相当于 `cp -r` 的智能版本，会处理前缀替换和可执行权限。

## 压缩级别参考

| 格式 | 0 | 1 | 3 | 6 | 9 | 19 |
|------|---|---|---|---|---|-----|
| gzip | 无压缩 | 最快 | 默认(4) | 较好压缩 | 最高压缩 | - |
| bzip2 | 无压缩 | 最快 | - | 默认(4) | 最高压缩 | - |
| xz/lzma | 无压缩 | 最快 | - | - | 最高压缩 | - |
| zstd | 无压缩 | 最快 | 推荐 | 默认(4) | 高压缩 | 超高压缩 |

> 注意：`compress_level=0` 不是所有格式都支持无压缩模式（squashfs 的 0 是 `noI noD noF noX` 完全无压缩，xz/bzip2 的 0 是最低压缩而非无压缩）。

## 性能建议

1. **大型环境（>1GB）**：使用 `-j -1` 多线程，推荐 `tar.zst` 格式
2. **分发环境**：使用 `tar.gz`（兼容性最好）或 `zip`（Windows）
3. **归档存储**：使用 `tar.xz --compress-level 9 -j -1` 最小体积
4. **开发迭代**：使用 `--format tar`（无压缩，打包最快）
5. **容器化部署**：使用 `squashfs` 只读镜像
6. **已知部署路径**：始终使用 `-d` 指定目标路径，省去 conda-unpack 步骤
