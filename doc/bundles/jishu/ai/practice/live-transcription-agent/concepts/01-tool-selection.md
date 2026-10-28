---
type: Guide
title: 现成工具与自建边界
sources:
  - {id: sources, resource: ../references/source-manifest.md}
  - {id: facts, resource: ../references/facts.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 现成工具与自建边界

先按输入来源和所需延迟选路线，再选识别模型。以下功能来自截至 2026-10-28 的官方资料和源码快照，不是逐平台实测排名；支持列表会变化，安装前重新核对。[证据来源](../references/source-manifest.md)

## 采集层候选

| 工具 | 适合什么 | 主要限制 |
|---|---|---|
| 平台原生导出 | 自有直播、平台提供的合法回放与字幕 | 仅导出权限允许的内容；字幕也需核对 |
| OBS Studio | 没有稳定提取器，但允许录制正在播放的应用 | 录到的是本机实际播放内容；系统与 OBS 版本影响音频来源 |
| Streamlink | 插件支持的直播页面 → 原始流 | 不是全平台下载器；可取得的历史受直播窗口限制 |
| yt-dlp | 回放获取与部分直播 | 直播从头功能有限且实验性；站点列出不等于当前可用 |
| FFmpeg | 已知、已授权的媒体直链，转封装与分段 | 不负责自动解析任意直播间网页；重连不补丢失历史 |
| Bililive-go | 国内多平台值守录制 | 平台插件和分段下载路径各有边界 |
| DouyinLiveRecorder | 直播间列表监控与 FFmpeg 录制 | 部分平台需要合法登录态；不能承诺无凭据录制 |
| StreamCap | 希望桌面或 Web 管理录播 | 部分地址一次性、部分下载路径不分段 |

事实与限制对应 F-001—F-012。国内工具属于第三方项目，不代表直播平台官方授权。不要复制仓库示例中的 Cookie，不应安装来历不明的再打包程序。

## 本地转录与实时层候选

| 工具 | 输入与定位 | 适合优先试用的情况 |
|---|---|---|
| Whisper | 完整媒体文件，内部滑动窗口识别 | 希望以原始实现为参考，容忍离线处理 |
| faster-whisper | CTranslate2 文件识别，CPU/int8 或 NVIDIA | 想用 Python 导出可自定义的片段 JSONL |
| whisper.cpp | 原生推理与 CLI，多硬件后端 | CPU、Apple Silicon 或 Intel 路径更重要 |
| WhisperLive | WebSocket 音频缓冲与近实时解码 | 需要字幕服务和客户端接入 |
| WhisperLiveKit | 后端加流式策略、Web 服务 | 需要对齐、定稿及说话人处理的集成体验 |
| FunASR | 多种离线和专用流式模型 | 中文优先，愿意按模型类型配置 |
| SenseVoiceSmall | 中粤英日韩识别及音频标签 | 短音频或 VAD 分段任务，不因速度快就视为原生流式 |
| sherpa-onnx | 在线/离线识别器与多平台推理 | 需要端侧部署、原生流式或明确的 ONNX 后端 |
| Buzz | 文件/麦克风图形转录及字幕导出 | 不想编写转录脚本；系统声音仍需正确路由 |
| VidBee | 视频获取、本地转录、AI 文本处理 | 侧重回放与内容整理；参阅库内既有教程 |

见 F-013—F-025。WhisperLive/WhisperLiveKit 不等于某个基础模型；选框架后仍需选择模型、后端和协议。VidBee 信息来自 2026-10-10 的既有知识包，本次不把它记为重新核验的软件实测。

## 四条起步路线

**Windows、不写代码**：OBS 指定应用音频录制 → Buzz 或 VidBee 选择本地模型 → 导出字幕/文本 → 检查时间戳 → 仅在批准的数据边界内交给 Agent。图形工具导出的格式不一定满足本包 JSONL 契约，需要手工或适配器归一化。

**开发者、先保证可复查**：Streamlink/OBS 保存原媒体 → faster-whisper 离线生成 JSONL → 只读 Agent 拆解 → 程序验证引用 → 人工回听关键结论。这是本包推荐的第一版；推荐依据是层间解耦和可重跑，不是性能胜出证明。

**中文、必须低延迟**：采集为固定格式 PCM → FunASR 流式 Paraformer 或 sherpa-onnx 在线模型 → 中间/最终结果分开 → 仅最终结果进入持久分析。需要独立验证端到端延迟与中文错误率。

**Apple/Intel、本地硬件优先**：先看 whisper.cpp 的 Metal/Core ML/OpenVINO 路径，或对应可用的 WhisperLiveKit/sherpa-onnx 后端。OpenVINO 在 whisper.cpp 文档中是 encoder 加速；不要把设备名字理解为全模型无条件加速。

## 何时不自建

仅需偶尔整理一场直播，现成录制与字幕导出通常足够。先完成一次真实小样，核实音轨、字幕、引用与隐私，再决定是否加入值守、数据库或 MCP。

自建前，以同场直播样本的平台原生字幕/导出或现成 GUI 流程为比较基线，按相同质量要求计入设备、算力、存储、维护与人工校对成本。净省时目标和预算由操作者自定；实测未达目标或超预算就不扩建，未测不声称收益。

需要长期多场直播、跨文件引用、可恢复消费、审计轨迹时，自建范围可限定为适配层：会话登记、任务队列、归一化、修订管理、证据校验、只读检索。不要重写 FFmpeg、ASR 引擎或各直播平台解析器。

## 许可证按组件核对

| 组件 | 本次读到的许可口径 | 仍需另查 |
|---|---|---|
| OBS | GPL-2.0+ | 插件、再分发与打包义务 |
| FFmpeg | 主体 LGPL-2.1+，启用 GPL 组件会改变许可 | 实际构建选项、二进制来源、编解码许可 |
| Streamlink | BSD-2-Clause | 附加依赖 |
| yt-dlp | 源码 Unlicense，PyInstaller 整包另有 GPLv3+ 口径 | 使用的发行形态 |
| Bililive-go / DouyinLiveRecorder / StreamCap | GPL-3.0 / MIT / Apache-2.0 | 实际版本、依赖、直播内容权利 |
| Whisper | 官方代码与权重均 MIT | 非官方转换、微调模型的许可 |
| faster-whisper / whisper.cpp / WhisperLive / Buzz | 代码 MIT | 配套模型、插件与依赖 |
| WhisperLiveKit / sherpa-onnx | 代码 Apache-2.0 | 选用模型与后端 |
| FunASR / SenseVoice | 当前代码 MIT，模型许可另列 | 模型卡、MODEL_LICENSE 与商用范围 |
| VidBee | 本次未核验许可证，不能据此作商用推荐 | 实际版本、模型权重、依赖与许可义务 |

许可证表是上游静态阅读摘要，不是法律意见；“工具开源”不会授予直播音视频和人物声音的权利。最终选中的组合须核对实际版本、模型权重、依赖及使用与分发义务。[来源与版本锚点](../references/source-manifest.md)
