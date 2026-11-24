---
type: Example
title: "CJK 构建"
description: "构建简中/繁中/日/韩四种 CJK 字体，选择静态或变量输出，并理解基座下载与回退"
tags: ["cjk", "cn", "jp", "tc", "kr", "variable"]
sources:
  - id: cjk-doc
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/cjk.md
    title: CJK Build
  - id: cjk-readme
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/cjk/README.md
    title: Maple Mono CJK Subsystem
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# CJK 构建

## 目标

在拉丁字体基础上合并中日韩字形，得到可安装的 CJK 字体。CJK 默认不构建，必须显式选择语种。

## 1. 单语种

```sh
uv run build.py --cjk cn --format ttf
```

输出：

```
fonts/CN/
├── MapleMono-CN-Regular.ttf
├── MapleMono-CN-Bold.ttf
└── ...
fonts/NF-CN/            # 默认同时生成 NF 配置档
├── MapleMono-NF-CN-Regular.ttf
└── ...
```

## 2. 多语种

```sh
uv run build.py --cjk cn,jp --format ttf
# 或重复传参
uv run build.py --cjk cn --cjk jp --format ttf
```

四语种可用值：`cn`、`jp`、`tc`、`kr`。

## 3. 变量输出

```sh
uv run build.py --cjk cn --cjk-variable
```

输出到 `fonts/Variable-CN/`（NF 为 `fonts/Variable-NF-CN/`），每个配置档只有 regular 与 italic 两个 `[wght]` 文件。

## 4. 只输出普通档

默认在 NF 可用时产出 NF-CJK。若只要普通档：

```json
{
  "cjk": {
    "with_nerd_font": false,
    "locales": { "cn": true }
  }
}
```

或在已有 NF 的情况下同时产出两者：

```sh
uv run build.py --cjk cn --cjk-both
```

## 5. 窄间距与缩放

```sh
uv run build.py --cjk cn --cjk-narrow
uv run build.py --cjk cn --cjk-scale-factor 1.1
uv run build.py --cjk cn --cjk-scale-factor 1.2,1.1
```

- `--cjk-narrow`：只收窄 CJK 字形间距，拉丁宽度不变；可能使字体不再被识别为严格等宽；
- `--cjk-scale-factor`：`<factor>` 或 `<width_factor>,<height_factor>`。

若拉丁字符也偏宽，应改用 `--width narrow|slim`。

## 6. Hinting

```sh
uv run build.py --cjk cn --cjk-hinted
```

两层控制相互独立：

- `--hinted` / `--no-hinted`：选择合并前的拉丁与 NF 静态基座；
- `--cjk-hinted` / `--no-cjk-hinted`：对最终合并的静态 CJK 字体再跑 AutoHint（默认关闭）。

## 7. 基座从哪来

首次构建会按以下顺序解析：

1. 有效本地静态目录（`sources/cjk/<locale>/static/`）；
2. 本地静态归档 `<locale>-base-static.zip`；
3. 远程静态归档（`cjk-base` 发布）；
4. 本地变量基座并实例化；
5. 本地变量归档；
6. 远程变量归档；
7. 从原始源重建。

下载失败时，设置 `github_mirror` 或环境变量 `$GITHUB`，也可以把目标 `.zip` 放到 `build.py` 同级目录。

## 8. 单独维护基座

```sh
uv run task.py cjk --help
uv run task.py cjk --preset cn
uv run task.py cjk --preset cn --vf-only
```

`task.py cjk` 总是重建 regular/italic 变量基座，并写出：

```
sources/cjk/cn/MapleMono-CN-VF.ttf
sources/cjk/cn/MapleMono-CN-Italic-VF.ttf
sources/cjk/cn/variable-cn.sha256
sources/cjk/cn/cn-base-variable.zip
sources/cjk/cn/static/...
sources/cjk/cn/static-cn.sha256
sources/cjk/cn/cn-base-static.zip
```

这些是生成物，不要手工编辑；`static-<locale>.sha256` 与 `variable-<locale>.sha256` 由任务更新并随配置提交。

## 9. 自定义 CJK 源

预设配置的公开字段为 `locale_name`、`freeze_feature`、`source`、`unicode`、`transform`：

```json
{
  "$schema": "./cjk_schema.json",
  "locale_name": "HK",
  "freeze_feature": "cv99",
  "source": {
    "path": "MyCJK-VF.ttf",
    "masters": {
      "100": { "wght": 250 },
      "400": { "wght": 470 },
      "800": { "wght": 900 }
    }
  }
}
```

约束：

- `source.path` 必须是带 `fvar` 的变量字体；
- 只能有一种轮廓格式（`glyf` 或 `CFF2`）；
- CFF2 会先转换为兼容 `glyf` master；
- `freeze_feature` 只能选 `cvXX` / `ssXX` / `zero`。

## 10. 旧 CN 选项迁移

| 旧写法 | 新写法 |
|--------|--------|
| `--cn` | `--cjk cn` |
| `--no-cn` | 从已选 locale 移除 `cn` |
| `--cn-narrow` | `--cjk-narrow`（目标 `cn`） |
| `--cn-scale-factor` | `--cjk-scale-factor`（目标 `cn`） |
| `--cn-both` | `--cjk-both` |

旧写法仍可运行，但会按新语义归一化。

## 11. 验证

1. `uv run build.py --dry`，确认 `cjk.locales` 与输出模式；
2. 检查 `fonts/<LOCALE>/` 与 `fonts/NF-<LOCALE>/` 是否同时存在；
3. 在编辑器中混排中英日韩文本与 Markdown 表格，确认 2:1 对齐；
4. 若 CJK 过宽，先试 `--cjk-narrow`，再考虑 `--width`；
5. 静态字体默认未 hint，需要时显式 `--cjk-hinted`。

## 12. 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| 没有 CJK 目录 | 未选择 locale | 加 `--cjk cn` 或改 `cjk.locales` |
| 只有 `NF-CN/` | 默认 NF 档 | 需要普通档时加 `--cjk-both` 或关闭 `with_nerd_font` |
| 下载卡住/失败 | GitHub 不可达 | 配置镜像或本地放置 zip |
| 改了基座但输出没变 | 命中了本地静态目录 | 用 `clean_cache` 或清理 `sources/cjk/<locale>/static/` |
| CJK 间距过宽 | 2:1 设计的默认取舍 | 用 `--cjk-narrow` |

## 相关文档

- 四语种来源与七级回退：[CJK 字体合并](../concepts/07-cjk-font-merge.md)
- 缓存与并行：[并行构建与缓存](../concepts/08-parallel-build.md)
- 图标组合：[Nerd Font 构建](nerd-font-build.md)
