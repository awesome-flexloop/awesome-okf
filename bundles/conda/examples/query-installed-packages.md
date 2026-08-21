---
okf_version: "0.2"
type: "example"
title: "查询已安装包和包缓存"
sources: ["conda/api.py", "conda/core/prefix_data.py", "conda/core/package_cache_data.py"]
---

# 查询已安装包和包缓存

conda 的 API 层提供三个数据查询类，分别面向不同的数据源：`PrefixData` 管理环境前缀中已安装的包、`PackageCacheData` 管理本地包缓存、`SubdirData` 管理远端通道的 repodata。本示例演示如何使用这三个类来查询已安装包、浏览缓存以及搜索所有可用通道。

相关概念：[包记录模型](../concepts/06-package-records.md)、[索引与 repodata](../concepts/08-index-and-repodata.md)、[环境与历史](../concepts/11-environments-history.md)。

## 完整示例

```python
"""
查询已安装包和包缓存示例。

引用事实：[F-064] PrefixData/PackageCacheData/SubdirData 四个高层API类
         [F-054] PackageCacheData 管理包缓存，提供 query/first_writable/is_writable
         [F-055] PrefixData 管理环境前缀，读取 conda-meta/ 目录下JSON文件
"""

import os
import sys
from conda.api import PrefixData, PackageCacheData, SubdirData
from conda.models.match_spec import MatchSpec
from conda.base.context import context


# ============================================================
# 1. 使用 PrefixData 查询环境中已安装的包
# ============================================================

def list_installed_packages(prefix: str = None):
    """
    列出指定环境中所有已安装的包。

    [F-055] PrefixData 读取 prefix/conda-meta/*.json 文件获取已安装包记录
    返回 PrefixRecord 对象（继承自 PackageCacheRecord → PackageRecord）
    """
    if prefix is None:
        prefix = sys.prefix  # 默认查询当前 Python 所在环境

    # 初始化 PrefixData，传入环境路径
    pd = PrefixData(prefix)

    print(f"环境路径: {prefix}")
    print(f"是否可写: {pd.is_writable}")
    print("-" * 60)

    # 方式一：iter_records() 遍历所有已安装包
    # 返回 PrefixRecord 生成器，包含完整的安装元数据
    records = list(pd.iter_records())
    print(f"已安装包数量: {len(records)}")
    print()

    for rec in sorted(records, key=lambda r: r.name)[:10]:  # 前10个
        # PrefixRecord 包含：name, version, build, channel, files(文件列表),
        #                   requested_spec, depends, constrains 等
        print(f"  {rec.name:25s} {rec.version:15s} {rec.build}")

    print("  ...")
    return pd


def query_installed_by_name(prefix: str, name: str):
    """
    按名称精确查询环境中已安装的包。
    """
    pd = PrefixData(prefix)

    # get() 通过包名精确查找，返回 PrefixRecord
    try:
        record = pd.get(name)
        print(f"\n找到包: {record.name} {record.version} {record.build}")
        print(f"  通道: {record.channel.name}")
        print(f"  子目录: {record.subdir}")
        print(f"  依赖数: {len(record.depends)}")
        print(f"  文件数: {len(record.files) if hasattr(record, 'files') else 'N/A'}")
        return record
    except KeyError:
        print(f"\n包 '{name}' 未安装在当前环境中")
        return None


def query_installed_by_spec(prefix: str, spec_str: str):
    """
    使用 MatchSpec 在已安装包中执行模糊查询。
    """
    pd = PrefixData(prefix)
    spec = MatchSpec(spec_str)

    # query() 接受 MatchSpec/str/PackageRef，返回匹配的 PrefixRecord 元组
    results = pd.query(spec)
    print(f"\n查询 '{spec_str}' 匹配 {len(results)} 个包:")
    for rec in results:
        print(f"  {rec.name} {rec.version} {rec.build}")
    return results


# ============================================================
# 2. 使用 PackageCacheData 查询本地包缓存
# ============================================================

def inspect_package_cache():
    """
    浏览本地包缓存目录（pkgs_dirs）中的包。

    [F-054] PackageCacheData 管理 pkgs_dirs 中的包缓存，
    提供 query(), first_writable(), is_writable 等方法。
    """
    print("\n" + "=" * 60)
    print("包缓存信息")
    print("=" * 60)

    # context.pkgs_dirs 列出所有包缓存目录
    print(f"配置的缓存目录:")
    for pkgs_dir in context.pkgs_dirs:
        pcd = PackageCacheData(pkgs_dir)
        writable = pcd.is_writable
        records = list(pcd.iter_records())
        print(f"  {pkgs_dir}")
        print(f"    可写: {writable}, 缓存包数: {len(records)}")

    # 获取第一个可写的缓存目录
    first_writable = PackageCacheData.first_writable()
    print(f"\n第一个可写缓存: {first_writable._internal.pkgs_dir}")

    return first_writable


def query_cache_by_spec(spec_str: str):
    """
    在所有缓存目录中搜索匹配的包。
    """
    spec = MatchSpec(spec_str)

    # query_all() 静态方法搜索所有 pkgs_dirs
    # [F-054] 当 pkgs_dirs=None 时回退到 context.pkgs_dirs
    results = PackageCacheData.query_all(spec)
    print(f"\n缓存中匹配 '{spec_str}' 的包 ({len(results)} 个):")
    for rec in results:
        print(f"  {rec.name} {rec.version} {rec.build}")
        # PackageCacheRecord 额外包含: extracted_package_dir, package_tarball_full_path
        if hasattr(rec, 'extracted_package_dir'):
            print(f"    解压路径: {rec.extracted_package_dir}")
    return results


# ============================================================
# 3. 使用 SubdirData.query_all() 搜索所有通道
# ============================================================

def search_all_channels(spec_str: str, channels=None, subdirs=None):
    """
    在所有配置通道和子目录中搜索可用包。

    [F-066] SubdirData.query_all() 静态方法查询通道×子目录矩阵中的repodata
    """
    spec = MatchSpec(spec_str)

    print(f"\n搜索所有通道: '{spec_str}'")
    print(f"  通道: {channels or '默认(context.channels)'}")
    print(f"  子目录: {subdirs or '默认(context.subdirs)'}")
    print("-" * 60)

    # query_all() 会下载/加载相关 repodata.json，可能需要网络访问
    results = SubdirData.query_all(spec, channels=channels, subdirs=subdirs)

    # 按通道分组显示
    from itertools import groupby
    for channel_name, group in groupby(
        sorted(results, key=lambda r: r.channel.name),
        key=lambda r: r.channel.name
    ):
        pkgs = list(group)
        print(f"\n  通道 {channel_name}: {len(pkgs)} 个匹配包")
        # 显示前5个版本
        for rec in sorted(pkgs, key=lambda r: r.version, reverse=True)[:5]:
            print(f"    {rec.name} {rec.version} {rec.build}")

    return results


# ============================================================
# 4. 刷新数据
# ============================================================

def refresh_data(prefix: str = None):
    """
    当磁盘数据可能已变更时，使用 reload() 强制刷新。

    [F-067] 每个API类都有 reload() 方法用于强制刷新数据
    """
    if prefix is None:
        prefix = sys.prefix

    pd = PrefixData(prefix)
    print(f"\n刷新前已安装包数: {len(list(pd.iter_records()))}")

    # reload() 重新读取 conda-meta/ 目录
    pd.reload()
    print(f"刷新后已安装包数: {len(list(pd.iter_records()))}")

    # PackageCacheData 和 SubdirData 也有 reload()
    # PackageCacheData.first_writable().reload()
    # SubdirData(channel).reload()


# ============================================================
# 主函数
# ============================================================

if __name__ == "__main__":
    # 查询当前环境已安装的包
    print("=" * 60)
    print("1. 查询已安装包")
    print("=" * 60)
    pd = list_installed_packages()

    # 查询特定包
    query_installed_by_name(sys.prefix, "python")
    query_installed_by_name(sys.prefix, "conda")

    # 按 MatchSpec 查询
    query_installed_by_spec(sys.prefix, "python>=3.10")

    # 浏览包缓存
    inspect_package_cache()
    # query_cache_by_spec("conda")  # 搜索缓存中的conda包

    # 搜索所有通道（需要网络，取消注释以使用）
    # search_all_channels("python=3.11", channels=["defaults"])

    # 刷新数据
    refresh_data()
```

## 三类数据源对比

| 类 | 数据源 | 记录类型 | 主要用途 |
|---|---|---|---|
| `PrefixData` | `prefix/conda-meta/*.json` | `PrefixRecord` | 查询已安装包、文件列表、依赖关系 |
| `PackageCacheData` | `pkgs_dirs/` 下的解压包 | `PackageCacheRecord` | 管理本地缓存、检查包是否已下载 |
| `SubdirData` | 远端 `repodata.json`（有缓存） | `PackageRecord` | 搜索可用包、查询通道中的包版本 |

## 记录继承链

三级记录继承链（[F-039]）：`PackageRecord`（通道包）→ `PackageCacheRecord`（缓存包）→ `PrefixRecord`（已安装包），每一级增加对应数据源的额外字段。

- **PackageRecord**：name, version, build, depends, channel, subdir 等基础字段
- **PackageCacheRecord**：额外增加 `extracted_package_dir`, `package_tarball_full_path`, `is_extracted` 等缓存路径字段
- **PrefixRecord**：额外增加 `files`（安装文件列表）, `requested_spec`, `link`（链接类型）等安装元数据

## 注意事项

- `PrefixData` 构造时不会立即加载数据，首次调用 `query()`/`iter_records()`/`get()` 时懒加载。
- `SubdirData.query_all()` 需要网络以下载 repodata.json，首次调用较慢，后续使用本地 pickle 缓存。
- `PackageCacheData.query_all()` 不访问网络，仅扫描本地 pkgs_dirs。
- 所有三个类的 `reload()` 方法都会清空内部缓存并重新加载数据。
- `is_writable` 属性可用于判断环境/缓存是否只读（例如 base 环境可能需要管理员权限）。
