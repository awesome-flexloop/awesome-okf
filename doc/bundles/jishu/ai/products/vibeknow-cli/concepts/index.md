# 概念解析（Concepts）

| 文档 | 主题 |
|------|------|
| [00-cli-overview.md](00-cli-overview.md) | 定位、19 个顶层命令的命令树全貌、四后端服务划分、配置目录解析、首次使用前的准备清单 |
| [01-exit-code-contract.md](01-exit-code-contract.md) | 八档退出码速查、4 与 5 的分界、exit 6 三态判定、阻塞式与单次读取式的分界规则 |
| [02-paid-action-gate.md](02-paid-action-gate.md) | 授权门四级解析、action_id 的 HMAC 派生、两个授权边界类型、exit 8 输出形态、无人值守处置 |
| [03-output-and-events.md](03-output-and-events.md) | 三种输出格式与优先级、`vk_event=` 事件通道开启规则、advisory 语义、统一快照结构 |
| [04-run-ledger-and-async.md](04-run-ledger-and-async.md) | 运行账本六状态与 best-effort 写入、三级目标解析、异步 60 秒脱离上限、导出幂等 |
| [05-create-parameter-space.md](05-create-parameter-space.md) | `--mode` 四档与 `--engine` 两档的正交组合、拒绝矩阵、取值域、`--from` 四种来源、校验顺序 |
| [06-preset-contract.md](06-preset-contract.md) | 14 允许键 / 9 拒绝键、命令行优先语义、严格解析、搜索目录与「无 `vk preset list`」 |
| [07-subtitle-style-and-work-edit.md](07-subtitle-style-and-work-edit.md) | work 级旗标集合、字幕样式读-改-写、preset 优先顺序、`strokeWidth=0` 语义、导出失效提示 |
| [08-preview-artifacts.md](08-preview-artifacts.md) | `--preview-dir` 落盘契约、两类资产、按内容去重、原子写入、文件名消毒、源 URL 不入事件 |
| [09-cleanup-safety-contract.md](09-cleanup-safety-contract.md) | 清理命令的强制筛选与 dry-run、分页常量、账本语义、prune 三档退出码 |
| [10-ai-skill-contract.md](10-ai-skill-contract.md) | 三个 Skill 的结构、Run Contract 硬约束、四个流水线阶段、事件与授权决策的消费方式 |

```{toctree}
:hidden:
:maxdepth: 1

00-cli-overview
01-exit-code-contract
02-paid-action-gate
03-output-and-events
04-run-ledger-and-async
05-create-parameter-space
06-preset-contract
07-subtitle-style-and-work-edit
08-preview-artifacts
09-cleanup-safety-contract
10-ai-skill-contract
```
