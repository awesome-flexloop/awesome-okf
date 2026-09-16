---
okf_version: "0.2"
type: Example
title: "小红书 dots3-note-prev 接入演练：api-key 头特例、WorkBuddy 直连与 Trae 绕行"
description: "dots.ai 注册拿 Key、非标准 api-key 认证头的 curl/WorkBuddy 配置、深度思考关闭、429 与视频 TTFT 处理；Trae 直连 401 障碍及 OpenRouter Bearer 通道（2026-09-30 关闭时效）"
tags: [dots3, 小红书, askdiandian, api-key, WorkBuddy, Trae, OpenRouter, 接入演练]
generated: { by: "process:blog-article-to-okf-wiki:E", at: "2026-09-16T21:55:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-16T21:55:00+08:00" }
status: flagged
stale_after: 2026-11-30
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/qnQqCivPiuRfJIVMM-zTNQ
    title: 博文 §3 小红书 dots3-note-prev 接入
  - id: dots-docs
    resource: https://dots.ai/platform/docs
    title: dots3-note Preview 官方 API 文档
  - id: openrouter
    resource: https://www.openrouter.ai/dots-studio/dots-3-note-preview:free
    title: OpenRouter 模型页（9-30 下线公告）
---

# 小红书 dots3-note-prev 接入演练

> 预计耗时 5 分钟。dots3 是三平台中**唯一不用 Bearer** 的一家，90% 的接入失败都源于此（F-035/F-071）。

## 0. 平台事实卡（核验后）

| 项 | 值 |
|---|---|
| 控制台 | https://dots.ai/platform |
| 官方文档 | https://dots.ai/platform/docs |
| Base URL | `https://note3-prev-api.askdiandian.com` |
| 模型名 | `dots3-note-prev` |
| 运营方 | 小红书旗下点点模型工作室 dots studio；askdiandian（问点点）为其官方服务域名（F-070） |
| 模态 | 文本/图片/视频/音频**输入**，仅文本**输出**；280B/16B MoE（F-069/F-071） |
| 上下文 | 512K = 524,288 token（**输入+最大输出合计**，F-071） |
| 认证头 | **`api-key: <Key>`**（OpenAI 与 Anthropic 两端点都用它，不是 Bearer、不是 x-api-key）（F-071） |
| 限流 | 60 RPM、150 万 TPM，按单个 Key 计（"默认限流值"，F-071） |
| 免费性质 | 预览期**限时免费**，官方直连截止日未公布；OpenRouter/AtlasCloud 免费通道 **2026-09-30 关闭**（F-069/F-072） |

## 1. 注册与拿 Key（3 步）

1. 浏览器打开 https://dots.ai/platform ，用 **+86 手机号**或**小红书 App 扫码**登录（F-034/F-069）。
2. 左侧进入「API Keys」→「创建 API Key」。
3. 弹窗提示"完整 API Key 仅在本次创建后可见"——**立即复制**到密码管理器或环境变量；关闭后无法再查看，丢了只能重建（F-034）。

## 2. curl 验证（先跑通再配客户端）

OpenAI 兼容端点：

```bash
curl -X POST https://note3-prev-api.askdiandian.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "api-key: 你的API_KEY" \
  -d '{
    "model": "dots3-note-prev",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

Anthropic 兼容端点（注意仍然是 `api-key` 头，外加版本头）：

```bash
curl -X POST https://note3-prev-api.askdiandian.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "api-key: 你的API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "dots3-note-prev",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

排错第一法则（F-035/F-071）：**返回 401，先检查是不是误用了 `Authorization: Bearer`**——两个端点都只认 `api-key` 头。网传"OpenAI 侧 Bearer、Anthropic 侧 x-api-key"的说法与官方文档矛盾，勿采用。

## 3. WorkBuddy 接入（直连可行）

1. 右上角齿轮设置（`Ctrl+,`）→「模型」→「添加自定义模型」（F-036）。
2. 提供商选「自定义 / OpenAI」。
3. 接口地址填**完整** URL（无尾斜杠）：
   `https://note3-prev-api.askdiandian.com/v1/chat/completions`
4. API Key 粘贴完整 Key；模型名称 `dots3-note-prev`；显示名称随意。
5. 高级配置：勾选工具调用、图片输入；推理模式选「仅思考 / 允许关闭思考」（F-036）。
6. 保存后在对话面板选中，发"你好"验证。

> WorkBuddy 自定义渠道允许配置任意请求头/接口，因此 dots3 的非标准认证不构成障碍；Trae（IDE）不同，见第 5 节。

## 4. 四个使用注意

| 现象/需求 | 处理 |
|---|---|
| 429 | 触发限流（60 RPM / 150 万 TPM），退避稍后重试；批量任务控节奏（F-038） |
| 含视频输入，首字很慢 | 官方文档明确视频输入 TTFT 显著变长，**调大客户端超时**，开启流式也要等（F-038/F-071） |
| 想关闭默认深度思考 | OpenAI 协议请求体加 `"chat_template_kwargs":{"enable_thinking":false}`；Anthropic 协议加 `"thinking":{"type":"disabled"}`（F-038/F-071） |
| 医疗/法律/财务内容 | 预览版幻觉抑制不足，输出必须人工复核（F-038） |

Key 纪律：不写进前端、URL 参数、GitHub、日志（F-038）。

## 5. Trae 接入：⚠️ 直连有鉴权障碍

博文称 Trae 桌面版可自定义接入（F-037），核验确认存在头协议冲突（F-073）：

- Trae 的自定义模型配置只发送标准 `Authorization: Bearer`，**没有自定义请求头入口**；
- dots3 两端点强制 `api-key` 头 → Trae 直连 dots.ai 网关大概率返回 401。

截至核验日的可行路径：

1. **Bearer 通道（有时效）**：在 OpenRouter 添加模型 `dots-studio/dots-3-note-preview:free`（AtlasCloud 免费托管），用 OpenRouter 的 Bearer Key 接入 Trae——AtlasCloud 文档已把 Trae 列为支持客户端。**该通道 2026-09-30 关闭**（官方模型页横幅"Going away September 30, 2026"），关闭后此路不通（F-072）。
2. **本地头转换代理**：在本机起一个转发服务，把入站 Bearer 请求改写为 `api-key` 头后转发 askdiandian（非官方方案，需自行维护）。
3. **9-30 之后**：先复核 dots.ai 官方直连政策与 Trae 版本说明，再决定方案。

## 6. 失效预案（建议加入日历）

- **2026-09-30**：OpenRouter 免费通道下线日——当天验证 Trae 侧调用；改用 WorkBuddy 直连或等待官方政策更新（F-072）。
- 预览期端点/限流官方声明"可能调整"，生产环境不要依赖；本演练定位开发测试（F-038）。
