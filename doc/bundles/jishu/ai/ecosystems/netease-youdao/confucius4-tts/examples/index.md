# 实战示例

Confucius4-TTS 实战示例，共 3 篇，覆盖推理、服务化与训练三条主线。

* [单次推理全流程（HF 后端）](single-inference.md) — 基于 `ConfuciusTTS` 完成一次零样本声音合成的最小完整流程：构造、generate 四组参数、raw 模式与语言选择、常见调参起点。
* [服务化启动与请求（server.py / webui.py）](serving.md) — FastAPI 服务启动与 /health、/api/tts、/api/tts/stream 请求示例（含流式 PCM 客户端）、Gradio WebUI 启动、三路径选型速查。
* [两阶段训练配置解读](two-stage-training.md) — train_t2s/train_s2a 两阶段训练命令与配置解读、冻结策略的 find_unused_parameters 后果、微调 TSV 五列数据与常见误区。

```{toctree}
:hidden:
:maxdepth: 7

single-inference
serving
two-stage-training
```
