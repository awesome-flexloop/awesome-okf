---
type: Concept
title: "特征冻结机制"
description: "Maple Mono 的 OpenType Feature 时冻结——enable/disable/ignore 三模式如何将动态规则固化到字形表"
tags: ["maple-mono", "freeze", "feature", "opentype", "fontfreeze"]
sources:
  - id: FREEZE-PY
    resource: "source/py/freeze.py"
    description: "freeze_feature() 主函数与三模式实现"
  - id: FONT-CONFIG-FREEZE
    resource: "build.py#FontConfig.freeze_feature_static"
    description: "FontConfig 中的特征冻结调度"
  - id: CONFIG-FREEZE-FIELD
    resource: "config.json#feature_freeze"
    description: "feature_freeze 配置段默认值"
prerequisites:
  - "03-feature-system"
  - "04-feature-ast-generator"
next:
  - "06-nerd-font-patching"
related:
  - "../examples/custom-feature-build.md"
status: draft
---

# 特征冻结机制

特征冻结（Feature Freeze）是 Maple Mono 构建系统最独特也最容易被忽略的能力。它的作用是**把动态 OpenType Feature 规则固化到字形表**，让最终用户拿到的字体就是定制好的样子——不需要字体渲染器支持 Feature 切换。

## 问题背景

默认的 OpenType Feature 是**动态的**：浏览器、IDE、终端渲染器根据用户偏好（如 "Ligatures: off"）决定是否应用规则。这带来两个问题：

1. **无法控制默认值**：用户设置可能关掉你精心设计的连字
2. **静态字体 vs 变量字体矛盾**：静态字体（TTF/OTF）没有 `rclt` 查找表，cvXX 变体只能以 `cvXX` feature 形式存在——但不是所有渲染器都支持

Maple Mono 的解决方案：**在构建时把你想要的 Feature 规则固化到字形表，把你不想要的从字体表中移除**。

## 三模式配置

`config.json` 的 `feature_freeze` 字段支持三种处理模式：

```json
"feature_freeze": {
  "cv01":  "ignore",   // 模式 1：不处理
  "ss08":  "enable",   // 模式 2：固化为默认
  "zero":  "disable"   // 模式 3：彻底移除
}
```

| 模式 | 行为 | 对静态字体 | 对变量字体 |
|------|------|-----------|-----------|
| `ignore` | 不处理，保留原 Feature | 原封不动 | 原封不动 |
| `enable` | 规则移入 `calt`，固化为默认 | 自动生效（不需要手动启用 cv01） | 移入 calt |
| `disable` | 从字体表中移除该 Feature | 彻底消失（即使手动启用也无效） | 彻底消失 |

## enable 模式：固化为默认

这是最常用的模式——"我就要 cv01 的品牌化字形当默认样式"：

```
# 构建前：cv01 是可选的（默认关闭）
字体表中有 cv01 feature，包含 A → A.brand, $ → $.brand 等替换规则

# 构建后（enable）：cv01 的规则固化到 calt
calt 查找表中加入 A → A.brand, $ → $.brand 的替换
最终用户看到的就是 A.brand / $.brand 这个默认字形
```

技术实现：在字形表中查找 `cv01` 查找表的 sub 规则，用 `fontTools` 把规则从 `cv01` 搬移到 `calt`，然后从 `cv01` 中清除。

## disable 模式：彻底移除

这是最激进的模式——"我不想要这个连字/变体，即使手动启用也不行"：

```
# 构建前：zero 特征允许 0 → 0.slash
字体表中有 zero feature

# 构建后（disable）：zero 从字体表中消失
不存在 zero feature，也没有 zero.slash 替换规则
```

技术实现：用 `fontTools` 的 `removeOpenTypeFeatures(font, ["zero"])` 从 GSUB 表中删除指定 feature 及其 lookup。

## ignore 模式：不处理

最保守的模式——"我对这个特征没有明确偏好，保留原样"。

## CLI --feat 参数如何映射

CLI `--feat cv01,ss07,zero` 参数等价于在 config.json 中把列出的所有特征置为 `enable`：

```bash
# 这两种方式效果相同
python build.py --feat cv01,ss07,zero
# 等价于 config.json: "feature_freeze": { "cv01": "enable", "ss07": "enable", "zero": "enable" }
```

而 `--normal` 预设会把 12 个常规特征置为 enable（详见 [03-Feature 系统](03-feature-system.md) 的 normal_enabled_features）。

## freeze_feature 主流程

`source/py/freeze.py` 的 `freeze_feature()` 函数是特征冻结的核心：

```python
def freeze_feature(font, feature_freeze, is_variable):
    """遍历 feature_freeze 字典，对每个特征应用对应模式"""
    for feature_name, mode in feature_freeze.items():
        if mode == "ignore":
            continue

        try:
            gsub = font["GSUB"].table
        except KeyError:
            continue  # 该字体无 GSUB 表

        if mode == "enable":
            # 从原 lookup 提取 sub 规则
            rules = extract_sub_rules(gsub, feature_name)
            # 注入到 calt lookup
            merge_into_calt(gsub, rules)
            # 从原 feature 中清除
            remove_feature(gsub, feature_name)

        elif mode == "disable":
            # 彻底移除
            remove_feature(gsub, feature_name)
```

## 变量字体的特殊处理

变量字体**没有**独立的 TTF 实例——它是单一 .ttf 文件，渲染器根据字重参数动态实例化字形。对于变量字体：

1. **enable**：规则从 `cv01` 移入 `calt`（calt 也在变量字体中工作）
2. **disable**：彻底移除（同静态字体）
3. **ignore**：保留原样（cv01 继续作为动态特征存在）

变量字体的冻结更简单——不需要考虑"不同字重的实例有不同特征表"。

## 与 fontfreeze 的关系

Maple Mono 的 `freeze.py` 参考了 [fontfreeze](https://github.com/MuLNY/fontfreeze) 的设计思路，但做了针对性适配：

| 对比项 | Maple Mono freeze.py | fontfreeze |
|--------|---------------------|------------|
| 模式 | enable / disable / ignore | 主要 enable |
| 变量字体支持 | ✅ | ❌ |
| 与构建流水线集成 | ✅ 作为 build.py 的后处理步骤 | ❌ 独立工具 |
| CLI 覆盖 | ✅ `--feat` 参数直接触发 enable | ❌ 需写配置 |

## 使用建议

1. **只想固化几个特征**：用 `--feat cv01,ss07` 快速启用
2. **全面定制**：写完整的 `feature_freeze` 配置段，覆盖 12-20 个 cv/ss 特征
3. **构建普通版**：保持默认 feature_freeze（全 ignore），最终用户自己开 OpenType 切换
4. **构建品牌定制版**：大量 use enable，固化你想要的风格
5. **彻底简化版**：use disable 移除你不想要的所有变体，最小化字体表

## 设计洞察

1. **特征冻结是"时"操作**：在构建时（build-time）把动态规则变成静态字形关系，而不是在渲染时（render-time）让渲染器决定
2. **三模式覆盖所有场景**：ignore = 让渲染器决定、enable = 我来决定默认值、disable = 我不让你决定
3. **enable 通过 lookup 搬移实现**：不是直接复制规则，而是把 sub 规则从原 lookup 搬入 calt——避免规则重复和冲突
4. **与 OpenType Feature 系统解耦**：freeze.py 用 fontTools 低水平操作 GSUB 表，不依赖 Maple Mono 的 Python AST 生成器——理论上可以对任何字体生效
