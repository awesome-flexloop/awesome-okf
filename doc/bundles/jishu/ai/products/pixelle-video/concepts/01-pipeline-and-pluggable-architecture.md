---
okf_version: "0.2"
type: Concept
title: 五步成片流水线与原子能力可插拔架构
description: 官方五步与四阶段两种表述、LLM/图像/视频/TTS 三条供给路径（本地 ComfyUI/RunningHub 云端/直连 API）、25 个 HTML 模板体系、数字人与动作迁移扩展
tags: [pixelle-video, pipeline, comfyui, runninghub, 模板, 数字人]
generated:
  by: trae-solo-agent
  at: "2026-10-08T20:30:00+08:00"
status: stable
stale_after: "2026-12-31"
sources:
  - id: github
    url: https://github.com/AIDC-AI/Pixelle-Video
  - id: docs-site
    url: https://aidc-ai.github.io/Pixelle-Video/zh
  - id: blog
    url: https://mp.weixin.qq.com/s/U1EwSpjYmq4oKrsikWTsIw
---

# 五步成片流水线与可插拔架构

## 一条流水线：五步说法与四阶段说法

推文作者转述的"五件事"与官方首页清单**逐字一致**（F-006、F-020）：

```
输入主题
  → ✍️ 撰写视频文案（LLM）
  → 🎨 生成 AI 配图 / 视频（图像或视频模型）
  → 🗣️ 合成语音解说（TTS，可克隆音色）
  → 🎵 添加背景音乐（内置 BGM 或 bgm/ 自定义）
  → 🎬 一键合成视频（模板 + 字幕 + FFmpeg 合成）
→ 输出 MP4 到 output/
```

官方架构图把同一流程压缩为**四阶段**："文案生成 → 配图规划 → 逐帧处理 → 视频合成"（F-020）。两者不是两套东西：五步是用户可感知的环节，四阶段是工程视角——"配图规划"承接文案输出结构化分镜（解说词、英文图像提示词、时长估算），"逐帧处理"把每句旁白对应的图/视频与语音逐分镜产出，最后统一合成。

README 自述生成时长"通常几分钟内完成"，取决于分镜数量、网络状况与 AI 推理速度（F-034）。

## 核心设计：每个环节都是可替换的"原子能力"

Pixelle-Video 自己不训练大模型，它的工程价值在于**编排**：通过 ComfyKit 抽象层把文案、图像、视频、TTS、VLM（素材分析）封装成可插拔能力，换模型只需改配置指向不同工作流/供应商，不动源码（F-023）。同一条流水线有三条能力供给路径：

| 路径 | 配置 | 适合谁 | 实测工作流/供应商 |
|---|---|---|---|
| **① 本地 ComfyUI**（默认） | 填本地 ComfyUI URL，默认 `http://127.0.0.1:8188` | 有 GPU、想零 API 成本 | `workflows/selfhost/` 8 个 JSON：image_flux、image_nano_banana、image_qwen、video_wan2.1_fusionx、analyse_image、analyse_video、tts_edge、tts_index2（F-023） |
| **② RunningHub 云端** | 填 RunningHub API Key | 无本地显卡、按量付费 | `workflows/runninghub/` 21 个 JSON：除上述外还有数字人三件套（digital_combination/customize/image）、LTX2、Z-image、sd3.5、sdxl、wan2.2 系列、tts_spark、视频理解等（F-023） |
| **③ 直连模型 API** | WebUI 内填各供应商 Key/Base URL/代理 | 不想部署 ComfyUI | DashScope/Wan/HappyHorse、OpenAI GPT Image、火山 ARK（Seedream 图/Seedance 视频）、Kling 可灵；选 `api/...` 工作流时启用（F-023） |

直连 API 的 WebUI 配置是 **2026-06-01** 才加入的较新能力（README 最新更新条目），支持每个供应商单独开关本地代理、打印请求参数用于调试；API 视频片段会尽量按旁白音频时长生成，并用相邻片段信息提升连贯性，内容审核失败时还有提示词中性化重试（F-023、F-035）。

**LLM 环节**与视觉环节解耦：GPT、通义千问、DeepSeek、Ollama 均可，WebUI 预设下拉自动填充 base_url 和 model，也可手动指定——推文作者用 DeepSeek 正是这一步（F-021）。

## TTS 与声音克隆

- 基础配音用 **Edge-TTS**（pyproject 中 `edge-tts==7.2.7` 锁版本，曾因 TTS 服务不稳定专门锁定，F-030、F-035）；高质量/克隆用 **Index-TTS**，云端另有讯飞 tts_spark。
- **克隆声音**的操作是上传参考音频（MP3/WAV/FLAC 等），适用于 Index-TTS 类工作流，上传后可直接试听，也能用参考音频做语音预览；2026-01-14 起新增多语言 TTS 音色（官方示例中有韩语数字人口播）（F-022、F-027）。

## 模板体系：static / image / video 三类 × 三种画幅

模板决定成片的**画面布局与设计**（不是生成模型本身），是纯 HTML/CSS 文件，懂 HTML 可以自建（F-024）：

- **命名规范**：`static_*.html`（纯文字静态画面，不用 AI 生成媒体）、`image_*.html`（以 AI 生成图片为背景）、`video_*.html`（以 AI 生成视频片段为背景）。
- **尺寸分组**：`templates/1080x1920`（竖屏 9:16，抖音/视频号/小红书）、`1920x1080`（横屏 16:9，B 站/公众号视频）、`1080x1080`（方形 1:1）。
- **数量实测**：仅竖屏目录就有 **25 个 HTML 模板**——从 default、book、cartoon、elegant、fashion_vintage、healing、neon、purple 到 simple_black、satirical_cartoon、long_text、psychology_card 等风格化模板，覆盖推文所说的卡通、心理、养生、情感等品类。
- 模板可在 WebUI 预览参数后选择，官方文档站有全部模板效果图册（F-024、F-036）。

这正是推文"你能看到的短视频类型基本都能套模板出草稿"的实际所指——需要注意该说法是作者的**营销式概括**（F-008）：模板覆盖的是口播/图文/轻视频这类版式，不等于任何镜头语言都能生成。

## 扩展模块时间线（2025-11 → 2026-06）

| 时间 | 能力 | 对应帖文 |
|---|---|---|
| 2025-11-18 | 批量创建视频任务、RunningHub 并行、历史记录页 | "批量生产模式"（F-012） |
| 2025-12-04 | **自定义素材**：上传自有照片/视频，AI 分析生成脚本 | "自定素材"（F-011） |
| 2025-12-05 | Windows 一键整合包首版 | 安装路径 |
| 2025-12-17 | ComfyUI API Key、Nano Banana 模型 | — |
| 2026-01-06 | RunningHub 48G 显存机器调用 | — |
| 2026-01-14 | **数字人口播** + 图生视频流水线 + 多语言 TTS | "数字人口播"（F-011） |
| 2026-01-26 | **动作迁移**：参考视频 + 图片迁移动作（如跳舞小猫） | 帖文未提 |
| 2026-06-01 | 直连 API 媒体模型在 WebUI 可视化配置 | 帖文未提 |

（F-026、F-027、F-035）

## 技术栈速览

main 分支 pyproject.toml 实测（F-030）：Streamlit（三栏 WebUI，端口 8501）+ moviepy 1.0.3 / ffmpeg-python（合成）+ edge-tts + dashscope + comfykit（ComfyUI 工作流封装）+ playwright（模板渲染截图）+ **fastmcp**（项目同时提供 MCP 服务能力）+ FastAPI/uvicorn（API 模式）+ pydantic/loguru。Python >=3.11，Apache-2.0。

## 延伸阅读

- [00 定位与身份核验](00-identity-and-positioning.md)——帖文未点名的推断过程、组织更名、star 快照
- [02 使用模式、成本边界与适用判断](02-usage-modes-and-boundaries.md)——三种内容模式、免费的 GPU 前提、平台限流
- [实操 1：安装与首条视频](../examples/00-install-and-first-video.md)
