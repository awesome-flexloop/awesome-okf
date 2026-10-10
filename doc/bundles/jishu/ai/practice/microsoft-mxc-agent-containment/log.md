# 变更日志

## 2026-10-10

- **创建**：生成 `microsoft-mxc-agent-containment` bundle，将腾讯科技博文《微软给Agent立规矩，Windows要管AI了》按 blog-article-to-okf-bundle 七阶段流程转化为 OKF v0.2 知识包。
- **阶段链路**：R（WebFetch 抓取信源 + F-001~F-032 事实采集 + P0/P1 核验）→ I（商业分析三层拆分）→ E（信源先行生成 bundle）→ V（对抗审查 + 索引接入 + 门禁）。
- **内容性质**：商业分析/战略资讯，不设 examples/；核验来源为微软 Windows Developer Blog、Windows Experience Blog 与 Anthropic 官方文章。
- **勘误记录**：F-027 名单口径、F-001 日期口径、F-007 归因三处，详见 [references/verification.md](references/verification.md)。
- **索引接入**：`jishu/ai/practice/index.md` 新增导航条目与 toctree；`jishu/ai/index.md`、`bundles/index.md` 三级索引计数同步。
- **门禁说明**：本环境 `invocations` 依赖未安装，采用 §7 手动等效验证清单（toctree/相对链接/UTF-8/F 编号双份比对），未运行 `invoke gates.*`。
- **V 阶段完成（2026-10-10）**：
  - 三级 toctree 接入：`bundles/index` → `jishu/ai/index` → `jishu/ai/practice/index` → 本 bundle `index`（`concepts/index`、`references/index`、`log`）逐级可达。
  - F 编号双份一致：`facts.md`（spec 区）与 `references/article-source.md`（bundle 区）均覆盖 F-001~F-032，连续无跳号。
  - 相对链接可达：`references/verification.md`、`references/article-source.md`、`concepts/*` 目标文件俱已落盘。
  - UTF-8 严格 roundtrip / 敏感信息零残留（公开内容）通过。
  - 计数同步：practice 组 17→18 束（14→15 目录）；ai 域 224→225；jishu 451；total_bundles 604。
  - **已知口径漂移说明**：`bundles/index.md` 的 ai 域行（L139）与 `jishu/ai/index.md`、`practice/index.md` 存在历史计数口径差异（如 ai 域 227 vs ai/index.md 225；`ai-security` 按束数 3 计 vs 目录数 1）。本次仅对与本 bundle 直接相关的三处（practice 组、ai 域、总量）做相对 +1，未根治既有全局计数漂移（超出本任务最小变更范围）。