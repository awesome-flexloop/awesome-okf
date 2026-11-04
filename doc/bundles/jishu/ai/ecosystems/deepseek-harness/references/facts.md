---
type: reference
title: "事实登记 F-001~F-016"
description: "DeepSeek Harness 2.0 文章的客观事实登记（页面事实/作者主张分层），含 P0 数字与主张的核验结论。"
tags: [DeepSeek, Harness, facts, 事实登记]
generated: { by: "process:seven-concepts-cmd+wechat-public-okf", at: "2026-11-04T10:15:04+08:00" }
status: draft
stale_after: 2026-12-05
sources:
  - id: wx-pjfnnu
    title: DeepSeek Harness 2.0 来了，Codex 该退休
    resource: https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw
    author: 有限进步Seven
    last_modified: 2026-10-05
---

# 事实登记 F-001 ~ F-016

> 事实分层遵循 wechat-public-okf：`page_fact` 为页面结构事实，`author_claim` 为作者主张/观点。执行者解释不进入本表。

本页保存 2026-10-05 文章的历史登记，本次没有重读旧原文或复现结果。2026-11-04 仅纠正信任层级：以下均为旧记录中的作者主张；曾有 `verified` 标签不代表独立执行验证，现撤回该标签。编号与主张文本保留，价格和能力不可作为当前契约。

| F | claim | type | locator | status |
|---|-------|------|---------|--------|
| F-001 | Harness 是模型外面那层壳，模型负责"想"，它负责"干"（读文件/改代码/跑命令/检查结果） | author_claim | 文章开头 | single-source |
| F-002 | 实测用假商店项目：16 条订单 + 1 个报表脚本，埋 2 个计算错误（含已取消订单、退货件数未扣） | author_claim | 文章实测段 | single-source |
| F-003 | Harness 跳过已取消订单 | author_claim | 实测段 | reported-result |
| F-004 | Harness 用真实退货件数而非一律当 0 | author_claim | 实测段 | reported-result |
| F-005 | 4 个原测试全过，CSV 和测试文件一个字节没动 | author_claim | 实测段 | reported-result |
| F-006 | 净收入从错误的 $977 修正到 $662 | author_claim | 实测段 | reported-result |
| F-007 | 同对话生成自包含 report.html（连生成器脚本和说明文档打包，不依赖外部库） | author_claim | 实测段 | reported-result |
| F-008 | 补"加个产品筛选"出现下拉框；选 Launch Tee 显示 $200/8 件，Reset 还原，显示整店总额 | author_claim | 实测段 | reported-result |
| F-009 | Creator 模式说"要个报告清单面板"直接生成插件源码，装完不重启出现在侧边栏，状态保留 | author_claim | Creator 段 | reported-result |
| F-010 | Automation 支持定时：90 秒后自动读数据、算出核实过的数字、写成文件 | author_claim | Automation 段 | single-source |
| F-011 | 四种模式：Standard 日常写代码、PTC 写 TS 编排工具、Minimal 极简实验、Creator 造插件 | author_claim | 模式段 | single-source |
| F-012 | Harness 本身 MIT 开源免费，模型调用单独计费 | author_claim | 钱账段 | single-source/flagged |
| F-013 | V4.1 Flash 非高峰输入 15 美分/百万、输出 60 美分/百万 token | author_claim | 钱账段 | single-source |
| F-014 | 高峰价格翻倍（原文如此，绝对值未给出） | author_claim | 钱账段 | single-source |
| F-015 | App 跑在电脑上不等于模型在本地跑 | author_claim | 钱账段 | single-source/flagged |
| F-016 | 需要人盯：报告浏览器截图磨蹭、Creator 乱翻源码；建议挑自己知道答案的项目起步 | author_claim | 结尾段 | single-source |

## 核验小结

- **作者结果自述（reported-result）**：过程、测试与文件不变等仅来自旧文章登记，不代表本次独立核验。表内未登记标题或账号事实，不以此宣称它们已独立核验。
- **单源（single-source / flagged）**：开源 MIT 免费、模型远端推理、定价、Automation、四种模式细节、"需人盯/建议"等保留历史来源层级，本次不升级为当前官方契约。
- **P0 数字**：977→662、15/60 美分、16 条订单、4 个测试等，均来自文章陈述；其中高峰翻倍推论已标注为推断，未升级为事实。
