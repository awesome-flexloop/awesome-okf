---
okf_version: "0.2"
type: index
title: "conda-lock 源码信源参考"
sources:
  - "conda_lock/"
---

# 信源登记簿

本目录登记本知识包所有内容据以派生的 conda-lock 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。

* [CLI 入口点 (conda_lock.py)](cli-entry.md) — conda-lock CLI 基于 Click 框架构建，使用 OrderedGroup 自定义命令组使 lock 成为默认子命令，包含 lock/install/render/render-lock-spec 四个核心命令及主要选项（lock/render 的 --dev-dependencies、install 的 --dev、--platform/--channel/--extras/--kind）。
* [Conda 求解器 (conda_solver.py)](solve-conda.md) — conda-lock 核心求解策略：不自实现 SAT 算法，而是调用 conda/mamba/micromamba 的 `create --dry-run --json` 获取求解结果；包含 solve_conda() 顶层入口、solve_specs_for_arch() 单平台 dry-run 求解、update_specs_for_arch() 增量更新（fake_conda_environment+pinning）、_to_match_spec() 依赖规格转换。
* [锁定规格模型 (models/lock_spec.py)](lock-spec-model.md) — 核心数据模型 LockSpecification（按平台分组的依赖字典+通道列表+源追踪+PyPI配置）、四类依赖模型（VersionedDependency/URLDependency/VCSDependency/PathDependency）及 Dependency TypeAlias 联合类型、Channel 不可变模型的凭证安全设计（token/basic-auth 自动脱敏、三种脱敏格式识别、环境变量替换）。
* [内容哈希算法 (content_hash.py)](content-hash.md) — SHA-256 内容哈希计算流程（channels JSON + 排序 specs + 虚拟包哈希）、确定性 JSON 序列化（sort_keys=True）、backwards_compatible_content_hashes() 多哈希向后兼容集合、已知设计缺陷说明（issue #432）。

```{toctree}
:hidden:
:maxdepth: 7

cli-entry
content-hash
lock-spec-model
solve-conda
```
