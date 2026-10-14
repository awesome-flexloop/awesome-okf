# 变更日志

## 2026-10-14 - 初始版本

- ✅ 按方法论编排知识沉淀链路 `R→I→E→V` 完成（七概念场景 4：知识沉淀；版本发布资讯骨架，承接同分组 5.0.10 束时效线）。
- ✅ 内容敏感度预检：公开官方页面（`work.weixin.qq.com` 无访问控制参数），走标准工作流；spec 位于主仓 `.trae/specs/okf-wiki-ecosystem/wecom-5-0-12-release-okf-wiki/`（spec.md/facts.md/tasks.md，Review 后补 review.md）。
- ✅ 信源获取：WebFetch 直接提取官方 5.0.12 发布页（W）成功；核验信源 O1～O10——O1 上证报 cnstock 802000（操子怡，2026-10-14 13:23，唯一独立采写稿）；O2 央广网（稿尾自标「商业信息」通稿位）；O3 36 氪快讯；O4 每经快讯；O5 腾讯新闻鞭牛士；O6 官方 AI 开放能力页 aicli（核验时仍 11 模块、无幻灯片）；O7 微信派推文头条镜像；O8 WorkBuddy 官方 changelog（最新仅 5.7.7/2026-10-08）；O9 开发者文档 path/101906（JS 渲染仅取得上下篇导航，未取得正文，不编造标题）；O10 三个官方规则页（privacy 等仅登记链接）。
- ✅ 登记事实 F-001～F-051（35 条发布页事实 F-001～F-035 + 16 条核验补充 F-036～F-051），编号连续；**F-049 为「存疑不录」行**（2026-10-12 页面快照无法复现），标 ❔ 保留编号维持连续；spec `facts.md` 与本束 `references/article-source.md` 双份 F 编号集合机械比对一致（各 51 个）。
- ✅ 四类必须分层的口径全部落实：①WorkBuddy 5.8.0/十大能力仅同源通稿、官方 changelog 止于 5.7.7、能力举例三处不一（网盘/日程微盘/邮件）；②幻灯片 CLI/MCP 系发布页宣布、O6 未列，按「前瞻口径」禁写「已可调用」；③智能表格 AI 报告 5.0.10 标注灰度、5.0.12 标注消失但未官宣 GA，只陈述标注消失；④机器人两入口（侧边栏领用 + 通讯录找到）媒体各取一面。灰度两项：频道、IP 访问限制文档场景；单源清单见 F-045；规模数字（1400 万企业/7.5 亿用户/2000 万访问量/50+）均媒体转引（F-038～F-040），发布页零成效数字；发布直播 2026-10-15 15:00（F-051）。
- ✅ 无核心声明证伪，status 定 `stable`，`stale_after: 2027-01-31`。
- ✅ 操作可复现性两问判定为「否」（版本资讯非操作教程），不设 `examples/`；生成 4 篇 concepts（事件/机制/产品/治理四层）、2 篇 references、2 个子目录索引、根索引与本日志（共 10 个文件）。
- ✅ 归属 `jishu/ai/ecosystems/tencent/wecom-5-0-12-release/`；索引接入：tencent 分组 index 12→13 束、93→97 概念、52→54 信源、事实 1555→**1619**（按各束 `references/` 与 `spec/facts.md` 登记文件 F 编号并集机械复算；复算发现旧投影 1555 相对逐束并集 1568 已有 13 条历史漂移，本次一并校正并在该页计数段注明口径）；ecosystems 类索引表内 tencent 12→13、本类已登记口径 87→88；jishu/ai/index.md 240→241（ecosystems 88→89）；jishu/index.md ai 描述 240→241；bundles 总索引 jishu 469→470、ai 行 240→241。
- ✅ 总索引 total_bundles 落为 **634**：本束 +1，工作期间并行会话另向 sheke/ 新增 1 束（目录树真值由 633 变 634，sheke 节标题/分组表/mermaid 66→67 由该并行会话自行改入）；本任务只机械对齐 frontmatter 与计数行，未触碰 sheke 任何文件。
- ✅ 互链：5.0.10 束 index「主题关联」段 +1 行回链（最小改动）；本束根 index 与概念篇向 5.0.10 束的跨束链接经机械 Test-Path 全存活（concepts/ 内链接深度为 `../../`，门禁曾抓出误用 `../` 的 4 处断链并已修复）。
- ✅ 门禁：`python scripts/check-bundles-index.py` 终采通过（9 域/61 组/634 束，五面一致）；`python scripts/check-utf8.py` 通过（初采 11555 文件、R1 复跑 11556，+1 为并行会话新增文件，门禁均绿）；`check-toctrees.py` 全量运行存在 81 处既有/并行在途污染（deepseek-harness、agent-self-evolution-evaluation、microsoft-mxc-agent-containment 等束未接入导航，与本束无关），过滤 `wecom-5-0-12` 复检零命中；束内机械门禁（F 双份集合、全部相对链接 Test-Path、零 file 协议绝对链接（`file`+三斜杠形态）/零本机绝对路径、frontmatter 必填键、无 examples/）全部通过。
- ⚠️ 观测记录（不扩大修复，非本束引入）：工作树存在并行会话在途束（hwe-bench、kylin-wayland-compositor、sheke 新增束等）及其索引改动，本任务未触碰其内容文件，仅在总索引计数面按目录树真值做最小对齐。
- ⚠️ `invoke gates.*` 未运行（子项目可选文档依赖 invocations 未确认安装）；已直接运行底层门禁脚本（check-bundles-index/check-utf8/check-toctrees）并完成 F 双份、相对链接、frontmatter、禁用路径等手动等效机械核对。
- ✅ 独立对抗评审 R1（fresh-context 只读子代理，独立 WebFetch 复核 W/O1/O6/O8/O9 共 5 个 URL）结论 `pass`：CP-R1～R5 全过、CP-U1/U2 双 5 分，无 P0/P1；Advisory 6 项中 A-1～A-5 已收口（概念 01 补「领用入口 2 个 vs 使用面 3 个」口径划界、CLI 11 模块句改「截至 5.0.12 核验时」、两处 Mermaid 节点补 F-036/F-037、tencent 导航行与 5.0.10 回链统一官方名「对外管理」与「双领用入口」、utf8 文件数 11555→11556 注明并行来源），A-6（O10 根 sources 仅列 privacy 一个 URL、W 页概览/详情邮件微差）经评为非错误、保持现状；收口后已在无写入窗口复跑 check-bundles-index 终采通过。
