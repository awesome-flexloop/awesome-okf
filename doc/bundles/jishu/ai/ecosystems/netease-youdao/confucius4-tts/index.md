---
type: bundle
title: Confucius4-TTS 基于 LLM 的高保真语音合成
okf_version: "0.2"
---

# Confucius4-TTS 知识库

本知识包是网易有道开源的零样本（zero-shot）高保真语音合成系统 [Confucius4-TTS](https://github.com/netease-youdao/Confucius4-TTS)（Apache-2.0 许可证）的系统化中文源码教程，基于 `vendor/netease-youdao/Confucius4-TTS/` 目录的信源基线 commit `4fb32c481302d8858c3aec6a1c2a8b4cea8894c0` 深度阅读生成。系统采用 LLM 自回归预测离散语义 token（T2S 段，vocab 8194）+ flow matching 一次性扩散生成 80 维 mel（S2A 段，ConditionalCFM + 13 层 DiT 估计器）+ BigVGAN 声码器还原波形的级联架构，支持 14 种语言的音色克隆朗读。所有内容均溯源至信源仓库 Python 源码与 YAML 配置，遵循 OKF v0.2 规范，经 R→I→E→V→C 五阶段链路生成。

> **命名注意**：Python 包目录实际拼写为 `confuciustts`（三个 t），setup.py 的 name 为 `"confuciustts"`、version 为 `"0.1.0"`，部分文档写作 `confuciusts`，一律以磁盘源码为准。

## 概念篇（concepts/）

* [仓库全景与推理链路总览](concepts/00-overview.md) — 14 语言支持、安装依赖约束、三段级联推理链路（T2S → S2A → BigVGAN）、`ConfuciusTTS.generate` 参数四组全貌与四条使用路径。
* [条件化机制：prompt 掩码、说话人与风格嵌入](concepts/01-conditioning.md) — S2A 训练期 prompt 0–30% 随机掩码、prompt_cond 可学习参数、Qwen3-TTS 说话人编码器与 CAMPPlus 风格编码器、训练-推理 CFG 不对称。
* [长度调节与时长启发式](concepts/02-length-regulation.md) — `int(T*1.72)` 目标帧数启发式、InterpolateRegulator nearest 上采样（只重采样不预测长度）、cross_fade/edge_fade 段间拼接、80 token 文本分段。
* [声学生成：flow matching 与 DiT 估计器](concepts/03-flow-matching.md) — ConditionalCFM 的 L1 损失/训练 CFG 丢弃率 0.2/25 步欧拉采样、DiT（depth=13）+ WaveNet 末层的速度场估计器结构。
* [声码器与 BigVGAN 集成](concepts/04-bigvgan-vocoder.md) — Snake 激活、ConvTranspose 上采样、AMP 抗混叠 resblock，`nvidia/bigvgan_v2_22khz_80band_256x` 的加载方式与替换边界。
* [vLLM 加速路径与服务化](concepts/05-vllm-serving.md) — HF/vLLM 双后端分治（两套实现而非透明切换）、patch_vllm 自定义架构注册、`generate_stream` 流式切块、FastAPI server.py 与 Gradio webui.py 服务化形态。
* [两阶段训练与微调体系](concepts/06-training.md) — 先 T2S 后 S2A 的训练顺序、S2A 冻结四处模块策略、EMA 稳定器、TSV 五列微调数据格式、w2v-bert 2.0 第 17 层条件提取。

## 实战示例（examples/）

* [单次推理全流程（HF 后端）](examples/single-inference.md) — 基于 `ConfuciusTTS` 的最小完整零样本合成：构造、generate 四组参数解读、raw 模式分段结果与常见调参起点。
* [服务化启动与请求（server.py / webui.py）](examples/serving.md) — FastAPI 服务启动与 `/health`、`/api/tts`、`/api/tts/stream` 调用（含流式 PCM 客户端）、Gradio WebUI 启动与双后端选型速查。
* [两阶段训练配置解读](examples/two-stage-training.md) — 逐步执行 train_t2s/train_s2a 两阶段训练、配置关键段解读、冻结策略的 DDP 后果与微调 TSV 五列数据格式。

## 信源与事实层（references/）

* [Confucius4-TTS 源码事实清单](references/facts.md) — 64 条源码事实 F-c4t-001~064（R 阶段登记、V 阶段核验），每条含证据位置映射。
* [Confucius4-TTS 核心洞察与知识地图](references/insights.md) — 5 条核心洞察四元组（陈述/证据/反常识/行动），覆盖级联架构、prompt 掩码、时长启发式、双后端、两阶段训练不对称。
* [Confucius4-TTS 信源登记](references/sources.md) — 上游仓库、固定基线 commit、Apache-2.0 许可证与 30 余个关键信源文件的核验内容清单。

## 信任与生命周期说明

* **status 判定依据**：全部 10 个内容文档（7 个概念 + 3 个示例）均 `status: stable`，3 个 references 文档（facts/insights/sources）均 `status: verified`。内容基于对 Confucius4-TTS 信源仓库（README、setup.py、requirements、双推理后端、两训练入口、llm/flow/frontend/external 模块与三份 YAML 配置）的逐文件阅读与事实提取（64 条源码事实 F-c4t-001~064），经 R→I→E→V→C 五阶段链路生成。
* **stale_after 解释**：内容文档统一设置为 `2027-09-09`。该系统为版本 0.1.0 的新开源项目，T2S/S2A/声码器的级联架构与配置契约（语义 token + mel 段间契约）在可见代码中自洽稳定，但该日期作为针对上游后续版本（如配置键增删、vLLM 适配层兼容性变更）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 source-reading 对抗验证事件（接口签名/配置键/调用链逐一比对源码），两者分离、可追溯；上游变更以 [log.md](log.md) 记录。

本知识包共收录 10 个内容文档（7 个概念 + 3 个示例），另含 3 个 references 文档（事实/洞察/信源）、3 个子目录 index.md、根 index.md 与 log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
