---
type: Reference
title: RTX Spark 信源与事实登记
description: 清理追踪参数后的官方文章及补充信源，逐条登记发布、架构、软件与性能声明
tags: [NVIDIA, RTX Spark, 事实登记, 信源]
source: https://blogs.nvidia.cn/blog/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/
generated: {by: "reference_agent/okf-wiki", at: "2026-10-27"}
status: stable
stale_after: 2026-12-31
sources:
  - id: cn
    resource: https://blogs.nvidia.cn/blog/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/
  - id: en
    resource: https://nvidianews.nvidia.com/news/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/
  - id: specs
    resource: https://www.nvidia.com/en-us/products/rtx-spark/
  - id: dev
    resource: https://developer.nvidia.com/blog/code-test-and-deploy-on-one-machine-with-nvidia-rtx-spark
  - id: ms
    resource: https://devblogs.microsoft.com/foundry-on-windows/build-on-winml-oct-7-26/
  - id: surface
    resource: https://www.microsoft.com/en-us/surface/devices/surface-laptop-ultra
  - id: adobe
    resource: https://news.adobe.com/news/2026/10/adobe-and-nvidia-expand-collaboration-to-speed-agentic-creation
  - id: history
    resource: https://blogs.windows.com/windowsdeveloper/2025/04/23/pytorch-arm-native-builds-now-available-for-windows/
  - id: pair
    resource: https://www.nvidia.com/en-us/ai-on-rtx/personal-ai-router/
---

# RTX Spark 信源与事实登记

## 信源距离

原文是 NVIDIA 官方发布兼厂商推广，公开、无访问控制。原链接的邮件活动及用户追踪参数不参与访问，已删除。中文稿和英文稿属于同一发布主体，不能计为两个独立验证源；微软与 Adobe 是合作厂商，能核对各自产品声明，不能替代第三方性能测量。

这里的“事实”包括“厂商确实发布了某项声明”，不等于该声明已由独立实验验证。性能、续航、兼容比例与市场规模均按这一原则归因。2026-10-27 为本包资料读取日，不代表所有页面都在当天更新。

| ID | 来源与用途 | 证据边界 |
|---|---|---|
| cn | [中文上市稿](https://blogs.nvidia.cn/blog/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/) | 页头2026-10-15、正文电头2026-10-16；中国价格与中文机型名称、创作应用与游戏名单 |
| en | [英文上市稿](https://nvidianews.nvidia.com/news/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/) | 全球品牌、美元价格、英文机型；同主体交叉对照 |
| specs | [产品规格页](https://www.nvidia.com/en-us/products/rtx-spark/) | 笔记本与桌面规格、TDP、媒体引擎；动态页面 |
| dev | [开发栈技术文章](https://developer.nvidia.com/blog/code-test-and-deploy-on-one-machine-with-nvidia-rtx-spark) | 框架、量化、移植路径；性能倍数为 NVIDIA 自测 |
| ms | [微软开发公告](https://devblogs.microsoft.com/foundry-on-windows/build-on-winml-oct-7-26/) | Windows Arm64 CPU/CUDA 包、Windows ML 实验状态 |
| surface | [Surface 产品页](https://www.microsoft.com/en-us/surface/devices/surface-laptop-ultra) | OEM 产品存在性、算力及内存脚注、续航测试条件 |
| adobe | [Adobe 合作公告](https://news.adobe.com/news/2026/10/adobe-and-nvidia-expand-collaboration-to-speed-agentic-creation) | 创作应用优化；合作方自述，非独立评测 |
| history | [2025 年 PyTorch Arm 公告](https://blogs.windows.com/windowsdeveloper/2025/04/23/pytorch-arm-native-builds-now-available-for-windows/) | “首个”的历史范围，CPU 路径已有先例 |
| pair | [PAIR 产品页](https://www.nvidia.com/en-us/ai-on-rtx/personal-ai-router/) | 多设备本地推理定位；未读取完整安装和网络安全规范 |

## 发布与硬件

| 编号 | 可归因声明 | 来源 | 核验分类 |
|---|---|---|---|
| F-001 | 中文稿页头日期为2026-10-15，正文电头为2026-10-16并宣布上市 | cn | 页面日期与上市电头分开，不猜时区原因 |
| F-002 | 中文稿列华硕、戴尔、联想、微软、微星五个首发品牌 | cn | 中国发布口径 |
| F-003 | 英文稿另列 HP，共六个品牌 | en | 全球发布口径 |
| F-004 | 中文稿给出人民币 18,999 元起，价格与配置因地区而异 | cn | 价格单源及时点 |
| F-005 | 英文稿给出 2,599 美元起；Surface 页面列 2,599.99 美元 | en、surface | 不同报价口径 |
| F-006 | RTX Spark 超级芯片组合 Blackwell RTX GPU 和 Grace CPU，MediaTek 参与定制 CPU 设计 | cn、en | NVIDIA 官方架构声明 |
| F-007 | 官方上限为 128 GB 统一内存和 1 Petaflop FP4 AI 性能 | cn、en、specs、surface | 规格声明；非实测 |
| F-008 | 高配笔记本 N1X 为 6,144 GPU 核心、20 CPU 核心，最高 128 GB LPDDR5X | specs | 官方规格 |
| F-009 | 另一笔记本 N1X 配置为 5,120 GPU 核心、18 CPU 核心，最高 64 GB LPDDR5X | specs | 官方规格 |
| F-010 | 产品页两种笔记本超级芯片 TDP 均列 45–80 W | specs | 芯片范围，非整机功率 |
| F-011 | 桌面 N1X 列 6,144 GPU 核心、20 CPU 核心、最高 128 GB，TDP 140 W | specs | 桌面规格 |
| F-012 | 产品页操作系统支持列 Windows 11；开发稿称紧凑桌面将于 11 月到来 | specs、dev | 支持与未来计划分开 |
| F-013 | Surface 脚注称算力基于启用稀疏性的理论 FP4 TOPS | surface | 峰值限定 |
| F-014 | Surface 脚注称内存为 CPU/GPU 共享系统内存，GPU 可寻址最大值小于总量且随配置、负载变化 | surface | 内存限定 |
| F-015 | 产品页列第四代光追核心、第五代 Tensor Core、DLSS 5 和 Reflex 2 | specs | 平台技术支持 |
| F-016 | 产品页列一个第九代编码器、一个第六代解码器；正文列 HEVC/H.264/AV1 硬件编码解码 | specs | 不等于每种格式组合均支持 |
| F-017 | 产品页接口脚注要求向 OEM 核对具体 PCIe、HDMI 与 DisplayPort 能力 | specs | 芯片能力与整机接线边界 |
| F-018 | 中文稿称纤薄设计、全天续航；Surface 续航脚注采用视频播放或网页浏览、150 nits 与预生产设备条件 | cn、surface | 续航自述，非 AI 持续负载 |

## 本地智能体

| 编号 | 可归因声明 | 来源 | 核验分类 |
|---|---|---|---|
| F-019 | 发布稿列引导设置和安装器，支持入门 Copilot、Hermes、OpenClaw、Perplexity、Pi、WorkBuddy | cn、en | 支持清单，非全部离线保证 |
| F-020 | Nous Research 在发布稿中说明 Hermes 可在 Windows 笔记本本地使用开放模型与智能体 | cn、en | 发布稿内合作方引语，非独立证据 |
| F-021 | 发布稿称 Nemotron 3.5 Bolt 74B-A9B 24GB 有 740 亿参数，针对工具调用和多步任务优化 | cn、en | 官方模型定位 |
| F-022 | 开发稿将该模型描述为 74B 总参数、9B 活跃参数 MoE，2-bit 量化压入 24 GB | dev | 技术补充；非总运行内存 |
| F-023 | 开发稿列 llama.cpp、vLLM、Ollama、Unsloth、LM Studio 与 Hermes/OpenClaw 接入 | dev | NVIDIA 框架支持声明 |
| F-024 | 发布稿列 OpenShell Secure Runtime 和 Microsoft Execution Containers 作为权限控制工具 | cn、en | 能力定位，未实测沙箱 |
| F-025 | NVIDIA Skills 可让兼容智能体调用 Broadcast、RTX Remix 与 Omniverse 库；例子是直播效果调整和批量处理录制片段 | cn、en | 兼容集成声明 |
| F-026 | PAIR 可让 RTX Spark 向家庭网络内兼容 Windows/Linux/macOS 电脑提供推理 | cn、en、pair | 服务拓扑，非所有客户端保证 |
| F-027 | PAIR 页面同时列 DGX Spark、RTX Spark、Windows/Linux RTX 系统与 macOS 电脑 | pair | 名称与产品区分 |
| F-028 | 开发稿描述本地/云端混合提示路由，本地不适合时可升级至云端 | dev | 本地优先不等于离线 |

## 创作与媒体

| 编号 | 可归因声明 | 来源 | 核验分类 |
|---|---|---|---|
| F-029 | 中文稿称可离电编辑 8K 4:2:2 视频及渲染高达 90 GB 的 3D 场景 | cn | 厂商能力声明 |
| F-030 | 中文、英文摘要称场景“超过 90 GB”/“90GB+”，正文及产品页写“高达 90 GB” | cn、en、specs | 原文内部口径差异 |
| F-031 | Photoshop 与 Premiere 在上市时通过 beta 提供原生支持；Substance 支持随后推出 | cn、en | 首发状态，不推定今日 GA |
| F-032 | NVIDIA 发布稿列 TensorRT 加速 AI 编辑及 Premiere 回放、渲染、特效、调色 | cn、en | 官方能力声明 |
| F-033 | Adobe 2026-10-15 公告确认 Photoshop、Premiere、Substance 3D 的 RTX Spark 优化合作 | adobe | 合作方确认，非全部首发 GA |
| F-034 | Adobe 列 Photoshop GPU 合成/Remove Tool/模糊及光效、Premiere Enhance Speech/Object Mask、Substance 3D Painter 纹理处理 | adobe | 应用内具体优化 |
| F-035 | Adobe 宣称相关 AI 处理、编辑、颜色与特效最高 2 倍加速 | adobe | 自述，未独立测量 |
| F-036 | 中文稿另列剪映专业版、哔哩哔哩直播姬、D5 Lite；万兴喵影支持计划为“本月底” | cn | 中国单源；本月底指 2026-10 |
| F-037 | 发布稿列 Broadcast 2.3，可去除已有录音背景噪声并调整 Studio Voice 声音效果 | cn、en | 版本能力声明 |
| F-038 | 发布稿列 beta RTX Video 最高 4K 超分辨率与 4 倍多帧生成 | cn、en | beta 和上限 |
| F-039 | 发布稿称 ComfyUI 新 RTX Video 节点可将 15 FPS 转为 60 FPS 并转 HDR，无按次云推理费 | cn、en | 厂商演示能力及收费范围 |

## 开发栈

| 编号 | 可归因声明 | 来源 | 核验分类 |
|---|---|---|---|
| F-040 | 发布稿称原生 CUDA 支持本地模型/智能体，部署目标涵盖超过 1.5 亿台 RTX AI PC 与云 NVIDIA GPU | cn、en | 能力与装机量分开；规模自述 |
| F-041 | Windows Developer Config 简化环境，WSL 提供 Linux 开发工具 | cn、en、dev | 开发路线，非全部环境一致 |
| F-042 | 发布稿链接 NVIDIA/skills 开源仓库，定位为教智能体使用 CUDA-X 工具和库 | cn、en、dev | 官方仓库定位，未源码精读 |
| F-043 | 发布稿称“首个 Windows on Arm PyTorch-CUDA build” | cn、en | CUDA 范围内的首个声明 |
| F-044 | 微软 2025-04-23 公告已有 PyTorch 2.7 Windows Arm64 原生构建，针对 Python 3.12；示例使用 CPU | history | 历史边界核对 |
| F-045 | 微软新公告区分 PyTorch 原生 Windows Arm64 CPU 构建与 NVIDIA 发布的 CUDA-enabled Arm64 包 | ms | 另一主体确认开发路径 |
| F-046 | NVIDIA 开发稿提 Python 3.15 native by default、超过 2,000 个 Conda 包 | dev | 厂商口径，无全量包审计 |
| F-047 | 发布稿称前 15,000 个 Python 包支持率 97%；开发稿写超过 97% 的 Arm 兼容版本 | cn、en、dev | 精确与超过口径不同，未实测全集 |
| F-048 | 微软公告安装示例使用 Python 3.14-arm64、torch 2.14.0+cu134、torchvision 0.29.0+cu134 与 triton-windows 3.8.0.post29 | ms | 示例组合；本包不复现实装 |
| F-049 | 微软称 Windows ML 的 llama.cpp/GGUF 与新 Runtime API 为 experimental/preview，列版本2.7.2021-experimental；ONNX Runtime 路径继续支持 | ms | 实验状态及版本，不推定今日GA |
| F-050 | 微软 Text Generation API 提供 ONNX/GGUF 路径和 OpenAI-compatible 本地端点，Speech Recognition API 使用 ONNX Whisper | ms | API 范围，非所有服务兼容 |
| F-051 | NVIDIA 开发稿建议先审计 Windows Arm 依赖，再选 Arm64 或 Arm64EC 渐进移植并测试安装、功能、性能、CUDA 路径 | dev | 官方移植建议 |
| F-052 | 开发稿自测编码智能体 4.6x、微调 2.7x、编译 1.8x，对照 Intel Core Ultra X9 388H；列 AA-AgentPerf-local/Qwen3.8-27B、Unsloth LoRA/Llama-3.1-8B、Linux 内核编译测试 | dev | 不同工作负载，非普遍倍率 |

## 游戏与地区口径

| 编号 | 可归因声明 | 来源 | 核验分类 |
|---|---|---|---|
| F-053 | 发布稿摘要称 3A 游戏可在 1440p 超过 100 FPS，正文称上市即支持数百游戏 | cn、en | 厂商摘要，无完整配置与测试集 |
| F-054 | 中文首发名单含明日方舟终末地、赛博朋克2077、原神、战争机器事变日、堡垒之夜、漫威争锋、异环、永劫无间、NBA 2K27、燕云十六声、鸣潮 | cn | 中文列举，非完整兼容矩阵 |
| F-055 | 英文名单含 Cyberpunk 2077、Fortnite、Gears of War E-Day、Marvel Rivals、World of Warcraft、NBA 2K27 | en | 全球稿列举，非中文遗漏勘误 |
| F-056 | 发布稿称 NBA 2K27 用 DLSS 5 的 3D 引导神经渲染增强光照与材质 | cn、en | 官方游戏集成声明 |
| F-057 | 发布稿称新 AI 模型运行速度 2 倍，可将 DLSS 5 帧率最高提升到 1.4 倍 | cn、en | 两个不同指标，非游戏帧率翻倍 |
| F-058 | Visual Concepts 制作人引语描述与 NVIDIA 的 NBA 2K27 合作 | cn、en | 发布稿内引语，未独立回源至 2K |
| F-059 | 中文机型名单为 ProArt 创16/创14 RTX Spark、XPS 16、YOGA Pro 15 RTX Spark、Surface Laptop Ultra、尊爵 N16 Flip AI+ 2026 | cn | 中国发布命名 |
| F-060 | 英文名单为 ProArt P14/P16、XPS 16、OmniBook Ultra/OmniBook X 14、Yoga Pro 9n、Surface Laptop Ultra、Prestige N16 Flip AI+/Prestige N16 | en | 全球发布命名，不强建型号映射 |
| F-061 | 微软 Surface 页面确认 RTX Spark 产品，并提醒功能与应用供应因地区而异、游戏性能随游戏资源及配置变化 | surface | OEM 产品确认与性能边界 |

## 审查补登的宣传上限

| 编号 | 可归因声明 | 来源 | 核验分类 |
|---|---|---|---|
| F-062 | 中文稿称相较“当前最常见的 Windows SoC”，游戏性能至高9倍 | cn | 厂商自述；基线型号及完整测试条件不明 |
| F-063 | 同一中文稿称AI图像生成速度至高11倍，沿用上述Windows SoC对照 | cn | 厂商自述；模型、输入及测试配置不明 |
| F-064 | 中文稿称可运行高达1,250亿参数的智能体；NVIDIA产品页写“120B parameters with 1M context”，Surface页写最高120B | cn、specs、surface | 125B与120B口径差异；模型、量化与运行条件不足，不能归并或断言容量实测通过 |

### 关键证据摘录与复核定位

以下为2026-10-27回读的短摘录，不是全文快照；动态页面后续变化须追加读取日与差异记录。

| 来源位置 | 短摘录 | 对应事实 |
|---|---|---|
| 中文稿页头／正文电头 | “2026年10月15日”／“2026年10月16日” | F-001 |
| 中文稿性能段 | “游戏性能至高可达它的 9 倍”“AI 图像生成速度至高可达它的 11 倍” | F-062~F-063 |
| 中文稿智能体段／产品页AI能力段 | “1,250亿参数”／“120B parameters with 1M context” | F-064 |
| 微软Windows ML版本说明 | “2.7.2021-experimental” | F-049 |

历史新闻起价与动态Surface报价仅代表相应读取时点；没有归档页面或完整测试报告时，不宣称能重放原始环境。

## 阅读约定

F-001 至 F-064 连续，共64条已登记事实；该数量不构成源文永无遗漏的保证。多行同源是为了让具体声明可以独立引用，不代表64次独立证实。概念页中的数学演算与方法建议均标“教学推导”或“本包建议”，不扩充为官方事实。不得从“支持安装”“支持框架”“支持游戏”推导“无需网络”“所有插件原生”“全部游戏通过反作弊”。
