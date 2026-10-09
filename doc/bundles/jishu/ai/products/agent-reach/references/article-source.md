---
okf_version: "0.2"
type: Reference
title: "Agent Reach 博文事实清单（信源登记）"
description: "微信公众号博文《9.2万星炸场：给AI装上眼睛》的 F 编号事实双份登记与官方核验状态（F-001~F-072，72 条）"
tags: [agent-reach, article-source, fact-registry, blog-article]
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-10-08T11:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: github-repo
    url: https://github.com/Panniantong/Agent-Reach
  - id: github-api
    url: https://api.github.com/repos/Panniantong/Agent-Reach
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
  - id: official-install
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
---

# 博文事实清单（article-source）

> 本文件是 F 编号事实的双份登记之一（另一份在 spec `facts.md`，两集合正则比对一致：F-001~F-072 连续无跳号，共 72 条）。
> 类型：O=客观事实，V=作者观点/评价，S=项目方（厂商）自述。核验：✅ 官方一致 ｜ ⚠️ 口径/时效差异（详见 [verification.md](verification.md)）｜ ➖ 无需外部核验。
> 博文：公众号「AI赋能干货铺」作者「学生小孙」，2026-10-06 15:03 发布，6833 字。F-001~F-054 出自博文，F-055~F-072 为 2026-10-07/08 官方核验补充。

## A. 博文元信息（F-001 ~ F-003）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-001 | O | 博文标题《9.2万星炸场：给AI装上眼睛，16个平台一个CLI全打通》，全文 6833 字，10 个编号小节 | ➖ |
| F-002 | O | 公众号「AI赋能干货铺」/作者「学生小孙」/原创/2026-10-06 15:03/IP 辽宁；文末"抽一位送咖啡"等互动引流 | ➖ |
| F-003 | O | 推介项目 Agent Reach，https://github.com/Panniantong/Agent-Reach（文内出现两次） | ✅ F-055 |

## B. 项目身份与热度（F-004 ~ F-007）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-004 | O | 信息卡：92,000+ Star；Python 3.10+；MIT；Star 约 92,000、Fork 约 8,000；16 渠道（6 个开箱即用）；2026 年 2 月首次发布、不到 8 个月 | 日期✅ F-055；数字⚠️ F-056；6/7口径⚠️ F-061 |
| F-005 | O | 定位概括："不是抓取工具，而是能力层——替你选型、安装、体检、路由" | ✅ F-057 |
| F-006 | O | Python 3.10+、MIT | ✅ F-059 |
| F-007 | V | "92k Star 的真正原因：它卖的不是功能，是'不用再操心'"；"维护动力来自自用而非流量" | ➖（作者归因，非可核验因果） |

## C. 痛点与能力层定位（F-008 ~ F-014）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-008 | O | 六平台门槛：YouTube 要 yt-dlp 且区分自动/手动字幕；Reddit 匿名接口封、API 审批制只剩登录态；B站通用工具被 412 拦死；小红书不登录打不开；GitHub 认证坑多；全网搜索付费/免费质量差 | B站412✅ F-064；其余与 README 描述一致 |
| F-009 | O/S | 引 README："这些不难实现，但是需要自己折腾配置"；痛点归纳"别让我每次都重来一次" | ✅ README |
| F-010 | O | 定位对比：同类项目做单平台抓取工具、寿命系于依赖路径；Agent Reach 不做抓取，只选型/安装/体检/路由，抓取由 Agent 直调上游，无包装层 | ✅ F-057/README |
| F-011 | O | 故障对比：传统模式等作者修；能力层调后端列表顺序，用户零操作 | ✅ F-064 |
| F-012 | S | 引 README："当下最稳的接入方式，我们替你选好、装好、体检好。接入方式会换代，你不用操心。" | ✅ README |
| F-013 | V | 作者架构翻译："易变的接入方式封装在稳定接口后面；变的是实现，不变的是入口和 16 个渠道名" | ➖ |
| F-014 | V | "能力层，不是第 17 个工具"是"最值得 AI 开发者学习的一点" | ➖ |

## D. 核心机制一：有序后端列表（F-015 ~ F-018）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-015 | O | channels/ 树示意 9 文件及后端链：web→Jina Reader；twitter→twitter-cli▸OpenCLI▸bird；youtube→yt-dlp；github→gh CLI；bilibili→bili-cli▸OpenCLI▸搜索 API；reddit→OpenCLI▸rdt-cli；xiaohongshu→OpenCLI▸xiaohongshu-mcp▸xhs-cli；rss→feedparser；exa_search→Exa via mcporter | ⚠️ 简化示意，实际规模 F-063 |
| F-016 | O | 每渠道维护有序候选后端列表；`active_backend` 字段上报当前实际后端；换接入方式=调列表顺序 | ✅ F-065/F-067 |
| F-017 | O | 可用环境变量（渠道名+`_backend` 形式）单独覆盖某渠道后端；改对应 channel 文件不影响其他渠道 | ✅ README |
| F-018 | V | 启示：上游会变就别写 if/else 分支，写有序候选列表+探测选主；"分支会随上游数量爆炸，列表不会" | ➖ |

## E. 核心机制二：doctor 真体检（F-019 ~ F-022）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-019 | V/O | 批评只做 `which xxx` 的体检；真实失败：shebang 失效、网络超时、登录态过期 | ➖（现象描述） |
| F-020 | O | probe.py 真跑上游命令三态：missing（没装→安装命令）、broken（跑不通如 shebang→重装处方）、timeout（超时→网络/凭据提示） | ✅ F-065 |
| F-021 | O | `agent-reach doctor --json`；JSON 中 active_backend 让 Agent 动手前知道调哪套命令 | ✅ F-065 |
| F-022 | V | "同一份诊断信息同时服务人和 Agent——文本给人、JSON 给 Agent；Agent 基建几乎都会走到这一步" | ➖ |

## F. 真实故障案例（F-023 ~ F-027）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-023 | O | 2026-06 B站风控升级，yt-dlp 拉 B站全面返回 412 | ✅ F-064 |
| F-024 | O | 应对：bilibili 后端列表 bili-cli▸OpenCLI▸搜索 API，yt-dlp 退役、bili-cli 顶上，用户零操作 | ✅ F-064 |
| F-025 | O/S | 转述 README 当前选型表：B站 bili-cli▸OpenCLI▸搜索 API（注"yt-dlp 被 B站风控 412 封死 2026-06 实测"）；Twitter twitter-cli▸OpenCLI▸bird；Reddit OpenCLI(桌面)▸rdt-cli；全网 Exa via mcporter 免 Key | ✅ README/F-060 |
| F-026 | O | 2026-03 一批单平台 CLI 集体停更，项目换了一轮路由；"不是意外，是常态" | ✅ F-064 |
| F-027 | V | 判断 Agent 基建项目要看 CHANGELOG 有没有"后端换了一轮但用户无感"的记录 | ➖ |

## G. 16 渠道三档（F-028 ~ F-033）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-028 | O | 16 渠道分三档：开箱即用/一句话解锁/需要登录态 | 16✅ F-060 |
| F-029 | O | 博文"开箱即用"列 **7** 个：网页、YouTube、GitHub、RSS/Atom、Exa、V2EX、B站——与头部"6 个"矛盾 | ⚠️ F-061 |
| F-030 | O | 一句话解锁 5 个：Twitter/X、雪球、小宇宙、LinkedIn、Boss直聘；对 Agent 说"帮我配 XXX"引导 | ✅ F-060 |
| F-031 | O | 需登录态 4 个：小红书、Reddit、Facebook、Instagram | ✅ F-060 |
| F-032 | O/V | 小红书链路不替用户登录、不读浏览器 Cookie，OpenCLI 只用用户已有且明确控制的会话；作者评"这个克制很少见" | ✅ README |
| F-033 | O/S | Cookie 平台务必专用小号；脚本调用有被检测限制风险；Cookie 等同完整登录权限 | ✅ F-068 |

## H. 安全设计（F-034 ~ F-039）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-034 | O | install 默认只读检查、不装包不写配置；动系统须显式 `--system`；`--dry-run` 列全部计划动作不改一字节 | ✅ F-065 |
| F-035 | O | 三命令：`install --env=auto`（检查）/`--dry-run`（预览）/`--system`（授权真装） | ✅ F-066 |
| F-036 | O | Cookie/Token 只存 `~/.agent-reach/config.yaml`，权限 600，不上传不外传 | ✅ F-065 |
| F-037 | O | uninstall 清配置目录/各 Agent skill 文件/MCP 配置；`--dry-run` 预览；`--keep-config` 留凭据 | ✅ F-065 |
| F-038 | O | 可插拔：换对应 channel 文件即替换组件，不影响其他渠道 | ✅ F-063/F-065 |
| F-039 | V | "默认只读+显式授权+dry-run 应成交给 Agent 的安装器标配，而不是加分项" | ➖ |

## I. SKILL.md 与一句话安装（F-040 ~ F-044）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-040 | O | 仓库放有给 AI Agent 的操作手册 SKILL.md：路由表、常用命令、重试链、失败规则、"动手前先 doctor --json 看 active_backend"纪律（博文语境为仓库根目录） | 功能✅；位置⚠️ F-062 |
| F-041 | O | 一句话安装话术（逐字）："帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md" | ✅ F-066 |
| F-042 | O | 人只说意图（"帮我看看这个链接""B站搜 XX"），Agent 自选 `bili search` 或 `curl r.jina.ai/URL` | ✅ F-067 |
| F-043 | O | SKILL.md 规则：大调研后顺手 `agent-reach check-update`，有新版在收尾汇报附一句 | ✅ F-062 |
| F-044 | V | "项目想被 Agent 用起来，缺的很可能不是 MCP server，而是 SKILL.md" | ➖ |

## J. 上手流程与命令（F-045 ~ F-048）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-045 | O | `pipx install https://github.com/Panniantong/agent-reach/archive/main.zip` + `agent-reach install --env=auto`；或把一句话话术发给 Claude Code/Cursor/OpenClaw | ⚠️ 出处仅 install.md，F-066 |
| F-046 | O | 装完 `agent-reach doctor` 体检；要某平台就说"帮我配 XXX" | ✅ F-065 |
| F-047 | O | 卸载：`uninstall --dry-run` 预览 → `uninstall` 真删 | ✅ F-065 |
| F-048 | O | 四零配置命令：`curl -s "https://r.jina.ai/URL"`、`gh search repos "query" --sort stars --limit 10`、`yt-dlp --write-sub --skip-download "URL"`、`bili search "AI 教程" --type video -n 5`；Windows python3 若开 Store 改用 `py -3` | ✅ F-067 |

## K. 五条设计启示与作者自述（F-049 ~ F-054）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-049 | V | 启示一："做能力层，不做工具层。价值不是'我实现了某件事'，而是'我知道当下谁实现得最好'。前者被上游变化打垮，后者不会。" | ➖ |
| F-050 | V | 启示二："有序候选列表 > 单一实现。换路线只是一次排序调整。" | ➖ |
| F-051 | V | 启示三："健康检查要'真跑'。missing/broken/timeout 处方完全不同。省这一步用户就要自己 debug。" | ➖ |
| F-052 | V | 启示四："同时给人给机器各一份输出。文本给人、JSON 给 Agent，Agent 基建几乎是必答题。" | ➖ |
| F-053 | V | 启示五："交付一份 SKILL.md。让 Agent 知道怎么用你的项目，比让人知道更重要。" | ➖ |
| F-054 | S/V | 引项目作者："这个项目我自己每天在用，所以我会一直维护它。"；推介作者归因"维护动力来自自用而非流量" | ✅ README 有此表述；归因为 V |

## L. 官方核验补充（F-055 ~ F-072，2026-10-07/08）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-055 | O | GitHub API：仓库真实，`created_at=2026-02-24T02:10:24Z`，main 分支，Python（617,420 字节为主），owner=User（显示名 Pnant，2020-11-04 注册，1,437 followers，38 仓库）；最近 commit 94f06c1（2026-10-07） | ✅ |
| F-056 | O | 时点快照 2026-10-07/08：Star **93,669→93,673**（93.7k）、Fork **8,195**、open issues 88、open PR 112、325 watching、36 贡献者；博文 92k/8k 均属实且现值更高 | ✅ 动态数字 |
| F-057 | O | About："Give your AI agent eyes to see the entire internet..."；topics：agent-infrastructure/ai-agent/mcp/claude-code/cursor；Trendshift 徽章 #24387 | ✅ |
| F-058 | O | Releases 共 7 个；最新 **v1.5.0「能力层:多后端路由 + 真体检 + OpenCLI」2026-06-11**（博文未提，补充） | ✅ |
| F-059 | O | MIT（LICENSE/API 一致）；Python 3.10+ | ✅ |
| F-060 | O | README 平台表 16 渠道：网页/YouTube/RSS/Exa/GitHub/Twitter-X/B站/Reddit/Facebook/Instagram/小红书/LinkedIn/Boss直聘/V2EX/雪球/小宇宙（xueqiu.py、v2ex.py 实际存在） | ✅ |
| F-061 | O | **零配置口径补正**：官方激活口径"默认只激活 6 个零配置渠道"；博文头部写 6、正文列 7（多 B站）；README 平台表 B站注"装好即用：搜索+详情 bili-cli 无需登录"——无需登录但不属默认激活 6 个（网页/YouTube/GitHub/RSS/Exa/V2EX） | ⚠️ |
| F-062 | O | **SKILL.md 路径勘误**：根目录不存在；实际 `agent_reach/skill/SKILL.md`，另有 SKILL_en.md 与 references/ 下 7 个分类 md；check-update 规则在其中 | ⚠️ |
| F-063 | O | **channels 规模勘误**：git tree 实际 channels/ 20 文件/17 渠道实现（__init__/_opencli_site/base + 17 个渠道 py：bilibili/boss/exa_search/facebook/github/instagram/linkedin/mcporter/reddit/rss/twitter/v2ex/web/xiaohongshu/xiaoyuzhou/xueqiu/youtube）；README 树图只画 13，漏 boss/v2ex/xueqiu/xiaoyuzhou；17 实现 vs 16 对外渠道存在 mcporter 承载 Exa 等内部映射 | ⚠️ |
| F-064 | O | 故障史核实：README 载"yt-dlp 被 B站风控 412 封死（2026-06 实测）"；设计理念段载 2026-03 单平台 CLI 停更换路由 | ✅ |
| F-065 | O | 安全机制核实：install 默认只读/`--dry-run`/`--system`（另 `--safe`/`--env=auto`）；config.yaml 600；uninstall 清 skill/MCP 配置 + `--dry-run`/`--keep-config`；probe 真探测；active_backend: null=无可用后端 | ✅ |
| F-066 | O | **安装命令出处补正**：pipx 命令与 install URL 逐字在 docs/install.md，raw URL 可访问；README 正文无 pipx 字样、主推"一句话发 Agent" | ⚠️ |
| F-067 | O | 零配置底层命令核实：r.jina.ai、gh search/repo view、yt-dlp、bili-cli、Exa via mcporter（MCP 免 Key）、feedparser；search-* 子命令族（search-twitter 默认 -n 10） | ✅ |
| F-068 | O | 登录态配置：Twitter 需 TWITTER_AUTH_TOKEN/TWITTER_CT0 环境变量；OpenClaw 需先 `openclaw config set tools.profile "coding"` 开 exec；官方建议服务器代理约 $1/月；Cookie 风险建议小号 | ✅ |
| F-069 | O | **PyPI 同名包警告**：官方明确不要从 PyPI 装同名包，以 GitHub archive/一句话安装文档为准 | ✅ |
| F-070 | O | **第三方镜像旧口径**：lobehub 镜像快照显示"13+ platforms"且含抖音/微博/微信文章，系旧版不采信；GitCode 有同步镜像 Panniantong/Agent-Reach，README 友链 AtomGit | ⚠️ 已标注 |
| F-071 | S | **商业化披露**：README 赞助商区块（BrowserAct/腾讯云 OpenClaw/CoreClaw/UCloud）；作者承接 Agent 落地业务合作（微信）；博文为第三方推介且有公众号引流 | ✅ 已登记 |
| F-072 | O | 增长旁证：neodrop.ai 载 2026-06-22 当周 GitHub Trending #2（36,854 stars，周增 +8,233），与 2 月发布→6 月爆发→10 月 93k 曲线吻合；另有 GitCode 博客（2026-09-24/25）、deepwiki 收录 | ✅ 第三方旁证 |

## 双份一致性核对

- 本文件 F 编号集合 = spec `facts.md` 集合 = {F-001 … F-072}，连续无跳号，共 72 条
- 类型分布：涉 V 观点标注 16 条（纯 V 13：F-007/F-013/F-014/F-018/F-022/F-027/F-039/F-044/F-049~F-053；复合 3：F-019 V/O、F-032 O/V、F-054 S/V）；涉 S 项目方自述 6 条（F-009/F-012/F-025/F-033/F-054/F-071）；其余为 O
- V 阶段补充事实：无（全部核验事实在 R 阶段一次性登记，双份回转完成）
