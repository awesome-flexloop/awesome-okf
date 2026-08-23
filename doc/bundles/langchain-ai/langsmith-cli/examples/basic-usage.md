---
type: example
scope: langsmith-cli
name: basic-usage
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: langsmith-cli 基础使用示例——认证、查询 traces/runs、管理数据集与评估器
---

# 基础使用示例

本示例演示 langsmith-cli 的核心工作流：认证 → 查询 traces/runs → 管理数据集与评估器 → JSON 输出供脚本消费。

## 前置条件

- Go 1.25+（从源码构建）或通过安装脚本安装
- LangSmith API Key（从 https://smith.langchain.com 获取）
- 已设置环境变量：

```bash
export LANGSMITH_API_KEY="lsv2_pt_..."
# 可选：自托管 endpoint
# export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
# 可选：默认项目
# export LANGSMITH_PROJECT="my-app"
```

## 示例 1：查询最近 traces

```bash
# 列出最近 5 条 trace（pretty 表格）
langsmith trace list --project my-app --limit 5

# 包含完整字段（metadata + IO + feedback）
langsmith trace list --project my-app --limit 5 --full

# 查看 trace 层级树
langsmith trace list --project my-app --limit 3 --show-hierarchy
```

工作流程：
1. `resolveSessionID` 将 project name "my-app" 解析为 session UUID（带缓存）。
2. `BuildRunQueryParams` 构建 `RunQueryParams`（`IsRoot=true`、`Order=Desc`、limit=5、start_time=7天前）。
3. `queryRunsAuto` 探测部署版本，Cloud 走 v2（SmithDB），旧版自托管走 v1。
4. `extractRunsToMaps` 将 `RunSchema` 归一化为扁平 map。
5. `--format pretty` 下 `output.PrintRunsTable` 渲染表格。

## 示例 2：JSON 输出与 jq 过滤

```bash
# 机器可读 JSON 输出
langsmith --format json trace list --project my-app --limit 10

# 写入文件
langsmith --format json trace list --project my-app -o traces.json

# 配合 jq 提取错误 trace 的 ID 和名称
langsmith --format json trace list --project my-app --error --limit 20 \
  | jq '.[] | {trace_id, name, start_time}'
```

## 示例 3：查询 LLM calls 与 token 统计

```bash
# 列出最近的 LLM calls（默认 50 条）
langsmith run list --project my-app --run-type llm --include-metadata

# 查找高 token 消耗调用（--min-tokens 客户端过滤）
langsmith run list --project my-app --run-type llm --min-tokens 1000 --include-metadata

# 导出为 JSONL
langsmith run export llm_calls.jsonl --project my-app --run-type llm --full --limit 200
```

`run list` 与 `trace list` 的区别：trace 仅查询 root run（`IsRoot=true`），run 可查询任意层级（包括子 LLM/tool 调用）。

## 示例 4：使用过滤器 DSL

```bash
# 按延迟过滤（>5 秒）
langsmith trace list --project my-app --min-latency 5

# 按标签过滤（OR 逻辑）
langsmith trace list --project my-app --tags production,v2

# 按 metadata 过滤
langsmith trace list --project my-app --metadata revision_id=abc123

# 原生 DSL 透传
langsmith run list --project my-app --filter 'eq(status, "error")'

# 组合条件自动用 and() 包裹
langsmith trace list --project my-app \
  --name agent --min-latency 2 --tags prod --error
```

## 示例 5：管理数据集

```bash
# 列出数据集
langsmith dataset list --name-contains eval

# 创建数据集
langsmith dataset create --name "qa-eval-v2" --description "QA pairs for v2"

# 导出数据集
langsmith dataset export qa-eval-v2 ./data.json --limit 500

# 从 JSON 上传
langsmith dataset upload data.json --name new-dataset
```

## 示例 6：上传代码评估器

准备一个 Python 文件 `evals.py`：

```python
def check_accuracy(run, example):
    output = run.get("outputs", {}).get("answer", "")
    expected = example.get("outputs", {}).get("answer", "")
    return {"score": 1.0 if output.strip() == expected.strip() else 0.0}
```

上传到 LangSmith：

```bash
# 离线评估器（关联数据集）
langsmith evaluator upload evals.py \
  --name accuracy \
  --function check_accuracy \
  --dataset qa-eval-v2

# 在线评估器（关联项目，50% 采样）
langsmith evaluator upload evals.py \
  --name latency-check \
  --function check_accuracy \
  --project my-app \
  --sampling-rate 0.5

# 替换已有评估器
langsmith evaluator upload evals.py \
  --name accuracy --function check_accuracy \
  --dataset qa-eval-v2 --replace --yes
```

CLI 会自动：
1. 读取文件，按扩展名（`.py`）检测语言为 python。
2. 用正则提取 `check_accuracy` 函数体。
3. 将函数名替换为规范名 `perform_eval`。
4. POST 到 `/api/v1/runs/rules`。

JavaScript/TypeScript 文件（`.js/.ts/.tsx/.mjs`）同理，函数重命名为 `performEval`，箭头函数转换为函数声明。

## 示例 7：查询实验结果

```bash
# 列出数据集的实验
langsmith experiment list --dataset qa-eval-v2

# 获取实验详情
langsmith experiment get my-experiment-2024-01-15
```

输出包含 feedback_stats、run_stats（latency P50、token_count、error_rate、total_cost）和 example_count。

## 示例 8：OAuth 登录与多 Profile

```bash
# OAuth 设备码登录（默认 profile）
langsmith auth login

# 创建命名 profile
langsmith profile create prod
langsmith auth login --profile prod

# 使用指定 profile
langsmith --profile prod trace list --project my-app --limit 5

# 查看认证状态
langsmith auth info

# 输出 access token（供其他工具使用）
langsmith auth token
```

## 示例 9：通用 API 调用

当 CLI 未封装某个端点时，使用 `langsmith api` 直接调用：

```bash
# 浏览可用端点
langsmith api ls --tag datasets

# GET 请求
langsmith api sessions?limit=5

# POST 创建资源
langsmith api sessions \
  -F name=my-new-project

# 从 stdin 读取 body
echo '{"name":"test"}' | langsmith api sessions --input -

# 包含响应头
langsmith api sessions/abc-123 -i
```

## 示例 10：导出 traces 到文件

```bash
# 每个 trace 一个 JSONL 文件
langsmith trace export ./traces --project my-app --limit 20 --full

# 自定义文件名
langsmith trace export ./traces --project my-app \
  --filename-pattern "{name}_{trace_id}.jsonl"
```

## 进一步阅读

- [命令参考](/langchain-ai/langsmith-cli/references/commands) — 完整命令与标志文档
- [CLI 命令体系](/langchain-ai/langsmith-cli/concepts/cli-commands) — 过滤器、分页、输出机制
- [API 客户端架构](/langchain-ai/langsmith-cli/concepts/api-client) — v1/v2 适配与认证细节
