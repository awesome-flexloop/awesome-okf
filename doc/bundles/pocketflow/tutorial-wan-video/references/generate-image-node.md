---
title: GenerateImageNode
type: reference
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py
related:
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/tutorial-wan-video/concepts/character-consistency
  - /pocketflow/tutorial-wan-video/references/generate-script-node
  - /pocketflow/tutorial-wan-video/references/generate-audio-node
  - /pocketflow/pocketflow-core/references/batch-node
---

# GenerateImageNode

`GenerateImageNode` 是流水线第三个节点，继承自 PocketFlow 的 `BatchNode`。它批量为每个场景生成 1280×720 的插画，使用 Wan 2.7 文生图模型，通过参考图和链式引用确保角色一致性。

## 类定义

```python
class GenerateImageNode(BatchNode):
```

## 生命周期方法

### `prep(self, shared)`

准备批量处理数据，保存 shared 引用供 exec 使用。

**参数：**
- `shared` — 共享数据字典

**读取：**
- `shared["scripts"]` — 全部场景脚本列表

**写入：**
- `self._shared` — 保存 shared 引用（BatchNode 的 exec 不直接接收 shared 参数）

**返回：**
- `list[dict]` — 脚本列表，BatchNode 框架会对每个元素调用一次 `exec`

### `exec(self, script)`

为单个场景生成图像。

**参数：**
- `script` (`dict`) — 单个场景脚本，包含 `speaker`、`text`、`image_prompt`、`animation_prompt`

**处理逻辑：**
1. 根据当前已生成图像数量确定索引和输出路径
2. 处理图像提示词：
   - 若 `image_prompt` 不以 `IMAGE_STYLE` 开头，自动添加前缀
   - 追加一致性指令：使用参考图保持角色设计一致，使用上一张图保持环境/色彩连贯，但改变角度、姿势和构图
3. 组装参考图列表：
   - 始终包含 `self._shared["ref_image"]`（角色设计参考图）
   - 若已有生成图像，追加最后一张（链式引用）
4. 调用 `generate_image()` 提交 Wan 2.7 异步任务，轮询等待完成
5. 下载生成的图像到输出目录
6. 将结果路径追加到 `self._shared["images"]`

**输出路径：** `{output_dir}/{idx+1}.png`（从 1 开始编号）

**返回：**
- `str` — 生成的图像文件路径

**输出：**
- 打印进度 `Image {idx+1}/{total} done`

### `post(self, shared, prep_res, exec_res)`

同步批量处理结果回 shared。

**参数：**
- `shared` — 共享数据字典
- `prep_res` — prep 返回的脚本列表
- `exec_res` — BatchNode 收集的所有 exec 返回值列表

**写入：**
- `shared["images"]` — 从 `self._shared["images"]` 同步图像路径列表

**注意：** 由于 exec 中已经通过 `self._shared["images"].append(result)` 实时累积结果，post 中再次赋值以确保数据一致性。

## 参考图机制

本节点实现了三层角色一致性中的第二、三层（参考图注入 + 链式引用），详见 [角色一致性策略](../concepts/character-consistency.md)。

```python
refs = [self._shared["ref_image"]]  # 第二层：角色设计参考图
if self._shared["images"]:
    refs.append(self._shared["images"][-1])  # 第三层：上一场景图链式引用
result = generate_image(prompt, path, ref_image_paths=refs)
```

## 图像参数

| 参数 | 值 | 说明 |
|------|----|------|
| 模型 | `wan2.7-image` | 万相 2.7 文生图模型 |
| 分辨率 | `1280*720` | 16:9 宽屏 |
| 生成数量 | `n=1` | 每场景一张图 |
| API 模式 | 异步（X-DashScope-Async） | 提交任务后轮询等待 |

## 依赖的工具函数

- `utils.ali_api.generate_image(prompt, output_path, ref_image_paths)` — 调用 Wan 2.7 API 生成图像
- `utils.ali_api.image_to_data_uri(path)` — 将图片编码为 Data URI

## 流程连接

```python
# flow.py
image = GenerateImageNode(max_retries=2, wait=10)
image >> audio  # 默认边连接到 GenerateAudioNode
script - "done" >> image  # 从 GenerateScriptNode 的 "done" 动作进入
```

重试配置：最多 2 次重试（共 3 次尝试），重试间隔 10 秒。

## Shared 数据契约

| 字段 | 方向 | 类型 | 说明 |
|------|------|------|------|
| `scripts` | 读取 | `list[dict]` | 场景脚本列表 |
| `output_dir` | 读取 | `str` | 输出目录路径 |
| `ref_image` | 读取 | `str` | 角色参考图路径 |
| `images` | 写入 | `list[str]` | 生成的图像路径列表 |

## 源码位置

[nodes.py#L161-L185](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py#L161-L185)
