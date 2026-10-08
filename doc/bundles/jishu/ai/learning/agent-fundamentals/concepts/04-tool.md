---
okf_version: "0.2"
type: Concept
title: "Tool（工具）— 让 AI 动手的能力"
description: "Tool 的定义、为什么需要 Tool、工作流程、常见类型及定义格式。"
tags: ["Tool", "工具调用", "Function Calling", "Tool Use", "API"]
generated: 2026-09-09
verified: 2026-09-09
status: verified
stale_after: "2027-09-09"
sources:
  - "F-031~F-040"
  - "S2: CSDN 镜像"
---

# 04 Tool（工具）— 让 AI 动手的能力

> 对应事实：F-031~F-040
> 知识层级：机制层

---

## 一、为什么需要 Tool？

大模型有个致命缺陷：**纸上谈兵**。

- ❌ 无法获取实时信息（天气、股价、新闻）
- ❌ 无法执行实际操作（读写文件、调用 API）
- ❌ 知识截止到训练数据，无法更新

**Tool 让 AI 从"纸上谈兵"变成真正能动手做事。**

---

## 二、Tool 的工作流程

```
用户："今天上海天气怎么样？"
 ↓
AI："我需要调用天气工具"
 ↓
调用 Tool（城市="上海"，日期="今天"）
 ↓
Tool 执行：请求气象局 API
 ↓
返回结果：{"temp": 25, "weather": "晴"}
 ↓
AI 生成回答："今天上海晴，气温 25°C，适合出行。"
```

---

## 三、常见 Tool 类型

| 类型 | 功能 | 示例 |
|------|------|------|
| **搜索工具** | 搜索互联网 | Google Search、Bing Search |
| **计算工具** | 执行代码 | Python 解释器、Shell 执行 |
| **数据工具** | 读写数据库 | SQL 查询、MongoDB 操作 |
| **文件工具** | 读写文件 | 文档处理、代码编辑 |
| **API 工具** | 调用外部服务 | 天气 API、支付 API |

---

## 四、Tool 的定义格式

Tool 以 JSON Schema 格式定义，供 LLM 理解参数结构：

```json
{
  "name": "get_weather",
  "description": "获取指定城市的天气信息",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "城市名称"
      },
      "date": {
        "type": "string",
        "description": "日期，如'今天'"
      }
    },
    "required": ["city"]
  }
}
```

> **核心认知**：Tool 是 Agent 系统的原子能力单元。一个 Tool = 一个可被 LLM 调用的函数。
