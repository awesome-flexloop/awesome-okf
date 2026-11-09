---
type: concept
title: 前置检查与身份
description: 拆解「版本检查 → 授权状态 → 非交互初始化」三步硬门禁、身份获取与 ID 类字段禁外露约束。
tags: [wecom, wecom-unified, preflight, identity]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# 前置检查与身份

`SKILL.md` 把环境检查写成一条强制门禁：标题即「⚠️ 前置检查 — 使用任何命令前必须执行」（F-024）。这不是建议性提示，而是带失败短路的启动协议——任一步不满足，就停止业务操作并把错误告知用户，不允许「先试试看」。对宿主 Agent 而言，这段内容应当被实现为一个幂等的 preflight 函数，而不是每次对话里复述的说明文字。

## 一、门禁的三步结构

| 步骤 | 目标 | 命令 | 通过条件 | 失败动作 | 证据 |
|---|---|---|---|---|---|
| Step 1 | CLI 已安装且版本达标 | `wecom-cli --version` | 版本 >= `1.2.1` | 安装 `@wecom/cli` 后复验；仍失败则停止 | F-025～F-028、F-106 |
| Step 2 | 凭证已配置 | `wecom-cli auth show --status` | 输出 `authorized` | 转 Step 3；其它状态停止 | F-029、F-030 |
| Step 3 | 完成扫码授权 | `wecom-cli auth init --noninteractive` | 阻塞至扫码成功，复验为 `authorized` | 未授权则不进入业务 | F-031、F-032 |

三步的顺序不可交换：版本不达标时授权命令本身可能不存在；授权状态未知时执行初始化可能产生重复凭证。门禁的产物是一个明确的「可进入业务」判断，而不是若干条检查日志。

## 二、Step 1：版本下限为什么是 1.2.1

`SKILL.md` 在第 13、19、25 行三处重复写了 `1.2.1` 这个下限（F-106）。三处分别对应「检查项描述」「安装说明」「安装后复验」，说明作者把版本要求当作贯穿修复流程的常量，而不是一次性提示。检查命令是 `wecom-cli --version`（F-026），安装命令是 `npm install -g @wecom/cli`（F-027）。

需要区分两类失败：**未安装**表现为命令不存在，按安装指引处理后必须重跑版本命令；**版本过低**表现为命令可执行但输出版本小于 `1.2.1`，同样要升级后复验。`SKILL.md` 对这两种情况的收尾一致——「仍失败或版本仍低于 1.2.1 时停止业务操作并把错误告知用户」（F-028）。这条约束的价值在于阻断「CLI 已装但版本旧」的半可用态：这种状态下部分子命令可用、部分不可用，失败原因极难归因。

## 三、Step 2：授权状态的三值分支

`auth show --status` 被定义为三值判定，而不是布尔值（F-029、F-030）：

| 输出 | 含义 | 后续动作 |
|---|---|---|
| `authorized` | 已有有效凭证 | 直接进入业务 |
| `unauthorized` | 未授权或凭证缺失 | 转 Step 3 初始化 |
| 报错或其它值 | 状态异常（网络、配置损坏等） | 停止，不尝试初始化 |

把「报错」与「未授权」分开处理是关键设计。若把任何非 `authorized` 都当作未授权而贸然初始化，可能在凭证文件损坏或服务端异常时反复写入，掩盖真实故障。正确做法是把异常状态原样上报，让用户或运维先修复环境。

## 四、Step 3：非交互初始化的阻塞语义

初始化命令是 `wecom-cli auth init --noninteractive`（F-031）。`--noninteractive` 并不表示「无需人工」，而是「不进入交互式问答」：命令会输出授权链接与二维码，然后**阻塞等待扫码**，授权成功后自动退出；该动作只需执行一次（F-032）。

这带来两个工程约束。第一，它必须放在有人工介入的节点，不能塞进无人值守的循环或 CI 任务，否则会永久挂起。第二，初始化成功不等于可用：`SKILL.md` 要求初始化后重跑 `auth show --status`，仅在返回 `authorized` 时才继续（F-032）。换言之，Step 3 的验收标准仍然是 Step 2 的命令，而不是初始化命令的退出码。

## 五、身份获取：identity whoami

授权完成后，`SKILL.md` 单列「获取个人身份」一节，命令为 `wecom-cli identity whoami`（F-033）。它的典型用途是确认当前凭证对应的账号、在多人共用设备时排除串号，以及在生成「我发起的会议 / 我的待办」这类个人范围查询前锁定主体。身份输出应按可读字段呈现（姓名、部门、邮箱等），而不是把内部标识直接抛给用户——这与下一节的输出约束同源。

## 六、ID 类字段禁止外露

这是 `SKILL.md` 中唯一覆盖全部 `wecomcli-*` 技能的通用输出约束，且明确「不因用户主动索要而放宽」（F-034）。禁止清单覆盖人员/组织标识与资源/分页标识两类，要求改用可读字段（F-035、F-036）：

| 类别 | 禁止外露字段 | 应替换为 |
|---|---|---|
| 人员与组织 | `userid`、`open_vid`、`department_id`、`chat_id` | `name`、`username`、`external_username`、部门名 |
| 资源 | `mail_id`、`media_id`、`file_id`、`space_id`、`folder_id`、`docid`、`content_id`、`msg_id` | `subject`、`doc_name`、`chat_name`、`title`、邮箱 |
| 分页 | `cursor`、`next_cursor` | 自然语言描述「还有更多结果」 |

当接口只返回 ID 时，规则要求先读对应业务域 reference 换取可读名称（示例指向 `references/wecomcli-contact.md`），换不到就用自然语言描述对象，例如「某位同事」「该文档」（F-037）。用户直接索要 ID 时，按「内部字段不便提供」处理；但 `doc_url`、微盘分享链接这类**可读链接**不在限制范围内（F-038）。

这条规则常被误读为安全脱敏。实际上它放行可读链接，说明目标是**交付物对人可读**：ID 是机器标识符，出现在报告、消息与总结里既降低可读性，也把内部实现细节带进用户视野。把它理解为输出形态规范（类似排版规范）比理解为权限控制更准确，因此不能用「用户已授权」来豁免。

## 七、可复用的启动清单

```bash
# Step 1：版本门禁
wecom-cli --version
# 未安装或版本 < 1.2.1 时：
npm install -g @wecom/cli
wecom-cli --version

# Step 2：授权状态
wecom-cli auth show --status

# Step 3：仅在 unauthorized 时执行，扫码后复验
wecom-cli auth init --noninteractive
wecom-cli auth show --status

# 身份确认
wecom-cli identity whoami
```

实现时建议把上述命令封装为「检查 → 修复 → 复验」的幂等流程，任一步失败直接返回可执行的修复指令，不进入业务分支；同时把 `1.2.1` 抽为常量，避免三处文案漂移（F-106）。

## 延伸阅读

- [套件定位与依赖](00-overview.md)：Skill 与 `wecom-cli` 两条交付链的分工。
- [意图路由](02-intent-routing.md)：门禁通过后如何选择业务域。
- [references 分类学](03-references-taxonomy.md)：换取可读名称时应读哪篇域文档。
- [quickstart 示例](../examples/01-quickstart-with-preflight.md)：带前置检查的完整接入演练。