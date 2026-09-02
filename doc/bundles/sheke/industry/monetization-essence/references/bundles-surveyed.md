---
type: Reference
title: 497 束 OKF 知识包考察记录
description: 对 awesome-okf-xs 知识包库 9 域/56 组/497 束的全面盘点与考察方法记录——每域代表性束深度阅读、可变现资产识别、133 种方案的溯源基底。
tags: [okf, bundles, survey, 考察, 497]
generated: { by: "agent:seven-concepts-cmd", at: "2026-09-02T00:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: bundles-index
    resource: "../../../index.md"
    title: "awesome-okf-xs 知识包总索引"
---

# 497 束 OKF 知识包考察记录

本文件记录「133 种可行性方案」的信源基底：对 `doc/bundles/` 下 **9 域 / 56 组 / 497 束** 的全面盘点与考察方法。所有方案引用的束均为本库真实存在的束。

## 一、9 域总览

| 域 | 组数 | 覆盖分组 | 代表性束（深度阅读） |
|---|---|---|---|
| guoxue 国学 | 15 | buddhism/confucian/confucius/daojia/guiguzi/hetu-luoshu/huangdi/laozi/legalism/mozi/suanxue/yangming/yinyangjia/zhouyi/zhuangzi | laozi-works、baopuzi、yinfujing、chuanxilu |
| jishu 技术 | 17 | ai/autonomous/build/comm/containers/data/dev/document/gui/iot/ml/python/rust/systems/terminal/viz/web | agent-industry-research、langchain-ai、deepseek-pricing、cpython、onnx |
| kexue 科学 | 3 | chemistry/math/physics | baopuzi（化学史）、physics-classics、east-west-dialogue |
| meta 元 | 3 | okf-desktop/okf-ecosystem/okf-spec | okf-ecosystem、okf-kit、okf-spec |
| sheke 社科 | 6 | finance/industry/marketing/relationships/sexology/workplace | ai-monetization、personal-investing、marketing-fundamentals、gottman-seven-principles |
| wenxue 文学 | 2 | classics/english | fusheng-liuji-reading、english-grammar |
| yishu 艺术 | 2 | liaoyu/vocal | music-therapy、art-therapy、meitong-yanyin-pedagogy |
| yixue 医学 | 6 | daoyi/fangzhong/huangdi-neijing/medicine/tcm/yangsheng | ishinpo-reading、neijing-reading、shanghan-zabinglun |
| zhexue 哲学 | 2 | methodology/psi | godgpt、psi-core、first-principles |

> 组数合计 56，与 `doc/bundles/index.md` 登记的 56 组一致；束总数 497（含带 index.md 的锚点束与根级 marker 束），以门控 `gates.bundles` 重算口径为准。

## 二、考察方法

1. **盘点**：按 `doc/bundles/` 目录树登记 9 域/56 组/497 束清单，标记可用信源（优先 jishu 17 组、sheke/industry、guoxue/daojia、zhexue/methodology、sheke/finance+marketing）。
2. **深读**：对每域抽取代表性束做深度阅读，采集事实台账（facts.md，44 条，无因果词、可溯源、F 编号）。
3. **洞察**：跨域提炼 5 条四元组洞察（见 [00-catalog-summary](../examples/00-catalog-summary.md) 三、跨域洞察）。
4. **萃取**：按 9 域逐域萃取方案，每个方案引用 ≥1 个真实束（溯源校验通过）。

## 三、方案溯源分布（133 种）

| 方案文件 | 溯源束覆盖 |
|---|---|
| [plans-jishu.md](../examples/plans-jishu.md)（48） | jishu 全部 17 组代表束 |
| [plans-sheke-zhexue-meta.md](../examples/plans-sheke-zhexue-meta.md)（41） | sheke 6 组 + zhexue 2 组 + meta 3 组 |
| [plans-guoxue-kexue-wenxue-yixue-yishu.md](../examples/plans-guoxue-kexue-wenxue-yixue-yishu.md)（44） | guoxue 15 组 + kexue 3 组 + wenxue 2 组 + yixue 6 组 + yishu 2 组 |

## 四、可变现资产共同特征（Task 4 归纳）

从 497 束考察中归纳出「可变现资产」的五项共同特征（详见 [03-channel-taxonomy](../concepts/03-channel-taxonomy.md)）：

1. **可独立交付**：能脱离生产者的实时在场，形成可交换的对象（文档/代码/服务/数据）。
2. **稀缺且被需求**：占据信息差/能力差/位置差/时间差/注意力差/许可差/数据差中的至少一种。
3. **交易成本可降**：标准化、协议化、自动化降低交付与匹配成本。
4. **信任可建立**：有客观验收信号、合规边界或口碑机制支撑信任。
5. **可进入正循环**：收入可再投入生产，形成复利而非一次性榨取。

## 五、考察局限与边界

- 束内数字（如市场规模、价格）以束内原文为准，本记录不新增市场判断。
- 对 497 束为「全量盘点 + 代表性深读」，未对每束全文精读；已深读束在 facts.md 中逐条登记可溯源位置。
- 方案为蓝图性质，真实落地以 [合规红绿区](../concepts/04-compliance-zones.md) 与平台沙箱验证为准。
