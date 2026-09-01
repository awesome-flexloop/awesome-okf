---
title: 基本使用
type: example
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/main.py
related:
  - /pocketflow/tutorial-wan-video/index
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/tutorial-wan-video/references/generate-scenes-node
---

# 基本使用

本文档介绍如何配置环境、安装依赖并运行 Wan-Video Generator 流水线，将 Markdown 文章转化为配音动画视频。

## 前置条件

### 1. API 密钥

需要两个 API 密钥：

| 密钥 | 获取地址 | 用途 |
|------|---------|------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/app/apikey) | LLM 文本生成（场景规划、脚本写作） |
| `DASHSCOPE_API_KEY` | [Alibaba Model Studio](https://www.alibabacloud.com/en/solutions/generative-ai/model-studio) | 图像生成（Wan 2.7）、视频生成（Wan 2.7 I2V）、语音合成（CosyVoice） |

### 2. 系统依赖

- **Python** 3.10+
- **FFmpeg**：用于音视频处理
  - macOS：`brew install ffmpeg`
  - Ubuntu/Debian：`sudo apt install ffmpeg`
  - Windows：从 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载并添加到 PATH

### 3. LLM 配置验证

项目默认使用 Google Gemini。如需更换 LLM，修改 utils/call_llm.py。可参考 [PocketFlow LLM Wrappers](https://the-pocket.github.io/PocketFlow/utility_function/llm.html) 文档。

验证 LLM 是否正确配置：
```bash
python utils/call_llm.py
```

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

依赖清单：
```
pocketflow>=0.0.1      # PocketFlow 框架
pyyaml>=6.0            # YAML 解析
requests>=2.28.0       # HTTP 请求（DashScope API）
python-dotenv>=1.0.0   # 环境变量加载
google-genai>=1.9.0    # Google Gemini SDK
dashscope>=1.20.0      # 阿里云 DashScope SDK（TTS）
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
GEMINI_API_KEY=your-actual-gemini-api-key
DASHSCOPE_API_KEY=your-actual-dashscope-api-key
```

也可以直接设置系统环境变量：
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-key"
$env:DASHSCOPE_API_KEY="your-key"

# Linux/macOS
export GEMINI_API_KEY="your-key"
export DASHSCOPE_API_KEY="your-key"
```

### 3. 准备角色参考图（可选）

项目默认使用 `assets/ref.png` 作为角色设计参考图。如需自定义角色，准备一张清晰展示角色设计的 PNG 图片。

## 运行流水线

### 基本命令

```bash
python main.py <input_markdown_file>
```

### 命令行参数

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `input` | （位置参数） | 必填 | 输入 Markdown 文件路径 |
| `--output` | `-o` | `./output` | 输出目录路径 |
| `--ref-image` | | `assets/ref.png` | 自定义角色参考图路径 |

### 使用示例

使用项目自带的神经网络示例文章：
```bash
python main.py examples/neural_networks.md
```

指定自定义输出目录：
```bash
python main.py my_article.md -o ./my_video_output
```

使用自定义角色参考图：
```bash
python main.py my_article.md --ref-image my_character.png
```

完整参数示例：
```bash
python main.py examples/neural_networks.md -o ./output/nn_demo --ref-image assets/ref.png
```

## 运行输出

流水线运行时会在终端打印各阶段进度：

```
Starting pipeline for: examples/neural_networks.md
Output directory: D:\projects\output
Planned 7 scenes:
  1. [Mia] Mia is sitting at her desk looking frustrated...
  2. [Ding Ding Dog] Ding Ding Dog walks in, wags his stubby tail...
  ...
Script 1/7 [Mia]: Ugh, my brain hurts! How am I supposed to...
[Cache MISS] Calling gemini-2.5-flash for abc12345...
Script 2/7 [Ding Ding Dog]: Arf! Don't let the dots and lines trick...
...
Image 1/7 done
Image 2/7 done
...
Audio 1/7 done
Audio 2/7 done
...
  Audio duration: 8.2s -> video duration: 9s
Video 1/7 done
...
[ffmpeg] Merging output\1.mp4 + output\1.mp3
[ffmpeg] Concatenating 7 clips
Final video: D:\projects\output\final.mp4

Done! Final video: D:\projects\output\final.mp4
```

## 输出文件

运行完成后，输出目录包含：

```
output/
├── 1.png ~ 7.png          # 各场景插画
├── 1.mp3 ~ 7.mp3          # 各场景配音
├── 1.mp4 ~ 7.mp4          # 各场景动画片段（I2V 原始输出）
├── 1_combined.mp4 ~ 7_combined.mp4  # 音视频合并片段（中间产物）
└── final.mp4              # 最终成品视频
```

## 编程式调用

除了命令行，也可以在 Python 代码中直接调用：

```python
from flow import create_flow

shared = {
    "md_path": "path/to/article.md",
    "md_content": "",
    "output_dir": "./output",
    "ref_image": "assets/ref.png",
    "scenes": [],
    "scripts": [],
    "images": [],
    "audios": [],
    "videos": [],
    "final_video": "",
    "current_idx": 0,
}

flow = create_flow()
flow.run(shared)
print(f"Final video: {shared['final_video']}")
```

## LLM 缓存机制

项目在 utils/call_llm.py 中实现了基于文件的提示词-响应缓存，缓存存储在 `utils/.llm_cache/cache.json`。相同的提示词会直接返回缓存结果，避免重复调用 LLM 产生费用。首次运行后，场景规划和脚本生成阶段会命中缓存，加速迭代。

如需强制重新生成（如修改了提示词），删除缓存文件即可：
```bash
rm utils/.llm_cache/cache.json
```

## 常见问题

### Q: 图像生成失败或返回错误
检查 `DASHSCOPE_API_KEY` 是否正确，以及阿里云账户是否有足够额度。Wan 2.7 模型需要开通 DashScope 国际站服务。

### Q: FFmpeg 相关错误
确保 FFmpeg 已正确安装且在系统 PATH 中。运行 `ffmpeg -version` 验证。

### Q: 角色外观不一致
确保参考图清晰展示角色设计。可以尝试调整 `assets/ref.png` 为更高质量的角色设计图。

### Q: 视频时长不够覆盖配音
对白文本过长时音频可能超过 15 秒（I2V 最大时长）。修改文章使其更简洁，或在 GenerateScriptNode 的提示词中进一步降低词数限制。

## 源码位置

- 入口程序：main.py
- 流程创建：flow.py
