---
type: concept
title: AI 服务：运行时大模型 API、9 个传参值与自动集成
description: 秒悟内置 AI 大模型服务的完整用法——文本/视觉/图片三类共 9 个 API 传参值、两个端点、按 Token 与按张数两档计费、自动四步集成（Service AK→MEOO_PROJECT_API_KEY→Edge Functions→前端）、Cloud→AI 用量查看；三段官方 fetch 参考代码（已还原换行）
tags: [meoo, miaowu, ai-service, llm, edge-functions, api, openai-compatible]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
sources:
  - id: ai
    resource: https://docs.meoo.com/features/ai
    title: AI 服务
  - id: models
    resource: https://docs.meoo.com/features/models
    title: 支持模型介绍
---

# AI 服务：运行时大模型 API、9 个传参值与自动集成

> Meoo 提供**开箱即用的 AI 大模型服务**：当应用需要 AI 能力时，平台自动集成并生成调用代码，无需手动配置（F-073）。
>
> ⚠️ 本页讲的是**应用运行时**调用 AI 的 API；它与构建应用时「选择哪个模型写代码」是两套清单，务必先读第 5 节。

## 1. 9 个 API 传参值（三类）

### 1.1 文本对话（6 个）

| 模型 | 传参值 | 特点（源页原话） |
|---|---|---|
| Qwen3.6-Plus | `qwen3.6-plus` | 通义千问旗舰版，综合能力强 |
| Qwen3-Max | `qwen3-max` | 通义千问增强版，适合复杂推理 |
| Kimi | `kimi-k2.5` | 月之暗面出品，长文本处理能力强 |
| Deepseek | `deepseek-v3.2` | 深度求索出品，代码与推理能力突出 |
| GLM | `glm-5` | 智谱 AI 出品，中文理解能力优秀 |
| MiniMax | `MiniMax-M2.5` | MiniMax 出品，多模态综合能力强 |

### 1.2 视觉理解（1 个）

| 模型 | 传参值 | 特点 |
|---|---|---|
| Qwen VL | `qwen3-vl-plus` | 支持图片内容识别与分析（F-075） |

### 1.3 图片生成（2 个）

| 模型 | 传参值 | 特点 |
|---|---|---|
| Qwen Image 2.0 | `qwen-image-2.0` | 通义图片生成，高质量、速度快 |
| Wan2.7 | `wan2.7-image` | 万象图片生成，艺术风格丰富（F-076） |

以上 9 个传参值逐字来自 S8 模型表（F-074–F-076）；大小写敏感（如 `MiniMax-M2.5` 保留大写），写进代码时不要改写。

## 2. 两个端点

| 用途 | 端点（逐字） |
|---|---|
| 文本对话 / 视觉理解 | `https://api.meoo.host/meoo-ai/compatible-mode/v1/chat/completions`（F-081） |
| 图片生成 | `https://api.meoo.host/meoo-ai/api/v1/services/aigc/image-generation/generation`（F-082） |

文本/视觉共用一个 OpenAI 兼容风格的 `chat/completions` 端点；图片生成走独立的 `aigc/image-generation/generation` 端点，请求体结构也不同（见第 6 节）。

## 3. 计费：两档

- **文本对话 / 视觉理解**：按 **Token 用量**计费；
- **图片生成**：按**生成张数**计费（F-077）。

源页未给单价、免费额度与套餐内配额；做成本测算时以 pricing 页为准（本束未抓取）。用量可在 **Cloud → AI** 查看使用记录与用量统计（F-079）。

## 4. 自动四步集成（无需手写鉴权）

AI 服务是内置服务，在对话中描述需求即可，平台自动完成（F-078）：

1. **识别需求**：判断应用是否需要 AI 能力；
2. **开通服务**：自动为应用申请 Service AK，并以 `MEOO_PROJECT_API_KEY` 为名写入环境变量；
3. **生成代码**：自动生成 **Edge Functions 服务端**调用代码，通过 `MEOO_PROJECT_API_KEY` 读取 AK——**不会暴露在前端**；
4. **完成集成**：自动生成前端调用代码，完成端到端 AI 功能集成。

已有应用追加 AI 能力，直接说需求即可，源页话术示例（逐字，F-080）：

> 「帮我加一个 AI 对话功能」、「帮我实现图片内容识别」。

鉴权要点（F-083）：

```text
Authorization: Bearer ${Deno.env.get("MEOO_PROJECT_API_KEY")}
Content-Type: application/json
```

AK 只在 Edge Functions 服务端经 `Deno.env.get` 读取。这与 [06 云服务 Secrets](06-cloud-services.md) 的环境变量管理是同一机制——**密钥进环境变量、不进前端代码**是本平台 AI 集成的第一安全前提。

## 5. 与构建器 13 模型的关系（重要辨析）⚠️

| | 本页（S8 AI 服务） | [02 构建器模型](02-model-selection.md)（S3） |
|---|---|---|
| 阶段 | 应用上线后的**运行时调用** | 创建应用时的**构建期选模型** |
| 数量 | 9 个传参值 | 13 个模型 |
| 形态 | 写进 `model` 字段的字符串 | 选择器里的型号 |
| 例 | `qwen3.6-plus`、`deepseek-v3.2`、`glm-5` | Qwen3.8-Flash、DeepSeek-V4-Pro、GLM-5.3 |

核验结论为 **conflicting 双源并存**（[verification.md](../references/verification.md) 核验项四）：两页命名代次对不齐（如构建器已是 Qwen3.8/V4/GLM-5.3 系，API 表仍是 qwen3.6-plus/deepseek-v3.2/glm-5），官方模型页自述存在版本差异、需注意时效（F-016）。唯一直接同名的是 Kimi `kimi-k2.5`；技能页「Kimi 2.5 / GLM-5 / MiniMax-M2.5」的推荐（F-129）与本页 API 口径一致，是第三处旁证。处置：**写代码只从第 1 节 9 个值里取；选构建模型只看 02 页 13 个**。

## 6. 三段调用参考（已还原换行）

> 源页声明（F-087）：Meoo 会自动生成调用代码，以下为**参考示例，实际代码由 Meoo 根据需求生成**。源页经 HTML→Markdown 转换后代码被压成单行、围栏无语言标识；以下按天然逻辑还原缩进换行，字符串、端点、参数名与取值零改写。

### 6.1 文本对话

```javascript
const response = await fetch("https://api.meoo.host/meoo-ai/compatible-mode/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${Deno.env.get("MEOO_PROJECT_API_KEY")}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "kimi-k2.5", // 可替换为其他模型：qwen3.6-plus / qwen3-max / deepseek-v3.2 / glm-5 / MiniMax-M2.5
    messages: [
      { role: "user", content: "你好" }
    ],
    stream: false,
  }),
});
const data = await response.json();
console.log(data.choices[0].message.content);
```

要点（F-084）：`model` 可取 6 个文本值之一；`stream: false` 为非流式；响应从 `data.choices[0].message.content` 读取。

### 6.2 视觉理解

```javascript
const response = await fetch("https://api.meoo.host/meoo-ai/compatible-mode/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${Deno.env.get("MEOO_PROJECT_API_KEY")}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "qwen3-vl-plus",
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "这张图片里有什么？" },
          { type: "image_url", image_url: { url: "https://your-image-url.com/image.png" } },
        ],
      }
    ],
  }),
});
const data = await response.json();
console.log(data.choices[0].message.content);
```

要点（F-085）：同一端点，但 `content` 是数组，文本与图片以 `type` 区分；图片以可访问 URL 传入（可用 [09 文件存储](09-file-storage.md) 的 CDN 链接承载）。

### 6.3 图片生成

```javascript
const response = await fetch("https://api.meoo.host/meoo-ai/api/v1/services/aigc/image-generation/generation", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${Deno.env.get("MEOO_PROJECT_API_KEY")}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "qwen-image-2.0", // 或 wan2.7-image
    input: {
      messages: [
        {
          role: "user",
          content: [{ text: "一只坐在窗边的橘猫，暖阳光照射" }],
        }
      ],
    },
    parameters: {
      size: "1024*1024",
    },
  }),
});
const data = await response.json();
```

要点（F-086）：不同端点、不同包体——提示词在 `input.messages[].content[].text`，尺寸在 `parameters.size`；**`"1024*1024"` 中的星号 `*` 是源页原文字符，不是乘号 `×`**，传参照抄。

## 7. 典型集成路径

```text
对话框：「帮我加一个 AI 对话功能」
  → 平台识别需求
  → 申请 Service AK，写入 MEOO_PROJECT_API_KEY（Secrets）
  → 生成 Edge Functions 服务端代码（Deno.env.get 读 AK）
  → 生成前端调用代码
  → Cloud → AI 查看使用记录与用量统计
```

> 洞察（架构型）：这套设计把 AI 应用最容易做错的两件事——密钥泄露与前后端鉴权——从用户选择变成了平台默认：AK 自动申请、自动入环境变量、调用代码强制落在 Edge Functions 服务端（F-078③）。用户面对的仍然只是一句话（F-080），但背后是「对话即控制台」主线第一次进入**带计费的运行时资源**：与 [03 一键建库](03-web-app-build.md)（F-038）不同，AI 调用每次发生都产生 Token/张数费用（F-077），因此 Cloud → AI 的用量面板（F-079）不只是监控，也是成本闸门。

## 8. 坑点与边界

- **传参值零改写**：`MiniMax-M2.5` 大小写、`1024*1024` 的星号、`qwen3.6-plus` 的点号都必须逐字（F-074–F-086）；把构建器型号（如 `Qwen3.8-Flash`）填进 `model` 字段没有官方依据。
- **图片生成端点和包体都不同**：不要给图片端点发 `messages` 直挂在顶层的 chat 包体（F-086）。
- **AK 不能放前端**：参考代码的服务端位置（Edge Functions + `Deno.env.get`）是安全模型的一部分（F-083）；把 `MEOO_PROJECT_API_KEY` 写进前端等于公开密钥。
- **参考代码 ≠ 你拿到的代码**：源页明示实际代码由 Meoo 按需求生成（F-087），排错时以项目内生成的代码为准。
- **视觉模型只列了 1 个**（`qwen3-vl-plus`，F-075）；构建器里其他标「原生多模态」的型号（F-017/F-018）不自动等于运行时可传，两页不要互推。
- **图片必须是 URL**：视觉理解示例的图片入参是公网可访问 URL（F-085），不是 base64 或本地文件；先传存储再取链接见 [09](09-file-storage.md)。

## 9. 延伸阅读

- [02 模型选择](02-model-selection.md)：构建期 13 模型与 9 传参值的完整对照
- [06 云服务](06-cloud-services.md)：Secrets 环境变量与 `MEOO_PROJECT_API_KEY` 的管理位置
- [09 文件存储](09-file-storage.md)：视觉理解图片 URL 的来源之一
- [11 技能创建](11-skills-authoring.md)：技能场景的模型推荐（F-129）与本页口径一致
- 逐字事实与代码处理声明：[source-ledger.md](../references/source-ledger.md) F-073–F-087
