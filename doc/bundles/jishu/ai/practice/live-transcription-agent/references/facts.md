---
type: Reference
title: 可引用事实登记
sources:
  - {id: sources, resource: source-manifest.md}
  - {id: fixture, resource: ../examples/agent-evidence-check.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 可引用事实登记

S 编号指向[来源清单](source-manifest.md)中的固定版本或官方网页。下表区分上游声明、源码静态核查、历史材料和本包程序测试；“确认存在某接口”不等于在本机确认了运行效果。

| 编号 | 事实陈述 | 来源与核验类型 | 限定 |
|---|---|---|---|
| F-001 | OBS Windows 应用音频指南要求 Windows 10 2004+ 或 Windows 11；OBS 28+ 提供应用音频捕获，30.1 的窗口/游戏捕获可包含音频选项。 | S01，官方文档 | 捕获应用后还需避免 Desktop Audio 重复收声；未实机测试 |
| F-002 | macOS 13+ 的 OBS 30+ 可使用独立 macOS Audio Capture；较旧 OBS 28/29 可通过 Screen Capture 捕获音频。 | S02，官方文档 | 不把 macOS 操作照搬到 Windows/Linux |
| F-003 | OBS 包含 Linux PulseAudio 设备输入实现；所查 PipeWire 应用音频插件是第三方项目，声明 OBS 28、WirePlumber 等条件。 | S03，源码与 README | 原生设备源与第三方按应用捕获不是同一能力 |
| F-004 | OBS 格式指南区分普通 MP4/MOV 与 MKV、fragmented/hybrid MP4 的中断恢复特征。 | S04，官方文档 | 不依赖页面不一致的默认格式表述；本包无断电实验 |
| F-005 | Streamlink 的 output、record、stdout 是不同输出模式；输出文件扩展名不负责转换媒体封装。 | S07，参数与文档 | 不把命名为 MP4 当作已转码或已重封装 |
| F-006 | Streamlink 的 HLS live restart 从当前播放列表可用起点开始，重试选项不能恢复已离开窗口的片段。 | S07，文档与 HLS 实现 | 不承诺开播起点或完整历史 |
| F-007 | FFmpeg stream-copy 视频分段受关键帧约束，实际切点可晚于指定 segment_time。 | S05，文档与实现 | 目标段长不能直接作为实际时间偏移 |
| F-008 | FFmpeg segment CSV 可记录段起止时间；reset_timestamps 重置段内时间；strftime 属文件命名时间格式。 | S05，文档 | 媒体时间和墙钟仍需单独建模 |
| F-009 | FFmpeg HTTP reconnect 选项分别针对连接、网络错误、流式输入等场景。 | S06，官方文档 | 重连不是断线历史补录 |
| F-010 | 所查 yt-dlp README 将 live-from-start 标为实验功能，并列出 YouTube、Twitch、TVer、mellow-fan 的支持范围。 | S08，官方 README | 不推广到所有站点；默认通常从当前直播位置开始 |
| F-011 | yt-dlp 提供 abort-on-unavailable-fragments；download-sections 用于选择下载区间。 | S08，官方 README | 默认跳缺片与严格失败不同；区间下载不等于周期切段 |
| F-012 | Bililive-go、DouyinLiveRecorder、StreamCap 均提供直播录制相关功能；Bililive-go 特定 FLV 代理路径、StreamCap 直链处理有各自分段条件。 | S09–S11，README 与源码 | 平台支持列表不是当前连通性证明；没有读取账号凭证 |
| F-013 | Whisper 的完整文件转录使用滑动 30 秒窗口；模型表区分多语与 .en 模型；项目声明代码与权重使用 MIT。 | S12，官方 README | 不据模型名推定本机实时速度 |
| F-014 | faster-whisper 使用 CTranslate2；transcribe 返回的 segments 是生成器；所查 GPU 文档列出 CUDA 12 cuBLAS 和 cuDNN 9。 | S13，官方 README | 结果惰性迭代不等于流式音频输入；需匹配安装版本 |
| F-015 | 所查 faster-whisper 源码在本地模型目录缺少 tokenizer.json 时调用 Tokenizer.from_pretrained；local_files_only 参数没有直接封住该分支。 | S13，源码静态核查 | 示例只消除这个已知回退，完整离线仍未实测 |
| F-016 | whisper.cpp 文档列出 CPU、CUDA、Metal/CoreML 和 OpenVINO 路径；stream 示例循环取样后执行 Whisper 窗口推理。 | S14，README 与源码 | 500 ms 采样步长不等于 500 ms 字幕延迟；OpenVINO 描述限 encoder |
| F-017 | WhisperLive 自述近实时转录，支持多个后端；所查消息结构有时间字段和 completed 状态。 | S15，README 与源码 | 消息定稿语义需映射到本包 final，非直接等同 |
| F-018 | WhisperLiveKit 文档说明 AlignAtt/SimulStreaming/LocalAgreement 等策略；所查 Qwen3-ASR 因果流式路径标注英语支持范围。 | S16，README 与 API | 不能推定所有后端均支持中文原生流式 |
| F-019 | FunASR 的 paraformer-zh-streaming 示例使用 cache、is_final、chunk_size；[0,10,5] 对应 600 ms 输入块。 | S17，官方 README | 输入块时长不是端到端延迟；代码与模型许可分开 |
| F-020 | SenseVoiceSmall 文档列出中、粤、英、日、韩；当前示例包含 output_timestamp=True 和毫秒时间对。 | S18，官方 README | 非自回归不等于原生流式；仍需核对所用模型版本 |
| F-021 | sherpa-onnx 分别列出 streaming 与 non-streaming 模型；online 结果结构有 token 与秒级时间信息。 | S19，README 与接口 | provider 取决于构建；token 时间点不等于精确词区间 |
| F-022 | 多个工具提供 speaker diarization 或说话人标签能力。 | S15、S18、S19，官方能力描述 | 本包只把结果作为录音内标签，不作为实名认证 |
| F-023 | Buzz 文档支持文件和麦克风转录及 TXT/SRT/VTT 导出，并区分本地模型与 API 选项；系统音频需要适当回环源。 | S20，README 与使用文档 | 未在本机验证 GUI 或音频设备 |
| F-024 | 所查项目的代码许可存在 MIT、Apache-2.0、BSD、GPL 等差异；FunASR 单列 MODEL_LICENSE。 | S08–S20，README 与许可材料 | 代码、模型、依赖、媒体权利必须分别确认 |
| F-025 | 库内 VidBee 包在 2026-10-10 记录本地识别与云 AI 的不同数据流，并声明未做抓包、安全审计。 | S23，历史库内材料 | 本次没有重新核验产品当前版本 |
| F-026 | Ollama 结构化输出文档允许 format 接收 JSON Schema，并展示 Pydantic 校验；该页当前注明云端不支持。 | S21，官方文档 | 文档时点限定；没有运行本地模型 |
| F-027 | OWASP 将外部文档和工具输出列入提示词注入边界，建议最小权限及模型之外的权限和参数校验。 | S22，安全指南 | 提示词中的“不执行”不是系统隔离 |
| F-028 | 本包引用检查夹具中，合法 ID、修订和逐字引文可通过程序，而与原话相反的结论也可通过。 | [引用检查示例](../examples/agent-evidence-check.md)，纯 Python 测试 | 这是合成单元测试，不是直播研究数据；说明语义支持度不在该函数的检查范围 |

## 研究与设计分界

JSONL 字段、工作目录、Agent 分工、短块定稿与只读查询接口是本包提出的工程设计，不冒充上游统一标准。代码示例没有直播采集器、持续运行守护、模型训练或完整安全边界；具体实测范围见[验证记录](verification.md)。
