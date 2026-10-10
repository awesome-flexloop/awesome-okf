---
okf_version: "0.2"
type: bundle
title: "OpenCreator：本地优先的创作者 AI 工作台"
description: "开源（Apache-2.0）本地优先 AI 创作者工作台（原名 KrillinAI）——以 Codex CLI 为 Agent 执行引擎，10 可用 + 2 开发中创作工具（视频翻译/下载、封面/图片/视频生成、写作、小红书、脚本、火柴人、配音），含本地数据纪律（源自公众号「AI开源无界」博文经 GitHub 官方一手核验 18✅/5⚠️/1估）"
tags: [opencreator, krillinai, ai-agent, local-first, codex-cli, video-translation, seedance, tts, content-creation, 博文转化]
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T12:40:00+08:00"
verified:
  - by: process:seven-concepts-v
    at: "2026-10-10T12:40:00+08:00"
status: draft
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator (formerly KrillinAI) README"
  - id: github-api
    url: "https://api.github.com/repos/krillinai/OpenCreator"
    title: "GitHub API 仓库元数据"
  - id: official-home
    url: "https://www.open-creator.ai/en/"
    title: "Open Creator 官方项目主页"
---

# OpenCreator：本地优先的创作者 AI 工作台

> **类型**：技术教程/选型
> **信源**：微信公众号「AI开源无界」博文（原创署名「小知小知」，2026-10-09 发布）→ 2026-10-10 经 GitHub API、官方仓库 README 逐项核验
> **核验结论**：24 项 P0 声明 **18✅ / 5⚠️ / 1❌（Agent token 估算为社区数字）**，无核心硬错误，技术参数高度精准
> **数据时点**：Star 等动态数字为 2026-10-10 GitHub API 快照；功能口径对齐 master 分支
> **状态**：`draft`（尚未经独立评审通过，见 [P0 核验报告](references/verification.md)）

## 本文概要

[OpenCreator](https://github.com/krillinai/OpenCreator)（原名 **KrillinAI**）是跑在**自己电脑上**的开源（**Apache-2.0**）创作者 **AI 工作台**，当前 GitHub Star 12,671（2026-10-10）。它把视频翻译、视频下载、封面/图片/视频生成、文章写作、小红书笔记、短视频脚本、火柴人动画、智能配音等创作日常汇聚到一个应用，数据默认留在本机。它**不自己实现 Agent 循环**，而是直接以 **Codex CLI 为执行引擎**，在其外围提供本地 Runtime、可视化工作台与桌面宿主。

## 阅读路径

**先建立概念（10 分钟）**

1. [OpenCreator 是什么：项目身份与定位](concepts/00-what-is-opencreator.md)——定位、归属、Apache-2.0 许可、热度（带时点）
2. [十个创作工具：多模态创作闭环](concepts/01-ten-creator-tools.md)——视频翻译（14 源/101 目标语言）为老本行，其余工具矩阵
3. [Agent 对话与 Codex 原生架构](concepts/02-agent-and-codex-native.md)——不造轮子的引擎策略、双模式状态机、版本化、记忆

**关键子特性**

4. [数据与安全：本地优先工程纪律](concepts/04-local-data-security.md)——.runtime/SQLite、127.0.0.1+token、凭据存储、yt-dlp 更新治理

**再动手实操**

5. [安装与快速上手](concepts/03-install-quickstart.md) / [实操示例](examples/index.md)——桌面版（自带 Codex，免装 Node）与网页版（Node+pnpm）路径（未实测）

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 归属 | [krillinai/OpenCreator](https://github.com/krillinai/OpenCreator) |
| 前身 / 创建 / 许可 | KrillinAI / 2024-12-17 / **Apache-2.0** |
| 社区数据 | Star 12,671、Fork 1,306、Issues 29、Trendshift 单日 #1（**2026-10-10 快照**） |
| 技术栈 | TypeScript monorepo（pnpm workspace）；模型服务自配 |
| 架构 | 本地 Runtime + 可视化工作台 + 桌面宿主 + Codex CLI 执行引擎 |
| 创作工具 | 10 可用 + 2 开发中（视频翻译/下载、封面/图片/视频生成、文章、小红书、脚本、火柴人、配音；Auto Clips、Digital Avatar） |
| 双模式 | 内容工作台 + Agent 对话，共用状态机、版本化、后台/定时任务、三层记忆 |
| 模型 | 语言：Codex 目录或 OpenAI 兼容（GPT/DeepSeek/Qwen/Kimi/GLM/Grok/豆包/文心/混元/MiniMax）；图像/视频/语音走 AI 服务设置 |
| 数据安全 | 本地优先、密钥系统凭据、日志脱敏、127.0.0.1+t待鉴权 |

## ⚠️ 阅读前已知要点（勘误与补充）

1. **许可**：博文未提，官方为 **Apache-2.0**（宽松，可商用），[F-046](references/facts.md)。
2. **Star 数**：博文「1.2 万」为成文口径，本包采用官方现值 **12,671（2026-10-10）**，动态数字须带时点。
3. **工具数**：博文只提「10 个」，官方另有 2 个 **开发中** 工具（Auto Clips、Digital Avatar）。
4. **语言模型**：博文清单遗漏 **Grok**，本包补充。
5. **Agent token 估算**：博文「单 Agent 任务 10~20 万 token」为**社区估算**，非官方数字，勿据此采信，仅作为「先小任务试水」的合理提醒。
6. **未实测项**：端口 19861、.runtime/SQLite、逐接口 token 等为博文细节，未在本机独立验证。
7. **成本未量化**：本包未提供任何「团队 vs 个人」ROI 或 token 成本量级——官方未公开成本数据，采用前须以社区数字自行估算并在小任务验证（见 [knowledge-map P4](references/knowledge-map.md)）。
8. **功能口径有时点**：「10+2 工具」「14/101 语言」等结构性数字对齐 **master 分支 2026-10-10** 快照；后续版本可能增删工具或语言，引用时须回源核对。

## 采用提示与已知边界

- **适合**：内容创作者、自媒体/多平台分发团队，想少装几个单功能工具、又要本地可控。
- **用过的 KrillinAI 用户**：翻译那套能力都在，无需迁移。
- **代价**：Agent 能力绑定 Codex CLI；模型额度自备、可能消耗较大 token。
- **博文特点**：「整理摘要」性质的第三方 AI 资讯号（AI开源无界），产品能力与命令已官方一手交叉核验；配图内嵌文字未采集。
- **数字时效**：Star/版本为 2026-10-10 快照，`stale_after: 2026-12-31`，到期前复核。

## 信源与可信度

- 事实清单与逐条核验状态：[references/facts.md](references/facts.md)（F-001~F-055）
- P0 核验报告与勘误清单：[references/verification.md](references/verification.md)
- 信源登记与公开性预检：[references/source-manifest.md](references/source-manifest.md)
- 知识地图（事实/机制/迁移三层）：[references/knowledge-map.md](references/knowledge-map.md)

## 主题关联

- [wigolo](../wigolo/index.md)：同为本地优先、local-first 的 Agent 基础设施（Web 情报层）
- [octop](../octop/index.md)：腾讯云开源本地 AI 工作空间（多 Agent 工作平台相邻话题）
- [todesk-ai](../todesk-ai/index.md)：跨设备 AI 助手产品教程（Agent 工具生态相邻话题）
- [loopx](../loopx/index.md)：长程 Agent 控制面（Agent 编排相邻话题）
- [coze](../../ecosystems/coze/index.md)：通过对话定义产品需求的 Agent 平台（多 Agent 生态另一形态）

```{toctree}
:maxdepth: 2
:hidden:

concepts/index
examples/index
references/index
log
```