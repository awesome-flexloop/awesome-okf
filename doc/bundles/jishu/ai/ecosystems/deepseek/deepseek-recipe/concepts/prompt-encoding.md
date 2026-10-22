---
type: concept
scope: deepseek-recipe
name: Prompt 编码
version: "0.2.0"
source: deepseek-recipe-encoding/src/, docs/tokenizer.zh.md
description: V4/V4.1 prompt 渲染差异、special token 防注入机制与分段并行 tokenize 加速
sources:
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践
---

# Prompt 渲染与 Token 编码

这是 recipe 工程含量最高的部分：既要渲染出与官方一致的 prompt，又要在 token 层面杜绝注入，还要把超长上下文的 tokenize 延迟压下来。

---

## 一、PromptEncoding 契约

`deepseek-recipe-encoding/src/lib.rs` 定义：

- `render_conversation(&Conversation) -> RenderedPrompt{prompt, special_ranges, image_sources}`——渲染 prompt 文本、其中**显式 special token 的字节区间**、图片来源；
- `encode(&Conversation) -> Vec<u32>`——渲染 + 分词（需先 `with_tokenizer` 附加 tokenizer，否则返回 `EncodingError::MissingTokenizer`）。

渲染把模板控制 token、消息图片来源对应的占位符、以及 assistant/reasoning 内容中的 grounding token 作为显式 special token 插入。

## 二、V4 与 V4.1 渲染差异

| 维度 | DeepseekV4Encoding | DeepseekV41Encoding |
|---|---|---|
| 系统消息 | 不发 `<｜System｜>` token，系统消息 hoist 到 BOS 后以空行拼接 | 常规 system token；工具提示/response format 追加到第一条 system 消息（无则插入空 system） |
| Reasoning Effort | 两大段长文本提示 | 渲染为数字评分 50/75/100 |
| DSML 标签 | 标签名不带空格 | 标签名带空格（`" calls"`/`" invoke"`/`" parameter"`） |
| 图片 | 每张图片替换为 `[Unsupported Image]` 文本 | 图片占位符 + `IMAGE_SPECIAL_TOKEN_ID`（129264） |

## 三、special token 防注入（双向）

### 3.1 输入侧：用户拼出的 special token 只是普通文本

`src/v4/mod.rs` 只把 **8 个 grounding token**（Ref/Box/Point/Polygon 及闭合标签，Aho-Corasick 匹配）在 assistant/reasoning 内容中升格为显式 special token；消息文本里拼出的任何 special token 拼写（如 `<｜User｜>`、`<｜image｜>`）一律按普通字符编码为 token 序列——防止通过文本注入控制 token 影响模型行为。

编码时：`special_ranges` 区间直接映射为对应 token ID，区间之间的纯文本按**基础词表**编码（不用 added vocabulary）。

### 3.2 输出侧：只有 token 形式的标记才算标记

模型输出解码时，每个 special token 单独解码成一段并带标记；输出解析器只把 **token 形式**的 `</think>` 与 DSML 标签当作标记，模型用普通 token 拼出的相同文本被正确保留为原始内容，不会获得触发思考结束或工具调用的能力（见[流式解析](stream-parsing.md)）。

## 四、分段并行 tokenize 加速

知乎报告描述的方案在代码中的落点：

1. **构建 prompt 时**已确定 special token 的位置和边界（`special_ranges`）；
2. 根据 BPE 编码原理，special token 之间的各段普通文本**可独立编码**；
3. 编码时先跳过普通文本中 special token 的匹配与切分，然后**并行编码各段普通文本**（`PromptTokenizer::encode_ids` 走 `encode_batch_fast`，受 `TOKENIZERS_PARALLELISM` 控制），最后按原顺序拼接。

效果：降低超长上下文请求的分词耗时，优化 TTFT 与 CPU 开销。

## 五、PromptTokenizer

`src/tokenizer.rs` 的 `PromptTokenizer`：

- 持有**去掉 added vocabulary 的 plain tokenizer** + special token ID 表（为何去 added vocabulary：防普通文本被 added vocab 意外命中）；
- `with_tokenizer` 也接受任何其他 `TokenizerEncoder` 实现；
- 调用方自行对 `RenderedPrompt::prompt` 分词时，必须同样处理 `special_ranges`。

## 六、内置 tokenizer 与匹配要求

- 仓库 `static/tokenizers/` 内置 V4 与 V4.1 两个 tokenizer 副本：`v4/` 改自 HF `deepseek-ai/DeepSeek-V4-Pro`（id 129264/129279 的 image token 对调）；`v41/` 改自 `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp`（id 129264 重赋值为 `<｜image｜>`）。各目录 README 记录比对 revision、SHA-256 与变更；上游 MIT（Copyright (c) 2023 DeepSeek）；
- 也可从 Hugging Face Hub 加载 tokenizer：其 added vocabulary 必须包含渲染写入的每个 special token 的拼写，否则 `encode` 返回 `EncodingError::Encode`；
- `IMAGE_SPECIAL_TOKEN_ID` 是内置 V4.1 tokenizer 中图片 token 的 token ID；使用该常量的调用方需要图片 token ID 与之相同的 tokenizer；
- encodings **不会自动加载**这些文件，转换 token IDs 需调用方自行加载匹配的 tokenizer。

## 七、max_tokens 解析时机

编码之后调用 `ConversationRequest::resolve_max_tokens(prompt_tokens, context_limit)`：

- `prompt_tokens` = 编码得到的 token ID 数 + 图片超出占位符的 token 数（`MultiModalData::image_token_adjustment`）；
- `context_limit` = 模型上下文可容纳的 token 数；
- 规则详见[协议转换](protocol-conversion.md)第四节。
