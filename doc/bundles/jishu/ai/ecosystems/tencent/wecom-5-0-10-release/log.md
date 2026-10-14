# 变更日志

## 2026-10-14 - 初始版本

- ✅ 按方法论编排知识沉淀链路 `R→I→E→V` 完成（七概念场景 4：知识沉淀；技术综述/版本发布资讯骨架）。
- ✅ 内容敏感度预检：公开官方页面（`work.weixin.qq.com` 无访问控制参数），走标准工作流；spec 位于主仓 `.trae/specs/okf-wiki-ecosystem/wecom-5-0-10-release-okf-wiki/`。
- ✅ 信源获取：WebFetch 直接提取官方发布页成功（未触发浏览器回退）。
- ✅ 登记发布页事实 F-001～F-018；P0 核验补充 F-019～F-033（共 33 条，连续无跳号），spec `facts.md` 与本束 `references/article-source.md` 双份编号集合一致。
- ✅ P0 核验：发布时间锚定 IT之家 2026-08-18（F-019）；官方 AI 开放能力页（O1）确认 CLI/MCP 与 11 模块现状；npm 注册表确认 `@wecom/cli`（MIT、WecomTeam/wecom-cli、v1.3.4，F-024）；官网逐字旁证大圆与智能文档更新（F-028/F-029）；上证报等锚定 5.0.12 于 2026-10-14 接替（F-031）。
- ✅ 无核心声明证伪，status 定 `stable`；3 类口径提示分层落实：①模块数 7（发布页）/10（IT之家概括）/11（当前官方页）时点差（F-027）；②安装命令大小写 wecomTeam/WecomTeam/WeComTeam 与 canonical（F-025）；③F-016 单源、F-026 媒体转述已标注。源页无成效数字，勘误清单第②张不适用。
- ✅ 操作可复现性两问判定为「否」，不设 `examples/`；生成 3 篇 concepts、2 篇 references、2 个子目录索引、根索引与本日志（共 9 个文件）。
- ✅ 归属 `jishu/ai/ecosystems/tencent/wecom-5-0-10-release/`；更新 tencent 分组 index（11→12 束；90→93 概念、50→52 信源、1522→1555 事实）、ecosystems 类索引（86→87 已登记口径）、jishu/ai/index.md（六类按目录树真值同步为 88/85/20/32/9/6＝240）、jishu/index.md（ai 239→240）、bundles 总索引（631→632，jishu 468→469，ai 239→240）。
- ✅ 门禁：`python scripts/check-bundles-index.py` 通过（9 域/61 组/632 束，五面一致）；`python scripts/check-utf8.py` 通过（11536 文件）；`check-toctrees.py` 全量基线在本会话开工前即已被其他在途工作污染（91 项：deepseek-harness、agent-self-evolution-evaluation、microsoft-mxc-agent-containment、wifit3 等束未接入导航），与本束无关；本束已接入 tencent 分组 toctree，BFS 可达性经过滤复检无本束相关项。
- ⚠️ 观测记录（不扩大修复，非本束引入）：①`ecosystems/index.md` 登记 15 目录/87 束，目录树真值 16 目录/88 束，差为历史束 deepseek-harness 未接入该类导航（本束按已登记口径 +1，并在该页加注口径说明）；②products 类索引历史计数 29 束 vs 目录树 32 束，本次在 ai/index.md 按目录树真值校正为 32；③工作树存在并行会话新增束（kylin-agent-runtime、hwe-bench、kylin-wayland-compositor）及其索引改动，本任务未触碰其文件。
- ⚠️ `invoke gates.*` 未运行（子项目可选文档依赖 invocations 未确认安装）；已直接运行底层门禁脚本（check-bundles-index/check-utf8/check-toctrees）并完成相对链接、双份 F 编号等手动等效核对。
- ✅ 独立对抗评审 R1（fresh-context 只读子代理）结论 `pass`：CP-R1～R5 全过、CP-U1/U2 双 5 分；按 advisory 收口两项——概念 00/02 frontmatter 补 O1 信源、verification.md 的 verified actor 统一为 process:seven-concepts-v；提交前应在无并行会话写入时复跑 check-bundles-index 锁定计数。
