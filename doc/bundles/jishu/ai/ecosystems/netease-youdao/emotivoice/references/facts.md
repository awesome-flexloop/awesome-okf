---
type: reference
title: "EmotiVoice 源码事实清单（v0.3 @ 59f0f36）"
tags: [emotivoice, tts, reference, source-code, netease-youdao]
sources:
  - id: emotivoice-repo
    resource: vendor/netease-youdao/EmotiVoice/
    title: EmotiVoice 源码仓库（git submodule，固定基线 59f0f36）
    files:
      - README.md
      - inference_am_vocoder_joint.py
      - inference_tts.py
      - frontend.py
      - frontend_cn.py
      - frontend_en.py
      - text/symbols.py
      - text/__init__.py
      - text/cleaners.py
      - text/numbers.py
      - text/cmudict.py
      - models/hifigan/get_vocoder.py
      - models/hifigan/models.py
      - models/prompt_tts_modified/jets.py
      - models/prompt_tts_modified/simbert.py
      - models/prompt_tts_modified/prompt_dataset.py
      - config/joint/config.py
      - config/joint/config.yaml
      - train_am_vocoder_joint.py
      - openaiapi.py
      - demo_page.py
      - mfa/
      - requirements.txt
      - requirements.openaiapi.txt
---

# EmotiVoice 源码事实清单

本文件登记 EmotiVoice 源码（vendor 子模块 `vendor/netease-youdao/EmotiVoice/`，git 基线 `59f0f36de4db12825f4705dd4e0780d79dd6bb01`）的编号事实，前缀 F-ev-，从 F-ev-001 连续编号。所有事实均直接来自源码文本，不含推断性表述。

## 事实清单

| 编号 | 事实陈述 | 证据位置 |
|------|----------|----------|
| F-ev-001 | 推理主入口为 `inference_am_vocoder_joint.py`；测试文件每一行按 `|` split 为 4 段：speaker、prompt、phoneme text、content；输出写入 `root_path + "/test_audio/audio/" + checkpoint_name + "/{i+1}.wav"`。 | `vendor/netease-youdao/EmotiVoice/inference_am_vocoder_joint.py` |
| F-ev-002 | README 给出的推理命令为 `python inference_am_vocoder_joint.py --logdir prompt_tts_open_source_joint --config_folder config/joint --checkpoint g_00140000 --test_file $TEXT`；输出目录为 `outputs/prompt_tts_open_source_joint/test_audio`。 | `vendor/netease-youdao/EmotiVoice/README.md` |
| F-ev-003 | README 定义推理文本格式为 `<speaker>\|<style_prompt/emotion_prompt/content>\|<phoneme>\|<content>`。 | `vendor/netease-youdao/EmotiVoice/README.md` |
| F-ev-004 | `frontend.py` 的 `g2p_cn_en(text, g2p, lexicon)` 是中英混合 g2p 入口；处理顺序为：先 `tn_chinese(text)` 做数字转中文，再用 `re_english_word` 正则切分中英文，中文走 `g2p_cn`、英文走 `get_eng_phoneme`，插入跨界标记 `eng_cn_sp`/`cn_eng_sp`，首尾包裹 `<sos/eos>`。 | `vendor/netease-youdao/EmotiVoice/frontend.py`（`g2p_cn_en`） |
| F-ev-005 | `frontend.py` 的 `__main__` 支持命令行用法 `python frontend.py data/my_text.txt > data/my_text_for_tts.txt` 生成音素文本。 | `vendor/netease-youdao/EmotiVoice/frontend.py`（`__main__`） |
| F-ev-006 | `frontend_cn.py` 的 `g2p_cn(text)` 用 `jieba.cut` 分词，再调 `pypinyin(pinyin, style=Style.TONE3, neutral_tone_with_five=True)`；标点转为 `sp3`，字间插 `sp0`、词间插 `sp1`。 | `vendor/netease-youdao/EmotiVoice/frontend_cn.py`（`g2p_cn`） |
| F-ev-007 | `frontend_cn.py` 的 `tn_chinese(text)` 经 `re_digits = re.compile('(\d[\d\.]*)')` 捕获数字，调用 `number_to_chinese`，再经 vendored `cn2an.An2Cn().an2cn()` 转中文数字。 | `vendor/netease-youdao/EmotiVoice/frontend_cn.py`（`tn_chinese`、`re_digits`） |
| F-ev-008 | `frontend_cn.py` 的 `split_py(py)` 将拼音切分为声母、韵母两部分。 | `vendor/netease-youdao/EmotiVoice/frontend_cn.py`（`split_py`） |
| F-ev-009 | `frontend_cn.py` 模块级调用 `cc_cedict.load()`（来自 `pypinyin_dict`）。 | `vendor/netease-youdao/EmotiVoice/frontend_cn.py`（模块级 import 与调用） |
| F-ev-010 | `frontend_en.py` 的 `read_lexicon(lex_path)` 读取 `lexicon/librispeech-lexicon.txt`。 | `vendor/netease-youdao/EmotiVoice/frontend_en.py`（`read_lexicon`） |
| F-ev-011 | `frontend_en.py` 的 `get_eng_phoneme(text, g2p, lexicon, pad_sos_eos=True)`：词在 lexicon 中取音素并包 `[...]`，词间插 `engsp1`，标点尾部插 `engsp4`；g2p 实例为 `g2p_en.G2p`。 | `vendor/netease-youdao/EmotiVoice/frontend_en.py`（`get_eng_phoneme`） |
| F-ev-012 | `frontend_en.py` 定义 `ROOT_DIR = os.path.dirname(os.path.abspath("__file__"))`；`openaiapi.py` 经 `frontend.py` 从 `frontend_en` 再导出 `g2p_cn_en`、`ROOT_DIR`、`read_lexicon`、`G2p`。 | `vendor/netease-youdao/EmotiVoice/frontend_en.py`、`openaiapi.py`（import 语句） |
| F-ev-013 | `text/__init__.py` 暴露 `text_to_sequence(text, cleaner_names)`（支持花括号 ARPAbet 语法）、`sequence_to_text`，以及 `_symbol_to_id` / `_id_to_symbol` 双向映射。 | `vendor/netease-youdao/EmotiVoice/text/__init__.py` |
| F-ev-014 | `text/symbols.py`（注明源自 tacotron）定义：`_pad="_"`、`_punctuation="!'(),.:;? "`、`_special="-"`、26 个小写 + 26 个大写字母、`_silences=["@sp","@spn","@sil"]`、`_arpabet=["@"+s for s in cmudict.valid_symbols]`；`symbols` 按 pad→special→punctuation→letters→arpabet→silences 顺序拼接。 | `vendor/netease-youdao/EmotiVoice/text/symbols.py` |
| F-ev-015 | `text/cmudict.py` 的 `valid_symbols` 共 84 个 ARPAbet 符号（15 个元音各含无调原形及 0/1/2 三档声调共 60 个 + 24 个辅音）。 | `vendor/netease-youdao/EmotiVoice/text/cmudict.py`（`valid_symbols`，已逐行计数） |
| F-ev-016 | `text/cleaners.py` 含 18 条缩写展开表（mrs/mr/dr/st/co/jr/maj/gen/drs/rev/lt/hon/sgt/capt/esq/ltd/col/ft，已逐条计数），以及 `basic_cleaners`、`transliteration_cleaners`（unidecode）、`english_cleaners` 三个管线函数。 | `vendor/netease-youdao/EmotiVoice/text/cleaners.py` |
| F-ev-017 | `text/numbers.py` 以 inflect 引擎为核心，含逗号数字、小数、英镑、美元、序数词、普通数字六组正则替换规则。 | `vendor/netease-youdao/EmotiVoice/text/numbers.py` |
| F-ev-018 | `models/prompt_tts_modified/jets.py` 的 `JETSGenerator(nn.Module)` 在 `__init__(config)` 中设置 `self.am = PromptTTS(config)`、`self.generator = HiFiGANGenerator(config.model)`、`self.upsample_factor = int(np.prod(config.model.upsample_rates))`、`self.segment_size = config.segment_size`。 | `vendor/netease-youdao/EmotiVoice/models/prompt_tts_modified/jets.py`（`JETSGenerator.__init__`） |
| F-ev-019 | `JETSGenerator.forward` 签名为 `forward(self, inputs_ling, input_lengths, inputs_speaker, inputs_style_embedding, inputs_content_embedding, mel_targets=None, output_lengths=None, pitch_targets=None, energy_targets=None, alpha=1.0, cut_flag=True)`；训练分支经 `get_random_segments` 切 mel 段后调 `self.generator(z_segments)`，结果写入 `outputs["wav_predictions"]`。 | `vendor/netease-youdao/EmotiVoice/models/prompt_tts_modified/jets.py`（`JETSGenerator.forward`） |
| F-ev-020 | `inference_tts.py` 的推理调用为 `generator(inputs_ling=sequence, inputs_style_embedding=style_embedding, input_lengths=sequence_len, inputs_content_embedding=content_embedding, inputs_speaker=speaker, alpha=1.0)`；输出经 `infer_output["wav_predictions"].squeeze() * MAX_WAV_VALUE` → `astype('int16')` → `sf.write(..., samplerate=config.sampling_rate)`。 | `vendor/netease-youdao/EmotiVoice/inference_tts.py` |
| F-ev-021 | `inference_tts.py` 的入口函数签名为 `main(args, config, gpu_id, start_idx, chunk_num)`；按 `gpu_ids` 与 `num_thread` 对测试文件分块，多进程并行推理。 | `vendor/netease-youdao/EmotiVoice/inference_tts.py`（`main`） |
| F-ev-022 | `models/hifigan/get_vocoder.py` 定义 `MAX_WAV_VALUE = 32768.0`；`vocoder(hifi_gan_path, hifi_gan_name)` 在 CPU 上加载（读 config.json 为 AttrDict、取 `state_dict_g['generator']`、`remove_weight_norm()`）；另有 `vocoder2(config, hifi_gan_ckpt_path)` 与 `vocoder_inference(vocoder, melspec, max_db, min_db)`。 | `vendor/netease-youdao/EmotiVoice/models/hifigan/get_vocoder.py` |
| F-ev-023 | `models/hifigan/models.py` 注明改自 jik876/hifi-gan；定义 `ResBlock1`（dilation (1,3,5)，每组 3 个卷积）、`ResBlock2`（dilation (1,3)）、`Generator`、`discriminator_loss`、`generator_loss`、`feature_loss`。 | `vendor/netease-youdao/EmotiVoice/models/hifigan/models.py` |
| F-ev-024 | `models/prompt_tts_modified/simbert.py` 的 `StyleEncoder(nn.Module)`：`self.bert = AutoModel.from_pretrained(config.bert_path)`；含 4 个 `ClassificationHead`（pitch/speed/energy/emotion，hidden→num_labels）；`self.style_embed_proj = nn.Linear(config.bert_hidden_size, config.style_dim)`；forward 返回 dict，键含 `pooled_output`、`pitch_outputs`、`speed_outputs`、`energy_outputs`、`emotion_outputs`。 | `vendor/netease-youdao/EmotiVoice/models/prompt_tts_modified/simbert.py`（`StyleEncoder`） |
| F-ev-025 | `inference_tts.py` 的 `get_style_embedding(prompt, tokenizer, style_encoder)` 返回 `output["pooled_output"].cpu().squeeze().numpy()`；同文件固定 prompts 列表为 `['Happy', 'Excited', 'Sad', 'Angry']`（源码注释 `# prompt is not efficient.`）。 | `vendor/netease-youdao/EmotiVoice/inference_tts.py`（`get_style_embedding`、prompts 列表） |
| F-ev-026 | `models/prompt_tts_modified/prompt_dataset.py` 的 `Dataset_PromptTTS(torch.utils.data.Dataset)` 定义 `get_style_embedding(self, uttid, prompt, dir)`（L106），含 npy 缓存逻辑（`np.load` 或计算后 `np.save`）；方法 `TextMelCollate(self, data)` 在 L179（另有一个同名方法在 `Dataset_Prompt_Pretrain` 的 L292）；batch 键含 `style_embedding` 与 `content_embedding`，分别由 prompt 与 original_text 计算。 | `vendor/netease-youdao/EmotiVoice/models/prompt_tts_modified/prompt_dataset.py` |
| F-ev-027 | `data/youdao/text/` 下标签文件实测：`speaker2` 共 2014 行（speaker 计数）、`tokenlist` 共 502 行（n_symbols）、`emotion` 7 类（普通/生气/开心/惊讶/悲伤/厌恶/恐惧）、`pitch`/`energy`/`speed` 各 3 类。 | `vendor/netease-youdao/EmotiVoice/data/youdao/text/`（speaker2、tokenlist、emotion、pitch、energy、speed，已逐文件计数） |
| F-ev-028 | `data/youdao/text/README.md` 是 voice wiki 表格，音色主要来自 LibriTTS/HiFiTTS 数据集。 | `vendor/netease-youdao/EmotiVoice/data/youdao/text/README.md` |
| F-ev-029 | `config/joint/config.py` 的 `Config` 类：`DATA_DIR = ROOT_DIR + "/data/youdao/"`、`bert_path = 'WangZeJun/simbert-base-chinese'`、`style_encoder_ckpt = ROOT_DIR + "/outputs/style_encoder/ckpt/checkpoint_163431"`、`bert_hidden_size = 768`、`style_dim = 128`、`batch_size = 16`、`train_steps = 10_000_000`、`iters_per_validation = 1000`、`iters_per_checkpoint = 10000`、`sampling_rate = 16_000`、80 mel 通道、`pitch_min = 80`、`pitch_max = 400`；`n_symbols`/`speaker_n_labels`/`emotion_n_labels` 由 `get_labels_length` 从 `data/youdao/text/` 下文件计数。 | `vendor/netease-youdao/EmotiVoice/config/joint/config.py`（`Config`、`get_labels_length`） |
| F-ev-030 | `config/joint/config.yaml` 关键配置：sr 16000、hop_size 256、win_size 1024、80 mels、segment_size 32、cut_sil True；model 段 speaker_embed_dim 384、bert_embedding 768、encoder/decoder 各 4 层 8 头 hidden 384、upsample_rates [8,8,2,2]、upsample_kernel_sizes [16,16,4,4]、initial_channel 80、upsample_initial_channel 512、resblock "1"、resblock_kernel_sizes [3,7,11]、resblock_dilation_sizes [[1,3,5]×3]；optimizer lr 1.25e-5、betas [0.5, 0.9]；scheduler gamma 0.999875。 | `vendor/netease-youdao/EmotiVoice/config/joint/config.yaml` |
| F-ev-031 | `train_am_vocoder_joint.py` 的 `train(args, config)`：`torch.distributed.init_process_group(backend="nccl", init_method="env://")`；StyleEncoder 冻结加载（`load_state_dict(..., strict=False)` 且 key 经 `key[7:]` 去前缀）；数据侧 `Dataset_PromptTTS_JETS` + `DistributedSampler` + DataLoader(num_workers=8)；模型侧 `generator = JETSGenerator(conf)`、`discriminator = Discriminator(conf)`（来自 `models.hifigan.pretrained_discriminator`）；均经 DDP 包装；优化器 Adam(lr=conf.optimizer.lr, betas=conf.optimizer.betas)、调度器 ExponentialLR(gamma=conf.scheduler.gamma)；损失 `loss_fn = TTSLoss()`。 | `vendor/netease-youdao/EmotiVoice/train_am_vocoder_joint.py`（`train`） |
| F-ev-032 | 生成器损失组合为 `loss_gen + loss_fm + dec_mel_loss*45 + dur_loss*1 + pitch_loss*1 + energy_loss*1 + forwardsum_loss*2 + bin_loss*2`（其中 dec_mel_loss 实际以 `F.l1_loss(y_mel, y_hat_mel)` 计算覆盖）；判别器损失为 `discriminator_loss`（f/s 两组）；checkpoint 命名 `g_{:08d}` / `do_{:08d}`（含 discriminator、optim_g、optim_d、steps、epoch）；`scan_checkpoint` 模式为 `prefix + '????????'`；每 `iters_per_validation` 跑 validate；epoch 上限 5_000_000。 | `vendor/netease-youdao/EmotiVoice/train_am_vocoder_joint.py` |
| F-ev-033 | `openaiapi.py` 是 FastAPI 服务：模块级执行 `config = Config()`、`models = get_models()`、`app = FastAPI()`；`scan_checkpoint(cp_dir, prefix, c=8)`；`get_models()` 返回 `(style_encoder, generator, tokenizer, token2id, speaker2id)`；核心推理函数 `emotivoice_tts(text, prompt, content, speaker, models)`；路由为 `@app.post("/v1/audio/speech")`。 | `vendor/netease-youdao/EmotiVoice/openaiapi.py` |
| F-ev-034 | `openaiapi.py` 的 `class SpeechRequest(BaseModel)` 字段：`input: str`、`voice: str = '8051'`、`prompt: Optional[str] = ''`、`language: Optional[str] = 'zh_us'`、`model: Optional[str] = 'emoti-voice'`、`response_format: Optional[str] = 'mp3'`、`speed: Optional[float] = 1.0`。 | `vendor/netease-youdao/EmotiVoice/openaiapi.py`（`SpeechRequest`） |
| F-ev-035 | `openaiapi.py` 中 speed≠1.0 时调用 `pyrubberband.time_stretch`；WAV 经 `soundfile` 写入 BytesIO，非 wav 格式经 `pydub.AudioSegment` 转码；响应为 `Response(content=..., media_type=f"audio/{response_format}")`。 | `vendor/netease-youdao/EmotiVoice/openaiapi.py`（路由处理函数） |
| F-ev-036 | `demo_page.py` 是 Streamlit 交互页：`get_models()` 带 `@st.cache_resource`；推理函数 `tts(name, text, prompt, content, speaker, models)`；语言下拉仅 `["zh_us"]`；speaker 下拉来自 `config.speakers`。 | `vendor/netease-youdao/EmotiVoice/demo_page.py` |
| F-ev-037 | `mfa/` 目录共 8 个 step 脚本（step1_create_dataset、step2_prepare_data、step3_prepare_special_tokens、step4_convert_text_to_phn、step5_prepare_alignment、step7_gen_alignment_from_textgrid、step8_make_data_list、step9_datalist_from_mfa；编号无 step6，已 Glob 计数）。 | `vendor/netease-youdao/EmotiVoice/mfa/`（*.py，已计数） |
| F-ev-038 | `mfa/step1_create_dataset.py` 把 datalist.jsonl 转为 `text_sp1-sp4` 与 `wav.scp`，并做 `cn_eng_sp→cnengsp` 等特殊标记转换；`mfa/step7_gen_alignment_from_textgrid.py` 用 `praatio.textgrid.openTextgrid` 读 TextGrid，处理 MFA1.x/MFA2.x 空标签差异，向对齐音素序列插入 special tokens。 | `vendor/netease-youdao/EmotiVoice/mfa/step1_create_dataset.py`、`mfa/step7_gen_alignment_from_textgrid.py` |
| F-ev-039 | `requirements.txt` 共 13 项依赖（torch、torchaudio、numpy、numba、scipy、transformers、soundfile、yacs、g2p_en、jieba、pypinyin、pypinyin_dict、streamlit，已逐行计数）；README 安装命令为 `pip install torch torchaudio numpy numba scipy transformers soundfile yacs g2p_en jieba pypinyin pypinyin_dict` 加 `python -m nltk.downloader "averaged_perceptron_tagger_eng"`。 | `vendor/netease-youdao/EmotiVoice/requirements.txt`、`README.md` |
| F-ev-040 | `requirements.openaiapi.txt` 共 5 项依赖（fastapi、python-multipart、uvicorn[standard]、pydub、pyrubberband，已逐行计数）。 | `vendor/netease-youdao/EmotiVoice/requirements.openaiapi.txt` |
| F-ev-041 | `cn2an/` 为 vendored cn2an，仅含 `an2cn.py`、`conf.py` 两个文件（已 Glob 计数）。 | `vendor/netease-youdao/EmotiVoice/cn2an/` |
| F-ev-042 | 仓库许可证为 Apache-2.0；README ROADMAP 声明仅用 pitch/speed/energy/emotion 作为 style factors，不使用 gender。 | `vendor/netease-youdao/EmotiVoice/README.md` |

## 基线与采集说明

- git 基线：`59f0f36de4db12825f4705dd4e0780d79dd6bb01`（`git log -1` 验证，对应 v0.3）。
- 计数类事实（F-ev-015、F-ev-016、F-ev-027、F-ev-037、F-ev-039、F-ev-040、F-ev-041）均经 Glob/逐行计数实测。
- 本文件仅含源码可证实的事实；读不到或未细读的部分（见下）未纳入。

## 未覆盖/存疑项

- `data/inference/text` 内容未读。
- `models/hifigan/env.py`、`dataset.py`、`pretrained_discriminator.py` 未细读。
- `models/prompt_tts_modified/` 目录共 11 个 `.py` 文件，其中 `encoder.py`、`decoder.py`、`variance_adaptor.py`、`optimizer.py`、`loss.py`、`data_module.py` 等未逐一细读。
