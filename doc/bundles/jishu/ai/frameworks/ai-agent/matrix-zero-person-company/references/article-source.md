---
okf_version: "0.2"
type: Reference
title: "博文事实清单：Matrix 0人公司（智潮笔记）"
description: "智潮笔记博文《这个AI工具真的疯了！它可以帮你开一家0人公司》全文事实登记，F-001~F-046 共46条，含作者观点分层标注"
tags: [信源登记, Matrix, 0人公司, AI Agent, 事实清单]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-01T17:30:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/C5clrnoai50eneYvgP1nLw
    title: 《这个AI工具真的疯了！它可以帮你开一家"0人公司"，只需要一个想法，Agent就能自己去赚钱》（智潮笔记，2026-07-04）
---

# 博文事实清单（article-source）

## 博文元信息

| 编号 | 事实 | 级别 |
|------|------|------|
| F-001 | 博文标题《这个AI工具真的疯了！它可以帮你开一家"0人公司"，只需要一个想法，Agent就能自己去赚钱》 | P2 |
| F-002 | 公众号"智潮笔记"，发布于 2026-07-04 08:00，作者署名"智潮笔记" | P2 |
| F-003 | 博文性质：第三方自媒体产品介绍/评论文章，非 Matrix 官方发布 | P2 |

## 产品定位与接入

| 编号 | 事实 | 级别 |
|------|------|------|
| F-004 | Matrix 官网 slogan 为"让你的第一家Agent公司活起来"（博文转述） | P1 |
| F-005 | 博文认为 Matrix 定位不是又一个 Coding Agent，与 Claude Code、Codex、Cursor 不是竞争关系，反而可接入当"员工"用 | 作者观点 |
| F-006 | Matrix 内置 Neo Agent，原生接入 Claude Code、Codex、ChatGPT、Gemini，以及国产的 GLM、DeepSeek、Kimi、Qwen | P0 |
| F-007 | 还可用 OpenRouter key 或自己的 Claude Max/Pro 账号登录后接入 | P1 |
| F-008 | 博文认为 Matrix 的野心是做"一家公司的操作系统" | 作者观点 |
| F-018 | 博文称 Matrix 主要是一个 macOS 桌面应用，Web 端还没上线 | P1 |
| F-019 | 博文文末称可去 matrix.build 看看，目前 Web 版还没上，只有 macOS 版本 | P1 |

## Agent 公司架构与机制

| 编号 | 事实 | 级别 |
|------|------|------|
| F-009 | 博文示例：给 Matrix 一个目标（如"做一个短剧频道并且赚到钱"），内部会像一家真正的公司那样开始运转 | P1 |
| F-010 | 有一个 CEO Office 级别的 Agent 统筹全局，下面分出调研、工程、创意、增长、安全、运营这些部门 | P0 |
| F-011 | 每个部门有自己的领队 Agent，领队再判断是自己干，还是派给协作 Agent 干 | P0 |
| F-012 | 每个 Agent 都有自己的浏览器、工具、文件和记忆 | P0 |
| F-013 | Agent 会自己拆任务、自己推进、自己处理卡点，最后给出一个可以验证的结果 | P0 |
| F-014 | 记忆靠 durable work memory：每个目标、决策、交接、卡点和结果都留存在公司里 | P0 |
| F-015 | 协作靠统一的文件系统和跨 Agent 通信 | P0 |
| F-016 | 反馈靠 proof 机制：每个 Agent 必须交付可验证的结果，比如文件、截图、上线的页面、收入或者流量 | P0 |
| F-017 | 博文总结：分工（部门化和领队路由）、记忆（durable work memory）、协作（统一文件系统）、反馈（proof 机制）四件事被工程化 | 作者总结 |

## 案例与成效数字（厂商自宣）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-020 | 官网案例 AI 视频工作室 aivideopro.io：从定位、报价页面、作品展示、创作者流程，到 Stripe 收款、付费套餐、客户 brief intake，整条链路都接通 | P0 |
| F-021 | 生产端交付了 100 多条定制视频 | P0 |
| F-022 | 分发端有自动化 YouTube 频道，最高的短视频跑到 700k+ 播放 | P0 |
| F-023 | 有用户分享用 Matrix 跑通了能收到客户钱的广告服务流程；作者明确表示"没法验证具体细节，但这种模式本身是合理的" | P0（含作者免责声明） |
| F-024 | Agent Revenue 模块把 Stripe 收款、付费套餐、客户 intake 这些链路都接通，从技术上可以完成"收到钱"这个动作 | P0 |
| F-025 | GDPval-Bench 它跑出了 95.45%，超过 Codex CLI 的 84.9% 和 Claude Opus 4.7 的 80.3% | P0 |
| F-026 | 博文解读：这说明 Matrix 的 harness 工程很强，同样的模型放进它的系统里能发挥出更强的干活水平 | 作者解读 |

## 作者观点与叙事

| 编号 | 内容 | 级别 |
|------|------|------|
| F-027 | 博文开篇独立开发者故事：朋友用 Claude Code 一个周末做了小工具，GitHub star 不到 20，无人使用——"用 AI 做东西这件事，技术上已经没难度了。但把做出来的东西卖出去，这就太难了"（作者转述朋友吐槽） | P2（背景叙事） |
| F-028 | 博文论点：问题不是 AI 不够强，是 AI 只会帮你"造"，不会帮你"卖" | 作者观点 |
| F-029 | 博文认为 Matrix 把分工、记忆、协作和反馈四件事都工程化了，一家公司可以在没有人类员工的情况下运转 | 作者观点 |
| F-030 | 博文"泼冷水"：现在的 Matrix 远没到"躺着赚钱"的程度；能跑出什么结果很大程度上取决于目标是否清晰、懂不懂这门生意 | 作者观点 |
| F-031 | 博文认为这些赚到钱的人本身不是小白，懂社区、懂获客、懂客户心理；Matrix 帮他们干"费时间但不需要顶级创意"的脏活累活（持续生产内容、自动发布、跟进邮件、跑数据） | 作者观点 |
| F-032 | 博文认为真正的判断、审美还在人手里 | 作者观点 |
| F-033 | 博文"AI 三阶段论"：第一阶段 AI 能回答问题；第二阶段 AI 能帮你写代码、做东西；第三阶段 AI 能帮你把东西卖出去，跑通一门生意 | 作者观点 |
| F-034 | 博文论点：当 AI 把"造"的成本打到接近零，真正的竞争会转移到"运营"和"商业判断"上 | 作者观点 |
| F-035 | 博文认为 Matrix 让一个人拥有 7×24 不知疲倦的执行团队，但公司能否赚钱取决于坐在 CEO 位置上的人 | 作者观点 |
| F-036 | 博文认为可能的方向不是 AI 替代某个岗位，而是 AI 替代一整个公司的结构 | 作者观点 |
| F-037 | 博文对照：过去开公司需要租办公室、招人、发工资、跑注册、开银行账号；现在只需要一个想法和一台能跑 Matrix 的 Mac | 作者表述 |
| F-038 | 博文结论："0人公司"能否成为主流不知道，但确定 AI 不会只停留在帮造东西，迟早进入帮做生意、赚钱的阶段 | 作者观点 |

## 核验补充事实（WebSearch，2026-09-01）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-039 | Matrix 产品真实存在：多个第三方 AI 工具导航站收录——aigjdh.com（"专为超长周期自主运行而生的主动式多智能体协作平台"）、hotools.com（2026-06-23 收录，"agentic runtime for long-term autonomous operation / 0-person company"）、aitoolnet.com（"multi-layer agentic runtime"），定位描述与博文一致 | aigjdh.com/sites/2669.html；hotools.com/item/matrix；aitoolnet.com/matrix |
| F-040 | 第三方转录的官方架构描述与博文一致：CEO Office → OKR 记忆系统 → 并行部门（Research/Product/Growth/Engineering）→ Lead Agent（durable memory）→ Worker Agent（disposable）；Agential OKR 分层循环；共享文件系统跨部门交接；proof 机制（verifiable artifacts：文件/测试/截图/转录） | aitoolnet.com/matrix；aigjdh.com/sites/2669.html |
| F-041 | 模型接入列表与博文一致：Neo（自研）、Claude Code、Codex、ChatGPT、Gemini、GLM、DeepSeek、Kimi、Qwen——aitoolnet 与 hotools 两方转录一致 | aitoolnet.com/matrix；hotools.com/item/matrix |
| F-042 | 商业基建与 Revenue 能力与博文一致：预置域名部署（matrix.site 子域名）、Stripe 支付、Agent 钱包、邮件收发、广告账户、GitHub/Vercel/Docker 集成，绕过实体注册与银行开户；另发现博文未提的官方经济指标 VPTD（Value per Token-Dollar） | aitoolnet.com/matrix；hotools.com/item/matrix |
| F-043 | GDPval-Bench 95.45% 仅见于厂商自述（aitoolnet 转录官方文案），无独立第三方评测可溯源；Codex CLI 84.9% 与第三方评测（danilchenko.dev）中 GPT-5.5 GDPval 84.9% 数值吻合但口径无法确认；Claude Opus 4.7 GDPval 80.3% 无法独立溯源（Anthropic 官方 GDPval-AA 为 Elo 制，与百分比口径不同） | aitoolnet.com/matrix；danilchenko.dev/posts/gpt-5-5-review/ |
| F-044 | aivideopro.io 案例数字（100+ 定制视频、700k+ 播放，aitoolnet 转录另含 $3,000+ 收入）仅厂商自述；aigjdh 转述"已累计产生超过 70 万次真实播放"与 700k+ 一致；无独立第三方验证 | aitoolnet.com/matrix；aigjdh.com/sites/2669.html |
| F-045 | 同名产品排除：OpenAI 官网收录的 Hebbia "Matrix" 为金融/法律多智能体平台（o3-mini/o1/GPT-4o），与本产品无关；GitHub matrix-agent-neo/matrix-core 与 NeoLabs-Systems/NeoAgent 亦非本产品 | openai.com/index/hebbia/ |
| F-046 | macOS 桌面应用、Web 端未上线：三家第三方工具站均未提及平台形态，该声明仅博文单源，引用时需提示读者甄别 | 仅博文 |

## 可信度分层说明

| 等级 | 事实编号 | 说明 |
|------|---------|------|
| ✅ 已核验 | F-006, F-009~F-017, F-020, F-024 | 产品存在、架构机制、模型列表、商业基建经三方工具站转录交叉一致（F-039~F-042） |
| ⚠️ 厂商/客户自述 | F-021, F-022, F-025 | GDPval 95.45%、100+ 视频、700k+ 播放均无独立出处（F-043/F-044） |
| 📝 作者观点 | F-005, F-008, F-017, F-026, F-028~F-038 | 智潮笔记分析判断，非客观事实 |
| 单源声明 | F-018, F-019, F-046 | macOS/Web 形态仅博文提及 |
