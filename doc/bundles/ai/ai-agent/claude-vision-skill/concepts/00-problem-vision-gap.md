# 00 纯文本模型的视觉鸿沟

> 对应事实：F-002~F-005
> 核验状态：✅ DeepSeek 官方 API 文档确认

## 现象：[Unsupported Image]

用 Claude Code 接入第三方纯文本模型（如 DeepSeek V4 Pro）时，想让 AI 看张截图，Read 工具读到的只会是一句 **[Unsupported Image]**——模型无法处理图片输入，只能"干瞪眼"。

这在日常开发中非常常见：

- 贴一张报错截图让 AI 排查
- 发一张架构图让 AI 理解项目结构
- 截一张 UI 设计稿让 AI 还原页面
- 拍一张白板讨论照片让 AI 整理

## DeepSeek 模型的视觉支持现状

### API 层面的事实 ✅

DeepSeek 官方 API 文档（Vision 指南）明确：

> "Only vision models (`deepseek-v4-flash-vision-exp`) accept images; other models return a 400 error ('This model does not support image')."

| 模型 | 视觉能力 | 说明 |
|------|----------|------|
| deepseek-v4-pro（V4 Pro 正式版 0813） | ❌ 不支持图片 | API 返回 400 错误 |
| deepseek-v4-flash（文本版） | ❌ 不支持图片 | 此前为 text-only |
| deepseek-v4-flash-vision-exp | ✅ 实验性视觉模型 | **2026-08-21 上线** |

### ⏰ 时效性补充（核验日 2026-08-29）

博文发表于 2026-08-21，**同一天** DeepSeek 上线了首个多模态模型 `deepseek-v4-flash-vision-exp`：

- 基于 V4-Flash，实验性质（exp 后缀）
- 基准测试表现被 TNW 等媒体报道
- 这意味着用户现在有两条路线：
  1. **直连方案**：换用 deepseek-v4-flash-vision-exp（但它是 Flash 而非 Pro，推理能力有差距，且为实验版）
  2. **中转方案**：继续用 V4 Pro 做推理 + 视觉模型转录（本 Skill 的方案，模型可自由选择）

> 网络上有第三方博客（CSDN，2026-08-16）称"V4 Pro 正式版首次原生支持图像推理"，该说法**与官方 API 文档矛盾**，不足采信。

## 为什么需要中转方案

即使 DeepSeek 有了官方视觉模型，中转方案仍有价值：

| 维度 | 直连视觉模型 | 中转转录方案（本Skill） |
|------|-------------|------------------------|
| 推理模型 | 受限于视觉模型本身（Flash） | 任意强推理文本模型（V4 Pro 等） |
| 视觉模型 | 厂商绑定 | 自由选择（qwen-vl-max / omni 等） |
| 成本 | 视觉+推理同一计费 | 视觉转录与推理解耦，可分别优化 |
| 通用性 | 仅该厂商 | 任何纯文本模型都能"看图" |
| 成熟度 | 实验版（exp） | 视觉模型已商用成熟 |

核心洞察：**视觉理解和语言推理解耦**——让最擅长看图的模型看图，让最擅长推理的模型推理。
