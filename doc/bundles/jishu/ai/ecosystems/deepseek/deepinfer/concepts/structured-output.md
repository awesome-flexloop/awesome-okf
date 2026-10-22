---
type: concept
scope: deepinfer
name: DeepInfer 结构化输出
version: "0.1.0"
source: deepinfer/structure_output/, examples/_structured_output.py
description: 结构化输出——xgrammar 文法编译、GrammarMatcher 增量掩码与编译推理解耦
sources:
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践
---

# 结构化输出（Structured Output）

结构化输出用于约束模型输出严格符合指定格式（JSON Schema、正则表达式、EBNF 文法），是可靠 Agent 工具调用的基础能力。

---

## 一、工作流程

DeepInfer 的结构化输出分两阶段：

```
编译阶段（独立 SO 机器）        运行时（推理引擎内）
┌──────────────────────┐      ┌────────────────────────────┐
│ 格式约束 → 语法自动机   │ ───→ │ 每步 decode：更新自动机 →     │
│ （异步进行，请求进入     │      │ 判断合法 token 集合 → 生成    │
│   engine 前取回结果）   │      │ mask 作用于采样逻辑          │
└──────────────────────┘      └────────────────────────────┘
```

**编译与推理解耦**：SO 编译异步进行，请求在进入 engine 前取回编译结果，编译不阻塞解码关键路径。

## 二、代码组织

| 模块 | 职责 |
|---|---|
| `structure_output/compiler.py` | `XGrammarCompiler` 封装 xgrammar `GrammarCompiler`；`dispatch_and_compile` 分发三种 `schema_type`——`json`（strict 模式）/ `regex` / `ebnf`；默认 10 GiB 编译缓存上限（防 CVE-2025-32381 DoS） |
| `structure_output/matcher.py` | `XGrammarMatcher` 封装 xgrammar `GrammarMatcher`，内置 KMP 失败函数支持 trigger-token 回滚；`MAX_ROLLBACK_TOKENS = DEEPINFER_USE_NEXTN_DECODE + 2`（与推测解码回退对齐） |
| `structure_output/mask.py` | 分配 vocab bitmask 并经 `tilelang_ops/structure_output.apply_token_bitmask_by_step_inplace`（TileLang kernel）就地施加 |
| `structure_output/so_matcher_builder.py` | `SOMatcherBuilder` 用线程池（默认 4 线程，`DEEPINFER_SO_BUILDER_CPUS`）+ CPU 亲和性绑定离线编译/构建 matcher，支持 `serialized` 形式传递 |

## 三、用户接口：so_args

结构化约束经 `SamplingParams` 的 `so_args` 传入，三种 `schema_type`（源自 `examples/_structured_output.py`）：

```python
from deepinfer import SamplingParams
import json

# 正则约束：输出形如 "AB-123"
params_regex = SamplingParams(
    temperature=0, max_tokens=128,
    so_args={"schema_type": "regex", "schema": r"[A-Z]{2}-[0-9]{3}"},
)

# JSON Schema 约束：注意 schema 必须序列化为字符串
schema = {
    "type": "object",
    "properties": {"answer": {"type": "string"}, "level": {"type": "integer"}},
    "required": ["answer"],
}
params_json = SamplingParams(
    temperature=0, max_tokens=128,
    so_args={"schema_type": "json", "schema": json.dumps(schema)},
)

# EBNF 文法约束
params_ebnf = SamplingParams(
    temperature=0, max_tokens=128,
    so_args={"schema_type": "ebnf", "schema": 'root ::= "answer=" ("yes" | "no") ";level=" [1-3]'},
)
```

**约定**：JSON Schema 必须 `json.dumps` 序列化为字符串后传入，而非直接传 dict；正常结束断言 `finish_reason == "stop"` 且最后一个 token 是 EOS。

## 四、验证方式

`python examples/offline_inference.py --check_structured_output` 复用同一个 LLM 实例，在样例输出与 decode PPL 之后运行 regex / JSON / EBNF 三类结构化输出检查并验证正常 EOS 终止，任一失败即判定运行失败。`tests/models/test_offline_inference.py` 显式启用该开关，单次运行同时校验 PPL 与结构化输出。

## 五、相关环境变量

| 变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_XGRAMMAR_TIMEOUT` | 20 | SO 编译超时（秒） |
| `DEEPINFER_XGRAMMAR_CACHE_LIMIT_BYTES` | 10 GiB | 编译缓存上限（DoS 防护） |
| `DEEPINFER_SO_BUILDER_CPUS` | 4 | SO matcher 构建线程数 |
