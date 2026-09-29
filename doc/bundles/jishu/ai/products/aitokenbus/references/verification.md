---
okf_version: "0.2"
type: reference
title: P0 权威核验报告——AITokenBus 发布文
status: stable
stale_after: 2026-12-31
---

# P0 独立核验报告

> 核验日期：2026-09-16（博文发布于 2026-07-22，间隔 56 天）
> 核验方式：① 浏览器实访产品站点公开页面 + 前端代码/公开 API 探测（未注册、未提交任何个人信息与 API Key）；② WebSearch 厂商官方文档/官方博客/主流媒体多轮交叉核验；③ 独立信源全渠道排查
> 信源距离预判：**个人开发者自宣**（作者唐霜即平台创建者，第一人称发布文），产品能力类声明全部按 P0 处理

## 核验结论总览

| P0 项 | 博文 F | 结论 | 关键证据 |
|-------|--------|------|---------|
| 平台已上线、网址可访问 | F-002 | ✅ | 站点 200 正常，SPA 完整渲染（F-025） |
| 托管 Key 建共享池 + 邀请机制 | F-014 | ✅ | 池配置字段、邀请码重发生成接口、/join/&lt;码&gt; 真实校验（F-026） |
| Token 市场挂售 + TC 支付交换 | F-015 | ✅ | /market 公开可浏览，8 个 active 挂售（F-027） |
| TC 获得/消耗闭环 | F-010/F-011 | ✅ | TC Wallet、赚 TC 三途径（F-026/F-028） |
| API 多协议兼容 | F-014/F-023 | ✅ | /v1、/v1/messages、/v1beta 三协议（F-037） |
| GLM-5.2 版本真实 | F-021 | ✅ | 智谱官方 2026-06-16 发布记录（F-033） |
| Kimi K3 版本真实 | F-021 | ✅ | Kimi 官方博客 2026-07-16/17（F-034） |
| 官方免费矿池注册即用 | F-012/F-018 | ⚠️ | 免费池真实但供给极薄（F-028） |
| "免费无限用 AI" | F-020 | ⚠️ | 营销修辞，实测 2 节点/1-of-35 模型可用（F-028） |
| ollama 本地算力贡献 | F-017 | ⚠️ | GPU 挖矿机制存在，"ollama"零佐证（F-031） |
| 路由故障自动切换 | F-019 | ⚠️ | 分流/优先级存在，跨池 failover 无说明（F-030） |
| TC 无法币/不可转让 | F-013 | ⚠️ | 代码行为一致但无条款公示（F-029） |
| qwen-3.8 版本 | F-021 | ❌ | 发文时点不存在，2026-08-03 才发布（F-035） |
| 运营主体/独立信源 | F-001 | ❌ | 零独立信源、无 ICP/主体/协议（F-032/F-036） |

**状态裁定**：核心产品声明（平台在线 + 共享池/市场/TC/免费池/算力/路由/多协议）经独立实地核验基本成立；2 项 ❌ 中，qwen-3.8 属结语顺带提及的**非核心版本号错误**（走勘误、正文呈现正确值），主体缺失属**风险提示**而非主结论证伪 → 不触发 flagged，bundle 定 **stable**，但附强边界声明并在 2026-12-31 前安排复核。

---

## 一、产品实地核验（F-025~F-032、F-037）

### F-025：站点在线与身份 ✅

`https://aitokenbus.24x7.to` HTTPS 正常打开，React/Vite 单页应用；标题 "AITokenBus - AI Token Sharing Platform"；主标语"共享 · 兑换 · 贡献 Token 并赚回更多"、大字"让你的 AI 永不熄火"；副文案"一个账号，让 AI Token 在整个生态里流动起来，驱动 Claude Code、Codex、Agent、Bot 等各类产品"；提供简中/繁中/英文与深色模式。HTTP 自动跳 HTTPS；www 子域未配置。

### F-026：功能模块导航 ✅

公开导航：Token 市场（/market）、Token 算力池（/mine）、下载 SUMU「新品」（/download）、登录、开始使用。前端代码可见登录后模块：我创建的池、我加入的池、Request Routing（/routes）、TC Wallet（/wallet）、Token 市场、Token 算力池、我的算力节点、Community（QQ 群，需登录）、个人资料。探测 /docs、/about、/pricing、/terms、/privacy 均被 SPA 兜底重定向到 /login——**无文档站、无定价页、无协议页**。

### F-014：共享池 + 邀请机制 ✅

前端代码中池上游配置含 `source_type / api_url / api_key / auth_type / models / fallback_model / max_members / lifecycle_days`；邀请机制含 `/pools/:id/regenerate-invite`，邀请链接形态 `https://aitokenbus.24x7.to/join/<邀请码>`，公开访问对无效码真实返回"链接无效"。博文所述"托管 API 地址 + 专有 Key + 邀请链接 + 分包"机制在产品中可验证（创建动作需登录，未实测）。

### F-015/F-027：Token 市场与挂售实测 ✅

/market 无需登录可浏览，核验日 API 返回 `total: 8` 个 active 挂售，发布时间跨度 2026-05-20 至 2026-09-13；每张卡片含模型列表、"X TC/千 Token 起"、成员数/上限、发布者与时间。实例：AIHubMix（Kimi K3/Hy3/MiniMax M3，6/100 人，1 TC）、"grok 500刀额度"（11/100，0.2 TC）、"FLASH 自用套餐"（GLM-5.3-Flash+Qwen3.8-Flash，1/3，0.05 TC）、OpenRouter 免费模型（0 TC）。博文 glm→TC→K3 的交换路径与产品形态一致。

### F-012/F-018/F-028：免费矿池 ⚠️

官方免费池 `official-mine-pool-free-llm` 真实存在：0 TC、模型 "Free"、131K 上下文、核验时 2 个在线节点；登录引导文案"点击加入，无需审批……池中所有模型完全免费，算力由在线节点捐赠"。但供给端实测单薄：LLM 矿池注册节点 71 个、仅 2 个在线；/mine 价目表 35 个模型中**仅 qwen-3-1.7b 标"可用"，其余 34 个"暂不可用"**。博文"注册即可立即使用"在机制上成立，"源源不断""免费无限"在核验时点无供给保障。

### F-017/F-031：本地算力贡献与"ollama" ⚠️

"用您的 GPU 提供 AI 推理算力，赚取 Token Coin"机制在算力池页与 API 中确认；注册节点需填 GPU 型号/显存/模型，节点密钥前缀 `skml_`；桌面端 SUMU v0.1.2（Windows exe、macOS dmg，Linux 开发中）承载节点能力，文案"贡献闲置 GPU 加入算力矿池"。但全站页面与前端 bundle 中 **"ollama"零命中**（vllm/lm-studio/docker 同为 0），无本地接入公开文档——博文"装 ollama 之类启动器"的具体说法无法佐证，实际封装形态是自研 SUMU 客户端。

### F-019/F-030：路由与故障切换 ⚠️

Request Routing 模块确认存在，英文副标题原文 "Create routing rules to dispatch requests to different pools based on content type"；规则支持目标池、池模型 passthrough、内容类型（Default/Thinking/Long Context/Image Understanding/Model Mapping）、请求模型与目标模型改写、优先级 Priority（高值优先）、启用停用、独立路由 API Key 与 Base URL。但前端代码 **"failover"零命中**，"fallback"全部为 React 框架内部用词；仅每个池上游配置含一个 `fallback_model`（备用模型）字段。博文宣称的"一个上游服务挂掉自动切换到下一条规则（跨上游池）"未见公开说明，优先级链是否构成隐式降级无法从公开页确认。

### F-013/F-029：TC 经济封闭性 ⚠️

全站无定价/充值/套餐/提现页面；前端代码无 ¥、$、CNY、USD、支付宝、微信支付、withdraw、recharge 字样；一切价格以 TC/千 Token 计，钱包（TC Wallet）记录余额、累计赚取/消耗。产品行为与博文"不发生真实兑换"一致；但**全站无任何"不可转让/不兑换法币/永久存储"的公示文字，且无用户协议/隐私政策承载该承诺**——这是自述属性，不是合同属性。

### F-032/F-036：主体、备案与独立信源 ❌

页脚仅一行文字，无公司/个人主体名称、无 ICP 备案、无协议、无联系方式（唯一社群入口为登录后 QQ 群）；注册页无协议勾选；安装包托管于腾讯云 COS 上海存储桶；.to 为汤加国家顶级域名；GitHub 仅作 OAuth 登录（client_id `Ov23liAStPyVPTYFvMnO`），无开源仓库。全渠道检索（GitHub/ProductHunt/Reddit/V2EX/少数派/即刻/知乎/主流媒体）**零独立第三方信源**，可检索信息全部来自唐霜自有博客（tangshuang.net/9822，页面日期 07-21）、公众号、播客与腾讯云 07-23 原文转载；作者博客存在前身产品 AICodingBus（tangshuang.net/9750），站内公告"We're Now AITokenBus"显示系更名而来。

### F-037：API 接入形态 ✅

池密钥走 OpenAI 兼容 Base URL `https://aitokenbus.24x7.to/v1`（/v1/chat/completions、/v1/responses、/v1/models），另有 Claude 格式 /v1/messages、Gemini 格式 /v1beta/models；密钥前缀 skm_/sks_（池）、路由专用 Key、skml_（算力节点）。首页声明兼容 OpenAI/Anthropic/Google Gemini/DeepSeek 四类接口并自动格式转换，支持 SSE 流式、配额（Token 限制/周期配额/并发/RPM）与成员自管 Key（创建者不可见）。矿池类型创建时间 2026-07-20，与"2026 年 7 月上线"吻合。

---

## 二、模型版本号核验（勘误清单①：日期/版本表）

### F-033：GLM-5.2 ✅

智谱 AI 官方文档《模型与产品发布记录》2026-06-16 条明确记载"GLM-5.2 新一代旗舰模型上线"（2026-06-15 全量开放），官方模型 ID 即 `glm-5.2`，1M 上下文、128K 输出。版本演进：GLM-4.6（2025-09-30）→ GLM-5（2026-02-11）→ GLM-5.1（04-07）→ **GLM-5.2（06-15/16）** → GLM-5.3（08-19）/GLM-5.3-Flash（08-26，核验日最新）。博文 07-22 提及 GLM-5.2 属实但非最新（注：核验日 AITokenBus 市场挂售已出现 GLM-5.3-Flash）。
信源：https://docs.bigmodel.cn/cn/update/new-releases 、https://docs.bigmodel.cn/cn/guide/models/text/glm-5.2 、https://z.ai/blog/glm-4.6

### F-034：Kimi K3 ✅

月之暗面 2026-07-16（美区）/07-17 凌晨（北京）正式发布 Kimi K3：2.8 万亿参数、100 万 token 上下文、原生多模态，官方 API ID 即 `kimi-k3`；2026-07-27 深夜开放完整权重与技术报告（HF：moonshotai/Kimi-K3）。博文 07-22 发布时 K3 刚上市 5 天、API 已可用但**权重尚未开源**——属跟进热点，时间成立。
信源：https://www.kimi.com/blog/kimi-k3 、https://platform.kimi.com/docs/api/chat 、https://www.eet-china.com/news/202607173308.html 、https://news.bjd.com.cn/2026/07/28/11889855.shtml

### F-035：Qwen3.8 ❌ 时间错位（本 bundle 唯一事实性勘误）

博文 2026-07-22 写"qwen-3.8"，该模型当时**尚未发布**：

| 项目 | 正确信息 |
|------|---------|
| 实际发布日 | **2026-08-03**（博文 12 天后），阿里巴巴正式发布 Qwen3.8，总参数 2.4 万亿，API 同日上线千问 AI 平台 |
| 开源节奏 | 2026-08-13 开放 Qwen3.8-2.4T 权重；2026-08-26 Qwen3.8-Flash 发布并开源 |
| 官方模型 ID | `qwen3.8-max`、`qwen3.8-flash`、`qwen3.8-2.4t-a95b`（**点号连接，无 `qwen-3.8` 连字符 ID**） |
| 发文时点最新版本 | Qwen3.7 系列（Qwen3.7-Max/Plus Preview，2026-05-19 API 上线/05-20 阿里云峰会官宣；Qwen3.7-Flash-2026-07-15 快照） |
| 平台侧佐证 | 核验日 AITokenBus 市场"FLASH 自用套餐"挂售 GLM-5.3-Flash+**Qwen3.8-Flash**（2026-09-13 上架），系博文发布后平台跟进 |

信源：http://www.stdaily.com/web/gdxw/2026-08/03/content_558298.html 、http://zjnews.zjol.com.cn/zjnews/202608/t20260804_31825351.shtml 、https://ad.36kr.com/p/3937886846368898 、https://36kr.com/newsflashes/3956345253084296 、https://platform.qianwenai.com/docs/changelog/models 、https://www.aliyun.com/product/news/29909

**处置**：新增 F-035 记录正确值；bundle 概念文档凡涉及该句一律呈现正确口径（"博文写作 qwen-3.8，但该版本 08-03 才发布"），不照搬源文。

---

## 三、勘误四张清单过筛

| 清单 | 结果 |
|------|------|
| ① 日期/版本表 | ❌ 1 项：qwen-3.8 时间错位 + ID 写法不符（F-035）；✅ glm-5.2、✅ kimi-k3 |
| ② 成效数字溯源表 | 博文无提效倍数/工时/成本数字；标题"免费无限"按营销宣称处理，以实测供给（F-028）对照，不引用为能力承诺 |
| ③ 口径对照表 | "全球最顶级行列"标作者观点；平台运营数字（8 挂售/71 节点/2 在线/35 模型）全部标注核验时点 2026-09-16，为动态快照 |
| ④ 引文逐字核对表 | 博文无第三方引语/报告；"分包器""挖矿""注水放水池"均标作者比喻，不加引号作官方表述；腾讯云文章确认系原文转载而非媒体独立报道 |

## 四、核验局限

1. 钱包、建池、挂售结算、路由配置、节点注册、Community 群号等登录后页面未进入（未注册账号），相关结论基于公开页面文案、前端代码与公开 API，不代表登录后全链路已跑通。
2. GitHub 站内搜索与 Whois 存在反爬/验证码，"零独立信源/无主体"基于搜索引擎索引与公开页面，不等于穷尽全渠道。
3. 平台运营数据为 2026-09-16 单次快照，供给规模快速变化，引用时须带时点。
