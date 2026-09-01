---
type: reference
id: hf-digital-sources
title: 数字信源
description: 本包全部数字信源登记——ctext.org 主信源、moocky.net 第二信源、古诗文网《史记》信源、百度百科背景信源，及 zh.wikisource.org 不可达记录与检索路径。
bundle: ../index.md
facts: [F-HF-003, F-HF-004, F-HF-005, F-HF-035]
sources:
  - https://ctext.org/hanfeizi/zhs
  - https://moocky.net/b/hanfeizi
  - https://m.gushiwen.cn/guwen/bookv_66bf9111c262.aspx
created: 2026-08-30
status: stable
---

# 数字信源

## 一、信源清单

| 信源 | 角色 | 底本 | 覆盖范围 |
|---|---|---|---|
| ctext.org | 主信源 | 《四部丛刊初编》本（F-HF-003） | 全书；本包逐篇页核对《定法》《二柄》《有度》《五蠹》《难势》《显学》《六反》《孤愤》《说难》 |
| moocky.net | 第二信源 | 据《四部丛刊》本整理（F-HF-005） | 全文；《五蠹》《孤愤》《说难》《有度》《定法》《显学》整篇提取 |
| 古诗文网（m.gushiwen.cn） | 史源信源 | 《史记·老子韩非列传》 | 传记事实（F-HF-031 至 F-HF-035）与《说难》史源对校 |
| 百度百科（m.baike.com） | 背景信源 | — | 篇数、书名沿革等背景事实（F-HF-001、F-HF-002） |

## 二、信源状态记录

- **zh.wikisource.org 不可达**：2026-08-30 多次访问超时（总目、篇目页、移动版均超时），未能作为第三核对源；本包双源核对以 ctext.org + moocky.net 完成（F-HF-005）。
- **ctext.org URN 体系**：篇页含 URN 标识（如《二柄》为 `ctp:hanfeizi/er-bing`，F-HF-004），可用于程序化引用定位。
- **《史记》引文与今本异文**：《说难》"所说实为厚利"（《史记》）与"所说阴为厚利"（今传本）之异（F-HF-035），是史源对校的直接产物——引用《说难》时须注明所据。

## 三、检索路径

- 原文核对：ctext.org 篇页路径格式 `https://ctext.org/hanfeizi/<篇名拼音>/zhs`；英文对照加 `?en=on`。
- 全文对照：moocky.net/b/hanfeizi 单页全文，宜配合 ctext 逐篇页交叉定位。
- 传记核对：古诗文网《史记》卷六十三《老子韩非列传》。

## 四、引用规范

1. 引用任何原文，标注事实编号（F-HF-XXX）回溯信源 URL 复核。
2. 两源文字一致处，标注"ctext 与 moocky 文字一致"；有出入处标注异文事实编号，不作隐性裁断。
3. moocky 录文存在形误层（F-HF-046、F-HF-049、F-HF-050 等），引用其独有段落时宜与 ctext 抽查核对。

## 关联

- [校本系统](collation-traditions.md)（传本线索与异文处理原则）
- [解读文献](interpretations.md)（现代学术研究信源）

返回 [知识包首页](../index.md)。