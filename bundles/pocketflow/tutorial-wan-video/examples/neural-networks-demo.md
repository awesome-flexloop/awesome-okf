---
title: 神经网络科普视频演示
type: example
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/examples/neural_networks.md
related:
  - /pocketflow/tutorial-wan-video/examples/basic-usage
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/tutorial-wan-video/concepts/self-loop-iteration
---

# 神经网络科普视频演示

本文档展示了使用 Wan-Video Generator 将一篇关于神经网络的 Markdown 短文转化为 73 秒配音动画视频的完整过程和输出结果。

## 输入文章

输入文件为 [examples/neural_networks.md](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/examples/neural_networks.md)，内容是关于神经网络的两段简介：

```markdown
## What are Neural Networks

Neural networks are computing systems inspired by the human brain. They consist 
of layers of interconnected nodes that process information. Each connection has 
a weight that adjusts during training, allowing the network to learn patterns 
from data.

## How Training Works

Training a neural network involves feeding it data and adjusting weights to 
minimize errors. This process, called backpropagation, computes gradients and 
updates each weight step by step. Over many iterations, the network learns to 
make accurate predictions.
```

## 运行命令

```bash
python main.py examples/neural_networks.md -o ./output/nn_demo
```

## 流水线各阶段输出

### 阶段 1：场景规划（GenerateScenesNode）

LLM 规划了 7 个场景，遵循"Mia 困惑 → Ding Ding Dog 解释 → Mia 追问 → Ding Ding Dog 深入 → Mia 理解"的叙事弧线：

| 场景 | 说话者 | 场景描述 |
|------|--------|---------|
| 1 | Mia | 坐在书桌前，被神经网络作业包围，神情沮丧 |
| 2 | Ding Ding Dog | 走进来摇尾巴，从肚皮口袋掏出发光大脑道具，展开全息图 |
| 3 | Mia | 推了推圆眼镜，好奇地指着发光节点提问 |
| 4 | Ding Ding Dog | 金铃铛响着，掏出微型旋钮道具安装在节点连接线上，解释权重 |
| 5 | Mia | 挠头困惑，追问网络犯错时如何调整旋钮 |
| 6 | Ding Ding Dog | 投影出微型全息机器人，沿连接倒走演示反向传播 |
| 7 | Mia | 从书桌跳起来，双手高举庆祝理解 |

### 阶段 2：脚本生成（GenerateScriptNode，自环 7 次）

每个场景生成对白和提示词，以下是各场景的脚本输出：

**场景 1（Mia）：**
> "Ugh, my brain hurts! How am I supposed to understand these 'neural networks' for my computer science homework? It just looks like a bunch of confusing dots and lines!"

**场景 2（Ding Ding Dog）：**
> "Arf! Don't let the dots and lines trick you, Mia! Neural networks are actually inspired by the human brain, using interconnected nodes to process information just like you do."

**场景 3（Mia）：**
> "Okay, I get the brain part... but how do a bunch of glowing dots actually learn to recognize patterns from the data? It still looks like magic!"

**场景 4（Ding Ding Dog）：**
> "Arf! It's not magic, it's math! See these dials on the lines? They represent 'weights' that automatically turn and adjust during training to help the network figure out exactly which paths are most important!"

**场景 5（Mia）：**
> "Wait, I'm still confused. If the network makes a mistake, how does it actually know which way to turn those dials to fix it?"

**场景 6（Ding Ding Dog）：**
> "Arf! It uses a trick called 'backpropagation'! Think of it like a little helper walking backward through the network, checking mistakes step-by-step to tell the dials exactly how to fix the errors."

**场景 7（Mia）：**
> "I get it now! So by repeating that backward step over and over, the network learns from its mistakes and finally makes accurate predictions! Thanks, Ding Ding Dog!"

自环过程中，每个场景的提示词都包含先前所有场景的对白作为上下文，确保对话自然衔接。

### 阶段 3-5：批量生成（图像/音频/视频）

三个 BatchNode 并行处理 7 个场景：

| 场景 | 图像 | 音频 | 视频 | 音频时长 | 视频时长 |
|------|------|------|------|---------|---------|
| 1 | 1.png | 1.mp3 | 1.mp4 | ~8s | 9s |
| 2 | 2.png | 2.mp3 | 2.mp4 | ~10s | 11s |
| 3 | 3.png | 3.mp3 | 3.mp4 | ~7s | 8s |
| 4 | 4.png | 4.mp3 | 4.mp4 | ~11s | 12s |
| 5 | 5.png | 5.mp3 | 5.mp4 | ~8s | 9s |
| 6 | 6.png | 6.mp3 | 6.mp4 | ~12s | 13s |
| 7 | 7.png | 7.mp3 | 7.mp4 | ~9s | 10s |

- 图像：1280×720，日式儿童动漫画风，每个场景不同构图和镜头角度
- 音频：Mia 使用明快女声（1.2x 语速），Ding Ding Dog 使用沉稳男声（1.0x 语速）
- 视频：Wan 2.7 I2V 动画，每个片段匹配音频时长

### 阶段 6：合成输出（CombineNode）

1. 7 个片段分别合并音视频 → `1_combined.mp4` ~ `7_combined.mp4`
2. FFmpeg 标准化分辨率/帧率后拼接 → `final.mp4`
3. 最终视频时长约 73 秒

## 视觉多样性体现

7 个场景的视觉设计各不相同：

| 场景 | 场景地点 | 镜头角度 | 角色动作 | 道具 |
|------|---------|---------|---------|------|
| 1 | 卧室书桌 | 中景 | Mia 坐着皱眉头 | 皱巴巴的作业纸 |
| 2 | 卧室 | 中景 | 叮叮狗摇尾巴、掏道具 | 发光大脑道具、全息图 |
| 3 | 卧室 | 近景 | Mia 推眼镜、指向节点 | 发光节点网络 |
| 4 | 卧室 | 特写 | 叮叮狗安装旋钮道具 | 微型旋钮、连接线 |
| 5 | 卧室 | 中景 | Mia 挠头思考 | - |
| 6 | 卧室 | 俯视角 | 叮叮狗投影机器人演示 | 全息反向传播机器人 |
| 7 | 卧室 | 全景 | Mia 跳起来欢呼 | - |

## 角色一致性效果

三层保障机制在本示例中的效果：
1. **文本描述**：每个 image_prompt 都包含 Mia（马尾辫+圆眼镜）和 Ding Ding Dog（蓝色机器狗+金铃铛+红项圈+肚皮口袋）的完整描述
2. **参考图**：所有 7 张图都使用 `assets/ref.png` 作为角色设计基准
3. **链式引用**：第 2-7 张图额外参考前一张生成图，保持色彩和画风连贯

## 自定义你自己的视频

要为自己的文章生成视频：

1. 准备 Markdown 文件（技术文章、科普内容、教程等效果最佳）
2. 确保文章长度适中（建议 200-500 词，过短会导致场景少，过长会导致场景多成本高）
3. 运行流水线：
   ```bash
   python main.py your_article.md -o ./output/your_video
   ```
4. 首次运行后，修改文章或调整提示词后重新运行时，LLM 缓存会自动命中未变更的提示词，加速迭代
5. 如需完全重新生成（包括图像和视频），清空输出目录即可

## 源码位置

- 示例文章：[examples/neural_networks.md](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/examples/neural_networks.md)
- 示例输出：[examples/](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/examples/)（含 7 组 png/mp3/mp4 和 final.mp4）
