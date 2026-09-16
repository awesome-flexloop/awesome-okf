---
okf_version: "0.2"
type: Reference
title: "博文信源事实清单"
description: "微信公众号博文《我用3个免费模型，把WorkBuddy的成本砍到了零》（免费大模型接入全攻略 2026-09 实战版）F-001~F-061 事实登记与 F-062~F-088 权威核验补充"
tags: [信源登记, 事实清单, 免费大模型, Agnes, dots3, AMD, WorkBuddy]
generated: { by: "process:blog-article-to-okf-wiki:R", at: "2026-09-16T21:10:00+08:00" }
status: flagged
stale_after: 2026-11-30
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/qnQqCivPiuRfJIVMM-zTNQ
    title: "《我用3个免费模型，把WorkBuddy的成本砍到了零》（技术宅SuperLaos，老商，2026-09-10）"
  - id: agnes-official-wiki
    resource: https://wiki.agnes-ai.cn/zh-Hans/docs/overview
    title: Agnes AI 官方文档中心（国内站）
  - id: dots-official-docs
    resource: https://dots.ai/platform/docs
    title: 小红书 dots3-note Preview 官方 API 文档
  - id: amd-token-factory
    resource: https://developer.amd.com.cn/radeon/modelapis
    title: AMD Radeon Cloud Token Factory（BETA）Public Free Model APIs
---

# 博文信源事实清单

> 本文件是 F 编号双份登记之一（另一份在 SpecWeave 主仓库 spec `.trae/specs/okf-wiki-ecosystem/free-llm-api-hands-on-blog-okf-wiki/facts.md`），两份编号集合须一致、连续无跳号。
>
> - **F-001 ~ F-061**：博文事实（2026-09-09 整理口径）。客观事实纯描述；「作者观点」「作者实测」已显式标注。
> - **F-062 ~ F-088**：2026-09-16 权威源核验补充（每条附信源）。标【勘误】者，正文呈现以核验值为准、博文口径仅作对照。
> - 价格/额度/日期时效性极强，全部以官方控制台当日显示为准。

## A. 元信息与术语（F-001 ~ F-005）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-001 | 文章推送标题《我用3个免费模型，把WorkBuddy的成本砍到了零》；正文内主标题为「免费大模型接入全攻略（2026-09 实战版）」 | 标题区 |
| F-002 | 公众号「技术宅SuperLaos」，作者署名老商；"原创"标记；2026-09-10 08:40 发布，IP 属地河北；正文注"整理日期 2026-09-09"；结尾称"整合多渠道+腾讯/字节官方及社区资料，交叉核实于 2026-09-09" | 元信息/结尾 |
| F-003 | 适用对象：想零成本把大模型接进 WorkBuddy / Trae Work 等 OpenAI 兼容客户端的开发者、运营、数据分析师 | 导语 |
| F-004 | 风险提示：各平台免费政策按周变动，额度/限流/截止日以控制台实时显示为准；医药、患者、未公开经营数据请勿传第三方模型；认准官方域名谨防仿冒 | 导语 |
| F-005 | 博文术语约定：LLM=纯文本大模型；VLM=视觉/多模态模型；Base URL 须带 /v1 否则 404；免费档五分法=无限期免费/限流不限量/每日重置/限时免费（有截止日）/一次性赠金；价格单位 元/百万 token（输出）；国内直连=无需代理 | §0 |

## B. 三平台总览（F-006 ~ F-008）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-006 | Agnes AI 总览（博文口径）：免费模型 agnes-3.0-flash（文本+图像 URL）＋image-2.5-flash（生图）＋video-2.5-flash（生视频）；另有 Agnes Code 桌面版内置 8 技能；国内直连；国内邮箱/Gmail·GitHub 注册、免绑卡；"无限期免费（定价待公布，免费档延续）"；约 20 RPM；最大坑"免费人多输出慢；4K 图 1 次/分" | §1/§5；定价与旧模型状态见 F-065 勘误 |
| F-007 | 小红书 dots 总览：模型 dots3-note-prev（VLM 四模态）；国内直连；手机号/小红书账号注册、免绑卡；"限时（官方未公布；OpenRouter 通道 9-30 关）"；60 RPM、150 万 TPM；512K；最大坑"认证头 api-key 非 Bearer" | §1/§3/§5 |
| F-008 | AMD Radeon 总览（博文口径）：4 款免费模型（2 LLM+2 VLM）；国内直连；手机号/邮箱/GitHub 等注册、免绑卡；每日重置积分制（不扣钱）；最大坑"速度慢；Vision 标 LIMITED FREE 随时撤"；"并发 >5 排队" | §1/§4/§5；名单现状见 F-075 |

## C. Agnes AI 细节（F-009 ~ F-032）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-009 | 两站对照表（博文口径）：国内站 platform.agnes-ai.cn（/login/），网关 `https://api.agnes-ai.cn/v1`，国内邮箱/手机号，国内直连，文档 agnes-ai.cn/doc/overview；国际站 platform.agnes-ai.com，网关 `https://apihub.agnes-ai.com/v1`，Gmail/GitHub，文档 agnes-ai.com/doc/overview；认证均为 Authorization: Bearer；推荐模型两站同为 agnes-3.0-flash | §2.1；规范文档站见 F-062 |
| F-010 | 博文转述"官方公告"：因部分国内网络访问国际站 API 不稳定，请将 apihub.agnes-ai.com 切换为 api.agnes-ai.cn（.com→.cn，apihub→api）；仅改域名，Key/模型名/参数不变 | §2.1；公告原文见 F-063 勘误 |
| F-011 | 博文称两站账号体系独立：国际站老用户用国内站需重新注册并生成新 Key | §2.1；政策演变见 F-064 |
| F-012 | agnes-3.0-flash 特性（博文据官方整理）：面向 Agent 任务与开发工作流；更稳定的函数调用、多步骤工具编排；文本+图像 URL 输入（公开 URL，非本地直传）；多协议 Chat Completions/Responses/Messages（Anthropic 兼容）；Thinking 模式（chat_template_kwargs.enable_thinking 或 thinking.type:enabled）；强化可信交付；价格待公布、免费档延续 | §2.2；价格见 F-065 勘误 |
| F-013 | 注册拿 Key：平台登录 → 控制台「API Key」管理页 →「创建 API Key」→ 立即复制保存 | §2.3 |
| F-014 | 安全红线：API Key 勿进公开代码仓库/前端/截图/公开文档；泄露即删除或重置 | §2.3 |
| F-015 | 网络自测法：浏览器开 https://api.agnes-ai.cn/v1，返回 404 或 JSON 错误都算通，打不开才是不通 | §2.3 |
| F-016 | WorkBuddy 配置：模型选择按钮 →「添加模型」→ 提供商选「自定义/Custom」→ 填 Base URL（含 /v1）、API Key、模型名 agnes-3.0-flash（区分大小写） | §2.4 |
| F-017 | 常见易错点：① Base URL 漏写 /v1；② 模型名大小写错（Agnes-3.0-Flash 会失败） | §2.4 |
| F-018 | 高级配置：勾选工具调用、图片输入、思考模式、允许关闭思考；不勾「仅思考模式、自定义协议」；思考强度「自动」 | §2.4 |
| F-019 | 连通验证：新建对话发"你好，请介绍一下你自己。"返回自我介绍即正确；博文附 chat/completions curl（POST，Bearer，model=agnes-3.0-flash） | §2.5 |
| F-020 | agnes-image-2.5-flash：POST /v1/images/generations；文生图/图生图/多图合成；size 1K/2K/3K/4K × ratio 八种；非原生精确尺寸自动映射，标准 16:9 用 size:"2K"+ratio:"16:9"（得 2624x1472）再裁剪；response_format 放 extra_body（url/b64_json）；输入图放 extra_body.image（HTTPS URL 或 Data URI），不需 tags:["img2img"]；文生图 Base64 用 return_base64:true；返回 data[0].url/b64_json；超时 60–360s | §2.6①；官方逐字确认 F-066 |
| F-021 | 刊例价（博文注"以平台公告为准"）：1K 图 ¥0.07/张、4K 图 ¥0.16/张、视频 ¥0.15/秒；现价均 ¥0 | §2.6；F-066 确认 |
| F-022 | 官方提示词结构：文生图=[主体]+[场景/环境]+[风格]+[光照]+[构图]+[质量要求]；图生图=[改变要求]+[新风格]+[增删元素]+[需保留的元素] | §2.6① |
| F-023 | agnes-video-2.5-flash 异步两步：POST /v1/videos 返回 video_id；GET `https://api.agnes-ai.cn/agnesapi?video_id=<ID>&model_name=agnes-video-2.5-flash`，1–2 秒轮询至 completed/failed | §2.6②；F-066 确认 |
| F-024 | 视频三种 mode：text；keyframe（first_frame/last_frame 至少一个）；reference（images ≤ 5 或 audios ≤ 3；不支持参考视频，传 videos 直接 400） | §2.6② |
| F-025 | Flash 视频限制：size 仅字符串 "720P"；seconds 字符串 "4"–"12"（默认 "5"）；n 固定 1；aspect_ratio 21:9/16:9/4:3/1:1/3:4/9:16；博文称 16:9 实测 1280x704（作者实测口径，官方文档 9 月注记同值）；校验失败创建时直接 400、不建任务不产生费用 | §2.6② |
| F-026 | "懒人法"：在 WorkBuddy 发指令让其访问 agnes-image-25-flash 与 agnes-video-25-flash 文档并分别打包为两个 Skill；博文附图像/视频 Skill 示例调用句 | §2.6③ |
| F-027 | Agnes Code 桌面版（爱思办公，依据 agnes-ai.cn/agnescode）：桌面客户端连接本地工作空间、与爱思 Web 账户同步订阅积分；另有 CLI（agnes --version）；博文称支持 macOS 12.0+/Windows 10+/Linux x86_64（.deb）；博文注"Linux 桌面版不与 CLI 混用（官方明示）" | §2.7；单源项见 F-068 |
| F-028 | 博文称 Agnes Code 内置 8 技能：agnes-aigc、agnes-text-to-image、agnes-image-to-image、agnes-text-to-video、agnes-image-to-video、agnes-sheet-author、agnes-doc-guide、skill-creator | §2.7②；清单仅博文单源 F-068 |
| F-029 | 双模式：智能模式（自动选模型/工具/路径）；专家模式（手动控制模型/上下文/工具/预算/产物/权限） | §2.7③；F-068 确认 |
| F-030 | 使用限制：爱思账户登录，订阅/积分/团队权限与网页端一致，无独立"桌面版免费额度"，底层消耗 Agnes 账户积分；客户端本身免费；国内直连；只读授权目录。"桌面版≠额外免费羊毛，而是图形化操作入口"（末句作者观点） | §2.7④；1200 积分赠额见 F-068 |
| F-031 | 故障排查 5 行：文本不返回→URL/Key；列表无模型→大小写；Skill 创建失败→文档 URL；视频慢→轮询等待；认证失败→Key/积分 | §2.8 |
| F-032 | Agnes 段红线：Key 不外泄；敏感资料不传第三方、对外内容人工复核标注来源；额度以控制台为准、批量节制；文本用 flash、图像/视频走对应模型 | §2.8 |

## D. 小红书 dots3（F-033 ~ F-038）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-033 | 本段源：同公众号原创《薅羊毛！公测免费的小红书大模型 dots3-note-prev 接入 WorkBuddy 与 Trae 指南》（老商，2026-08-21） | §3 源注 |
| F-034 | 注册 3 步：开 https://dots.ai/platform 登录；国内手机号或小红书账号；「API Keys」→「创建 API Key」，Key 只展示一次 | §3.1；F-069 确认 |
| F-035 | API 基础信息：Base URL `https://note3-prev-api.askdiandian.com`；OpenAI 端点 /v1/chat/completions；Anthropic /v1/messages；模型 dots3-note-prev；512K（输入+输出 ≤ 524,288 token）；认证头 `api-key: <Key>`（非 Bearer）；60 RPM、150 万 TPM | §3.2；F-071 逐字确认 |
| F-036 | WorkBuddy 接入：设置（Ctrl+,）→「模型」→「添加自定义模型」→ 自定义/OpenAI → 接口填完整 …/v1/chat/completions（无尾斜杠）→ Key、模型名；勾工具调用、图片输入；保存发"你好"验证 | §3.3 |
| F-037 | Trae 接入（博文限定桌面版本地用）：添加模型→自定义配置；OpenAI Chat Completions 或 Anthropic Messages（anthropic-version 2023-06-01）；关「Auto」手选 | §3.4；直连障碍见 F-073 勘误 |
| F-038 | 注意事项：免费截止未公布、只做开发测试；429 退避或多 Key；视频输入 TTFT 长放宽超时；预览版医疗/法律/财务人工复核；Key 不进前端/URL/日志；深度思考默认开（enable_thinking:false / thinking.type:disabled 关） | §3.5 |

## E. AMD Radeon Token Factory（F-039 ~ F-044）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-039 | AMD 中国开发者平台（Radeon Cloud）Public Free Model APIs：OpenAI 兼容、一把 Key 多模型、国内直连；OpenAI /v1/chat/completions 与 Anthropic /v1/messages 双格式；推理跑 AMD GPU 云、不耗本地算力；入口 https://developer.amd.com.cn/radeon/modelapis | §4.1；F-074 补品牌与端点细节 |
| F-040 | 博文列四款模型（参数据 AMD 模型卡 2026-09）：① DeepSeek-V4-Flash-0731（LLM，博文称 64K–128K，0731 快照，FREE）；② MiniCPM5-1B（LLM，约 128K，清华 OpenBMB，INT4 0.5GB，手机/浏览器可跑，FREE）；③ DeepSeek-V4-Flash-Vision-Exp（VLM，约 1M，博文称 305B/激活 13B、MIT，看图/OCR/截图问答，LIMITED FREE）；④ Qwen3.8-Flash-Next（AMD 归 LLM 文本、博文按实际能力列 VLM，262K 可扩 1M，博文称 125B/6B、Qwen4 先导、接近 Qwen3.7-Plus，FREE） | §4.2；逐项核验见 F-075/F-078~F-080 |
| F-041 | 注册领 Key（约 10 分钟 4 步）：入口 Login；手机号/邮箱/GitHub/CSDN/魔搭登录（GitHub 仅读基础公开信息）；邮箱验证；点模型卡片弹窗给 Base URL/Model/Key（免费模型共用同一把 Key）/curl | §4.3 |
| F-042 | 额度规则：积分制，输入 0.14 pts/1M、输出 0.28 pts/1M、缓存 0.0028 pts/1M，引文"Free to use. Points show relative usage, not a charge"；每天重置；博文称早期宣传"每天 $10"、近期实测缩到约 $1/天；作者实测"DeepSeek-V4-Flash 跑 200 万 token 才耗约 5%"；活动无到期时间但可能缩水/收回 | §4.4；$1/天与 5% 见 F-077 勘误 |
| F-043 | 调用：POST https://developer.amd.com.cn/radeon/api/v1/chat/completions，Bearer，model=DeepSeek-V4-Flash-0731；换 model 名即切换；VLM 可喂图；Cherry Studio/Cursor/opencode 接法相同 | §4.5 |
| F-044 | 短板（作者实测+观点）：速度慢首字延迟高；连接偶发错误需调大 retry；并发超 5 排队、定位开发调试；Vision LIMITED FREE 随时撤；敏感内容建议本地 MiniCPM5-1B 或 Ollama；缓存便宜（0.0028 pts/1M）多轮对话自动命中 | §4.6 |

## F. 横向对比与全局表（F-045 ~ F-058）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-045 | §5 横评：Agnes 上下文"未公开（约数百 K）"、约 20 RPM；dots 512K、60 RPM/150 万 TPM；AMD 1M/128K/256K、并发 >5 排队；Agnes 为 OpenAI+Responses/Messages，dots/AMD 为 OpenAI/Anthropic 双兼容 | §5 |
| F-046 | §5 选型结论（**作者观点**）：无限期免费→Agnes；每日额度→AMD；多模态→dots3 或 AMD Vision；本地端侧→MiniCPM5-1B 或 Ollama | §5 |
| F-047 | GLM-4.7-Flash（智谱，200K，永久免费，输出 0，"限流不限量"） | §6；F-083 确认 |
| F-048 | GLM-5.x（智谱，200K，"新用户 2000 万/限免窗口"，博文称输出 8–28 元；"旗舰限免，随时收"） | §6；价格边界见 F-083 勘误 |
| F-049 | DeepSeek V4-Flash（博文称 64K–128K，"新户 500 万/30 天"，输出 3–9 元，"已预告涨价"） | §6；F-079/F-086 勘误 |
| F-050 | Qwen-Turbo（阿里，128K–1M，"7000 万一次性"，输出 0.5–1.0 元） | §6；礼包口径见 F-085 |
| F-051 | ERNIE-Lite / Speed（百度，博文均标 128K，永久免费，0 元） | §6；Lite 实为 8K，见 F-085 |
| F-052 | 豆包 Seed-2.0-Lite（字节，博文称 128K、"100 万/月永久"、输出 0.6–3.66 元，火山方舟） | §6；三项见 F-084 勘误 |
| F-053 | Kimi K2.5（月之暗面，256K，网页免费/10 万月，博文称输出 6–12 元，"长文档强"） | §6；输出价见 F-082 勘误 |
| F-054 | Hunyuan-lite（腾讯，免费档 0/0 永久，0 元） | §6；F-085 确认 |
| F-055 | Hy3（混元 3，腾讯，256K，WorkBuddy 限时免费，295B/21B，MoE，Apache 2.0） | §6；F-081 确认 |
| F-056 | Hy4 preview（混元 4，腾讯，1M，WorkBuddy 限时两周免费，770B/49B，MoE，Apache 2.0） | §6；F-081 确认 |
| F-057 | Trae 内置两行（博文口径）：Doubao-1.5-pro/Seed-1.6；DeepSeek-V3.1/Kimi-K2/GLM-4.6/Qwen-3-Coder；"Trae 基础版免费"；WorkBuddy 自带 Hy3/Hy4 限时免费 | §6；清单代际见 F-087 勘误 |
| F-058 | 博文称付费旗舰（GLM-5、DeepSeek V4-Pro、Qwen3.5、ERNIE 6.0）输出价 3–28 元；表声明"价格/免费档为公开口径，波动频繁，以官网为准" | §6 |

## G. 词汇表/收尾/引用（F-059 ~ F-061）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-059 | §7 词汇表约 30 条：LLM/VLM/MoE/上下文窗口/Token（中文约 1–2 字=1 token）/RPM/TPM/RPD（举 Gemini 免费层 1500 RPD）/QPS/OpenAI 兼容/Base URL/Endpoint/Bearer（注 dots3 用 api-key 头）/Rate Limit（429 退避）/Multimodal/Thinking/Prompt Cache（举 AMD 0.0028 pts/1M）/Cache Hit Free/灰度发布/Streaming/Agent/Open Source（Apache 2.0、MIT、Qwen Community）/SDK | §7 |
| F-060 | §8 收尾（**作者观点+行动建议**）：组合策略=日常 Agnes+AMD 主力、dots3 处理多模态混流、高配旗舰看 §6、本地敏感走 Ollama；"免费有尽头"（dots OpenRouter 9-30 关、AMD Vision LIMITED FREE、DeepSeek 预告涨价）"能接先接"；合规红线重申；额度以控制台为准 | §8；部分前提已被 F-072/F-075/F-086 修正 |
| F-061 | 正文内微信链接 5 条：①《零消耗！把免费模型 Agnes 接入 WorkBuddy》②《Agnes2.5 接入 WorkBuddy（国内站注册版）》③《dots3-note-prev 接入 WorkBuddy 与 Trae 指南》④《2B 干翻 4B！国产小钢炮重划斩杀线》⑤"Ollama 本地大模型系列教程合集"（「阅读原文」）；正文含 4 张无 alt 截图 | 正文链接 |

## H. Agnes 核验补充（F-062 ~ F-068）

| 编号 | 事实（权威核验） | 信源 |
|------|------|------|
| F-062 | 官方规范文档站为 wiki.agnes-ai.cn/zh-Hans/docs/...（博文的 /doc/overview 是 302 跳转别名）；9 月现行国内站统一网关 `https://api.agnes-ai.cn/v1`（FAQ 原文"中国站统一使用以下 Base URL"）；platform.agnes-ai.cn/.com、apihub.agnes-ai.com 主机均存活 | wiki.agnes-ai.cn/zh-Hans/docs/overview、faqs.md |
| F-063 | 【勘误·域名公告】2026-07-29 官方通稿切换目标是 `https://apihub.agnes-ai.cn/v1`（仅 .com→.cn，**保留 apihub 主机名**），并非博文所写 api.agnes-ai.cn；通稿承诺"无需重新注册、无需换 Key，模型名称/请求参数/调用方式均无需修改"。api.agnes-ai.cn 是 9 月现行网关（与 apihub.agnes-ai.cn 均可通），博文把两个时点压成一条 | 太平洋科技 g.pconline.com.cn/x/2179/21794505.html；腾讯云社区 2718438 |
| F-064 | 【演变】7·29 通稿曾承诺国际站用户无需重新注册；8-9 月多源实测两站账号/Key 已不通用、混用报"无效的令牌"；博文按 9 月现状描述基本准确，官方无"两站独立"原句 | CSDN bigbear00007/163419246 |
| F-065 | 【勘误·定价与模型状态】agnes-3.0-flash 刊例价**已公布**：输入缓存命中 ¥0.035、输入 ¥0.35、输出 ¥1.00/百万 token，三项现价 ¥0（非"待公布"）；agnes-2.5-flash 已全量上线（非灰度）；agnes-2.0-flash 官方标"已废弃，建议迁移 2.5"（非"灰度可用"）。3.0-flash 能力清单与官方页逐字吻合 | wiki.agnes-ai.cn agnes-30-flash/agnes-25-flash；wiki.agnes-ai.com agnes-20-flash |
| F-066 | 图像/视频 API 细节与官方文档逐字吻合（size/ratio/2624x1472/extra_body/60–360s；/v1/videos+/agnesapi 轮询、三 mode、images≤5/audios≤3/videos→400、720P、4–12、n=1、16:9=1280x704——该实测注记本身出自官方文档"2026 年 9 月实测"）；刊例 ¥0.07/¥0.16/¥0.15、现价 ¥0 属实；视频页措辞为"当前**限时**免费" | wiki.agnes-ai.cn agnes-image-25-flash.md、agnes-video-25-flash.md |
| F-067 | FAQ 原文"核心 AI 模型可以**无限期免费**使用……完整多模态模型免费，包括文本、图像、视频"；Token Plan（2026-06-22 生效）default 文本"允许 RPM 30/实际 RPM 20"、4K 图"允许 1/实际 1"——博文约 20 RPM、4K 1 次/分精确对应"实际"列；数值可按产品策略调整 | wiki.agnes-ai.cn faqs.md、tokenplan.md |
| F-068 | 【部分单源】官方页确认"爱思办公·Desktop + CLI"、三平台安装包（dmg 双架构/exe/deb x86_64，分发源 cos-agnes-code.agnes-ai.cn）、agnes --version、订阅积分一体化、智能/专家双模式、客户端免费；三条❌/❓仅博文单源：① "Linux 桌面版不与 CLI 混用（官方明示）"官方页与安装脚本均无；② 最低系统 macOS 12.0+ 官方未列；③ 8 个内置技能 slug 全网零命中、官方仅泛述技能扩展。另第三方载桌面端每日登录送 1200 积分（账户级赠额） | agnes-ai.cn/agnescode；download_cli 脚本 |

## I. dots3 核验补充（F-069 ~ F-073）

| 编号 | 事实（权威核验） | 信源 |
|------|------|------|
| F-069 | dots.ai/platform 真实存在：标题 dots3-note Preview，"+86 手机号/小红书扫码"登录，文档 dots.ai/platform/docs；官方定位"预览期**限时免费**"；favicon 托管小红书 CDN（it-force.xhscdn.com）；模型为 280B 总参/16B 激活 MoE，输出仅文本（预览版） | dots.ai/platform；机器之心经 36氪 ad.36kr.com/p/3938759517896072 |
| F-070 | askdiandian.com 是小红书官方同一套服务：runtime-config.js 显式指向 authApiOrigin www.askdiandian.com、platformApiOrigin dots-platform.askdiandian.com；DNSPod 注册（2024-08-20），站点名"点点"（小红书 AI 品牌）；博文拼写正确（askdian/askdianian 为错拼） | dots.ai/platform/runtime-config.js；WHOIS |
| F-071 | API 细节官方逐字确认：512K=524,288（输入+最大输出之和）；四模态输入（文本/图片/视频/音频）；认证头 `api-key`（两端点均用，非 Bearer、非 x-api-key）；60 RPM/150 万 TPM 按 Key 计；深度思考默认开（enable_thinking:false/thinking.type:disabled 关）；anthropic-version 2023-06-01 | dots.ai/platform/docs |
| F-072 | 【关键时效】OpenRouter 免费通道 2026-09-30 关闭：模型页顶部"**Going away September 30, 2026**"，slug `dots-studio/dots-3-note-preview:free`，AtlasCloud 单一供应商免费托管；dots.ai 直连截止日未公布 | openrouter.ai/dots-studio/dots-3-note-preview:free |
| F-073 | 【勘误·接入路径】WorkBuddy 直连可行（有实测）；**Trae 直连有鉴权障碍**——Trae 自定义模型仅 Bearer、无自定义头入口，dots 强制 api-key 头，直连大概率 401；可行路径为经 OpenRouter/AtlasCloud 的 Bearer 通道（AtlasCloud 已把 Trae 列入支持客户端）或本地头转换 | docs.trae.com.cn/ide/models；atlascloud.ai dots-3-note-prev-free 页 |

## J. AMD 核验补充（F-074 ~ F-077）

| 编号 | 事实（权威核验） | 信源 |
|------|------|------|
| F-074 | 官方品牌名 **Radeon Cloud / Token Factory（BETA）**；入口 developer.amd.com.cn/radeon/modelapis（/radeon/tokenfactory 同官方）；OpenAI /radeon/api/v1/chat/completions（Bearer）、Anthropic /radeon/api/v1/messages（**x-api-key** + anthropic-version 2023-06-01）；模型卡"served by the AMD GPU Cloud"；一账户一个 `rc-` 开头 Key 通用；手机号/邮箱/GitHub/CSDN/魔搭登录 | AMD 面板模型卡 JSON；CSDN 164341618 |
| F-075 | 【重大时效·名单已变】4 款名单在 2026-09 初成立（freeaiapi 09-02、CSDN 09-04 同款）；**2026-09-16 官方页已变 5 款**：DeepSeek-V4-Flash-0731（Free）、Qwen3.8-Flash-Next（Free）、Qwen3.8-27B（Limited Free，新增）、MiniCPM5-2B（Free，**取代 1B**）、MinerU2.5-Pro（Limited Free，新增）；Vision-Exp 模型卡返回 `{"detail":"Model card not found"}`。背景：DeepSeek 2026-09-10 下线 V4-Flash/Vision-Exp，旧名路由 V4.1-Flash | developer.amd.com.cn/radeon/modelapis；api-docs.deepseek.com/updates |
| F-076 | 积分单价模型卡 JSON 逐字确认：`"Free to use. Points show relative usage—not a charge."`（pts/1M），输入 0.14/输出 0.28/缓存读 0.0028；重置两口径：固定日切（Asia/Shanghai）vs 每 24h 滚动 1 积分≈2500 万 token——以控制台为准 | AMD 模型卡 token_factory.pricing |
| F-077 | 【勘误·额度传言】"早期每天 $10"有二手源（points 不构成真实扣费，$ 仅参考折算）；"近期缩到约 $1/天"**查无证据且被相反口径覆盖，判 ❌ 传言**；"200 万 token 耗 5%"与单价粗算不符（混合负载约 30–60% 日额度，大量缓存命中才可能个位数）❓；"并发>5 排队"单源体感，第三方硬口径 20–30 RPM、并发 8（⚠️）；稳定性 experimental、全站 BETA | uscardforum 523739；tools321；igetoken |

## K. 模型规格与全局价格核验补充（F-078 ~ F-088）

| 编号 | 事实（权威核验） | 信源 |
|------|------|------|
| F-078 | 【勘误·MiniCPM5 混用】1B/2B **均存在**：MiniCPM5-1B（2026-05-26，面壁/OpenBMB，1,080,632,832 参数，128K，Apache-2.0，INT4 0.5GB，GGUF Q4_K_M 约 657MB）；MiniCPM5-2B（2026-09-07/08 开源，AA 23 分，全球 4B 以下开源第一）。博文模型卡描述的是 1B，"2B 干翻 4B"描述的是 2B | huggingface.co/openbmb/MiniCPM5-1B；openbmb.cn/news；CSDN 164717441 |
| F-079 | 【勘误·上下文+时效】Vision-Exp 305B/13B/MIT（2026-09-01 开源权重）/1M/单图 384 视觉 token/无视觉加价属实；**文本 V4-Flash 上下文官方同为 1M，博文 64K–128K 失实**；2026-09-10 起旧模型名"仍可调用，但对应模型已下线，请求将由 DeepSeek-V4.1-Flash 提供服务"；0731 为 2026-07-31 快照版 | api-docs.deepseek.com pricing/updates；vLLM recipes |
| F-080 | Qwen3.8-Flash-Next 高度属实：2026-08-26 开源，125B MoE/6B 激活，HF 自述 Qwen4 架构先导，原生 262K、YaRN 扩 1M，文本/图像/视频单一 API；百炼名 Qwen3.8-Flash（08-28 上线）；"接近 Qwen3.7-Plus"偏保守（第三方称多项超 Claude Opus 4.6 Max、训练成本 1/9）；AMD 分类无百炼对应证据 ❓ | datacamp.com qwen3-8-flash-next；aliyun.com/product/news/30535 |
| F-081 | 混元规格全部属实：Hy3 正式版 2026-07-06（Preview 04-23），295B/21B/256K/MoE/Apache-2.0，API 输入 ¥1/输出 ¥4；Hy4 preview 2026-08-28 发布开源，770B/49B/1M/Apache-2.0，输入 ¥6/输出 ¥18，首发 WorkBuddy/CodeBuddy、元宝、ima | 腾讯云 4205517；新华网 20260828 |
| F-082 | 【勘误·Kimi】K2.5 存在（2026-01，1T/32B MoE，多模态，262,144 上下文）；官方价输入缓存命中 ¥0.70/未命中 ¥4.00/**输出 ¥21**——博文 6–12 元失实；网页/App 免费属实，"10 万/月免费"无官方口径 ❓（现行为新用户代金券）；现役 K2.6/K2.7 Code/K3 | platform.kimi.com/docs/pricing/chat-k25 |
| F-083 | 【勘误·智谱】GLM-4.7-Flash 永久免费/无上限/200K/约 30 并发/缓存免费属实（2026-01-20）；GLM 5.x 现役 5/5.1/5.2/5.3/5.3-Flash，输出 ¥24/28/26.6/2.66——博文"5.x 8–28 元"边界错（¥8 是 GLM-4.7 火山档，5.x 旗舰 24–28）；2000 万体验包属实但 90 天有效且分包（200 万通用+600 万 4.6V+1200 万 4.5-Air） | 36kr 3977443117635203；open.bigmodel.cn trialcenter |
| F-084 | 【勘误·豆包三项】Seed-2.0-Lite 官方**上下文 256K、最大输出 128K**（博文混淆）；刊例 ≤32k 输入 ¥0.6/输出 ¥3.6，32–128k ¥0.9/5.4，128–256k ¥1.8/10.8（博文把输入价当输出、3.66 无对应数字）；免费为每模型**一次性 50 万 token 试用**（博文"100 万/月永久"失实），另有授权采集奖励日返最高 500 万、30 天有效；Doubao-1.5-pro 曾入 Trae ✅，Seed-1.6 无证据 ❓ | docs.volcengine.com 2374452/1099320/1391869 |
| F-085 | 【勘误·其余免费档】① 百度 ernie-speed-128k（0/0、128K、永久免费）、ernie-lite-8k（0/0、**8K**）——博文"Lite 128K"张冠李戴；② Hunyuan-lite 免费属实（社区称 256K）；③ Qwen-Turbo 官方输入约 ¥0.3/输出 ¥0.6；"7000 万"为百炼全平台新用户礼包总和（各约 100 万、90 天），非 turbo 独占非永久 | InfoQ 计费表；腾讯云 PDF 1729_105924；help.aliyun.com 3023262 |
| F-086 | 【勘误·DeepSeek 价格方向】3–9 元对应 2026-08-17 生效峰谷价（空闲 4.5/高峰 9）；**2026-09-09 官方公告 9-10 起 Flash 降价**（空闲输出 ¥4、缓存未命中 ¥1，高峰翻倍）随 V4.1-Flash 上线——博文发布当天旧区间即被 4–8 元取代，"预告涨价"方向反；"新户 500 万/30 天"无载 ❓ | 新浪财经 2026-08-17；36kr 3975405867069960 |
| F-087 | 【勘误·Trae 清单滞后】博文四款均为往代；现行（2026-09）内置 Seed-Evolving/2.1、GLM-5.3 系列、DeepSeek-V4.1/V4-Pro/V4-Flash、Kimi K3/K2.8/K2.7-Code、MiniMax-M3、Qwen3.8 系列（Qwen-3-Coder 2026-02-26 已被 Next 替代）；Trae 已上线积分计费与付费会员，"基础版免费"部分成立 | docs.trae.cn/ide_models；forum.trae.cn/t/topic/218 |
| F-088 | WorkBuddy 为腾讯云 CodeBuddy 团队（代号"小龙虾"）出品的全场景 AI 办公桌面工作台（workbuddy.cn），支持文档/表格/PPT/数据分析、内置 Hy3/Hy4、可加 OpenAI 兼容自定义模型；TraeWork 为**字节跳动**产品（2026-06 由 TRAE SOLO 改名），二者是腾讯 vs 字节同赛道竞品、非同一产品；博文并列举例未混淆归属 | workbuddy.cn/docs；36kr 3958796219137161 |

## L. V 阶段第二轮独立复核追加（F-089）

| 编号 | 事实（权威核验） | 信源 |
|------|------|------|
| F-089 | V 阶段第二轮独立复核补三项：① Agnes `/v1/messages` 官方示例鉴权头为 `x-api-key` + `anthropic-version: 2023-06-01`，非博文 F-009"均 Bearer"口径（Bearer 第三方实测可兼容）；② Agnes 视频免费档实际限流 1 RPM（博文未提）；③ AMD 另提供 `/v1/messages/count_tokens` 端点 | wiki.agnes-ai.cn agnes-30-flash/tokenplan；radeon-cloud-docs api/overview |
