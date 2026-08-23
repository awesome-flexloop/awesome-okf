# DeepSpec API 与技术参考

本章节提供 DeepSpec 的完整 API 参考和技术细节文档。

## 参考文档列表

| 文档 | 说明 |
|---|---|
| [training-api](/ai/deepseek/deep-spec/references/training-api) | 训练管线 API 参考，包括 BaseTrainer/DSparkTrainer/Eagle3Trainer、BF16Optimizer、FSDP 配置、Checkpoint 管理、配置系统结构 |
| [model-api](/ai/deepseek/deep-spec/references/model-api) | 模型 API 参考，包括 Qwen3/Gemma4 DSpark/Eagle3 模型类、Markov 头三种变体、FusedLogSoftmaxLoss、损失函数、配置构建函数 |
| [eval-api](/ai/deepseek/deep-spec/references/eval-api) | 评估管线 API 参考，包括 BaseEvaluator、DSpark/Eagle3 评估器、verify_draft_tokens、generate_decoding_sample 回调框架、9个评测任务、采样工具 |
