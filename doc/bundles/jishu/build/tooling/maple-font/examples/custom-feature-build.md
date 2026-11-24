---
type: Example
title: "自定义特征构建"
description: "用 --feat 冻结字形变体、用 --apply-fea-file 直接编辑特征文件，并正确再生成签入产物"
tags: ["feature-freeze", "fea", "normal", "custom-build"]
sources:
  - id: build-options
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/build-options.md
    title: Build Options
  - id: feature-readme
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/feature/README.md
    title: Maple Mono Feature Module
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# 自定义特征构建

## 场景一：冻结字形变体

目标：不依赖编辑器开启 OpenType 特性，直接得到喜欢的 `cvXX` / `ssXX`。

```sh
uv run build.py --feat zero,cv01,ss07,ss08 --format ttf
```

- `--feat` 是 `enable` 的批量写法，逗号分隔；
- 启用的单一替换会被写入每个 UFO master，静态与变量输出一致；
- 上下文规则移入 `calt`，默认渲染即可生效。

等价配置：

```json
{
  "feature_freeze": {
    "zero": "enable",
    "cv01": "enable",
    "ss07": "enable",
    "ss08": "enable"
  }
}
```

若要“彻底禁止”某个特征：

```json
{
  "feature_freeze": {
    "cv05": "disable"
  }
}
```

## 场景二：`--normal` 预设

```sh
uv run build.py --normal --format ttf
```

`--normal` 使用更接近 JetBrains Mono 的字形（例如中间带斜线的 `0`），并默认启用 12 个特征：

```
cv01 cv02 cv33 cv34 cv35 cv36 cv61 cv62 ss05 ss06 ss07 ss08
```

发布名会带 `Normal` 后缀；若同时 `--no-liga`，则为 `NormalNL`。

## 场景三：标准零号语义

```sh
uv run build.py --standard-zero
```

默认行为是“`0` 斜零、启用 `zero` 显示点零”；加上该选项后改为“默认点零、启用 `zero` 显示斜零”。

## 场景四：直接编辑 `.fea`

1. 编辑 `sources/features/regular.fea` 或 `italic.fea`；
2. 构建时加 `--apply-fea-file`：

```sh
uv run build.py --apply-fea-file --format ttf --debug
```

要点：

- 该路径读取签入文件，而不是运行 Python 生成器；
- `include` 在冻结规则之前解析；
- 仍发生在源准备阶段，因此静态与变量输出一致；
- CJK 静态字体在合并后使用 `regular_cn.fea` / `italic_cn.fea`，只冻结 CJK 专属替换。

## 场景五：修改生成器后同步产物

若改的是 `scripts/feature/` 下的 Python 规则：

```sh
uv run task.py fea
```

会刷新：

- `sources/features/regular.fea`、`italic.fea`、`cn.fea`、`regular_cn.fea`、`italic_cn.fea`
- `documentation/opentype-features.md`
- `sources/schema.json` 与 `config.json` 的 feature-freeze 段
- `scripts/in_browser.py` 的 moving-rule 列表

然后逐文件审查 diff，再构建：

```sh
uv run build.py --format ttf --debug
```

## 场景六：字符宽度与连字

```sh
uv run build.py --width narrow --no-liga --format ttf
```

- `--width`：`default`(600) / `narrow`(550) / `slim`(500)；同样作用于 Variable、NF 与 CJK；
- `--no-liga`：移除全部连字，发布名带 `NL`；
- `--remove-tag-liga`：只移除 `[TODO]` 一类纯文本标签连字；
- `--no-infinite-arrow`：关闭无限箭头。

## 场景七：Unicode 与字重微调

```json
{
  "codepoint_alias": { "U+E000": "U+E001" },
  "weight_mapping": {
    "regular": 350,
    "bold": 700
  },
  "line_height": 1.1
}
```

- `codepoint_alias` 把缺失码点映射到已有字形；
- `weight_mapping` 调整静态字体字重；
- `line_height` 的最终行高为 `(ascender - descender) * line_height`。

## 验证清单

1. `uv run build.py --dry`，确认 `feature_freeze`、`feat`、`width`、`normal` 已按预期归一化；
2. 构建后检查 `GSUB`：`disable` 的特征应消失；
3. 在编辑器中不开启任何特性，输入目标字符，确认 `enable` 生效；
4. 对比 Variable 与静态 TTF 的同一字符，确认形态一致；
5. 改了生成器源码时，确认构建未使用 `--cache`。

## 常见陷阱

| 陷阱 | 后果 | 正确做法 |
|------|------|----------|
| 改了 `scripts/feature/` 仍用 `--cache` | 旧阶段被误判命中 | 去掉 `--cache` |
| 只改 `.fea` 却未加 `--apply-fea-file` | 构建仍走生成器 | 加 `--apply-fea-file` |
| 手工编辑 `documentation/opentype-features.md` | 下次 `task.py fea` 被覆盖 | 改规则后重新生成 |
| 同时要求 `--nf-mono` 与 `--nf-propo` | 语义冲突 | `propo` 优先生效；显式二选一 |

## 相关文档

- 三态模式与生效时机：[特征冻结机制](../concepts/05-freeze-mechanism.md)
- AST 与编译入口：[特征 AST 生成器](../concepts/04-feature-ast-generator.md)
- 参数级 API：[特征生成 API](../references/feature-generator-api.md)
