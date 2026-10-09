---
okf_version: "0.2"
type: Concept
title: Pixelle-Video 是什么——帖文身份核验、阿里归属与热度快照
description: 从一篇不点名的微信推荐短帖核验出 Pixelle-Video 的完整过程、AIDC-AI→ATH-MaaS 组织迁移、28.7k star 时效快照、与 MoneyPrinterTurbo 的同名辨析
tags: [pixelle-video, 身份核验, flagged, 阿里AIDC, apache-2.0]
generated:
  by: trae-solo-agent
  at: "2026-10-08T20:30:00+08:00"
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/U1EwSpjYmq4oKrsikWTsIw
  - id: github
    url: https://github.com/AIDC-AI/Pixelle-Video
  - id: github-api
    url: https://api.github.com/repos/AIDC-AI/Pixelle-Video
  - id: docs-site
    url: https://aidc-ai.github.io/Pixelle-Video/zh
---

# Pixelle-Video 是什么——身份核验、归属与热度

> 本篇所有结论基于公众号「赛博煎蛋」第 134 期推文（2026-09-25）与官方源的交叉核验（核验日 2026-10-08）。完整推断链见 [verification.md](../references/verification.md)。

## 一句话定位

**Pixelle-Video 是一款开源的 AI 全自动短视频引擎**：输入一个主题，系统自动完成文案撰写、AI 配图/视频生成、语音解说合成、背景音乐添加到最终视频合成的全链路，输出可直接发布的成片（F-006、F-020）。官方中文标语为"只需输入一个**主题**……零门槛，零剪辑经验"，英文描述为 "AI Fully Automated Short Video Engine"（F-017）。

## 先读：本知识包的身份风险（flagged）

源推文是一篇典型的**截图驱动型资源推荐短帖**——正文仅 478 字、20 行，操作过程全部在截图里，并且有两个关键缺失（F-002、F-003）：

1. **全文没有点名项目**，没有任何一处出现 "Pixelle-Video"；
2. **没有给仓库地址**，结尾是"关注公众号，点私信自动获取"的引流式引导。

因此"推文所指 = Pixelle-Video"是核验者的**推断结论而非帖文明示**。推断依据是五个特征的唯一合取：阿里开源 + 28.4k star + 输入主题五步成片 + 数字人口播/声音克隆/分镜模板/批量 + 免费本地部署，GitHub 上仅此一个项目同时满足；功能相似的 MoneyPrinterTurbo 是个人项目、组织与量级均不符（F-015、F-031）。该推断定级 **flagged（高置信）**，若你在别处引用本帖，请保留"帖文未点名"这一前提。

> 原帖的这种形态也决定了本包的证据结构：帖文只提供**功能存在性**证据，所有安装、配置、架构细节均来自官方 README 与仓库实测，实操篇会逐处区分来源（F-039）。

## 归属：阿里 AIDC-AI 团队（组织已更名 ATH-MaaS）

- 推文称其为"**阿里开源**"项目（F-005）。GitHub 组织页本身未自报公司全称，但多家独立技术媒体（2026 年 5–6 月）一致表述为"**阿里巴巴国际数字商业集团 AIDC-AI 团队**开源"，README 的「系列工作」也列出与哈工大（深圳）HITsz-TMG 团队合作的 SIGGRAPH Asia 2024/ACL 2025 论文（FilmAgent、Anim-Director、ComfyUI-Copilot 等），归属有强旁证（F-018）。
- **组织迁移是最容易踩的引用坑**：GitHub API 中的规范名已是 `ATH-MaaS/Pixelle-Video`，原 `AIDC-AI` 组织整体迁移到了 **ATH-MaaS**（Organization 账号，2024-06-13 创建）；同组织的 Pixelle-MCP、ComfyUI-Copilot 同样已迁移。旧地址 `github.com/AIDC-AI/Pixelle-Video` 仍自动重定向、可正常访问，且官方 README、文档站、Release 资产链接**至今仍普遍写旧名**（F-016）。两个地址等价，但严谨写法是"AIDC-AI 团队（GitHub 组织现名 ATH-MaaS）"。

## 基本盘（核验时点 2026-10-08，均为快照）

| 指标 | 值 | 出处 |
|---|---|---|
| API 规范名 | `ATH-MaaS/Pixelle-Video`（旧名 `AIDC-AI/Pixelle-Video` 可重定向） | GitHub API（F-016） |
| Star / Fork | **28,745 / 4,178** | GitHub API（F-017）；推文"28.4k"✅ |
| 许可证 | **Apache-2.0**（允许商用、二次开发） | GitHub API / LICENSE（F-017、F-033） |
| 主语言 / 运行时 | Python；`requires-python >=3.11`；WebUI 为 Streamlit | pyproject.toml（F-030） |
| 创建时间 | 2025-11-07；最近 push 2026-06-14 | GitHub API（F-017） |
| 最新 Release | **v0.1.15（2026-01-27）**，均为 Windows 一键整合包 | GitHub Releases（F-019） |
| main 分支版本 | pyproject 已标 **0.2.0**（"Part of Pixelle ecosystem"），尚未正式发版 | pyproject.toml（F-019） |
| 官方文档 | aidc-ai.github.io/Pixelle-Video/zh；社区为微信群 + Discord | README（F-036） |

**热度数字务必带时点引用**：第三方报道拼出一条整体陡峭但个别口径异常的曲线——11.4k（2026-05-09）→ 11.6k（05-20）→ 22k（06-15）→ 27.4k~27.6k（09 月）→ **28,745（10-08 实测）**（F-040）。注：脚本之家 2026-08-26 一文称 7.6k，与前后时点矛盾，疑为旧数据或笔误，不作为趋势依据。该项目 2025 年 11 月创建，约一年内冲到近 2.9 万 star。

> 第三方文章里的"日更 5 条、成本从 2500 元降到 5 元、月费 69 元"等成效/价格数字均无具名来源，本知识包**不采信、不转述**（F-040）。

## 它在"AI 视频工厂"工具谱系中的位置

2026 年出现了一批"一句话生成短视频"的开源工具，Pixelle-Video 的差异化坐标是：

- **流水线派，而非智能体剧组派**：Pixelle-Video 把 LLM、ComfyUI 工作流、TTS、FFmpeg 串成一条**固定的自动化流水线**（文案→配图规划→逐帧处理→视频合成），主打几十秒到几分钟的口播/科普/图文轮播短平快内容；同类报道常把它与哈工大（深圳）的 VideoClaw（多智能体"剧组"、场记状态库、主攻长视频/连续短剧）对照，两者覆盖不同时长段（F-020）。
- **原子能力可插拔**：图像、视频、TTS、VLM 每个环节都是独立工作流或 API 供应商，可替换而无需改源码（详见 [01 流水线与可插拔架构](01-pipeline-and-pluggable-architecture.md)）。

### 同名辨析：别和 MoneyPrinterTurbo 搞混

官方 README 的「参考项目」首列 `harry0703/MoneyPrinterTurbo`，称其为"优秀的视频生成工具"（F-031）：

| | **Pixelle-Video** | MoneyPrinterTurbo |
|---|---|---|
| 归属 | 阿里国际 AIDC-AI 团队（ATH-MaaS 组织） | 个人开发者 harry0703，**非阿里项目** |
| 关系 | 受其启发的**独立项目**，README 明确鸣谢 | 被参考的前身之一 |
| 检索提示 | 名字都含"视频/钱"隐喻，功能高度相似，搜"阿里 自动剪视频"时两个仓库常同时出现 | — |

README 同时列出 NarratoAI（影视解说）、MoneyPrinterPlus（视频创作平台）、同组织的 Pixelle-MCP（ComfyUI MCP 服务器）与 ComfyKit（工作流封装库），均为不同项目（F-031）。

## 延伸阅读

- [01 流水线与可插拔架构](01-pipeline-and-pluggable-architecture.md)——官方五步 vs 四阶段、三条能力供给路径、模板体系与数字人扩展
- [02 使用模式、成本边界与适用判断](02-usage-modes-and-boundaries.md)——双内容模式/自定义素材/批量、"免费"的 GPU 前提、平台限流风险
- [verification.md](../references/verification.md)——13 项 P0 核验与身份推断链完整记录
