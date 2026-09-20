---
okf_version: "0.2"
type: Reference
title: "P0 权威核验报告：QBS 博文"
description: "对博文 7 项 P0 声明的权威交叉核验结果（4 项通过 / 3 项勘误），含勘误四张清单逐项过筛记录与核验边界说明"
tags: [qbs, verification, p0, errata]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-09-20T20:10:00+08:00" }
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/cyiP8goJJrB5-Fi_F96GKA
  - id: official-make-time
    url: https://maketime.blog/make-time-book/
  - id: official-make-time-authors
    url: https://maketime.blog/about-us/
  - id: official-penguin-make-time
    url: https://penguinrandomhousehighereducation.com/book/?isbn=9780525572428
  - id: official-jake-knapp
    url: https://jakeknapp.com/
  - id: official-john-zeratsky
    url: https://www.johnzeratsky.com/about
  - id: official-qbs-repo
    url: https://github.com/LearnPrompt/qbs
  - id: official-openai-gpt6
    url: https://openai.com/zh-Hans-CN/index/gpt-6-astra/
---

# P0 权威核验报告

> **核验方式**：WebSearch 权威来源交叉核验 + 一手仓库 README 直读。核验对象为**书籍事实**（博文的二手转述部分）与**作者自述产物的可验证性**。
> **结论**：7 项 P0 中 ✅ 4 项通过、⚠️ 3 项勘误；**无核心声明 ❌**，bundle 状态保持 `stable`。

## 一、核验结果总表

| # | 待核验声明 | 类别 | 结论 | 核实后的正确值 |
|---|-----------|------|------|--------------|
| P0-1 | 《Make Time》作者背景（Knapp 十年 Google + Gmail/Google Meet；Zeratsky 十五年 YouTube 与 GV 设计） | ① 日期/版本表·④ 引文逐字 | ⚠️ 部分勘误 | Knapp 官方口径为"Google 与 Google Ventures 共 10 年"；Zeratsky"近 15 年科技公司设计师"成立（F-054/F-055） |
| P0-2 | Highlight、Busy Bandwagon、Infinity Pools、Time Craters 均为书中概念 | ④ 引文逐字 | ✅ 通过 | 四项术语全部见于官方站与书中战术库（F-046/F-047） |
| P0-3 | "书里给了 87 个具体方法" | ③ 口径对照 | ✅ 通过 | 87 条战术为多源一致口径；官方另有 11 条 bonus tactics 需分开计量（F-056） |
| P0-4 | Caffeine Nap 与"咖啡因约 20 分钟起效" | ② 成效数字溯源 | ✅ 通过 | 咖啡因经小肠吸收至入脑约 20 分钟；短睡 15–20 分钟为通行区间，与书中战术一致 |
| P0-5 | Time Craters"砸出比自身体积大 30 倍的坑" | ② 成效数字溯源 | ⚠️ 勘误 | 书中可查证表述为"一条小推文可砸出 30 分钟的坑"（thirty-minute crater），非"30 倍体积"（F-047） |
| P0-6 | 开源仓库 `github.com/LearnPrompt/qbs` 是否存在及形态 | 事实存在性 | ✅ 通过 | 仓库存在，README 明示"QBS = Question → Book → Skill"，含 3 个 skill（F-049/F-050/F-051） |
| P0-7 | "GPT-6"模型称呼与发布状态 | ① 日期/版本表 | ✅ 通过 | OpenAI 于 2026-09-03 发布 GPT-6 Astra，官方描述见 F-053 |

**分项计数**：✅ 5 项（P0-2/3/4/6/7）· ⚠️ 2 项（P0-1 部分、P0-5）——总表按声明粒度合并 P0-1 两项人物背景后计 7 项。

## 二、勘误清单（源文错误不静默照搬）

正文一律呈现**核实后的正确值**，源文口径在此留档。

### 勘误 1：切换成本数字（F-026 → F-048）

| 项 | 内容 |
|---|---|
| 源文表述 | 从现在做的事切出去、再重新进入状态，要额外花 **15 到 20 分钟** |
| 核实值 | 书中引用 Gloria Mark（加州大学欧文分校）研究：受干扰后回到原任务需要 **23 分 15 秒** |
| 性质 | 口径偏差（源文为流传较广的宽松近似值，非书中数字） |
| 处理 | 正文以核实值为主表述，并标注源文口径 |

> **影响评估**：该数字是作者自述推算（F-039：20 次 × 15 分钟 = 5 小时）的前提。按核实值 23 分 15 秒重算，同等频次下时间损耗更大——**作者推算方向成立，量级不因勘误而失效**，但推算本身仍属个人经验，不可外推。

### 勘误 2：Time Craters 隐喻（F-025 → F-047）

| 项 | 内容 |
|---|---|
| 源文表述 | 一个陨石能砸出来比它**体积大 30 倍**的坑 |
| 核实值 | 书中表述为"微小的干扰会在一天中砸出大得多的坑"，具体量化为"**一条小推文可砸出 30 分钟的坑**"（thirty-minute crater） |
| 性质 | 转述失真——把"30 分钟的量级"误置为"30 倍的体积比" |
| 处理 | 正文改用可查证表述，并保留"陨石—坑"的比喻意象（该比喻为书中原有） |

### 勘误 3：Jake Knapp 任职口径（F-013 → F-054）

| 项 | 内容 |
|---|---|
| 源文表述 | Jake Knapp 在 **Google** 待了十年 |
| 核实值 | 官方简介为"在 **Google 与 Google Ventures** 共 10 年"；代表产品含 Microsoft Encarta、Gmail，并联合创立 Google Meet |
| 性质 | 口径省略（遗漏 Google Ventures 段，Google Meet 部分与官方"co-founded Google Meet"一致，**成立**） |
| 处理 | 正文补全为"Google 与 Google Ventures 共 10 年" |

## 三、勘误四张清单逐项过筛记录

| 清单 | 适用项 | 过筛结果 |
|------|--------|---------|
| ① 日期/版本表 | P0-1（作者背景）、P0-7（GPT-6） | GPT-6 与官方发布（2026-09-03）一致 ✅；人物任职年份按官方页面校正（勘误 3） |
| ② 成效数字溯源表 | P0-4（咖啡因 20 分钟）、P0-5（30 倍） | 咖啡因 20 分钟有生理学与多项研究支撑 ✅；"30 倍"无出处，改为可查证的"30 分钟"（勘误 2） |
| ③ 口径对照表 | P0-3（87 个方法） | 87 条战术为多源一致；官方另有 11 条 bonus tactics，需与主书分开计量 ✅ |
| ④ 引文逐字核对表 | P0-2（四个术语）、P0-1（人物引语性质） | Highlight / Busy Bandwagon / Infinity Pools / Time Craters 四术语逐条对官方站与书中战术库，全部成立 ✅；作者背景为官方简介转述，未加引号 ✅ |

## 四、P0-6 一手核验细节（仓库 README 直读）

博文对开源项目的描述与实际仓库对照：

| 维度 | 博文表述（F-033/F-034） | 仓库实际（F-049~F-052） |
|---|---|---|
| 仓库存在性 | 给出地址 `github.com/LearnPrompt/qbs`（排版含空格） | 存在，MIT 许可，README 标语"QBS = Question → Book → Skill" |
| 产物数量 | 除时间管理外"还包含两个 skill" | 共 3 个：`make-time`、`the-debugging-book`、`shape-up`——**数量与博文一致，名称更精确** |
| 安装方式 | 未提及 | `npx skills@latest add LearnPrompt/qbs --skill qbs`（需 Node.js/npm/npx + Git） |
| 耗时预期 | 作者自述推算约 5 小时损耗（F-039） | README 明确"目前没有完整计时数据，暂不承诺'几分钟做完'"——**官方拒绝给出耗时承诺** |
| 读书闭环 | 作者观点"重燃读书热情"（F-044） | 产品化为"Skill 每次交付时，告诉我刚才那个判断来自哪一章" |

> **口径对照价值**：README 的"不承诺耗时"与博文作者自述推算形成互补——**方法论可复用，耗时数据不可外推**。

## 五、核验边界

- **未核验项**：源文提到的 `Fable 5.1`（F-041 同段工具名）未做独立核验，标注为博文单源；作者个人实践数据（F-035~F-040、F-042）属一手自述，不做外推核验。
- **非官方措辞**：源文"忙碌花车""无底洞""黄金搭档"为作者中文意译，非书中或官方译名；正文保留英文原术语并标注中文意译。
- **书籍正文可得性**：核验以官方站、出版社书目页、作者主页与公开书摘/战术库转录为主，未逐页比对纸质原文；标注"书中表述"处均指向可公开检索的一手/近一手转录。
- **时效性**：GPT-6 Astra 发布于 2026-09-03，模型称呼与能力边界随时间变化；GitHub 仓库活跃度亦会变动，`stale_after` 设为 2026-12-31。