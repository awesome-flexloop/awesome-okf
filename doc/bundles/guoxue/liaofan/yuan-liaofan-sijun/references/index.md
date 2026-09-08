---
type: Reference
title: 《了凡四训》原文 Bundle 信源登记
description: 立命篇、修养篇、改过篇、积善篇、感应篇、益学篇六篇原文的权威信源登记，含古籍底本与在线数字化双源、现代学者校注与跨知识包交叉引用。
tags: [liaofan, 了凡四训, 袁黄, 云谷禅师, 原文, 信源]
generated: { by: "agent:general_purpose_task", at: "2026-09-08T14:40:00+08:00" }
status: stable
stale_after: 2027-09-08
okf_version: "0.2"
---

# 《了凡四训》原文 Bundle 信源登记

本目录登记本 bundle 依循的全部权威信源。每条信源含可核查 resource（出版社·年份·ISBN / 机构 URL），供正文脚注溯源。

## 信源分类总览

| 文档 | 内容 | 对应层级 |
|------|------|---------|
| [权威原文信源清单](sources.md) | 古籍底本（万历刻本/宝诰录/功过格丛编）、现代点校本（中华书局/上海古籍）、数字化来源（ctext.org/维基文库/古诗文网） | 一级文献 + 数字化源 |

## 统一信源 ID 清单

### 古籍原刻本

| 信源 ID | 信源 | 类型 |
|---------|------|------|
| `source-cfolu-liaofan` | 了凡先生《了凡四训》（明·袁黄著），万历二十八年（1600）刻本，收入《宝诰录》 | 明刻原典 |
| `source-baogao-liao` | 《了凡四训》收入《道藏精华》或《太上感应篇汇编》《功过格》丛编本（多种版本） | 明清丛编 |

### 现代点校本

| 信源 ID | 信源 | 类型 |
|---------|------|------|
| `source-shuge-liaofan` | 袁黄《了凡四训》，上海古籍出版社整理本（含白话译文与注释） | 现代点校本 |
| `source-zhonghua-liaofan` | 袁黄《了凡四训》，中华书局整理本（含校勘记） | 现代点校本 |

### 数字化在线信源

| 信源 ID | 信源 | 类型 |
|---------|------|------|
| `source-ctext-liaofan` | ctext.org《了凡四训》，https://ctext.org/liao-fan-si-xun | 电子文本（核对用） |
| `source-wikisource-liaofan` | 维基文库《了凡四训》，https://zh.wikisource.org/wiki/了凡四训 | 电子文本（核对用） |
| `source-gushiwen-liaofan` | 古诗文网《了凡四训》全文，https://www.gushiwen.cn | 电子文本（核对用） |

### 音频与讲座信源

| 信源 ID | 信源 | 类型 |
|---------|------|------|
| `source-ximalaya-82159945` | 喜马拉雅《了凡四训》解读系列，https://www.ximalaya.com/album/82159945 | 音频讲读（辅助参考） |

### 跨 bundle 关联

| 关联 bundle | 关联内容 |
|------------|---------|
| `guoxue/yangming/chuanxilu` | 明代理学语境（王阳明心学与了凡改命思想的共时背景） |
| `guoxue/confucian/four-books` | 儒家修身传统与改过积善的义理根基 |
| `yixue/yangsheng/yangsheng-classics-reading` | 养生与积善的古典养生观交叉 |

## 使用说明

- 原文引用以 `source-baogao-liaofan` 或 `source-shuge-liaofan` 为文字基准，`source-ctext-liaofan` 与 `source-wikisource-liaofan` 为双源逐字核对。
- 电子版与底本偶有出入处从底本并在正文加注异文。
- `source-ximalaya-82159945` 等音频信源仅作讲读参考，不作为原文定本依据。
- 各概念文档通过 frontmatter 的 `sources` 字段引用本目录信源 ID。

```{toctree}
:hidden:
:maxdepth: 7

sources
```
