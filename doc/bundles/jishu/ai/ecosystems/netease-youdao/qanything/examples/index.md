# 示例

QAnything 实战示例，共 3 篇，均以仓库 `scripts/` 目录下的真实脚本为线索演练完整数据通路。

* [API 流式问答调用——SSE 帧解析与 LLM 参数透传](api-streaming-chat.md) — 以 stream_chat.py 演练 local_doc_chat 流式调用：SSE 帧格式（`data: ` 前缀 + `[DONE]` 末帧）、增量解析与 LLM 参数透传。
* [知识库上传与检索流程——批量入库到命中回填](kb-upload-and-retrieval.md) — 以 multi_upload_files.py 演练批量上传（扩展名白名单、200MB 分批、aiohttp 并发）与"child 命中、parent 回填"检索链路。
* [最小问答闭环——建库、传文件、提问](minimal-qa-loop.md) — 走通"新建知识库 → 上传文件 → 等待入库 → 非流式问答"最小闭环，说明每步的接口与状态机语义。

```{toctree}
:hidden:
:maxdepth: 7

api-streaming-chat
kb-upload-and-retrieval
minimal-qa-loop
```
