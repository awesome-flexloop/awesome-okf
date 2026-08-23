---
title: 模块路线图
type: example
bundle: /datawhale/tiny-universe
sources:
  - https://github.com/datawhalechina/tiny-universe
---

# 示例：tiny-universe 模块路线图

本示例展示 tiny-universe 八个主体模块按 LLM 技术栈层次的递进关系，帮助学习者规划阅读路径。

## 分层路线图

```
┌─────────────────────────────────────────────────────┐
│                   评估闭环层                          │
│                   TinyEval                           │
│         （选择式/判别式/生成式评测指标）                │
└──────────────────────┬──────────────────────────────┘
                       │ 评估
┌──────────────────────▼──────────────────────────────┐
│                   增强系统层                          │
│   TinyRAG        TinyGraphRAG       TinyAgent        │
│  （检索增强）   （图检索增强）    （ReAct 工具调用）   │
└──────────────────────┬──────────────────────────────┘
                       │ 调用/增强
┌──────────────────────▼──────────────────────────────┐
│                   模型训练层                          │
│        TinyLLM/TinyLlama3       TinyDiffusion        │
│        （语言模型预训练）       （DDPM 图像生成）      │
└──────────────────────┬──────────────────────────────┘
                       │ 构建于
┌──────────────────────▼──────────────────────────────┐
│                   基础组件层                          │
│      TinyTransformer              Qwen-Blog          │
│  （手工搭建 Attention）    （解剖 Qwen2：GQA/RoPE）   │
└─────────────────────────────────────────────────────┘
```

## 推荐阅读路径

### 路径 A：零基础入门

TinyTransformer → Qwen-Blog → TinyLLM → TinyRAG → TinyEval

适合只有深度学习基础、希望系统理解 LLM 的学习者。

### 路径 B：应用开发导向

TinyRAG → TinyGraphRAG → TinyAgent → TinyEval

适合已有 LLM 使用经验、希望理解 RAG/Agent 原理以便魔改的开发者。TinyTransformer 作为补基础材料按需阅读。

### 路径 C：生成模型导向

TinyDiffusion → TinyLLM → TinyTransformer

对图像生成与语言生成都感兴趣的学习者，可从扩散模型切入，再对比语言模型的预训练流程。

### 路径 D：前沿复现导向

主体部分任意模块 → CDDRS (ADVEI25)

先掌握经典技术白盒实现，再进入探索部分复现前沿学术作品，完成从"会做"到"创新"的跃迁。

## 学习时间预估（基于 README 信息）

| 模块 | 关键资源指标 |
|------|-------------|
| TinyDiffusion | 两小时完成图像生成预训练 |
| TinyLlama3/TinyLLM | 2G 显存，数小时训练 |
| TinyRAG | 有 GPU 镜像可直接使用 |
| TinyAgent | 视频号录播 |
| TinyEval | 含高考数学评测选修 |

具体学习时间因基础而异，README 未提供统一预估。

## 相关概念

- [白盒构建理念](/datawhale/tiny-universe/concepts/white-box-philosophy)
- [TinyLLM](/datawhale/tiny-universe/concepts/tiny-llm)
- [TinyRAG](/datawhale/tiny-universe/concepts/tiny-rag)
- [TinyAgent](/datawhale/tiny-universe/concepts/tiny-agent)
- [TinyDiffusion](/datawhale/tiny-universe/concepts/tiny-diffusion)
