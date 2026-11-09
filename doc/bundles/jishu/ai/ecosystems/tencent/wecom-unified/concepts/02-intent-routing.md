---
type: concept
title: 意图路由
description: 说明 SKILL.md 如何把自然语言意图与链接特征分流到 14 个业务域，并强制转读对应 reference 后再构造命令。
tags: [wecom, wecom-unified, routing]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-unified/
  - resource: /references/facts.md
---

# 意图路由

`wecom-unified` 的核心不是「会调用哪些接口」，而是「如何稳定地把一句话分到正确的业务域」。`SKILL.md` 用一个三步规则定义了这件事：判断意图所属业务域 → 读取该域 reference 文件 → 按其中参数规范构造命令；句末是硬性禁令「严禁凭路由表描述或自身记忆猜测拼参数」（F-023）。路由因此不是分类表演示，而是取参数的强制前置动作。

## 一、路由的三步与一个禁令

| 步骤 | 动作 | 产物 | 失败后果 | 证据 |
|---|---|---|---|---|
| 1 | 判定业务域 | 一个域标识（如 `sheet`） | 域错则后续全错 | F-023 |
| 2 | 读取该域 reference | 参数契约与操作细则 | 跳过则参数靠猜 | F-023、F-040 |
| 3 | 按契约构造命令 | 可执行的 `wecom-cli` 调用 | 参数缺失或类型错误 | F-023 |
| 禁令 | 不得凭描述/记忆拼参数 | — | 命令被服务端拒绝或产生误操作 | F-023 |

这条禁令针对的是一种典型失败：模型记得「大概有这么个接口」，于是把 `docid`、`sheet`、`range` 之类的字段按直觉拼出来。企业微信接口对字段名、必填性与取值格式要求严格，猜测往往表现为「命令能跑但结果不对」，比直接报错更难排查。

## 二、触发信号：描述与链接

`SKILL.md` 的 frontmatter `description` 本身就是触发器清单，明确规定两类链接「必触发」：包含 `doc.weixin.qq.com` 或 `page.weixin.qq.com` 的链接，以及包含 `drive.weixin.qq.com` 的链接（F-021）。这解决了一个常见歧义：用户只贴一条链接、不说明要做什么时，宿主也应进入本 Skill，而不是泛泛回答「我可以帮你处理文档」。

链接特征与业务域存在稳定的对应关系，可作为路由的第一层判据：`doc.weixin.qq.com/doc/...` 指向 doc 域，`/sheet/` 指向在线表格，`/smartsheet/` 或 `s3_` 前缀指向智能表格，`/smartpage/` 或 `page.weixin.qq.com/smartpage/...` 指向智能文档，`drive.weixin.qq.com` 指向微盘。链接无法判定时，再退回语义判据。

## 三、14 个业务域

`SKILL.md` 的「业务域概览」包含 14 个 `###` 小节，依序为 contact、doc、doc-manage、sheet、smartsheet、smartpage、pptx、calendar、meeting、todo、disk、email、message、media，每个小节都以一行 `→ 详见 references/wecomcli-<域>.md` 收尾（F-039、F-040）。

| # | 业务域 | 职责摘要 | 域入口文件 |
|---|---|---|---|
| 1 | contact | 按姓名、拼音、英文名、别名搜索人员，为人名解析内部标识 | `wecomcli-contact.md` |
| 2 | doc | 在线文档新建（生成 `.docx` 后导入）、读取、追加、覆盖 | `wecomcli-doc.md` |
| 3 | doc-manage | 文档搜索、改名、成员与权限管理；不负责正文 | `wecomcli-doc-manage.md` |
| 4 | sheet | `/sheet/` 在线表格与本地 Excel/CSV/TSV 处理 | `wecomcli-sheet.md` |
| 5 | smartsheet | `/smartsheet/` 智能表格的结构、记录、视图与图表 | `wecomcli-smartsheet.md` |
| 6 | smartpage | 智能文档页面、Block 编辑、数据驱动页面 | `wecomcli-smartpage.md` |
| 7 | pptx | 在线幻灯片生成、编辑、导入；仅在线链接，无导出 | `wecomcli-pptx.md` |
| 8 | calendar | 日程、忙闲、会议室；不含在线会议链接 | `wecomcli-calendar.md` |
| 9 | meeting | 在线会议、纪要、待办与转写 | `wecomcli-meeting.md` |
| 10 | todo | 待办创建、完成、查询与更新 | `wecomcli-todo.md` |
| 11 | disk | 微盘空间与文件 | `wecomcli-disk.md` |
| 12 | email | 邮件发送、回复、转发、搜索与安全 | `wecomcli-email.md` |
| 13 | message | 消息收发 | `wecomcli-message.md` |
| 14 | media | 媒体文件下载与本地读取 | `wecomcli-media.md` |

## 四、歧义判据

路由的主要难点不在「分不出来」，而在「几个域都能沾边」。`SKILL.md` 对高频歧义给出了明确判据：

| 场景 | 判据 | 落域 | 证据 |
|---|---|---|---|
| 「表格」 | 明确说「在线表格」或链接含 `/sheet/` → sheet；说「智能表格 / 导入成智能表格」、链接含 `/smartsheet/` 或 `s3_` 前缀 → smartsheet；**泛称表格默认 smartsheet** | 二者之一 | F-043 |
| 新建文档未指定品类 | 默认智能文档（smartpage）；仅明确 doc 或 `doc.weixin.qq.com/doc/` 链接才走 doc | smartpage / doc | F-044 |
| 只给文档名称要读写正文 | 先走 doc-manage 搜索定位，再回正文域 | doc-manage → 正文域 | F-044 |
| 要「做个 PPT / 汇报材料」 | 进入 pptx；交付只有在线链接，**没有任何导出能力** | pptx | F-041 |
| 智能表格写入返回 `851003` / `no authority` | 按 smartsheet 域流程改用 Webhook 兜底 | smartsheet | F-042 |

其中两条最容易被忽略。第一，「泛称表格默认智能表格」与直觉相反——多数人会把「表格」理解为 Excel 式在线表格，但套件把默认值给了 smartsheet，只有在用户明确说「在线表格」或给出 `/sheet/` 链接时才切到 sheet（F-043）。第二，doc 域的新建流程是「生成 `.docx` → 导入」，而不是直接在线创建；同时 doc-manage 只做搜索、改名、成员与权限，**不负责正文读写**，把这两件事混在一个域里会导致「找到了文档却改不了内容」（F-044）。

## 五、路由后的自检

完成分流后，建议在构造命令前做三项自检：

1. **是否读到了域入口**：不是「知道文件名」，而是实际读取了 `references/wecomcli-<域>.md`，并按其中的接口路由表继续下钻到细则（F-040）。
2. **是否误用了其它域的默认值**：例如把「表格」默认成 sheet、把「创建文档」默认成 doc，都是与 `SKILL.md` 相反的判断（F-043、F-044）。
3. **是否越过了能力边界**：pptx 无导出、sheet 导出在第一步拒绝、doc-manage 不碰正文，这些边界写在各域文档中，路由阶段就应识别并直接告知用户，而不是调用后再失败（F-041）。

路由层的质量指标也应随之改变：不要只看「最终命令是否成功」，而要看「是否读取了目标域 reference」。前者可能靠试错蒙对，后者才是可复现的能力。

## 延伸阅读

- [套件定位与依赖](00-overview.md)：`SKILL.md` 在整体架构中的位置。
- [references 分类学](03-references-taxonomy.md)：分到域之后，如何继续定位到具体细则。
- [前置检查与身份](01-preflight-and-identity.md)：路由之前的门禁条件。
- [sheet 转 PPT 示例](../examples/02-sheet-to-ppt-pipeline.md)：一次跨 sheet 与 pptx 两域的路由演练。