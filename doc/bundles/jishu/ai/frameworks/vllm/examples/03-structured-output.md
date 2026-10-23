---
type: Example
title: "示例 03：结构化输出（Structured Outputs）"
description: "在 vllm serve 上开启结构化输出——--structured-outputs-config.backend 选择后端、请求级 structured_outputs（json/regex/choice/grammar/structural_tag）、StructuredOutputsParams 离线用法，附 v0.12 起 guided_* 旧 API 迁移说明
tags: [vllm, example, structured-outputs, json-schema, xgrammar, regex, constrained-decoding]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-structured
    resource: /references/source-map.md
    title: vllm/v1/structured_output/ 与 docs/features/structured_outputs.md（本地检出）
---

# 示例 03：结构化输出（Structured Outputs）

结构化输出让解码过程**只能产出符合约束的 token**，把「模型偶尔吐出非法 JSON」变成确定性合法。v0.32 的参数名是 `structured_outputs`（F-143）；旧的 `guided_json`/`guided_regex`/`guided_choice` 等字段已在 v0.12.0 移除，见文末迁移表。

## 启动带结构化输出的服务

```bash
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
  --structured-outputs-config.backend xgrammar
```

| 后端 | 源码文件 | 特点 |
|------|---------|------|
| `xgrammar` | `backend_xgrammar.py` | 编译为 token mask，开销低，**默认推荐** |
| `guidance` | `backend_guidance.py` | Guidance/llguidance 生态，控制流强 |
| `outlines` | `backend_outlines.py` | Outlines 生态，正则友好 |
| `lm-format-enforcer` | `backend_lm_format_enforcer.py` | 轻量格式强制，依赖少 |

`--structured-outputs-config.backend` 缺省为 `auto`，按请求细节自动挑选后端（F-143）。正则语法随后端而异：xgrammar/guidance/outlines 用 Rust 风格正则，lm-format-enforcer 用 Python `re`。

## 请求级 JSON schema（OpenAI API）

```python
from openai import OpenAI
import json

client = OpenAI(base_url="http://localhost:8000/v1", api_key="-")

json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "capital": {"type": "string"},
        "population_millions": {"type": "number"},
    },
    "required": ["name", "capital", "population_millions"],
}

completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[{"role": "user", "content": "Tell me about France."}],
    extra_body={"structured_outputs": {"json": json_schema}},
)
print(completion.choices[0].message.content)
data = json.loads(completion.choices[0].message.content)  # 必然可解析
```

`extra_body={"structured_outputs": {...}}` 内可用键：`choice`（枚举）、`regex`、`json`、`grammar`（CFG）、`structural_tag`（标签内 schema）（F-143）。

## 离线模式同款

```python
from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams

llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct")

sp = SamplingParams(
    max_tokens=256,
    structured_outputs=StructuredOutputsParams(json=json_schema),
)
out = llm.generate(["Tell me about Japan."], sp)
print(out[0].outputs[0].text)
```

`StructuredOutputsParams` 定义在 `vllm/sampling_params.py`，可选项与在线 `structured_outputs` 键一一对应（json/regex/choice/grammar/structural_tag）。

## 工具调用（Tool Calling）

结构化输出是 function calling 的地基：把工具签名做成 schema，模型输出可直接 `json.loads` 后分发执行。chat completions 传 `tools=[...]` 时服务端自动应用约束，详见 [08 在线服务](../concepts/08-online-serving.md)。

## v0.12.0 起旧 API 迁移表

| 旧字段（已移除） | 新写法 |
|-----------------|--------|
| `guided_json` | `{"structured_outputs": {"json": ...}}` 或 `StructuredOutputsParams(json=...)` |
| `guided_regex` | `{"structured_outputs": {"regex": ...}}` |
| `guided_choice` | `{"structured_outputs": {"choice": ...}}` |
| `guided_grammar` | `{"structured_outputs": {"grammar": ...}}` |
| `guided_whitespace_pattern` | `{"structured_outputs": {"whitespace_pattern": ...}}` |
| `structural_tag` | `{"structured_outputs": {"structural_tag": ...}}` |
| `guided_decoding_backend` | 从请求中删除，改用服务端 `--structured-outputs-config.backend` |

## 性能提示

- mask 编译有一次性开销，**同一 schema 重复请求命中缓存**；schema 多变时优先稳定 schema。
- 结构化输出增加单步解码开销（随后端与 schema 复杂度变化，以实测为准）。
- 与[投机解码](../concepts/11-speculative-decoding.md)可叠加：先加速解码，再约束输出合法性。

## 相关阅读

- [08 在线服务与 API](../concepts/08-online-serving.md)：tool calling 与 chat 模板
- [13 进阶主题](../concepts/13-advanced.md)：四后端源码位置与统一接口
- [04 吞吐基准测试](04-benchmarking.md)：量化结构化输出的开销
