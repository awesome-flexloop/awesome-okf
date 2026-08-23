---
okf_version: "0.2"
type: "concept"
title: "内容哈希机制"
sources:
  - "conda_lock/content_hash.py"
  - "conda_lock/content_hash_types.py"
  - "conda_lock/virtual_package.py"
---

# 内容哈希机制

内容哈希（Content Hash）是 conda-lock 用于快速检测锁文件输入是否变化的机制。当 channels、依赖规格或虚拟包配置改变时，内容哈希值会改变，提示需要重新锁定。哈希使用 SHA-256 算法计算，输入为三部分：channels 的确定性 JSON、排序后的依赖规格、虚拟包哈希。

## 设计目的

内容哈希解决的问题是：如果环境规格文件没有改变，且通道内容没有更新，是否需要重新运行锁定？通过比较锁文件中记录的 content_hash 与当前计算的哈希，可以快速判断输入是否变化。

```bash
# conda-lock 内部逻辑（伪代码）
old_hash = lockfile.metadata.content_hash[platform]
new_hashes = backwards_compatible_content_hashes(spec)[platform]
if old_hash not in new_hashes:
    print("Input changed, re-locking needed")
else:
    print("Lockfile is up to date")
```

[F-001]

`--check-input-hash` 选项利用此机制实现"仅在输入变化时重新锁定"，避免不必要的全量求解（全量求解可能耗时数分钟）。

## 计算流程

```python
# conda_lock/content_hash.py

def compute_content_hashes(spec: LockSpecification) -> Dict[str, str]:
    hashes = {}
    vpkgs = default_virtual_package_repodata()

    for platform in spec.platforms:
        # 1. Channels 的确定性 JSON
        channels_data = [ch.env_replaced_url() for ch in spec.channels]
        channels_json = json.dumps(channels_data, sort_keys=True,
                                   separators=(",", ":"))

        # 2. 该平台 conda 依赖的排序列表
        conda_deps = sorted(
            [d for d in spec.dependencies[platform] if d.manager == "conda"],
            key=lambda d: d.name
        )
        specs_data = [
            {"name": d.name, "version": str(d.version), "manager": d.manager}
            for d in conda_deps
        ]
        specs_json = json.dumps(specs_data, sort_keys=True,
                                separators=(",", ":"))

        # 3. 虚拟包哈希
        vpkg_hash = _compute_virtual_package_hash(vpkgs, platform)

        # 4. 拼接并计算 SHA-256
        hash_input = channels_json + "|" + specs_json + "|" + vpkg_hash
        hashes[platform] = hashlib.sha256(hash_input.encode()).hexdigest()

    return hashes
```

[F-002]

### 三部分输入详解

| 组成部分 | 内容 | 变化触发条件 |
|---------|------|------------|
| **channels_json** | 通道 URL 列表的确定性 JSON | 添加/移除/更换通道，通道 URL 变化 |
| **specs_json** | 按名称排序的 conda 依赖规格（name+version+manager） | 添加/移除/修改依赖，版本约束变化 |
| **vpkg_hash** | 目标平台虚拟包配置的哈希 | 虚拟包版本变化（如 CUDA 版本覆盖） |

[F-003]

### 确定性序列化

使用 `json.dumps(sort_keys=True, separators=(",", ":"))` 确保相同输入始终产生相同 JSON 字符串：

- `sort_keys=True`：字典键按字母序排列，不受 Python 字典遍历顺序影响
- `separators=(",", ":")`：使用紧凑分隔符（无空格），避免因空格差异导致哈希不同
- 依赖列表按 `name` 排序，确保列表顺序不影响哈希

[F-004]

## 虚拟包哈希贡献

虚拟包也参与哈希计算，因为虚拟包版本影响求解结果。例如：
- `__glibc=2.17` vs `__glibc=2.28` 可能选择不同版本的包
- `__cuda=11.8` vs `__cuda=12.1` 会选择不同版本的 CUDA 相关包

```python
def _compute_virtual_package_hash(vpkgs: FakeRepoData, platform: str) -> str:
    """计算特定平台虚拟包配置的哈希。"""
    platform_packages = [
        {"name": p.name, "version": p.version, "build": p.build_string}
        for p in vpkgs.virtual_packages
        if p.subdir == platform
    ]
    data = json.dumps(platform_packages, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()
```

[F-005]

## 向后兼容多哈希

```python
def backwards_compatible_content_hashes(
    spec: LockSpecification
) -> Dict[str, List[str]]:
    """为每个平台计算多个向后兼容的哈希变体。"""
    hashes = {}
    for platform in spec.platforms:
        platform_hashes = []

        # 1. 当前版本标准哈希
        platform_hashes.append(compute_content_hashes(spec)[platform])

        # 2. 含重复 __osx=10.15 包的变体
        vpkgs_dup = default_virtual_package_repodata(add_duplicate_osx_package=True)
        platform_hashes.append(_compute_hash_with_vpkgs(spec, platform, vpkgs_dup))

        # 3. build_number 为整数格式的变体
        vpkgs_int = default_virtual_package_repodata(build_number_as_int=True)
        platform_hashes.append(_compute_hash_with_vpkgs(spec, platform, vpkgs_int))

        # 4. null 字段省略变体
        platform_hashes.append(_compute_hash_null_variant(spec, platform))

        hashes[platform] = platform_hashes
    return hashes
```

[F-006]

**为什么需要多哈希？** conda-lock 的虚拟包模型经历过演进：
1. 旧版在 repodata 中为 osx-64 添加重复的 `__osx=10.15` 包记录
2. 旧版虚拟包的 `build_number` 字段序列化为整数（`0`）而非字符串（`"0"`）
3. 旧版 JSON 序列化中 None 值字段可能被省略而非保留为 null

这些序列化差异会导致相同语义的输入产生不同的哈希值。多哈希集合允许旧锁文件在新版 conda-lock 中仍被认为"输入未变化"，避免强制重新锁定。

**匹配逻辑**：锁文件验证时，只要锁文件中记录的哈希值在当前计算的兼容哈希列表中，即视为匹配。

[F-007]

## 已知设计缺陷

源码模块文档明确引用 issue #432，警告内容哈希机制存在根本缺陷：

### 1. 遗漏影响因素

内容哈希仅包含 channels/specs/virtual_packages，但以下因素也影响求解结果：
- **conda/mamba 版本**：不同版本的求解器可能产生不同结果
- **repodata 时间点**：通道的 repodata.json 随时更新，相同 specs 在不同时间可能求解出不同版本
- **求解器后端**：conda vs mamba vs micromamba 可能有不同的求解策略
- **Python 版本**：目标 Python 版本影响包选择

[F-008]

### 2. 虚拟包的近似性

`default_virtual_package_repodata()` 返回的是硬编码的默认虚拟包集，而非从实际目标系统探测。在 macOS 上锁定 linux-64 时，虚拟包信息是构造的，可能与实际 Linux 系统不完全匹配。

### 3. repodata 时序问题

这是最根本的缺陷：conda 通道是"滚动"的，包不断更新。即使输入 specs 和 channels 完全不变，今天锁定的 numpy 版本可能与一个月后锁定的不同（因为 numpy 发布了新版本，且 specs 中的版本约束允许更新）。内容哈希无法捕获 repodata 的变化。

### 4. 多哈希的模糊性

向后兼容的多哈希集合扩大了"匹配"范围，可能漏检实际变化。例如，两个语义不同的虚拟包配置如果恰好产生兼容哈希列表中的重叠值，可能错误地认为"未变化"。

## 正确理解内容哈希

基于上述缺陷，内容哈希应被理解为：

- ✅ **快速变化检测的启发式方法**：可以快速排除"肯定未变化"的情况
- ✅ **开发效率工具**：`--check-input-hash` 避免不必要的重锁定
- ❌ **不是锁文件有效性的严格保证**：哈希匹配不保证求解结果可重现
- ❌ **不能替代锁文件本身**：锁文件中的精确版本/哈希才是可重现性的真正保障

真正的可重现性保证来自锁文件中记录的每个包的精确版本、build、MD5/SHA256 哈希和下载 URL，而非内容哈希。

## 在锁文件中的存储

内容哈希存储在锁文件 metadata 中：

```yaml
metadata:
  content_hash:
    linux-64: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    osx-arm64: "a1b2c3d4e5f6..."
    win-64: "789abc012def..."
```

[F-009]

每个平台一个哈希值。`lock` 命令写入新哈希，`lock --update` 增量更新时更新变化平台的哈希，`install`/`render`/`render-lock-spec` 命令读取但不修改哈希。

## 相关概念

- [虚拟包系统](10-virtual-packages.md)
- [锁文件 v1/v2 格式](06-lockfile-formats.md)
- [LockSpecification 模型](03-lock-specification.md)
- [Conda 求解器](08-conda-solver.md)
- [CLI 命令体系](11-cli-commands.md)
