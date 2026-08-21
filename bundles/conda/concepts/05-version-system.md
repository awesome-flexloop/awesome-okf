---
okf_version: "0.2"
type: "concept"
title: "VersionOrder 版本系统"
sources:
  - conda/models/version.py
---

# VersionOrder 版本系统

conda 实现了一套独立的版本解析与比较系统，核心由三个类组成：`VersionOrder`（版本值的解析与排序）、`VersionSpec`（版本约束匹配）和 `BuildNumberMatch`（构建号匹配）。这套系统支持 epoch、预发布、开发版、后置发布、本地版本标签等复杂版本语义 [F-036]。

## 版本字符串解析规则

`VersionOrder` 使用 `SingleStrArgCachingType` 元类实现单字符串参数缓存——同一个版本字符串只解析一次，后续直接返回缓存实例 [F-036]。解析流程如下 [F-037]：

1. **Epoch 分割**：按 `!` 分割为 epoch 和 version 部分。无 `!` 时 epoch 默认为 `"0"`。epoch 必须是整数。
2. **Local version 分割**：按 `+` 分割主版本和本地版本标签。无 `+` 时本地版本为空。
3. **组件分割**：主版本和本地版本分别按 `.` 和 `_` 分割为组件序列（分割前 `_` 替换为 `.`）。
4. **数字/字母 runs 分割**：每个组件再按连续数字/非数字分割为子组件，如 `1a2` → `[1, 'a', 2]`。
5. **类型转换**：数字子组件转 `int`，字母子组件转小写；特殊标记 `"dev"` 转为大写 `"DEV"`（使其排序在 `_` 之前），`"post"` 转为 `float("inf")`（最大）。
6. **填充对齐**：以字母开头的组件前插入填充值 `0`，确保数字和字母相位一致，如 `1.1.a1` 等价于 `1.1.0a1`。
7. **尾部下划线特殊处理**：版本末尾的 `_`（如 openssl 的 `1.0.1_`）作为整体保留，不单独分割。

```python
# 解析示例
# 1.2g.beta15.rc  =>  [[0], [1], [2, 'g'], [0, 'beta', 15], [0, 'rc']]
# 1!2.15.1_ALPHA  =>  [[1], [2], [15], [1, '_alpha']]
```

对应的内部数据结构是 `self.version`（epoch + 主版本组件列表）和 `self.local`（本地版本组件列表），每个组件都是数字/字符串混合的列表。

## 版本比较算法

`VersionOrder` 实现了完整的比较运算符（`__eq__`, `__lt__`, `__le__`, `__gt__`, `__ge__`, `__ne__`），比较规则为 [F-037]：

- **逐组件字典序比较**：对 `self.version` 和 `other.version` 使用 `zip_longest` 逐对比较，缺失项以 `fillvalue=0` 填充
- **整数 vs 字符串**：字符串始终小于整数（`'rc' < 0`）
- **特殊值排序**：`"DEV"`（小写 `dev`）< `"_"` < 其他字母 < 数字 < `float("inf")`（小写 `post`）
- **大小写不敏感**：解析时统一转小写，`1.1RC` == `1.1rc`
- **本地版本**：仅当主版本（含 epoch）相等时才比较 local 部分
- **缺失组件等价于 0**：`1.1` == `1.1.0`

完整排序示例（从低到高）：

```
0.4 < 0.4.0 < 0.4.1.rc == 0.4.1.RC < 0.4.1 < 0.5a1 < 0.5b3 < 0.5C1
< 0.5 < 0.9.6 < 0.960923 < 1.0 < 1.1dev1 < 1.1_ < 1.1a1
< 1.1.0dev1 == 1.1.dev1 < 1.1.a1 < 1.1.0rc1 < 1.1.0 == 1.1
< 1.1.0post1 == 1.1.post1 < 1.1post1 < 1996.07.12
< 1!0.4.1 < 1!3.1.1.6 < 2!0.4.1
```

OpenSSL 风格版本（字母作为计数器而非预发布标记）可通过追加下划线解决：`1.0.1_ < 1.0.1a` 为 `True`。

## VersionSpec 约束匹配

`VersionSpec` 类同样使用 `SingleStrArgCachingType` 缓存，将版本约束字符串解析为匹配器函数 [F-038]。支持的运算符通过 `OPERATOR_MAP` 定义：

```python
OPERATOR_MAP = {
    "==": op.__eq__,       # 精确等于
    "!=": op.__ne__,       # 不等于
    "<=": op.__le__,       # 小于等于
    ">=": op.__ge__,       # 大于等于
    "<":  op.__lt__,       # 小于
    ">":  op.__gt__,       # 大于
    "=":  VersionOrder.startswith,  # 前缀匹配（startswith）
    "!=startswith": lambda x, y: not x.startswith(y),
    "~=": compatible_release_operator,  # 兼容发布（PEP 440 风格）
}
```

约束解析支持多种形式：

| 约束形式 | 匹配器 | 说明 |
|---------|--------|------|
| `1.2.3` | 精确匹配 `==` | 无运算符默认精确匹配 |
| `>=1.0,<2.0` | `all_match`（AND） | 逗号分隔的约束全部满足 |
| `1.0|2.0` | `any_match`（OR） | 竖线分隔任一满足 |
| `>=1.0|(>2.0,<3.0)` | 组合树 | 括号分组，支持嵌套 |
| `1.1.*` / `1.1*` | `startswith` | 前缀匹配 |
| `^1\.2.*$` | 正则匹配 | 首尾锚定的正则 |
| `*` | `always_true_match` | 通配，匹配所有版本 |
| `~=1.2` | 兼容发布 | `>=1.2,<1.3`（去掉末段） |

`treeify()` 函数将约束字符串解析为表达式树（嵌套元组），支持 `,`（AND，优先级低）和 `|`（OR，优先级高）以及括号分组。`untreeify()` 反向将树转回字符串。

```python
# 表达式树示例
treeify("1.2.3,>4.5.6")        # (',', '1.2.3', '>4.5.6')
treeify("1.2.3|<=7.8.9")        # ('|', '1.2.3', '<=7.8.9')
treeify("(1.0|2.0),<3.0")       # (',', ('|', '1.0', '2.0'), '<3.0')
```

VersionSpec 的 `merge()` 方法将两个约束用逗号连接（AND 语义），`union()` 用竖线连接（OR 语义）。

## BuildNumberMatch

`BuildNumberMatch` 继承自 `BaseSpec`，处理 build number（整数构建号）的约束匹配 [F-038]。它复用 `version_relation_re` 解析运算符，但 matcher_vo 直接与整数比较而非 VersionOrder：

- 纯整数（如 `3`）→ 精确匹配
- 运算符+整数（如 `>=3`、`<5`）→ 使用比较运算符
- `*` → 匹配所有
- 正则（`^...$`）→ 正则匹配

build number 是一个单调递增的整数，同一包名+版本的每次重构建递增 1，用于区分同一版本的不同构建。

## 与其他模型的关系

VersionOrder 和 VersionSpec 是 [MatchSpec](04-matchspec.md) 中 `version` 字段的底层引擎——MatchSpec 解析出的 version 约束字符串会被传给 VersionSpec 构造；BuildNumberMatch 服务于 `build_number` 字段。[PackageRecord](06-package-records.md) 的 `version` 字段是字符串，在求解时通过 VersionOrder 进行比较和排序。
