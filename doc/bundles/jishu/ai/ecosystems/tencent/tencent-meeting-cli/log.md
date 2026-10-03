---
type: Changelog
scope: tencent-meeting-cli
name: log
version: "0.1.0"
---

# Changelog

## 0.1.0 — 2026-10-03

### 新增

- 初始 OKF v0.2 知识包生成（七概念方法论 R→I→E→V→C 链路，知识沉淀场景）
- **spec/facts.md**：98 条编号事实（F-001 ~ F-098），覆盖 8 个官方公开信源，含 3 处信源口径差异并列登记
- **spec/insights.md**：4 条四元组核心洞察（陈述/证据/反常识/行动）：
  1. 安全边界在 Skill 提示词层而非 CLI 代码层——手/脑双件与策略机制分离
  2. 「纪要」是两套权限模型不同的独立产物——permission_status 分流与双向兜底
  3. CLI 的第一用户是模型而非人——信封/compact/游标/ready/退出码的机器可组合性
  4. 能力缺口与实时事件都被产品化——tshoot feedback 回流 + per-host 事件总线
- **6 个信源登记文档**：
  - product-page.md（产品首页，F-002/F-005~F-007/F-011/F-016/F-018/F-020）
  - install-guide.md（安装指南，F-012/F-013/F-019/F-020）
  - github-readme.md（README，F-001/F-003/F-017/F-021/F-022/F-024/F-028/F-033/F-035/F-038/F-039/F-097）
  - cloud-doc.md（腾讯云文档 133827，F-004/F-015/F-025/F-029/F-030/F-034/F-040/F-093/F-094/F-096）
  - command-reference.md（docs/command.md v1.0.18，F-026/F-027/F-041~F-061/F-065/F-067~F-071/F-080~F-091）
  - skill-manifest.md（SKILL.md/CHANGELOG/package.json，F-008~F-010/F-014/F-023/F-032/F-036/F-037/F-062~F-064/F-066/F-072~F-079/F-082/F-086/F-092/F-095/F-098）
- **9 个概念文档**：
  - 00-overview.md（产品定位与双件架构）
  - 01-install-auth.md（安装与 OAuth2 授权）
  - 02-command-map.md（命令体系与全局约定）
  - 03-meeting-lifecycle.md（会议全生命周期）
  - 04-record-minutes.md（录制、转写与双纪要体系）
  - 05-report-control.md（参会报告、会中控制与通讯录边界）
  - 06-agent-safety-contract.md（Agent 安全契约）
  - 07-event-bus.md（实时事件总线，v1.0.18+）
  - 08-app-tshoot.md（应用配置与运维反馈）
- **4 个示例文档**：
  - 01-quickstart.md（十分钟上手）
  - 02-minutes-workflow.md（会后取纪要双链路工作流）
  - 03-recurring-export.md（周期会议与异步导出）
  - 04-event-automation.md（事件订阅自动化）
- **索引文件**：concepts/index.md、examples/index.md、references/index.md
- **根 index.md**：分区导航、信源登记、学习路径、信任与生命周期说明（含未运行验证声明、口径差异说明、stale_after 依据）

### 数据来源

- 腾讯会议 CLI 产品首页（https://meeting.tencent.com/meeting-cli/index.html）
- CLI 安装指南（https://meeting.tencent.com/wemeet-tapi/v2/oauth2/oauth/cli-install-guide?ch=web）
- GitHub 仓库（https://github.com/TencentCloud/tencentmeeting-cli，README / docs/command.md / skills/tmeet-skill/SKILL.md / package.json / CHANGELOG.md）
- 腾讯云文档（https://cloud.tencent.com/document/product/1095/133827，页面更新时间 2026-07-08）

### 生成方式

- R 阶段：抓取并通读 8 个信源（command.md 1594 行、SKILL.md 约 34KB 全文），提取 98 条编号事实，G1 事实门通过
- I 阶段：形成 4 条四元组洞察，G2 洞察门通过
- E 阶段：按 OKF v0.2 规范落盘 9 概念 + 4 示例 + 6 信源 + spec 与完整索引，G3 模式门通过
- V 阶段：四视角（魔鬼/新人/老板/未来）对抗审查，采纳意见修正（见下条）
- C 阶段：质量门与构建验证后交付，提交待用户确认

### 已知局限

- 文档学习生成，未在真实腾讯会议账号上执行验证；
- 腾讯云文档口径滞后于 main 分支（19 命令 vs 44 子命令），已并列标注；
- SKILL.md 附带 references/ 子目录的分命令细则与 scripts/agent_init.py 未逐字抓取，核心行为契约已由 SKILL.md 主文件覆盖；
- stale_after：2027-04-03。
