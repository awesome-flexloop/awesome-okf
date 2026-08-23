---
title: GenerateScenesNode
type: reference
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py
related:
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/tutorial-wan-video/references/generate-script-node
  - /pocketflow/pocketflow-core/references/node
---

# GenerateScenesNode

`GenerateScenesNode` 是流水线的第一个节点，继承自 PocketFlow 的 `Node`。它读取 Markdown 文章内容，调用 LLM 规划 4-8 个卡通对话场景，并初始化流水线的共享数据容器。

## 类定义

```python
class GenerateScenesNode(Node):
```

## 生命周期方法

### `prep(self, shared)`

读取输入 Markdown 文件并加载内容。

**参数：**
- `shared` — 共享数据字典

**读取：**
- `shared["md_path"]` — Markdown 文件路径（由 [main.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/main.py) 设置）

**写入：**
- `shared["md_content"]` — 加载的 Markdown 文件全文

**返回：**
- `str` — Markdown 文件全文内容

### `exec(self, content)`

调用 LLM 规划卡通场景。

**参数：**
- `content` — Markdown 文章全文（prep 的返回值）

**处理逻辑：**
1. 构建场景规划提示词，包含：
   - 两个角色（Mia、Ding Ding Dog）的详细外观描述
   - 对话交替规则（提问→解释→追问→深入→庆祝）
   - 场景数量要求（4-8 个）
2. 根据 `self.cur_retry` 决定是否使用缓存（首次调用使用缓存，重试时跳过缓存）
3. 调用 `call_llm()` 获取响应
4. 从响应中提取 YAML 代码块并解析
5. 断言验证：`scenes` 必须是列表且长度 ≥ 2

**返回：**
- `list[dict]` — 场景列表，每个场景包含：
  - `speaker` (`str`) — 说话角色："Mia" 或 "Ding Ding Dog"
  - `description` (`str`) — 场景画面描述

**异常：**
- YAML 解析失败或断言失败时抛出异常，触发 PocketFlow 重试机制

### `post(self, shared, prep_res, exec_res)`

存储场景规划结果并初始化后续数据容器。

**参数：**
- `shared` — 共享数据字典
- `prep_res` — prep 的返回值（Markdown 内容）
- `exec_res` — exec 的返回值（场景列表）

**写入：**
- `shared["scenes"]` — 场景列表
- `shared["scripts"]` — 初始化空列表
- `shared["images"]` — 初始化空列表
- `shared["audios"]` — 初始化空列表
- `shared["videos"]` — 初始化空列表
- `shared["current_idx"]` — 初始化为 0

**返回：**
- `None`（默认动作，沿默认边 `>>` 流向下一节点）

**输出：**
- 打印场景数量和每个场景的摘要（前 70 字符）

## 上下文依赖

### 角色描述常量

节点使用模块级常量定义角色外观：

```python
CHARACTER_DESC = {
    "Ding Ding Dog": "A cute blue robotic puppy with big floppy dog ears, ...",
    "Mia": "A cheerful girl with pigtails and round glasses.",
}
```

### LLM 提示词结构

提示词要求 LLM 输出 YAML 格式：

```yaml
scenes:
  - speaker: "Mia"
    description: "Mia is sitting at her desk looking frustrated..."
  - speaker: "Ding Ding Dog"
    description: "Ding Ding Dog pulls a glowing brain gadget..."
```

## 流程连接

```python
# flow.py
scenes = GenerateScenesNode(max_retries=2, wait=10)
scenes >> script  # 默认边连接到 GenerateScriptNode
```

重试配置：最多 2 次重试（共 3 次尝试），重试间隔 10 秒。

## Shared 数据契约

| 字段 | 方向 | 类型 | 说明 |
|------|------|------|------|
| `md_path` | 读取 | `str` | Markdown 文件路径 |
| `md_content` | 写入 | `str` | Markdown 文件内容 |
| `output_dir` | 读取（由 main 设置） | `str` | 输出目录 |
| `ref_image` | 读取（由 main 设置） | `str` | 参考图路径 |
| `scenes` | 写入 | `list[dict]` | 场景规划列表 |
| `scripts` | 写入 | `list` | 初始化为空列表 |
| `images` | 写入 | `list` | 初始化为空列表 |
| `audios` | 写入 | `list` | 初始化为空列表 |
| `videos` | 写入 | `list` | 初始化为空列表 |
| `current_idx` | 写入 | `int` | 初始化为 0 |

## 源码位置

[nodes.py#L19-L68](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py#L19-L68)
