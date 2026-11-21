---
type: Concept
title: "Feature AST 生成器"
description: "Maple Mono 如何用 Python AST 对象组合生成 OpenType .fea 字符串——FeatureWithDocs/Lookup/ClassDef 设计"
tags: ["maple-mono", "feature", "ast", "fea", "code-generation", "dsl"]
sources:
  - id: FEATURE-AST
    resource: "source/py/feature/ast.py"
    description: "FeatureWithDocs / Lookup / ClassDef 等 AST 类定义"
  - id: FEATURE-INIT
    resource: "source/py/feature/__init__.py"
    description: "generate_fea_string 主函数与各层组装逻辑"
  - id: CALT-PIPE
    resource: "source/py/feature/calt/pipe.py"
    description: "calt 管道箭头模块——典型的 Lookup 组合示例"
prerequisites:
  - "03-feature-system"
next:
  - "05-freeze-mechanism"
related:
  - "../references/feature-generator-api.md"
status: draft
---

# Feature AST 生成器

Maple Mono 不手写 OpenType .fea 文件，而是用 Python 对象**组合生成** .fea 字符串。这种"Python 作为 DSL 宿主"的设计，是构建系统最大也最值得学习的架构决策。

## 为什么不用手写 .fea

手写 .fea 文件有两个问题 Maple Mono 必须解决：

**问题 1：特征规则要随构建参数动态变化**

同一个 `calt` 查找表在不同构建下需要不同内容：
- `is_italic=True` 时，需要排除 `l` `i` 等斜体字母的连体连字
- `enable_infinite=True` 时，`---->` 扩展为无限箭头
- `is_cn=True` 时，要额外加入中文标点变体
- `is_variable=True` 时，部分规则移到 `rclt` 查找表

手写 .fea 意味着维护多份文件（regular.fea / italic.fea / cn.fea / italic_cn.fea ...），极其混乱。

**问题 2：每条规则需要可追溯文档**

开发者想知道"cv01 这条变体规则控制了哪些字形、默认是什么、启用后是什么"——手写 .fea 注释容易过时。

## 核心 AST 类设计

### 整体结构

```
┌────────────────────────────────────────────────────────────┐
│                    .fea 文件输出                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  feature calt {                                        │ │
│  │    sub [a b] by c;                    ← Lookup.sub     │ │
│  │    sub a b by c;                      ← Lookup.sub (3)  │ │
│  │  } calt;                                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                    ▲                                        │
│                    │                                        │
│  ┌─────────────────┴─────────────────────────────────────┐ │
│  │  FeatureWithDocs                                       │ │
│  │    name = "calt"                                       │ │
│  │    description = "上下文感知连字"                         │ │
│  │    lookups: List[Lookup]                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                    ▲                                        │
│                    │                                        │
│  ┌─────────────────┴─────────────────────────────────────┐ │
│  │  Lookup                                                 │ │
│  │    description = "等号箭头"                              │ │
│  │    sub: List[Substitute]                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                    ▲                                        │
│                    │                                        │
│  ┌─────────────────┴─────────────────────────────────────┐ │
│  │  Substitute (str)                                      │ │
│  │    "sub = > => by =>_arrow_1;"                          │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### 类层级

```python
# ast.py 核心类

class ClassDef:
    """字形类定义，如 @A = [a A];"""
    name: str      # "@A"
    glyphs: list   # ["a", "A"]

class Lookup:
    """查找表——包含若干 sub 规则 + 可选文档"""
    sub: list                       # 替换规则字符串列表
    description: str | None         # 文档注释
    flags: int | None               # Lookup flag
    lookups: list[Lookup] | None    # 嵌套 lookup

class FeatureWithDocs:
    """带文档的 OpenType Feature"""
    name: str                       # "calt" / "cv01" / "ss08"
    description: str                # 文档（写入 .fea 注释）
    lookups: list[Lookup]           # 该 feature 包含的所有 lookup

class ClassListWithDocs:
    """带文档的字形类列表"""
    class_list: list[ClassDef]
    description: str
```

### Substitute 的两种模式

OpenType 替换有两种语法，Maple Mono 都支持：

**单字形替换**（2 参数）：
```fea
sub a by b;
# 在 Python 中：Lookup(sub=["sub a by b;"])
```

**序列替换**（3 参数）：
```fea
sub a b by c;
# 在 Python 中：Lookup(sub=["sub a b by c;"])
```

**带上下文替换**（4-5 参数）：
```fea
sub = > => by =>_arrow_1;
# 在 Python 中：Lookup(sub=["sub = > => by =>_arrow_1;"])
```

## 代码组织模式

以 `calt/pipe.py` 为例（管道箭头连字），典型的模块结构：

```python
# source/py/feature/calt/pipe.py

def get_pipe_lookup():
    return Lookup(
        description="管道箭头",
        sub=[
            "sub | >  |>_pipe_1;",
            "sub |>_pipe_1 >  ||>_pipe_2;",
            "sub |>_pipe_1 [>=]  |>_ge_1;",
            "sub ||>_pipe_2  =>  ||>=_pipe_3;",
            "sub ||>=_pipe_3  =  ||>=_pipe_4;",
            "sub |>_pipe_1 <  |<_back_1;",
            # ... 更多规则
        ],
    )
```

每个 lookup 独立成函数返回，便于 `__init__.py` 组合：

```python
# source/py/feature/calt/__init__.py

def get_calt_lookup(enable_infinite=False, is_variable=False, ...):
    """组装 calt 的所有 lookup"""
    lookups = []
    lookups.append(asciitilde.get_asciitilde_lookup())
    lookups.append(cross.get_cross_lookup())
    lookups.append(pipe.get_pipe_lookup())
    # ... 按参数条件添加
    if enable_infinite:
        lookups.append(equal_arrow.get_infinite_arrow_lookup())
    # ...
    return lookups
```

## generate_fea_string 主函数

最终由 `generate_fea_string()` 函数将三层 AST 组装成完整的 .fea 字符串：

```python
# source/py/feature/__init__.py

def generate_fea_string(
    is_italic: bool,
    is_cn: bool,
    is_calt: bool,
    enable_infinite: bool,
    remove_italic_calt: bool,
    feature_freeze: dict[str, Literal["enable", "disable", "ignore"]],
) -> str:
    # 1. 选择 regular / italic / cn 版本
    regular_classes = class_list(is_cn)
    cv_features = cv_list(is_italic, is_cn)
    ss_features = ss_list(is_italic, is_cn)
    calt_features = get_calt(...)

    # 2. 按 feature_freeze 过滤
    enabled_features = filter_by_freeze(
        cv_features + ss_features, feature_freeze
    )

    # 3. 组装 .fea
    lines = []
    lines += regular_classes.to_fea()       # @classdef 部分
    lines += calt_features.to_fea()          # feature calt { ... }
    lines += enabled_features.to_fea()       # feature cv01 { ... }
    return "\n\n".join(lines)
```

## 为什么这个设计优秀

| 优势 | 说明 |
|------|------|
| **动态组合** | 同一个生成函数根据参数产出不同 .fea，避免多文件维护 |
| **内嵌文档** | 每条 Lookup 自带 description，写入 .fea 注释，且可被 Playground 前端读取渲染 |
| **测试友好** | 可以为每个 Lookup 单独写测试（断言输出字符串包含预期 sub 规则） |
| **扩展性强** | 新增一种连字只需：在 calt/ 下新建 .py → 写 get_xxx_lookup() → 在 `__init__.py` 导入 |
| **静态字体 vs 变量字体复用** | 同样的特征 AST，静态字体直接注入，变量字体将 cv/ss 转为 rclt |

## 与手写 .fea 对比

| 对比项 | Maple Mono Python AST | 手写 .fea |
|--------|----------------------|-----------|
| 动态参数 | ✅ `if enable_infinite` 加规则 | ❌ 必须多份文件或手写条件分支 |
| 代码复用 | ✅ 函数返回 Lookup 对象组合 | ❌ 复制粘贴 |
| 文档自动生成 | ✅ 每个 Lookup 自带 description | ❌ 注释容易过时 |
| IDE 支持 | ✅ 自动补全、语法高亮 | ⚠️ .fea 语法高亮有限 |
| 测试 | ✅ Python pytest | ❌ 困难 |
| 新手上手成本 | 需理解 AST 结构 | 直接写 OpenType 语法 |

## 设计洞察

1. **Python 作为 DSL 宿主**：这不是通用 Python 的滥用，而是"用你已经在写的语言当 DSL"——Maple Mono 构建系统全是 Python，.fea 只是最终产出物
2. **纯函数式 Lookup**：每个 `get_xxx_lookup()` 是纯函数，输入固定输出固定，不依赖全局状态
3. **分层组合**：calt 层组合各连字 lookup，cv/ss 层组合各变体 Lookup，最后 `generate_fea_string` 组装全部
4. **文档即代码**：`FeatureWithDocs.description` 和 `Lookup.description` 是代码的一部分，不是独立 README
