---
type: Reference
title: 了凡生意经（智然解读）Bundle 信源登记
description: 智然《了凡生意经》五讲解读的全部权威信源登记，含喜马拉雅课程实录、书籍出版物、在线文章，每条含可核查 resource。
tags: [liaofan, 了凡生意经, 智然, 信源, 解读]
generated: { by: "agent:seven-concepts-cmd", at: "2026-09-08T15:00:00+08:00" }
status: stable
stale_after: 2027-09-08
okf_version: "0.2"
---

# 了凡生意经（智然解读）Bundle 信源登记

本目录登记本 bundle 依循的全部权威信源。每条信源含可核查 `resource`（URL / 出版社·年份 / 集数范围），供正文脚注溯源。

> ⚠️ 本 bundle 为阐释层内容，所有信源均为公开课程实录或出版物，无任何内部或未公开信息。

## 信源分类总览

| 文档                   | 内容                     | 对应层级  |
| -------------------- | ---------------------- | ----- |
| [权威信源清单](sources.md) | 喜马拉雅课程实录、出版物、在线文章、学术引用 | 阐释层信源 |

## 统一信源 ID 清单

### 音频课程实录（主信源）

| 信源 ID                       | 信源                                                              | 类型           | 集数范围 |
| --------------------------- | --------------------------------------------------------------- | ------------ | ---- |
| `source-ximalaya-82159945`  | 智然《了凡生意经（完结篇）》，喜马拉雅专辑，<https://www.ximalaya.com/album/82159945> | 音频课程实录（主信源）  | 105集 |
| `source-ximalaya-105855596` | 智然《了凡生意经》，喜马拉雅专辑，<https://www.ximalaya.com/album/105855596>     | 音频课程实录（辅助核对） | 83集  |
| `source-ximalaya-33860583`  | 智然《了凡生意经》，喜马拉雅专辑，<https://www.ximalaya.com/album/33860583>      | 音频课程实录（交叉验证） | 94集  |

### 出版物信源

| 信源 ID                     | 信源                                                                  | 类型   |
| ------------------------- | ------------------------------------------------------------------- | ---- |
| `source-shuge-shengyi`    | 智然《了凡生意经》，中华书局整理本（含课堂实录文字稿）                                         | 出版物  |
| `source-dangdang-shengyi` | 智然《了凡生意经》，当当网书籍介绍页（目录结构确认）                                          | 辅助确认 |
| `source-toutiao-shengyi`  | 今日头条《智然老师《了凡生意经》》，<http://m.toutiao.com/group/7583711457557119507/> | 在线文章 |

### 关联信源（原文层）

| 信源 ID                  | 信源                                                               | 用途              |
| ---------------------- | ---------------------------------------------------------------- | --------------- |
| `source-cfolu-liaofan` | 佛弟子文汇·了凡四训全文，<http://www.cfolu.com/xiuxueyd/027lfsx-baihua.html> | 《了凡四训》原文底本（古典层） |
| `source-shuge-liaofan` | 中华书库《了凡四训》，<https://www.shuge.org/view/liao_fan_si_xun/>         | 《了凡四训》双源核对（古典层） |

### 跨 bundle 关联

| 关联 bundle                           | 关联内容                      |
| ----------------------------------- | ------------------------- |
| `guoxue/liaofan/yuan-liaofan-sijun` | 《了凡四训》四篇原文（古典层底本）         |
| `guoxue/yangming/chuanxilu`         | 明代理学语境（王阳明心学与了凡改命思想的共时背景） |
| `guoxue/confucian/four-books`       | 儒家修身传统与改过积善的义理根基          |

## 使用说明

- 本 bundle 所有内容标注 **"智然老师阐释"**，不伪装为古文原意
- 每个观点条目末尾须标明对应的《了凡四训》原文出处（篇名+段落）
- 原文引用以 `source-cfolu-liaofan` 为基准，`source-shuge-liaofan` 为双源核对
- 各概念文档通过 frontmatter 的 `sources` 字段引用本目录信源 ID

```{toctree}
:hidden:
:maxdepth: 7

sources
```

