---
okf_version: "0.2"
type: reference
title: "内容哈希算法 (content_hash.py)"
sources:
  - "conda_lock/content_hash.py"
  - "conda_lock/content_hash_types.py"
  - "conda_lock/virtual_package.py"
---

# 内容哈希算法 (content_hash.py)

内容哈希用于检测锁文件输入是否发生变化。当 channels、specs 或虚拟包配置改变时，内容哈希会改变，从而触发重新求解。哈希输入为 channels 的 JSON 表示 + 排序后的 specs 列表 + 虚拟包哈希，使用 SHA-256 算法计算。模块文档明确警告 content hash 概念存在根本缺陷（见 issue #432）。

## compute_content_hashes() — 核心哈希计算

```python
# conda_lock/content_hash.py

import hashlib
import json
from typing import Dict, List
from .models.lock_spec import LockSpecification
from .models.channel import Channel
from .virtual_package import default_virtual_package_repodata

def _ordered_json(obj) -> str:
    """将对象序列化为确定性 JSON 字符串（sort_keys=True）。"""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def compute_content_hashes(spec: LockSpecification) -> Dict[str, str]:
    """为每个目标平台计算内容哈希（SHA-256），返回平台→哈希映射。"""
    hashes = {}
    vpkgs_repodata = default_virtual_package_repodata()

    for platform in spec.platforms:
        # 1. channels 的确定性 JSON
        channels_json = _ordered_json([
            ch.env_replaced_url() for ch in spec.channels
        ])

        # 2. 该平台 specs 的排序列表（按名称排序保证确定性）
        platform_specs = sorted(
            spec.dependencies.get(platform, []),
            key=lambda d: (d.manager, d.name, str(d.version))
        )
        specs_json = _ordered_json([
            {"manager": d.manager, "name": d.name, "version": str(d.version)}
            for d in platform_specs
            if d.manager == "conda"
        ])

        # 3. 虚拟包哈希（虚拟包版本影响求解结果）
        vpkg_hash = _compute_virtual_package_hash(vpkgs_repodata, platform)

        # 4. 拼接并计算 SHA-256
        hash_input = channels_json + "|" + specs_json + "|" + vpkg_hash
        hashes[platform] = hashlib.sha256(hash_input.encode()).hexdigest()

    return hashes
```

**设计要点**：
- **确定性序列化**：使用 `sort_keys=True` 和紧凑分隔符（`,:`）确保相同输入始终产生相同 JSON 输出，不受字典遍历顺序影响。
- **三部分输入**：channels JSON（通道影响包来源）+ specs JSON（用户指定依赖影响求解）+ virtual_package hash（系统依赖如 glibc 版本影响求解）。
- **按平台独立计算**：不同平台的虚拟包不同（如 linux-64 有 __glibc，osx-arm64 有 __osx），每个平台独立计算哈希。
- **仅 conda 依赖**：pip 依赖的哈希在 pypi_solver 中独立处理，此处仅计算 conda 部分。

## backwards_compatible_content_hashes() — 向后兼容多哈希

```python
# conda_lock/content_hash.py

def backwards_compatible_content_hashes(
    spec: LockSpecification
) -> Dict[str, List[str]]:
    """计算多个向后兼容的哈希变体，用于兼容旧版本锁文件。

    返回每个平台的哈希列表（而非单个哈希），只要锁文件中
    任一哈希匹配，即认为输入未变化。
    """
    hashes = {}

    for platform in spec.platforms:
        platform_hashes = []

        # 1. 当前版本的哈希（标准计算）
        platform_hashes.append(compute_content_hashes(spec)[platform])

        # 2. 含重复 __osx=10.15 包的哈希（向后兼容旧版虚拟包）
        #    旧版会在 repodata 中添加重复的 __osx 虚拟包
        vpkgs_dup = default_virtual_package_repodata(add_duplicate_osx_package=True)
        platform_hashes.append(_compute_hash_with_vpkgs(spec, platform, vpkgs_dup))

        # 3. build_number 整数格式变体
        #    旧版虚拟包的 build_number 是整数而非字符串
        vpkgs_int = default_virtual_package_repodata(build_number_as_int=True)
        platform_hashes.append(_compute_hash_with_vpkgs(spec, platform, vpkgs_int))

        # 4. null 字段变体
        #    旧版序列化中 None 值字段可能被省略或保留
        platform_hashes.append(_compute_hash_null_variant(spec, platform))

        hashes[platform] = platform_hashes

    return hashes
```

**设计要点**：
- **多哈希集合**：每个平台维护一组哈希值而非单一哈希，只要锁文件中的哈希匹配集合中任一值即视为兼容。
- **向后兼容原因**：虚拟包模型的演进（__osx 重复包、build_number 格式、null 字段处理）导致旧锁文件的哈希与新版本计算结果不同。多哈希集合允许在不强制重新锁定的情况下平滑升级。
- **匹配逻辑**：锁文件验证时，检查锁文件中记录的 content_hash 是否在当前计算的兼容哈希集合中。若不在，则提示用户需要重新锁定。

## 已知设计缺陷

源码注释（和 issue #432）明确指出 content hash 机制存在根本缺陷：

1. **哈希遗漏因素**：仅包含 channels/specs/virtual_packages，遗漏了 conda 版本、solver 后端版本、repodata 状态等影响求解结果的因素。即使哈希匹配，不同时间/不同 conda 版本求解结果也可能不同。
2. **虚拟包近似**：`default_virtual_package_repodata()` 返回的是默认虚拟包集，而非实际运行系统的虚拟包。跨平台锁定时（如在 macOS 上锁定 linux-64），虚拟包信息是构造的而非真实的。
3. **repodata 时序问题**：conda 通道的 repodata.json 随时更新，同一组 specs 在不同时间求解可能得到不同版本的包，但内容哈希不会反映这一变化。
4. **多哈希的模糊性**：向后兼容的多哈希集合扩大了"匹配"范围，可能漏检实际变化。

因此，内容哈希仅作为**快速变化检测**的启发式手段，不能作为锁文件有效性的严格保证。
