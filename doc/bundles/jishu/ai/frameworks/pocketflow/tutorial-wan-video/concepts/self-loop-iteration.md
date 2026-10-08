---
title: 自环迭代优化
type: concept
bundle: /pocketflow/tutorial-wan-video
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Wan-Video/nodes.py
related:
  - /pocketflow/tutorial-wan-video/references/generate-script-node
  - /pocketflow/tutorial-wan-video/concepts/video-pipeline
  - /pocketflow/pocketflow-core/concepts/flow-orchestration
---

# 自环迭代优化

自环（Self-Loop）是 PocketFlow 中实现**顺序迭代处理**的核心模式。在 Wan-Video Generator 中，[GenerateScriptNode](../references/generate-script-node.md) 通过自环逐场景生成脚本，每轮处理一个场景并将结果累积到 `shared` 中，同时利用已有脚本作为上下文，确保对话连贯性。

## 自环模式原理

自环的核心是节点的 `post` 方法返回一个**动作字符串**（action），Flow 根据该字符串选择下一个节点。当动作匹配到节点自身的条件边时，节点会再次执行，形成循环：

```python
# flow.py 中的连接方式
script - "next" >> script   # "next" 动作 → 回到自身（自环）
script - "done" >> image    # "done" 动作 → 进入下一节点
```

```
     ┌──────────────────────┐
     │                      │ "next"
     ▼                      │
┌─────────────┐             │
│ GenerateScript│────────────┘
│    Node      │
└──────┬──────┘
       │ "done"
       ▼
┌─────────────┐
│GenerateImage│
│    Node     │
└─────────────┘
```

## 三阶段协作

自环模式下，节点的 `prep`/`exec`/`post` 三阶段各自承担不同职责：

### prep：读取进度与上下文

`prep` 方法在每次循环开始时执行，负责：
1. 读取当前进度索引 `current_idx`
2. 判断是否所有场景已处理完毕
3. 组装当前场景数据 + 全局上下文 + 已有脚本

```python
def prep(self, shared):
    idx = shared["current_idx"]
    if idx >= len(shared["scenes"]):
        return None  # 信号：所有场景已完成
    return {
        "scene": shared["scenes"][idx],
        "all_scenes": shared["scenes"],
        "md_content": shared["md_content"],
        "previous_scripts": shared["scripts"].copy(),
    }
```

关键设计点：
- **终止信号**：返回 `None` 表示循环结束，`exec` 和 `post` 据此判断
- **上下文传递**：`previous_scripts` 使用 `.copy()` 创建副本，避免 exec 中意外修改累积数据
- **全局视野**：将所有场景列表和原文传入，让 LLM 了解整体叙事弧线

### exec：单步处理

`exec` 方法接收 `prep` 的返回值，处理单个场景：

```python
def exec(self, data):
    if data is None:
        return None
    scene = data["scene"]
    # ... 构建 LLM 提示词，调用 call_llm ...
    return result  # 单场景脚本 {speaker, text, image_prompt, animation_prompt}
```

提示词设计要点：
1. **对话连续性**：在提示词中包含所有先前场景的脚本文本，LLM 据此自然延续对话
2. **视觉多样性**：要求每个场景使用不同的场景、镜头角度、角色姿势和道具
3. **风格一致性**：`image_prompt` 必须以统一的 `IMAGE_STYLE` 前缀开头
4. **角色共现**：每个场景两个角色同时出现（说话者为焦点，另一人反应）

### post：累积结果与循环控制

`post` 方法在每次 exec 后执行，负责结果累积和流程控制：

```python
def post(self, shared, prep_res, exec_res):
    if exec_res is None:
        shared["current_idx"] = 0
        return "done"           # 终止自环，进入下一阶段
    shared["scripts"].append(exec_res)
    shared["current_idx"] += 1
    if shared["current_idx"] >= len(shared["scenes"]):
        shared["current_idx"] = 0
        return "done"           # 所有场景完成
    return "next"               # 继续自环，处理下一个场景
```

控制逻辑：
1. `exec_res is None` → prep 已判断完毕（所有场景处理完）→ 返回 `"done"`
2. 累积结果后检查索引 → 超出场景数 → 返回 `"done"`
3. 否则 → 返回 `"next"` → 再次执行自身

## 重试与缓存的协同

GenerateScriptNode 配置了 `max_retries=2, wait=10`，与自环模式协同工作：

- **首次调用**（`cur_retry == 0`）：`use_cache=True`，命中缓存则跳过 LLM 调用
- **重试调用**（`cur_retry > 0`）：`use_cache=False`，强制重新生成，避免 LLM 返回格式错误时反复命中坏缓存

```python
use_cache = self.cur_retry == 0
response = call_llm(prompt, use_cache=use_cache)
```

这种设计确保：
- 正常情况下缓存命中，节省 API 费用
- 当 YAML 解析失败触发重试时，不使用缓存，让 LLM 重新生成
- `assert` 语句验证输出格式，格式错误直接抛异常触发重试

## 与 BatchNode 的对比

自环迭代和 BatchNode 都能处理集合数据，但适用场景不同：

| 维度 | 自环迭代（Self-Loop） | 批量处理（BatchNode） |
|------|---------------------|---------------------|
| 处理方式 | 逐个顺序处理 | 逐个独立处理 |
| 上下文 | 每步可访问前序结果 | 各 item 独立无状态 |
| 适用场景 | 需要累积上下文的顺序任务 | 独立可并行的数据转换 |
| 示例 | 脚本生成（对话需连贯） | 图像生成（各场景独立） |
| 实现方式 | 节点 post 返回 "next" 连自身 | 继承 BatchNode，prep 返回列表 |
| 结果累积 | post 中 append 到 shared | 框架自动收集 exec 返回值列表 |

在 Wan-Video 流水线中：
- **脚本生成**需要对话上下文 → 自环迭代
- **图像/音频/视频生成**各场景独立 → BatchNode 批量处理

## 自环模式的通用模板

```python
class IterativeNode(Node):
    def prep(self, shared):
        idx = shared.get("current_idx", 0)
        items = shared["items"]
        if idx >= len(items):
            return None
        return {"item": items[idx], "idx": idx, "results": shared["results"]}

    def exec(self, data):
        if data is None:
            return None
        # 处理单个 item，可访问之前的 results 作为上下文
        return process(data["item"], data["results"])

    def post(self, shared, prep_res, exec_res):
        if exec_res is None:
            shared["current_idx"] = 0
            return "done"
        shared["results"].append(exec_res)
        shared["current_idx"] += 1
        if shared["current_idx"] >= len(shared["items"]):
            shared["current_idx"] = 0
            return "done"
        return "next"

# 连接
node - "next" >> node
node - "done" >> next_node
```

## 注意事项

1. **重置索引**：循环结束时务必将 `current_idx` 重置为 0，避免 Flow 重新运行时索引异常
2. **防御性拷贝**：向 exec 传递累积数据时使用 `.copy()`，防止 exec 中的意外修改影响 shared
3. **终止条件**：prep 返回 `None` 和 post 返回 `"done"` 需要一致，避免死循环或提前退出
4. **缓存策略**：重试时禁用缓存，确保 LLM 有机会生成不同输出
5. **断言校验**：在 exec 中对 LLM 输出做格式断言，异常会触发 PocketFlow 的重试机制
