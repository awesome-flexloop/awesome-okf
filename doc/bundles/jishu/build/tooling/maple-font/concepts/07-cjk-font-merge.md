---
type: Concept
title: "CJK 字体合并"
description: "四语种 CJK 预设、独立基座缓存、七级回退顺序、静态/变量输出与 NF 配置档的组合规则"
tags: ["cjk", "font-merge", "variable-font", "chinese", "japanese", "korean"]
sources:
  - id: cjk-readme
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/cjk/README.md
    title: Maple Mono CJK Subsystem
  - id: cjk-doc
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/cjk.md
    title: CJK Build
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# CJK 字体合并

## 1. 与 v7 的差异

v7 的 CJK 支持以简体中文为主，使用 `--cn*` 选项，合并逻辑位于主构建脚本内。v8 把 CJK 拆成独立子系统：

- 支持简体中文（CN）、繁体中文（TC）、日文（JP）、韩文（KR）四语种；
- 每种语言有独立预设、配置、变量基座、静态实例与摘要文件；
- CJK 基座缓存位于 `sources/cjk/`，与主流水线缓存 `fonts/build-cache.json` 完全独立；
- 旧 `--cn*` 选项保留为弃用别名。

## 2. 四语种来源

| 语种 | 覆盖范围 | 源字体 | 轮廓格式 | 输出后缀 |
|------|----------|--------|----------|----------|
| CN | 简中，并含常用繁中与日文假名 | WenYuan Rounded SC | `glyf` | `CN` |
| TC | 繁中，不含日文假名 | Chiron Go Round TC | `glyf` | `TC` |
| JP | 日文 CP932 覆盖 | Resource Han Rounded JP | `CFF2` | `JP` |
| KR | 韩文谚文，源字体过滤韩文区段 | Chiron Go Round TC | `glyf` | `KR` |

CJK 字形与拉丁字符采用 **2:1 宽度比**，用于保证多语言文本与 Markdown 表格对齐。代价是默认 CJK 间距比常见中文字体更宽；若只嫌 CJK 太宽而拉丁正常，使用 `cjk.narrow` / `--cjk-narrow`。

## 3. 两条独立工作流

| 工作流 | 命令 | 产出与缓存 |
|--------|------|------------|
| 构建可复用基座 | `uv run task.py cjk --preset cn` | `sources/cjk/<locale>/` 下的变量基座、变量摘要/归档、可选静态实例、静态摘要与归档；总是重建 regular/italic 变量基座 |
| 构建发布字体 | `uv run build.py --cjk cn` | `fonts/<LOCALE>/`、`fonts/NF-<LOCALE>/`、`fonts/Variable-<LOCALE>/`、`fonts/Variable-NF-<LOCALE>/` 等 |

两者缓存互不影响：`build.py --cache` 管 `fonts/`；`cjk.clean_cache` 管 CJK 变量/源回退工作，但**不删除文件**，也不会绕过有效的静态目录摘要。

## 4. 输出模式

| 模式 | 每个配置档 | 目录 |
|------|------------|------|
| `static`（默认） | 最多 16 个 TTF：8 字重 × regular/italic；`--debug` / `--least-styles` 可缩减 | 普通：`fonts/<LOCALE>/`；NF：`fonts/NF-<LOCALE>/` 等 |
| `variable` | 2 个 TTF：regular 与 italic 的 `[wght]` 变量字体 | 普通：`fonts/Variable-<LOCALE>/`；NF：`fonts/Variable-NF-<LOCALE>/` 等 |

`task.py cjk` 还会写出两个预处理变量基座、`<locale>-base-variable.zip`、`variable-<locale>.sha256`，以及（除非 `--vf-only`）最多 16 个静态实例。

## 5. 普通档与 NF 档

- `nerd_font.enable` 控制主流水线是否构建 NF 基座；
- `cjk.with_nerd_font` 控制每个 CJK 条目是否有资格进入 NF 配置档；
- 两者都为真时，默认选择 NF-CJK；
- `--cjk-both` 在 NF-CJK 之外再产出普通档；NF 被禁用时只能产出普通档。

该规则对每个语种、每种输出模式独立应用。`--nf-mono` / `--nf-propo` 会改用 `NFMono-*` / `NFPropo-*` 目录；发布任务只发布默认 NF 语言包，Mono/Propo 的 CJK 与变量输出属于本地自定义构建。

## 6. Hinting 的两层控制

| 设置 | 作用域 | 效果 |
|------|--------|------|
| `use_hinted` / `--hinted` / `--no-hinted` | 全局 | 选择静态 CJK 合并前的拉丁与 NF 静态基座 |
| `cjk.use_hinted` / `--cjk-hinted` / `--no-cjk-hinted` | CJK | 对最终合并的普通/NF 静态 CJK 字体再跑一次 AutoHint |

两者相互独立；变量 CJK 输出不参与任何一个静态 AutoHint 步骤。最终静态 CJK 默认不自动 hint。

## 7. 七级回退顺序

主流水线做静态合并时，按以下顺序取基座：

1. **有效本地静态目录**：目录与 `static-<locale>.sha256` 有效即复用；即使 `clean_cache` 为真也优先走这条；
2. **有效本地静态归档**：目录不可用时，校验并解压 `<locale>-base-static.zip`；
3. **远程静态归档**：本地归档无效且该语种有发布归档时，下载并校验；无效归档会保留并继续回退；
4. **本地变量基座**：regular/italic 都存在且 `clean_cache` 为假时，本地实例化为所需静态样式；
5. **有效本地变量归档**：变量文件不可用时，校验并安装 `<locale>-base-variable.zip`；
6. **远程变量归档**：下载 `cjk-base` 归档，校验两个成员、`fvar`、ZIP 完整性与提交的哈希，再实例化；
7. **源重建**：以上都不可用时，按配置下载源并 `vf_only=True` 重建变量基座，再实例化静态样式。

无效的静态目录不会被静默删除；所有可用来源都失败后抛出 `CJKBaseUnavailable`。变量模式发布输出使用同样的“本地文件 → 本地归档 → 远程归档 → 源重建”规则，但不要求静态目录。

## 8. 配置面与构建阶段

CJK 预设的公开 JSON 面很小：`locale_name`、`freeze_feature`、`source`、`unicode`、`transform`。输出布局、命名、特征字体、临时路径与轮廓模式由构建器派生或固定。

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

`source.path` 必须指向带 `fvar`、且只有一种轮廓格式（`glyf` 或 `CFF2`）的变量字体。可选配置控制下载、丢弃表、Unicode 区段与编码过滤、特征码点排除、宽度/缩放/平移/斜体变换。CLI 值覆盖已加载配置。

构建阶段依次为：源解析 → Unicode 子集化 → 100/400/800 master 准备 → 轮廓归一化 → 变量基座生成 → 可选静态实例化 → 主流水线合并。CFF2 源会先转换为兼容的 `glyf` master。

## 9. 生成的目录

以 `locale_name: "CN"` 为例：

| 路径 | 含义 |
|------|------|
| `sources/cjk/cn/config-cn.json` | 内置源配置 |
| `sources/cjk/cn/MapleMono-CN-VF.ttf` | 常规变量基座 |
| `sources/cjk/cn/MapleMono-CN-Italic-VF.ttf` | 斜体变量基座 |
| `sources/cjk/cn/variable-cn.sha256` | 两个变量基座的摘要 |
| `sources/cjk/cn/cn-base-variable.zip` | 变量基座归档 |
| `sources/cjk/cn/static/MapleMonoCN-<Style>.ttf` | 静态基座实例 |
| `sources/cjk/cn/static-cn.sha256` | 静态目录内容摘要 |
| `sources/cjk/cn/cn-base-static.zip` | 静态基座归档 |
| `sources/cjk/variable-source/` | 缓存的源文件、Maple 特征与元数据输入 |

这些都是生成物：修改 JSON 配置或生成器后重建，不要手工修补字体或归档。

## 10. 弃用的 CN 选项

| 旧选项 | 新写法 |
|--------|--------|
| `--cn` | `--cjk cn` |
| `--no-cn` | 从已选 locale 中移除 `cn` |
| `--cn-narrow` | 目标为 `cn` 时的 `--cjk-narrow` |
| `--cn-scale-factor` | 目标为 `cn` 时的 `--cjk-scale-factor` |
| `--cn-both` | `--cjk-both` |

## 11. 相关文档

- 字体命名与选择：[Nerd Font 补丁](06-nerd-font-patching.md)
- 阶段缓存：[并行构建与缓存](08-parallel-build.md)
- 动手构建：[CJK 构建示例](../examples/cjk-build.md)
