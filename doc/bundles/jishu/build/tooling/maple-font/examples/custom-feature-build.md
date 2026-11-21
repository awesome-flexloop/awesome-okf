---
type: Example
title: "自定义特征构建"
description: "通过 --feat 参数和 config.json feature_freeze 段定制 OpenType 特征的三种模式"
tags: ["maple-mono", "feature", "freeze", "customize", "cli"]
sources:
  - id: CONFIG-JSON
    resource: "config.json#feature_freeze"
    description: "feature_freeze 配置段默认值"
  - id: BUILD-PY-FREEZE
    resource: "build.py#FontConfig._apply_feature_options"
    description: "Feature Options CLI 参数处理"
prerequisites:
  - "basic-build.md"
  - "../concepts/02-config-system.md"
  - "../concepts/03-feature-system.md"
  - "../concepts/05-freeze-mechanism.md"
status: draft
---

# 示例 2：自定义特征构建

本示例展示三种定制 OpenType 特征的方法——CLI 快速试验、config.json 版本化配置、Feature Freeze 三模式精细控制。

## 方法 1：CLI --feat 参数（最快）

想快速启用几个特征？用 `--feat`：

```bash
# 启用 cv01（@$%品牌化）、ss07（箭头变体）、zero（零斜杠）
python build.py --feat cv01,ss07,zero

# 启用 Normal 预设（12 项 JetBrains Mono 风格）
python build.py --normal
```

这等价于在 config.json 中把列出的特征置为 `enable` 模式。

## 方法 2：config.json feature_freeze 段（版本化）

想让配置可以 git 追踪和共享？编辑 config.json：

### 场景 A：我想要 cv01 品牌化字形当默认值

```json
{
  "feature_freeze": {
    "cv01": "enable",
    "ss08": "enable"
  }
}
```

效果：最终字体中 cv01 的规则被固化到 calt，所有 `@` `$` `%` 自动显示品牌化圆角版本。

### 场景 B：我不想要 zero 零斜杠

```json
{
  "feature_freeze": {
    "zero": "disable"
  }
}
```

效果：从字体表中彻底移除 zero 特征——即使渲染器尝试启用也无效。

### 场景 C：混合策略

```json
{
  "feature_freeze": {
    "cv01": "enable",
    "cv02": "ignore",
    "ss05": "enable",
    "ss08": "disable",
    "zero": "ignore"
  }
}
```

- cv01 → 固化为默认
- cv02 → 保留，渲染器可切换
- ss05 → 固化为默认
- ss08 → 彻底移除
- zero → 保留

## 方法 3：width / hinted / ligature 等全局参数

```bash
# slim 宽度 + hinted 基座 + 禁用连字
python build.py --width slim --no-hinted --no-liga

# narrow 宽度 + 启用无限箭头
python build.py --width narrow --infinite-arrow
```

### 参数速查

| CLI 参数 | config.json 字段 | 效果 |
|---------|-----------------|------|
| `--width default` | `"width": "default"` (600) | 标准等宽 |
| `--width narrow` | `"width": "narrow"` (550) | 略窄等宽 |
| `--width slim` | `"width": "slim"` (500) | 紧凑等宽 |
| `--no-hinted` | `"use_hinted": false` | 用 unhinted 基座 |
| `--no-liga` | `"enable_ligature": false` | 禁用所有 calt 连字 |
| `--infinite-arrow` | `"infinite_arrow": true` | 强制启用无限箭头 |
| `--feat cv01,ss07` | `"feature_freeze": {...}` | 启用指定特征 |
| `-n` / `--normal` | （预设，12 项） | JetBrains Mono 风格 |

## 实战：构建一份 JetBrains Mono 风格的 Maple Mono

目标：看起来像 JetBrains Mono 但字体更好看——圆角 + 更好的连字 + 草书斜体。

```bash
# 方式 1：CLI 一行搞定
python build.py --normal --width narrow --no-hinted

# 方式 2：写 config.json 版本化
```

```json
// config.json
{
  "family_name": "Maple Mono JetBrains Style",
  "use_hinted": false,
  "width": "narrow",
  "enable_ligature": true,
  "feature_freeze": {
    "cv01": "enable", "cv02": "enable", "cv33": "enable",
    "cv34": "enable", "cv35": "enable", "cv36": "enable",
    "cv61": "enable", "cv62": "enable",
    "ss05": "enable", "ss06": "enable", "ss07": "enable",
    "ss08": "enable"
  }
}
```

```bash
# 然后运行
python build.py
```

## 验证效果

构建完成后，在支持 OpenType 的编辑器中验证：

1. **vscode**：设置 `editor.fontFamily` 指向新字体
2. **查看连字**：输入 `=>` `!=` `->` `>=` 看是否正确渲染
3. **查看变体**：如果不确定 CV 是否生效，用 fontTools 检查：

```bash
python -c "
from fontTools.ttLib import TTFont
font = TTFont('fonts/Variable/MapleMono[wght]-VF.ttf')
gsub = font['GSUB'].table
print('GSUB features:', [f.FeatureTag for f in gsub.FeatureList.FeatureRecord])
"
```

如果 cv01 被 enable 固化了，GSUB 中应该**没有** cv01 feature 了（规则已移入 calt）。

## 常见问题

### CLI 和 config.json 冲突时谁优先？

CLI 参数优先级更高。`python build.py --feat cv01,ss07` 会把这两项覆盖 config.json 中的对应值。

### enable 后怎么恢复原状？

把该特征在 feature_freeze 中设为 `"ignore"`，或从 CLI --feat 参数中移除。

### disable 和 enable 有什么区别？

- `enable`：规则从 cvXX 搬到 calt，作为默认字形生效
- `disable`：规则从字体中彻底删除，该 cvXX 不再存在
