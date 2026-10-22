# deepseek-recipe 核心概念

本章节深入讲解 deepseek-recipe 的核心概念与设计原理。

## 概念文档列表

| 文档 | 说明 |
|---|---|
| overview | 组件定位、六大 crate 职责、请求到响应的数据流主线 |
| protocol-conversion | 三协议（Messages/Chat Completions/Responses）统一转换、ConversionOptions、resolve_max_tokens |
| prompt-encoding | V4/V4.1 prompt 渲染差异、special token 防注入、分段并行 tokenize |
| stream-parsing | 流式输出解析：InferenceChunk、跨 chunk KMP 状态机、工具参数转换 |
| image-pipeline | 图片拉取与 OpenCV 预处理、DestinationFilter SSRF 防护 |

```{toctree}
:hidden:
:maxdepth: 7

image-pipeline
overview
prompt-encoding
protocol-conversion
stream-parsing
```
