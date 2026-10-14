---
type: Changelog
scope: kylin-agent-runtime
name: log
version: "0.1.0"
source: gitee.com/openkylin/agent-runtime@ee0c170
description: kylin-agent-runtime OKF 知识库变更日志。
---

# Changelog

## 2026-10-14

### 新增

- 初始创建 kylin-agent-runtime OKF v0.2 wiki bundle（源码快照 commit `ee0c1709199b37ebccdc69b545f266e52e5ed6c9`，`V0.9.4-52`，打包版本 1.0.1；2026-10-14 经七概念知识沉淀链路 R→I→E→V 生成）。
- **spec/facts.md**：150 条编号事实（F-001 ~ F-150），覆盖项目元数据、AIAgent 核心环、工具体系、模型 Provider、记忆上下文/画像、技能插件、网关、ACP/MCP/LSP、cron、SessionDB、CLI/TUI/Web 与横切设施；10 条数量卡（Q-001 ~ Q-010）全部附计数命令与口径（含/不含项、原始匹配/去重名、lone-CR 行口径差异）。
- **spec/insights.md**：5 条四元组洞察——三代架构同层共存、工具自注册 vs 平台枚举硬连双轨、openKylin 下游"分发层改名/符号层留血"、自进化三条带治理的学习回路、供应链安全约束；附 10+2 文档知识地图。
- **references/source-code-map.md**：快照元数据（远程 URL、全 hash、tag 血缘、四处组件版本、复验方式）与关键文件→事实 ID 映射；**references/community-sig.md**：openKylin AISubsystem SIG（SIG 120）使命三条、邮件列表、9 页仓库生态与动态数字不采信边界。
- **concepts/**（10 篇）：00-overview、01-architecture-module-map、02-agent-core-loop、03-cli-and-tui、04-tool-system、05-model-providers、06-skills-and-plugins、07-memory-and-context、08-gateway-and-cron、09-acp-mcp-protocols。
- **examples/**（2 篇）：01-install-setup-first-run（uv/setup/四种运行/测试更新，命令逐条对齐 README.zh-CN）、02-gateway-and-cron-usage（systemd 服务与 cron 作业字段）。
- **index.md / 三个子目录 index.md**：表格导航与隐藏 toctree 齐备。

### 信源

- 主信源：https://gitee.com/openkylin/agent-runtime.git @ `ee0c170`（只读，工作树零改动，开工与 V 前两次复验 hash 一致）。
- 社区信源：https://www.openkylin.top/sig/sig_detail.html?sig_id=120 （AISubsystem SIG，抓取于 2026-10-14；JS 分页静态不可翻页，动态 PR/Issue 数字不引用）。
- 关键数量口径：agent/ 120 py、plugins/ 118、tools/ 93（76+12+5）、CLI 包 94（87+7）、gateway/ 64；platforms 32 文件 = 20 适配器文件 + base + helpers + 10 辅助，适配器实现 21 个（含 qqbot 子包）、Platform 枚举 22 成员；31 工具集、48 内置子命令、4 注册传输、17 插件目录、77 个 SKILL.md、26 LSP 服务器、SessionDB 9+2 表 + 2 FTS5。

### 勘误记录（8 条，全文见 spec/facts.md）

- E-001：终端后端初稿口头数"7 个"，枚举叶子实为 8 个（补 managed_modal/vercel_sandbox）。
- E-002：platforms 32 个 .py 文件与 21 个适配器实现/22 个枚举成员三口径显式区分。
- E-003：hermes/kylin 双命名并存（portal_tags、FastAPI 标题、ui-tui 包名、HERMES_* env）如实记录。
- E-004：ContextCompressor 入参 0.50 被函数体 0.80 无条件覆盖，作为代码事实/技术债线索。
- E-005：12 个 agent 根文件未深采、巨型文件仅采顶层符号、纯静态分析的疑点留痕。
- E-006：快照残留 .before-kylin-approvals 文件与 web_dist/tui_dist 缺失（仅 wheel 路径）记录。
- E-007：V 前修正三处行号偏差（probe_gemini_tier 61→47、CopilotACPClient 321→334、apply_anthropic_cache_control 41→49），符号真实、快照零漂移。
- E-008：V 独立复核修正终端环境继承关系（ModalEnvironment 直接继承 BaseEnvironment；继承树 9 类/8 叶子）；F-064 传输注册行号口径统一。
- R1 独立评审整改（2026-10-14）：补写 F-128（cron/ 目录事实）使编号连续 150 条；02 篇 recovery_policy_for_tool 返回语义由"四元组"更正为"四个策略名之一的字符串"；03 篇 gateway status 归因改挂 F-136。
