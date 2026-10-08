---
type: bundle
title: EmotiVoice 多音色情感控制语音合成
okf_version: "0.2"
---

# EmotiVoice 知识库

本知识包是网易有道开源的多音色、富情感文本转语音（TTS）系统 [EmotiVoice](https://github.com/netease-youdao/EmotiVoice)（Apache-2.0 许可证）的系统化中文源码教程，基于源码（`vendor/netease-youdao/EmotiVoice/`，双基线 tag v0.3 + pin commit `59f0f36de4db12825f4705dd4e0780d79dd6bb01`，`git describe` 输出 v0.3-17-g59f0f36）深度阅读生成。系统经由「文本前端 g2p → 符号表/文本清洗 → PromptTTS 风格条件注入 → JETS 声学模型与 HiFiGAN 声码器联合推理 → 服务化 API」五阶段链路（R→I→E→V→C）产出最终语音，覆盖中英混读前端、风格提示情感控制、JETS 联合训练、MFA 数据对齐与 OpenAI 兼容服务化的完整知识体系，全部内容溯源至 EmotiVoice Python 源码与配置。

## 核心概念篇（concepts/）

* [EmotiVoice 整体架构与推理入口](concepts/00-architecture.md) — 联合推理主入口 inference_am_vocoder_joint.py、测试文本四段格式（speaker|prompt|phoneme|content）、「文本前端 → PromptTTS 声学模型 → HiFiGAN 声码器」三段式数据通路、批量推理入口 inference_tts.py。
* [中英混合前端与 g2p 管线](concepts/01-g2p-pipeline.md) — frontend.py 的 g2p_cn_en 单管线五步处理：数字归一化、中文 jieba+pypinyin 与英文 lexicon+g2p_en 分工、eng_cn_sp/cn_eng_sp 跨界标记、sos/eos 包裹。
* [符号表与文本清洗](concepts/02-symbols-text-cleaning.md) — text/symbols.py 符号拼接顺序、84 个 ARPAbet 符号、18 条缩写展开与数字规范化规则，token 世界边界与序列化机制。
* [PromptTTS 风格条件注入](concepts/03-style-conditioning.md) — StyleEncoder「多任务头训练、单嵌入推理」非对称机制：simbert 底座、4 个分类头（pitch/speed/energy/emotion）、768→128 维投影、7 类情绪标签体系。
* [JETS 联合训练与 HiFiGAN 声码器](concepts/04-jets-joint-training.md) — JETSGenerator 把声学模型与声码器内嵌为单一模块、mel 重建损失主导（dec_mel_loss×45）的损失组合、DDP 训练循环与 g_/do_ checkpoint 组织。
* [标签体系、数据集与 MFA 对齐流水线](concepts/05-labels-dataset-mfa.md) — data/youdao/text 标签文件（speaker2 2014 行、tokenlist 502 行等）、mfa/ 八步数据制备与对齐脚本、sp 标记家族贯穿前端与数据的隐形契约。
* [服务化部署：OpenAI 兼容 API 与 Streamlit Demo](concepts/06-serving-api.md) — openaiapi.py 的 FastAPI 薄封装、SpeechRequest 字段、speed 波形级后处理真相、demo_page.py 交互形态与两套分离的依赖清单。

## 实战示例（examples/）

* [联合推理完整流程示例](examples/joint-inference-workflow.md) — 基于 inference_am_vocoder_joint.py 演练完整 TTS 推理：准备四段式测试文件、执行推理命令、拆解内部装配与生成调用、定位输出音频。
* [中英混读文本处理示例](examples/mixed-lingual-g2p.md) — 基于 frontend.py 演练中英混合文本音素化：数字转中文、双前端分工、跨界标记插入与 sos/eos 包裹，覆盖命令行与 Python 调用两种形态。
* [OpenAI 兼容 API 调用示例](examples/openai-compatible-api.md) — 基于 openaiapi.py 演练服务启动与调用：curl 与 Python 客户端两种形态、SpeechRequest 字段语义、speed 后处理注意事项与依赖分装。

## 信源登记簿（references/）

* [EmotiVoice 源码事实清单（v0.3 @ 59f0f36）](references/facts.md) — F-ev-001~042 共 42 条源码事实，逐条登记 README、推理入口、前端、text/ 包、HiFiGAN 与 PromptTTS 修改版模型等 20 余个源文件的实测结论。
* [EmotiVoice 架构洞察与知识地图（v0.3 @ 59f0f36）](references/insights.md) — 基于 42 条事实提炼的核心架构洞察（风格控制非对称路径、中英混读跨界标记等），全部给出事实证据编号并可回溯源码位置。
* [EmotiVoice 信源登记（v0.3 @ 59f0f36）](references/sources.md) — 上游仓库 URL、本地 vendor 子模块路径、tag v0.3 与 pin commit 基线说明、基线核验方式、Apache-2.0 许可证登记。

## 信任与生命周期说明

* **文档总数构成**：本知识包共收录 13 个内容文档（7 个概念 + 3 个示例 + 3 个信源登记），另含 3 个子目录 index.md、根 index.md 与 log.md，合计 18 个文件。
* **status 判定依据**：全部 13 个内容文档均 `status: stable`。内容基于对 EmotiVoice 源码（推理入口、前端、text/ 包、models/ 模型栈、mfa/ 数据流水线、openaiapi.py 等）的逐文件阅读与事实提取（42 条源码事实 F-ev-001~042），经 R→I→E→V→C 五阶段流程生成，并经 `process:facts-cross-check` 事实交叉核验（`generated.at` 与 `verified.at` 分离记录于各文档 frontmatter，均为 2026-09-09）。
* **stale_after 解释**：全部内容文档统一设置为 `2027-09-09`（生成后一年）。EmotiVoice 自 2023 年底开源后架构（PromptTTS + HiFiGAN 三段式、g2p_cn_en 前端、StyleEncoder 风格注入）保持稳定，上游更新频率低；该日期作为针对未来上游重大变更（如前端管线或风格机制重构）的保守重新评估节点。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
