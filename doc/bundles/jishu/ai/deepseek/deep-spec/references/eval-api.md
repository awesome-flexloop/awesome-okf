---
type: api-reference
scope: deep-spec
name: DeepSpec 评估 API 参考
version: "1.0.0"
source: deepspec/eval/base_evaluator.py, deepspec/eval/dspark/evaluator.py, deepspec/eval/dspark/draft_ops.py, deepspec/eval/eagle3/evaluator.py, eval.py
description: DeepSpec 评估器类、投机解码验证框架、DraftProposal/VerificationResult、9个评测任务完整 API 参考
---

# DeepSpec 评估 API 参考

DeepSpec 的评估系统提供了一个通用的投机解码验证框架，通过回调接口支持 DSpark 和 Eagle3 两种草稿模型的评估。评估管线覆盖 9 个标准评测任务，支持接受率统计、置信度校准等指标收集。

---

## 一、评估入口

### 1.1 `eval.py` 入口脚本

```bash
torchrun --nproc_per_node=<num_gpus> eval.py \
    --target_name_or_path <target_model_path> \
    --draft_name_or_path <draft_model_path> \
    [--max-new-tokens 2048] \
    [--temperature 1.0] \
    [--confidence-threshold 0.0] \
    [--tensorboard-dir <dir>] \
    [--step <step>] \
    [--seed 980406]
```

**命令行参数：**

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `--target_name_or_path` | str | 必填 | 目标模型路径或名称 |
| `--draft_name_or_path` | str | 必填 | 草稿模型路径或名称 |
| `--max-new-tokens` | int | 2048 | 最大生成 token 数 |
| `--temperature` | float | 1.0 | 采样温度（0=贪婪解码） |
| `--confidence-threshold` | float | 0.0 | 置信度早停阈值（0=收集校准指标） |
| `--tensorboard-dir` | str | None | TensorBoard 日志目录 |
| `--step` | int | None | TensorBoard 记录的步数 |
| `--seed` | int | 980406 | 随机种子 |

### 1.2 评估器路由

```python
EVALUATORS = {
    "Qwen3DSparkModel": Qwen3DSparkEvaluator,
    "Gemma4DSparkModel": Gemma4DSparkEvaluator,
    "Qwen3Eagle3Model": Qwen3Eagle3Evaluator,
    "Gemma4Eagle3Model": Gemma4Eagle3Evaluator,
    "Eagle3DraftModel": Qwen3Eagle3Evaluator,
}
```

评估器根据 draft 模型 config 中的 `architectures[0]` 自动选择。

### 1.3 评测任务

```python
TASKS = [
    ("gsm8k", 500),          # 数学推理 - 小学数学
    ("math500", 500),        # 数学推理 - 竞赛数学
    ("aime25", 30),          # 数学推理 - AIME 2025
    ("humaneval", 164),      # 代码生成 - HumanEval
    ("mbpp", 256),           # 代码生成 - MBPP
    ("livecodebench", 500),  # 代码生成 - LiveCodeBench
    ("mt-bench", 80),        # 对话 - MT-Bench
    ("alpaca", 500),         # 对话 - Alpaca
    ("arena-hard-v2", 500),  # 对话 - Arena-Hard v2
]
```

每个任务元组为 `(dataset_name, max_samples)`。

---

## 二、核心数据结构

### 2.1 `DraftProposal`

```python
@dataclass
class DraftProposal:
    draft_token_count: int           # 提议的 draft token 数量
    verify_input_ids: torch.Tensor   # 用于验证的输入 token ID
    draft_probs: torch.Tensor | None # draft 模型的概率分布（用于拒绝采样）
```

### 2.2 `DSparkDraftProposal`

```python
@dataclass
class DSparkDraftProposal(DraftProposal):
    confidence_logits: torch.Tensor | None = None  # 置信度预测 logits（DSpark 特有）
```

### 2.3 `VerificationResult`

```python
@dataclass
class VerificationResult:
    target_output: torch.Tensor           # 目标模型输出
    target_probs: torch.Tensor            # 目标模型概率分布
    accept_prefix_mask: torch.Tensor | None  # 接受前缀 mask
    accepted_draft_tokens: int            # 被接受的 draft token 数量
    next_token: torch.Tensor              # 下一 token（从残差分布采样）
    effective_proposal_length: int        # 有效提议长度
    terminated_by_stop_token: bool = False # 是否因 stop token 终止
    committed_tokens: torch.Tensor | None = None  # 已提交的 tokens
```

---

## 三、投机解码核心函数

### 3.1 `verify_draft_tokens`

```python
def verify_draft_tokens(
    *,
    target_model: nn.Module,
    proposal: DraftProposal,
    position_ids: torch.Tensor,
    start: int,
    past_key_values_target,
    temperature: float,
    max_proposal_tokens: int,
    current_token_ids: torch.Tensor | None = None,
    stop_token_ids: list[int] | None = None,
) -> VerificationResult:
    """
    执行投机解码验证：
    
    1. 用目标模型前向计算 target_probs
    2. 逐 token 执行拒绝采样：accept_prob = min(1, target_prob / draft_prob)
    3. 被拒绝位置从残差分布 max(0, target - draft) 归一化后采样补全
    4. 处理 stop token 截断
    5. 返回 VerificationResult
    """
    ...
```

**拒绝采样机制：**
- 对于每个 draft token，从均匀分布 U(0,1) 采样 u
- 若 u < min(1, target_prob / draft_prob)，接受该 token
- 否则拒绝，从残差分布采样新 token，停止后续 draft token 的验证
- 接受的 token 数量即为 `accepted_draft_tokens`

### 3.2 `generate_decoding_sample`

```python
def generate_decoding_sample(
    *,
    target_model: nn.Module,
    input_ids: torch.Tensor,
    max_new_tokens: int,
    max_proposal_tokens: int,
    temperature: float,
    stop_token_ids: list[int] | None,
    init_context: callable,
    propose: callable,
    update: callable,
    post_verify: callable | None = None,
) -> SimpleNamespace:
    """
    通用投机解码生成循环。
    
    回调接口：
    - init_context(initial_output, output_ids, position_ids, num_input_tokens) -> context
      初始化算法状态（如 KV cache、隐状态缓存）
    
    - propose(context, output_ids, position_ids, start, stop_token_ids) -> DraftProposal
      生成 draft 提议
    
    - update(context, verification: VerificationResult) -> None
      根据验证结果更新状态（如裁剪 KV cache、更新隐状态）
    
    - post_verify(proposal: DraftProposal, verification: VerificationResult) -> None
      可选诊断钩子（如收集置信度校准数据）
    
    返回 SimpleNamespace，包含：
    - output_ids: 完整生成的 token 序列
    - acceptance_lengths: 每次验证接受的 token 数列表
    - proposal_lengths: 每次提议的 token 数列表
    - accepted_draft_lengths: 被接受的 draft token 数列表
    - verify_count: 目标模型前向调用次数
    """
    ...
```

---

## 四、BaseEvaluator 基类

```python
class BaseEvaluator:
    def __init__(self, local_rank: int, args: argparse.Namespace):
        """
        初始化评估器：
        1. 初始化分布式环境
        2. 加载目标模型和 draft 模型（BF16, SDPA 注意力）
        3. 初始化 tokenizer
        """
        ...
    
    @property
    def max_proposal_tokens(self) -> int:
        """最大提议 token 数（抽象属性）"""
        ...
    
    def build_models(self):
        """构建目标模型和 draft 模型（抽象方法）"""
        ...
    
    def generate_one_sample(
        self,
        input_ids: torch.Tensor,
        stop_token_ids: list[int] | None = None,
    ) -> SimpleNamespace:
        """生成单个样本（抽象方法）"""
        ...
    
    def run_dataset(self, dataset_name: str, max_samples: int):
        """
        运行单个数据集评估：
        1. 加载数据集
        2. 编码输入
        3. 逐样本调用 generate_one_sample
        4. 收集指标
        """
        ...
    
    def allreduce_response_metrics(self, responses: list) -> dict:
        """跨 rank 汇总指标：acceptance_length_sum、proposal_length_sum、逐位置接受率"""
        ...
    
    def evaluate(self):
        """遍历所有 TASKS 执行评估，输出汇总结果"""
        ...
    
    def build_metrics_row(self, responses: list) -> dict:
        """
        计算汇总指标：
        - draft_tokens_per_proposal: 平均每次提议的 draft token 数
        - acceptance_length: 平均接受长度
        - verify_rate: 目标模型调用率（verify_count / total_tokens）
        - 逐位置 accept_rate
        """
        ...
    
    def clean_up(self):
        """清理分布式环境"""
        ...
```

---

## 五、DSpark 评估器

### 5.1 `Qwen3DSparkEvaluator`

```python
class Qwen3DSparkEvaluator(BaseEvaluator):
    EVAL_ATTN_IMPLEMENTATION = "sdpa"
    
    @property
    def max_proposal_tokens(self) -> int:
        return self.block_size  # 等于 draft 模型配置的 block_size
    
    def build_models(self):
        """
        加载 BF16 的目标模型和 DSpark draft 模型（均使用 SDPA 注意力）。
        校验 target_layer_ids 不含最后一层。
        """
        ...
    
    def _init_context(self, initial_output, output_ids, position_ids, num_input_tokens):
        """初始化 draft DynamicCache 和 target_hidden_states"""
        ...
    
    def _propose(self, context, output_ids, position_ids, start, stop_token_ids):
        """
        调用 forward_dspark_draft_block 和 build_dspark_proposal 生成 DSparkDraftProposal。
        支持基于 confidence head 提前截断。
        """
        ...
    
    def _update(self, context, verification: VerificationResult):
        """裁剪并更新 target_hidden_states 和 KV cache"""
        ...
    
    def generate_one_sample(self, input_ids, stop_token_ids=None):
        """
        使用 generate_decoding_sample 框架，配置 DSpark 专用回调：
        - init_context: 初始化 draft cache 和 target_hidden_states
        - propose: 调用 _propose 生成 block 级提议
        - update: 调用 _update 更新状态
        - post_verify: 使用 ConfidenceHeadRecorder 收集置信度数据
        """
        ...
```

### 5.2 `Gemma4DSparkEvaluator`

```python
class Gemma4DSparkEvaluator(Qwen3DSparkEvaluator):
    draft_model_cls = Gemma4DSparkModel
    # 其余逻辑继承自 Qwen3DSparkEvaluator
```

### 5.3 DSpark Draft 操作

```python
def forward_dspark_draft_block(
    model: nn.Module,
    draft_input_ids: torch.Tensor,
    position_ids: torch.Tensor,
    past_key_values_draft,
    target_hidden_states: torch.Tensor,
    start: int,
    block_size: int,
):
    """执行单块 DSpark draft 前向传播，返回 block 级隐状态"""
    ...

def build_dspark_proposal(
    model: nn.Module,
    draft_input_ids: torch.Tensor,
    block_hidden: torch.Tensor,
    block_size: int,
    temperature: float,
    confidence_threshold: float = 0.0,
) -> DSparkDraftProposal:
    """
    自回归采样 draft tokens 构建提议：
    1. 通过 lm_head + markov_head 生成 logits
    2. 逐 token 采样（temperature 控制）
    3. 可选基于 confidence head 提前截断：
       _confident_prefix_length 找到第一个低于阈值的位置
    """
    ...
```

### 5.4 `ConfidenceHeadRecorder`

```python
class ConfidenceHeadRecorder:
    """收集置信度校准指标"""
    
    def __call__(self, proposal: DSparkDraftProposal, verification: VerificationResult):
        """记录每个位置的置信度预测和实际接受/拒绝结果"""
        ...
    
    def get_calibration_metrics(self) -> dict:
        """计算 ECE（Expected Calibration Error）等校准指标"""
        ...
```

---

## 六、Eagle3 评估器

### 6.1 `Qwen3Eagle3Evaluator`

```python
class Qwen3Eagle3Evaluator(BaseEvaluator):
    EVAL_ATTN_IMPLEMENTATION = "sdpa"
    
    def __init__(self, local_rank, args):
        """断言 draft_num_hidden_layers == 1"""
        ...
    
    @property
    def max_proposal_tokens(self) -> int:
        return self.ttt_length  # 等于 draft 模型配置的 ttt_length
    
    def build_models(self):
        """加载 BF16 的目标模型和 Eagle3 draft 模型（SDPA 注意力）"""
        ...
    
    def _init_context(self, initial_output, output_ids, position_ids, num_input_tokens):
        """使用 shifted prompt ids 预填充 draft KV cache"""
        ...
    
    def _propose(self, context, output_ids, position_ids, start, stop_token_ids):
        """
        循环 TTT 步自回归采样 draft tokens：
        1. 每步使用 draft 模型预测下一个 token
        2. 更新 KV cache
        3. 构建 DraftProposal
        """
        ...
    
    def _update(self, context, verification: VerificationResult):
        """裁剪 draft cache 并 extend 已验证 token 的 KV"""
        ...
    
    def generate_one_sample(self, input_ids, stop_token_ids=None):
        """使用 generate_decoding_sample 框架，配置 Eagle3 专用回调"""
        ...
```

### 6.2 `Gemma4Eagle3Evaluator`

```python
class Gemma4Eagle3Evaluator(Qwen3Eagle3Evaluator):
    draft_model_cls = Gemma4Eagle3Model
    # 其余逻辑继承自 Qwen3Eagle3Evaluator
```

---

## 七、采样工具函数

```python
# deepspec/utils/sampling.py

def logits_to_probs(logits: torch.Tensor, temperature: float) -> torch.Tensor:
    """温度为0时返回 one-hot argmax，否则返回 softmax 概率"""
    ...

def sample_from_probs(probs: torch.Tensor) -> torch.Tensor:
    """对 3D probs 调用 torch.multinomial 采样"""
    ...

def sample_tokens(logits: torch.Tensor, temperature: float = 0.0) -> torch.Tensor:
    """温度为0时 argmax，否则 softmax + multinomial 采样"""
    ...

def gather_token_probs(probs: torch.Tensor, token_ids: torch.Tensor) -> torch.Tensor:
    """沿最后一维 gather 指定 token 的概率"""
    ...

def sample_residual(
    target_probs: torch.Tensor,
    draft_probs: torch.Tensor,
) -> torch.Tensor:
    """计算残差分布 max(0, target - draft) 归一化后采样"""
    ...
```

---

## 八、评估流程总结

```
输入数据 → 编码 → generate_decoding_sample 循环
                         ↓
              ┌─────────────────────┐
              │  init_context()     │ → 初始化 KV cache、隐状态
              └─────────┬───────────┘
                        ↓
              ┌─────────────────────┐
              │  while 未结束:       │
              │    propose()        │ → draft 模型生成提议
              │    verify_draft()   │ → 目标模型验证 + 拒绝采样
              │    post_verify()    │ → 收集诊断数据（可选）
              │    update()         │ → 更新状态
              └─────────┬───────────┘
                        ↓
              输出序列 + 统计指标（接受率、验证率等）
                        ↓
              跨 rank 汇总 → build_metrics_row → 打印结果
```

---

## 九、相关链接

- /deepseek/deep-spec/concepts/speculative-decoding-training — 投机解码训练方法论
- /deepseek/deep-spec/concepts/overview — DeepSpec 整体概述
- /deepseek/deep-spec/examples/evaluation — 评估使用示例
- /deepseek/deep-spec/references/model-api — 模型 API 参考
- /deepseek/deep-spec/references/training-api — 训练 API 参考
