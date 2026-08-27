---
type: concept
title: "分页与模型管理"
description: "掌握 SDK 分页机制：list 类 API 的分页迭代器模式、SyncPage/AsyncPage 自动分页、分页参数（limit/after_id/before_id），以及 Models 资源查询可用模型、Batches API 批量消息处理。"
tags: [pagination, models, batches, list-api, auto-paging, model-ids]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-007
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
  - id: F-016~F-025
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
  - id: F-021~F-023
    resource: /python-sdk/references/messages-api.md
    title: "Anthropic Python SDK 消息 API 与流式处理参考"
---

# 分页与模型管理

当你需要获取列表类数据（如列出所有可用模型、查询批量任务、列出已上传文件）时，API 不会一次性返回所有结果——数据量可能很大，一次性返回既慢又浪费资源。Anthropic API 使用标准的**分页（Pagination）**机制，每页返回有限数量的结果，通过游标（cursor）获取下一页。SDK 封装了分页逻辑，提供了简洁的自动迭代接口。

本文档将讲解 SDK 的分页机制、如何列出和查询 Claude 模型、模型命名规则、已废弃模型列表，以及消息批处理（Batches API）的基本概念。

## 为什么需要分页

列表类 API（如 `models.list()`）返回的数据可能随时间增长：
- Anthropic 不断发布新模型，模型列表会越来越长
- 批量消息任务会累积
- 上传的文件会越来越多

如果每次都返回全量数据：
1. **响应慢**：数据量大时网络传输时间长
2. **浪费资源**：很多时候你只需要前几条结果
3. **不稳定**：超大响应可能超时或被截断

分页通过"每次取一小页"解决了这些问题，而 SDK 的自动分页迭代器让你几乎感知不到分页的存在。

## Models 资源：查询可用模型

`client.models` 是模型管理资源（懒加载属性），提供两个核心方法：

| 方法 | 用途 |
|------|------|
| `models.list()` | 列出当前 API Key 可用的所有 Claude 模型 |
| `models.retrieve(model_id)` | 获取指定模型的详细信息 |

### models.list()：列出可用模型

`models.list()` 返回模型列表，支持分页。最基础的用法：

```python
from anthropic import Anthropic

client = Anthropic()

# 列出所有可用模型
models_page = client.models.list()

# models_page 是一个分页对象，可以直接迭代获取该页的模型
for model in models_page:
    print(f"- {model.id}: {model.display_name}")
```

但这只返回第一页。要获取**所有**模型，使用 `auto_paging_iter()` 自动分页迭代器：

```python
# auto_paging_iter() 自动处理分页，迭代所有结果
all_models = []
for model in client.models.list().auto_paging_iter():
    all_models.append(model)
    print(f"- {model.id}")
    if model.display_name:
        print(f"  显示名: {model.display_name}")

print(f"\n共 {len(all_models)} 个可用模型")
```

`auto_paging_iter()` 会在后台自动请求下一页，直到所有结果都被迭代完，你不需要手动处理 `after_id` 游标。

### models.retrieve()：获取单个模型信息

如果你知道模型 ID，可以直接获取其详细信息：

```python
model = client.models.retrieve("claude-3-5-sonnet-latest")

print(f"模型 ID: {model.id}")
print(f"显示名: {model.display_name}")
print(f"创建时间: {model.created_at}")
```

### 分页参数

`list()` 方法接受三个常用分页参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `limit` | `int` | 每页返回的条目数（大小限制） |
| `after_id` | `str` | 游标：返回 ID 大于此值的条目（用于获取下一页） |
| `before_id` | `str` | 游标：返回 ID 小于此值的条目（用于获取上一页） |

**手动分页示例**（如果你需要精确控制分页）：

```python
# 第一页：取 10 条
page1 = client.models.list(limit=10)
print("=== 第一页 ===")
for model in page1:
    print(f"- {model.id}")

# 获取下一页：使用最后一个条目的 ID 作为 after_id
if page1.has_more:
    last_id = page1.data[-1].id
    page2 = client.models.list(limit=10, after_id=last_id)
    print("\n=== 第二页 ===")
    for model in page2:
        print(f"- {model.id}")
```

分页对象的常用属性：

| 属性/方法 | 说明 |
|----------|------|
| `.data` | 当前页的条目列表 |
| `.has_more` | 布尔值，是否还有下一页 |
| `.auto_paging_iter()` | 返回自动迭代所有页的迭代器 |
| `.next_page()` | 获取下一页（手动分页时使用） |

> 💡 **大多数情况下，你只需要 `auto_paging_iter()`**——它封装了所有游标逻辑，代码最简洁。手动分页仅在需要实现"加载更多"按钮等场景时使用。

## 分页迭代器模式：SyncPage 与 AsyncPage

SDK 的所有 list 类 API 都使用统一的分页模式：
- 同步 API 返回 `SyncPage[T]` 分页对象
- 异步 API 返回 `AsyncPage[T]` 分页对象
- 两者都支持 `auto_paging_iter()`，异步版本是 `async for` 迭代

### 异步分页示例

```python
import asyncio
from anthropic import AsyncAnthropic

async def list_all_models():
    client = AsyncAnthropic()
    
    # 异步自动分页迭代
    count = 0
    async for model in client.models.list().auto_paging_iter():
        print(f"- {model.id}")
        count += 1
    
    print(f"\n共 {count} 个模型")

asyncio.run(list_all_models())
```

其他支持分页的资源：
- `client.files.list()` — 列出已上传文件
- `client.beta.agents.list()` — 列出托管智能体
- `client.beta.memory_stores.memories.list()` — 列出记忆条目
- 以及所有其他 `.list()` 方法

分页模式是完全一致的，学会一个就学会了全部。

## Claude 模型命名规则

Anthropic 模型 ID 遵循统一的命名规范：`claude-{family}-{version}-{date}` 或 `claude-{family}-latest`。

### 命名结构解析

以 `claude-3-5-sonnet-20241022` 为例：

```
claude-3-5-sonnet-20241022
       ↑   ↑    ↑     ↑
       |   |    |     └─ 发布日期：2024年10月22日
       |   |    └─────── 模型家族：sonnet（平衡型）
       |   └──────────── 版本：3.5 代
       └──────────────── 品牌前缀：claude
```

### 模型家族对比

| 家族后缀 | 定位 | 特点 | 适用场景 |
|---------|------|------|---------|
| `opus` | 最强旗舰 | 推理能力最强，智能程度最高 | 复杂分析、深度推理、数学证明 |
| `sonnet` | 平衡之选 | 智能与速度的平衡，性价比高 | **大多数应用的首选**，对话、内容生成 |
| `haiku` | 快速轻量 | 速度最快，成本最低 | 简单任务、分类、提取、实时应用 |

### latest 后缀 vs 固定日期

模型 ID 有两种形式：

| 形式 | 示例 | 说明 | 推荐场景 |
|------|------|------|---------|
| `{family}-latest` | `claude-3-5-sonnet-latest` | 始终指向该家族最新版本 | 开发、原型、不需要版本锁定的场景 |
| `{family}-{date}` | `claude-3-5-sonnet-20241022` | 固定指向特定日期发布的版本 | 生产环境，确保行为可复现 |

**最佳实践**：
- 开发阶段用 `-latest`，自动获取新功能
- 生产环境用固定日期版本，避免模型更新导致行为变化
- 定期测试新版本，验证后再升级生产版本

### 常用模型 ID 参考

基于 SDK 中的模型信息，常用模型包括：

| 模型 ID | 说明 |
|---------|------|
| `claude-3-5-sonnet-latest` | Claude 3.5 Sonnet 最新版（推荐大多数场景使用） |
| `claude-3-5-haiku-latest` | Claude 3.5 Haiku 最新版（最快） |
| `claude-opus-4-latest` | Claude Opus 4 最新版（最强推理） |
| `claude-sonnet-4-20250514` | Claude Sonnet 4（2025年5月14日版本） |
| `claude-haiku-4-20250514` | Claude Haiku 4（2025年5月14日版本） |
| `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet 固定版本 |

> ⚠️ **模型列表会更新**：以上是常见模型，实际可用模型请通过 `client.models.list()` 查询你的 API Key 能访问的完整列表。新模型会持续发布，旧模型可能被废弃。

### 已废弃模型（DEPRECATED_MODELS）

SDK 中维护了一个 `DEPRECATED_MODELS` 字典，列出了已废弃的模型。使用废弃模型会收到警告或错误。已废弃的模型包括：

| 模型 ID | 说明 |
|---------|------|
| `claude-1.3` | Claude 1.x 早期版本 |
| `claude-instant-1.2` | Claude Instant 旧版 |
| `claude-3-sonnet-20240229` | Claude 3 Sonnet（已被 3.5 替代） |
| `claude-3-opus-20240229` | Claude 3 Opus（已被更新版本替代） |

新代码不应使用这些模型，旧代码应尽快迁移到新版本。

### 模型 token 限制

SDK 中还定义了 `MODEL_NONSTREAMING_TOKENS` 常量，部分模型在非流式模式下有 8192 token 的输出限制（如 `claude-opus-4-20250514`）。流式模式不受此限制。需要长输出时：
- 使用流式模式（`stream=True`）
- 或者分块生成，通过多轮对话续接

另外，`MODELS_TO_WARN_WITH_THINKING_ENABLED` 列出了启用 Extended Thinking 时需要特别注意的模型（如 `claude-opus-4-6`、`claude-mythos-preview`）。

## Batches API：消息批处理

`client.messages.batches` 提供消息批处理能力，允许你一次性提交大量消息请求，异步处理后获取结果。这适合不需要实时响应的批量任务场景。

### 什么场景用 Batches？

- **批量评估/标注**：对成百上千个 prompt 运行模型，收集结果
- **数据处理**：批量分类、提取、总结大量文档
- **离线任务**：不需要即时返回的后台任务

Batches 的优势：
- 更高的速率限制
- 更低的成本（通常有折扣）
- 不阻塞实时请求
- 可以稍后查询结果

### Batches 资源的方法

`client.messages.batches` 是 `Batches` 实例（通过 `@cached_property` 懒加载），提供以下方法：

| 方法 | 用途 |
|------|------|
| `batches.create(...)` | 创建一个新的批量任务 |
| `batches.list()` | 列出批量任务（分页） |
| `batches.retrieve(batch_id)` | 获取批量任务状态和结果 |
| `batches.cancel(batch_id)` | 取消正在处理的批量任务 |

### 批处理基本流程

1. **创建批量任务**：提交一组消息请求
2. **轮询状态**：任务处理中，定期查询状态
3. **获取结果**：任务完成后，下载结果

```python
from anthropic import Anthropic

client = Anthropic()

# 1. 创建批量任务（伪代码，实际参数参考 API 文档）
# batch = client.messages.batches.create(
#     requests=[
#         {"custom_id": "req1", "params": {...}},
#         {"custom_id": "req2", "params": {...}},
#         ...
#     ]
# )
# print(f"批量任务已创建: {batch.id}")

# 2. 列出批量任务
for batch in client.messages.batches.list().auto_paging_iter():
    print(f"- {batch.id}: {batch.processing_status}")
```

> 📝 **Batches API 详细用法**：批处理是进阶功能，具体请求格式和结果处理请参考 Messages API 参考文档和官方 API 文档。

## 代码示例：模型列表查询工具

下面是一个实用的小工具，列出并分组显示所有可用模型：

```python
from anthropic import Anthropic

def list_models_summary():
    """列出所有可用模型并按家族分组"""
    client = Anthropic()
    
    models_by_family = {}
    
    print("正在获取模型列表...\n")
    
    for model in client.models.list().auto_paging_iter():
        model_id = model.id
        
        # 提取家族名称
        if "opus" in model_id:
            family = "Opus（旗舰）"
        elif "sonnet" in model_id:
            family = "Sonnet（平衡）"
        elif "haiku" in model_id:
            family = "Haiku（快速）"
        else:
            family = "其他"
        
        if family not in models_by_family:
            models_by_family[family] = []
        models_by_family[family].append(model_id)
    
    # 按家族输出
    for family, models in sorted(models_by_family.items()):
        print(f"=== {family} ===")
        for mid in sorted(models):
            print(f"  - {mid}")
        print()

def get_model_recommendation(task: str) -> str:
    """根据任务类型推荐模型"""
    task_lower = task.lower()
    
    if any(k in task_lower for k in ["复杂", "推理", "数学", "分析", "深度"]):
        return "claude-opus-4-latest"
    elif any(k in task_lower for k in ["快速", "分类", "提取", "简单", "实时"]):
        return "claude-3-5-haiku-latest"
    else:
        return "claude-3-5-sonnet-latest"

if __name__ == "__main__":
    list_models_summary()
    print(f"通用对话推荐模型: {get_model_recommendation('通用')}")
    print(f"复杂分析推荐模型: {get_model_recommendation('复杂推理')}")
    print(f"快速分类推荐模型: {get_model_recommendation('实时分类')}")
```

## 异步分页与资源操作

所有分页和模型操作都有对应的异步版本，API 完全对称：

```python
import asyncio
from anthropic import AsyncAnthropic

async def async_model_ops():
    client = AsyncAnthropic()
    
    # 异步列出所有模型
    print("=== 异步获取模型列表 ===")
    async for model in client.models.list().auto_paging_iter():
        print(f"- {model.id}")
    
    # 异步获取模型信息
    sonnet = await client.models.retrieve("claude-3-5-sonnet-latest")
    print(f"\nSonnet 信息: {sonnet.display_name}")

asyncio.run(async_model_ops())
```

## 常见问题

### Q: 为什么 `models.list()` 返回空？
A: 检查你的 API Key 是否有效、是否有模型访问权限。某些模型（如最新的 Opus）可能需要单独申请访问。

### Q: 如何知道我该用哪个模型？
A: 默认用 `claude-3-5-sonnet-latest`，这是大多数场景的最佳选择。对速度要求高用 haiku，对智能要求高用 opus。

### Q: 分页每页默认多少条？
A: 默认 limit 由 API 服务端决定（通常是 20 或 50），你可以通过 `limit` 参数自定义。

### Q: `auto_paging_iter()` 会一次性加载所有数据到内存吗？
A: 不会。它按页懒加载——迭代到当前页末尾时才请求下一页，内存中始终只保留当前页的数据。

### Q: Batches 和 stream 有什么区别？
A:
- **stream（流式）**：单个请求，实时返回 token，需要保持连接，用于实时交互
- **batches（批处理）**：提交大量请求，异步离线处理，稍后取结果，用于批量任务

## 相关概念

- [整体架构概览](/python-sdk/concepts/00-overview.md) — 回顾 SDK 架构和懒加载资源机制
- [Messages API 基础](/python-sdk/concepts/02-messages-basics.md) — model 参数和 messages.create 基础
- [客户端初始化与配置](/python-sdk/concepts/01-client-init.md) — 配置 API Key 和超时等客户端选项
- [Anthropic Python SDK 消息 API 与流式处理参考](/python-sdk/references/messages-api.md) — Batches 资源和 DEPRECATED_MODELS 的完整参考
- [Anthropic Python SDK 客户端入口与基础设施参考](/python-sdk/references/sdk-client.md) — client.models 和 client.files 资源的 API 参考
