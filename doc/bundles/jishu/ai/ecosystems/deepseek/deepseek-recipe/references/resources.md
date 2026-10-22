---
type: reference
scope: deepseek-recipe
name: deepseek-recipe 外部资源
version: "0.2.0"
source: README.zh.md, Cargo.toml, static/tokenizers/README.md
description: 官方文档与 crate 索引、内置 tokenizer 溯源声明与语言生态链接
---

# 外部资源索引

## 一、官方发布

| 资源 | 链接 | 说明 |
|---|---|---|
| deepseek-recipe 仓库 | <https://github.com/deepseek-ai/deepseek-recipe> | 开源源码（MIT） |
| PyPI 包 | <https://pypi.org/project/deepseek-recipe/> | `pip install deepseek-recipe`（Python 3.10+） |
| 开源公告（微信） | <https://mp.weixin.qq.com/s?__biz=Mzk0OTYwNzc3NQ%3D%3D&mid=2247485884&idx=1&sn=d457981abe7db1f1b5d600fc109dc836> | DeepSeek 官方公众号（2026-10-20），与 DeepInfer 同日开源 |
| 部署实践技术报告（知乎） | <https://zhuanlan.zhihu.com/p/2095560295930508953> | DeepSeek Recipe 生产细节：多协议适配、tokenizer 加速、流式解析 |

## 二、crate 文档（docs.rs）

| crate | 链接 | 用途 |
|---|---|---|
| `deepseek-recipe` | <https://docs.rs/deepseek-recipe> | 协议转换与模型输出解析 |
| `deepseek-recipe-core` | <https://docs.rs/deepseek-recipe-core> | 共享的对话、消息、图片与工具类型 |
| `deepseek-recipe-encoding` | <https://docs.rs/deepseek-recipe-encoding> | DeepSeek V4 与 V4.1 的 prompt 渲染与 token 编码 |
| `deepseek-recipe-image` | <https://docs.rs/deepseek-recipe-image> | 图片拉取与预处理 |
| `deepseek-recipe-macros` | <https://docs.rs/deepseek-recipe-macros> | prompt 渲染使用的 `prompt!` 宏 |
| `deepseek-recipe-python` | 仓库内 deepseek-recipe-python/README.md | Python bindings（以 `deepseek_recipe` 导入） |

## 三、仓库内文档

| 文档 | 内容 |
|---|---|
| `docs/streaming.zh.md` / `streaming.md` | 流式响应示例（中/英） |
| `docs/tokenizer.zh.md` / `tokenizer.md` | tokenizer 使用（编码/解码/计数） |
| `docs/development.md` | 源码构建与图片依赖 |
| `docs/build-python-wheel.md` | Python wheel 构建（maturin、cp310-abi3） |
| `CHANGELOG.md` | 0.1.0 → 0.2.0 完整变更与迁移对照表 |

## 四、内置 tokenizer 溯源

`static/tokenizers/` 下两个副本均改自 Hugging Face 官方 tokenizer 并保留 MIT（Copyright (c) 2023 DeepSeek）声明，再分发须保留：

| 目录 | 上游 | 变更 |
|---|---|---|
| `v4/` | `deepseek-ai/DeepSeek-V4-Pro` | id 129264/129279 的 image token 对调 |
| `v41/` | `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp` | id 129264 重赋值为 `<｜image｜>`（即 `IMAGE_SPECIAL_TOKEN_ID`） |

各目录 README 记录比对 revision 与 SHA-256 校验和；encodings 不会自动加载这些文件，需调用方显式加载。

## 五、关联生态

| 项目 | 关系 |
|---|---|
| [DeepInfer](../../deepinfer/index.md) | 姊妹推理引擎束（本分组内） |
| [tokenizers（Rust crate）](https://crates.io/crates/tokenizers) | 分词依赖（0.23；`TOKENIZERS_PARALLELISM` 控制并行） |
| [PyO3](https://github.com/PyO3/pyo3) | Python 绑定（abi3-py310 稳定 ABI） |
| [Axum](https://github.com/tokio-rs/axum) / [FastAPI](https://fastapi.tiangolo.com) | 官方 mock 服务器框架（server-rs / server-py） |
| [OpenCV](https://opencv.org) | 图片预处理（源码构建 4.11+；发布 wheel 打包 4.12.0） |
