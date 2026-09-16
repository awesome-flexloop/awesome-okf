---
okf_version: "0.2"
type: Example
title: "Agnes AI 接入演练：注册拿 Key、WorkBuddy 配置与文本/图像/视频调用"
description: "从国内站注册到 curl 验证的完整走查：agnes-3.0-flash 对话、agnes-image-2.5-flash 生图（extra_body 坑）、agnes-video-2.5-flash 异步两步轮询、Agnes Code 桌面端边界"
tags: [Agnes-AI, WorkBuddy, curl, 文生图, 文生视频, 接入演练]
generated: { by: "process:blog-article-to-okf-wiki:E", at: "2026-09-16T21:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-16T21:50:00+08:00" }
status: flagged
stale_after: 2026-11-30
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/qnQqCivPiuRfJIVMM-zTNQ
    title: 博文 §2 Agnes AI 接入 WorkBuddy
  - id: agnes-30
    resource: https://wiki.agnes-ai.cn/zh-Hans/docs/agnes-30-flash
    title: agnes-3.0-flash 官方文档
  - id: agnes-image
    resource: https://wiki.agnes-ai.cn/zh-Hans/docs/agnes-image-25-flash
    title: agnes-image-2.5-flash 官方文档
  - id: agnes-video
    resource: https://wiki.agnes-ai.cn/zh-Hans/docs/agnes-video-25-flash
    title: agnes-video-2.5-flash 官方文档
---

# Agnes AI 接入演练

> 预计耗时 10 分钟。机制解释见 [概念 01](../concepts/01-platform-deep-dive.md)；本演练参数为 2026-09-16 官方文档口径。

## 0. 前置选择：直接用国内站

| 项 | 值（国内站，推荐） |
|---|---|
| 控制台 | https://platform.agnes-ai.cn/login/ |
| Base URL | `https://api.agnes-ai.cn/v1` |
| 文档 | https://wiki.agnes-ai.cn/zh-Hans/docs/overview |
| 登录 | 国内邮箱（QQ 邮箱等）或手机号 |

说明（F-009/F-062/F-063）：国际站 platform.agnes-ai.com 网关为 apihub.agnes-ai.com；2026-07-29 官方曾公告切换到 apihub.agnes-ai.cn 并承诺免重新注册，但 8–9 月实测两站账号/Key 已不通用——**无论你以前是否注册过国际站，国内站都重新注册并生成新 Key**（F-064）。

网络自测：浏览器打开 https://api.agnes-ai.cn/v1 ，看到 404 或 JSON 报错即代表网关可达（F-015）。

## 1. 注册并创建 API Key

1. 打开控制台登录（F-013）。
2. 进入「API Key」管理页（侧边栏/个人中心）。
3. 点「创建 API Key」，**立刻复制保存**到密码管理器或本地安全笔记——页面只完整展示一次。

🔐 Key 不进 Git 仓库、前端代码、截图、公开文档；泄露立刻回控制台删除/重置（F-014）。

## 2. WorkBuddy 自定义接入（3 分钟）

1. 聊天界面输入框右下角模型选择按钮 →「添加模型」→ 提供商下拉到底选「自定义 / Custom」（F-016）。
2. 点 Add Model，照填：

| 字段 | 值 |
|---|---|
| Provider | Custom |
| API Base URL | `https://api.agnes-ai.cn/v1`（**必须含 /v1**） |
| API Key | 上一步保存的密钥 |
| 模型名称 | `agnes-3.0-flash`（**区分大小写**，写成 Agnes-3.0-Flash 会失败） |

3. 高级配置：勾选工具调用、图片输入、思考模式、允许关闭思考；不勾「仅思考模式、自定义协议」；思考强度保持「自动」（F-018）。
4. 保存后在聊天面板选中该模型，发"你好，请介绍一下你自己。"返回自我介绍即成功（F-019）。

排错对照（F-017/F-031）：不返回→查 /v1 与 Key；模型列表没有它→查大小写；401→Key 错或额度异常。

## 3. 命令行验证（chat/completions）

```bash
curl https://api.agnes-ai.cn/v1/chat/completions \
  -H "Authorization: Bearer 你的API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-3.0-flash","messages":[{"role":"user","content":"你好，请介绍一下你自己。"}]}'
```

要点（F-019/F-089）：

- OpenAI 协议端点用 `Authorization: Bearer`；同一模型的 Anthropic 端点 `/v1/messages` 官方示例改用 `x-api-key` 头并要求 `anthropic-version: 2023-06-01`。
- 免费档实际限流约 20 RPM（名义 30），触发 429 退避重试即可（F-067）。
- 图像输入传**公开可访问的图片 URL**，不能直传本地文件（F-012）。
- 需要深度思考：OpenAI 协议加 `"chat_template_kwargs":{"enable_thinking":true}`，Anthropic 协议加 `"thinking":{"type":"enabled"}`（F-012）。

## 4. 文生图：agnes-image-2.5-flash

```bash
curl https://api.agnes-ai.cn/v1/images/generations \
  -H "Authorization: Bearer 你的API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.5-flash",
    "prompt": "日出薄雾峡谷上方的发光浮空城市，电影级写实，广角构图，高视觉密度",
    "size": "2K",
    "ratio": "16:9",
    "extra_body": { "response_format": "url" }
  }'
```

关键规则（F-020/F-066，官方逐字确认）：

1. **`size` 是档位（1K/2K/3K/4K）不是像素**，与 `ratio`（1:1、3:4、4:3、16:9、9:16、2:3、3:2、21:9）组合；要标准 16:9 素材就用 `"size":"2K"`+`"ratio":"16:9"`，得到 **2624x1472** 再自行裁剪，不要传 1920x1080（会被映射）。
2. **`response_format` 必须放 `extra_body` 里**，放请求体顶层无效；要 Base64 用 `"extra_body":{"response_format":"b64_json"}` 或文生图 `"return_base64":true`。
3. 图生图/多图合成：输入图放 `extra_body.image`（公共 HTTPS URL 或 Data URI Base64），不需要 `tags:["img2img"]`。
4. 返回读 `data[0].url` 或 `data[0].b64_json`；客户端超时设 **60–360 秒**。
5. 限流：免费档 4K 图 1 次/分（F-067）。

提示词模板（官方给出，F-022）：文生图 = 主体+场景+风格+光照+构图+质量；图生图 = 改变要求+新风格+增删元素+需保留元素。

费用口径（F-021/F-066）：刊例 1K 图 ¥0.07/张、4K 图 ¥0.16/张，**当前现价 ¥0**；属于阶段性免费，批量任务前看控制台公告。

## 5. 文生视频：agnes-video-2.5-flash（异步两步）

第一步，创建任务：

```bash
curl -X POST https://api.agnes-ai.cn/v1/videos \
  -H "Authorization: Bearer 你的API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-2.5-flash",
    "prompt": "雨后的未来城市街道，霓虹倒映地面，一辆银色跑车缓慢驶过，电影级运镜",
    "seconds": "5", "mode": "text", "size": "720P", "aspect_ratio": "16:9"
  }'
# 返回 {"video_id": "..."}
```

第二步，每 1–2 秒轮询直到 `completed`/`failed`：

```bash
curl "https://api.agnes-ai.cn/agnesapi?video_id=VIDEO_ID&model_name=agnes-video-2.5-flash" \
  -H "Authorization: Bearer 你的API_KEY"
```

参数铁律（F-023~F-025/F-066/F-078）：

| 参数 | 取值 |
|---|---|
| `size` | 只能是字符串 `"720P"`，其他值创建即 400 |
| `seconds` | 字符串 `"4"`–`"12"`，默认 `"5"` |
| `n` | 固定 1 |
| `aspect_ratio` | 21:9(1680x720) / 16:9(1280x704) / 4:3(960x720) / 1:1(720x720) / 3:4(720x960) / 9:16(720x1280) |
| `mode` | `text` / `keyframe`（first_frame、last_frame 至少给一个）/ `reference` |
| reference 限制 | 图片 ≤5 张或音频 ≤3 段；**传参考视频直接 400** |

校验失败在创建时同步返回 400，**不建任务、不计费**（F-025）。免费档视频限流 1 RPM（F-089），出片耗时数秒到数十秒，耐心轮询。刊例 ¥0.15/秒（720P），当前 ¥0、官方措辞为"限时免费"（F-066）。

## 6. 懒人法：让 WorkBuddy 自建图像/视频 Skill

在 WorkBuddy 对话中直接发（F-026）：

> 我想使用 Agnes 2.5 Flash 系列模型生成图片和视频，请访问其 API 文档（agnes-image-25-flash 与 agnes-video-25-flash）并分别打包为两个 Skill。

随后即可用自然语言调用，例如"生成一个 2K 16:9 赛博朋克城市夜景，霓虹灯光，电影风格，高细节"。若 Skill 创建失败，先确认本机能打开 https://wiki.agnes-ai.cn/zh-Hans/docs/overview（F-031）。

## 7. Agnes Code（爱思办公）：桌面壳，不是新免费额度

- 官方页 https://agnes-ai.cn/agnescode，形态为桌面客户端 + CLI（CLI 装完跑 `agnes --version` 验证），安装包经官方 COS 桶分发：macOS 双架构 dmg、Windows exe x64、Linux deb x86_64（F-027/F-068）。
- 必须用爱思账户登录，订阅/积分与网页端一致，**底层消耗 Agnes 账户积分，不存在独立"桌面版免费额度"**；客户端本身免费（F-030）。
- 智能模式自动选模型/工具，专家模式手动控模型、上下文、预算与权限（F-029）。
- ⚠️ 单源边界（F-068）：博文所写"Linux 桌面版不与 CLI 混用（官方明示）"、精确系统版本号（macOS 12+/Win10+）以及"内置 8 个技能 slug 清单"均**未在官方页面/安装脚本/官方 GitHub 得到证实**，实际技能面板以你安装后的客户端为准，不要把该清单当官方目录引用。

## 8. 安全红线（结束前自查）

- [ ] Key 未写入任何会被提交/截图/分享的位置（F-014）
- [ ] 医学、患者、未公开经营数据未发送（F-032）
- [ ] 批量任务已控制在 20 RPM / 4K 图 1 RPM / 视频 1 RPM 内（F-067/F-089）
- [ ] 对外发布的生成内容已人工复核并标注来源（F-032）
