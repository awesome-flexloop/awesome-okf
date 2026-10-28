---
type: Reference
title: 时间轴、JSONL 与证据契约
sources:
  - {id: evidence, resource: ../references/facts.md}
  - {id: design, resource: 00-architecture.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 时间轴、JSONL 与证据契约

推荐把 UTF-8 JSONL 作为 Agent 的输入，每行一个片段；SRT/VTT 用于播放器，Markdown 用于阅读。JSONL 是本教程约定的交换格式，不是声称所有 ASR 都原生输出这种结构。

## 最小本地目录

```text
session/
  manifest.json
  media/
  audio/
  transcripts/
    revision-001.jsonl
  analysis/
    topics.json
    claims.json
    notes.md
```

目录应位于经批准的媒体工作区，不要放进公开知识库。`manifest.json` 记录会话身份、来源别名、授权用途、模型版本、参数、原文件散列和采集缺口；原始签名 URL、Cookie、密钥不进入该文件。

## 片段字段

| 字段 | 类型与规则 |
|---|---|
| `schema_version` | 字符串，本文定义为 `1.0` |
| `session_id` | 一次采集的稳定 ID；恢复同一次会话不随意更换 |
| `segment_id` | 在会话内唯一，不能只用字幕文本当 ID |
| `revision` | 正整数；改正原文或时间戳时加一 |
| `status` | `provisional` 或 `final`；分析默认只消费 `final` |
| `media_id` | 对应 manifest 中的证据媒体项；离线示例指输入 WAV，原视频另存映射 |
| `audio_sha256` | 本次识别输入文件的 SHA-256，64 个十六进制字符 |
| `start_ms` / `end_ms` | 相对该连续媒体项起点的毫秒整数，`0 <= start_ms < end_ms` |
| `text` | 原始 ASR 文本；人工修订另留修订记录 |
| `speaker` | 未知为 `null`；聚类标签不等于实名身份 |
| `quality_flags` | 字符串数组，如 `overlap`、`needs_review`；空数组不等于绝对正确 |

`segment_id + revision` 才能固定一次引用。重新分段会改变边界，必须生成新的修订映射；不要让旧摘要无声指向新文字。单文件离线示例用输入散列前缀标识媒体；大型系统应处理 ID 碰撞，不能把短前缀当安全签名。

## 三种时钟

1. **块内时间**：ASR 对某个短文件返回的起止秒数。
2. **连续媒体时间**：该文件在一段连续录制中的准确偏移加块内时间。
3. **墙钟时间**：录制现场的 UTC 时间，仅在明确时钟锚点和误差后才能推算。

设块在连续音轨中的偏移为 `chunk_start_ms`，则 `start_ms = chunk_start_ms + round(local_start_seconds * 1000)`。偏移应来自采样位置或可信容器时间轴，不能用“第 N 块 × 计划块长”代替。关键帧、编码器延迟、重叠窗口和中断都会破坏后者。

直播重连后的内容可能没有前段连续 PTS；这时建立新的 `media_id`，记录缺口，禁止伪造一条连续的全会话时轴。播放器时间、直播平台展示时间和本机收到声音的时刻也可能不同。

## 重叠与定稿

为了保留跨块句子，滚动识别通常需要重叠上下文。合并时只提交一个窗口的稳定区间，把尾部留给下一窗口确认。简单的“相邻文本相同就删除”会误删主播真实重复的话；仅凭时间区间相交也不能决定哪份识别更准确。

归一化层应记录原始两个候选、匹配依据及选择结果。实时界面可以显示 `provisional`，持久分析记录应等待 `final`；若已分析的 `final` 被修正，应使关联分析失效并重算，而不是覆盖证据。

宿主发布不可变的“当前快照”，同一 `segment_id` 仅含一个当前有效版本。旧版保留在历史档案，不与新版拼接为分析输入；删除或重分段时，旧 ID 从当前快照移除，另记替代映射。更高版本还在 `provisional` 时，当前快照也不得继续提供旧 `final` 充作新结论依据。旧分析可以按其原快照回查，但必须标为已失效，不能作为当前结果发布。[示例检查器](../examples/agent-evidence-check.md)会拒绝一个快照里同 ID 的多个版本；它无法自行发现操作者提供了过时快照，最新快照选择仍由宿主负责。

## 引用验证

分析结论至少返回 `segment_id`、`revision`、引用原文和结论类别。独立验证程序逐条检查：

- ID 和修订确实存在于本次输入的定稿集合；
- 引文确实出现在指定片段，跨片段引文拆开记录；
- 引用时间范围来自归一化记录，不由语言模型重新估计；
- 引用媒体散列与清单一致；
- `kind` 只能是 `quote`（原话）、`paraphrase`（转述）、`inference`（推断）。外部核验属于另一个任务，另存外部来源对象，不混入本版 `claims`。

这些是完整流程的检查目标；[教学函数](../examples/agent-evidence-check.md)只实现当前快照版本唯一性、引用身份和逐字匹配，不核查媒体散列或时间映射。合法枚举不证明分类正确，引文存在也不证明支持结论；是否断章取义仍需回听、相邻上下文和人工判断。

## 从文件到查询服务

最小方案是目录加 JSONL，不需要数据库和向量库。会话增加后，可用 SQLite 存会话、片段、分析及引用关系；中文全文检索须实际评估分词或 trigram，不能默认英文 tokenizer 适用。需要语义检索时再引入本地 embedding，保留返回片段的原始 ID；向量相似度不是事实置信度。

如封装 MCP，只暴露 `list_sessions`、`read_segments`、`search_segments`、`get_evidence` 这类只读接口。服务端用会话 ID 映射固定目录，拒绝任意路径、任意 URL 和任意 shell。MCP 是工具接口，不会自动让云 Agent 变成离线 Agent。
