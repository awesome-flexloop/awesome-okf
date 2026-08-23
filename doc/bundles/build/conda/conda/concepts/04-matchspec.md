---
okf_version: "0.2"
type: "concept"
title: "MatchSpec 包查询语言"
sources:
  - conda/models/match_spec.py
---

# MatchSpec 包查询语言

MatchSpec 是 conda 的包查询语言（Package Query Language），用于在安装、搜索、求解、移除等所有操作中精确描述"想要哪些包"。它支持丰富的语法，从简单的包名到包含版本约束、构建字符串、通道过滤、平台限定等多字段的复杂查询 [F-034]。

## 语法概览

MatchSpec 的规范化字符串形式为：

```
(channel(/subdir):(namespace):)name(version(build))[key1=value1,key2=value2]
```

其中 `()` 表示可选部分。最常见的写法是 **V3 方括号语法**：

```
name[version='>=3.6',build=py37_0,channel=conda-forge]
```

此外还兼容多种历史写法：

| 写法示例 | 说明 |
|---------|------|
| `python` | 仅包名 |
| `python=3.12` | 精确版本（等价于 `python==3.12`） |
| `python>=3.10,<3.13` | 版本范围 |
| `python 3.12 py312_0` | 空格分隔 name version build（旧版） |
| `python=3.12=py312_0` | 等号分隔三段式 |
| `conda-forge::python>=3.10` | 带通道前缀 |
| `conda-forge/linux-64::python` | 带通道和 subdir |
| `python[version='>=3.10',build_number=3]` | V3 方括号语法 |

## 正则解析器

MatchSpec 使用 7 个编译正则表达式完成字符串解析 [F-035]：

```python
# 匹配整个方括号段（旧版）
_BRACKETS_RE = re.compile(r".*(?:(\[.*\]))")
# 匹配方括号内的 key=value 对（旧版）
_BRACKETS_KV_RE = re.compile(r"""
    ([a-zA-Z0-9_-]+?)       # key
    =                        # separator
    (["']?)                 # optional opening quote
    ([^\'"]*?)              # value
    (\2)                    # matching closing quote
    (?:[,\ ]|$)             # delimiter or end
""", re.VERBOSE)
# V3 方括号段（非贪婪匹配第一个方括号）
_BRACKETS_RE_V3 = re.compile(r"^.*?(\[.*\])")
# V3 方括号内 key=value 对（支持列表值 {a,b}）
_BRACKETS_KV_RE_V3 = re.compile(r"""
    (?P<key>[a-zA-Z0-9_-]+?)
    \ *=\ *
    (?:
        \[\ *(?P<value_list>[^\[\]]*?)\ *\]    # 列表值
        |
        (?P<quote_s>["']?)(?P<value>.*?)(?P=quote_s)  # 引号字符串
    )
    (?:[,\ ]|$)
""", re.VERBOSE)
# 匹配旧版括号段（被忽略）
_PARENS_RE = re.compile(r".*(?:(\(.*\)))")
# 分离包名和版本约束
_NAME_VERSION_RE = re.compile(r"([^\ =<>!~]+)?([><!=~\ ].+)?", re.VERBOSE)
# 分离版本和 build 字符串
_VERSION_BUILD_RE = re.compile(r"((?:.+?)[^><!,|]?)(?:(?<![=!|,<>~])(?:[\ =])([^-=,|<>~]+?))?$", re.VERBOSE)
```

此外还有 CEP-26 包名校验正则 [F-035]：

```python
_CEP26_NAME_RE = re.compile(r"^(([a-z0-9])|([a-z0-9_](?!_)))[._-]?([a-z0-9]+(\.|-|_|$))*$")
_CEP26_VIRTUAL_NAME_RE = re.compile(r"^__[a-z0-9][._-]?([a-z0-9]+(\.|-|_|$))*$")
```

CEP-26 要求普通包名只能包含小写字母、数字、点、下划线、连字符；虚拟包（如 `__cuda`、`__unix`）以双下划线开头。

## V3 语法与旧版语法并存

MatchSpec 的元类 `MatchSpecType` 在 `__call__` 中实现了多态构造：

```python
class MatchSpecType(type):
    def __call__(cls, spec_arg=None, **kwargs):
        if spec_arg:
            if isinstance(spec_arg, MatchSpec) and not kwargs:
                return spec_arg  # 身份短路
            elif isinstance(spec_arg, str):
                parsed = _parse_spec_str_dispatcher(spec_arg)  # 字符串分发
                return super().__call__(**parsed)
            elif isinstance(spec_arg, Mapping):
                return super().__call__(**dict(spec_arg, **kwargs))
```

`_parse_spec_str_dispatcher()` 会按优先级尝试多种解析策略：先尝试 V3 方括号语法，再回退到旧版空格/等号分隔语法。方括号内的 key-value 对会覆盖括号外的同名字段。

## MatchSpec.merge() 合并

`MatchSpec.merge()` 是类方法，将一组 MatchSpec 按包名分组并合并约束 [F-034]：

```python
@classmethod
def merge(cls, match_specs, union=False):
    match_specs = sorted(tuple(cls(s) for s in match_specs if s), key=str)
    name_groups = groupby(attrgetter("name"), match_specs)
    unmergeable = name_groups.pop("*", []) + name_groups.pop(None, [])
    # 同包名、同 optional、同 target 的约束被 reduce(_merge) 合并
    ...
```

合并规则：同名包的多个约束通过 `_merge()` 交集合并（`union=False`，默认）或并集合并（`union=True`）。Solver 初始化时会对用户输入的 specs 调用 `MatchSpec.merge()` 以消除冗余。版本约束通过逗号连接（AND 语义），如 `>=3.10,<3.13`。

## 可匹配字段

`FIELD_NAMES` 元组列出了所有可用于查询的字段：

```python
FIELD_NAMES = (
    "channel", "subdir", "name", "version", "build", "build_number",
    "track_features", "features", "url", "md5", "sha256",
    "license", "license_family", "fn", "when", "extras", "flags",
)
```

- **字符串字段**（name, build, channel, fn 等）：支持通配符 `*`（glob→regex），首尾 `^...$` 为正则匹配
- **版本字段**（version）：使用 [VersionSpec](05-version-system.md) 解析比较运算符——VersionOrder 缓存机制确保版本字符串只解析一次 [F-036]
- **build_number**：整数，使用 `BuildNumberMatch` 支持 `>=3` 等范围
- **extras/flags**：列表值，使用 `[...]` 语法
- **when**：条件依赖（嵌套 MatchSpec 字符串）

## MatchSpec 语法速查表

| 语法 | 含义 | 示例 |
|------|------|------|
| `name` | 匹配任意版本的 name 包 | `numpy` |
| `name=version` | 前缀匹配（startswith） | `python=3.12` → `3.12.*` |
| `name==version` | 精确版本匹配 | `python==3.12.0` |
| `name>version` | 大于 | `python>3.10` |
| `name>=version` | 大于等于 | `python>=3.10` |
| `name!=version` | 不等于 | `python!=3.9` |
| `name~=version` | 兼容发布（同一次版本） | `numpy~=1.24` → `>=1.24,<1.25` |
| `name=version=build` | 精确版本+build | `python=3.12=py312_0` |
| `channel::name` | 指定通道 | `conda-forge::numpy` |
| `channel/subdir::name` | 指定通道和平台 | `conda-forge/linux-64::numpy` |
| `name[key=val,...]` | V3 多字段约束 | `numpy[version='>=1.24',build_number=0]` |
| `name[version='>=1,<2']` | 版本范围 | 逗号表示 AND |
| `*[md5=hex]` | 按 md5 精确匹配任意包 | 用于锁定具体文件 |

## 与其他模型的关系

MatchSpec 的 `version` 和 `build_number` 字段分别委托给 [VersionSpec 和 BuildNumberMatch](05-version-system.md) 处理约束匹配；`channel` 字段使用 [Channel](03-channel-subdir.md) 类型；`match()` 方法接收 [PackageRecord](06-package-records.md) 或 dict，逐字段校验匹配。
