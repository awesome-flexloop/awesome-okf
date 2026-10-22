---
type: concept
scope: deepseek-recipe
name: 图片管线
version: "0.2.0"
source: deepseek-recipe-image/src/, deepseek-recipe-image/README
description: 图片拉取与 OpenCV 预处理、ReqwestImageFetcher 与 DestinationFilter SSRF 防护
---

# 图片管线

`deepseek-recipe-image` crate 负责图片的拉取与预处理，服务于 DeepSeek V4.1 的多模态输入（V4 不接受图片，转换把请求中的每张图片替换为文本 `[Unsupported Image]`）。

---

## 一、Feature 与核心 trait

默认 feature 为 `opencv-preprocess` + `reqwest-fetch`；禁用 `opencv-preprocess` 可在无 OpenCV 环境构建（调用方自供 preprocessor）。核心 trait：

| trait | 职责 |
|---|---|
| `ImageFetcher` | 拉取外部 URL 图片 |
| `ImagePreprocessor` | 预处理（缩放/padding/编码） |
| `ImageResolver` | 组合 fetch + preprocess |

图片支持 **base64 或外部 URL** 两种传入方式。

## 二、OpenCvImagePreprocessor

`src/opencv.rs` 的预处理流程（面向 V4.1 视觉编码器的输入规范）：

1. `infer` 探测媒体类型；
2. 只读 header 校验尺寸上限；
3. 低 detail 降采样；
4. 按 V4.1 token 预算缩放；
5. padding 色 127（匹配模型 mean 0.5）；
6. 透明背景填充 `#FDFDFD`；
7. 输出 WebP 质量 90。

## 三、ReqwestImageFetcher 与 SSRF 防护

- `ReqwestImageFetcher` 默认**不限制**连接的地址——若服务会拉取不受信任请求中的 URL，**必须**为它安装 `DestinationFilter`；
- `DestinationFilter` 是闭包 `Fn(&str, IpAddr) -> bool`（可直接实现），经 `ReqwestImageFetcher::with_destination_filter` 安装：
  - 在 **DNS 解析层**（`FilteringResolver`）过滤目标地址；
  - **每个重定向目标**都过滤（最多跟随 5 次重定向）；
- 错误语义：`ImageError` 的 Display 文本即 400 响应体，如 `.messages[0].image[1]: Failed to download image from …`；
- 配额与并发共享 `ImageByteBudget`，重试由 `RetryPolicy` 控制。

## 四、与编码层的衔接

- 预处理产出经 `ImageResolver` 进入 `Conversation` 的多模态数据；
- prompt 编码侧：`RenderedPrompt::image_sources` 记录图片来源；`IMAGE_SPECIAL_TOKEN_ID`（内置 V4.1 tokenizer 中 id 129264）标记图片 token；
- token 计数：`MultiModalData::image_token_adjustment` 提供图片超出占位符的 token 数，并入 `resolve_max_tokens` 的 `prompt_tokens`。

## 五、Python 侧

Python 绑定导出 `OpenCvImagePreprocessor`、`ReqwestImageFetcher`、`ImageResolver` 等类；`ImageError`/`CalcResizeError` 作为异常类导出——图片失败在 Python 侧表现为可直接捕获的异常。
