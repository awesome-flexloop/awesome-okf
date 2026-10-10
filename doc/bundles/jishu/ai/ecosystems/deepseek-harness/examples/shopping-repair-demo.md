---
type: example
title: "假商店项目修复与生成演示"
description: "Harness 2.0 实测演示复述：修复 16 条订单+报表脚本中 2 个计算错误（净收入 977→662），同对话生成自包含 report.html、产品筛选下拉框、Creator 插件面板与定时自动化。"
tags: [DeepSeek, Harness, 演示, Bug修复, report.html]
generated: { by: "process:seven-concepts-cmd+wechat-public-okf", at: "2026-10-10T00:00:00Z" }
status: draft
stale_after: 2026-12-05
sources:
  - id: wx-pjfnnu
    title: DeepSeek Harness 2.0 来了，Codex 该退休
    resource: https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw
---

# 假商店项目修复与生成演示

> 本页为公众号文章中的实测过程**复述**，非本文档独立复现；过程与数字以原文章为准。[^wx-pjfnnu][F-002]

## 1. 测试场景

- 一个假商店项目：**16 条订单** + 一个报表脚本。
- 里面埋了 **2 个计算错误**：
  - 把**已取消的订单**也算进去；
  - **退货件数**没正确扣掉。

## 2. Harness 的处理结果

| 检查 | 结果 |
|------|------|
| 跳过已取消订单 | ✅ |
| 用真实退货件数，而非一律当 0 | ✅ |
| 4 个原测试全过 | ✅ |
| CSV 和测试文件一个字节没动 | ✅ |
| **净收入** | 从错误的 **977 修正到 662**（美元） |

> 这是真修好的 bug，不是把数字变好看。

## 3. 同对话进阶能力

在**同一段对话**中 Harness 顺手完成：

- **report.html**：自包含报告，连生成器脚本和说明文档一起打包，**不依赖任何外部库**。
- **产品筛选**：补一句"加个产品筛选"就出现下拉框——选 Launch Tee 显示 200/8 件，Reset 一键还原，整店总额标得清清楚楚。
- **Creator 插件**：说"要个报告清单面板"，直接生成插件源码，装完不重启出现在侧边栏，三个勾全打上，切走再回来状态还在。
- **Automation 定时**：90 秒后自动读数据、算出核实过的数字、写成文件。

## 4. 局限（作者观察）

- 报告任务在**浏览器截图那步磨蹭太久**，需要手动叫停。
- Creator 模式一开始**乱翻源码**，指令缩小了才干活。

> 这几条局限是作者对演示过程的观察结论，属单源主观描述，未独立复现验证。

[^wx-pjfnnu]: [DeepSeek Harness 2.0 来了，Codex 该退休](https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw)，有限进步Seven，2026-10-05。