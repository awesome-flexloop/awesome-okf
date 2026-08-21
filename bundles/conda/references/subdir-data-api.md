---
okf_version: "0.2"
type: reference
title: SubdirData 仓库数据 API
sources:
  - conda/api.py
---

# SubdirData 仓库数据 API

`SubdirData` 类是 Conda 对 `repodata.json`（频道子目录的包元数据索引）的高层管理与查询 API，同样采用**后端委托模式**——公开 API 转发给内部 `_SubdirData` 实例。支持单频道子目录查询、跨频道矩阵查询、记录遍历和数据重载，是依赖求解和包搜索的基础设施。

```python
# conda/api.py

class SubdirData:
    """
    **Beta** High-level management and usage of repodata.json for subdirs.
    """

    def __init__(self, channel):
        """
        Args:
            channel (str or Channel):
                The target subdir. Must include a subdir, e.g.:
                    * 'https://repo.anaconda.com/pkgs/main/linux-64'
                    * Channel('conda-forge/osx-64')
        """
        channel = Channel(channel)
        if not channel.subdir:
            raise ValueError("SubdirData requires platform-aware Channel objects.")
        self._internal = _SubdirData(channel)

    def query(self, package_ref_or_match_spec):
        """Run a query against this specific instance of repodata.

        Args:
            package_ref_or_match_spec: PackageRef, MatchSpec, or str (auto-converted).

        Returns:
            tuple[PackageRecord]
        """
        return tuple(self._internal.query(package_ref_or_match_spec))

    @staticmethod
    def query_all(package_ref_or_match_spec, channels=None, subdirs=None):
        """Run a query against all repodata instances in channel/subdir matrix.

        Args:
            package_ref_or_match_spec: PackageRef, MatchSpec, or str.
            channels: Iterable of channels/URLs; defaults to context.channels.
            subdirs: Iterable of subdir strings; defaults to context.subdirs.

        Returns:
            tuple[PackageRecord]
        """
        return tuple(
            _SubdirData.query_all(package_ref_or_match_spec, channels, subdirs)
        )

    def iter_records(self):
        """Iterate over all records in the repodata.json instance.

        Warning: this is a generator that is exhausted on first use.

        Returns:
            Iterable[PackageRecord]
        """
        return self._internal.iter_records()

    def reload(self):
        """Update the instance with new information. Repodata is lazily
        downloaded/loaded on first use; only call this if certain data is outdated.

        Returns:
            SubdirData
        """
        self._internal = self._internal.reload()
        return self
```

**关键设计**：
- **平台感知约束**：构造函数强制要求 `Channel` 对象包含 `subdir`（平台子目录如 `linux-64`、`osx-arm64`、`win-64`），因为 repodata.json 始终按平台子目录组织，不存在"跨平台"的 repodata
- **双查询模式**：`query()` 在单个 SubdirData 实例（即单个频道+子目录组合）上查询；`query_all()` 是静态方法，自动遍历频道×子目录矩阵进行跨仓库查询
- **惰性加载**：repodata.json 在首次调用 `query()`/`iter_records()` 时才下载和解析，`reload()` 提供强制刷新能力
- **生成器遍历**：`iter_records()` 返回一次性生成器，适用于需要扫描全部包记录的场景（如求解器预热），调用方需注意不可重复遍历
- **后端委托**：与 `Solver` 一致，公开类仅作 API 门面，实际逻辑在 `_SubdirData` 内部类中实现，为未来缓存策略和数据源替换留出走马
