---
okf_version: "0.2"
type: Concept
title: "Verbi 产品形态与团队事实"
description: "AI 口语陪练 Verbi 的产品定位、9 种语言、四技能功能矩阵、双端上架与创始人/技术栈事实"
tags: [verbi, ai-language-tutor, 产品分析, react-native]
generated: { by: "process:blog-article-to-okf-wiki", at: 2026-09-20T00:00:00Z }
status: stable
stale_after: 2026-12-31
sources:
  - id: refs
    resource: /references/article-source.md
  - id: official-site
    url: https://www.appverbi.com/
---

# Verbi 产品形态与团队事实

## 一句话定位

Verbi 是一款把「开口说」放在中心的 AI 语言学习应用：与 AI 老师进行真实对话练习，明确不做闪卡刷词（F-002）。其官网表述为「The fastest path to confidence is speaking, not endless flashcards」。

## 语言覆盖：9 种

西班牙语、法语、葡萄牙语、德语、意大利语、日语、韩语、中文（普通话）、俄语（F-003）。每种语言均包含对话练习、每日词汇、动词变位、语法与听力模块。

## 功能矩阵：围绕「说」的四技能

| 技能 | 具体功能（F-004） |
|------|------------------|
| 口语 | 入门→高级结构化语音课程、主题短课、检查点与对话 capstone；自由 Roleplay（自设场景）；Hold to speak 即时反馈；可选 AI 语音与个性；支持从「英语为主」到「全目标语言」的辅助强度调节 |
| 词汇 | 每日单词推送（含释义/例句/发音）、收藏生词、薄弱点复习 |
| 语法 | 动词变位演练、真实聊天场景中的文字表达 |
| 听力 | 按水平分级的情景音频，随等级加速、趋近自然语速 |

**习惯与留存机制：** 打卡 streak（产品界面示例为连续 12 天）、周目标、技能分数（口语均分示例 ~66%）、环形学习进度、Word of the Day 主页小组件、iOS Focus Mode（屏蔽干扰应用、靠练习挣休息时间）；并用填字游戏、词义匹配/回忆/填空测验巩固词汇（F-004）。

## 上架形态：iOS + Android + Web 三端

| 渠道 | 形态（F-005） |
|------|---------------|
| App Store | 「Verbi: Speak a New Language」，id6760734657，教育类，免费 + 内购，iPhone/iPad |
| Google Play | 同名应用，包名 com.vocably.app |
| Web | appverbi.com 提供浏览器版，无需下载 |

应用包名沿用 `vocably`，产品早期名称曾为「Verbi: Vocabulary Training App」，后转向口语定位。

## 上线时间

2026-04-01 首次发布（F-006）；TrustMRR 记录 Founded 为 2026 年 4 月，RevenueCat 数据自 2026-07-29 起接入追踪。

## 创始人画像

**Pedro Henrique Machado**（X：@pedrotech_），账号所在地加拿大温哥华（F-007）：

- Verbi 创始人；
- 同时是 Twitch 的软件工程师（SDE）；
- 软件顾问 / YouTuber，YouTube 频道约 28 万订阅。

因此「单人开发者」的准确含义是：**Verbi 没有联合创始人与雇员，由他一人完成产品、ASO、增长等全部工作**；但他并非全职 all-in，且内容创作能力（YouTube/TikTok）是其个人禀赋的一部分。

## 技术栈与融资

- 技术栈：**React Native（前端）+ Node.js（后端）+ RevenueCat（订阅基础设施）**（F-008，TrustMRR 与博文口径一致）；
- Bootstrapped，无外部融资（F-009）。

RevenueCat 在其中承担跨平台购买、收据核验与订阅/营收看板，使小团队无需自建订阅后端（其免费档覆盖月追踪收入 $2,500 以下的应用）。
