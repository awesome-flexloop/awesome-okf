---
type: Reference
title: "特征生成 API 参考"
description: "ast.py 节点与辅助函数、compiler.py 生成入口、apply.py 冻结与应用接口的完整签名"
tags: ["api", "opentype", "ast", "fea", "freeze"]
sources:
  - id: ast-source
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/feature/ast.py
    title: scripts/feature/ast.py
  - id: compiler-source
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/feature/compiler.py
    title: scripts/feature/compiler.py
  - id: apply-source
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/feature/apply.py
    title: scripts/feature/apply.py
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# 特征生成 API 参考

## 1. 类型约定

```python
GlyphContext = str | Clazz | Sequence[str | Clazz] | None
FeatureContent = Clazz | Lookup | Line | Sequence["FeatureContent"] | None
```

绝大多数函数接受“字形名字符串 / `Clazz` / 二者的序列”，内部统一展开为 `.fea` 文本。

## 2. ast.py — 节点

### Line

```python
class Line:
    def __init__(self, text: str, level: int = 0) -> None: ...
    def indent(self) -> "Line": ...
```

`indent()` 返回层级 +1 的新行；空文本的层级归零，避免产生纯空白行。

### Clazz

```python
class Clazz:
    def __init__(self, name: str, glyphs: Sequence[str | Clazz] | None = None) -> None: ...
    def use(self) -> str: ...      # "@Name"
    def state(self) -> Line: ...   # "@Name = [g1 g2 ...];"
```

### Lookup

```python
class Lookup:
    def __init__(self, name: str, desc: str | None, content: list) -> None: ...
    def use(self) -> Line: ...              # "lookup Name;"
    def state(self) -> list[Line]: ...      # 带注释的完整 lookup 块
```

### Feature

```python
class Feature:
    def __init__(self, tag: str, content: Clazz | Lookup | Line | list, version) -> None: ...
    def use(self) -> Line: ...                 # "feature tag;"
    def get_name_lines(self) -> list[Line]: ... # 默认空
    def state(self) -> list[Line]: ...          # "feature tag { ... } tag;"
```

### FeatureWithDocs / CharacterVariant / StylisticSet

```python
class FeatureWithDocs(Feature):
    def __init__(
        self, id: int, tag: str, desc: str,
        content: Clazz | Lookup | Line | list,
        version: str, example: str,
    ) -> None: ...
    def desc_item(self) -> str: ...   # "- [vX.Y] tag: desc"

class CharacterVariant(FeatureWithDocs):
    def __init__(self, id: int, desc: str, content, version: str, example: str) -> None: ...
    # 1 <= id <= 99，tag = f"cv{id:02d}"，生成 cvParameters 名称块

class StylisticSet(FeatureWithDocs):
    def __init__(self, id: int, desc: str, content, version: str, example: str) -> None: ...
    # 1 <= id <= 20，tag = f"ss{id:02d}"，生成 featureNames 名称块
```

## 3. ast.py — 辅助函数

```python
def gly(g: str | Clazz | Sequence[str | Clazz], suffix: str = "", overwrite=False) -> str: ...
def gly_seq(g: str | list[str], variant: Literal["sta", "mid", "end"]) -> list[str]: ...
def cls(glyphs: str | Clazz | Sequence[str | Clazz], *rest: str | Clazz) -> str: ...
def cls_states(*cls: Clazz) -> list[Line]: ...

def langsys(script: str, lang: str) -> Line: ...
def lang(lang: str) -> Line: ...
def script(script: str) -> Line: ...

def subst(
    prefix: GlyphContext,
    glyph: str | Clazz,
    suffix: GlyphContext,
    replace: str | Clazz,
) -> Line: ...
def subst_map(
    glyphs: str | list[str],
    source_suffix: str = "",
    target_suffix: str = "",
) -> list[Line]: ...
def subst_liga(
    source: str | list[str],
    target: str | None = None,
    lookup_name: str | None = None,
    desc: str | None = None,
    surround: list[tuple[GlyphContext, GlyphContext]] | None = None,
    ign_prefix: str | Clazz | None = None,
    ign_suffix: str | Clazz | None = None,
) -> ...: ...
def ign(prefix: GlyphContext, glyph: str | Clazz, suffix: GlyphContext) -> Line: ...

def create(content: list, indent: int = 2) -> str: ...
def recursive_iterate(data): ...
def flatten_to_lines(data: Line | Clazz | Lookup | Feature | list | tuple) -> list[Line]: ...
def clone_empty(feature: FeatureWithDocs, desc_prefix: str = "") -> ...: ...
def filter_empty(features: list[FeatureWithDocs], full: bool) -> ...: ...
```

`subst` 的示例：

```python
subst(["-"], "b", cls, "d")   # Line("sub hyphen b' @cls by d;")
```

`subst_map` 的示例：

```python
subst_map(["Q", "all", gly("{{")], target_suffix=".cv01")
# sub Q by Q.cv01;
# sub all by all.cv01;
# sub braceleft_braceleft.liga by braceleft_braceleft.liga.cv01;
```

`ign` 的示例：

```python
ign("{", "b", ["c", "d"])   # ignore sub braceleft b' c d;
```

## 4. compiler.py — 生成入口

```python
@dataclass(frozen=True)
class FeatureGenOptions:
    is_italic: bool = False
    is_cn: bool = False
    is_normal: bool = False
    is_calt: bool = True
    enable_infinite: bool = True
    enable_tag: bool = True
    remove_italic_calt: bool = False

def generate_fea_string(
    options: FeatureGenOptions | None = None,
    *,
    is_italic: bool = False,
    is_cn: bool = False,
    is_normal: bool = False,
    is_calt: bool = True,
    enable_infinite: bool = True,
    enable_tag: bool = True,
    remove_italic_calt: bool = False,
) -> str: ...
```

- `options` 非空时忽略所有关键字参数；
- 返回值是完整特征源码，包含字形类、语言系统、基础特征、风格变体与上下文规则；
- 典型调用：`generate_fea_string(is_italic=False, is_cn=True)`。

其他公开辅助：

```python
def generate_fea_string_cn_only() -> str: ...
def get_all_calt_text() -> ...: ...
def get_cv_desc() -> ...: ...
def get_cv_italic_desc() -> ...: ...
def get_cv_cn_desc() -> ...: ...
def get_ss_desc() -> ...: ...
def get_total_feat_dict() -> dict[str, str]: ...
def get_freeze_moving_rules() -> list[str]: ...
```

常量：

```python
NORMAL_ENABLED_FEATURES = (
    "cv01", "cv02", "cv33", "cv34", "cv35", "cv36",
    "cv61", "cv62", "ss05", "ss06", "ss07", "ss08",
)
CJK_FEATURES = (cv96.cv96_feat_cn, cv97.cv97_feat_cn, cv98.cv98_feat_cn, cv99.cv99_feat_cn)
```

## 5. apply.py — 冻结与应用

### 数据类

```python
@dataclass(frozen=True, slots=True)
class FeatureSubstitution:
    tag: str
    source: str
    target: str

@dataclass(frozen=True, slots=True)
class PreparedFeatureSource:
    source: str
    substitutions: tuple[FeatureSubstitution, ...]
```

### 源准备

```python
def prepare_feature_source(
    config: ResolvedConfig,
    *,
    glyph_names: tuple[str, ...],
    issue_fea_dir: str | Path,
    is_italic: bool,
    is_cn: bool,
    fea_path: str,
) -> PreparedFeatureSource: ...
```

职责：选择生成式或文件式输入 → 解析特征 → 应用冻结策略 → 收集需要烘焙的单一替换。解析失败时把问题源码写入 `issue_fea_dir` 并抛出 `SyntaxError`。

```python
def prepare_designspace_features(
    config: ResolvedConfig,
    designspace: DesignSpaceDocument,
    *,
    issue_fea_dir: str | Path,
    is_italic: bool,
    fea_path: str,
) -> PreparedFeatureSource: ...
```

职责：在 Fontmake 之前冻结每个 master 的轮廓，并把最终特征源码写入各 UFO 的 `features.text`。若 `standard_zero` 为真，先调用 `apply_standard_zero()`。

```python
def apply_standard_zero(designspace: DesignSpaceDocument) -> None: ...
def apply_ufo_substitutions(
    designspace: DesignSpaceDocument,
    substitutions: tuple[FeatureSubstitution, ...],
) -> None: ...
```

`apply_standard_zero` 交换 `zero` 与 `zero.zero` 的轮廓，使注册的 `zero` 特征选择斜零。`apply_ufo_substitutions` 只替换轮廓，不替换元数据。

### 二进制应用

```python
def apply_binary_features(
    config: ResolvedConfig,
    font: TTFont,
    issue_fea_dir: str | Path,
    *,
    is_italic: bool,
    is_cn: bool,
    fea_path: str,
    outline_tags: frozenset[str] = frozenset(),
) -> None: ...
```

职责：对成品 TTFont 应用准备好的特征表；`outline_tags` 指定哪些标签的单一替换可以在二进制阶段继续烘焙（CJK 静态合并后的晚到字形即走此路径）。

## 6. 使用示例

```python
from scripts.feature.compiler import generate_fea_string
from scripts.feature.ast import Clazz, Lookup, Feature, subst, create

# 直接生成完整源码
fea = generate_fea_string(is_italic=False, is_cn=False)

# 构造自定义片段
cls_digit = Clazz("Digit", ["zero", "one", "two", "three"])
lookup = Lookup(
    name="example_lookup",
    desc="Example substitution",
    content=[subst("a", "b", None, "c")],
)
print(create([cls_digit, Feature("calt", [lookup], "1.0")]))
```

## 7. 稳定性说明

- `ast.py`、`compiler.py` 的公开函数是特征模块的主要契约；
- `apply.py` 的 `prepare_*` 与 `apply_binary_features` 供流水线调用，属于内部契约；
- 下划线开头的函数（`_feature_source`、`_single_substitutions`、`_rewrite_feature_tree` 等）不保证跨版本稳定。

## 相关文档

- 规则组织与标签：[特征系统](../concepts/03-feature-system.md)
- 生成器设计动机：[特征 AST 生成器](../concepts/04-feature-ast-generator.md)
- 冻结语义：[特征冻结机制](../concepts/05-freeze-mechanism.md)
