---
type: example
scope: deepseek-recipe
name: 服务器示例
version: "0.2.0"
source: server-rs/README.md, server-py/README.md, encoding-decoding-demo/README.md
description: server-rs（Axum）与 server-py（FastAPI）mock 服务器、create_app 自定义后端注入与 encoding-decoding-demo Web 演示
---

# 服务器示例

官方提供两个 mock 推理的服务器示例与一个 Web 演示，展示 recipe 接入 HTTP 服务的完整形态。

---

## 一、server-rs（Rust · Axum）

```sh
cargo run -p server-rs --locked
# 默认监听 127.0.0.1:7777（SERVER_ADDR 可改）
```

- **路由**：`POST /v1/chat/completions`、`/v1/responses`、`/v1/messages` 三端点；
- **泛型处理**：`api_handler<T: ProtocolRequest + DeserializeOwned>`——`stream=false` 返回完整 JSON，`stream=true` 以 `text/event-stream` 返回 SSE；
- **模型别名**：示例注册 `deepseek-v4-pro`/`deepseek-flash` 别名（`conversion_options()`）；
- mock 回答固定为 `Hello world!`。

## 二、server-py（Python · FastAPI）

```sh
pip install ./deepseek-recipe-python
uvicorn main:app        # 同三端点同端口
```

- `PROMPT_ENCODINGS` 按 `ModelVersion` 选 `DeepseekV4Encoding`/`DeepseekV41Encoding`；
- **扩展点 `create_app(infer=...)`**：注入自定义推理后端——回调收 `PreparedRequest`（含渲染 prompt、推理选项、处理后的图片）并产出 `InferenceChunk` 异步迭代器；
- processor 无 tokenizer 时后端必须产 `text` chunk。

## 三、两者的部署边界

两个示例服务器均**无鉴权**、图片 fetcher 不过滤私网地址，仅限本机回环使用（两份 README 的 Deployment scope 节）。生产部署需自行补齐：鉴权、`DestinationFilter`（SSRF 防护，见[图片管线](../concepts/image-pipeline.md)）、真实推理后端。

## 四、encoding-decoding-demo（Web 演示）

```sh
cargo run -p encoding-decoding-demo --locked
# 打开 http://127.0.0.1:7778（DEMO_ADDR 可改）
```

无需 OpenCV/权重/API key 的本地 Web 界面，两种模式：

- **Render**：选 API 格式、编辑请求 JSON、渲染 prompt 并高亮 special token；
- **Parse**：编辑完整模型输出，解析为所选协议的完整响应。

HTTP 端点 `POST /api/render` 与 `POST /api/parse`（`format` + `body` + `output` + 可选 `finish_reason`）；示例输出含 `…` 推理、两个 DSML 天气工具调用与 EOS；首个 EOS 后的内容被丢弃。不做 token 编解码、不执行推理、不拉取图片 URL。

## 五、完整接入形态参考

```
客户端 ──HTTP──▶ 你的服务（Axum/FastAPI）
                   │ 协议解析（serde/Pydantic）
                   ▼
         ChatCompletionRequest / ResponsesRequest / MessagesRequest
                   │ convert(ConversionOptions)
                   ▼
         ConversationRequest ──▶ DeepseekV41Encoding.encode ──▶ token IDs
                   │
                   ▼
         你的推理后端（DeepInfer 或自研）产出 InferenceChunk 流
                   │
                   ▼
         StreamProcessor.into_protocol_stream / push
                   │
                   ▼
         协议响应（JSON 或 SSE）──▶ 客户端
```

> 后端换 DeepInfer 时，参考 [DeepInfer 束](../../deepinfer/index.md)的离线推理与采样参数；协议侧的一切由 recipe 承担。
