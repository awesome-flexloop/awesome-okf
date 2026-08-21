---
okf_version: "0.2"
type: "concept"
title: "环境管理与 History"
sources:
  - "conda/core/prefix_data.py"
  - "conda/core/envs_manager.py"
  - "conda/history.py"
  - "conda/models/prefix_graph.py"
---

# 环境管理与 History

## 概述

conda 环境是一个目录前缀（prefix），包含一组已安装的 conda 包及其元数据。环境管理涉及三个核心组件：`PrefixData` 管理环境前缀中 `conda-meta/` 目录的包记录，`envs_manager` 维护已知环境的注册表，`History` 类记录环境的变更历史 [F-055][F-056]。此外，`PrefixGraph` 提供已安装包之间的依赖图拓扑排序能力，用于确定包的安装/卸载顺序 [F-043]。

## conda-meta/ 目录结构

每个 conda 环境的根目录下都有一个 `conda-meta/` 目录，是环境存在的标志和元数据存储位置。环境的有效性通过 `conda-meta/history` 文件（常量 `PREFIX_MAGIC_FILE`）是否存在来判断 [F-028]。关键文件包括：

| 文件 | 用途 |
|------|------|
| `history` | 变更历史：时间、命令、specs、包差异 |
| `<pkg>-<ver>-<build>.json` | 每个已安装包的元数据（PrefixRecord 序列化） |
| `pinned` | 固定版本包列表，求解器不更新这些包 |
| `frozen` | 环境冻结标记（CEP 22） |
| `state` | 环境状态文件 |

其中 `<pkg>-<ver>-<build>.json` 是 `PrefixRecord` 的序列化，记录包名、版本、依赖、文件列表、链接类型等，是已安装包信息的权威来源。

## PrefixData：环境前缀数据管理

`PrefixData` 类代表一个 conda 环境在磁盘上的状态，使用 `PrefixDataType` 元类实现实例缓存 [F-055]。

### 元类缓存与懒加载

`PrefixDataType` 元类以 `(prefix_path, interoperability)` 为缓存键实现实例复用，传入已有 PrefixData 实例时直接返回。`PrefixRecordDict(UserDict)` 实现 dict 到 PrefixRecord 的延迟转换——加载 conda-meta 时先读为原始 dict，访问时才转为 PrefixRecord 对象。

### 工厂方法与状态检查

PrefixData 提供三个工厂方法：
- `PrefixData(prefix_path)`：从路径直接创建；
- `PrefixData.from_name(name)`：从名称创建，自动在 envs_dirs 中查找；
- `PrefixData.from_context()`：从 context.target_prefix 创建。

状态检查方法：`exists()`（路径存在）、`is_environment()`（conda-meta/history 存在）、`is_frozen()`（frozen 文件存在）、`is_base()`（等于 root_prefix）、`is_writable`（history 可写）。对应的 `assert_*()` 方法在失败时抛出具体异常。核心功能是 `iter_records()` 遍历 conda-meta 下所有 JSON 包记录。

## envs_manager：环境注册表

`envs_manager` 管理所有已知 conda 环境的注册表 [F-056]。

注册表文件为 `~/.conda/environments.txt`，每行一个环境绝对路径。`register_env(location)` 将路径追加到文件（过滤 conda-build 临时环境、跳过重复路径）；`unregister_env(location)` 仅当 conda-meta 目录中只剩 history 文件时才注销（表示环境已清空）。`list_all_known_prefixes()` 扫描 environments.txt 和 envs_dirs 返回所有已知环境，管理员用户还会扫描所有用户的主目录。

## History：环境变更历史

`History` 类管理 `conda-meta/history` 文件，记录每次变更操作。

### history 文件格式

history 以段为单位，每段以时间戳分隔：

```
==> 2024-01-15 10:30:00 <==
# cmd: conda install numpy
# conda version: 24.1.0
# install specs: ['numpy>=1.20']
+numpy-1.26.0-py311h01a0d98_0
```

`==> 时间戳 <==` 标记段开始，`# cmd:` 记录命令行，`# conda version:` 记录版本，`# install/update/remove specs:` 记录操作的 specs，`+`/`-` 前缀行标记新增/移除的包。

### 解析与更新

History 使用三个正则解析文件（命令行、specs行、版本行）。核心方法：
- `parse()`：返回 `[(datetime, dists_set, comments)]`；
- `get_user_requests()`：返回用户请求列表（date/cmd/action/specs）；
- `construct_states()`：从差异重建每版本的全包集合；
- `get_state(rev=-1)`：获取指定修订版本的包集合；
- `update()`：比较当前包集合与上次状态，写入差异新段。

`get_requested_specs_map()` 从历史重建用户显式请求的 specs 映射，按时间顺序应用 install/remove/neutered 操作。History 还提供版本降级保护：环境被更高版本 conda 操作过时，旧版本会发出警告。

## PrefixGraph：依赖图拓扑排序

`PrefixGraph` 实现已安装包的有向依赖图，用于拓扑排序 [F-043]。

图用邻接表表示：`self.graph` 字典，键为 PrefixRecord 节点，值为父节点集合（此包依赖的包）。`_toposort()` 执行 Kahn 算法：反复移除零入度节点；遇到环时，`allow_cycles` 为 True 则选父节点最少的节点打破，否则抛 `CyclicalDependencyError`。排序按包名字母序稳定排列。

`_toposort_prepare_graph()` 处理三种特殊情况：①移除 python-pip 循环依赖边；②menuinst 优先链接（确保其他包可用 menuinst 创建快捷方式）；③Windows 上 noarch:python 包隐式依赖 conda。主要操作方法：`remove_spec(spec)` 移除匹配节点及后代，`prune()` 剪枝无依赖的叶节点，`all_descendants()/all_ancestors()` 查询后代/祖先。

## 相关概念

- [UnlinkLinkTransaction 事务与包链接](./10-transaction-link.md)：事务通过 Action 调用 PrefixData、History、envs_manager 维护环境元数据
- [Index 索引与 SubdirData](./08-index-and-repodata.md)：Index 使用 PrefixData 补充已安装包信息
- [Context 全局配置与 condarc](./07-context-configuration.md)：envs_dirs、register_envs 等配置来自 context
