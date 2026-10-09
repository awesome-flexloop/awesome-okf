---
okf_version: "0.2"
type: Example
title: 实操 1——安装 Pixelle-Video 并生成第一条视频
description: Windows 一键整合包与 macOS/Linux uv 源码两条安装路径、首次系统配置（LLM/ComfyUI或RunningHub/直连API）、三栏 WebUI 出片全流程与 output 产物
tags: [pixelle-video, 安装, streamlit, 整合包, 快速开始]
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

# 实操 1：安装 Pixelle-Video 并生成第一条视频

> **来源声明**：源推文只有操作截图配文（"先添加 API → 选模式 → 选配音 → 选分镜模板 → 生产视频"），不含任何命令行细节（F-010~F-013）。本篇安装与配置步骤来自**官方 README 逐字比对**，本知识包制作中**未真机执行**，实际以官方 Getting Started 与你本机环境为准（F-039）。

## 0. 先想清楚走哪条路径

安装本体之前，先确定"画面和语音由谁生成"，这决定后续配置量（F-023、F-029）：

- 有 NVIDIA GPU、愿意部署 ComfyUI → 本地路径，配好后可以 0 API 成本；
- 没有 GPU → RunningHub 云端工作流（按量付费）或直连模型 API（DashScope/Seedream/Kling 等），无需 ComfyUI；
- 两条路径可以混用：比如 LLM 用 DeepSeek 云端、图像用 RunningHub、TTS 用 Edge-TTS（免费在线）。

## 1. 安装本体（二选一）

### 路径 A：Windows 一键整合包（官方推荐 Windows 用户）

无需安装 Python、uv 或 ffmpeg，整合包已含全部依赖（F-028）：

1. 到 Releases 页下载最新 **Windows 一键整合包**（最新 release 为 v0.1.15，2026-01-27）：`https://github.com/AIDC-AI/Pixelle-Video/releases/latest`；
2. 解压后双击运行 **`start.bat`**；
3. 浏览器自动打开 **`http://localhost:8501`**；
4. 在「⚙️ 系统配置」中填入 API（见第 2 节），即可开始。

### 路径 B：源码安装（macOS / Linux / 需要自定义）

前置依赖两个（F-028）：

- **uv**（Python 包管理器）：按 `https://docs.astral.sh/uv/getting-started/installation/` 安装，`uv --version` 验证；
- **ffmpeg**：macOS `brew install ffmpeg`；Ubuntu/Debian `sudo apt install ffmpeg`；Windows 到 ffmpeg.org 下载并把 `bin` 加入 PATH，`ffmpeg -version` 验证。

然后：

```bash
git clone https://github.com/AIDC-AI/Pixelle-Video.git
cd Pixelle-Video
uv run streamlit run web/app.py
```

`uv run` 会自动建立环境并安装依赖（pyproject 要求 Python >=3.11），浏览器同样自动打开 `http://localhost:8501`（F-028、F-030）。

## 2. 首次系统配置（对应推文"先添加 API"）

WebUI 展开「⚙️ 系统配置」面板，共三组配置（F-021、F-023）：

1. **LLM 配置**（必填，负责写文案）：下拉选预设模型（通义千问、GPT-4o、DeepSeek 等，推文作者选的是 DeepSeek，F-010），预设会自动填好 base_url 和 model；填入 API Key。也支持手动填 Key/Base URL/Model。面板内有「🔑 获取 API Key」注册链接。
2. **ComfyUI / RunningHub 配置**（用工作流出图/视频/语音时填）：
   - 本地部署填 ComfyUI URL（默认 `http://127.0.0.1:8188`），点「测试连接」；
   - 云端部署填 RunningHub API Key。
3. **API 媒体模型配置**（不用 ComfyUI、想直连供应商时填，2026-06-01 新增）：按需填 OpenAI / DashScope(Wan) / 火山 ARK(Seedream、Seedance) / Kling 的 Key、Base URL，可单独为每个供应商开关本地代理。只使用 ComfyUI/RunningHub 时本组可留空；选择 `api/...` 工作流时才必须填对应供应商密钥。

填完点「保存配置」。

## 3. 生成第一条视频（三栏布局）

按推文截图顺序与官方三栏说明对照（F-010~F-013、F-021~F-026）：

1. **左侧栏 · 内容输入**：生成模式选「AI 生成内容」，输入一个主题（先用官方示例风格的题，如"为什么要养成阅读习惯"）；BGM 选「无 BGM」或内置 `default.mp3`（自定义音乐把 MP3/WAV 放进项目 `bgm/` 文件夹，可试听）。
2. **中间栏 · 语音设置**：TTS 工作流选 `tts_edge`（零门槛在线音色）或 `tts_index2`（克隆音色）；克隆声音需上传参考音频（MP3/WAV/FLAC）。输入测试文本点「预览语音」先试听。
3. **中间栏 · 视觉设置**：图像工作流默认 `image_flux.json`（RunningHub/直连用户可选 qwen、sdxl、nano_banana 或 `api/...`）；图像尺寸默认 1024×1024；提示词前缀（需英文）控制统一画风。视频模板按竖屏/横屏/方形分组选择，可先「预览模板」。
4. **右侧栏 · 生成**：点「🎬 生成视频」，实时进度按"生成文案 → 生成配图 → 合成语音 → 合成视频"推进，并显示"分镜 3/5 - 生成插图"类状态。
5. **取片**：完成后自动预览，显示时长、文件大小、分镜数；**成片保存在项目 `output/` 文件夹**（F-028）。

官方称通常几分钟完成（F-034）。第一次试跑建议：一条主题 + Edge-TTS + RunningHub/直连单图工作流 + `image_default` 竖屏模板，先跑通闭环，再换 Index-TTS 克隆与 video_* 动态模板。

## 4. 效果不满意时的官方调优顺序

README FAQ 给出的四条路径（F-034）：

1. 换 LLM——不同模型文案风格差异最大；
2. 调图像尺寸与英文提示词前缀，改变配图风格；
3. 换 TTS 工作流或更换参考音频，改变声音；
4. 换视频模板与画幅。

## 5. 常见问题（依据官方文档，非真机实测）

| 现象 | 可能原因 | 处理 |
|---|---|---|
| 启动后 8501 打不开 | start.bat 未跑完依赖初始化/端口被占 | 看控制台日志；确认 8501 未被占用 |
| 「测试连接」ComfyUI 失败 | 本地 ComfyUI 未启动或端口非 8188 | 先启动 ComfyUI（`--listen 127.0.0.1 --port 8188`）或改填实际地址 |
| 选了 `api/...` 工作流报鉴权错 | 未在系统配置填该供应商 Key | 补填对应供应商密钥后保存（F-023） |
| TTS 不稳定/报错 | edge-tts 服务波动 | 官方已在 12-10 锁定 edge-tts 版本修复；更新到最新整合包，或换 Index-TTS（F-035） |
| 克隆音色无效果 | 选错工作流 | 声音克隆仅 Index-TTS 等支持克隆的工作流生效（F-022） |

下一篇：[零成本本地组合：Ollama + 本地 ComfyUI](01-zero-cost-local-stack.md)。
