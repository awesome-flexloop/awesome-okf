---
title: AnimateVideoNode
type: reference
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py
related:
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/tutorial-wan-video/references/generate-audio-node
  - /pocketflow/tutorial-wan-video/references/combine-node
  - /pocketflow/pocketflow-core/references/batch-node
---

# AnimateVideoNode

`AnimateVideoNode` 是流水线第五个节点，继承自 PocketFlow 的 `BatchNode`。它批量将每个场景的静态图像转化为动画视频片段，使用 Wan 2.7 I2V（Image-to-Video）模型，视频时长自动匹配音频长度。

## 类定义

```python
class AnimateVideoNode(BatchNode):
```

## 生命周期方法

### `prep(self, shared)`

准备批量处理数据，将图像、脚本、音频三组列表打包。

**参数：**
- `shared` — 共享数据字典

**读取：**
- `shared["images"]` — 生成的图像路径列表
- `shared["scripts"]` — 场景脚本列表
- `shared["audios"]` — 生成的音频路径列表

**写入：**
- `self._shared` — 保存 shared 引用

**返回：**
- `list[tuple]` — 使用 `zip(images, scripts, audios)` 将三组数据按场景配对，每个元素是 `(image_path, script, audio_path)` 三元组

### `exec(self, item)`

将单张静态图像转为动画视频。

**参数：**
- `item` (`tuple`) — `(image_path, script, audio_path)` 三元组

**处理逻辑：**
1. 解包三元组为 `image_path`、`script`、`audio_path`
2. 确定输出索引和路径
3. **探测音频时长**：使用 ffprobe 获取音频文件的实际时长
   ```python
   probe = subprocess.run(
       ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", audio_path],
       capture_output=True, text=True,
   )
   audio_dur = float(_json.loads(probe.stdout)["format"]["duration"])
   ```
4. **计算视频时长**：`duration = min(int(audio_dur) + 1, 15)`，即音频时长向上取整加 1 秒缓冲，但不超过 15 秒（API 限制）
5. 调用 `animate_image()` 提交 Wan 2.7 I2V 异步任务
6. 轮询等待任务完成，下载生成的视频
7. 将结果路径追加到 `self._shared["videos"]`

**输出路径：** `{output_dir}/{idx+1}.mp4`（从 1 开始编号）

**返回：**
- `str` — 生成的视频片段路径

**输出：**
- 打印音频时长和视频时长信息 `Audio duration: {audio_dur:.1f}s -> video duration: {duration}s`
- 打印进度 `Video {idx+1}/{total} done`

### `post(self, shared, prep_res, exec_res)`

同步结果回 shared。

**写入：**
- `shared["videos"]` — 从 `self._shared["videos"]` 同步视频路径列表

## 时长匹配策略

视频时长自动适配音频长度，确保配音完整播放：

```
音频时长 (ffprobe)  →  int(audio_dur) + 1  →  min(..., 15)  →  视频时长
```

| 音频时长 | 视频时长 | 说明 |
|---------|---------|------|
| 3.2 秒 | 4 秒 | 向上取整 + 1 秒缓冲 |
| 10.8 秒 | 11 秒 | 向上取整 + 1 秒缓冲 |
| 16.5 秒 | 15 秒 | 超过 15 秒上限，截断为 15 秒 |

> **注意**：如果对白文本过长导致音频超过 14 秒（+1 秒缓冲 = 15 秒），视频可能无法覆盖完整配音。GenerateScriptNode 提示词限制对白不超过 40 词，通常音频时长在 5-10 秒。

## I2V 模型参数

| 参数 | 值 | 说明 |
|------|----|------|
| 模型 | `wan2.7-i2v` | 万相 2.7 图生视频模型 |
| 分辨率 | `720P` | 1280×720 |
| duration | 动态计算 | 匹配音频时长，最大 15 秒 |
| prompt_extend | `True` | 启用提示词扩展 |
| watermark | `False` | 不添加水印 |
| 输入 | 首帧图像 + 动画提示词 | image 作为 first_frame，animation_prompt 作为运动描述 |
| API 模式 | 异步 | 提交任务后轮询等待 |

## 依赖的工具函数

- `utils.ali_api.animate_image(image_path, prompt, output_path, duration)` — 调用 Wan 2.7 I2V 生成视频
- `subprocess.run` + `ffprobe` — 探测音频时长

## 前置依赖

- **系统要求**：需要安装 `ffmpeg`（提供 ffprobe 命令）
- **前置节点**：GenerateImageNode（生成图像）和 GenerateAudioNode（生成音频）必须在此节点之前完成

## 流程连接

```python
# flow.py
animate = AnimateVideoNode(max_retries=2, wait=10)
animate >> combine  # 默认边连接到 CombineNode
audio >> animate    # 从 GenerateAudioNode 进入
```

重试配置：最多 2 次重试（共 3 次尝试），重试间隔 10 秒。

## Shared 数据契约

| 字段 | 方向 | 类型 | 说明 |
|------|------|------|------|
| `images` | 读取 | `list[str]` | 图像路径列表 |
| `scripts` | 读取 | `list[dict]` | 脚本列表（使用 animation_prompt） |
| `audios` | 读取 | `list[str]` | 音频路径列表（用于探测时长） |
| `output_dir` | 读取 | `str` | 输出目录路径 |
| `videos` | 写入 | `list[str]` | 生成的视频片段路径列表 |

## 源码位置

nodes.py#L210-L236
