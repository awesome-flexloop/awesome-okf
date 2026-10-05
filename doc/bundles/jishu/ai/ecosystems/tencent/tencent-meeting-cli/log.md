---
type: Changelog
scope: tencent-meeting-cli
name: log
version: "0.3.0"
---

# Changelog

## 0.3.0 — 2026-10-04

### 新增

- 第三轮增量：源码主体学习（七概念链路 R→I→E→V→C 知识沉淀场景），信源固定 tag **v1.0.18**（commit `e631b355da2b001d24b82f453b65d96f39c59865`，2026-09-11，remote `git@github.com:TencentCloud/tencentmeeting-cli.git`），符合 G0 信源稳定性门（固定 tag 非浮动分支）
- **新增第 10 个信源**：references/source-code.md（type: Reference），含仓库坐标、cmd/internal 模块地图、15 项机械复核计数原始记录、源码对文档的印证/深化/纠正清单
- **spec/facts.md**：新增 F-113 ~ F-199 共 87 条源码事实（112 → 199），分 8 组：工程骨架/构建分发（12）、命令装配/中间件（13）、OAuth/配置（10）、keychain/加密/文件原语（8）、HTTP/错误码/重试（7）、事件总线内核（22）、枚举/输出/日志/崩溃（10）、版本沿革/统计（5）；全部带 `文件:行号` 锚点
- **spec/insights.md**：新增洞察六~八（5 → 8 条）：
  6. 「薄 CLI」架构——手写 cobra 壳，唯一远程驱动的是 compact 输出契约而非命令定义
  7. 凭证安全平台自适应体系——主密钥分层托管 + GCM AAD 绑定 + 原子文件；「系统 Keychain」仅 macOS 字面成立
  8. per-host bus 是单机 IPC 微内核——alive-lock 选举、owner 哈希隔离、8 个硬编码事件注册表、字符串退出语义
- **新增 5 个概念文档**（00~08 不改动，续编号）：
  - 09-codebase-architecture.md（工程总览）
  - 10-command-assembly.md（命令装配与中间件）
  - 11-credential-security-internals.md（凭证安全内部机制）
  - 12-event-bus-internals.md（事件总线内核）
  - 13-cross-platform-engineering.md（传输、输出与跨平台工程）
- **索引同步**：concepts/index.md（9→14 篇 + 源码学习路径）、references/index.md（7→8 信源、3 行新增口径差异、toctree）、根 index.md（version 0.3.0、概念表/洞察/信源/学习路径/目录结构/信任说明）、tencent 组索引（概念/信源/事实计数）

### 对既有结论的深化与纠正（不覆盖旧条目，以「⚠️ 口径」并列）

- **F-025/F-107 深化**：「凭证存入系统 Keychain」仅 macOS 成立；Linux 为 0600 `master.key` 文件（无系统 keyring），Windows 为注册表 `HKCU\Software\TmeetCli\keychain` + DPAPI；三平台业务数据统一 AES-256-GCM `.enc`（F-149）
- **F-106 措辞澄清**：CHANGELOG 实测 18 版（v1.0.1~v1.0.18），**无 v1.0.0**；「v1.0.0 时期」为依据手册保存日期的推断（F-195）
- **事件注册表**：实测恰好 8 个 RegisterKey（meeting 5 + recording 1 + smart 2）；schemas.go 头注释的 recording.failed 未注册（F-173/F-174）
- **其他源码证伪**：ApiCmd 常量不生成命令/flag（F-130）；Go 中无 BuildTime 符号、-X 被静默忽略（F-115）；postinstall cleanup.js 不删跨平台二进制而是执行 auth logout（F-122）；Base64DecodeConverter 源码 3 种 vs CHANGELOG 4 种（F-189）；docs/command.md 实测 1594 行（与 v0.1.0 信源登记一致，F-196）

### 已知局限（本版新增）

- 源码静态学习未做真实账号运行期验证；OAuth 时序、WSS 行为、DPAPI/Keychain 表现的依据为代码静态分析 + 用户面文档互证；
- 源码快照为本地固定 tag 学习副本，事实引用以 GitHub tag v1.0.18 为权威坐标；
- 未逐行复核 wsspb protobuf 的全部消息字段（仅覆盖鉴权/心跳/订阅/推送主路径）；`internal/utils/enumerate` 16 个文件中仅 InstanceType 等高频枚举逐成员计数，长尾枚举以 F-187 摘要登记。

### V 阶段对抗审查记录（四视角，2026-10-04）

| # | 视角 | 意见 | 处置 |
|---|------|------|------|
| V-1 | 魔鬼 | **P0**：多处称「业务数据三平台统一写 `<open_id>.enc`」与源码矛盾——Windows 业务密文（AES-GCM base64）写注册表值 `HKCU\Software\TmeetCli\keychain\<open_id>`，全程无文件操作（keychain_windows.go:338-361）；DPAPI 仅保护主密钥；keychain.go 泛化头注释是误导来源 | **采纳已修**：concepts/11（图示/三平台表/磁盘表/排障表/登出段共 7 处）、source-code.md 深化段+纠正表新增行、insights 洞察七陈述与行动、F-142/F-149/F-150/F-151 全部改为「加密原语统一、存储载体分叉」口径，并注明源码历史注释与平台实现的权威性差异 |
| V-2 | 魔鬼 | **P0**：F-175 称「最后一个消费者 1→0 退订」与源码矛盾——subreg.go:13-15,57-61 与 source.go:63-66 明确刻意不发 UNSUBSCRIBE，由服务端 TTL 自动取消，重连后 Snapshot Replay | **采纳已修**：F-175 重写并补行号证据；concepts/12 引用计数段改写；insights 洞察八陈述补「0→1 订阅、1→0 不发 UNSUBSCRIBE」；source-code.md 纠正表新增行 |
| V-3 | 魔鬼 | **P1**：函数名 `registerResourceExitHook` 不存在（实际 registerResourceReleaseHook，root.go:172-178）；`TmeetError.Is` 不存在（实际包级函数 exception.Is，errors.go:31-39） | **采纳已修**：F-125/F-160 与 concepts/09、concepts/13 四处改名并补符号形态说明 |
| V-4 | 魔鬼 | **P1**：「payload 长度恒为 1」被泛化到全部 8 个 key；源码注释（schemas.go:32-39）该保证仅 meeting.started/meeting.end，数组为未来批量推送预留 | **采纳已修**：F-173、concepts/12 共性段与排障表收窄口径并加未来兼容性提示；旧文 07-event-bus 本就只限定两个 key，无需改；source-code.md 纠正表新增行 |
| V-5 | 新人 | **P1**：①concepts/12「六层」与箭头枚举 7 个组件、frontmatter 列 5 个名字三处不一致，并扩散至根 index 与 concepts/index；②DPAPI/IPC/SDDL/ACL/WSS/DFS/ORM/KDF/jitter 首现未解释 | **采纳已修**：统一为「七个组件（守护进程侧 6 + consume_runner 客户端侧 1）」四处同步；各缩写在首现处补全称（中文或英文全称） |
| V-6 | 老板 | 版本 minor bump 与上级计数连锁是否成立？全部计数断言（252/64 Go、38 ApiCmd、8 EventKey、23 InstanceType、16 enumerate、18 CHANGELOG、401/1594/125/122 行、100/512/65536/25s、8 依赖等）是否经得起机械复核？ | 复核通过：源码审查员逐条 Grep/Glob 机械核验，**计数类断言零错误**；0.2.0→0.3.0 成立（新增信源+87 事实+3 洞察+5 概念，00-08 无破坏性改写）；组索引 57+5=62 概念、40+1=41 信源、676+87=763 事实算术闭合（独立重数磁盘 10 包：62/16/41 一致），束总数 583 不变 |
| V-7 | 未来 | frontmatter/链接/F 编号/stale 与固定 tag 可追溯性 | 复核通过：6 个新文件 frontmatter 九字段齐全（type/status/stale_after=2027-04-04/sources/2026-10-04）；57 条相对链接 0 断链、0 file:///；F-001~F-199 共 199 定义连续无重号，新文件引用全部存在；新文件均标注 tag v1.0.18 @ e631b35；五处索引计数（根/concepts/references/log/组）一致；无 v0.2.0 残留自我标注 |
| V-8 | 魔鬼 | **P2 精度项**：DPAPI purge 触发条件写宽（实际仅 3 错误码且双 entropy 都失败）；InstanceType「20-33」看似连续区间；依赖表 8 依赖列 7 行；F-123 .gitignore 转述少了全局 `*.log`；根 index 链接前缺空格；「加解密零分叉」过头 | **采纳已修**：F-152/concepts/11 补三错误码与双次失败条件；F-186/concepts/13 改精确集合；09 依赖表拆 cobra/pflag 两行并标注；F-123 改 `/log`/`/logs`+全局 `*.log`；「零分叉」改「原语统一、后端分叉」；空格修复。references/index toctree 中 command-reference/cloud-doc 字母序倒置为 v0.2.0 既有问题且 hidden toctree 不影响构建，本轮不动 |
| V-9 | 老板 | 审查发现 2 个 P0 是否需要回滚版本号？ | 不需要：P0 均在 V 阶段（C 质量门之前）修复并完成全束一致性回归（Grep 扫描旧错误措辞零残留），知识包从未以错误状态交付；修复扩大了 F-149/F-175 的证据密度（补具体文件:行号），质量高于初版 |
| V-10 | 魔鬼 | 回归 Grep 扩面发现：v0.1.0 旧文件 examples/04-event-automation.md 有 4 处命令示例写 `meeting.ended`，而官方 EventKey 为 `meeting.end`（schemas.go:44-45 + command.md:1472 双证），照抄会得 UnknownEventKey——属用户面 P0 | **采纳已修**：4 处命令改为 `meeting.end`（保留对齐空格），节末加 v0.3.0 更正说明（不改写示例结构）；F-174 补登记该拼写纠正与双重证据，source-code.md 纠正表加行。旧文件仅做事实点修正，符合「00-08 不结构性重写」纪律 |

## 0.2.0 — 2026-10-03

### 新增

- 学习腾讯文档平台官方用户手册《腾讯会议 CLI使用说明》（`https://docs.qq.com/doc/DVUNDV0trdUdqeW5X`，页面元数据最后保存 2026-06-25 16:00，无需登录可读全文）
- **新增第 9 个信源**：references/user-manual-qqdoc.md（type: Reference，抓取方式可复现：dop-api/opendoc JSON → base64 → protobuf 线格式递归解析）
- **spec/facts.md**：新增 F-099 ~ F-112 共 14 条编号事实（98 → 112）：
  - F-099 信源元信息与用户手册风险提示；F-100「给 AI Agent 的那双手」用户面话术；F-101 兼容宿主点名名单（Workbuddy/Qclaw/Cursor/Claude Code/Codex）
  - F-102 环境要求（Node ≥16、支持 Shell 命令的 AI Agent）；F-103 企业灰度申请表精确 URL；F-104 v1.0.0 时期 19 命令逐名+职责表
  - F-105 跨版本比对（19 旧名 v1.0.18 全部存活、44=19+25 纯增量）；F-106 二次确认范围 3→9 命令的加厚轨迹
  - F-107 AES-256-GCM 与 Keychain 同句并列；F-108 腾讯用户规则中心 URL；F-109 反馈三入口；F-110 第三方 AI 客户端数据风险；F-111 四个对话式场景；F-112「对 agent 说」安装 prompt
- **spec/insights.md**：新增洞察五——三套带日期信源构成「文档时间差」证据链：对外命令契约纯增量、安全契约在提示词层独立加厚（4 → 5 条）
- **概念文档同步**：
  - 00-overview.md：双宿主名单并列、口径提示引用 F-104/F-105、灰度申请表 URL、第三方客户端风险与规则中心
  - 01-install-auth.md：Node ≥16 升级为两个用户面信源佐证、Keychain 加密口径补 F-107 单文本证据、新增「对 agent 说」安装 prompt
  - 02-command-map.md：新增 v1.0.0 十九命令存活对照表
  - 06-agent-safety-contract.md：二次确认范围演进注（F-106）、新增第十一节用户面安全指引（规则中心/反馈分流/第三方客户端风险）
  - 顺带修复 00-overview.md 延伸阅读断链（`05-agent-safety-contract.md` → `06-agent-safety-contract.md`）
- **索引同步**：references/index.md、根 index.md、tencent 组索引的信源/事实计数与登记表

### 已知局限（本版新增）

- 用户手册内截图与内测体验群二维码为图片对象，文本接口无 URL，仅登记文字内容；
- 「v1.0.0 时期」为依据源码构建示例 `Version=v1.0.0` + 19 命令面 + 2026-06-25 保存时间的推断，手册正文未逐字写版本号，相关处已注明。

### V 阶段对抗审查记录（四视角，2026-10-03）

| # | 视角 | 意见 | 处置 |
|---|------|------|------|
| V-1 | 魔鬼 | 00-overview 风险段引用「模型幻觉、提示词注入等原因产生非预期操作」标注 F-099，但原 F-099 未登记该引文，属事实-引用错位 | **采纳**：回查抓取全文确认原文存在（风险提示节），已将两句原文补登进 F-099 |
| V-2 | 魔鬼 | F-105「19→44 纯增量」是否真正逐一核对？新命令构成算术是否闭合？ | 复核通过并留痕：新增 25 = meeting 4 + record 3 + report 2 + tshoot 1 + contact 3 + control 3 + minutes 2 + app 2 + event 5（F-052/053/056/059/060/065/068~071/091 等逐条对应），19 旧名全保留 |
| V-3 | 新人 | 「v1.0.0 时期」推断若只引 F-104 会被误读为手册明示版本号 | **采纳**：00-overview 与 02-command-map 相关处改为标注推断依据（源码构建示例 Version=v1.0.0 + 保存日期，见 F-106 注） |
| V-4 | 老板 | 版本号 0.1.0→0.2.0 是否恰当？上级索引计数是否要连锁改？ | minor bump 成立（新增信源+14 事实+1 洞察，无破坏性改写）；束总数 583 不变，仅 tencent 组索引记信源/事实数（39→40、662→676），上级只记束数，gates 复核 |
| V-5 | 未来 | 截图/二维码缺失会否导致事实空洞？「首选安装路径」措辞是否越出 F-112 原文？ | 截图局限已在 F-099/信源文档/本日志三处声明，不影响文字事实完整性；**采纳**：01-install-auth「列为首选路径」改为「安装节首先给出」（F-112 只登记该路径存在，顺序经抓取全文核实） |

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
