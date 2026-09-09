---
type: concept
title: 符号表与文本清洗
description: 解析 text/symbols.py 的符号拼接顺序、84 个 ARPAbet 符号、18 条缩写展开与数字规范化规则，理解 EmotiVoice token 世界的边界与序列化机制。
tags: [emotivoice, tts, symbols, arpabet, text-processing]
generated: { by: "reference_agent/trae-solo", at: 2026-09-09T00:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T00:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: EmotiVoice 源码事实清单（v0.3 @ 59f0f36）
  - id: insights
    resource: /references/insights.md
    title: EmotiVoice 架构洞察与知识地图（v0.3 @ 59f0f36）
---

# 符号表与文本清洗

前端产出的音素序列要变成模型可消费的整数 id，须经过两层基础设施：`text/` 包提供的符号表与序列化函数，以及 cleaners/numbers 提供的文本规范化管线。本文解释 token 世界的边界是如何划定的。

## 符号表：symbols 的拼接顺序

`text/symbols.py`（注明源自 tacotron）定义了模型认识的全部分词单元，`symbols` 列表按固定顺序拼接（F-ev-014）：

```
1. _pad      = "_"
2. _special  = "-"
3. _punctuation = "!'(),.:;? "        # 10 个标点字符
4. letters   = 26 个小写 + 26 个大写字母
5. _arpabet  = ["@" + s for s in cmudict.valid_symbols]
6. _silences = ["@sp", "@spn", "@sil"]
```

拼接顺序为 pad → special → punctuation → letters → arpabet → silences（F-ev-014）。这个顺序决定符号 id 的排布，改动顺序等于重排整个词表，属于破坏性变更。

## ARPAbet：84 个有效符号

`text/cmudict.py` 的 `valid_symbols` 共 **84 个** ARPAbet 符号：15 个元音各含无调原形及 0/1/2 三档声调（共 60 个），加 24 个辅音（F-ev-015）。符号表中的 ARPAbet 条目以 `@` 前缀拼出（如 `@AA0`，F-ev-014），与前端英文管线输出的 `[AA0]` 方括号写法在花括号语法中互相转换（见下文）。

## 序列化：text_to_sequence 与花括号语法

`text/__init__.py` 暴露三个核心接口（F-ev-013）：

- `text_to_sequence(text, cleaner_names)`：文本 → 整数 id 序列，**支持花括号 ARPAbet 语法**——`{AA0 R P AH0 B EH0 T}` 形式的片段被直接解析为音素，而非逐字符处理；
- `sequence_to_text`：整数 id 序列 → 文本，用于调试回显；
- `_symbol_to_id` / `_id_to_symbol`：符号与 id 的双向映射。

推理主入口则走更直接的路径：按空格 split 音素序列后查 `token2id` 映射（该映射由 `data/youdao/text/tokenlist` 的 502 行词表构建，F-ev-027），不经 cleaner。

## 文本清洗：cleaners.py

`text/cleaners.py` 提供英文文本进入 g2p 前的规范化，包含（F-ev-016）：

- **18 条缩写展开表**：mrs/mr/dr/st/co/jr/maj/gen/drs/rev/lt/hon/sgt/capt/esq/ltd/col/ft，逐条把缩写还原为完整读音形式；
- **三个管线函数**：`basic_cleaners`、`transliteration_cleaners`（基于 unidecode 的转写）、`english_cleaners`。

缩写展开解决了「Dr. 读作 doctor 还是字母 D-R」这类歧义，是词典命中率的保障。

## 数字规范化：numbers.py

`text/numbers.py` 以 inflect 引擎为核心，用六组正则替换规则覆盖英文数字读法（F-ev-017）：

| 规则组 | 场景 |
|--------|------|
| 逗号数字 | 千分位数字串 |
| 小数 | 小数点读法 |
| 英镑 | 货币金额 |
| 美元 | 货币金额 |
| 序数词 | first、second…… |
| 普通数字 | 一般整数 |

注意与中文侧的分工：中文场景的数字在更上游已由 `tn_chinese` + cn2an 转成中文数字（见 [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)），`numbers.py` 服务的是英文读法。

## 设计启示

符号表、清洗器与数字规范化三者共同划定了「模型能读什么」的边界：

1. **想加新语言/新标记** → 改 `symbols.py` 的拼接段与 `_silences`/`_arpabet`，并同步训练数据侧的标记约定（见 [05](/concepts/05-labels-dataset-mfa.md)）；
2. **英文发音错误** → 先查缩写是否被 18 条展开表覆盖、数字是否命中六组规则，再查词典（F-ev-016、F-ev-017）；
3. **调试序列化问题** → 用 `sequence_to_text` 回显整数 id 对应的符号（F-ev-013）。

## 相关概念

- [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)
- [04 JETS 联合训练与 HiFiGAN 声码器](/concepts/04-jets-joint-training.md)
