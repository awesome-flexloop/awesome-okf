---
type: bundle
okf_version: "0.2"
scope: tencent-meeting-cli
name: tencent-meeting-cli
version: "0.3.0"
source: web
description: "腾讯会议官方 CLI（tmeet）OKF 知识包：CLI + CLI-Skill 双件架构、OAuth2 设备码授权、44 个会议管理子命令、录制与元宝双纪要体系、Agent 安全行为契约、实时事件总线（v1.0.18）；v0.3.0 增补 v1.0.18 源码级内部机制（命令装配、凭证安全、事件总线内核、跨平台工程）。"
---

# 腾讯会议 CLI（tmeet）知识库

腾讯会议 CLI 是腾讯会议官方推出的命令行工具（命令名 `tmeet`，npm 包 `@tencentcloud/tmeet`，MIT 开源），让 AI Agent 通过自然语言直接完成会议预约、成员管理、录制纪要获取、参会报告导出、会中控制与实时事件订阅。本知识包基于 10 个官方公开信源（产品首页、安装指南、GitHub README、腾讯云文档、1594 行完整命令参考、34KB CLI-Skill 清单、package.json、CHANGELOG、腾讯文档官方用户手册，以及 v1.0.18 固定 tag 源码主体）系统梳理，覆盖 v1.0.18（2026-09-11）版本形态。

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

### 源码内部机制（v0.3.0 新增，基于 v1.0.18 固定 tag）

| 文档 | 说明 |
|------|------|
| [源码工程总览](concepts/09-codebase-architecture.md) | module/8 直接依赖、cmd-internal 分层、Tmeet 容器与四主机、5 目标静态构建、Node 包装器分发链路 |
| [命令装配与中间件](concepts/10-command-assembly.md) | 手写 cobra 壳、38 个 ApiCmd 常量的真实用途、compact 远程字段表、分页兼容、隐藏命令 |
| [凭证安全内部机制](concepts/11-credential-security-internals.md) | OAuth 设备码时序、macOS Keychain/Linux 0600/Windows DPAPI 三平台托管、AES-256-GCM 与 AAD 绑定 |
| [事件总线内核](concepts/12-event-bus-internals.md) | 七组件微内核、alive-lock 选举、wsspb 心跳重连、8 个硬编码 EventKey、owner 哈希与清理闭环 |
| [传输、输出与跨平台工程](concepts/13-cross-platform-engineering.md) | 双代理与诊断头、错误码分段/重试、16 枚举文件、输出中间件族、自研日志与崩溃上报、18 版演进 |

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
4. **能力缺口与实时事件都被产品化**——feedback 回流管道 + per-host 事件总线；
5. **带日期信源构成「文档时间差」证据链**——19 旧命令名跨版本全部存活（44=19+25 纯增量），安全契约 3→9 命令在提示词层独立加厚；
6. **「薄 CLI」架构**——命令是手写 cobra 壳，唯一被远程驱动的是 compact 输出契约而非命令定义（v0.3.0 新增）；
7. **凭证安全是平台自适应体系**——主密钥分层托管 + GCM AAD 绑定 + 原子文件，官方「Keychain」说法仅 macOS 字面成立（v0.3.0 新增）；
8. **per-host bus 是单机 IPC 微内核**——alive-lock 选举、owner 哈希隔离、8 个硬编码事件注册表、字符串退出语义（v0.3.0 新增）。

详见 [spec/insights.md](spec/insights.md)。

## 信源登记簿

| 信源 | 文件 | 内容 |
|------|------|------|
| 产品首页 | [product-page.md](references/product-page.md) | 定位、兼容 Agent、业务场景、FAQ |
| 安装指南 | [install-guide.md](references/install-guide.md) | CLI+Skill 安装、Node 版本、重启验证 |
| GitHub README | [github-readme.md](references/github-readme.md) | 开源属性、构建、授权、命令树、风险提示 |
| 腾讯云文档 | [cloud-doc.md](references/cloud-doc.md) | 调用链路、Keychain、套餐条件、旧版 19 命令口径 |
| 腾讯文档用户手册 | [user-manual-qqdoc.md](references/user-manual-qqdoc.md) | 最终用户面教程（2026-06-25）、v1.0.0 十九命令逐名表、灰度申请表与反馈渠道 URL、跨版本比对 |
| 完整命令参考 | [command-reference.md](references/command-reference.md) | 44 子命令参数级权威（v1.0.18，1594 行） |
| Skill/变更/包清单 | [skill-manifest.md](references/skill-manifest.md) | Agent 行为契约、版本演进、包元数据 |
| 源码主体（v1.0.18 固定 tag） | [source-code.md](references/source-code.md) | Go module `tmeet` 实现侧权威：模块地图、文件:行号锚点、机械复核统计、对文档口径的印证/深化/纠正 |

完整编号事实见 [spec/facts.md](spec/facts.md)（F-001 ~ F-199）。

## 学习路径建议

1. **首次接触**：[产品定位](concepts/00-overview.md) → [安装授权](concepts/01-install-auth.md) → [十分钟上手](examples/01-quickstart.md)
2. **日常会议助理**：[命令约定](concepts/02-command-map.md) → [会议生命周期](concepts/03-meeting-lifecycle.md) → [参会与控制](concepts/05-report-control.md)
3. **知识管理场景**：[双纪要体系](concepts/04-record-minutes.md) → [取纪要工作流](examples/02-minutes-workflow.md)
4. **Agent 集成者（必读红线）**：[Agent 安全契约](concepts/06-agent-safety-contract.md)
5. **自动化/集成开发**：[事件总线](concepts/07-event-bus.md) → [事件自动化示例](examples/04-event-automation.md) → [运维反馈](concepts/08-app-tshoot.md)；深入排障续读 [事件总线内核](concepts/12-event-bus-internals.md)
6. **源码学习/二次开发者（v0.3.0）**：[工程总览](concepts/09-codebase-architecture.md) → [命令装配](concepts/10-command-assembly.md) → [凭证安全](concepts/11-credential-security-internals.md) → [总线内核](concepts/12-event-bus-internals.md) → [跨平台工程](concepts/13-cross-platform-engineering.md)，锚点对照 [源码信源](references/source-code.md)

## 目录结构

```
tencent-meeting-cli/
├── index.md                    # 本文件（知识包根索引）
├── log.md                      # 变更日志
├── spec/
│   ├── facts.md                # R 阶段：199 条编号事实（F-001 ~ F-199；F-113+ 为源码事实）
│   └── insights.md             # I 阶段：8 条四元组洞察
├── concepts/
│   ├── index.md
│   ├── 00-overview.md          # 00 ~ 08 用户面 9 篇
│   ├── 09-codebase-architecture.md  # 09 ~ 13 源码内部机制 5 篇（v0.3.0）
│   └── …
├── examples/
│   ├── index.md
│   ├── 01-quickstart.md        # 共 4 篇
│   └── …
└── references/
    ├── index.md
    ├── product-page.md         # 共 8 篇（10 个 URL/文件；source-code 为 v0.3.0 新增）
    └── …
```

## 信任与生命周期说明

- **事实来源**：全部 199 条事实来自 10 个官方公开信源（腾讯会议官网、腾讯云文档中心、官方 GitHub 仓库及其仓库内文档、腾讯文档平台官方用户手册，以及 v1.0.18 固定 tag 源码主体 commit e631b35）。F-001~F-112 抓取于 2026-10-03，F-113~F-199 采集于 2026-10-04 且均带 `文件:行号` 锚点，关键计数（38 ApiCmd、8 EventKey、23 InstanceType、252/64 Go 文件、18 个 CHANGELOG 版本等）已经 Glob/Grep 机械复核；未引入外部推测。命令参数级内容以 v1.0.18 `docs/command.md` 为准，机制解释以同 tag 源码为准。
- **未运行验证声明**：本束由文档与源码静态学习生成，编写时未在真实账号上执行 tmeet 网络命令，命令行为依据为官方文档、Skill 清单原文与源码静态分析；源码可确认实现路径但无法替代真实账号联调，落地使用前建议按[十分钟上手](examples/01-quickstart.md)实际验证。
- **口径差异处理**：除既有 Node 版本（14 vs 16）、命令数量（44 vs 19）、凭证存储（本地加密 vs Keychain）三处外，v0.3.0 源码侧新增四处并列登记：事件 key（头注释 recording.failed 未注册）、Base64 编码数（CHANGELOG 4 种 vs 源码 3 种）、首个版本（无 v1.0.0）、「系统 Keychain」仅 macOS 字面成立；全部以「⚠️ 口径」并列为先，源码结论只做机制侧补充，不覆盖旧条目。
- **v0.2.0 增补**：新增腾讯文档官方用户手册信源（2026-06-25 保存）与 F-099~F-112 共 14 条事实、洞察五（文档时间差证据链）；正文截图与内测群二维码为图片对象，文本接口不可得，仅登记文字内容。
- **v0.3.0 增补**：新增源码主体信源（tag v1.0.18 @ e631b35）与 F-113~F-199 共 87 条源码事实、洞察六~八（薄 CLI/凭证平台自适应/总线微内核）、概念 09~13 共 5 篇源码内部机制文档；00~08 既有文档内容不改动。
- **status 判定**：14 概念 + 4 示例 + 8 信源均标记 `stable`，表示基于已抓取信源可直接消费。
- **stale_after 解释**：00~08 文档设置为 2027-04-03（生成日后 6 个月）；09~13 源码文档与 source-code 信源设置为 2027-04-04（对应固定 tag 的 6 个月复核点）。到期应重新抓取 command.md、SKILL.md、CHANGELOG，并将源码快照 rebase 到最新 release tag 后复核 F-113~F-199（尤其 8 事件注册表、ApiCmd 常量集与三平台 keychain 实现）。
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
