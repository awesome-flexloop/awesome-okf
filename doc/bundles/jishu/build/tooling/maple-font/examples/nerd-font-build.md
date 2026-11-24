---
type: Example
title: "Nerd Font 构建"
description: "构建默认、Mono、Propo 与变量形式的 Nerd Font，并判断何时需要 font-patcher 回退"
tags: ["nerd-font", "nf", "nfm", "nfp", "font-patcher"]
sources:
  - id: build-options-nf
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/build-options.md
    title: Custom Nerd Font Configuration
  - id: choose-nf
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/choose.md
    title: Terminal Icon Variants
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# Nerd Font 构建

## 目标

生成带图标的字体，并根据终端/编辑器选择图标间距。

## 1. 默认 NF

```sh
uv run build.py --format ttf
```

`nerd_font.enable` 默认是 `true`，因此即使不写 `--nf` 也会产出：

```
fonts/NF/
├── MapleMono-NF-Regular.ttf
├── MapleMono-NF-Bold.ttf
└── ...
```

默认 NF 的每个图标占一个拉丁字符前进宽度，但字形宽度可变。

## 2. 固定宽（Mono）

```sh
uv run build.py --nf-mono --format ttf
```

输出到 `fonts/NFMono/`，文件名标记为 `NFM`，例如 `MapleMono-NFM-Regular.ttf`。适合要求严格单元格对齐的终端。

## 3. 比例宽（Propo）

```sh
uv run build.py --nf-propo --format ttf
```

输出到 `fonts/NFPropo/`，文件名标记为 `NFP`。图标按可变宽度绘制，视觉更自然。

> `--nf-propo` 优先于 `--nf-mono`；两者同时出现时按 Propo 处理。

## 4. 变量 NF

```sh
uv run build.py --nf-variable --format ttf
```

输出到 `fonts/Variable-NF/`（Mono/Propo 对应 `Variable-NFMono/`、`Variable-NFPropo/`）。变量 NF 不参与静态 hinting 选择。

## 5. 跳过 NF

```sh
uv run build.py --no-nf --format ttf
```

用于只关心基础字体的场景，或排查 NF 阶段问题时。

## 6. 强制 font-patcher

默认路径使用三份签入基座，速度快。以下任一情况会回退到 FontForge 修补器：

- `nerd_font.extra_args` 非空；
- `--font-patcher`；
- `glyphs` 不等于 `["--complete"]`。

```sh
uv run build.py --font-patcher --format ttf
```

环境要求：安装 `fontforge`，可能还需要 `python3-fontforge`。默认参数为 `-l --careful --outputdir dir`，并按变体追加：

- `propo` → `--variable-width-glyphs`；
- `mono` → `--mono`。

## 7. 配置写法

```json
{
  "nerd_font": {
    "enable": true,
    "version": "3.5.0",
    "mono": false,
    "propo": false,
    "variable": false,
    "use_font_patcher": false,
    "glyphs": ["--complete"],
    "extra_args": []
  }
}
```

`version` 必须与所用修补器版本一致；`task.py nf` 会检查并同步。

## 8. 维护基座

```sh
uv run build.py --format ttf     # 先有基础 TTF
uv run task.py nf                # 检查上游、更新 config、下载修补器、重写三份基座
uv run task.py nf --no-update    # 版本已正确，仅重建本地输出
```

`task.py nf` 会写入：

```
sources/MapleMono-NF-Base.ttf
sources/MapleMono-NF-Base-Mono.ttf
sources/MapleMono-NF-Base-Propo.ttf
```

它们与 `config.json` 一起提交。

## 9. Hinting 选择

静态 NF 的基座由 `use_hinted` 决定：

| 设置 | 基座 |
|------|------|
| `--hinted`（默认） | `fonts/TTF-AutoHint/` |
| `--no-hinted` | `fonts/TTF/` |

低分辨率屏幕建议 hinted；高分辨率屏幕可对比 unhinted 版本的笔画与对齐。

## 10. 验证

```sh
ls fonts/NF fonts/NFMono fonts/NFPropo
```

- 目录名与文件名标记是否匹配（`NF` / `NFM` / `NFP`）；
- 在终端输入常见图标（如 Git、文件夹、语言标志）确认渲染；
- 若图标宽度异常，检查是否误用了 Mono/Propo 变体；
- 若构建时间异常长，确认是否因 `extra_args` 触发了 font-patcher。

## 11. NF + CJK

CJK 与 NF 的组合由 `cjk.with_nerd_font` 控制，输出到 `fonts/NF-<LOCALE>/`。详见 [CJK 构建](cjk-build.md)。

## 相关文档

- 三变体的命名与路径：[Nerd Font 补丁](../concepts/06-nerd-font-patching.md)
- NF 与 CJK 的组合规则：[CJK 字体合并](../concepts/07-cjk-font-merge.md)
