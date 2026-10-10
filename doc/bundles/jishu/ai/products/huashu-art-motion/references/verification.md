---
okf_version: "0.2"
type: Reference
title: "huashu-art-motion 推介文 P0 权威核验报告"
description: "对微信推介文关键声明的 GitHub 一手信源交叉核验：15 项 P0/P1，其中 Star 数(1.3K vs 41)与解说语法数(8 vs 9)为必读勘误"
tags: [huashu-art-motion, verification, p0-check, fact-check, errata]
generated:
  by: "wechat-public-okf:R/V"
  at: "2026-10-10T12:35:00+08:00"
status: stable
stale_after: 2027-01-31
sources:
  - id: wechat
    url: https://mp.weixin.qq.com/s/BbsIpq82oAq7RPusw_jHXA
  - id: github-repo
    url: https://github.com/alchaincyf/huashu-art-motion
  - id: github-readme
    url: https://raw.githubusercontent.com/alchaincyf/huashu-art-motion/main/README.md
---

# P0 权威核验报告

> 核验时间：2026-10-10。信源：GitHub 仓库页（作者/许可/Star/语言/仓库树动态快照）+ 官方 README.md（main 分支一手文档，含"里面有什么""能做什么""背后的故事""致谢"四段）。
> 推介文信源距离：第三方开源推介号（开源星探）转述作者（花叔）项目，属**次级转述**；本文档以官方 README 为更高可信度一手信源逐项交叉。

## 核验总览

| 级别 | 数量 | 结论分布 |
|------|------|---------|
| P0（数字/日期/命令/许可/成效） | 11 | ✅ 8 / ⚠️ 1 / ❌ 2 |
| P1（能力声明/结构/兼容） | 4 | ✅ 4 |
| 合计 | 15 | **✅ 12 / ⚠️ 1 / ❌ 2** |

**总体评估**：核心身份/命令/数字（35 风格卡、仓库路径、安装命令、试渲命令）均与一手信源逐字一致，项目真实存在、MIT 许可、作者为花叔（alchaincyf）。但两处须在正文强制勘误：

1. **❌ F-007 Star 数失实**：文章标题「开源一天就收获 1.3K Star」与 GitHub 实测 **41 stars**（2026-10-10 采集，仓库 2026-10-06 首评）严重不符。41 是实测值，1.3K 无法核实，按 `single-source/flagged` 处理，正文一律不沿用标题夸大口径，仅陈述可验证的 41 stars 时点值。
2. **❌ F-013 语法数不一致**：文章衔接处写「8 种解说语法」，官方 README 明确 **9 种**（8 种附示范片 + 第9种讲解员式财经科普）。文章核心亮点段第 89 行实际也写「9 种解说动画语法」，属**文章内部自相矛盾**；正文以官方 9 种为准。

## 勘误清单

### ① 日期/版本表

| 推介文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| 「开源一天就收获 1.3K Star」（F-007） | GitHub 实测 **41 stars**、0 watching、6 forks（2026-10-10），首发 commit 445c0752 Oct 6, 2026 | ❌ **严重失实/无法核实**；正文用 41 时点值并标注"文章标题夸大为 1.3K" |
| 「万星项目创作者」（F-005/F-046） | 指 huashu-design（另一项目）的 Star 量级，本仓库页无法核证 | ⚠️ 无法独立证实；正文去掉"万星"硬断言，改为"曾打造 huashu-design" |

### ② 成效/能力数字溯源表

| 推介文声明（F） | 官方核验 | 结论 |
|--------------|---------|------|
| 35 种艺术风格配方卡（F-008） | README「35张，references/风格配方/」+「35个场景代码 scripts/engine/scenes/」 | ✅ 一致 |
| 9 种解说语法 / 8 种参数化片段 | README「9种解说语法 · 8种参数化片段」；9 种中 8 种附示范片，第 9 种讲解员式为代码快照 | ✅ 以官方 9 为准；文章衔接处"8 种"为笔误 |
| 8 种参数化片段 + 长卷骨架（F-021） | README「8种参数化片段」+「长卷穿越片示范（骨架＋3段＋角色帧库）」 | ✅ 一致 |
| 23 种画风、2 分 08 秒（F-024） | README「从洞穴一路走到 2026……23种画风、2分08秒」 | ✅ 一致 |
| 派 4 组 agent 做 20 种新风格（F-012） | README「派了 4 组只读 skill 的 agent 去做它没见过的 20 种风格」 | ✅ 一致 |

### ③ 命令/结构逐字核对表

| 推介文引用（F） | 官方原文核对 | 结论 |
|--------------|-------------|------|
| `npx skills add alchaincyf/huashu-art-motion`（F-034） | README 首栏代码块逐字一致 | ✅ |
| `uv run --with playwright python scripts/engine/render.py --solo 09_postimp --stills 0.3 --out 试渲`（F-036） | README 试一下示例逐字一致 | ✅ |
| `breakdown.py` / `qa.py`（F-028/F-029） | 仓库树 scripts/analyze/breakdown.py、scripts/qa.py 确认存在 | ✅ |
| 三依赖 uv/ffmpeg/Playwright Chromium（F-033） | 官方「依赖：uv、ffmpeg、Playwright Chromium」 | ✅ |
| skills CLI ≤1.5.15 只同步 SKILL.md 单文件（F-035） | 仓库确含 references/assets/scripts 多子目录；但"skills CLI 版本阈值 1.5.15"与"99 处引用"为**文章口径，官方 README 未列** | ⚠️ 目录结构✅；版本阈值/99处无法独立核证，正文标注文章口径 |
| `demos/` 顶层目录（F-035） | 官方仓库树显示 demos 在 `scripts/engine/demos/` 内，README 文件列表顶层为 references/assets/scripts 三目录 | ⚠️ 文章"references/assets/scripts/demos 四子目录"的 `demos/` 位置口径有偏差 |

### ④ 版权边界逐字核对表

| 声明 | 官方核对 | 结论 |
|------|---------|------|
| 画面不全是纯 Canvas，人物交生图模型（F-031） | README「画面里要有人→人交给生图模型出帧，代码负责合成、换帧和材质」 | ✅ |
| 不含原片帧/截图/音频（F-048） | README 致谢：「仓库里不含原片的帧、截图或音频文件」；配乐脚本是原创示例乐谱 | ✅ 版权边界清晰可复用 |

## 提取给执行者/读者的边界结论

1. **不要用标题「1.3K Star」作为传播数据**——实测仅 41 stars，且该数字高度动态，任何星标引用须带时点。
2. **解说语法以 9 种为准**（Kurzgesagt/Vox/白板/3B1B/Storytime/动态文字/发布会/财经图表 + 讲解员式财经科普）。
3. **安装坑是真问题但参数需校准**：skill 确为多目录结构（非单 SKILL.md），skills CLI 旧版只同步单文件的坑真实存在；"≤1.5.15"、"99 处"等具体数值为文章口径，本文档按官方目录树描述"references/assets/scripts + scripts/engine/demos 等"。
4. **版权边界是亮点**：仓库不含原片素材、字体走 OFL、角色帧仅示范用，适合作为"开源 Skill 版权合规"的可迁移范式参考。

## 核验方法与局限

1. **方法**：WebFetch 拉取 GitHub 仓库页（Stars/许可/语言/仓库树/首发时间）+ README.md 全文逐字比对命令、数字、结构。Star 等动态数字以 2026-10-10 快照为准。
2. **局限**：① 未实际安装运行 skill，渲染命令行为层未验证；② "99 处引用""skills CLI 1.5.15"等文章特有数值未能在官方独立复现；③ huashu-design 项目 Star 量级不在本仓库可核范围；④ 35 张风格卡具体清单与 17 个库清单未逐一展开。
3. **复核安排**：stale_after=2027-01-31 前复核 Star 量级、35/9/8 数字是否随版本增长、skills CLI 安装门槛是否下降。