---
okf_version: "0.2"
type: Reference
title: "P0 核验报告：Matrix 0人公司"
description: "6项P0声明核验：产品存在/架构/模型列表/商业基建✅，GDPval数字与案例数字⚠️厂商自述，平台形态单源；无❌硬错误，无勘误"
tags: [核验报告, Matrix, GDPval, 厂商自述, P0核验]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-01T17:30:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/C5clrnoai50eneYvgP1nLw
    title: 智潮笔记博文（2026-07-04）
  - id: official-1
    url: https://www.aitoolnet.com/matrix
    title: AI Toolnet 收录页（转录 Matrix 官方文案）
  - id: official-2
    url: https://hotools.com/item/matrix
    title: Hotools 收录页（2026-06-23）
  - id: official-3
    url: https://aigjdh.com/sites/2669.html
    title: AI工具集（aigjdh）收录页
---

# P0 核验报告（verification）

> 核验时间：2026-09-01 ｜ 核验方式：WebSearch 权威来源交叉 ｜ 信源距离预判：**厂商自宣浓度高的第三方转述**
>
> **结论：6 项 P0 核验 = 2 ✅ + 3 ⚠️ + 1 单源，0 ❌。无源文硬错误，无勘误项。**

## 核验明细

### ✅ V1：Matrix 产品存在性与定位（覆盖 F-003/F-039）

- 博文口径：Matrix 是"让 Agent 帮你开公司"的产品，官网 matrix.build
- 核验：三个独立第三方 AI 工具导航站收录（aigjdh.com / hotools.com（2026-06-23）/ aitoolnet.com），描述均为"为超长周期自主运行而生的主动式多智能体协作平台"，CEO Agent 动态组建部门的叙事与博文一致
- 结论：**✅ 通过**——产品真实存在，定位转述准确

### ✅ V2：架构机制与模型接入列表（覆盖 F-006/F-010~F-017/F-040/F-041/F-042）

- 博文口径：CEO Office + 六部门 + 领队/协作 Agent；内置 Neo Agent + 接入 Claude Code/Codex/ChatGPT/Gemini/GLM/DeepSeek/Kimi/Qwen；Stripe 收款/付费套餐/客户 intake
- 核验：aitoolnet 与 hotools 两方转录的官方能力清单与博文完全一致（Multi-Model Agent Fleet 九模型名单、Departmental Coordination、Built-in Company Primitives：Stripe/GitHub/Gmail/Vercel/Docker/matrix.site 域名/Agent 钱包）；另发现博文未提的官方 VPTD（Value per Token-Dollar）经济指标
- 口径差异提示：博文称部门为"调研、工程、创意、增长、安全、运营"，第三方转录为"Research/Product/Growth/Engineering"（研究/产品/增长/工程）——博文部门列举更细（多了创意/安全/运营），以官网实际运行动态组建为准，两者不矛盾（动态组建）
- 结论：**✅ 通过**

### ⚠️ V3：GDPval-Bench 95.45% 与对照数字（覆盖 F-025/F-043）

- 博文口径：GDPval-Bench 95.45%，超过 Codex CLI 的 84.9% 和 Claude Opus 4.7 的 80.3%
- 核验：95.45% 仅见于 aitoolnet 转录的 Matrix 官方文案（"The system achieves 95.45% on GDPval-Bench by providing every model with the operational harness..."），**未找到任何独立第三方评测或榜单可溯源**——属厂商自述
- 对照数字：Codex CLI 84.9% 与第三方评测（danilchenko.dev，2026-06-12）中 GPT-5.5 的 GDPval 84.9% 数值吻合，但无法确认 Matrix 官网对照表的口径与对象；Claude Opus 4.7 GDPval 80.3% 无法独立溯源。**口径风险**：Anthropic 官方 GDPval-AA 采用 Elo 制（Opus 4.6 = 1606，Opus 4.8 = 1890），百分比口径见于第三方评测，两者不可直接混比
- 结论：**⚠️ 厂商自述，对照数字口径无法确认**——正文保留数字但标注"厂商自述 + 口径未验证"

### ⚠️ V4：aivideopro.io 案例数字（覆盖 F-020~F-022/F-044）

- 博文口径：aivideopro.io 全链路（定位/报价页/Stripe 收款/客户 intake），100+ 定制视频，最高短视频 700k+ 播放
- 核验：aitoolnet 转录官方 Use Cases 与博文一致（另含 $3,000+ 收入）；aigjdh 转述"累计产生超过 70 万次真实播放"与 700k+ 吻合。但所有来源最终都指向 Matrix 官方文案，**无独立第三方流量/收入验证**（如 YouTube 频道独立核验未执行成功）
- 结论：**⚠️ 厂商/客户自述**——正文保留数字但标注自述属性
- 注意：作者本人已在博文中对广告服务流程案例作出免责声明（F-023"没法验证具体细节"）

### 仅单源 V5：macOS 桌面应用、Web 端未上线（覆盖 F-018/F-019/F-046）

- 核验：三家第三方工具站均未提及平台形态；未找到独立来源证实或证伪
- 结论：**仅博文单源**——引用时需提示读者以官网为准

### ✅ V6：同名产品排除（覆盖 F-045）

- 核验发现三个同名干扰项，均非本产品：① OpenAI 官网收录的 Hebbia "Matrix"（金融/法律多智能体研究平台）；② GitHub matrix-agent-neo/matrix-core（fork 仓库）；③ NeoLabs-Systems/NeoAgent（自托管开源 Agent）
- 结论：**✅ 通过**——本 bundle 所述 Matrix 特指 matrix.build 的 Agent 公司操作系统

## 勘误

**无勘误项**（0 ❌）。博文未发现源文硬错误；主要风险为成效数字的厂商自述属性，已在正文以 ⚠️ 标注落实，不构成事实性错误。

## 权威信源清单

| 信源 | URL | 用途 |
|------|-----|------|
| AI Toolnet 收录页 | https://www.aitoolnet.com/matrix | 转录 Matrix 官方能力清单/案例/GDPval 宣称 |
| Hotools 收录页 | https://hotools.com/item/matrix | 0-person company 定位、模型列表、收录时间 2026-06-23 |
| AI工具集收录页 | https://aigjdh.com/sites/2669.html | 中文定位描述、70万播放转述 |
| danilchenko.dev GPT-5.5 评测 | https://www.danilchenko.dev/posts/gpt-5-5-review/ | GDPval 84.9% 第三方口径参照 |
| OpenAI × Hebbia 官方页 | https://openai.com/index/hebbia/ | 同名产品排除依据 |
