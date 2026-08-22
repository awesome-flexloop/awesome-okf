---
title: GenerateScriptNode
type: reference
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py
related:
  - /pocketflow/tutorial-wan-video/concepts/self-loop-iteration
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/tutorial-wan-video/references/generate-scenes-node
  - /pocketflow/tutorial-wan-video/references/generate-image-node
  - /pocketflow/pocketflow-core/references/node
---

# GenerateScriptNode

`GenerateScriptNode` 是流水线中第二个节点，继承自 PocketFlow 的 `Node`。它采用**自环模式**逐场景生成脚本，每个脚本包含对白文本、图像提示词和动画提示词。自环确保脚本生成时能访问所有先前场景的对白，保持对话连贯性。

## 类定义

```python
class GenerateScriptNode(Node):
```

## 生命周期方法

### `prep(self, shared)`

读取当前场景索引，判断是否所有场景处理完毕，组装上下文数据。

**参数：**
- `shared` — 共享数据字典

**读取：**
- `shared["current_idx"]` — 当前场景索引
- `shared["scenes"]` — 全部场景列表
- `shared["md_content"]` — 原文内容
- `shared["scripts"]` — 已有脚本列表（副本）

**返回：**
- `None` — 所有场景已处理完毕，触发 `"done"` 动作
- `dict` — 当前场景上下文，包含：
  - `scene` (`dict`) — 当前场景 `{speaker, description}`
  - `all_scenes` (`list`) — 全部场景列表（用于提示词中的全局视野）
  - `md_content` (`str`) — 原文内容（确保技术准确性）
  - `previous_scripts` (`list`) — 已有脚本的副本（对话上下文）

### `exec(self, data)`

调用 LLM 为单个场景生成脚本。

**参数：**
- `data` — prep 返回的上下文字典，或 `None`

**处理逻辑（data 不为 None 时）：**
1. 构建脚本生成提示词，包含：
   - 角色外观描述
   - 全部场景列表（全局叙事上下文）
   - 先前场景脚本（对话连续性）
   - 当前场景信息（说话者、描述）
   - 原文内容（技术准确性参考）
2. 提示词规则：
   - 对白 1-2 句短句，不超过 40 词，口语化、温暖
   - 对话自然延续，不重复已说内容
   - `image_prompt` 必须以 `IMAGE_STYLE` 前缀开头，包含双角色描述
   - 每个场景必须有独特视觉构图（不同场景/角度/姿势/道具）
   - `animation_prompt` 描述镜头运动和角色动作，要求动态感
3. 缓存策略：`self.cur_retry == 0` 时使用缓存，重试时跳过缓存
4. 调用 `call_llm()` 获取响应
5. 从响应中提取 YAML 代码块并解析
6. 断言验证必须包含 `speaker`、`text`、`image_prompt`、`animation_prompt` 四个字段

**返回：**
- `None` — data 为 None 时直接返回
- `dict` — 场景脚本，包含：
  - `speaker` (`str`) — 说话角色
  - `text` (`str`) — 对白文本
  - `image_prompt` (`str`) — 图像生成提示词
  - `animation_prompt` (`str`) — 动画运动描述

**异常：**
- YAML 解析失败或字段缺失时抛出异常，触发重试

### `post(self, shared, prep_res, exec_res)`

累积脚本结果并控制自环流程。

**参数：**
- `shared` — 共享数据字典
- `prep_res` — prep 的返回值
- `exec_res` — exec 的返回值（单场景脚本或 None）

**写入：**
- `shared["scripts"]` — 追加当前场景脚本
- `shared["current_idx"]` — 递增或重置为 0

**返回动作：**

| 条件 | 动作 | 流向 |
|------|------|------|
| `exec_res is None` | `"done"` | 进入 GenerateImageNode |
| `current_idx >= len(scenes)` | `"done"` | 进入 GenerateImageNode |
| 其他情况 | `"next"` | 自环，处理下一个场景 |

**输出：**
- 打印当前脚本进度 `Script {idx}/{total} [speaker]: text前60字符...`

## 自环流程详解

```
                    ┌─────────────────────────────┐
                    │                             │
prep→exec→post ────►│  返回 "next" → 再次 prep    │
                    │                             │
                    │  返回 "done" → image 节点    │
                    └─────────────────────────────┘
```

自环次数 = 场景数量（由 GenerateScenesNode 确定，4-8 次）。每次循环：
1. `prep` 读取 `current_idx` 对应的场景
2. `exec` 生成该场景脚本（可访问所有先前脚本作为上下文）
3. `post` 追加结果、递增索引、决定继续还是结束

## 流程连接

```python
# flow.py
script = GenerateScriptNode(max_retries=2, wait=10)
script - "next" >> script  # 自环：继续处理下一场景
script - "done" >> image   # 退出：进入图像生成
scenes >> script           # 入口：从场景规划节点连接
```

重试配置：最多 2 次重试（共 3 次尝试），重试间隔 10 秒。

## Shared 数据契约

| 字段 | 方向 | 类型 | 说明 |
|------|------|------|------|
| `scenes` | 读取 | `list[dict]` | 场景规划列表 |
| `md_content` | 读取 | `str` | Markdown 原文 |
| `scripts` | 读写 | `list[dict]` | 脚本列表（逐场景追加） |
| `current_idx` | 读写 | `int` | 当前场景索引（自环控制） |

## 提示词输出格式

LLM 返回的 YAML 结构：

```yaml
speaker: "Mia"
text: "What the speaker says..."
image_prompt: "Japanese children anime cartoon style, ..."
animation_prompt: "Camera movement description..."
```

## 源码位置

[nodes.py#L73-L156](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py#L73-L156)
