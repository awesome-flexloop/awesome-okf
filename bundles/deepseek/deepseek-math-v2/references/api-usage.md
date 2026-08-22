---
type: reference
scope: deepseek-math-v2
name: api-usage
description: DeepSeekMath-V2 API 调用方式、推理参数和 prompt 模板
---

# API 使用参考

DeepSeekMath-V2 基于 DeepSeek-V3.2-Exp-Base，通过 OpenAI 兼容 API 调用。

## API 基础配置

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="your-api-key",       # DeepSeek API Key
    timeout=300000,               # 5 分钟超时（数学推理可能耗时较长）
    base_url="https://api.deepseek.com"  # DeepSeek API 端点
)
```

## 基本调用

```python
response = await client.chat.completions.create(
    messages=[{"role": "user", "content": problem}],
    stream=False,
    temperature=0.7,
    top_p=0.95,
    max_tokens=32768,
    max_total_tokens=32768
)

reasoning_content = response.choices[0].message.reasoning_content.strip()  # 思考链
content = response.choices[0].message.content.strip()                        # 最终答案
finish_reason = response.choices[0].finish_reason
```

模型输出包含 `reasoning_content`（`<think>` 标签内的推理过程）和 `content`（最终解答），输出格式为：

```
<think>
{reasoning_content}
</think>
{content}
```

## 批量推理参数

参考仓库 `inference/generate.py` 的多进程异步推理：

| 参数 | 说明 | 默认值 |
|---|---|---|
| `--num_processes` | 并发进程数 | 16 |
| `--batch_size` | 每批请求数 | 16 |
| `--temperature` | 采样温度 | 必须指定 |
| `--top_p` | Top-p 采样 | 必须指定 |
| `--max_tokens` | 最大生成长度 | 必须指定 |
| `--n` | 每题采样数 | 必须指定 |

### 批量推理脚本支持断点续传

- 使用 `.meta` 文件（pickle 格式）记录已完成批次
- 如 `n` 或 `batch_size` 变化需删除旧的 meta 文件

## Prompt 模板

仓库 `inference/math_templates.py` 定义了四种核心 prompt 模板。

### 1. 证明生成（proof_generation）

用于生成数学证明，模型需先求解再自评：

```
Your task is to solve a given problem...
Your final response should be in the following format:

## Solution
... // 完整证明过程

## Self Evaluation
Here is my evaluation of the solution:
... // 详细的步骤正确性分析
Based on my evaluation, the final overal score should be:
\boxed{{...}} // 0, 0.5, 或 1
```

关键要求：
- 模型必须先生成完整解答，再进行自评
- 评分标准：1（完全正确）/ 0.5（大体正确但有细节遗漏或小错）/ 0（致命错误或未解决问题）
- 引用论文结论必须同时给出证明，否则不能得 1 分
- 禁止"作弊"——发现问题必须如实报告，错误声称正确会被惩罚

### 2. 证明验证（proof_verification）

作为验证器评估已有证明的质量：

```
Your task is to evaluate the quality of a solution to a problem...
Here is my evaluation of the solution:
...
Based on my evaluation, the final overal score should be:
\boxed{{...}}
```

### 3. 元验证（meta_verification）

评估验证器本身的判定是否合理，从三方面分析：
- **步骤重述检查**：验证器对解决方案的重述是否准确
- **缺陷分析**：指出的错误是否确实存在
- **表达分析**：验证器的表述是否准确
- **评分分析**：最终评分与发现的缺陷是否匹配

### 4. 证明精炼（proof_refinement）

基于已有候选解和评估，生成更优解：

```
Here are some solution sample(s) along with their correctness evaluation(s).
You should provide a better solution by solving issues mentioned in the evaluation(s),
or by re-using promising ideas mentioned in the solution sample(s), or by doing both.
```
