---
okf_version: "0.2"
type: Reference
title: 推文事实清单——《【134期】阿里居然把它开源了！》
description: 公众号「赛博煎蛋」2026-09-25 截图型推荐短帖的 F 编号事实登记（【博】页面事实/作者主张与【官】核验补充分层，F-001~F-040 连续）
tags: [pixelle-video, 事实登记, 微信推文, ai视频, 短视频生成]
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

# 推文事实清单（article-source）

> 本文件是 F 编号事实的 bundle 侧登记。【博】= 推文事实（页面事实 page_fact 或作者主张 author_claim，观点条目标注「作者观点」）；【官】= 核验阶段从官方源（GitHub API、官方 README、pyproject.toml、仓库目录清单）补充的事实。编号 **F-001 ~ F-040，连续无跳号**。
>
> ⚠️ **特别说明**：原帖是**截图驱动的推荐短帖**（正文仅 478 字符、20 行，操作细节全部在截图中），且**全文未点名项目、未给仓库地址**。项目身份 Pixelle-Video 为核验者据特征推断（F-015，flagged）。

## A. 信源元信息（页面事实）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-001 | 标题《【134期】阿里居然把它开源了！》；公众号「赛博煎蛋」；作者署名「赛博煎蛋」；发布时间 2026-09-25 23:25:07（页面 ct 时间戳 1790349907）；期号第 134 期 | 【博】 | ✅ 页面元信息 |
| F-002 | 文章 URL：https://mp.weixin.qq.com/s/U1EwSpjYmq4oKrsikWTsIw ；正文纯文字仅 **478 字符 / 20 行**，内容形态为"短配文 + 多张操作截图"的资源推荐帖 | 【博】 | ✅ 抓取提取 |
| F-003 | 全文**未出现项目名称与仓库地址**；结尾引导"关注下方公众号，点私信自动获取"（私信关键词领取资源位），属引流式结尾而非公开链接 | 【博】 | ✅ |
| F-004 | 文末打赏声明（页面事实）：账号自述"只打算做纯粹的分享，不接广告、不带货"，靠读者打赏维持运营 | 【博】 | P2 单源（号主自述） |

## B. 作者主张（帖内功能描述，含观点分层）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-005 | 作者称该项目为"**阿里开源的 AI 自动剪辑项目**，GitHub 上已经获得 **28.4k star**" | 【博】作者主张 | ✅ star 量级一致（F-017）；归属见 F-018 |
| F-006 | 核心用法："你输一个主题进去"，它自动做五件事——**写文案、生成配图、合成语音、配背景音乐、合成视频**，"出来就是一条能发的成片" | 【博】作者主张 | ✅ 官方五步逐字对应（F-020） |
| F-007 | 作者列举可做类型：**数字人口播、卡通视频、小说推文、个人成长、知识科普**，"同时还支持横屏视频" | 【博】作者主张 | ✅ 官方示例区逐一覆盖（F-024/F-027） |
| F-008 | 作者称"你能看到的短视频类型基本都能套模板出草稿" | 【博】作者观点（含夸张） | P2：模板覆盖面有官方清单支撑，但"基本都能"为营销式概括 |
| F-009 | 作者称"最关键的是它还支持**免费本地化部署**，不管你是想做什么视频，都会节省很多时间" | 【博】作者观点（含成效判断） | ✅ 免费路径成立但有 GPU 门槛（F-029，需补注） |
| F-010 | 初次使用"先添加 API"，作者本人用的是 **DeepSeek**，读者"选择自己的就行了" | 【博】作者实测 | ✅ DeepSeek 在官方支持 LLM 之列（F-021） |
| F-011 | "模式可以选择**快速创作、自定素材、数字人口播**等" | 【博】作者实测 | ⚠️ 名称为近似转述，官方模式命名不同（F-032） |
| F-012 | "有批量的需求这里可以选择**批量生产模式**" | 【博】作者实测 | ✅ 官方 2025-11-18 起支持批量创建任务（F-026） |
| F-013 | "选好配音，**也可以克隆声音**"；随后"选好分镜模板 → 最后直接生产视频" | 【博】作者实测 | ✅ Index-TTS 声音克隆 + 模板体系（F-022/F-024） |
| F-014 | 作者总评："这个是真不错，可以收藏一下" | 【博】作者观点 | P2 单源评价 |

## C. 项目身份与归属（核验补充）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-015 | **身份推断（flagged）**：原帖未点名，核验者据"①阿里开源 ②28.4k star ③输入主题自动完成文案/配图/语音/BGM/合成五步 ④数字人口播、声音克隆、分镜模板、批量、免费本地部署"特征簇唯一匹配到 **Pixelle-Video**，置信度高；推断风险：截图未随帖留存为文字证据，存在同名/仿冒工具的理论可能 | 【官】交叉推断 | flagged，见 verification.md 第 2 节 |
| F-016 | API 规范名为 **`ATH-MaaS/Pixelle-Video`**：GitHub 组织 **AIDC-AI 已整体迁移/重命名为 ATH-MaaS**（Organization 账号，2024-06-13 创建）；旧地址 `github.com/AIDC-AI/Pixelle-Video` 仍可访问（自动重定向），官方 README/文档站内链接仍普遍使用 AIDC-AI 旧名；同组织 Pixelle-MCP、ComfyUI-Copilot 也已迁移到 ATH-MaaS | 【官】GitHub API | ✅ |
| F-017 | GitHub API 实测（2026-10-08）：star **28,745**、fork **4,178**；许可证 **Apache-2.0**；主语言 Python；仓库创建于 **2025-11-07**；最近 push 2026-06-14；描述"🚀 AI 全自动短视频引擎"；homepage 指向官方文档站 | 【官】GitHub API | ✅ 帖子"28.4k"为四舍五入口径，与 28,745 一致 |
| F-018 | **团队归属**：多篇独立第三方报道（2026-05~06，稀土掘金/什么值得买/头条技术号/besthub）一致称 Pixelle-Video 由**阿里巴巴国际数字商业集团 AIDC-AI 团队**开源；README「系列工作」列出 HITsz-TMG 合作论文（SIGGRAPH Asia 2024 FilmAgent、Anim-Director，ACL 2025 ComfyUI-Copilot 等）。注意：GitHub 组织页本身未自报公司全称，"阿里"属强旁证而非仓库自述 | 【官】README + 第三方多源 | ✅（间接证据，多源一致） |
| F-019 | 版本：GitHub Releases 最新为 **v0.1.15（2026-01-27）**，各 release 均以"Windows 一键整合包"形式发布（v0.1.10 起，2025-12-10）；main 分支 pyproject.toml 版本号已到 **0.2.0**（声明 "Part of Pixelle ecosystem"，作者署名 Pixelle.AI）但**尚未对应正式 release**；`requires-python >=3.11` | 【官】GitHub API + pyproject.toml | ✅ |

## D. 架构与功能（核验补充）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-020 | 官方五步与帖文逐字对应：✍️撰写视频文案 → 🎨生成 AI 配图/视频 → 🗣️合成语音解说 → 🎵添加背景音乐 → 🎬一键合成视频；README 架构图另以**四阶段**概括：文案生成 → 配图规划 → 逐帧处理 → 视频合成 | 【官】README | ✅ |
| F-021 | LLM 支持 **GPT、通义千问、DeepSeek、Ollama** 等；WebUI 提供预设下拉（自动填充 base_url/model）与手动配置两种方式 | 【官】README | ✅ |
| F-022 | TTS 支持 **Edge-TTS、Index-TTS** 等（云端工作流另含 tts_spark）；**声音克隆**通过上传参考音频（MP3/WAV/FLAC 等，适用于 Index-TTS 类工作流）实现，可直接试听；2026-01-14 起新增多语言 TTS 音色 | 【官】README + workflows 清单 | ✅ |
| F-023 | 视觉/语音能力有**三条供给路径**：①本地 **ComfyUI**（默认地址 `http://127.0.0.1:8188`，`workflows/selfhost/` 实测 8 个 JSON：image_flux/nano_banana/qwen、video_wan2.1_fusionx、analyse_image/video、tts_edge/index2）；②云端 **RunningHub**（`workflows/runninghub/` 实测 21 个 JSON，含数字人 digital_combination/customize/image、LTX2、Z-image、sd3.5/sdxl、tts_spark 等）；③**直连模型 API**（DashScope/Wan/HappyHorse、OpenAI GPT Image、火山 ARK Seedream/Seedance、Kling），2026-06-01 起可在 WebUI 配置供应商 Key/Base URL/代理 | 【官】README + 目录清单 | ✅ |
| F-024 | 模板体系：`templates/` 下按尺寸分三目录——**1080x1920 竖屏、1920x1080 横屏、1080x1080 方形**；竖屏目录实测含 **25 个 HTML 模板**；命名规范 `static_*.html`（纯文字静态）/`image_*.html`（AI 图背景）/`video_*.html`（AI 视频背景）；可在文档站查看全部模板效果图，懂 HTML 可自建 | 【官】仓库目录清单 + README | ✅ |
| F-025 | 内容输入官方为两种模式：**AI 生成内容**（输入主题，AI 写稿）与**固定文案内容**（直接给完整文案，支持按段落/行/句子分割，2025-12-08）；另有「**自定义素材**」功能（2025-12-04）：上传自有照片/视频，AI 智能分析后生成脚本 | 【官】README | ✅ |
| F-026 | **批量**：2025-11-18 起支持批量创建视频任务、RunningHub 并行处理与历史记录页面 | 【官】README | ✅ |
| F-027 | 扩展模块：**数字人口播**与图生视频流水线（2026-01-14，v0.1.12）、**动作迁移**（上传参考视频+图片，2026-01-26，v0.1.14）；RunningHub 48G 显存机器调用（2026-01-06） | 【官】README + releases | ✅ |
| F-028 | 安装与运行：Windows 推荐**一键整合包**（releases 下载解压 → 双击 `start.bat` → 浏览器自动开 `http://localhost:8501`，已含 Python/ffmpeg 全部依赖）；macOS/Linux 源码安装需先备 **uv 与 ffmpeg**，再 `git clone` 后 `uv run streamlit run web/app.py`；成片保存在 `output/`，自定义 BGM 放 `bgm/`（MP3/WAV） | 【官】README | ✅ |
| F-029 | 费用三方案（官方 FAQ 原文口径）：**完全免费** = Ollama 本地 LLM + ComfyUI 本地部署 = 0 元（前提：本地有显卡/GPU）；**推荐** = 通义千问 + 本地 ComfyUI（成本极低）；**云端** = OpenAI + RunningHub（较贵但免本地环境） | 【官】README | ✅（帖子"免费"需补 GPU 门槛注） |
| F-030 | 技术栈（main 分支 pyproject 实测）：Streamlit WebUI、moviepy 1.0.3 + ffmpeg-python 视频合成、edge-tts 7.2.7 锁定、dashscope、comfykit、playwright、fastmcp（MCP 服务能力）、pydantic/loguru 等；输出竖屏 9:16 / 横屏 16:9 / 方形 1:1 的 MP4 | 【官】pyproject.toml + README | ✅ |

## E. 生态辨析与时效

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-031 | **同名辨析**：官方 README「参考项目」列出 `harry0703/MoneyPrinterTurbo`（"优秀的视频生成工具"，**个人项目、非阿里开源**）、NarratoAI、MoneyPrinterPlus、Pixelle-MCP（同组织 ComfyUI MCP 服务器）、ComfyKit——Pixelle-Video 与 MoneyPrinterTurbo 是**不同项目**，仅功能相似、名称风格相近，检索时勿混 | 【官】README | ✅ |
| F-032 | 帖子"快速创作 / 自定素材 / 数字人口播"与官方界面用词对照（**flagged 近似**）：快速创作 ≈「AI 生成内容」模式；自定素材 ≈「自定义素材」功能（2025-12-04）；数字人口播为官方同名扩展模块（2026-01-14）。此外官方另有「固定文案内容」模式帖文未提 | 【官】README 对照 | ⚠️ 近似对应，非逐字 |
| F-033 | Apache-2.0 许可证允许商用与二次开发（LICENSE 授权条款；多篇报道转述"免费商用"） | 【官】LICENSE + 第三方 | ✅ |
| F-034 | README 自述生成时长"通常几分钟内完成"，取决于分镜数量、网络与推理速度；效果不满意的四条调优路径：换 LLM、调图像尺寸/提示词前缀、换 TTS 或参考音频、换模板/尺寸 | 【官】README | ✅ |
| F-035 | 官方更新时间线（README「最近更新」）：2025-11-18 批量任务 → 12-04 自定义素材 → 12-05 Windows 整合包 → 12-17 Nano Banana/ComfyUI API Key → 12-28 RunningHub 并发可配 → 2026-01-06 48G 显存 → 01-14 数字人/图生视频/多语言 TTS → 01-26 动作迁移 → **06-01 直连 API 媒体模型 WebUI 配置**（核验时 README 最新条目） | 【官】README | ✅ |
| F-036 | 官方文档站 `https://aidc-ai.github.io/Pixelle-Video/zh`（含模板效果图与用户指南）；社区渠道为微信群 + Discord；视频教程发布于 B 站 | 【官】README | ✅ |

## F. 核验方法与信源边界

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-037 | 原帖为公开图文（无验证码/token/邀请码），判定为**公开内容**，按标准工作流入 bundles；微信正文经 PowerShell 带 Chrome UA 请求取得完整 HTML 后提取（WebFetch 对 mp.weixin.qq.com 不可用） | 【官】核验记录 | ✅ |
| F-038 | 官方 README 经 GitHub API `repos/AIDC-AI/Pixelle-Video/readme`（Accept: raw）取得中文版全文（约 1.4 万字符）；仓库元数据、releases、templates/workflows 目录清单、pyproject.toml 均经 GitHub REST API/Contents API 实测 | 【官】核验记录 | ✅ |
| F-039 | **未真机安装运行**：examples 各步骤依据官方 README 逐字比对整理，非本包制作中的实测；帖子本身只有操作截图配文、无任何命令行或配置细节，故实操篇事实来源为官方文档而非帖主实测，引用时须区分 | 【官】核验记录 | 方法边界 |
| F-040 | 第三方热度旁证（**非帖子内容，仅作增长曲线，不采信其成效数字**）：脚本之家 2026-08-26 报 7.6k、掘金 05-09 报 11.4k、什么值得买 05-20 报 11.6k、besthub 06-15 报 22k、头条技术号 09 月报 27.4k~27.6k → 与核验日 28,745 共同构成快速增长曲线；第三方文章中"日更 5 条/成本 2500→5 元"等营销成效数字为无具名来源的聚合说法，**不登记为事实、不进入教程正文** | 【官】核验记录 | 已隔离 |
