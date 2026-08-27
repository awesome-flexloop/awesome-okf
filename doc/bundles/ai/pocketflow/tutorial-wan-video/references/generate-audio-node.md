---
title: GenerateAudioNode
type: reference
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py
related:
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/tutorial-wan-video/references/generate-image-node
  - /pocketflow/tutorial-wan-video/references/animate-video-node
  - /pocketflow/pocketflow-core/references/batch-node
---

# GenerateAudioNode

`GenerateAudioNode` 是流水线第四个节点，继承自 PocketFlow 的 `BatchNode`。它批量为每个场景的对白生成语音配音，使用 CosyVoice v3+ TTS 模型，根据角色选择不同的音色、语速和音调。

## 类定义

```python
class GenerateAudioNode(BatchNode):
```

## 生命周期方法

### `prep(self, shared)`

准备批量处理数据。

**参数：**
- `shared` — 共享数据字典

**读取：**
- `shared["scripts"]` — 全部场景脚本列表

**写入：**
- `self._shared` — 保存 shared 引用

**返回：**
- `list[dict]` — 脚本列表，BatchNode 对每个脚本调用一次 exec

### `exec(self, script)`

为单个场景生成配音。

**参数：**
- `script` (`dict`) — 单个场景脚本，需包含 `text`（对白文本）和 `speaker`（说话角色）

**处理逻辑：**
1. 根据当前已生成音频数量确定索引和输出路径
2. 调用 `generate_audio(script["text"], script["speaker"], path)` 生成配音
3. 将结果路径追加到 `self._shared["audios"]`

**输出路径：** `{output_dir}/{idx+1}.mp3`（从 1 开始编号）

**返回：**
- `str` — 生成的音频文件路径

**输出：**
- 打印进度 `Audio {idx+1}/{total} done`

### `post(self, shared, prep_res, exec_res)`

同步结果回 shared。

**写入：**
- `shared["audios"]` — 从 `self._shared["audios"]` 同步音频路径列表

## 角色语音配置

语音参数定义在 utils/audio.py：

```python
VOICE_MAP = {
    "Mia": {"voice": "longanhuan", "speech_rate": 1.2, "pitch_rate": 1.15},
    "Ding Ding Dog": {"voice": "longanyang", "speech_rate": 1.0, "pitch_rate": 0.9},
}
```

| 角色 | 音色 | 语速 | 音调 | 效果 |
|------|------|------|------|------|
| Mia | longanhuan | 1.2x | 1.15x | 年轻女孩的明快声音 |
| Ding Ding Dog | longanyang | 1.0x | 0.9x | 沉稳的讲解声音 |

若脚本中的 speaker 不在 VOICE_MAP 中，默认使用 Ding Ding Dog 的配置。

## TTS 模型参数

| 参数 | 值 | 说明 |
|------|----|------|
| 模型 | `cosyvoice-v3-plus` | CosyVoice 多语言 TTS |
| API 协议 | WebSocket | 实时流式合成 |
| 输出格式 | 二进制音频 | 写入 .mp3 文件 |
| 端点 | `wss://dashscope-intl.aliyuncs.com/api-ws/v1/inference` | DashScope 国际站 |

## 依赖的工具函数

- `utils.audio.generate_audio(text, speaker, output_path)` — 调用 CosyVoice 合成语音

## 流程连接

```python
# flow.py
audio = GenerateAudioNode(max_retries=2, wait=10)
audio >> animate  # 默认边连接到 AnimateVideoNode
image >> audio    # 从 GenerateImageNode 进入
```

重试配置：最多 2 次重试（共 3 次尝试），重试间隔 10 秒。

## Shared 数据契约

| 字段 | 方向 | 类型 | 说明 |
|------|------|------|------|
| `scripts` | 读取 | `list[dict]` | 场景脚本列表 |
| `output_dir` | 读取 | `str` | 输出目录路径 |
| `audios` | 写入 | `list[str]` | 生成的音频路径列表 |

## 源码位置

nodes.py#L190-L205
