---
okf_version: "0.2"
type: Reference
title: "文章信源事实登记"
description: "Zhihu CLI 知识包信源事实底账，收录 F-001~F-150 共 150 条事实，与规划阶段 facts.md 保持双份一致。"
tags: ["信源事实", "F编号", "双份登记", "知乎开放平台", "Zhihu CLI"]
generated: 2026-09-04
verified: 2026-09-05
status: verified
stale_after: "2026-12-31"
sources:
  - "S1: 腾讯云开发者社区"
  - "S2: 觉醒AI博客"
  - "S3: 知乎官方开放平台 (developer.zhihu.com)"
  - "S4: 知乎问题页"
  - "S5: 老狼知乎专栏"
  - "S6: 老狼知乎回答"
  - "S7: 知乎开发者官方文档 (developer.zhihu.com/docs)"
---

# 文章信源事实登记

> 本文档为 Zhihu CLI 知识包的信源事实底账，与知识包规划阶段的 `facts.md` 保持双份一致（双份登记原则）。所有事实均带唯一 F 编号，知识包正文引用事实时须标注对应 F 编号以便溯源。
>
> **信源**：6 篇公开文章（S1 腾讯云开发者社区、S2 觉醒AI博客、S3 知乎官方开放平台、S4 知乎问题页、S5 老狼知乎专栏、S6 老狼知乎回答）
> **信源距离**：S3 = 官方发布；S1/S2/S5/S6 = 作者一手实测；S4 = 社区讨论
> **标记说明**：📝 标注为作者观点；[厂商自述] 标注为官方/厂商自述数据，列为 P0 待核验

---

## 一、平台定位（F-001~F-010）

| 编号 | 事实内容 | 来源 | 分类 |
|------|----------|------|------|
| F-001 | Zhihu CLI 是知乎数据开放平台给 AI Agent 提供的官方命令行工具 | S1、S2、S5 | 平台定位 |
| F-002 | 知乎数据开放平台提供全链路数据产品矩阵，包含知乎海量优质专业内容 | S3 | 平台定位 |
| F-003 | 知乎数据开放平台核心产品包括：全网搜索、知乎搜索、直答 Agent、工具、社区数据、知识库 | S3 | 平台定位 |
| F-004 | Zhihu CLI 最大价值在于：公共内容 + 个人数据同时交到 AI 手中 | S6 📝 作者观点 | 平台定位 |
| F-005 | 知乎数据开放平台处于邀测阶段 | S3 | 平台定位 |
| F-006 | 邀测阶段免费试用额度为 5000 次/天 [厂商自述] | S3 | 平台定位 |
| F-007 | 知乎数据开放平台提供 L1-L5 内容分级体系以保障内容质量 [厂商自述] | S3 | 平台定位 |
| F-008 | 知乎平台汇聚了大量专业创作者 [厂商自述] | S3 | 平台定位 |
| F-009 | Zhihu CLI 技能已更新到 v0.5.0 | S4 回答2 | 平台定位 |
| F-010 | Zhihu CLI 支持 Linux 平台 | S4 回答2 | 平台定位 |

## 二、产品能力（F-011~F-030）

| 编号 | 事实内容 | 来源 | 分类 |
|------|----------|------|------|
| F-011 | Zhihu CLI 核心能力包括：搜索知乎、搜索全网、知乎热榜、知乎直答、我的创作、我的关注、我的收藏 | S1 | 产品能力 |
| F-012 | 全网搜索能力：百亿索引、全网+知乎双源融合、实时分钟级索引、平均响应延迟 600ms [厂商自述] | S3 | 产品能力 |
| F-013 | 常用命令：search（知乎/全网搜索）、trending（热榜）、ask（直答）、quota（额度查询） | S2 | 产品能力 |
| F-014 | CLI 命令：search zhihu/global、hot、answer（流式）、me contents/followees/favorites | S5 | 产品能力 |
| F-015 | search 命令支持两种范围：zhihu（知乎站内搜索）和 global（全网搜索） | S2、S5 | 产品能力 |
| F-016 | hot / trending 命令用于获取知乎热榜 | S2、S5 | 产品能力 |
| F-017 | ask / answer 命令用于知乎直答，支持流式输出 | S2、S5 | 产品能力 |
| F-018 | me 命令组包含三个子命令：contents（我的创作）、followees（我的关注）、favorites（我的收藏） | S1、S5 | 产品能力 |
| F-019 | quota 命令用于查询额度使用情况 | S2 | 产品能力 |
| F-020 | 支持接入知乎直答知识库 | S4 回答2 | 产品能力 |
| F-021 | 支持查询体验额度 | S4 回答2 | 产品能力 |
| F-022 | 输出约定：stdout 输出 JSON，stderr 输出诊断信息，错误返回稳定 JSON 错误码 | S5 | 产品能力 |
| F-023 | answer（直答）命令支持流式输出 | S5 | 产品能力 |
| F-024 | 知乎直答 Agent 是平台核心产品之一 [厂商自述] | S3 | 产品能力 |
| F-025 | 工具类产品是平台核心产品之一 [厂商自述] | S3 | 产品能力 |
| F-026 | 社区数据类产品是平台核心产品之一 [厂商自述] | S3 | 产品能力 |
| F-027 | 知识库类产品是平台核心产品之一 [厂商自述] | S3 | 产品能力 |
| F-028 | 全网搜索为分钟级实时索引更新 [厂商自述] | S3 | 产品能力 |
| F-029 | 全网搜索平均响应延迟 600ms [厂商自述] | S3 | 产品能力 |
| F-030 | 全网搜索为百亿级索引规模 [厂商自述] | S3 | 产品能力 |

## 三、安装配置（F-031~F-050）

| 编号 | 事实内容 | 来源 | 分类 |
|------|----------|------|------|
| F-031 | 安装流程：将 Skill 发给 Agent → 自动下载安装 CLI → 生成 Access Secret → 完成验证 | S1 | 安装配置 |
| F-032 | 注册步骤：打开 developer.zhihu.com → 知乎账号登录 → 完成实名认证 → 获取 Access Secret | S2 | 安装配置 |
| F-033 | 官方推荐使用 uv 安装 CLI | S2 | 安装配置 |
| F-034 | 也可使用社区封装的 zhihu-search 工具（作者 klarkxy） | S2 | 安装配置 |
| F-035 | Access Secret 存储在 macOS Keychain 或 Windows Credential Manager 中 | S1 | 安装配置 |
| F-036 | Secret 存进 Windows 凭证库，无明文存储 | S5 | 安装配置 |
| F-037 | 两种接入方式：Skill + CLI 组合、托管式 MCP 服务，共用同一套接口和 Access Secret | S5 | 安装配置 |
| F-038 | Skill 是 42KB 纯文本压缩包 | S5 | 安装配置 |
| F-039 | CLI 是二进制可执行文件 | S5 | 安装配置 |
| F-040 | Windows 安装坑：PowerShell 5.1 对 UTF-8 无 BOM 编码的 .ps1 文件会报解析错误 | S5 | 安装配置 |
| F-041 | 支持多种 Agent 集成方式：Codex、Claude Code、Cursor | S2 | 安装配置 |
| F-042 | 每种 Agent 均支持 Skill 和 MCP 两种接入方式 | S2 | 安装配置 |
| F-043 | 鉴权方式：Bearer Token + X-Request-Timestamp 秒级时间戳双重校验 [厂商自述] | S3 | 安装配置 |
| F-044 | 获取 Access Secret 需要先完成实名认证 | S2 | 安装配置 |
| F-045 | Access Secret 是调用开放平台接口的凭证 | S1、S2、S5 | 安装配置 |
| F-046 | 调用链路：自然语言 → AI 按 Skill 指令调用 CLI → CLI 带 Access Secret 请求开放平台 → 返回 JSON → AI 整理 | S5 | 安装配置 |
| F-047 | Skill + CLI 组合方式和托管式 MCP 服务共用同一套 Access Secret | S5 | 安装配置 |
| F-048 | 官方开放平台网址：developer.zhihu.com | S2、S3 | 安装配置 |
| F-049 | 登录知乎开放平台使用知乎账号 | S2 | 安装配置 |
| F-050 | CLI 安装过程由 Agent 自动完成下载和配置 | S1 | 安装配置 |

## 四、技术架构（F-051~F-060）

| 编号 | 事实内容 | 来源 | 分类 |
|------|----------|------|------|
| F-051 | 调用链路：自然语言 → AI 按 Skill 指令调用 CLI → CLI 带 Access Secret 请求开放平台 → 返回 JSON → AI 整理 | S5 | 技术架构 |
| F-052 | 输出约定：stdout JSON，stderr 诊断信息，错误返回稳定 JSON 错误码 | S5 | 技术架构 |
| F-053 | Skill 是 42KB 纯文本压缩包，包含调用指令规范 | S5 | 技术架构 |
| F-054 | CLI 是二进制可执行文件，负责实际的 API 调用 | S5 | 技术架构 |
| F-055 | 两种接入方式（Skill+CLI 和 MCP）共用同一套后端接口 | S5 | 技术架构 |
| F-056 | 全网搜索采用全网+知乎双源融合架构 [厂商自述] | S3 | 技术架构 |
| F-057 | 全网搜索为实时分钟级索引更新机制 [厂商自述] | S3 | 技术架构 |
| F-058 | 鉴权采用 Bearer Token + 秒级时间戳双重校验机制 [厂商自述] | S3 | 技术架构 |
| F-059 | answer 命令支持流式输出（SSE/流式响应） | S5 | 技术架构 |
| F-060 | CLI 与开放平台通过 HTTPS 通信（隐含于安全设计中） | S1、S5 | 技术架构 |

## 五、安全设计（F-061~F-070）

| 编号 | 事实内容 | 来源 | 分类 |
|------|----------|------|------|
| F-061 | 官方 first-party 技能，HTTPS-only 下载 | S1 | 安全设计 |
| F-062 | 供应链安全四道校验：官方域名、文件大小、SHA-256、二进制自报版本 | S5 | 安全设计 |
| F-063 | SHA-256 + 文件大小 + 版本三重校验 | S1 | 安全设计 |
| F-064 | Access Secret 存储在系统凭证管理中（macOS Keychain / Windows Credential Manager），无明文存储 | S1、S5 | 安全设计 |
| F-065 | 安全审计结论为 P2/安全 | S1 | 安全设计 |
| F-066 | 鉴权方式：Bearer Token + X-Request-Timestamp 秒级时间戳双重校验 [厂商自述] | S3 | 安全设计 |
| F-067 | 下载源为官方域名，确保供应链可信 | S5 | 安全设计 |
| F-068 | 文件大小校验作为供应链安全措施之一 | S5 | 安全设计 |
| F-069 | 二进制自报版本校验作为供应链安全措施之一 | S5 | 安全设计 |
| F-070 | SHA-256 哈希校验作为供应链安全措施之一 | S1、S5 | 安全设计 |

## 六、实战玩法（F-071~F-095）

| 编号 | 事实内容 | 来源 | 分类 |
|------|----------|------|------|
| F-071 | 玩法一：创作生涯全身体检——全量拉取分析个人创作数据 | S6 | 实战玩法 |
| F-072 | 老狼知乎创作 9 年、430 篇文章，可通过 CLI 全量拉取分析 | S6 | 实战玩法 |
| F-073 | 创作数据分析可产出：各年产量分布图、历年赞同收藏累计图、创作方向分布图、赞同×收藏散点图 | S6 | 实战玩法 |
| F-074 | 玩法二：把写作风格提炼成 Skill——全量正文作为专属语料 | S6 | 实战玩法 |
| F-075 | 风格蒸馏可提炼：论证结构、段落长度、术语密度、惯用类比、开头结尾方式 | S6 | 实战玩法 |
| F-076 | 玩法三：选题雷达——热榜替你盯梢，定时跑 hot 命令拉热榜，与个人创作领域标签匹配 | S6 | 实战玩法 |
| F-077 | 让 Agent 读取分析自己过去积累的知乎内容是最有价值的玩法之一 | S4 回答1 📝 作者观点 | 实战玩法 |
| F-078 | 可分析创作领域、统计互动数据 | S4 回答1 | 实战玩法 |
| F-079 | 可蒸馏写作风格成 Skill | S4 回答1、S4 回答3 | 实战玩法 |
| F-080 | 老狼知乎创作 15 年约 49 万字内容（S4 回答3数据，与 S6 的 9 年/430 篇表述存在差异） | S4 回答3 | 实战玩法 |
| F-081 | AI loop engineering 思路可应用于 CLI 数据使用 | S4 回答3 📝 作者观点 | 实战玩法 |
| F-082 | 可做智能硬件看板 | S4 回答2 📝 作者观点 | 实战玩法 |
| F-083 | 可定时推送热榜到飞书 | S4 回答2 | 实战玩法 |
| F-084 | 公共内容 + 个人数据结合的玩法具有独特价值 | S6 📝 作者观点 | 实战玩法 |
| F-085 | 创作数据分析维度包括：年产量、赞同数、收藏数、创作方向分类 | S6 | 实战玩法 |
| F-086 | 赞同×收藏散点图可用于识别高价值内容 | S6 📝 作者观点 | 实战玩法 |
| F-087 | 风格蒸馏需要全量正文作为语料输入 | S6 | 实战玩法 |
| F-088 | 选题雷达玩法需要定时任务 + 热榜数据 + 个人标签匹配 | S6 | 实战玩法 |
| F-089 | 个人创作数据可通过 me contents 命令获取 | S1、S5、S6 | 实战玩法 |
| F-090 | 热榜数据可通过 hot/trending 命令获取 | S1、S2、S5 | 实战玩法 |
| F-091 | 知乎直答可用于快速获取问题答案 | S1、S2、S5 | 实战玩法 |
| F-092 | 全网搜索可用于获取更广泛的信息来源 | S2、S3、S5 | 实战玩法 |
| F-093 | 我的关注数据可通过 me followees 命令获取 | S1、S5 | 实战玩法 |
| F-094 | 我的收藏数据可通过 me favorites 命令获取 | S1、S5 | 实战玩法 |
| F-095 | 用 CLI 数据蒸馏自己的写作 Skill 是一种被多位作者提到的玩法 | S4 回答1、S4 回答3、S6 | 实战玩法 |

## 七、生态集成（F-096~F-105）

| 编号 | 事实内容 | 来源 | 分类 |
|------|----------|------|------|
| F-096 | 支持 Codex Agent 集成 | S2 | 生态集成 |
| F-097 | 支持 Claude Code Agent 集成 | S2 | 生态集成 |
| F-098 | 支持 Cursor Agent 集成 | S2 | 生态集成 |
| F-099 | 每种 Agent 均支持 Skill 和 MCP 两种接入方式 | S2 | 生态集成 |
| F-100 | 托管式 MCP 服务是接入方式之一 | S5 | 生态集成 |
| F-101 | Skill + CLI 组合是接入方式之一 | S5 | 生态集成 |
| F-102 | 两种接入方式共用同一套接口和 Access Secret | S5 | 生态集成 |
| F-103 | 社区有第三方封装的 zhihu-search 工具（作者 klarkxy） | S2 | 生态集成 |
| F-104 | 可与飞书等工具集成实现定时推送 | S4 回答2 | 生态集成 |
| F-105 | 可用于智能硬件看板等场景 | S4 回答2 📝 作者观点 | 生态集成 |

---

## 八、官方 API 接口规范（F-106~F-135）

> 本章节事实均来自 S7 知乎开发者官方文档（developer.zhihu.com/docs），为一手官方权威信源，标记为 [官方文档验证]。

| 编号 | 事实内容 | 来源 | 分类 |
|------|----------|------|------|
| F-106 | 官方 API 采用 Bearer Token 鉴权 + X-Request-Timestamp 秒级时间戳双重校验机制 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-107 | 知乎搜索 API URL: https://developer.zhihu.com/api/v1/zhihu_search/query，POST JSON 入参 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-108 | 全网搜索 API URL: https://developer.zhihu.com/api/v1/global_search/query，POST JSON 入参 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-109 | 知乎热榜 API URL: https://developer.zhihu.com/api/v1/hot_list/query，POST JSON 入参 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-110 | 知乎直答 API URL: https://developer.zhihu.com/v1/chat/completions，POST JSON 入参 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-111 | 额度查询 API URL: https://developer.zhihu.com/api/v1/quota，POST JSON 入参 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-112 | 统一额度体系共 7 项：global_search、zhihu_search、hot_list、user_data、zhida_openai、knowledge、tools | S7 [官方文档验证] | 官方 API 接口规范 |
| F-113 | 额度为日额度，自然日重置；额度查询本身不消耗业务额度 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-114 | 知识库系列（上传/列表/内容列表/检索）共用 knowledge 一个日额度池 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-115 | 工具系列（PDF 解析/PPT 生成）共用 tools 一个日额度池 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-116 | 知乎搜索 API 必填参数：Query（关键词） | S7 [官方文档验证] | 官方 API 接口规范 |
| F-117 | 知乎搜索 API 可选参数：Count（返回数，默认10，最大20）、Offset（偏移量） | S7 [官方文档验证] | 官方 API 接口规范 |
| F-118 | 全网搜索 API 支持 Filter 筛选语法：支持 host、publish_time 字段，AND/OR 逻辑，括号优先级 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-119 | 全网搜索 Filter 中不支持 host=="zhihu.com" 及其子域名，站内搜索请用 zhihu_search 接口 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-120 | 全网搜索 API 可选 SearchDB 参数：all（默认）/ realtime（实时库）/ static（静态库） | S7 [官方文档验证] | 官方 API 接口规范 |
| F-121 | 热榜 API Limit 默认 30，最大 30，<=0 或 >30 自动回退为 30 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-122 | 热榜仅返回问题和文章两类内容；无封面时 ThumbnailUrl 为空字符串 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-123 | 直答 API 必填参数：model（模型）、messages（消息列表） | S7 [官方文档验证] | 官方 API 接口规范 |
| F-124 | 直答 API 可选参数：stream（是否流式，默认 false） | S7 [官方文档验证] | 官方 API 接口规范 |
| F-125 | 直答提供 3 档模型：zhida-fast-1p5（快速）、zhida-thinking-1p5（深度思考带 reasoning_content）、zhida-agent（Agent 模式） | S7 [官方文档验证] | 官方 API 接口规范 |
| F-126 | MCP over SSE 架构：SSE 端点建立连接，返回 endpoint 事件（含 sessionId 的 message 地址），请求通过 message 端点发送 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-127 | MCP 服务当前仅提供 tools 能力，不提供 resources 和 prompts 能力 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-128 | MCP message 端点返回 HTTP 202 Accepted，实际响应通过 SSE 异步送达 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-129 | MCP 工具调用结果为 text 类型，正文为面向大模型消费的 XML 格式文本 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-130 | 每个核心能力都有独立 MCP 端点：zhihu_search、global_search、zhida、hot_list | S7 [官方文档验证] | 官方 API 接口规范 |
| F-131 | MCP 接入四步：1 建立 SSE 连接 → 2 initialize → 3 tools/list → 4 tools/call | S7 [官方文档验证] | 官方 API 接口规范 |
| F-132 | 直答流式响应（SSE）：data: {...} 逐块返回，data: [DONE] 结束，含 : keep-alive 心跳 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-133 | 官方 API 错误码：40001 参数错误、40101 鉴权失败、40301 额度不足、40401 资源不存在、50001 服务内部错误 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-134 | 官方 API 鉴权头：Authorization: Bearer <access_secret>，X-Request-Timestamp: <秒级时间戳> | S7 [官方文档验证] | 官方 API 接口规范 |
| F-135 | 直答非流式响应包含 reasoning_content（推理过程）和 content（最终回答）字段 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-136 | 知乎 OAuth 服务用于集成知乎第三方登录与获取授权用户的个人信息；仅使用通用 API 和本人数据无需接入 OAuth | S7 [官方文档验证] | 官方 API 接口规范 |
| F-137 | 知乎 OAuth API 采用标准 OAuth 2.0 Authorization Code Flow | S7 [官方文档验证] | 官方 API 接口规范 |
| F-138 | 接入 OAuth 需要申请 app_id 和 app_key，申请邮箱 openplatform@zhihu.com | S7 [官方文档验证] | 官方 API 接口规范 |
| F-139 | authorization_code 的交换和 access_token 的使用应在应用后端完成，避免泄露 app_key 和用户令牌 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-140 | 用户内容 API：/api/v1/user/contents，获取用户创作内容（回答/文章/视频/想法/问题），支持分页和排序 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-141 | 用户数据 API 支持 X-OAuth-Token 请求头：不传时查询本人数据，传入时查询已授权用户数据 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-142 | 用户关注 API：/api/v1/user/followees，获取用户关注列表，支持分页（默认20，最大50） | S7 [官方文档验证] | 官方 API 接口规范 |
| F-143 | 用户收藏 API：/api/v1/user/collections，获取近期收藏内容，包含 FavTime、Favlists 收藏夹列表、Author 作者信息 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-144 | 用户收藏夹列表 API：/api/v1/user/favlists，获取收藏夹列表（UrlToken/Title/Description/IsPublic） | S7 [官方文档验证] | 官方 API 接口规范 |
| F-145 | 收藏夹内容 API：/api/v1/user/favlist_contents，获取指定收藏夹内容，FavlistUrlToken 为必填参数，支持分页 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-146 | 用户数据 API 统一错误码：0成功/10001参数错误/20001鉴权失败/30001频率限制/30002配额限制/90001内部错误 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-147 | 用户内容 API 支持 6 种内容类型：all/answer/article/zvideo/pin/question | S7 [官方文档验证] | 官方 API 接口规范 |
| F-148 | 用户内容 API 支持按 like_count（点赞数）或 ts（时间）排序，支持 asc/desc 方向 | S7 [官方文档验证] | 官方 API 接口规范 |
| F-149 | 收藏内容 Item 统一结构：ContentType/Url/CreatedAt/FavTime/LikeCount/CommentCount/FavoriteCount/Title/Summary/Favlists/Author | S7 [官方文档验证] | 官方 API 接口规范 |
| F-150 | 所有用户数据 API 均归属 user_data 额度项，共用一个日额度池 | S7 [官方文档验证] | 官方 API 接口规范 |

---

## 统计

- 总计 **150 条**事实（F-001 ~ F-150 连续无跳号）
- 分类分布：
  - 平台定位：10 条（F-001~F-010）
  - 产品能力：20 条（F-011~F-030）
  - 安装配置：20 条（F-031~F-050）
  - 技术架构：10 条（F-051~F-060）
  - 安全设计：10 条（F-061~F-070）
  - 实战玩法：25 条（F-071~F-095）
  - 生态集成：10 条（F-096~F-105）
  - 官方 API 接口规范：45 条（F-106~F-150）
- 📝 作者观点：约 10 条
- [厂商自述]：约 15 条
- ✅ [官方文档验证]：45 条
