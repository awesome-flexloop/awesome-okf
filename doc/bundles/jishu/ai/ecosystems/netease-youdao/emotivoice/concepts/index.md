# 概念文档

EmotiVoice 核心架构概念，共 7 篇，按数据通路依赖顺序组织：从推理入口建立整体认知，依次深入文本前端、token 基础设施、风格条件注入、联合训练结构、数据流水线与服务化部署。

* [00 EmotiVoice 整体架构与推理入口](00-architecture.md) — inference_am_vocoder_joint.py 主入口、测试文本四段格式、文本前端→PromptTTS→HiFiGAN 三段式数据通路、批量推理入口。
* [01 中英混合前端与 g2p 管线](01-g2p-pipeline.md) — g2p_cn_en 单管线五步处理：数字归一化、中文 jieba+pypinyin 与英文 lexicon+g2p_en 分工、跨界标记、sos/eos 包裹。
* [02 符号表与文本清洗](02-symbols-text-cleaning.md) — symbols.py 符号拼接顺序、84 个 ARPAbet 符号、18 条缩写展开、数字规范化与序列化机制。
* [03 PromptTTS 风格条件注入](03-style-conditioning.md) — StyleEncoder「多任务头训练、单嵌入推理」：simbert 底座、4 个分类头、768→128 投影、情绪/韵律标签体系。
* [04 JETS 联合训练与 HiFiGAN 声码器](04-jets-joint-training.md) — JETSGenerator 声学模型与声码器内嵌、mel 重建损失主导（dec_mel_loss×45）、DDP 训练循环与 checkpoint 组织。
* [05 标签体系、数据集与 MFA 对齐流水线](05-labels-dataset-mfa.md) — data/youdao/text 标签文件、mfa/ 八步数据制备与对齐脚本、sp 标记家族的隐形契约。
* [06 服务化部署：OpenAI 兼容 API 与 Streamlit Demo](06-serving-api.md) — openaiapi.py FastAPI 薄封装、SpeechRequest 字段、speed 波形级后处理、demo_page.py 与两套依赖清单。

```{toctree}
:hidden:
:maxdepth: 7

00-architecture
01-g2p-pipeline
02-symbols-text-cleaning
03-style-conditioning
04-jets-joint-training
05-labels-dataset-mfa
06-serving-api
```
