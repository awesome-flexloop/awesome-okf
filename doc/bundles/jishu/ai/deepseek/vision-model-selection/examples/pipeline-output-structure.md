---
type: Example
title: 视觉模型输出结构设计示例
description: 视觉模型结构化返回（OCR 文本/物体/位置关系/表格/不确定项五字段）的 JSON Schema 与 Python 调用伪代码
tags: [示例, JSON Schema, 伪代码, 双模型管线, 结构化输出]
generated: { by: "seven-concepts-cmd", at: "2026-08-28T23:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T23:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-hubei
    resource: https://mp.weixin.qq.com/s/iqoikK7m7arGSHnso-q9hQ
    title: 《DeepSeek 多模态视觉实验模型发布！》
---

# 视觉模型输出结构设计示例

双模型协作架构（[视觉-推理双模型协作架构](../concepts/03-vision-reasoning-pipeline.md)）的第一步，是给视觉模型的输出定一个**稳定的结构**：落地时最好让视觉模型只返回 OCR 文本、物体、位置关系、表格和不确定项，再交给 DeepSeek 判断（F-028）。本示例给出五字段结构化返回的 JSON Schema 与 Python 调用伪代码。

> ⚠️ **示意伪代码声明**：以下 schema 与代码为基于博文落地模式（F-028）推导的设计示意，**非官方 API 文档**。字段命名、调用方式与具体参数请以各厂商官方文档为准。

## 设计目标

结构化返回直接服务于协作架构的三大收益：

| 设计约束 | 对应收益 | 事实编号 |
|---------|---------|---------|
| 字段固定、只含感知结果 | 输出 tokens 更少 | F-028、F-029 |
| 结果与图片一一对应、可序列化 | 识别结果能缓存 | F-030 |
| 感知与判断分离 | 避免两个模型重复推理 | F-031 |

## 五字段 JSON 返回示例

以"识别报错弹窗"任务为例（背景见 [成本-场景选型演练](cost-scenario-walkthrough.md)）：

```json
{
  "image_id": "screenshot-20260828-001",
  "ocr_text": "系统提示：操作失败，请稍后重试（错误码 E-1004）",
  "objects": [
    { "label": "错误弹窗", "confidence": 0.98 },
    { "label": "重试按钮", "confidence": 0.95 },
    { "label": "关闭按钮", "confidence": 0.93 }
  ],
  "spatial_relations": [
    { "subject": "错误弹窗", "relation": "包含", "object": "重试按钮" },
    { "subject": "重试按钮", "relation": "相邻", "object": "关闭按钮" }
  ],
  "tables": [],
  "uncertainties": [
    { "field": "ocr_text", "detail": "错误码末位字符识别置信度低" }
  ]
}
```

五个顶层字段严格对应 F-028 的五类感知结果（示例中的数值均为虚构演示数据）：

| 字段 | 对应感知结果 | 事实编号 |
|------|-------------|---------|
| `ocr_text` | OCR 文本 | F-028 |
| `objects` | 物体 | F-028 |
| `spatial_relations` | 位置关系 | F-028 |
| `tables` | 表格 | F-028 |
| `uncertainties` | 不确定项 | F-028 |

`uncertainties` 是字段设计的灵魂：视觉模型拿不准的内容显式暴露出来，交由 DeepSeek 判断（F-028），而不是硬猜或静默丢弃。

## JSON Schema（示意）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "VisionPerceptionResult",
  "type": "object",
  "required": ["image_id", "ocr_text", "objects", "spatial_relations", "tables", "uncertainties"],
  "properties": {
    "image_id": {
      "type": "string",
      "description": "图片唯一标识，兼作缓存键（F-030）"
    },
    "ocr_text": {
      "type": "string",
      "description": "OCR 文本（F-028）"
    },
    "objects": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      },
      "description": "物体清单（F-028）"
    },
    "spatial_relations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "subject": { "type": "string" },
          "relation": { "type": "string" },
          "object": { "type": "string" }
        }
      },
      "description": "位置关系（F-028）"
    },
    "tables": {
      "type": "array",
      "items": {
        "type": "array",
        "items": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "description": "表格按行列二维结构转写（F-028）"
    },
    "uncertainties": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "field": { "type": "string" },
          "detail": { "type": "string" }
        }
      },
      "description": "不确定项，交由 DeepSeek 判断（F-028）"
    }
  }
}
```

## Python 调用伪代码

```python
def perceive_then_judge(image, question):
    """视觉模型做感知，DeepSeek 做判断（F-028）。

    示意伪代码：基于博文落地模式（F-028）推导，非官方 API 文档。
    """
    # 0) 缓存命中则直接进入判断（F-030）
    cached = cache.get(image.id)
    if cached:
        perception = cached
    else:
        # 1) 视觉侧：按场景选型（零成本档可用 GLM-4.6V-Flash，F-010）
        #    只要求返回五字段结构（F-028），控制输出 tokens（F-029）
        perception = vision_model.parse(
            image=image,
            schema=VISION_PERCEPTION_SCHEMA,   # 上文五字段 schema
            prompt="只提取 OCR 文本、物体、位置关系、表格与不确定项，不要下结论",
        )
        cache.put(image.id, perception)         # 识别结果缓存（F-030）

    # 2) 判断侧：感知结果 + 问题交给 DeepSeek（F-024、F-028）
    #    判断收敛在 DeepSeek，避免两个模型重复推理（F-031）
    answer = deepseek.chat(
        system="你是判断模块。基于视觉感知结果回答，不要重复识别。",
        user={
            "perception": perception,           # 结构化感知结果
            "question": question,
        },
    )
    return answer
```

## 设计要点回溯

- **只感知、不下结论**：视觉模型的 prompt 与 schema 都限制其输出感知五字段（F-028），从源头减少输出 tokens（F-029）；
- **缓存以图片为键**：感知结果只依赖图片内容、不依赖下游问题，识别结果可缓存（F-030）；
- **判断单点收敛**：所有问题在 DeepSeek 侧回答，避免两个模型重复推理（F-031）；本地隐私场景下 MiniCPM-V 提取、DeepSeek 分析是同一模式（F-024）；
- **不确定项显式化**：`uncertainties` 让视觉模型的低置信度内容流向判断侧，而不是被静默丢弃（F-028）。

## 相关示例

- [成本-场景选型演练](cost-scenario-walkthrough.md) — 视觉侧模型怎么按成本选
- [选型决策树](selection-decision-tree.md) — 选型的图形化路径
