---
okf_version: "0.2"
type: Example
title: 实操 2——零成本本地组合（Ollama + 本地 ComfyUI）
description: 官方 FAQ 的 0 元方案落地拆解：Ollama 本地 LLM 接入、本地 ComfyUI（127.0.0.1:8188）与 selfhost 工作流对应、Edge/Index-TTS 选择、硬件账单核对与无 GPU 替代组合
tags: [pixelle-video, ollama, comfyui, 本地部署, 零成本, gpu]
generated:
  by: trae-solo-agent
  at: "2026-10-08T20:30:00+08:00"
status: stable
stale_after: "2026-12-31"
sources:
  - id: github
    url: https://github.com/AIDC-AI/Pixelle-Video
  - id: blog
    url: https://mp.weixin.qq.com/s/U1EwSpjYmq4oKrsikWTsIw
---

# 实操 2：零成本本地组合（Ollama + 本地 ComfyUI）

> 本篇对应推文"支持免费本地化部署"（F-009）与官方 FAQ 的"完全免费方案"（F-029）。**官方 FAQ 只给了方案构成（Ollama + 本地 ComfyUI = 0 元）与"本地有显卡"的前提，未提供 Ollama/ComfyUI 本身的部署教程**；本篇对 Pixelle-Video 侧配置逐字依据 README，Ollama/ComfyUI 侧只描述与本项目对接所必需的接口信息，具体安装以两者官方文档为准。本包未真机实测（F-039）。

## 0. 方案构成与硬件前提

| 环节 | 零成本选择 | 运行位置 | 备注 |
|---|---|---|---|
| 文案 LLM | **Ollama** 本地模型 | 本机 | 免 API 费；文案质量取决于所选模型大小 |
| 配图/视频 | **本地 ComfyUI** + selfhost 工作流 | 本机 GPU | FLUX/Qwen/WAN 等权重体积大、推理吃显存 |
| 语音 | Edge-TTS（在线但免费）或 Index-TTS（本地克隆） | 在线 / 本机 GPU | Edge-TTS 不花 API 费但需联网；克隆音色走 Index-TTS 需本地资源 |
| BGM/合成 | 内置 BGM + 本地 FFmpeg | 本机 | 整合包已含 ffmpeg |

官方选择建议原文："**本地有显卡建议完全免费方案，否则推荐使用通义千问**"（F-029）。没有独立 GPU 的机器不要尝试全本地组合——生图/生视频/Index-TTS 都依赖 CUDA 级显卡，CPU 推理不具备可用性。显存需求随工作流上升：图生图类（FLUX/Qwen）与 WAN 视频类差距很大，官方云端路径专门提供 48G 显存机器选项（2026-01-06）即是佐证（F-035）。

## 1. 接入本地 LLM：Ollama

1. 按 Ollama 官方文档安装并启动服务（默认监听本地 `http://localhost:11434`，兼容 OpenAI 接口形态）；
2. 拉取一个你显存能承载的模型（模型名以 `ollama list` 实际为准，Pixelle-Video 不绑定具体模型）；
3. 在 Pixelle-Video「⚙️ 系统配置 → LLM 配置」中：
   - 优先查看预设下拉是否已有 Ollama 项（README 将 Ollama 与 GPT/通义/DeepSeek 并列为支持模型，F-021）；
   - 若无预设则手动配置：API Key 本地服务可任意填（如 `ollama`），Base URL 填 Ollama 的兼容端点，Model 填你拉取的模型名；
4. 保存后先在左侧栏用一个短主题试跑，确认文案能正常返回再继续配置视觉环节。

> 提示：LLM 环节与视觉环节解耦（见 [01 架构篇](../concepts/01-pipeline-and-pluggable-architecture.md)）。本地小模型写分镜脚本质量不足时，可只把 LLM 换成通义千问等低价云端 API（官方"推荐方案"），视觉仍走本地，整体成本依然极低——这比强行用跑不动的本地模型更实际。

## 2. 接入本地 ComfyUI 与 selfhost 工作流

**ComfyUI 是独立前置软件，不在整合包内**，需自行安装、启动并确保其模型权重/自定义节点与工作流匹配：

1. 启动本地 ComfyUI，使其监听 **`http://127.0.0.1:8188`**（Pixelle-Video 的默认地址）；
2. 在「⚙️ 系统配置 → ComfyUI / RunningHub 配置」填该地址，点「**测试连接**」确认可用（F-023）；
3. Pixelle-Video 会扫描 `workflows/selfhost/` 目录，仓库实测自带 8 个本地工作流，按需在视觉/语音下拉中选择（F-023）：

| 工作流文件 | 能力 | 所需 ComfyUI 侧模型（类别） |
|---|---|---|
| `image_flux.json` | FLUX 文生图（默认图像工作流） | FLUX 系列权重 |
| `image_qwen.json` | Qwen 图像生成 | Qwen 图像权重 |
| `image_nano_banana.json` | Nano Banana 图像（2025-12-17 起支持） | 对应模型 |
| `video_wan2.1_fusionx.json` | WAN 2.1 FusionX 图/文生视频 | WAN 2.1 视频权重，显存需求高 |
| `analyse_image.json` / `analyse_video.json` | 图片/视频反推分析（自定义素材用） | VLM 类 |
| `tts_edge.json` | Edge-TTS 语音（在线、免费） | 无需本地模型 |
| `tts_index2.json` | Index-TTS 语音与声音克隆 | Index-TTS 权重（本地 GPU） |

4. 工作流缺模型或缺自定义节点时，错误会从 ComfyUI 端返回——按 ComfyUI 自身机制补齐后重选工作流即可；懂 ComfyUI 的用户也可以把自建 JSON 放进 `workflows/` 目录被自动扫描（F-023）。

首次出片建议从 `tts_edge` + `image_flux`（或你已具备权重的图像工作流）+ `image_default` 竖屏模板开始，**先不要上 `video_*` 模板和 WAN 工作流**——视频生成对显存与调试的要求最高。

## 3. 语音的两个"免费"层次

- **Edge-TTS**：`tts_edge.json`，微软在线语音，**不产生 API 账单但需要联网**，不能克隆任意音色；官方在 2025-12-10 锁定 edge-tts 包版本修复服务不稳定问题，遇到异常先确认版本/整合包为新（F-035）。
- **Index-TTS**：`tts_index2.json`，本地推理、支持上传参考音频克隆声音（F-022），这才是完全离线的语音方案，但需要本地 GPU 与对应权重；克隆音频支持 MP3/WAV/FLAC，可先「预览语音」确认相似度再正式生成。

## 4. 零成本方案的"账单"核对

走完后逐项核对确实为 0 元（F-029）：

- [ ] LLM 请求落在本机 Ollama（系统配置中 Base URL 指向 localhost）；
- [ ] 图像/视频/TTS 工作流全部选自 `selfhost/`（非 runninghub、非 `api/...`）；
- [ ] TTS 用 Edge-TTS（接受联网）或本地 Index-TTS；
- [ ] ComfyUI「测试连接」通过，且生成过程中 ComfyUI 控制台无云端调用；
- [ ] BGM 用内置或本地 `bgm/` 文件。

隐性成本要心里有数：**GPU 硬件购置/电费、ComfyUI 与数 GB～数十 GB 模型权重的下载与维护、排查工作流缺节点的时间**。"零现金成本"不等于"零成本"。

## 5. 无 GPU 的现实替代（别硬装本地方案）

| 你的条件 | 官方建议组合 | 成本形态 |
|---|---|---|
| 有显卡 | Ollama + 本地 ComfyUI | 0 元 API 费（本方案） |
| 有显卡但嫌本地 LLM 慢/差 | 通义千问 + 本地 ComfyUI | LLM API 极低费用 |
| 无显卡 | 云端 LLM + RunningHub（按量），或直连 DashScope/Seedream/Kling API | 持续按用量付费，免本地环境 |

RunningHub 并发限制可配置（2025-12-28），也支持 48G 显存机器（2026-01-06）；直连 API 路径在 2026-06-01 后可完全在 WebUI 内完成供应商配置，无需 ComfyUI（F-023、F-035）。

回到：[安装与首条视频](00-install-and-first-video.md)。
