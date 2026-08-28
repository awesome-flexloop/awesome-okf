---
type: Concept
title: 项目概述与定位
description: Qwen-UI-Agent开源发布背景、GUI智能体定位、与MAI-UI的版本关系、四类能力覆盖、官方副标题
tags: [Qwen-UI-Agent, MAI-UI, GUI智能体, 开源, 阿里通义, 项目概述]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:45:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-renjianpanghuang
    resource: https://mp.weixin.qq.com/s/krPGm4HWX_uJwjQtWIRNCA
    title: 《阿里刚开源的 Qwen-UI-Agent》（人间彷徨，2026-08-26）
  - id: arxiv-2607-28227
    resource: https://arxiv.org/abs/2607.28227
    title: arXiv 2607.28227 官方技术报告
  - id: official-project-page
    resource: https://tongyi-mai.github.io/Qwen-UI-Agent/
    title: Qwen-UI-Agent官方项目主页
---

# 项目概述与定位

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。

## 1. 开源发布

2026 年 8 月 20 日，阿里通义（Alibaba Tongyi Lab）正式开源发布 **Qwen-UI-Agent** 项目（F-002）。arXiv 技术报告（2607.28227）于 7 月 30 日提交，GitHub 仓库同日重组，8 月 20 日为对外公开发布日（F-044）。

- **官方项目主页**：https://tongyi-mai.github.io/Qwen-UI-Agent/（F-035）
- **GitHub 仓库**：https://github.com/Tongyi-MAI/MAI-UI（F-014，Apache 2.0 协议）
- **arXiv 论文**：https://arxiv.org/abs/2607.28227（F-036）

## 2. 产品定位：GUI 智能体而非聊天机器人

Qwen-UI-Agent 的核心定位是**数字设备上的通用执行器**（general purpose executor over existing digital devices），而非聊天机器人（F-003、F-040）：

- **看屏幕**：感知应用界面状态（perceive application states）
- **点按钮/填表单**：理解用户意图后直接操作界面（understand user intent, operate interfaces）
- **跨设备**：覆盖手机 GUI、电脑操作、网页浏览器、深度搜索四类环境（F-039）

官方副标题为"Towards Next-Generation Real-World Centric Foundation GUI Agent"（面向下一代真实世界中心的基础 GUI 智能体）（F-040）。

博文举例说明其使用方式（F-004）：

> "帮我在 12306 查最早到杭州的高铁，再算下到公司要多久，最后在钉钉建个会"

Qwen-UI-Agent 会自己打开 App、一步步点完，全程无需用户手动操作。这与传统 RPA（机器人流程自动化）的区别在于：RPA 需要预先录制脚本，界面一变就崩；GUI 智能体能像人一样实时感知界面并决策。

## 3. MAI-UI 与 Qwen-UI-Agent 的版本关系

> ⚠️ **重要勘误（F-032/F-042）**：博文将 MAI-UI-2B/8B 权重描述为 Qwen-UI-Agent 的权重，这是**混淆了两代产品**。

arXiv 论文脚注明确写道：

> "Qwen-UI-Agent is a continuation of our previous work, MAI-UI."

| 版本 | 时间 | 模型规格 | 权重状态 |
|------|------|---------|---------|
| **MAI-UI 1.0** | 2025-12-29 | 2B / 8B（基于 Qwen3-VL） | ✅ 已在 HuggingFace 发布（Apache 2.0） |
| **Qwen-UI-Agent** | 2026-08-20 | 基于 Qwen 3.5 系列，据媒体报道 4B/27B/35B-A3B（主力 27B） | ⚠️ **截至 2026-08-28 权重尚未公开发布** |

GitHub 仓库 `Tongyi-MAI/MAI-UI` 同时包含两个子目录（F-041）：
- `MAI-UI/`：1.0 版代码和权重引用
- `Qwen-UI-Agent/`：新版代码框架（目前仅 README、assets 和技术报告 PDF，无安装文档）

**这意味着**：博文标题称"开源"，代码框架确实 Apache 2.0 开源，但 Qwen-UI-Agent 自身模型权重尚未放出。目前可从 HuggingFace 下载的 MAI-UI-2B/8B 是前代模型，性能不等于 Qwen-UI-Agent。引用博文"权重开源了"的说法时须注意这一区分。

## 4. 四类能力覆盖

根据官方项目主页和技术报告，Qwen-UI-Agent 能力覆盖四类环境（F-039）：

| 能力 | 说明 |
|------|------|
| **Mobile GUI Use** | 操作手机 App（Android 为主） |
| **Computer Use** | 操作电脑桌面应用 |
| **Browser Use** | 操作网页浏览器 |
| **DeepSearch** | 深度搜索与信息整合 |

博文指出，"会操作界面的 AI 不是新概念，但大多数要么在模拟器里成绩好看、一上真机就翻车，要么只能调有接口的软件"（F-005）。Qwen-UI-Agent 的差异化在于真机训练而非模拟器，以及不依赖 API 直接操作 GUI。

## 5. 开源意义

博文作者认为（F-029~F-031）：屏幕是数字世界最通用的入口，过去 AI 只能调有 API 的软件，大量老系统、老界面成了盲区；Qwen-UI-Agent 这类"会自己点屏幕"的模型开源，使重复枯燥的点屏活儿第一次有了被自动化替代的可能。

代码开源（Apache 2.0）意味着可以自部署，数据不出本地环境——这对隐私敏感场景（如财务、客服系统）尤其重要（F-015）。但需注意：**Qwen-UI-Agent 自身权重尚未发布**，目前自部署只能使用前代 MAI-UI 模型。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- 技术能力与基准成绩：[01-capabilities-benchmarks.md](01-capabilities-benchmarks.md)
