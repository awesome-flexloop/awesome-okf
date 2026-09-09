# 实战示例

EmotiVoice 实战示例，共 3 篇，对应推理、前端与服务化三条动手路径。

* [联合推理完整流程示例](joint-inference-workflow.md) — 基于 inference_am_vocoder_joint.py 演练完整 TTS 推理：准备四段式测试文件、执行推理命令、拆解内部装配与生成调用、定位输出音频。
* [中英混读文本处理示例](mixed-lingual-g2p.md) — 基于 frontend.py 演练中英混合文本音素化：数字转中文、双前端分工、跨界标记插入与 sos/eos 包裹，覆盖命令行与 Python 调用两种形态。
* [OpenAI 兼容 API 调用示例](openai-compatible-api.md) — 基于 openaiapi.py 演练服务启动与调用：curl 与 Python 客户端两种形态、SpeechRequest 字段语义、speed 后处理注意事项与依赖分装。

```{toctree}
:hidden:
:maxdepth: 7

joint-inference-workflow
mixed-lingual-g2p
openai-compatible-api
```
