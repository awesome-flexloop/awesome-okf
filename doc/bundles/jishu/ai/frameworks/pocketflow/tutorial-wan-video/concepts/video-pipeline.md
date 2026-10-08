---
title: 视频生成流水线
type: concept
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/
related:
  - /pocketflow/tutorial-wan-video/references/generate-scenes-node
  - /pocketflow/tutorial-wan-video/references/generate-script-node
  - /pocketflow/tutorial-wan-video/references/generate-image-node
  - /pocketflow/tutorial-wan-video/references/generate-audio-node
  - /pocketflow/tutorial-wan-video/references/animate-video-node
  - /pocketflow/tutorial-wan-video/references/combine-node
  - /pocketflow/tutorial-wan-video/concepts/self-loop-iteration
  - /pocketflow/tutorial-wan-video/concepts/character-consistency
---

# 视频生成流水线

Wan-Video Generator 采用**六阶段线性流水线**架构，将 Markdown 文章逐步转化为完整配音动画视频。流水线在 PocketFlow 的 Flow 编排引擎上运行，每个阶段对应一个 Node，阶段之间通过 `shared` 字典传递数据。

## 流水线总览

```
Markdown 文件
    │
    ▼
┌─────────────┐
│ 1. 场景规划  │  GenerateScenesNode (Node)
│   (LLM)     │  读取文章 → 规划 4-8 个对话场景
└──────┬──────┘
       │ scenes: [{speaker, description}, ...]
       ▼
┌─────────────┐
│ 2. 脚本生成  │  GenerateScriptNode (Node, 自环)
│   (LLM)     │  逐场景生成对白 + 图像提示词 + 动画提示词
│  ↻ next     │  自环直到所有场景处理完毕
└──────┬──────┘
       │ scripts: [{speaker, text, image_prompt, animation_prompt}, ...]
       ▼
┌─────────────┐
│ 3. 图像生成  │  GenerateImageNode (BatchNode)
│  (Wan 2.7)  │  批量为每个场景生成插画（含角色参考图）
└──────┬──────┘
       │ images: ["1.png", "2.png", ...]
       ▼
┌─────────────┐
│ 4. 音频生成  │  GenerateAudioNode (BatchNode)
│ (CosyVoice) │  批量为每个场景生成角色配音
└──────┬──────┘
       │ audios: ["1.mp3", "2.mp3", ...]
       ▼
┌─────────────┐
│ 5. 视频动画  │  AnimateVideoNode (BatchNode)
│(Wan 2.7 I2V)│  批量将静态图转为动画片段（匹配音频时长）
└──────┬──────┘
       │ videos: ["1.mp4", "2.mp4", ...]
       ▼
┌─────────────┐
│ 6. 合成输出  │  CombineNode (Node)
│  (FFmpeg)   │  合并音视频 → 拼接片段 → 输出 final.mp4
└──────┬──────┘
       │
       ▼
   final.mp4
```

## 阶段详解

### 阶段 1：场景规划（GenerateScenesNode）

- **输入**：Markdown 文件路径（`shared["md_path"]`）
- **处理**：读取文件内容，调用 LLM 规划卡通场景
- **输出**：场景列表写入 `shared["scenes"]`，初始化后续数据容器
- **LLM 提示词策略**：定义两个角色（Mia / Ding Ding Dog）、对话交替规则、情绪弧线（困惑→解释→追问→深入→庆祝）

每个场景包含：
- `speaker`：说话角色（"Mia" 或 "Ding Ding Dog"）
- `description`：场景画面描述

### 阶段 2：脚本生成（GenerateScriptNode，自环）

- **输入**：`shared["scenes"]`、`shared["md_content"]`、已有脚本（上下文）
- **处理**：逐场景调用 LLM，生成对白文本、图像提示词、动画提示词
- **输出**：脚本列表写入 `shared["scripts"]`
- **自环控制**：通过 `shared["current_idx"]` 追踪进度，返回 `"next"` 继续自环，`"done"` 进入下一阶段

每个脚本包含：
- `speaker`：说话角色
- `text`：对白文本（1-2 句，不超过 40 词）
- `image_prompt`：图像生成提示词（含风格前缀和双角色描述）
- `animation_prompt`：动画运动描述（镜头运动 + 角色动作）

### 阶段 3：图像生成（GenerateImageNode，批量）

- **输入**：`shared["scripts"]`、`shared["ref_image"]`、已生成图像（链式引用）
- **处理**：调用 Wan 2.7 Image API，为每个场景生成 1280×720 插画
- **输出**：图像路径列表写入 `shared["images"]`
- **角色一致性**：每个请求携带参考图 + 上一张生成图作为风格参考

### 阶段 4：音频生成（GenerateAudioNode，批量）

- **输入**：`shared["scripts"]`
- **处理**：调用 CosyVoice TTS，根据角色选择不同音色/语速/音调
- **输出**：音频路径列表写入 `shared["audios"]`
- **角色语音映射**：Mia 使用 longanhuan（快语速、高音调），Ding Ding Dog 使用 longanyang（标准语速、低音调）

### 阶段 5：视频动画（AnimateVideoNode，批量）

- **输入**：`shared["images"]` + `shared["scripts"]` + `shared["audios"]`（zip 组合）
- **处理**：先用 ffprobe 获取音频时长，再调用 Wan 2.7 I2V 将静态图转为动画
- **输出**：视频片段路径列表写入 `shared["videos"]`
- **时长匹配**：视频时长 = min(音频时长 + 1秒, 15秒)，确保动画覆盖完整配音

### 阶段 6：合成输出（CombineNode）

- **输入**：`shared["videos"]` + `shared["audios"]`
- **处理**：
  1. 对每个片段调用 FFmpeg 合并音视频轨道
  2. 若只有 1 个片段直接复制，否则先标准化分辨率/帧率再拼接
- **输出**：最终视频路径写入 `shared["final_video"]`

## 数据流转

数据通过 `shared` 字典在节点间单向流动，形成清晰的生产者-消费者关系：

| 节点 | 读取 | 写入 |
|------|------|------|
| GenerateScenesNode | `md_path` | `md_content`, `scenes`, 初始化所有列表 |
| GenerateScriptNode | `scenes`, `md_content`, `scripts` | `scripts`（追加）, `current_idx` |
| GenerateImageNode | `scripts`, `ref_image`, `images` | `images`（追加） |
| GenerateAudioNode | `scripts` | `audios`（追加） |
| AnimateVideoNode | `images`, `scripts`, `audios` | `videos`（追加） |
| CombineNode | `videos`, `audios` | `final_video` |

## 重试配置

所有外部 API 调用节点都配置了重试机制：

```python
GenerateScenesNode(max_retries=2, wait=10)
GenerateScriptNode(max_retries=2, wait=10)
GenerateImageNode(max_retries=2, wait=10)
GenerateAudioNode(max_retries=2, wait=10)
AnimateVideoNode(max_retries=2, wait=10)
```

每个节点最多重试 2 次（共 3 次尝试），重试间隔 10 秒，应对 API 临时故障。

## 设计模式

本流水线综合运用了 PocketFlow 的两种核心设计模式：

1. **自环迭代**：[GenerateScriptNode](../references/generate-script-node.md) 通过 `"next"` 条件边连接自身，实现逐场景顺序处理
2. **批量处理**：[GenerateImageNode](../references/generate-image-node.md)、[GenerateAudioNode](../references/generate-audio-node.md)、[AnimateVideoNode](../references/animate-video-node.md) 使用 BatchNode 对所有场景并行执行相同操作

更多细节参见：[自环迭代优化](self-loop-iteration.md)、[角色一致性策略](character-consistency.md)。
