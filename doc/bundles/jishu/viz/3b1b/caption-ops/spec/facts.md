---
type: spec
title: "caption_ops 字幕处理工具集源码事实采集（R阶段）"
---

# caption_ops 字幕处理工具集源码事实采集（R阶段）

## 模块概览表

| 模块 | 文件路径 | 核心内容 |
|------|----------|----------|
| 目录概览 | `caption_ops/` 根目录 | 工具脚本集合、子目录scripts/、data/ |
| 辅助工具 | `helpers.py` | 路径常量、字符串处理、JSON封装、目录映射 |
| 转录模块 | `transcribe_video.py` | faster-whisper本地转录、OpenAI API转录、词级时间戳 |
| 翻译模块 | `translate.py` | DeepL/Google翻译API、多语言批量翻译、SRT生成 |
| GPT翻译 | `gpt_translate.py` | GPT-4o上下文感知翻译、句子缩写、翻译对比采样 |
| SRT操作 | `srt_ops.py` | SRT读写、时间格式化、智能分句分段 |
| SRT时间调整 | `retime_srt.py` | 命令行工具：SRT时间戳整体偏移 |
| 句子时间轴 | `sentence_timings.py` | 模糊匹配对齐、词级到句级时间映射、SRT句子提取 |
| 下载模块 | `download.py` | YouTube音频下载、字幕下载、标题描述获取、本地/在线比对 |
| 上传模块 | `upload.py` | YouTube字幕上传、视频本地化更新、贡献者署名 |
| 贡献者追踪 | `track_contributors.py` | git log提取贡献者、手动补充名单 |
| CLI脚本 | `scripts/auto_caption.py` | 一键自动字幕管线（转录→翻译→上传） |
| CLI脚本 | `scripts/transcribe.py` | 单个音频文件转录命令行工具 |
| CLI脚本 | `scripts/sync_captions.py` | 单视频单语言字幕同步上传 |
| CLI脚本 | `scripts/sync_all_captions.py` | 全量字幕同步生成与上传 |
| CLI脚本 | `scripts/sync_transcription_update.py` | 转录文本更新后同步翻译文件 |
| CLI脚本 | `scripts/generate_missing_srt_files.py` | 批量从word_timings生成缺失SRT |
| CLI脚本 | `scripts/copy_transcriptions_to_audio_tracks.py` | 转录文件复制到音频目录 |
| CLI脚本 | `scripts/upload_all_new_languages.py` | 批量上传所有新语言字幕（含配额休眠） |

---

## 一、目录概览与配置

F-001：`caption_ops/` 根目录包含13个.py文件（`__init__.py`为空、`helpers.py`、`transcribe_video.py`、`translate.py`、`gpt_translate.py`、`srt_ops.py`、`retime_srt.py`、`sentence_timings.py`、`download.py`、`upload.py`、`track_contributors.py`、`reorganize.py`、`clear_trasnslated_titles.py`、`criblate_conversion.py`、`compile_audio_track_links.py`、`n_reviews_from_git_blame.py`）、1个`scripts/`子目录（含8个CLI脚本）、1个`data/`目录（含`manually-added-contributors.csv`）。

F-002：`caption_ops/.gitignore` 第1-4行忽略 `*.pyc`、`*.DS_Store`、`playground.py`、`updates.txt`。

F-003：`helpers.py` 第16行硬编码字幕根目录常量 `CAPTIONS_DIRECTORY = "/Users/grant/cs/captions"`。

F-004：`helpers.py` 第17行硬编码音频目录常量 `AUDIO_DIRECTORY = "/Users/grant/3Blue1Brown Dropbox/3Blue1Brown/audio_tracks"`。

F-005：`helpers.py` 第18行定义句子结尾正则模式 `SENTENCE_ENDING_PATTERN = r'(?<=[.!?])\s+|\.$|(?<=[।۔՝։።။។፡。！？])'`，支持英文、中文、日文、阿拉伯文、印地语等多语言标点。

F-006：`helpers.py` 第19行定义标点分割模式 `PUNCTUATION_PATTERN`，在句子结尾基础上增加逗号、冒号、分号、中文逗号等。

---

## 二、辅助工具模块（helpers.py）

F-007：`helpers.py` 第1-13行导入依赖：`Levenshtein`（编辑距离）、`numpy`、`os`、`sys`、`re`、`json`、`pycountry`（ISO语言代码）、`functools.lru_cache`、`contextlib.contextmanager`、`pathlib.Path`、`pytube.YouTube`、`pytube.extract.video_id`。

F-008：`helpers.py` 第22-31行定义上下文管理器 `temporary_message(message)`，在stdout输出临时消息（带\r回车覆盖），用于显示进度提示。

F-009：`helpers.py` 第34-35行定义线性插值函数 `interpolate(start, end, alpha) = (1 - alpha) * start + alpha * end`。

F-010：`helpers.py` 第38-41行定义 `ensure_exists(path)`，递归创建目录（若不存在）并返回路径。

F-011：`helpers.py` 第47-48行定义 `to_snake_case(name)`，将名称转为蛇形命名：小写、空格→下划线、冒号→下划线、双下划线→单下划线、移除斜杠。

F-012：`helpers.py` 第51-57行定义 `nearest_string(src, trg_list)`，基于Levenshtein编辑距离返回目标列表中与源字符串最接近的字符串及其距离。

F-013：`helpers.py` 第60-67行定义 `get_sentences(full_text, end_marks=SENTENCE_ENDING_PATTERN)`，使用正则按句末标点分割全文为句子列表，保留标点。

F-014：`helpers.py` 第70-78行定义 `get_language_code(language)`，将语言名称转换为ISO 639-1双字母代码；Hebrew特殊映射为`'iw'`，Greek映射为`'el'`，其余通过`pycountry.languages.get(name=...)`查询。

F-015：`helpers.py` 第81-85行定义 `get_language_from_code(language_code)`，反向查询：ISO代码→语言名称。

F-016：`helpers.py` 第91-104行定义JSON封装函数 `json_load(filename)` 和 `json_dump(obj, filename, indent=1, ensure_ascii=False)`，统一使用utf-8编码。

F-017：`helpers.py` 第110-117行定义 `get_all_files_with_ending(ending, root=CAPTIONS_DIRECTORY)`，递归遍历目录返回所有指定后缀的文件路径列表。

F-018：`helpers.py` 第120-126行定义 `@lru_cache()` 装饰的 `get_video_id_to_caption_directory_map()`，扫描所有`video_url.txt`文件构建`video_id → caption目录`映射缓存。

F-019：`helpers.py` 第129-150行定义 `create_default_directory(video_url)`，通过pytube获取视频信息，按`年/标题前三长词/`结构创建目录（shorts视频额外放入`shorts/`子目录），写入`video_url.txt`并清除缓存。

F-020：`helpers.py` 第153-162行定义 `url_to_directory(video_url, root=None)`，通过video_id查找对应目录；不存在则调用`create_default_directory`创建；可通过root参数替换根目录前缀。

---

## 三、转录模块（transcribe_video.py）

F-021：`transcribe_video.py` 第5行导入 `from faster_whisper import WhisperModel`，使用faster-whisper作为本地转录引擎（非OpenAI官方whisper）。

F-022：`transcribe_video.py` 第20-26行定义 `@lru_cache()` 装饰的 `load_whisper_model(model_name="medium.en")`，加载faster-whisper模型，默认`medium.en`、`device="cpu"`、`compute_type="int8"`（CPU量化加速）。

F-023：`transcribe_video.py` 第29-89行定义 `transcribe_file(model, audio_file, word_timestamps=True)`，调用faster-whisper转录音频，固定`language="en"`、`beam_size=1`，返回格式兼容OpenAI Whisper（含`text`、`segments`、`language`字段），segments中每个segment包含`start`/`end`/`text`，词级时间戳时额外包含`words`列表（每项`word`/`start`/`end`）。

F-024：`transcribe_video.py` 第57-80行转录过程使用`tqdm(total=info.duration)`进度条，按音频秒数更新进度。

F-025：`transcribe_video.py` 第92-156行定义 `transcribe_file_api(audio_file, word_timestamps=True)`，使用OpenAI Whisper API转录，需要`OPENAI_KEY`环境变量，调用`client.audio.transcriptions.create(model="whisper-1", response_format="verbose_json")`。

F-026：`transcribe_video.py` 第159-175行定义 `transcribe_file_with_fallback(audio_file, word_timestamps=True)`，先尝试API转录，失败则回退到本地faster-whisper模型。

F-027：`transcribe_video.py` 第178-183行定义 `get_words_with_timings(whisper_segments, precision=2)`，从Whisper segments中提取`[[word, start, end], ...]`列表，时间保留precision位小数。

F-028：`transcribe_video.py` 第186-189行定义 `save_word_timings(whisper_transcription, file_path)`，调用`get_words_with_timings`后以无缩进JSON格式保存词级时间戳。

F-029：`transcribe_video.py` 第192-207行定义 `words_with_timings_to_srt(words_with_timings, srt_path)`：拼接单词为全文→按句子分割→调用`get_sentence_timings`获取句子时间→调用`write_srt_from_sentences_and_time_ranges`写SRT；句子超过2000字符时输出警告。

F-030：`transcribe_video.py` 第210-235行定义 `write_whisper_srt(transcription, srt_path)`，直接从Whisper segments写SRT（不经过句子重分割），使用`datetime.timedelta`格式化时间戳。

---

## 四、翻译模块（translate.py + gpt_translate.py）

F-031：`translate.py` 第5-9行导入翻译API依赖：`google.cloud.translate_v2`（Google Translate）、`google.oauth2.service_account`、`deepl`（DeepL API）、`google_auth_oauthlib.flow`。

F-032：`translate.py` 第26-27行定义环境变量名常量：`GOOGLE_TRANSLATION_SERVICE_ACCOUNT`（Google服务账号JSON路径）、`DEEPL_KEY_FILE`（DeepL API密钥文件路径）。

F-033：`translate.py` 第28-48行定义目标语言列表 `TARGET_LANGUAGES`，包含19种语言：Spanish、Hindi、Chinese、French、Russian、German、Arabic、Italian、Portuguese、Japanese、Korean、Ukrainian、Thai、Persian、Indonesian、Hebrew、Turkish、Hungarian、Vietnamese。

F-034：`translate.py` 第51-60行定义 `@lru_cache()` 的 `get_deepl_translator()`，从`DEEPL_KEY_FILE`环境变量指向的文件读取密钥，返回`deepl.Translator`实例。

F-035：`translate.py` 第63-72行定义 `@lru_cache()` 的 `get_google_translate_client(service_account_file=None)`，从服务账号JSON文件创建Google Translate v2客户端。

F-036：`translate.py` 第75-94行定义 `deepl_translate_sentences(src_sentences, target_language_code, src_language_code="en")`，调用DeepL API批量翻译句子，使用`formality="prefer_less"`（非正式语体），返回格式为`[{input, translatedText, model: "DeepL"}, ...]`。

F-037：`translate.py` 第97-115行定义 `google_translate_sentences(src_sentences, target_language_code, src_language_code="en", chunk_size=50, model=None)`，按chunk_size分批（默认50句）调用Google Translate API，标记`model: "google_nmt"`。

F-038：`translate.py` 第118-140行定义 `translate_sentences(en_sentences, target_language)`，策略：DeepL支持的语言优先用DeepL（失败回退Google），不支持的语言直接用Google；每条翻译初始`n_reviews: 0`。

F-039：`translate.py` 第174-192行定义 `sentence_translations_to_srt(sentence_translation_file)`，从翻译JSON生成SRT；中日韩语言（character_based）每段最多30字符，其他语言90字符；输出文件名为`auto_generated.srt`。

F-040：`gpt_translate.py` 第14-47行定义 `gpt4_translate(sentences, language, formality="informal", n_context_sentences=2)`，使用OpenAI GPT-4o进行上下文感知翻译：system prompt要求非正式第二人称、教育视频旁白风格；每条句子翻译时保留最近`2*n_context_sentences`条对话历史作为上下文；`temperature=0.3`低随机性；`max_tokens=2*len(sentence)`限制输出长度。

F-041：`gpt_translate.py` 第50-76行定义 `gpt4_abbreviate(sentence, language, proportion)`，调用GPT-4o将句子缩写到原长度的指定比例（0-1），`temperature=0.0`。

---

## 五、SRT操作模块（srt_ops.py + retime_srt.py）

F-042：`srt_ops.py` 第1-6行导入依赖：`re`、`regex`（第三方正则库，支持复杂Unicode）、`numpy`、`pathlib.Path`、`pysrt`（SRT文件读写）、`datetime`。

F-043：`srt_ops.py` 第13-19行定义 `format_time(seconds)`，将秒数转换为SRT标准时间格式`HH:MM:SS,mmm`。

F-044：`srt_ops.py` 第22-31行定义 `unformat_time(timestamp)`，反向解析SRT时间戳为秒数，校验格式（必须2个冒号、最多1个逗号）。

F-045：`srt_ops.py` 第34-40行定义 `sub_rip_time_to_seconds(sub_rip_time)`，将pysrt的SubRipTime对象转换为秒数。

F-046：`srt_ops.py` 第43-56行定义 `write_srt(segments, file_name)`，接收`[(text, start_seconds, end_seconds), ...]`列表，通过pysrt创建SubRipItem列表并保存为UTF-8编码SRT文件。

F-047：`srt_ops.py` 第78-131行定义核心函数 `write_srt_from_sentences_and_time_ranges(sentences, time_ranges, output_file_path, max_chars_per_segment=90)`：按max_chars_per_segment分割长句，优先在标点处切割、其次在空格处切割、字符型语言直接硬切；切割点时间使用线性插值；最后排序starts/ends防止时间重叠。

F-048：`retime_srt.py` 第5-32行实现SRT时间偏移功能：`parse_time`/`format_time`处理`%H:%M:%S,%f`格式，`shift_timestamps(line, seconds)`将时间戳向前回退指定秒数（禁止负时间）。

F-049：`retime_srt.py` 第56-70行定义CLI入口：接受三个位置参数`input_file`、`output_file`、`seconds`（正浮点数），使用argparse解析。

---

## 六、句子时间轴模块（sentence_timings.py）

F-050：`sentence_timings.py` 第1-4行导入依赖：`re`、`numpy`、`pysrt`、`Levenshtein`。

F-051：`sentence_timings.py` 第16-56行定义核心模糊对齐算法 `find_closest_aligning_substring_indices(full_text, sentences, max_shift=300, radius=20, sentence_end_bias=2)`：基于Levenshtein距离在全文中滑动窗口查找相邻句子边界，句末标点位置有偏置加成（sentence_end_bias），返回句子边界索引列表。

F-052：`sentence_timings.py` 第64-100行定义 `get_sentence_timings(words_with_timings, sentences, **kwargs)`：将词级时间戳映射到句级时间，先通过词长度累积构建词索引→全文→模糊匹配句子边界→在词索引中查找最近的词时间作为句子起止时间。

F-053：`sentence_timings.py` 第103-107行定义 `get_sentences_with_timings(words_with_timings)`，便捷函数：拼接单词→按标点分句→获取时间范围，返回`(sentences, time_ranges)`二元组。

F-054：`sentence_timings.py` 第128-168行定义 `get_substring_timings_from_srt(srt_file, ...)`，从现有SRT文件反推句子时间戳，支持按句末标点合并SRT分段（split_at_segments=False时）。

---

## 七、下载与上传模块（download.py + upload.py）

F-055：`download.py` 第6-7行导入YouTube相关依赖：`pytube.YouTube`（视频/音频下载）、`youtube_transcript_api.YouTubeTranscriptApi`（字幕获取）。

F-056：`download.py` 第22-28行定义 `download_youtube_audio(url, file_path)`，通过pytube下载最高码率纯音频流（`only_audio=True, file_extension="mp4"`，按abr降序取第一个）。

F-057：`download.py` 第169-190行定义 `download_captions(video_id, directory, suffix="community")`，通过YouTubeTranscriptApi获取所有非英语字幕，保存为`{language}_{suffix}.srt`格式。

F-058：`upload.py` 第4-9行导入YouTube Data API依赖：`google_auth_oauthlib.flow`、`googleapiclient.discovery`、`google.auth.transport.requests`、`google.oauth2.credentials.Credentials`、`googleapiclient.http.MediaFileUpload`。

F-059：`upload.py` 第30-31行定义环境变量常量：`YOUTUBE_UPLOADING_KEY`（客户端密钥JSON）、`YOUTUBE_CREDENTIALS_FILE`（OAuth凭证存储路径）；OAuth scope为`https://www.googleapis.com/auth/youtubepartner`。

F-060：`upload.py` 第35-70行定义 `@lru_cache()` 的 `get_youtube_api()`，实现OAuth2认证流程：优先从凭证文件加载→过期则refresh→无有效凭证则启动本地服务器OAuth流程→保存凭证供下次使用→返回YouTube Data API v3客户端。

F-061：`upload.py` 第98-128行定义 `upload_caption(youtube_api, video_id, caption_file, name="", replace=False, language_code=None)`，通过`captions().insert()`上传SRT文件；replace=True时先删除现有字幕；配额超限抛出异常。

F-062：`upload.py` 第131-205行定义 `upload_video_localizations(youtube_api, caption_directory, video_id, languages=None)`，从各语言目录的`title.json`和`description.json`读取翻译，调用`videos().update()`更新YouTube视频本地化标题和描述。

---

## 八、CLI脚本与数据管线

F-063：`scripts/auto_caption.py` 第39-78行定义 `write_whisper_transcription_files(audio_file, directory, ...)`，完整生成英文字幕产物：`word_timings.json`（词级时间）→`sentence_timings.json`（句级时间）→`full_sentences.srt`（完整句子SRT）→`captions.srt`（分段SRT）→`transcript.txt`（纯文本）。

F-064：`scripts/auto_caption.py` 第81-122行定义 `auto_caption(video_url, upload=True, languages=None)`，端到端自动字幕管线：定位本地音频文件（优先`only_narration.mp3/wav`，其次`original_audio.mp3/wav`）→生成英文转录文件→翻译到指定语言→上传不匹配的字幕。

F-065：`scripts/auto_caption.py` 第125-148行CLI入口：位置参数`video`（YouTube URL或含URL列表的txt文件），可选参数`--languages`（语言列表，`all`表示TARGET_LANGUAGES全量）、`--no-upload`（禁用上传）。

F-066：`scripts/transcribe.py` 第17-34行单文件转录CLI：接受`audio_file`位置参数，输出`transcription_sentences.srt`、`captions.srt`（max_chars_per_segment=50）、`word_timings.json`。

F-067：`scripts/sync_all_captions.py` 第40-56行定义 `sync_srts_to_translations(trans_file)`，从翻译JSON重新生成SRT；当审核比例>50%时将旧的community.srt重命名为community_old.srt；有空翻译时跳过。

F-068：`scripts/sync_transcription_update.py` 第23-81行定义转录更新同步：接受修改后的`transcript.txt`或`captions.srt`，重新分句→更新sentence_timings→更新各语言的sentence_translations.json中input字段（模糊匹配对齐）→可上传。

F-069：`scripts/upload_all_new_languages.py` 第11-27行定义批量上传循环：遍历所有视频URL→上传新语言字幕→配额超时时休眠12小时后重试（将当前URL放回队列尾部）。

F-070：`track_contributors.py` 第30-48行定义 `get_contributor_names(folder)`，通过`git -C {LOCAL_REPO} log {folder}`提取提交者（Author行）和网页编辑者（Edit ... by行），排除"Grant Sanderson"本人。

---

## 九、外部依赖总结

F-071：本地可运行依赖（无需API密钥）：`faster-whisper`（本地语音转录）、`pysrt`（SRT读写）、`Levenshtein`（编辑距离模糊匹配）、`pytube`（YouTube视频下载）、`youtube_transcript_api`（YouTube字幕下载）、`pycountry`（语言代码转换）、`regex`（高级正则）、`numpy`、`tqdm`（进度条）、`pandas`（CSV读取，track_contributors用）。

F-072：外部API依赖（需密钥/凭证）：OpenAI API（`OPENAI_KEY`，Whisper转录+GPT-4o翻译）、DeepL API（`DEEPL_KEY_FILE`，翻译）、Google Cloud Translation（`GOOGLE_TRANSLATION_SERVICE_ACCOUNT`，翻译回退）、YouTube Data API v3（`YOUTUBE_UPLOADING_KEY`+OAuth，字幕上传/视频本地化）。
