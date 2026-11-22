---
type: Example
title: "基本构建"
description: "从零跑通 Maple Mono v8 的最小构建，并用 --dry 与目录清单验证产物"
tags: ["build", "quickstart", "ttf", "variable"]
sources:
  - id: build-doc
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/build.md
    title: Custom Build
  - id: cli-doc
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/cli.md
    title: build.py CLI
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# 基本构建

## 目标

用最少参数完成一次构建，并确认每个输出目录的来源。

## 1. 准备

```sh
git clone https://github.com/subframe7536/maple-font --depth 1 -b variable
cd maple-font
uv sync
```

## 2. 先看解析结果

```sh
uv run build.py --dry
```

本地终端会打印两段带标签的 JSON：

- `resolved_config`：归一化后的用户意图；
- `runtime_context`：输出路径、镜像、FontForge 路径、垂直度量等。

在 CI 中只打印 `resolved_config`，便于脚本直接解析。`--dry` 不会创建 `BuildPlan`，也不会生成任何字体。

## 3. 最小构建

```sh
uv run build.py --format ttf
```

要点：

- **Variable 始终构建**，不受 `--format` 影响；
- `--format ttf` 只请求静态 TTF；
- 未请求 OTF/WOFF2 时不会产出对应目录；
- 默认仍会构建 Nerd Font（`nerd_font.enable=true`）。

产物：

```
fonts/
├── Variable/          # MapleMono[wght].ttf / MapleMono-Italic[wght].ttf
├── TTF/               # 各字重静态 TTF
├── TTF-AutoHint/      # 自动 hint 版本（NF/默认 hinted 消费）
├── NF/                # 默认 Nerd Font 静态输出
├── build-config.json  # 本次解析配置
└── build-cache.json   # 仅完整成功后写入
```

## 4. 快速迭代构建

```sh
uv run build.py --format ttf --debug
```

`--debug` 会：

- 给族名加 `Debug`；
- 打开 debug 日志；
- 只构建 Regular / Italic；
- 跳过 OTF、WOFF2 与 Nerd Font。

适合改特征或源之后做快速验证。

## 5. 完整构建

```sh
uv run build.py
```

按 `config.json` 的 `formats`（默认 `ttf,otf,woff2`）产出全部基础格式，并构建默认 NF。

## 6. 复用缓存

```sh
uv run build.py --format ttf
uv run build.py --format ttf --cache   # 第二次应命中已完成的阶段
```

`--cache` 会读取 `fonts/build-cache.json`，按阶段身份、输出清单、文件存在性与内容摘要判定命中。日志中应出现 `Cache hit`。

> 若刚改过 `scripts/`、依赖或 UFO 轮廓，先去掉 `--cache` 构建一次，详见 [并行构建与缓存](../concepts/08-parallel-build.md)。

## 7. 验证产物

```sh
ls fonts/Variable fonts/TTF
```

- `fonts/Variable/MapleMono[wght].ttf` 应带 `fvar` 表；
- `fonts/TTF/` 中应存在请求的字重；
- `fonts/build-config.json` 中的 `formats`、`width`、`feature_freeze` 应与预期一致。

安装到系统后，用字体查看器确认族名与字重列表；若族名带 `Debug`，说明使用了 `--debug`。

## 8. 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| 没有 `fonts/OTF/` | 未请求或使用了 `--debug` | 去掉 `--debug` 并确认 `formats` 含 `otf` |
| 没有 `fonts/Woff2/` | 未请求或 debug | 同上 |
| 没有 `fonts/NF/` | `--no-nf` 或 debug | 检查 `nerd_font.enable` |
| 改动没生效 | 误用了 `--cache` | 去掉缓存重建 |
| 下载失败 | GitHub 不可达 | 设置 `github_mirror` 或 `$GITHUB` |

## 9. 下一步

- 定制字形与连字：[自定义特征构建](custom-feature-build.md)
- 生成图标版本：[Nerd Font 构建](nerd-font-build.md)
- 生成中日韩版本：[CJK 构建](cjk-build.md)
