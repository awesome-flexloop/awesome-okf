---
type: reference
scope: deepinfer
name: DeepInfer 外部资源
version: "0.1.0"
source: README.md, eval/README.md, 知乎技术报告引文
description: DeepInfer 官方公告、技术报告、论文引用与 DeepSeek 生态关联仓库索引
---

# 外部资源索引

## 一、官方发布

| 资源 | 链接 | 说明 |
|---|---|---|
| DeepInfer 仓库 | <https://github.com/deepseek-ai/DeepInfer> | 开源源码（Apache-2.0） |
| 开源公告（微信） | <https://mp.weixin.qq.com/s?__biz=Mzk0OTYwNzc3NQ%3D%3D&mid=2247485884&idx=1&sn=d457981abe7db1f1b5d600fc109dc836> | DeepSeek 官方公众号《DeepSeek 开源推理框架：走向真正普惠的未来》（2026-10-20） |
| 部署实践技术报告（知乎） | <https://zhuanlan.zhihu.com/p/2095560295930508953> | 《DeepSeek V4.1 Flash 大规模推理部署实践》——生产架构、负载均衡、KVCache、扩缩容 |
| 默认 checkpoint | <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017> | DeepSeek-V4.1-Flash-1017（Hugging Face） |

## 二、论文引用（技术报告参考文献）

| 论文 | 出处 | 与 DeepInfer 的关系 |
|---|---|---|
| DualPath: Accelerating Agentic LLM Inference by Harvesting Disaggregated KV-Cache Storage I/O | ACM SIGCOMM 2026（ISBN 979-8-4007-2467-1） | Decode Load Balancer 组内调度算法参考 |
| DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression | arXiv:2609.19969 | V4.1 模型与 SWA 缓存压缩设计 |
| DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation | arXiv:2607.05147 | 投机解码算法本体 |
| SGLang: Efficient Execution of Structured Language Model Programs | NeurIPS 2024 | 异步调度参考实现 |
| Nanoflow: Towards Optimal Large Language Model Serving Throughput | OSDI 2025 | 异步调度参考实现 |
| 3FS: A High-Performance Distributed File System | deepseek-ai/3FS | Block KVCache 存储底座 |

## 三、DeepSeek 生态关联仓库

| 仓库 | 引入方式 | 用途 |
|---|---|---|
| [DeepSelect](https://github.com/deepseek-ai/DeepSelect) | vendor submodule | 稀疏注意力选择 |
| [FlashMLA](https://github.com/deepseek-ai/FlashMLA) | vendor submodule | MLA 注意力解码核 |
| [DeepEP](https://github.com/deepseek-ai/DeepEP) | vendor submodule | MoE 专家并行通信 |
| [DeepGEMM](https://github.com/deepseek-ai/DeepGEMM) | vendor submodule | GEMM/MoE 核 |
| DeepEP-Ascend / DeepGEMM-Ascend | vendor submodule（昇腾版） | 昇腾平台对应实现 |
| [TileLang](https://github.com/tile-lang/tilelang) | PyPI（`tilelang==0.1.15`） | 核函数 DSL 编译器 |
| [TileKernels](https://github.com/deepseek-ai/TileKernels) | PyPI（`tile-kernels==2.1.0`） | TileLang 核函数库 |
| [deepseek-recipe](https://github.com/deepseek-ai/deepseek-recipe) | 独立开源 | Token 编解码组件（见[本分组姊妹束](../../deepseek-recipe/index.md)） |
| [vLLM](https://github.com/vllm-project/vllm) | 代码基座 | "Derived from vLLM; modified by DeepSeek" |
| [SGLang](https://github.com/sgl-project/sglang) | 灵感来源 | 异步调度等设计 |
| [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | 灵感来源 | README 致谢 |

## 四、评测与复现

| 资源 | 说明 |
|---|---|
| `eval/README.md` | AIME 2026 / HLE / GPQA Diamond 离线评测流程（生成/评分两阶段、LLM judge 或 rule 模式） |
| `examples/sweep/run_sweep.sh` | 性能基准复现（README 基准图：4 SM100 prefill / 64 SM100 decode，单一 scale-up 域内测量） |
