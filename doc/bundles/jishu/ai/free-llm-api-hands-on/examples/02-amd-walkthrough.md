---
okf_version: "0.2"
type: Example
title: "AMD Radeon Cloud Token Factory 接入演练：领 Key、当日模型名单与积分调用"
description: "developer.amd.com.cn 注册领 Key、OpenAI/Anthropic 双端点 curl、2026-09-16 在册五款模型（含 VLM 喂图）、积分相对用量解读、重试/并发与客户端接入；博文 4 款名单的时效对照"
tags: [AMD, Radeon-Cloud, Token-Factory, 积分制, MiniCPM5, Qwen3.8, DeepSeek, 接入演练]
generated: { by: "process:blog-article-to-okf-wiki:E", at: "2026-09-16T22:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-16T22:00:00+08:00" }
status: flagged
stale_after: 2026-11-30
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/qnQqCivPiuRfJIVMM-zTNQ
    title: 博文 §4 AMD Radeon Token Factory
  - id: amd-panel
    resource: https://developer.amd.com.cn/radeon/modelapis
    title: AMD Public Free Model APIs 面板（核验日实时名单）
  - id: amd-docs
    resource: https://amd-aim.github.io/radeon-cloud-docs/zh-cn/
    title: AMD Radeon Cloud 官方文档
---

# AMD Radeon Cloud Token Factory 接入演练

> ⚠️ 本篇最大的坑不是接不通，而是**模型名单变得快**：博文 2026-09-09 的 4 款名单在核验日（09-16）已变为 5 款。**每次使用前先刷新面板** https://developer.amd.com.cn/radeon/modelapis 核对当日模型名（F-075）。

## 0. 平台事实卡（核验后）

| 项 | 值 |
|---|---|
| 官方品牌 | Radeon Cloud / **Token Factory（BETA）**，面板名 Public Free Model APIs（F-074） |
| 入口 | https://developer.amd.com.cn/radeon/modelapis （/radeon/tokenfactory 同为官方入口） |
| OpenAI 端点 | `https://developer.amd.com.cn/radeon/api/v1/chat/completions`（Bearer） |
| Anthropic 端点 | `https://developer.amd.com.cn/radeon/api/v1/messages`（**x-api-key** + anthropic-version 2023-06-01）；另有 `/v1/messages/count_tokens`（F-074/F-089） |
| Key | 一个 `rc-` 开头 Key，全模型通用；"想换模型改 model 字段就行"（F-074） |
| 登录 | 手机号 / 邮箱 / GitHub / CSDN / 魔搭 ModelScope；免绑卡；GitHub 授权仅读基础公开信息（F-041） |
| 计量 | 积分 pts：输入 0.14 / 输出 0.28 / 缓存读 0.0028（每百万 token），模型卡原文 "Free to use. Points show relative usage—not a charge."（F-076） |
| 稳定性 | BETA/experimental；官方并发每 Key 8；速度偏慢有独立旁证（F-077） |

## 1. 注册领 Key（约 10 分钟）

1. 打开入口，右上角 **Login**（F-041）。
2. 任选一种方式登录：国内手机号、邮箱（收验证邮件激活）、GitHub / CSDN / 魔搭快捷登录。
3. 进入 **Public Free Model APIs** 区域，点任一模型卡片。
4. 弹窗一次性给出三件套：Base URL、Model 名、API Key（所有免费模型共用），并附现成 curl——全部复制保存（F-041）。

## 2. 核验日在册模型（以面板当日列表为准）

| model 字段（2026-09-16） | 类型 | 标签 | 与博文名单关系 |
|---|---|---|---|
| `DeepSeek-V4-Flash-0731` | LLM（原生 **1M** 上下文，F-079） | Free | 博文有；注意旧 V4-Flash 名 09-10 起路由 V4.1-Flash |
| `Qwen3.8-Flash-Next` | 多模态（文本/图像/视频），125B/6B，原生 262K 可外推 1M | Free | 博文有（F-080） |
| `MiniCPM5-2B` | LLM 端侧向，128K | Free | **取代博文的 MiniCPM5-1B**（2B 版 2026-09-07 开源，F-078） |
| `Qwen3.8-27B` | LLM 稠密版 | Limited Free | **新增** |
| `MinerU2.5-Pro` | 文档解析/OCR 向 | Limited Free | **新增** |
| ~~`DeepSeek-V4-Flash-Vision-Exp`~~ | — | 已下架 | 模型卡返回 "Model card not found"（F-075） |
| ~~`MiniCPM5-1B`~~ | — | 移出免费池 | 官方文档称不再对外提供（F-075） |

> 勘误对照（F-040/F-079）：博文称 DeepSeek-V4-Flash-0731 上下文 64K–128K，**官方为原生 1M**；博文把 1B（0.5GB INT4/128K，2026-05-26 开源）与正文他处的 2B（4B 以下新榜首）混用——AMD 窗口现在给的是 2B（F-078）。

## 3. curl 调用

OpenAI 兼容（文本）：

```bash
curl https://developer.amd.com.cn/radeon/api/v1/chat/completions \
  -H "Authorization: Bearer 你的Key" \
  -H "Content-Type: application/json" \
  -d '{"model":"DeepSeek-V4-Flash-0731","messages":[{"role":"user","content":"你好"}]}'
```

VLM 喂图（Qwen3.8-Flash-Next 支持文本/图像/视频，按 OpenAI 视觉消息格式）：

```bash
curl https://developer.amd.com.cn/radeon/api/v1/chat/completions \
  -H "Authorization: Bearer 你的Key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.8-Flash-Next",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "这张截图里报了什么错？"},
        {"type": "image_url", "image_url": {"url": "https://example.com/screenshot.png"}}
      ]
    }]
  }'
```

Anthropic 兼容客户端（如 Claude Code）：端点用 `/radeon/api/v1/messages`，认证头用 `x-api-key: 你的Key` 并带 `anthropic-version: 2023-06-01`（F-074）。

## 4. 积分怎么读（避免两个误解）

1. **pts 不是账单**：模型卡明示积分只表示相对用量、不构成收费（F-076）。控制台的美元数字是参考折算；官方文档示例里的 `daily_cost_limit_usd: 10` 同时声明"只是示例，不同账户不一样且会随时间变化"（F-077）。
2. **不要采信"额度已从 $10/天缩到 $1/天"**：该说法仅见于博文，无任何官方公告或可信实测佐证，且被 09 月仍在更新的多份相反口径覆盖，已判传言（F-077）。博文作者"200 万 token 耗约 5%"为个人实测、按官方单价粗算不可复算，仅作体感参考（F-077）。
3. **重置节奏两口径并存**：credits/usage 页称按亚洲/上海时间每日重置，rate-limits 页称滚动周期——以你登录后控制台显示为准（F-076）。
4. **省钱技巧**：多轮对话把历史整段传入，缓存读取单价仅为输出价的 1%（0.0028 vs 0.28），自动命中 Prompt Cache（F-044/F-076）。

## 5. 客户端接入与稳定性设置

- **WorkBuddy / Cherry Studio / Cursor / opencode**：与普通 OpenAI 兼容渠道相同——Base URL 填 `https://developer.amd.com.cn/radeon/api/v1`（或面板弹窗给的完整值），Bearer 粘 Key，model 从第 2 节名单原样复制（F-043）。
- **客户端必调两项**（F-044/F-077）：
  - 重试次数调大（连接偶发网络错误，重试基本可稳）；
  - 超时放宽（首字延迟明显、高峰更甚，独立实测约 800 tok/s）。
- **并发预期**：官方每 Key 8 并发；博文"超过 5 个开始排队"是个人体感，方向一致。定位开发调试，**不当生产高并发 API 用**（F-077）。
- Limited Free 模型（Qwen3.8-27B、MinerU2.5-Pro）随时可能撤，有工作流依赖就尽快固化备用方案（F-044）。

## 6. 数据边界

未公开产品信息、个人隐私、医药/患者/经营数据不要走云端推理；这类需求改用本地 MiniCPM5-2B（端侧）或 Ollama 本地模型（F-044/F-078）。

## 7. 每次开工 30 秒检查清单

- [ ] 面板当日模型名单与脚本中的 `model` 字段一致（名单以周计变动）
- [ ] 用的是免费区卡片弹窗给出的 Key（`rc-` 开头）与 Base URL
- [ ] 客户端 retry/超时已放宽
- [ ] 积分余额足够当日任务（每日重置，但 Limited Free 标签仍在）
