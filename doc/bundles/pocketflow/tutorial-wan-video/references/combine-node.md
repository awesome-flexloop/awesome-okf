---
title: CombineNode
type: reference
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py
related:
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/tutorial-wan-video/references/animate-video-node
  - /pocketflow/pocketflow-core/references/node
---

# CombineNode

`CombineNode` 是流水线的最后一个节点，继承自 PocketFlow 的 `Node`。它将每个场景的视频片段与配音合并，然后将所有片段拼接为一个完整的最终视频文件。

## 类定义

```python
class CombineNode(Node):
```

## 生命周期方法

### `prep(self, shared)`

收集合成所需的数据。

**参数：**
- `shared` — 共享数据字典

**读取：**
- `shared["videos"]` — 动画视频片段路径列表
- `shared["audios"]` — 配音音频路径列表
- `shared["output_dir"]` — 输出目录路径

**返回：**
- `dict` — 包含 `videos`、`audios`、`output_dir` 的字典

### `exec(self, data)`

执行两步合成操作：先逐片段合并音视频，再拼接为最终视频。

**参数：**
- `data` (`dict`) — prep 返回的数据字典

**处理逻辑：**

**第一步：合并音视频（逐场景）**

对每个场景的视频片段和音频文件调用 FFmpeg 合并：

```python
for i, (vp, ap) in enumerate(zip(data["videos"], data["audios"])):
    out = os.path.join(output_dir, f"{i + 1}_combined.mp4")
    merge_audio_video(vp, ap, out)
    combined.append(out)
```

合并方式：
- 视频流直接复制（`-c:v copy`），不重新编码
- 音频使用 AAC 编码（`-c:a aac`）
- 音频混合使用 amix 滤镜，将视频原音轨（来自 I2V 生成）与配音混合，取较短时长
- 输出为 `{i+1}_combined.mp4`

**第二步：拼接片段**

- 若只有 1 个片段，直接复制为 `final.mp4`
- 若有多个片段，先标准化（分辨率 1280×720、30fps、AAC 音频），再使用 concat demuxer 拼接

```python
final = os.path.join(output_dir, "final.mp4")
if len(combined) == 1:
    import shutil
    shutil.copy2(combined[0], final)
else:
    concat_videos(combined, final)
```

**输出路径：** `{output_dir}/final.mp4`

**返回：**
- `str` — 最终视频文件的绝对路径

### `post(self, shared, prep_res, exec_res)`

存储最终结果。

**参数：**
- `shared` — 共享数据字典
- `prep_res` — prep 的返回值
- `exec_res` — exec 返回的最终视频路径

**写入：**
- `shared["final_video"]` — 最终视频路径

**返回：**
- `None`（流水线结束节点，无后续节点）

**输出：**
- 打印 `Final video: {exec_res}`

## FFmpeg 合成细节

### merge_audio_video：音视频合并

在 [utils/ffmpeg.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/utils/ffmpeg.py) 中实现：

```
ffmpeg -y
  -i video.mp4        # 输入视频（含 I2V 生成的原音轨）
  -i audio.mp3        # 输入配音
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=shortest:dropout_transition=0[aout]"
  -map 0:v -map "[aout]"
  -c:v copy           # 视频流直接复制
  -c:a aac            # 音频重新编码为 AAC
  output.mp4
```

关键点：
- `amix` 将两个音频轨（I2V 视频自带的环境音 + TTS 配音）混合
- `duration=shortest` 以较短音轨为准
- `dropout_transition=0` 音轨结束时无过渡
- 视频流 copy 不重新编码，速度快

### concat_videos：视频拼接

标准化 + 拼接两步：

**标准化（确保所有片段参数一致）：**
```
ffmpeg -y -i input.mp4
  -c:v libx264        # 视频统一编码为 H.264
  -c:a aac            # 音频统一编码为 AAC
  -r 30               # 统一 30fps
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"
                      # 缩放到 1280×720，保持比例，黑边填充
  -ar 44100 -ac 2     # 统一音频采样率 44100Hz、立体声
  output_norm.mp4
```

**拼接（使用 concat demuxer）：**
```
ffmpeg -y -f concat -safe 0 -i list.txt -c copy final.mp4
```

拼接完成后自动删除临时标准化文件和列表文件。

## 流程连接

```python
# flow.py
combine = CombineNode()  # 无重试配置（FFmpeg 本地操作，通常无需重试）
animate >> combine       # 从 AnimateVideoNode 进入
```

## Shared 数据契约

| 字段 | 方向 | 类型 | 说明 |
|------|------|------|------|
| `videos` | 读取 | `list[str]` | 视频片段路径列表 |
| `audios` | 读取 | `list[str]` | 音频路径列表 |
| `output_dir` | 读取 | `str` | 输出目录路径 |
| `final_video` | 写入 | `str` | 最终合成视频路径 |

## 输出文件清单

流水线运行完成后，输出目录包含：

| 文件 | 来源 | 说明 |
|------|------|------|
| `1.png` ~ `N.png` | GenerateImageNode | 各场景插画 |
| `1.mp3` ~ `N.mp3` | GenerateAudioNode | 各场景配音 |
| `1.mp4` ~ `N.mp4` | AnimateVideoNode | 各场景动画片段（I2V 原始输出） |
| `1_combined.mp4` ~ `N_combined.mp4` | CombineNode | 音视频合并后的片段（中间产物） |
| `final.mp4` | CombineNode | **最终成品视频** |

## 源码位置

[nodes.py#L241-L266](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py#L241-L266)
