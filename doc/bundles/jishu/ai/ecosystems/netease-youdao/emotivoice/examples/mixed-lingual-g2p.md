---
type: example
title: 中英混读文本处理示例
description: 基于 frontend.py 演练中英混合文本的音素化：数字转中文、双前端分工、跨界标记插入与 sos/eos 包裹，覆盖命令行用法与 Python 调用两种形态。
tags: [emotivoice, tts, frontend, g2p, example, bilingual]
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

# 中英混读文本处理示例

本例演练 `frontend.py` 的 `g2p_cn_en` 如何处理中英混合文本，覆盖命令行与 Python 调用两种形态。管线原理见 [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)。

## 形态一：命令行批量音素化

`frontend.py` 的 `__main__` 支持直接处理文本文件（F-ev-005）：

```bash
# data/my_text.txt 每行一句待合成文本
python frontend.py data/my_text.txt > data/my_text_for_tts.txt
```

输入 `data/my_text.txt`：

```
我有3个apple，你要不要来1个？
明天下午3点，我们在park门口见。
```

`data/my_text_for_tts.txt` 得到每行对应的音素序列，可直接填入推理测试文件的第三段（phoneme text，F-ev-003）。

## 形态二：Python 调用

服务层与批量推理入口都直接调用 `g2p_cn_en`（F-ev-012）。等价写法：

```python
from frontend import g2p_cn_en
from frontend_en import ROOT_DIR, read_lexicon, G2p

lexicon = read_lexicon(f"{ROOT_DIR}/lexicon/librispeech-lexicon.txt")
g2p = G2p()

text = "我有3个apple，你要不要来1个？"
phoneme = g2p_cn_en(text, g2p, lexicon)
print(phoneme)
```

## 逐步拆解：一行混读文本的旅程

以「我有3个apple，你要不要来1个？」为例，`g2p_cn_en` 内部依次发生（F-ev-004）：

### ① 数字转中文

`tn_chinese` 用 `re_digits = re.compile('(\d[\d\.]*)')` 捕获数字，经 `number_to_chinese` 与 vendored `cn2an.An2Cn().an2cn()` 转写（F-ev-007）：

```
我有3个apple，你要不要来1个？
        ↓ 3 → 三，1 → 一
我有三个apple，你要不要来一个？
```

只要文本含中文，数字一律走中文读法（F-ev-004 的处理策略）。

### ② 正则切分与路由

`re_english_word` 把文本切成中文段与英文段（F-ev-004）：

```
[我有三个] [apple] [你要不要来一个]
   中文      英文         中文
```

### ③ 分段 g2p

- 中文段走 `g2p_cn`：jieba 分词 + `pypinyin(style=Style.TONE3, neutral_tone_with_five=True)`，字间插 `sp0`、词间插 `sp1`、标点转 `sp3`（F-ev-006）；
- 英文段走 `get_eng_phoneme(text, g2p, lexicon, pad_sos_eos=True)`：词典命中音素包 `[...]`、词间插 `engsp1`（F-ev-010、F-ev-011）。

### ④ 跨界标记

- 「我有三个」（中文）→「apple」（英文）：插入 `cn_eng_sp`；
- 「apple」（英文）→「你要不要来一个」（中文）：插入 `eng_cn_sp`（F-ev-004）。

### ⑤ sos/eos 包裹

首尾各加一个 `<sos/eos>`（F-ev-004）。最终概念形态：

```
<sos/eos> wo3 you3 sp0 san1 sp0 ge4 cn_eng_sp [ae1] [p] [ah0] [l] eng_cn_sp
ni3 yao4 bu2 yao4 sp0 lai2 sp0 yi2 sp0 ge4 sp3 <sos/eos>
```

> 说明：上式为概念示意，展示标记排布方式；实际输出以 `python frontend.py` 的 dump 结果为准（F-ev-005）。

## 纯英文与纯中文文本

- **纯英文**：`g2p_cn_en` 仍**无条件**先执行 `tn_chinese`（frontend.py 第 24 行，F-ev-004），句中数字会先被转成中文数字并落入中文路径——这是实现细节而非按语言分流；英文部分走 `get_eng_phoneme`，词间 `engsp1`、标点尾部 `engsp4`（F-ev-011）；
- **纯中文**：全句走 `g2p_cn`，标点统一为 `sp3`（F-ev-006）。

## 诊断技巧

混读发音出错时，按序排查：

1. **先 dump 音素**：用形态一确认跨界标记 `cn_eng_sp`/`eng_cn_sp` 位置是否正确（F-ev-004、F-ev-005）；
2. **查数字读法**：确认数字是否被 `tn_chinese` 按预期转写（F-ev-007）；
3. **查英文词典**：未命中 `librispeech-lexicon.txt` 的词由 `g2p_en.G2p` 推断，专名容易出错（F-ev-010、F-ev-011）；
4. **再排查模型侧**：前端输出正确而发音仍异常时，问题才在声学模型。

## 相关概念

- [01 中英混合前端与 g2p 管线](/concepts/01-g2p-pipeline.md)
- [02 符号表与文本清洗](/concepts/02-symbols-text-cleaning.md)
- [联合推理完整流程示例](/examples/joint-inference-workflow.md)
