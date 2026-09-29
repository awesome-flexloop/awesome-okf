---
type: reference
title: "EmotiVoice 架构洞察与知识地图（v0.3 @ 59f0f36）"
tags: [emotivoice, tts, insights, knowledge-map, netease-youdao]
sources:
  - id: emotivoice-repo
    resource: vendor/netease-youdao/EmotiVoice/
    title: EmotiVoice 源码仓库（git submodule，固定基线 59f0f36，tag v0.3）
---

# EmotiVoice 架构洞察与知识地图

本文件基于 [facts.md](facts.md)（F-ev-001~042，共 42 条源码事实）提炼核心架构洞察（I 阶段产出），并规划 concepts/ 概念文档的知识地图。所有洞察均给出事实证据编号，可回溯至源码位置；推断性表述仅限「反常识」与「行动」两栏。

## 核心洞察

### 洞察 1：风格控制走「多任务头训练、单嵌入推理」的非对称路径

- **陈述**：风格条件注入的核心是 `StyleEncoder`——以 `WangZeJun/simbert-base-chinese` 为底座，挂 4 个分类头（pitch/speed/energy/emotion）做有监督预训练；但联合训练与推理时仅取 `pooled_output` 经线性投影（768→128 维）得到的 `style_embedding`，分类头被完全旁路。
- **证据**：F-ev-024（StyleEncoder 结构、4 个 ClassificationHead、`style_embed_proj`）、F-ev-025（推理仅返回 `pooled_output`）、F-ev-029（bert_hidden_size=768、style_dim=128）、F-ev-031（联合训练时 StyleEncoder 冻结加载）、F-ev-042（ROADMAP 声明仅用 pitch/speed/energy/emotion 作 style factors，不用 gender）。
- **反常识**：通常认为控制条件应当端到端联合微调；实际架构中风格编码器是**冻结的预训练件**（`load_state_dict(..., strict=False)` 且 key 去 `module.` 前缀），4 个分类头只是训练期的监督脚手架，推理期零开销、零参与。
- **行动**：自定义风格/情绪时无需重训分类头——只需用同一 simbert 底座计算新 prompt 文本的 `pooled_output` 并过 `style_embed_proj`；改造风格空间应优先替换 `style_encoder_ckpt`（config 中为 `checkpoint_163431`），而非触碰联合训练主链路。

### 洞察 2：中英混读靠「跨界标记」而非双语模型拼接

- **陈述**：中英混合文本的处理是单一前端 `g2p_cn_en` 串行完成：数字先经 `tn_chinese` 转中文（vendored cn2an），正则切分中英文片段后，中文走 jieba+pypinyin（TONE3 声调、字间 sp0/词间 sp1/标点 sp3），英文走 librispeech-lexicon+g2p_en（ARPAbet、词间 engsp1/标点 engsp4），并在语言切换处插入 `eng_cn_sp`/`cn_eng_sp` 跨界标记，首尾以 `<sos/eos>` 包裹。
- **证据**：F-ev-004（g2p_cn_en 全流程与跨界标记）、F-ev-006（中文 jieba/pypinyin 与 sp0/sp1/sp3）、F-ev-007（数字转中文）、F-ev-010/F-ev-011（英文 lexicon 与 engsp1/engsp4）、F-ev-041（vendored cn2an 仅 2 文件）。
- **反常识**：直觉上中英混读需要两套独立前端再拼接输出；实际实现把「语言边界」建模为**音素序列中的特殊标记**（sp1-sp4 家族与跨界标记共用同一生成方式，见 mfa/step1 的 `cn_eng_sp→cnengsp` 转换），由联合模型在训练中自行学习跨界处的声学表现，前端本身无状态、无对齐决策。
- **行动**：扩展新语言或改韵律粒度时，正确切口是 `text/symbols.py` 的符号表（`_silences`/`_arpabet` 按序拼接）与 sp 标记体系，而非替换 g2p 引擎；诊断混读发音错误应先在 `python frontend.py` 命令行（F-ev-005） dump 音素序列确认跨界标记位置。

### 洞察 3：JETS 架构把声码器内嵌进生成器，mel 重建损失主导训练

- **陈述**：`JETSGenerator` 在单个 nn.Module 中内联 PromptTTS 声学模型（`self.am`）与 HiFiGAN 生成器（`self.generator`），一次 forward 从音素序列直达波形；训练损失以 `dec_mel_loss*45` 的 mel 重建项为主导，对抗损失（loss_gen/loss_fm）与时长/音高/能量损失为辅，判别器复用 hifigan 预训练判别器。
- **证据**：F-ev-018（`self.am = PromptTTS`、`self.generator = HiFiGANGenerator`）、F-ev-019（forward 签名含 pitch/energy targets、随机切 mel 段后 `generator(z_segments)`）、F-ev-032（损失组合 dec_mel_loss×45 等权重与 g_/do_ checkpoint 命名）、F-ev-023（models.py 注明改自 jik876/hifi-gan）、F-ev-031（Discriminator 来自 pretrained_discriminator、DDP+DistributedSampler）。
- **反常识**：流水线式 TTS 把声码器当作可独立替换的后处理组件；EmotiVoice 的声码器与声学模型**共享同一优化器、同一训练循环、同一 mel 监督信号**（mel 损失权重 45 倍于其余各项），声码器不是事后组件而是联合训练的一等公民；且采样率仅 16kHz（F-ev-029/F-ev-030），对抗 HiFi 直觉的 22.05/24kHz 惯例。
- **行动**：微调或移植时勿单独替换 vocoder checkpoint——`g_xxxxxxxx` checkpoint 同时内含 am 与 generator（F-ev-032），替换会同时换掉声学模型；评估合成质量应优先看 mel 谱重建而非仅听感，因为训练目标本身以 mel 损失为锚。

### 洞察 4：OpenAI 兼容层是「薄封装 + 外部后处理」，speed 并非模型能力

- **陈述**：`openaiapi.py` 以 FastAPI 暴露 `POST /v1/audio/speech`，请求模型 `SpeechRequest` 与 OpenAI TTS API 字段对齐（input/voice/prompt/response_format/speed 等）；但 `speed≠1.0` 时调用 `pyrubberband.time_stretch` 做**波形级后处理**，非 wav 格式经 pydub 转码，模型本体只产出 16kHz 单速波形。
- **证据**：F-ev-033（FastAPI 应用与路由）、F-ev-034（SpeechRequest 字段）、F-ev-035（pyrubberband/pydub/BytesIO）、F-ev-020（推理输出 `wav_predictions*32768 → int16 → sf.write`）、F-ev-040（openaiapi 专用 requirements 5 项）。
- **反常识**：API 形态兼容 OpenAI 容易让人误以为 speed 是模型内生的时长控制（如 duration predictor 调节）；实际 `alpha=1.0` 在推理中写死（F-ev-020），变速完全依赖外部 rubberband 拉伸，会引入相位失真与音质损耗。
- **行动**：对音质敏感的场景应显式保持 `speed=1.0`；需要变速优先在文本侧（增减标点/停顿标记 sp1-sp4）调节节奏而非依赖 time_stretch；部署依赖必须分装 `requirements.openaiapi.txt`（fastapi/pydub/pyrubberband 等，F-ev-040），与推理核心依赖（F-ev-039）分离。

### 洞察 5：训练数据工程以 MFA 对齐流水线为骨架，特殊标记贯穿全链路

- **陈述**：训练数据的构建由 `mfa/` 下 8 个 step 脚本（编号缺 step6）流水线完成：从 datalist 到 wav.scp、TextGrid 对齐、再向对齐音素序列插入 special tokens 生成最终数据清单；sp 标记家族（sp1-sp4、cnengsp）在**前端生成→MFA 转换→对齐插桩**三处保持一致，是串联前端与训练数据的隐形契约。
- **证据**：F-ev-037（8 个 step 脚本、无 step6）、F-ev-038（step1 的 `cn_eng_sp→cnengsp` 转换、step7 读 TextGrid 处理 MFA1.x/2.x 差异并插入 special tokens）、F-ev-026（prompt_dataset 的 npy 缓存与 batch 键 style/content_embedding）。
- **反常识**：多数 TTS 教程把注意力放在模型结构上；EmotiVoice 的源码里训练数据准备是**与模型同等篇幅**的工程（8 个脚本 vs 模型目录 11 个 py 文件），且对齐工具链对 MFA 大版本差异（1.x/2.x 空标签行为不同）做了显式兼容——对齐质量直接决定 special token 插桩位置的正确性。
- **行动**：复刻训练流程时必须先跑通 MFA 对齐链路再谈训练；新建语料的 sp 标记约定必须与 `frontend.py` 输出严格对齐，否则对齐插桩会错位。风格嵌入建议在数据预处理阶段离线缓存 npy（F-ev-026 已有缓存逻辑），避免训练时重复计算 simbert。

## 知识地图（concepts/ 规划）

> 说明：以下为规划清单（编号、标题、概要、前置依赖、引用事实区间），实际 concepts/ 文档由 E 阶段按本图生成。学习路径总体为「推理入口 → 文本前端 → 风格注入 → 联合训练 → 数据工程 → 服务化」。

| 编号 | 标题 | 一句话概要 | 前置依赖 | 引用事实编号 |
|------|------|-----------|----------|--------------|
| 00 | 整体架构与推理入口 | 从推理主入口与测试文本格式出发，建立 EmotiVoice 「前端→PromptTTS→HiFiGAN」三段式整体认知 | 无 | F-ev-001~003、F-ev-020、F-ev-021 |
| 01 | 中英混合前端与 g2p 管线 | 讲清 `g2p_cn_en` 单管线如何处理中英混读：数字转中文、双前端分工、跨界标记与 sos/eos 包裹 | 00 | F-ev-004~012 |
| 02 | 符号表与文本清洗 | 解析 symbols 拼接顺序、84 个 ARPAbet 符号、18 条缩写展开与数字规范化，理解 token 世界的边界 | 01 | F-ev-013~017 |
| 03 | PromptTTS 风格条件注入 | 剖析 StyleEncoder「多任务头训练、单嵌入推理」机制与 7 类情绪/3 类 pitch-energy-speed 标签体系 | 00 | F-ev-024、F-ev-025、F-ev-027、F-ev-029、F-ev-042 |
| 04 | JETS 联合训练与 HiFiGAN 声码器 | 解读 JETSGenerator 内嵌结构、损失权重（mel×45）、DDP 训练循环与 checkpoint 组织 | 03 | F-ev-018、F-ev-019、F-ev-022、F-ev-023、F-ev-030~032 |
| 05 | 标签体系、数据集与 MFA 对齐流水线 | 从 data/youdao 标签文件到 mfa/ 八步脚本，理解训练数据如何被制备与对齐插桩 | 01、03 | F-ev-026~029、F-ev-037、F-ev-038 |
| 06 | 服务化部署：OpenAI 兼容 API 与 Streamlit Demo | 讲解 openaiapi.py 兼容层、speed 后处理真相与 demo_page.py 交互形态 | 00、04 | F-ev-033~036、F-ev-039、F-ev-040 |

依赖关系：`00 → 01 → 02`；`00 → 03 → 04`；`01+03 → 05`；`00+04 → 06`。其中 04 与 06 是高级篇，其余为入门→进阶主线。

## 相关说明

- 本文件与 [facts.md](facts.md)、[sources.md](sources.md) 同属 references/ 信源层，为 concepts/（概念）、examples/（示例）的 E 阶段生成提供洞察框架。
- 事实编号引用区间均为闭区间或显式枚举，E 阶段生成文档时须逐条核对，不得超出 facts.md 已登记事实范围。
