---
type: concept
title: 中英混合前端与 g2p 管线
description: 讲清 frontend.py 的 g2p_cn_en 如何用单管线处理中英混读：数字转中文、中文 jieba+pypinyin 与英文 lexicon+g2p_en 分工、eng_cn_sp/cn_eng_sp 跨界标记与 sos/eos 包裹。
tags: [emotivoice, tts, frontend, g2p, bilingual]
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

# 中英混合前端与 g2p 管线

EmotiVoice 面对的核心文本场景是**中英混合**：一句话里可能同时出现中文、英文、阿拉伯数字与标点。前端的设计选择是**单管线串行处理**——`frontend.py` 的 `g2p_cn_en(text, g2p, lexicon)` 一个函数完成全部工作（F-ev-004），而不是为两种语言各建一套前端再拼接输出。

## g2p_cn_en 的五步处理顺序

`g2p_cn_en` 对输入文本依次执行以下步骤（F-ev-004）：

```
输入文本："今天天气真好，适合去 park 散步。"
   │
   │ ① 数字归一化：tn_chinese(text)
   ▼
"今天天气真好，适合去 park 散步。"（含数字时已被转成中文数字）
   │
   │ ② 正则切分：re_english_word.split(text)
   ▼
["今天天气真好", "，", "适合去", " park ", "散步", "。"]
   │
   │ ③ 逐段路由：中文段 → g2p_cn；英文段 → get_eng_phoneme
   ▼
拼音 / ARPAbet 音素 + sp 停顿标记
   │
   │ ④ 语言切换处插入跨界标记 eng_cn_sp / cn_eng_sp
   ▼
   │ ⑤ 首尾包裹 <sos/eos>
   ▼
"<sos/eos> jin1 tian1 ... sp3 ... p aa1 r k eng_cn_sp ... <sos/eos>"
```

### ① 数字转中文：tn_chinese

只要文本含中文，数字就先被转成中文数字：`frontend_cn.py` 的 `tn_chinese(text)` 用 `re_digits = re.compile('(\d[\d\.]*)')` 捕获数字片段，调 `number_to_chinese`，再经 vendored `cn2an.An2Cn().an2cn()` 完成阿拉伯数字到中文数字的转换（F-ev-007）。仓库内置的 `cn2an/` 是裁剪版，仅含 `an2cn.py`、`conf.py` 两个文件（F-ev-041）。这一步保证了「我今天吃了 3 个苹果」中的 `3` 会按中文读法「三」进入后续管线。

### ② 正则切分：re_english_word

`frontend.py` 用模块级正则 `re_english_word` 把文本切成中文片段与非中文片段（F-ev-004）。切分结果按 `filter(None, ...)` 去除空段后逐段路由。

### ③ 双前端分工

每个片段按类型进入对应子前端：

| 片段类型 | 处理函数 | 引擎与词典 | 停顿标记 |
|----------|----------|-----------|----------|
| 中文 | `frontend_cn.py` 的 `g2p_cn(text)` | `jieba.cut` 分词 + `pypinyin(style=Style.TONE3, neutral_tone_with_five=True)` | 字间 `sp0`、词间 `sp1`、标点 `sp3` |
| 英文 | `frontend_en.py` 的 `get_eng_phoneme(text, g2p, lexicon, pad_sos_eos=True)` | `lexicon/librispeech-lexicon.txt` 词典 + `g2p_en.G2p` | 词间 `engsp1`、标点尾部 `engsp4` |

中文侧，`g2p_cn` 用 jieba 分词后逐词取拼音，TONE3 风格输出带声调数字（如 `jin1`）；模块加载时还调用 `cc_cedict.load()`（来自 `pypinyin_dict`）加载自定义词典（F-ev-006、F-ev-009）；`split_py(py)` 负责把拼音切成声母、韵母两部分（F-ev-008）。英文侧，词典命中时按 `read_lexicon` 读取的音素并包 `[...]` 方括号，未命中词由 `g2p_en.G2p` 推断（F-ev-010、F-ev-011）。

### ④ 跨界标记：把语言边界编码进音素序列

这是本管线最有教学价值的决策：语言切换**不是**由前端做对齐决策，而是往音素序列里插入特殊标记——

- 由英文切到中文时插入 `eng_cn_sp`；
- 由中文切到英文时插入 `cn_eng_sp`（F-ev-004）。

跨界标记与 `sp0`/`sp1`/`sp3`/`engsp1`/`engsp4` 同属 sp 标记家族，由联合模型在训练中自行学习跨界处的声学表现；前端本身无状态、无对齐决策。训练数据侧的 MFA 流水线会把 `cn_eng_sp` 进一步规范为 `cnengsp`（F-ev-038），保证前端输出与训练数据约定一致——这是串联前端与数据工程的隐形契约，详见 [05 标签体系、数据集与 MFA 对齐流水线](/concepts/05-labels-dataset-mfa.md)。

### ⑤ sos/eos 包裹

最终序列以 `<sos/eos>` 开头、以 `<sos/eos>` 结尾（F-ev-004），为模型提供明确的序列边界信号。

## 命令行用法

`frontend.py` 支持独立命令行使用，便于在接入推理前 dump 音素序列做人工检查（F-ev-005）：

```bash
python frontend.py data/my_text.txt > data/my_text_for_tts.txt
```

诊断混读发音错误时，正确做法是先在这一步确认跨界标记位置与音素内容，再排查模型侧。动手演练见 [中英混读文本处理示例](/examples/mixed-lingual-g2p.md)。

## 模块导出关系

`frontend_en.py` 定义 `ROOT_DIR = os.path.dirname(os.path.abspath("__file__"))`，用于定位 `lexicon/librispeech-lexicon.txt` 等资源；`openaiapi.py` 经 `frontend.py` 间接从 `frontend_en` 再导出 `g2p_cn_en`、`ROOT_DIR`、`read_lexicon`、`G2p`（F-ev-012）。服务层因此无需直接依赖前端内部模块。

## 常见误区

- **「需要双语模型才能混读」**：实际是单管线 + 跨界标记。扩展新语言或改韵律粒度的正确切口是符号表与 sp 标记体系（见 [02 符号表与文本清洗](/concepts/02-symbols-text-cleaning.md)），而非替换 g2p 引擎。
- **「数字按英文读」**：`g2p_cn_en` 对任意文本都**无条件**先调用 `tn_chinese`（frontend.py 第 24 行），数字一律被转成中文数字并按中文路径发音，不存在"含中文才转换"的条件分流（F-ev-004、F-ev-007）。

## 相关概念

- [00 整体架构与推理入口](/concepts/00-architecture.md)
- [02 符号表与文本清洗](/concepts/02-symbols-text-cleaning.md)
- [05 标签体系、数据集与 MFA 对齐流水线](/concepts/05-labels-dataset-mfa.md)
