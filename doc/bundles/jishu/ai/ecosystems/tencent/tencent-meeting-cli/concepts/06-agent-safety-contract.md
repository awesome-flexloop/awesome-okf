---
type: Concept
title: "Agent 安全契约：写在 SKILL.md 里的行为红线"
description: "tmeet-skill 规定的 9 个二次确认命令与跨轮确认流程、meeting_id 隐私禁令、成员回显格式、必填参数禁自填、通讯录白名单、踢人来源、翻页阈值、反馈脱敏与错误码处置规则。"
tags: [tencent-meeting, tmeet, agent-safety, skill, confirmation, privacy, prompt-contract]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单 tmeet-skill/SKILL.md
  - id: github-readme
    resource: /references/github-readme.md
    title: tencentmeeting-cli GitHub README
  - id: user-manual-qqdoc
    resource: /references/user-manual-qqdoc.md
    title: 腾讯文档官方用户手册《腾讯会议 CLI使用说明》
---

# Agent 安全契约

> 本篇汇总 `tmeet-skill/SKILL.md`（v1.0.18）对 AI Agent 的全部行为红线。关键认知：这些规则以自然语言提示词形式分发，**依赖宿主 Agent 忠实执行**，CLI 二进制本身不强制——这是「手/脑分离」架构的直接推论（见[洞察一](../spec/insights.md)）。

## 一、9 个命令必须跨轮二次确认

| 命令 | 风险 |
|------|------|
| `meeting cancel` | 会议被取消，受邀人受影响 |
| `meeting update` | 时间/设置被改 |
| `meeting invitees-add` | 拉人入会 |
| `meeting invitees-remove` | 移除受邀人 |
| `meeting invitees-replace` | 全量替换受邀人 |
| `control call` | 呼叫入会（打扰） |
| `control kick` | 会中踢人 |
| `auth logout` | 清除登录态 |
| `record permission-apply-commit` | 正式提交权限申请 |

（F-072；v1.0.18 起另含 `event stop --force` 这类破坏性总线操作，F-082）

> 演进注：2026-06-25 保存的官方用户手册中，二次确认范围只有 `meeting create` / `meeting update` / `meeting cancel` 三个写命令（F-106）；v1.0.18 的 9 命令清单新增了受邀者变更、会中控制、权限申请、登出六类。这印证了安全策略在 SKILL.md 提示词层独立加厚、无需改动命令二进制契约（见[洞察五](../spec/insights.md)）。

### 确认流程的三个动作

1. **展示操作详情**：要做什么、影响哪场会——会议一律用 `meeting_code`（会议号）标识；
2. **结束本轮回复**：停下来等用户的下一条真实输入；
3. **收到明确肯定**（「确认」「是」「yes」）后才执行。

三种明确违规模式（F-073）：

- ❏ **自问自答**：模型自己写「用户已确认」然后执行；
- ❏ **虚构指令**：把上下文中不存在的「确认」当作用户授权；
- ❏ **默认代选**：「我先帮你取消了，有问题再说」。

否定（「取消操作」「先不用」）则不执行。

## 二、隐私字段：meeting_id 禁令

- 严禁向用户输出 `meeting_id`，对外展示统一用 `meeting_code`（F-074）；
- meeting_id 仅作为命令行参数在 Agent 与 CLI 之间传递；
- 同理不主动回显 open_id 等内部标识——成员回显用规定格式（见下）。

## 三、成员回显格式

每名成员必须按如下格式输出（F-075）：

```
姓名（<标识>）
```

- 姓名优先级：接口返回的显示名字段 → 用户输入的搜索关键词 → 「未知成员」；
- 括号内只放一项，按 **部门 > 职位 > open_id** 的优先级取第一个有值的。

示例：`张*（研发部）`、`李*（产品总监）`。

## 四、多候选必须用户定夺

通讯录搜索、成员匹配出现多个候选时（F-076）：

- 列出候选让用户选，**禁止**基于职位高低、部门相关性、匹配度自行选择；
- 必填参数缺失时必须向用户询问，**禁止**自行填充默认值（例如缺时间就自己定个「下午三点」）。

## 五、通讯录场景白名单

`contact search` / `lookup-by-email` / `lookup-by-phone` 仅可用于：

1. 会议邀请（invitees-add/replace、create --invitees）的前置 openid 解析；
2. 会中呼叫（control call）的前置解析。

独立查人（联系方式、部门、人员是否存在）一律拒绝（F-066）。详见 [05 - 参会报告与会中控制](05-report-control.md)。

## 六、踢人来源硬约束

`control kick` 的目标成员**必须**来自 `report participants`（当前会中成员），禁止拿 `contact search` 结果踢人（F-071）。

## 七、输出与翻页节流

- 查询类命令默认 `--compact` 省 token（F-077）；
- page-token 只能原样回传，禁止拼接/自增；
- 首页结果返回后，非穷尽需求先问「是否继续」；
- 连续翻页 > 5 页或累计 > 200 条，必须主动征询（F-078）。

## 八、问题反馈的脱敏与去重

`tshoot feedback` 可由 Agent 在工具能力受阻时上报，但（F-092）：

- 上报前必须二次确认；
- 内容**严禁**包含姓名、电话、会议号、会议链接、会议主题、参会人；
- 必须脱敏：姓名打星（张*）、手机号中段打星（138****8000）；
- 同一会话中同一问题只报一次。

## 九、错误码纪律

| 错误码 | 纪律 |
|--------|------|
| 500284（功能暂不可用） | **严禁重试**；如实告知该功能不可用、解释权归腾讯会议（F-095） |
| 500294（套餐不足） | 响应中若带升级链接，原样渲染为可点击 Markdown 链接输出给用户（F-095） |
| 凭证类报错 | 未登录（`user config is empty`）→ 引导前台 `auth login`，勿后台执行 |

## 十、Token 与凭证

- 不输出 Access/Refresh Token（`auth status` 的剩余有效期可以转述，Token 值不回显）；
- 不把 `~/.tmeet/` 内容、Keychain 数据贴进对话或上传；
- 怀疑泄露：立即 `auth logout` + 账号安全中心吊销（F-031）。

## 十一、官方用户手册的用户面安全指引

面向普通用户（而非 Agent 作者），官方用户手册的三条补充边界（F-108、F-109、F-110）：

- **规则依据**：使用须知链接[腾讯用户规则中心](https://rule.tencent.com/rule/202603130003)（F-108）；
- **第三方客户端风险**：CLI 只把数据传给宿主 Agent；使用 Cursor、Claude Code、ChatGPT 等第三方 AI 客户端时，会议内容可能被对应平台模型处理，须遵循该平台隐私政策（F-110）——换言之，SKILL.md 红线只约束 Agent「怎么操作会议」，不覆盖平台方「怎么处理看到的内容」，后者是独立的数据合规面；
- **漏洞与问题上报分流**：安全漏洞走仓库 [SECURITY.md](https://github.com/TencentCloud/tencentmeeting-cli/blob/main/SECURITY.md)，体验问题走 [GitHub Issues](https://github.com/TencentCloud/tencentmeeting-cli/issues)，另有内测体验互助群（F-109）。

## 为什么这些规则能成立（也为什么不能只靠它）

官方风险提示承认模型幻觉、提示词注入、投毒攻击可能造成数据泄露与越权（F-097）。SKILL.md 的红线设计相当系统化（确认、标识隔离、最小权限、来源约束、脱敏、去重试），但它的强制力来源是**模型对指令的遵循**，不是操作系统级权限。因此：

- ✅ 个人使用：装好 Skill、保持 Agent 更新，可获得官方设计的完整防护；
- ⚠ 企业/高敏场景：应在 CLI 外层增加网关审计或包装脚本（拦截 cancel/kick 等命令），把提示词级策略下沉为机制级强制；
- ⚠ 任意场景：不要把 tmeet 凭证所在的 Agent 会话暴露给不可信的网页/文档内容（提示词注入面）。

## 延伸阅读

- [00 - 产品定位与双件架构](00-overview.md)
- [05 - 参会报告与会中控制](05-report-control.md)
- 核心洞察：[洞察一 · 安全边界在 Skill 提示词层](../spec/insights.md)
