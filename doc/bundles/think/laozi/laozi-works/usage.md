---
type: Guide
title: 使用说明
description: laozi-works 知识包的使用说明：目标读者、按场景阅读路径、信源溯源方法、与其他 bundle 的分工及使用注意。
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T10:00:00+08:00" }
status: stable
stale_after: 2027-08-30
---

# 使用说明

本知识包聚焦**老子本人著作的原文与解读本体**：以出土文献为主基准提供《道德经》原文，三线并收权威解读。本文说明如何按需查阅。

## 目标读者与入口

| 读者需求 | 建议入口 |
|---------|---------|
| 想先了解《道德经》是什么 | [名实与全书概览](concepts/daodejing-overview.md) |
| 想读最接近古本的原文 | [帛书乙本](text/boshu-yi.md)（较完整底本）/ [北大汉简](text/beida-hanjian.md)（最完整汉本） |
| 想理解注家如何解读 | [权威解读](commentaries/index.md) 三线任选 |
| 想核对某句的版本差异 | [关键异文对照](text/key-variants.md) |
| 想溯源某条论断的信源 | [信源登记簿](references/index.md) |

## 按场景阅读路径

1. **通读入门**：概念（名实概览 → 出土三大系统 → 核心概念）→ 原文（以帛书乙本为主线）→ 解读（现代注本入门）。
2. **研究校勘**：四个出土原文文档 + [关键异文对照](text/key-variants.md) + [出土文献校注解读](commentaries/unerthed-collation.md)，逐条核对异文。
3. **义理钻研**：[历代注本解读](commentaries/historical-commentaries.md)（王弼/河上公/严遵/苏辙）对照 [现代学者注本解读](commentaries/modern-commentaries.md)（陈鼓应/楼宇烈/李零），分歧见 [争议与不确定性](commentaries/controversies.md)。
4. **版本断代**：[出土文献三大系统](concepts/unerthed-systems.md) + [争议与不确定性](commentaries/controversies.md)（断代/释文分歧)。

## 信源溯源方法

- 正文每条事实性论断以脚注 `[^source-id]` 溯源，ID 对应 [信源登记簿](references/index.md) 的「统一信源 ID 清单」。
- 每条信源含可核查 `resource`（出版社·年份），可据此核对原著。
- 释文一律溯源自正式出版整理本（帛书/楚简/汉简），残毁处标注，不编造。

## 与其他 bundle 的分工

| 需求 | 用哪个 bundle |
|------|--------------|
| 怎么读帛书、如何选注本 | `boshu-reading` |
| 版本源流谱系、传本考证 | `laozi-lineage` |
| **原文 + 三线解读的横向整合** | `laozi-works`（本 bundle） |

## 使用注意

- 郭店楚简本为**节选本**（现存约 2000 字，非全本），勿当全本引用。
- 帛书甲本残毁较多，原文以**乙本为底本、甲本补校**。
- 本 bundle 呈现「关键篇目通读释文 + 逐章题解」，完整逐字转录以正式整理本图版与释文为准。