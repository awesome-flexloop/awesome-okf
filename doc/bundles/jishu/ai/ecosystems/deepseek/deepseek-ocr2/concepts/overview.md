---
type: concept
scope: deepseek-ocr2
name: overview
description: DeepSeek-OCR-2 总览——Visual Causal Flow 视觉因果流架构升级
---

# DeepSeek-OCR-2 总览

## 什么是 DeepSeek-OCR-2

**DeepSeek-OCR-2**（论文标题：*DeepSeek-OCR 2: Visual Causal Flow*）是 DeepSeek-OCR 的升级版，于 2026 年 1 月 27 日发布。核心创新是引入**视觉因果流（Visual Causal Flow）**机制，用 Qwen2 解码器改造的因果编码器替代 v1 的 CLIP 双向编码器，实现更接近人类视觉处理方式的编码方式。

- **论文**：arXiv:2601.20552
- **发布时间**：2026年1月27日
- **HuggingFace 模型**：`deepseek-ai/DeepSeek-OCR-2`
- **作者**：Haoran Wei, Yaofeng Sun, Yukun Li
- **标语**："Explore more human-like visual encoding"

## v1 到 v2 的核心演进

### 架构革新：从双向编码到因果流

v1 使用 CLIP-L（纯编码器，双向注意力）作为高层视觉编码器，所有图像 patch 之间可以互相注意。v2 引入 **Qwen2 Decoder-as-Encoder (D2E)** 架构：

```
v1 视觉编码路径：
  图像 → SAM ViT-B → CLIP-L(双向注意力) → concat → Linear(2048→1280) → LLM

v2 视觉编码路径：
  图像 → SAM ViT-B → Qwen2-D2E(因果+非因果混合注意力) → Linear(896→1280) → LLM
```

**D2E（Decoder-to-Encoder）核心思想：**
- 基于 Qwen2 解码器架构（24层，896维，14头GQA），但删除词嵌入层
- 通过 `token_type_ids` 区分两种注意力模式：
  - `token_type_ids=0`：非因果注意力（双向），用于局部 patch 间的信息交换
  - `token_type_ids=1`：因果注意力（单向），模拟从局部到全局的序列化处理
- 不支持 flash_attention_2（自定义掩码需要 sdpa/eager 实现）

### 视觉编码范式对比

| 维度 | v1 (Contexts Optical Compression) | v2 (Visual Causal Flow) |
|---|---|---|
| 核心理念 | 视觉-文本压缩效率 | 类人视觉编码的因果流 |
| 高层编码器 | CLIP-L（编码器，双向注意力） | Qwen2-D2E（解码器改造，混合注意力） |
| 特征维度 | 2048（SAM+CLIP拼接） | 896（Qwen2输出，不拼接SAM） |
| 2D布局标记 | image_newline + view_separator | 仅 view_separator（更紧凑） |
| 默认局部块尺寸 | 640×640 | **768×768** |
| 最大裁剪块数 | 9（推荐6） | **6（硬性上限）** |
| 视觉 token 开销 | 较高（含 newline 标记） | 更紧凑（移除 newline） |
| Prompt 种类 | 7种（文档/通用/图表/描述/定位等） | **2种**（Markdown/纯文本） |

### 性能特点

- **推理速度**：PDF 并发推理速度与 v1 持平（on-par speed）
- **识别质量**：Visual Causal Flow 带来更好的视觉特征建模，尤其在复杂布局和长文档场景
- **代码简化**：移除了 image_newline 参数和特征拼接逻辑，代码更简洁

## 模型架构

```
输入图像
    │
    ├─── 全局视图 ──── SAM ViT-B ──┐
    │    (1024×1024)              │
    │                              ├─── Qwen2-D2E ──── MlpProjector ──── 视觉嵌入
    ├─── 局部裁剪块 ── SAM ViT-B ──┘    (因果流编码)      (896→1280)         │
    │    (n×768×768)                                                         │
    │                                                                        ▼
    └─── <image> tokens 序列替换 ────────────────────────────── DeepSeek LLM ──→ 输出
```

### 视觉编码流程

1. **图像预处理**：与 v1 类似，但局部块尺寸为 768×768，小图判定阈值为 768px
2. **SAM 特征提取**：使用 SAM ViT-B 提取低层视觉特征
3. **Qwen2-D2E 因果编码**：SAM 特征输入 Qwen2 解码器，通过混合因果/非因果注意力实现视觉因果流
4. **线性投影**：896 维 → 1280 维
5. **特征布局**：局部特征在前，全局特征在后，以 view_separator 分隔（无 newline 标记）
