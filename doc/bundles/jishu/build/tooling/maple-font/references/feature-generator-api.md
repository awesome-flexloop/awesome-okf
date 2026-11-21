---
type: Reference
title: "Feature 生成器 API"
description: "Maple Mono Python AST 风格 OpenType Feature 生成器——核心类与 generate_fea_string 主函数"
tags: ["maple-mono", "feature", "ast", "reference", "api", "opentype"]
sources:
  - id: FEATURE-AST
    resource: "source/py/feature/ast.py"
    description: "AST 类定义"
  - id: FEATURE-INIT
    resource: "source/py/feature/__init__.py"
    description: "generate_fea_string 主函数"
  - id: FEATURE-CALT-INIT
    resource: "source/py/feature/calt/__init__.py"
    description: "calt 查找表组装"
  - id: FEATURE-CV-REGULAR
    resource: "source/py/feature/regular.py"
    description: "regular 风格 cv 列表"
prerequisites:
  - "../concepts/03-feature-system.md"
  - "../concepts/04-feature-ast-generator.md"
---

# Feature 生成器 API

Maple Mono 的 OpenType Feature 生成器是一个小型 DSL——用 Python 对象组合生成 .fea 字符串。以下是完整 API 参考。

## 入口：generate_fea_string()

```python
from source.py.feature import generate_fea_string

def generate_fea_string(
    is_italic: bool,
    is_cn: bool,
    is_calt: bool,
    enable_infinite: bool,
    remove_italic_calt: bool,
    feature_freeze: dict[str, Literal["enable", "disable", "ignore"]],
) -> str:
    """
    生成完整的 OpenType Feature .fea 字符串
    
    参数:
        is_italic: 是否斜体字体（决定用 regular 还是 italic 的 cv/ss 列表）
        is_cn: 是否中文版（加入中文标点变体 cv96-99）
        is_calt: 是否启用 calt 连字（false 则移除 calt 层）
        enable_infinite: 是否启用无限箭头扩展（---->------>）
        remove_italic_calt: 斜体时是否移除 calt 中破坏草书风格的规则
        feature_freeze: {特征名: 模式} 三模式配置
    
    返回:
        完整 .fea 文件字符串，可直接 addOpenTypeFeaturesFromString 注入
    
    示例:
        >>> fea = generate_fea_string(
        ...     is_italic=False, is_cn=False, is_calt=True,
        ...     enable_infinite=True, remove_italic_calt=False,
        ...     feature_freeze={"cv01": "enable", "zero": "disable"}
        ... )
        >>> fontTools.addOpenTypeFeaturesFromString(font, fea)
    """
```

## AST 类（source/py/feature/ast.py）

### FeatureWithDocs

```python
class FeatureWithDocs:
    """带文档的 OpenType Feature"""
    name: str
    description: str
    lookups: list[Lookup]

    def to_fea(self) -> str:
        """生成 feature XXX { ... } XXX; 块"""
        # 输出格式:
        # # description
        # feature name {
        #   # Lookup.description
        #   lookup_name {
        #     sub ...;
        #   } lookup_name;
        # } name;
```

### Lookup

```python
class Lookup:
    """OpenType 查找表"""
    sub: list[str]              # sub 规则字符串列表
    description: str | None      # 文档注释
    flags: int | None            # Lookup flag（如 UseMarkFilteringSet）
    lookups: list[Lookup] | None  # 嵌套 lookup（calt 特殊情况）

    def to_fea(self, indent: str = "  ") -> str:
        """生成 lookup_name { ... } 块"""
```

### ClassDef

```python
class ClassDef:
    """字形类定义"""
    name: str                    # "@A" / "@Base"
    glyphs: list[str]            # ["a", "A", "à"]

    def to_fea(self) -> str:
        """生成 @name = [glyph1 glyph2 ...];"""
```

### ClassListWithDocs

```python
class ClassListWithDocs:
    """带文档的字形类列表"""
    class_list: list[ClassDef]
    description: str

    def to_fea(self) -> str:
        """生成 .fea 顶部的所有 @classdef"""
```

## calt 模块 API

### calt.get_calt()

```python
from source.py.feature.calt import get_calt

def get_calt(
    enable_infinite: bool = False,
    remove_italic_calt: bool = False,
) -> list[FeatureWithDocs]:
    """
    获取 calt feature 的所有 lookup
    
    参数:
        enable_infinite: 启用无限箭头扩展
        remove_italic_calt: 移除斜体破坏规则
    
    返回:
        list[FeatureWithDocs] — 通常只有一个，name="calt"
    """
```

### 各子模块 get_xxx_lookup()

每个子模块导出一个纯函数，返回 Lookup 对象：

```python
from source.py.feature.calt import (
    asciitilde, cross, equal_arrow, escape,
    hyphen_arrow, markup_like, pipe, tag,
    whitespace,
)

# 每个函数签名相同
asciitilde.get_asciitilde_lookup() -> Lookup
cross.get_cross_lookup() -> Lookup
pipe.get_pipe_lookup() -> Lookup
# ... 等等
```

## cv / ss 模块 API

### regular.py

```python
from source.py.feature import regular

# 返回 regular 风格的所有 cv 变体 FeatureWithDocs
regular.cv_list(is_cn: bool) -> list[FeatureWithDocs]
regular.ss_list() -> list[FeatureWithDocs]
```

### italic.py

```python
from source.py.feature import italic

# 返回 italic 风格的所有 cv 变体（cv31-cv44）
italic.cv_list() -> list[FeatureWithDocs]
italic.ss_list() -> list[FeatureWithDocs]
```

### 各 cv / ss 子模块

```python
# cv 子模块（cv01-cv11, cv31-cv44, cv61-cv66, cv96-cv99）
from source.py.feature.cv.cv01 import get_cv01_feature
get_cv01_feature() -> FeatureWithDocs

# ss 子模块（ss01-ss11）
from source.py.feature.ss.ss07 import get_ss07_feature
get_ss07_feature() -> FeatureWithDocs
```

## base 模块（查找表基础设施）

### base/case.py, ccmp.py, clazz.py, lang.py, locl.py, number.py

这些模块提供 calt 查找表的基础设施：

| 模块 | 作用 |
|------|------|
| `clazz` | 定义 @A / @B / @Base 等字形类 |
| `ccmp` | Composition / Decomposition 替换规则 |
| `case` | 大小写映射（calt 中间查找表） |
| `locl` | 语言特定字形变体 |
| `number` | 数字间距调整 |

## 完整 import 链

```
build.py
  └─ FontConfig.patch_font_feature()
      └─ generate_fea_string()        ← 主入口
          ├─ regular.cv_list()        ← regular 风格 cv 列表
          ├─ italic.cv_list()         ← italic 风格 cv 列表
          ├─ regular.ss_list()        ← ss 样式集
          ├─ calt.get_calt()          ← calt 连字查找表
          │   ├─ pipe.get_pipe_lookup()
          │   ├─ asciitilde.get_asciitilde_lookup()
          │   ├─ cross.get_cross_lookup()
          │   └─ ... 10+ 子模块
          └─ filter_by_freeze()        ← 应用 feature_freeze 三模式
```

## 扩展指南

### 新增一种连字

1. 在 `source/py/feature/calt/` 下新建 `.py` 文件，导出 `get_xxx_lookup() -> Lookup`
2. 在 `source/py/feature/calt/__init__.py` 的 `get_calt_lookup()` 中导入并添加
3. 在 `source/py/features/regular.fea` 中同步更新（font-patcher 模式需要）

### 新增一个 cv 变体

1. 在 `source/py/feature/cv/` 下新建 `cvNN.py`，导出 `get_cvNN_feature() -> FeatureWithDocs`
2. 在 `source/py/feature/regular.py` 或 `italic.py` 的列表中添加
3. 在 `source/py/features/regular.fea` 中同步更新
4. 在 `config.json` 的 `feature_freeze` 默认值中添加对应条目

### 测试你的改动

```bash
# 生成 .fea 查看效果
python task.py fea
cat source/features/regular.fea | head -100
```

或直接：
```python
from source.py.feature import generate_fea_string
fea = generate_fea_string(False, False, True, False, False, {})
print(fea[:2000])
```
