---
type: bundle
okf_version: "0.2"
scope: tencent-meeting-cli
name: tencent-meeting-cli
version: "0.1.0"
source: web
description: "腾讯会议官方 CLI（tmeet）OKF 知识包：CLI + CLI-Skill 双件架构、OAuth2 设备码授权、44 个会议管理子命令、录制与元宝双纪要体系、Agent 安全行为契约、实时事件总线（v1.0.18）。"
---

# 腾讯会议 CLI（tmeet）知识库

腾讯会议 CLI 是腾讯会议官方推出的命令行工具（命令名 `tmeet`，npm 包 `@tencentcloud/tmeet`，MIT 开源），让 AI Agent 通过自然语言直接完成会议预约、成员管理、录制纪要获取、参会报告导出、会中控制与实时事件订阅。本知识包基于 8 个官方公开信源（产品首页、安装指南、GitHub README、腾讯云文档、1594 行完整命令参考、34KB CLI-Skill 清单、package.json、CHANGELOG）系统梳理，覆盖 v1.0.18（2026-09-11）版本形态。

理解 tmeet 的钥匙是**双件架构**：Go 编写的 CLI 二进制只负责注入 OAuth Token 并透传开放平台 REST API；真正约束 AI 行为的安全规则（9 个二次确认命令、meeting_id 隐私禁令、通讯录场景白名单、踢人来源硬约束）写在随仓库分发、需单独安装的 `tmeet-skill/SKILL.md` 提示词契约里。CLI 是「手」，Skill 是「脑」。

## 概念篇

| 文档 | 说明 |
|------|------|
| [产品定位与双件架构](concepts/00-overview.md) | CLI + Skill 双件模型、自然语言→REST 调用链路、10 命令域全景、账号条件与官方风险 |
| [安装与 OAuth2 授权](concepts/01-install-auth.md) | npm/源码安装、Skill 安装与重启、设备码登录、AES-256-GCM + Keychain 凭证 |
| [命令体系与全局约定](concepts/02-command-map.md) | 44 命令地图、JSON 信封、--compact、ISO 8601、游标分页、bool 等号语法 |
| [会议全生命周期管理](concepts/03-meeting-lifecycle.md) | 普通/周期会议创建、查询搜索、改期取消、受邀成员管理 |
| [录制、转写与双纪要体系](concepts/04-record-minutes.md) | record/minutes 双链路、permission_status 分流、权限两阶段申请、跨会议双搜 |
| [参会报告与会中控制](concepts/05-report-control.md) | 参会明细、异步导出轮询、呼叫/踢人/等候室、通讯录白名单 |
| [Agent 安全契约](concepts/06-agent-safety-contract.md) | 9 命令跨轮确认、隐私字段、成员回显、脱敏去重、错误码纪律 |
| [实时事件总线](concepts/07-event-bus.md) | event 五命令、per-host bus、共享 WSS、NDJSON、ready 标记与退出码（v1.0.18+） |
| [应用配置与运维反馈](concepts/08-app-tshoot.md) | app 会中展示三档布局、tshoot 日志导出与五类结构化反馈 |

## 实战示例

| 示例 | 说明 |
|------|------|
| [十分钟上手](examples/01-quickstart.md) | 安装 CLI/Skill → 设备码登录 → 创建第一场会 → 查询列表的最小闭环 |
| [会后取纪要工作流](examples/02-minutes-workflow.md) | 双纪要权限分流、录制失败降级元宝、跨会议双搜去重、权限两阶段申请 |
| [周期会议与参会明细导出](examples/03-recurring-export.md) | 每周周期会、受邀管理、participants-export 异步轮询下载 |
| [事件订阅自动化](examples/04-event-automation.md) | NDJSON 流消费、jq 投影、stderr ready 同步、orphan/stale_owner 自愈 |

## 核心洞察（四元组）

1. **安全边界在 Skill 提示词层而非 CLI 代码层**——策略与机制分离，策略以 Markdown 为载体；
2. **「纪要」是两套权限模型不同的独立产物**——按 permission_status 分流并双向兜底；
3. **CLI 的第一用户是模型而非人**——信封/compact/游标/ready 标记/退出码皆为机器可组合性设计；
4. **能力缺口与实时事件都被产品化**——feedback 回流管道 + per-host 事件总线。

详见 [spec/insights.md](spec/insights.md)。

## 信源登记簿

| 信源 | 文件 | 内容 |
|------|------|------|
| 产品首页 | [product-page.md](references/product-page.md) | 定位、兼容 Agent、业务场景、FAQ |
| 安装指南 | [install-guide.md](references/install-guide.md) | CLI+Skill 安装、Node 版本、重启验证 |
| GitHub README | [github-readme.md](references/github-readme.md) | 开源属性、构建、授权、命令树、风险提示 |
| 腾讯云文档 | [cloud-doc.md](references/cloud-doc.md) | 调用链路、Keychain、套餐条件、旧版 19 命令口径 |
| 完整命令参考 | [command-reference.md](references/command-reference.md) | 44 子命令参数级权威（v1.0.18，1594 行） |
| Skill/变更/包清单 | [skill-manifest.md](references/skill-manifest.md) | Agent 行为契约、版本演进、包元数据 |

完整编号事实见 [spec/facts.md](spec/facts.md)（F-001 ~ F-098）。

## 学习路径建议

1. **首次接触**：[产品定位](concepts/00-overview.md) → [安装授权](concepts/01-install-auth.md) → [十分钟上手](examples/01-quickstart.md)
2. **日常会议助理**：[命令约定](concepts/02-command-map.md) → [会议生命周期](concepts/03-meeting-lifecycle.md) → [参会与控制](concepts/05-report-control.md)
3. **知识管理场景**：[双纪要体系](concepts/04-record-minutes.md) → [取纪要工作流](examples/02-minutes-workflow.md)
4. **Agent 集成者（必读红线）**：[Agent 安全契约](concepts/06-agent-safety-contract.md)
5. **自动化/集成开发**：[事件总线](concepts/07-event-bus.md) → [事件自动化示例](examples/04-event-automation.md) → [运维反馈](concepts/08-app-tshoot.md)

## 目录结构

```
tencent-meeting-cli/
├── index.md                    # 本文件（知识包根索引）
├── log.md                      # 变更日志
├── spec/
│   ├── facts.md                # R 阶段：98 条编号事实（F-001 ~ F-098）
│   └── insights.md             # I 阶段：4 条四元组洞察
├── concepts/
│   ├── index.md
│   ├── 00-overview.md          # 01 ~ 08 共 9 篇
│   └── …
├── examples/
│   ├── index.md
│   ├── 01-quickstart.md        # 共 4 篇
│   └── …
└── references/
    ├── index.md
    ├── product-page.md         # 共 6 篇（8 个 URL/文件）
    └── …
```

## 信任与生命周期说明

- **事实来源**：全部 98 条事实来自 8 个官方公开信源（腾讯会议官网、腾讯云文档中心、官方 GitHub 仓库及其仓库内文档），抓取日期 2026-10-03，未引入外部推测；命令参数级内容以 v1.0.18 main 分支 `docs/command.md` 为准。
- **未运行验证声明**：本束由文档学习生成，编写时未在真实账号上执行 tmeet 命令，命令行为依据为官方文档与 Skill 清单原文；落地使用前建议按[十分钟上手](examples/01-quickstart.md)实际验证。
- **口径差异处理**：Node 版本（14 vs 16）、命令数量（44 vs 19）、凭证存储（本地加密 vs Keychain）三处信源差异均并列登记（F-015、F-034、F-024/F-025），不做单边删改。
- **status 判定**：9 概念 + 4 示例 + 6 信源均标记 `stable`，表示基于已抓取信源可直接消费。
- **stale_after 解释**：统一设置为 2027-04-03（生成日后 6 个月）。依据：v1.0.17 与 v1.0.18 发布间隔仅 2 天、命令数两月内 19→44，产品处于高速迭代期；到期应重新抓取 command.md、SKILL.md 与 CHANGELOG 核验（尤其 event/app 新域）。
- **覆盖范围**：覆盖 CLI 安装授权、会议/录制/纪要/报告/控制/通讯录/事件/应用/反馈全部命令域与 Agent 行为契约；不含开放平台 REST API 全量字段、企业灰度申请流程细节、计费策略与第三方评测。
- **内容敏感度**：全部内容来自公开发布的官方网页与开源仓库，属公开内容（Public）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
