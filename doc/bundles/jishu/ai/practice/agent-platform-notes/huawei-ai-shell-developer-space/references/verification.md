---
type: Reference
title: "AI Shell 官方核验与边界"
description: "对文章中的产品定位、免费容器、入口、授权执行和模型信息进行官方交叉核验，并记录未证实的作者实测声明。"
tags: [verification, ai-shell, huawei-cloud, provenance]
sources:
  - id: official-product
    resource: "https://developer.huaweicloud.com/aishell.html"
    title: "华为云 AI Shell 产品页"
  - id: official-faq
    resource: "https://support.huaweicloud.com/hdspace_faq/zh-cn_topic_0000002659760463.html"
    title: "华为云开发者空间 AI Shell 入口 FAQ"
  - id: official-community
    resource: "https://bbs.huaweicloud.com/blogs/479448"
    title: "华为云云社区：探索智能 Shell 交互新范式"
generated: { by: process:seven-concepts-r, at: "2026-09-20T00:00:00Z" }
verified: [{ by: process:seven-concepts-v, at: "2026-09-20T00:00:00Z" }]
status: stable
stale_after: "2026-12-31"
---

# 官方核验与边界

## P0 核验表

| 核验对象 | 文章口径 | 官方证据 | 结论 |
|---|---|---|---|
| 产品定位 | 云端 Linux + 大模型开发机 | 官方产品页称其为大模型驱动的云上部署发布智能体 | ✅ 产品定位相符，不能据此证明具体机器规格 |
| 免费性 | 体验版免费、不扣核时 | 官方 FAQ/产品页称容器免费使用 | ✅ 容器免费；持久化版额度扣减规则仍需以当前控制台为准 |
| 入口 | 开发者官网侧边栏进入 | 官方 FAQ 明确支持从开发者栏目侧边栏拉起 | ✅ |
| 授权执行 | 自然语言生成脚本，用户授权后执行 | 官方产品页明确描述授权命令执行 | ✅ |
| 预置模型 | 自带大模型，作者提到多个模型 | 官方页面称预置多款模型，FAQ 举例 GLM5 | ✅ 预置模型存在；具体版本会变化 |
| 8 核 16G、磁盘、地域 | 作者实测配置 | 未找到对应的官方固定规格承诺 | ⚠️ 仅博文单源 |
| 3 小时释放、12 小时断连关机 | 作者实测环境行为 | 未找到对应的官方 FAQ 固定条款 | ⚠️ 仅博文单源 |
| 7934 核时、47 天/一年 | 作者计算 | 未找到可复核的官方额度页面 | ⚠️ 仅作者计算，不进入推荐结论 |
| 18 个技能 | 作者观察 | 官方页面只确认预置技能/最佳实践，未确认数量 | ⚠️ 仅博文单源 |

## 勘误与使用边界

1. 本知识包不把作者使用的具体硬件配置写成华为云的固定产品规格。
2. “免费”仅指官方页面所称容器免费使用，不等于用户主动创建的 ECS、模型 API 或其他云资源全部免费。
3. 模型名称、模型版本、技能数量和体验时长会随平台更新变化，读者应以控制台和官方页面当前显示为准。
4. 文章截图未作为独立证据使用；截图中的信息若未在文字或官方源中出现，均不进入事实层。
