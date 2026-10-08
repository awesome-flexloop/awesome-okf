---
type: Reference
title: langchain-core 核心抽象源码信源
description: Runnable 协议、Serializable 序列化基类与版本信息的源码溯源
tags: [langchain, runnable, serializable, source]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: src-runnables-base
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/runnables/base.py
    title: runnables/base.py
  - id: src-serializable
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/load/serializable.py
    title: load/serializable.py
  - id: src-config
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/runnables/config.py
    title: runnables/config.py
  - id: src-version
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/version.py
    title: version.py
---

# 核心抽象源码信源

本信源登记 langchain-core 中 `Runnable` 协议、`Serializable` 序列化基类与 `RunnableConfig` 的源码位置，供概念文档溯源引用。

## 版本信息

- `langchain_core/version.py:1` —— `VERSION = "1.6.1"`。

## Runnable 协议（runnables/base.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `Runnable(ABC, Generic[Input, Output])` | 133 | 所有可执行组件的抽象基类 |
| `Runnable.get_name` | 270 | 获取运行名称 |
| `Runnable.input_schema` / `get_input_schema` | 375 / 379 | 输入 Pydantic schema |
| `Runnable.output_schema` / `get_output_schema` | 451 / 458 | 输出 schema |
| `Runnable.config_specs` / `config_schema` | 530 / 534 | 可配置字段 schema |
| `Runnable.get_graph` | 593 | 返回执行图 `Graph` |
| `Runnable.__or__` / `__ror__` / `pipe` | 628 / 676 / 724 | 管道组合运算符 |
| `Runnable.pick` | 773 | 从字典输出中选取键 |
| `Runnable.assign` | 836 | 向字典输出追加键 |
| `Runnable.invoke`（抽象） | 885 | 同步单输入执行 |
| `Runnable.ainvoke` | 907 | 异步单输入（默认线程池） |
| `Runnable.batch` | 930 | 批量并行执行 |
| `Runnable.batch_as_completed` | 982 | 批量完成即产出 |
| `Runnable.stream` / `astream` | 1193 / 1214 | 流式输出 |
| `Runnable.astream_log` | 1237 | 流式日志补丁 |
| `Runnable.astream_events` | 1343 | 流式事件（v1/v2） |
| `Runnable.stream_events` | 1674 | 同步流式事件 |
| `Runnable.transform` | 1760 | 输入迭代器→输出迭代器 |
| `Runnable.bind` | 1851 | 绑定 kwargs |
| `Runnable.with_config` | 1885 | 绑定配置 |
| `Runnable.with_retry` | 2101 | 重试包装 |
| `Runnable.with_fallbacks` | 2188 | 降级包装 |
| `Runnable.map` | 2165 | 逐元素映射 |
| `Runnable.as_tool` | 2708 | 转为 BaseTool（beta） |
| `RunnableSerializable` | 2827 | 可序列化 Runnable |
| `RunnableSerializable.configurable_fields` | 2855 | 声明可运行时配置字段 |
| `RunnableSerializable.configurable_alternatives` | 2913 | 声明可运行时替换实现 |
| `RunnableSequence` | 3075 | 顺序组合（`\|`） |
| `RunnableParallel` | 3864 | 并行组合（字典） |
| `RunnableGenerator` | 4399 | 生成器适配 |
| `RunnableLambda` | 4703 | 函数适配 |
| `RunnableEachBase` / `RunnableEach` | 5577 / 5734 | map 操作实现 |
| `RunnableBindingBase` | 5851 | bind/with_config 产物基类 |

## Runnable 配置（runnables/config.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `RunnableConfig(TypedDict, total=False)` | 57 | 执行配置字典 |
| 字段 `tags` | 80 | 标签列表 |
| 字段 `metadata` | 86 | 元数据字典 |
| 字段 `callbacks` | 92 | 回调列表 |
| 字段 `run_name` | 98 | 运行名称 |
| 字段 `max_concurrency` | 103 | 最大并发 |
| 字段 `recursion_limit` | 109 | 递归上限（默认25） |
| 字段 `configurable` | 115 | 运行时配置值 |
| 字段 `run_id` | 124 | 运行 UUID |
| `CONFIG_KEYS` | 131 | 全部8个配置键 |
| `DEFAULT_RECURSION_LIMIT = 25` | 171 | 默认递归上限 |
| `var_child_runnable_config` | 174 | ContextVar，配置自动传播 |
| `ensure_config` | 255 | 补全配置默认值 |
| `get_config_list` | 311 | 将单配置展开为列表 |
| `patch_config` | 357 | 局部修补配置 |
| `merge_configs` | 431 | 合并多个配置 |

## Serializable 序列化（load/serializable.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `BaseSerialized(TypedDict)` | 21 | 序列化产物基类（含 `lc: 1`） |
| `SerializedConstructor` | 34 | 构造函数形式（id + kwargs） |
| `SerializedSecret` | 43 | 秘密字段占位 |
| `SerializedNotImplemented` | 50 | 不可序列化标记 |
| `Serializable(BaseModel, ABC)` | 106 | 可序列化基类 |
| `is_lc_serializable` | 138 | 默认返回 `False` |
| `get_lc_namespace` | 151 | 默认 `__module__.split(".")` |
| `lc_secrets` | 177 | 构造参数→环境变量 ID 映射 |
| `lc_attributes` | 185 | 额外纳入序列化的属性 |
| `lc_id` | 195 | 返回 `[*namespace, classname]` |
| `model_config = ConfigDict(extra="ignore")` | 215 | 忽略额外字段 |
| `to_json` | 227 | 序列化为 JSON 结构 |

## 相关事实

- F-lc-002、F-lc-003（Serializable 与序列化产物类型）
- F-lc-004 ~ F-lc-019（Runnable 及各子类）
- F-lc-020、F-lc-021（RunnableConfig）
- F-lc-001（版本）
