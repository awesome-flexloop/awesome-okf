---
type: Guide
title: Sol 的 API 契约与迁移
source: https://developers.openai.com/api/docs/models/gpt-6.1-sol
sources:
  - id: facts
    resource: ../references/source-inventory.md
status: draft
---

# Sol 的 API 契约与迁移

模型名使用 `gpt-6.1-sol`，不能把产品显示名称 `GPT-6.1-Sol` 直接填入请求。[F-001] API 是应用调用模型的接口；端点决定请求和返回格式，模型决定可用能力，工具与执行环境负责实际动作。四者需要分别核对。

## 模型规格

| 项目 | 官方参考声明 |
|---|---|
| 输入与输出 | 文本、图像输入；文本输出；原生音频与视频不支持 [F-006] |
| 上下文窗口 | 1,050,000 tokens [F-004] |
| 最大输出 | 128,000 tokens [F-005] |
| 推理档 | `low`、`medium`、`high`、`xhigh`、`max`；默认 `medium` [F-007] |
| 无推理档 | 不支持 `none` [F-008] |
| 功能 | 流式输出、函数调用、结构化输出支持；微调不支持 [F-009、F-010] |

token 是模型计量信息的单位，不等于汉字或单词。上下文窗口是容量上限，不能当作全范围检索正确率保证。最大输出也不是每次请求都会使用的数量。推理档控制模型投入的推理工作，不应解释成固定耗时或准确率承诺。

## 工具与端点

模型页列出 Responses 下的 web search、file search、image generation、code interpreter、hosted shell、apply patch、skills、computer use、MCP 和 tool search。[F-011] 图像生成工具受支持，并不意味着 Sol 原生输出图像；电脑操作工具受支持，也不意味着 API 自动接管本机。

Sol 的工具调用必须使用 Responses API。[F-012] Chat Completions 可用于受支持的文本流程，但不能通过它给 Sol 启用工具推理。[F-028] 浏览器另核对支持图标，而非只读扁平端点列表，结果如下。[F-047]

| 端点范围 | 本次支持状态 |
|---|---|
| Chat Completions、Responses、Batch | 支持；Chat Completions 无工具调用 |
| Live、Realtime 及实时翻译/转写 | 不支持 |
| Assistants、Fine-tuning、Embeddings、Moderation、legacy Completions | 不支持 |
| 专门图像生成/编辑、视频、语音生成、转写、翻译端点 | 不支持 |

“image generation 工具支持”和“专门图像生成端点不支持”没有矛盾：前者让 Sol 调用其他工具，后者描述直接端点能力。

结构化输出指按指定结构生成内容；它不能证明字段里的事实正确。微调不受支持，也不等于不能通过提示、检索或工具提供业务上下文。[F-009、F-010]

## 从旧模型迁移

官方指南建议在支持范围内保持现有有效推理档，比较代表性任务；旧流程的 `none` 迁移到 Sol 时用 `low`，旧 `minimal` 也先以 `low` 对比。[F-027] 这会改变推理行为，不能称为只改模型名的等价迁移。

1. 固定一组脱敏任务、旧请求和验收条件，保存旧模型结果作为对照。
2. 将 `model` 改为 `gpt-6.1-sol`，把不支持的档位映射到 `low`，其余档位先保持。
3. 使用工具的流程迁入 Responses，检查请求结构、工具定义、输出类型和状态传递。
4. 以前轮取得的 Sol 迁移说明为起点，检查 `temperature`、`top_p`、`top_logprobs`、Chat 的 `logprobs` 和 Responses `include` 中的 `message.output_text.logprobs` 删除要求。[F-029] 恢复后同 URL 返回 Astra 主章节，不能把这次返回当作 Sol 参数二次确认；以实际测试请求裁定。
5. 比较同一批任务的通过情况、费用、延迟和错误，不在迁移阶段同时重写提示与更换执行器。

这组步骤是基于官方契约的迁移设计，未执行真实 Sol 请求。

## 输出与多轮状态

Responses 用 `input` 和带类型的 `output` Items，不能继续读取 Chat Completions 的 `choices[0].message.content`。[F-030] 只需要最终文本时可使用 SDK 的 `output_text`；有工具时必须按 Item 类型处理 `function_call` 等输出。

工具返回通过 `function_call_output` 和原 `call_id` 关联。[F-031] 掉失调用标识、只保留最终自然语言，都会破坏后续上下文。

可以用 `previous_response_id` 继续对话，也可以由应用重放 Items。使用前者时要重新发送稳定的顶层 `instructions`，它不会自动继承前一请求的这项指令。[F-032] 先前上下文仍作为输入计费；会话 ID 不代表免费上下文或必然缓存命中。[F-033、F-026]

对话上下文与浏览器登录、标签页、运行时变量是两套状态；继续 API response 不会恢复已关闭的浏览器。[F-036]

## 限速与可用性

模型页两次取数都列 Free 不支持。前轮浏览器为 Build/Launch/Grow；恢复后 WebFetch 为 Tier 1–5，具体数值在[台账 F-014](../references/source-inventory.md)并列保存，未裁定两组名称的账户映射。RPM 是每分钟请求数，TPM 是每分钟 token 数。这些是页面上限，不是本账户实测，不是并发保证，也不是 ChatGPT 订阅用量。

恢复后模型参考称支持 US/EU data residency，EU data residency 下 Fast 不可用。[F-082] 地域资格、限速与服务模式须在账户层确认。

本次 Snapshots 栏只取得 `gpt-6.1-sol`，没有登记日期固定的 snapshot 名称。[F-013] 复现时记录服务返回型号、请求时间、参数、SDK 与执行器版本，不能凭空构造日期后缀。

返回[教程入口](../index.md)。
