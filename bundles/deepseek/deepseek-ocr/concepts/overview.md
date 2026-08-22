---
type: concept
scope: deepseek-ocr
name: overview
description: DeepSeek-OCR 总览——Contexts Optical Compression 视觉文本压缩模型
---

# DeepSeek-OCR 总览

## 什么是 DeepSeek-OCR

**DeepSeek-OCR**（论文标题：*DeepSeek-OCR: Contexts Optical Compression*）是 DeepSeek 团队于 2025 年 10 月发布的开源 OCR（光学字符识别）多模态大模型。它从 LLM 中心视角重新审视视觉编码器的角色，探索视觉-文本压缩的边界。

- **论文**：arXiv:2510.18234
- **发布时间**：2025年10月20日
- **HuggingFace 模型**：`deepseek-ai/DeepSeek-OCR`
- **作者**：Haoran Wei, Yaofeng Sun, Yukun Li
- **基础模型**：基于 DeepSeek-VL2 架构，语言模型采用 DeepSeek-V2/V3 系列

## 核心理念

传统 OCR 模型以视觉编码器为中心，将文档图像编码为特征序列后由 LLM 解码。DeepSeek-OCR 提出**上下文光学压缩（Contexts Optical Compression）**范式：

1. **从 LLM 视角设计视觉编码**：不追求视觉编码器本身的表征能力，而是优化视觉 token 到语言 token 的压缩效率
2. **双编码器架构**：SAM ViT-B 提取低层视觉特征 + CLIP-L 提取高层语义特征，拼接后通过线性投影层映射到语言模型空间
3. **2D 动态分块策略**：全局缩略图（1024×1024）+ 局部高分辨率裁剪块（640×640），兼顾全局布局理解与局部文字清晰度

## 模型架构

```
输入图像
    │
    ├─── 全局视图 ──── SAM ViT-B + CLIP-L ──┐
    │         (1024×1024, pad)              │
    │                                       ├─── 特征拼接 ──── MlpProjector ──── 视觉嵌入
    ├─── 局部裁剪块 ── SAM ViT-B + CLIP-L ──┘       (2048→1280)        │
    │    (n×640×640, dynamic crop)                                    │
    │                                                                ▼
    └─── <image> tokens 序列替换 ────────────────────── DeepSeek LLM (V2/V3)
                                                                      │
                                                                      ▼
                                                              OCR 文本输出
```

### 视觉编码流程

1. **图像预处理**：
   - 全局视图：将原图 pad 到 1024×1024
   - 局部视图：对大于 640×640 的图像，按最佳宽高比动态裁剪为多个 640×640 块
   
2. **双编码器特征提取**：
   - SAM ViT-B 提取边缘、纹理等低层特征
   - CLIP-L 提取语义级视觉特征
   - 两者在特征维度拼接（CLIP 去掉 CLS token 后与 SAM flatten 特征拼接，总维度 2048）

3. **投影与布局**：
   - MlpProjector 将 2048 维线性投影到 1280 维
   - 使用 `image_newline` 和 `view_seperator` 特殊嵌入标记 2D 布局和视图边界
   - 局部特征在前，全局特征在后，以 view_separator 分隔

### 视觉 Token 布局（2D tile_tag 模式）

```
[local_tile_1_row_1][newline]...[local_tile_m_row_n][newline]
[global_view_rows][newline]...[global_view_rows]
[view_seperator]
```

- `image_newline`：标记每行 tile 的结束
- `view_seperator`：标记局部视图与全局视图的分界

### 支持的输入格式

- 图片格式：JPG、PNG、JPEG
- PDF 文档：通过 PyMuPDF 转换为图像后逐页处理
- 支持单图推理和批量推理
