---
okf_version: "0.2"
type: "example"
title: "MatchSpec 查询示例"
sources: ["conda/models/match_spec.py", "conda/api.py"]
---

# MatchSpec 查询示例

MatchSpec 是 conda 的包查询语言，用于精确或模糊地描述包的名称、版本、构建号、通道等属性。本示例展示 MatchSpec 对象的创建方式、版本约束语法、以及在 SubdirData 上执行查询的常见场景。

相关概念：[MatchSpec 查询语言](../concepts/04-matchspec.md)、[版本系统](../concepts/05-version-system.md)、[通道与子目录](../concepts/03-channel-subdir.md)。

## 完整示例

```python
"""
MatchSpec 查询示例。

引用事实：[F-034] MatchSpec 支持 name[version='>=3.6',build=py37_0] 方括号语法
         [F-035] MatchSpec 使用多个正则解析（_BRACKETS_RE/_NAME_VERSION_RE等）
         [F-036] VersionOrder 类实现版本字符串的解析和比较
         [F-064] SubdirData 高层API类，提供 query/query_all 方法
"""

from conda.models.match_spec import MatchSpec
from conda.models.channel import Channel
from conda.api import SubdirData


# ============================================================
# 1. 创建 MatchSpec 对象的多种方式
# ============================================================

# 方式一：最简字符串形式（仅包名）
spec_name = MatchSpec("numpy")
print(f"仅包名: {spec_name}")           # numpy

# 方式二：带版本约束的字符串（空格分隔）
spec_version = MatchSpec("numpy >=1.20")
print(f"版本约束: {spec_version}")        # numpy[version='>=1.20']

# 方式三：精确版本（== 表示精确匹配）
spec_exact = MatchSpec("numpy==1.24.0")
print(f"精确版本: {spec_exact}")          # numpy==1.24.0

# 方式四：方括号语法（最灵活，支持任意字段约束）
spec_bracket = MatchSpec("numpy[version='>=1.20,<1.25',build=py310*]")
print(f"方括号语法: {spec_bracket}")

# 方式五：通道限定（:: 分隔符）
spec_channel = MatchSpec("conda-forge::numpy")
print(f"通道限定: {spec_channel}")        # conda-forge::numpy

# 方式六：通道+子目录限定
spec_subdir = MatchSpec("conda-forge/linux-64::numpy>=1.20")
print(f"通道+子目录: {spec_subdir}")

# 方式七：关键字参数构造（编程式）
spec_kwargs = MatchSpec(name="numpy", version=">=1.20", build="py310*")
print(f"关键字参数: {spec_kwargs}")

# 方式八：模糊版本（= 前缀表示模糊匹配，如 1.24.* 匹配 1.24.x）
spec_fuzzy = MatchSpec("numpy=1.24")
print(f"模糊版本: {spec_fuzzy}")          # numpy=1.24 (等价于 numpy 1.24.*)

# 方式九：三要素精确格式（name version build）
spec_exact_full = MatchSpec("numpy==1.24.0=py310h0000000_0")
print(f"精确三要素: {spec_exact_full}")


# ============================================================
# 2. 版本约束语法详解
# ============================================================

# 支持的比较运算符: >, <, ==, >=, <=, !=
constraints = [
    "python>=3.10",       # 大于等于 3.10
    "python<3.12",        # 小于 3.12
    "python!=3.9.7",      # 不等于 3.9.7
    "python=3.10",        # 模糊匹配 3.10.*
    "python==3.10.13",    # 精确匹配 3.10.13
]

for c in constraints:
    ms = MatchSpec(c)
    print(f"  {c:20s} -> 规范化: {ms}")

# 组合约束（方括号内逗号分隔，相当于 AND）
spec_combo = MatchSpec("python[version='>=3.10,<3.12']")
print(f"\n组合约束: {spec_combo}")


# ============================================================
# 3. 在 SubdirData 上查询包
# ============================================================

def query_packages(spec_str: str, channel_url: str = None):
    """
    在指定通道的 repodata 中查询匹配的包。

    参数:
        spec_str: MatchSpec 字符串
        channel_url: 通道URL（含subdir），例如
                     "https://repo.anaconda.com/pkgs/main/linux-64"
                     若为 None，则使用 query_all() 搜索所有配置通道
    """
    spec = MatchSpec(spec_str)

    if channel_url:
        # 查询单个 subdir 的 repodata
        # SubdirData 需要包含 subdir 的 Channel
        sd = SubdirData(Channel(channel_url))
        results = sd.query(spec)
    else:
        # [F-066] query_all() 静态方法查询所有通道/子目录矩阵
        results = SubdirData.query_all(spec)

    return list(results)


# 示例：查找特定版本的 numpy（注意：需要网络下载 repodata）
# results = query_packages("numpy>=1.24,<1.25")
# for pkg in results[:5]:
#     print(f"  {pkg.name}-{pkg.version}-{pkg.build}  通道:{pkg.channel.name}")


# ============================================================
# 4. 常见查询场景
# ============================================================

# 场景一：查找特定版本范围的包
spec_range = MatchSpec("pandas[version='>=2.0,<2.1']")
print(f"\n场景一 - 版本范围: {spec_range}")

# 场景二：按 build 字符串过滤（如匹配特定 Python 版本构建的包）
spec_build = MatchSpec("numpy[build=py311*]")
print(f"场景二 - build过滤: {spec_build}")

# 场景三：按通道过滤
spec_ch = MatchSpec("conda-forge::scipy")
print(f"场景三 - 通道过滤: {spec_ch}")

# 场景四：按 md5/sha256 精确查找（哈希定位）
spec_md5 = MatchSpec("*[md5=abcdef1234567890]")
print(f"场景四 - MD5定位: {spec_md5}")

# 场景五：按 track_features 查找
spec_tf = MatchSpec("numpy[track_features=mkl]")
print(f"场景五 - 特性追踪: {spec_tf}")

# 场景六：平台条件（when 字段，用于虚拟包条件）
spec_when = MatchSpec("package[when=__cuda]")
print(f"场景六 - 虚拟包条件: {spec_when}")


# ============================================================
# 5. MatchSpec 属性访问
# ============================================================

ms = MatchSpec("conda-forge::numpy[version='>=1.20',build=py310*]")

# 访问匹配组件
print(f"\nMatchSpec 解析结果:")
print(f"  name:    {ms.name}")
print(f"  version: {ms.get('version')}")
print(f"  build:   {ms.get('build')}")
print(f"  channel: {ms.get('channel')}")

# 检查 MatchSpec 是否匹配某个 PackageRecord
# (需要先获取 PackageRecord 对象)
# record = ...  # 来自 SubdirData.query()
# is_match = ms.match(record)


# ============================================================
# 6. MatchSpec 合并
# ============================================================

# MatchSpec.merge() 将多个 spec 合并为 frozenset
specs = [MatchSpec("numpy"), MatchSpec("numpy>=1.20")]
merged = MatchSpec.merge(specs)
print(f"\n合并结果: {list(merged)}")
# 合并后，更严格的约束会覆盖宽松的约束
```

## MatchSpec 语法速查

MatchSpec 的规范字符串格式为：

```
(channel(/subdir):(namespace):)name(version(build))[key1=value1,key2=value2]
```

| 字段 | 位置 | 示例 | 说明 |
|------|------|------|------|
| channel | 前缀+`::` | `conda-forge::numpy` | 通道名或URL |
| subdir | channel后+`/` | `conda-forge/linux-64::numpy` | 平台子目录 |
| name | 主体 | `numpy` | 包名（必填，可为`*`） |
| version | name后空格/`=`/`==` | `numpy>=1.20` 或 `numpy==1.24.0` | 版本约束 |
| build | version后空格/`=` | `numpy==1.24.0=py310_0` | 构建字符串 |
| 其他字段 | 方括号内 | `numpy[build_number=1]` | 任意 PackageRecord 属性 |

## 注意事项

- 方括号内的值如果包含逗号、空格或等号，必须用单引号或双引号包裹。
- 通配符 `*` 支持 glob 模式匹配，自动转换为正则。
- `^pattern$` 形式直接作为正则表达式匹配。
- `SubdirData.query()` 接受字符串、MatchSpec 或 PackageRef，字符串会自动转为 MatchSpec。
- MatchSpec 使用 `@cache` 机制做缓存，重复创建相同 spec 不会重复解析。
