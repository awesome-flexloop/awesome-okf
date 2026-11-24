---
okf_version: "0.2"
type: index
title: "实战示例索引"
description: "Maple Mono v8 的四个动手场景：最小构建、特征定制、Nerd Font 与 CJK 构建"
---

# 实战示例索引

四个示例按“先跑通、再定制”的顺序排列。命令默认在仓库根目录执行，并假定已安装 Python 3.10+ 与依赖。

| 场景 | 文档 | 你将得到 |
|------|------|----------|
| 最小构建与产物检查 | [基本构建](basic-build.md) | `fonts/TTF/`、`fonts/Variable/` 等基础输出 |
| 特征冻结与自定义 `.fea` | [自定义特征构建](custom-feature-build.md) | 冻结了 `cvXX` / `ssXX` 的字体，或文件式特征构建 |
| Nerd Font 三种间距变体 | [Nerd Font 构建](nerd-font-build.md) | `fonts/NF/`、`NFMono/`、`NFPropo/` 或变量 NF |
| 四语种 CJK 合并 | [CJK 构建](cjk-build.md) | `fonts/<LOCALE>/`、`NF-<LOCALE>/` 等 |

## 通用准备

```sh
git clone https://github.com/subframe7536/maple-font --depth 1 -b variable
cd maple-font
uv sync
```

若不使用 `uv`，可 `pip install -r requirements.txt` 后以 `python build.py` 运行。Debian/Ubuntu 可能还需要 `python-is-python3`。

## 通用验证

```sh
uv run build.py --dry          # 检查解析后的配置与运行期上下文
uv run ruff format --check .
uv run ruff check .
uv run pyrefly check
uv run python -m unittest discover -s scripts/tests
```

`--dry` 是排查“为什么没生成某个目录”的第一手段：它不创建 `BuildPlan`，只打印归一化后的输入。

```{toctree}
:hidden:
:maxdepth: 7

basic-build
custom-feature-build
nerd-font-build
cjk-build
```
