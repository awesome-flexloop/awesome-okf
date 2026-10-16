---
type: Concept
title: "专家与专家团：单 Agent 资产与主理人编排团队的结构差异"
description: "WorkBuddy 开放平台「专家」（D6）与「专家团」（D7）的概念界定、目录树与 plugin.json 配置差异、主理人（lead）机制、Agent 定义文件与内置工具、内置 MCP 与连接器依赖、头像规范、行业分类与专家市场，事实区间 F-155～F-210。"
tags: [WorkBuddy, 开放平台, 专家, 专家团, 主理人, plugin.json, 腾讯]
generated: { by: "process:seven-concepts-e", at: "2026-10-16" }
verified: { by: "process:seven-concepts-v", at: "2026-10-16" }
status: stable
stale_after: "2027-04-16"
sources:
  - { id: D6, resource: "https://open.workbuddy.cn/docs/expert" }
  - { id: D7, resource: "https://open.workbuddy.cn/docs/expert-team" }
---

# 专家与专家团：单 Agent 资产与主理人编排团队的结构差异

> 本篇归纳 WorkBuddy 开放平台开发者文档 D6「专家」与 D7「专家团」两页（2026-10-16 采集，服务端渲染 `/docs/` 页正文，核验时点 2026-10-16），F 编号区间 **F-155～F-210**。信源为**厂商单源**开发者文档；**未在本机实跑**任何创建、打包、提交或上架流程。

## 一、专家与专家团分别是什么

- **专家**由「一份 `plugin.json` 核心配置文件 + 一个主 Agent 定义文件」构成，`expertType` 填 `"agent"`，基础结构目录树为 `.codebuddy-plugin/plugin.json`、`avatars/expert.png`、`agents/my-expert.md`、`README.md`（F-158、F-162）。
- **专家团**在专家结构之上引入**主理人（lead）编排**：`expertType` 填 `"team"`，目录树增加 `skills/`、`.mcp.json`、`bin/`、`settings.json`（★设置主理人）等，主 Agent 文件命名为 `{team}-team-lead.md`（F-192、F-193、F-198）。
- 两者共用同一套核心配置文件 `plugin.json`（同时承载**运行配置**与**市场展示信息**，F-159），共享展示字段分组、依赖声明方式、头像规范与「召唤前引导连接」机制（F-165、F-171、F-188、F-199）。
- 模板文件：专家为 `design-experts.zip`（F-191），专家团为 `trading-team.zip`（F-210）。

## 二、专家 vs 专家团结构差异对照表

| 维度 | 专家（D6） | 专家团（D7） | F 编号 |
| --- | --- | --- | --- |
| 资产类型标识 | 基础字段表 `expertType` 填 `"agent"`；类型字段表表述为 `"agent"` 或 `"team"` | `expertType` 填 `"team"` | F-162、F-163、F-198 |
| 主 Agent 命名 | `agentName` = `agents/` 下 MD 文件名（不含 `.md`），示例 `design-md-architect` | `agentName` = 主 Agent（主理人）名称，文件名为 `{team}-team-lead.md`；**名称须加专家团前缀，不可用通用 `team-lead`** | F-163、F-193、F-194 |
| 主理人机制 | 无 `teamInfo` 字段 | `teamInfo.leadAgent` 指定主理人、`memberAgents` 列出成员；`members[].role` 为 `lead`（主理人）或 `member`；目录树含 `settings.json`（★设置主理人）与 `avatars/team-lead.png` | F-164、F-192、F-200 |
| 目录树范围 | `.codebuddy-plugin/plugin.json`、`avatars/expert.png`、`agents/my-expert.md`、`README.md` | 扩展为多头像（`team.png`/`team-lead.png`/`member-a.png`/`member-b.png`）、多 `agents/*.md`，并含 `skills/`（可选共享技能）、`.mcp.json`（可选）、`bin/`（可选）、`settings.json`（★必须） | F-158、F-192 |
| 字段说明层级 | 基础字段 / 类型字段 / 展示字段 三组 | 基础字段 / 展示字段 / **专家团成员字段** 三组 | F-162、F-163、F-165、F-198、F-199、F-200 |
| 展示字段 `profession` | 职业头衔 | **必须与 `displayName` 保持一致** | F-165、F-199 |
| 「专家市场 / 行业分类」小节 | 页内设「专家市场」（含创建工具）与「行业分类」15 项 | 页内**未见**「专家市场」与「行业分类」两个小节（D7 页小节为：基础结构／配置文件／Agent 定义文件／内置 MCP 与连接器依赖／头像规范／模板文件）——**本条为本束对照观察，非 F 编号事实**，不得据其推断专家团分类规则 | F-155～F-157、F-190（D6 侧） |
| 模板文件 | `design-experts.zip` | `trading-team.zip` | F-191、F-210 |

## 三、基础结构（目录树逐字照抄原文）

专家（F-158）：

```
my-expert/
├── .codebuddy-plugin/
│   └── plugin.json
├── avatars/
│   └── expert.png
├── agents/
│   └── my-expert.md
└── README.md
```

专家团（F-192，★为必须）：

```
my-team/
├── .codebuddy-plugin/
│   └── plugin.json              # ★ 配置文件（必须）
├── avatars/                     # ★ 头像目录（必须）
│   ├── team.png                 #    团队头像
│   ├── team-lead.png            #    主理人头像
│   ├── member-a.png             #    成员头像
│   └── member-b.png             #    成员头像
├── agents/                      # ★ Agent 定义（必须）
│   ├── {team}-team-lead.md      #    主理人（名称须加专家团前缀，不可用通用 team-lead）
│   ├── member-a.md              #    成员 A
│   └── member-b.md              #    成员 B
├── skills/                      #    共享技能（可选）
│   └── {skill-name}/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── templates/
├── .mcp.json                    #    内置 MCP / 连接器依赖声明（可选，见第六节）
├── bin/                         #    可执行文件（可选）
├── settings.json                # ★ 设置主理人（必须）
└── README.md                    #    说明文档（推荐）
```

## 四、`plugin.json`：核心配置文件与字段说明

`plugin.json` 是专家（专家团）的**核心配置文件**，包含运行配置和市场展示信息（F-159）。专家侧完整示例（`name`/`version`/`description`/`author`/`agents`/`expertType`/`agentName`/`avatar`/`categoryId`/`plugin`/`displayName`/`profession`/`displayDescription`/`defaultInitPrompt`/`tags`/`quickPrompts` 各项取值）见原文事实 F-160、F-161；专家团侧完整示例见 F-194～F-197。下述为**专家团独有配置的逐字节选**（连续摘录自 F-194、F-196、F-200）：

```json
  "expertType": "team",
  "agentName": "trading-team-lead",
  "teamInfo": {
    "leadAgent": "trading-team-lead",
    "memberAgents": [
      "market-analyst", "fundamentals-analyst", "news-analyst", "sentiment-analyst",
      "bull-researcher", "bear-researcher", "research-manager", "trader",
      "aggressive-risk-analyst", "conservative-risk-analyst", "neutral-risk-analyst", "risk-manager"
    ]
  },
```

```json
  "members": [
    { "id": "trading-team-lead", "name": {"en":"Captain","zh":"队长"}, "profession": {"en":"Team Lead & Orchestrator","zh":"主理人"}, "avatar": "avatars/team-lead.png", "role": "lead" },
```

> 专家团示例的 `members` 数组共含 **13 个成员对象**，其中主理人 `role` 为 `"lead"`，其余 12 位为 `"member"`（F-200）；完整 13 行与 `agents` 数组 13 项路径见 F-195、F-200。

### 4.1 基础字段（专家 F-162 / 专家团 F-198）

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| name | ✅ | string | 专家唯一标识（小写字母 + 连字符，如 "design-experts"） |
| expertType | ✅ | string | 专家填 `"agent"`（F-162）；专家团填 `"team"`（F-198） |
| version | ✅ | string | 版本号（语义化版本，如 "1.0.0"） |
| description | ✅ | string | 英文简短描述（专家团侧为「一句话」，F-198） |
| author | ✅ | object | {name, email} 作者信息 |
| agents | ✅ | string[] | Agent 定义文件路径列表（如 ["./agents/my-expert.md"]） |
| agentName | ✅ | string | Agent 的名称（对应 agents/ 下的 MD 文件名，不含 .md）；专家团侧为「主 Agent 的名称」 |
| teamInfo | 专家团 ✅ | object | 见 4.2，仅专家团必备（专家侧为「team 时」字段） |
| skills | 否 | string[] | 技能目录路径列表（如 ["./skills/my-skill"]） |
| homepage | 否 | string | 项目主页 URL |
| license | 否 | string | 许可证 |
| keywords | 否 | string[] | 搜索标签 |

### 4.2 类型字段与 `teamInfo` 结构（F-163、F-164）

D6「类型字段」表：`expertType`（✅ string，`"agent"` 或 `"team"`）、`agentName`（✅ string，主 Agent 名称，对应 `agents/` 下 MD 文件名不含 `.md`）、`teamInfo`（team 时 object）。`teamInfo` 结构（逐字照抄原文）：

```
{
  "leadAgent": "主理人 Agent 名称",
  "memberAgents": ["成员A名称", "成员B名称", "..."]
}
```

### 4.3 展示字段（专家 F-165 / 专家团 F-199）

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| displayName | ✅ | {en, zh} | 市场展示名称 |
| profession | ✅ | {en, zh} | 职业头衔；**专家团侧必须与 `displayName` 保持一致** |
| displayDescription | ✅ | {en, zh} | 市场展示描述。中文字数须在 40-50 字之间，突出专家或专家团的核心能力 |
| avatar | ✅ | string | 头像路径（相对路径，如 "avatars/expert.png"） |
| categoryId | ✅ | string | 行业分类（专家侧原文标注「见第九节」） |
| defaultInitPrompt | ✅ | {en, zh} | 用户首次对话时的默认提示语。必须与 quickPrompts 的第一条保持一致 |
| plugin | ✅ | string | 关联的 Plugin 名称（与 name 字段值一致） |
| tags | ✅ | {en, zh}[] | 专家擅长领域标签（固定 3 个），用于搜索和市场展示 |
| quickPrompts | ✅ | {en, zh}[] | 推荐提示词（固定 3 个），展示在专家卡片上引导用户快速提问 |

> 专家团示例中 `tags` 实列 **4 项**（股票分析／投资决策／风险评估／多空辩论，F-197），与展示字段表「固定 3 个」的表述不一致——两处均按原文并列登记，不替官方判定。

### 4.4 专家团成员字段（F-200）

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| members | ✅ | array | 所有团队成员列表（含主理人） |

每个成员对象：

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| id | ✅ | string | 成员标识（对应 Agent MD 文件名，不含 .md） |
| name | ✅ | {en, zh} | 成员名称 |
| profession | ✅ | {en, zh} | 成员职业头衔 |
| avatar | ✅ | string | 成员头像路径 |
| role | ✅ | string | `"lead"`（主理人）或 `"member"`（成员） |

## 五、Agent 定义文件

Agent 定义文件放在 `agents/` 目录下，使用 Markdown 格式，文件头部用 YAML frontmatter 声明配置，正文为 Agent 的系统提示词（F-166）。Frontmatter 字段（F-167）：`name`（✅，与文件名一致不含 .md）、`description`（✅，英文，AI 用来判断何时激活）、`displayName`（✅，含 en 和 zh）、`profession`（✅，含 en 和 zh）、`maxTurns`（否，默认 50）、`skills`（否，预加载的技能名称列表）。

专家主 Agent frontmatter 示例（逐字照抄原文，F-168）：

```
---
name: design-md-architect
description: Design system document architect based on awesome-design-md standard
displayName:
  en: "Diana"
  zh: "黛安娜"
profession:
  en: "Design System Architect"
  zh: "设计系统文档架构师"
maxTurns: 100
---
```

- 专家团主理人示例 `agents/trading-team-lead.md`：`name: trading-team-lead`、`displayName {en:"He", zh:"何执舟"}`、`profession {en:"Chief Strategist", zh:"首席策略官"}`、`maxTurns: 200`（F-201）；正文职责为编排而非自做分析（F-202），并含协作铁律四条（F-203）、严禁行为五条（F-204）、团队分组表四组（F-205）、SOP 五阶段（F-206）、协作规则六条（F-207）。
- 成员示例 `agents/market-analyst.md`：`name: market-analyst`、`displayName {en:"Marco", zh:"Marco"}`、`profession {en:"Technical Analyst", zh:"技术分析师"}`、`maxTurns: 50`（F-208），正文指定分析维度与输出格式（F-209）。
- **工具**：开发者**不可自行添加 `tools`**，所有工具权限由系统统一分配（F-169）；系统内置工具含 Read／Write／Grep／Glob／Bash／WebSearch／WebFetch／AgentTool（主理人可用）／SendMessage（主理人可用）（F-170）。

## 六、内置 MCP 与连接器依赖（可选）

专家 / 专家团可声明运行时依赖的 MCP 服务或 WorkBuddy 已有连接器；声明后用户在**召唤前**会看到内联引导卡片逐个引导完成连接，连接完成后才进入对话；内置 MCP 连接后统一在「连接器 → 自定义连接器」中管理（F-171）。简单专家不需要依赖声明，只有必须调用外部 MCP 工具或企业连接器时才声明（F-172）。

- **声明方式**：通过 `plugin.json` 的 `dependencies` 字段声明，或放在插件根目录的 `.mcp.json` 中（F-173）；方式一示例（逐字照抄原文，F-174）：`"dependencies": { "mcpServers": "./.mcp.json", "connectors": ["tencent-docs", "feishu"] }`；`dependencies.mcpServers` 类型为 `string` 或 `string[]`，`dependencies.connectors` 为 WorkBuddy 已有连接器 ID 列表（F-175）。
- **方式二（兜底）**：`plugin.json` 未声明 `dependencies.mcpServers` 时，系统自动读取插件根目录的 `.mcp.json`，格式与标准 MCP 配置一致，每个 server 下可附加 `x-workbuddy` 元信息（F-176）。
- **MCP 服务基础字段**（F-177）：`url`（远程 MCP SSE / Streamable HTTP 地址）、`type`（传输类型如 `"http"`，远程 SSE 可省略）、`headers`（Token 鉴权用 `${VAR}` 占位，如 `Bearer ${SIYUAN_TOKEN}`）、`x-workbuddy`（私有展示与鉴权元信息，不写入用户最终连接器配置）。
- **`x-workbuddy` 元信息**（F-178）：`displayName`（LocalizedString，不填回退 server 名）、`description`（不填回退 url）、`icon`（支持 `https://`、`data:` URL 或相对插件根目录路径，推荐放 `avatars/`）、`auth.type`（`"oauth"` / `"token"` / `"none"`）、`auth.tokenSchema`。
- **LocalizedString 约定**（F-179）：文案字段可写纯字符串或 `{ zh, en }` 双语对象，双语时按界面语言展示、缺失语言回退 `zh` → `en`。
- **Token 类型鉴权**（F-180～F-182）：`auth.type: "token"` + `tokenSchema` 声明表单，用户点击「连接」后弹出统一 Token 授权弹窗，值回填到 `headers` 的 `${VAR}` 占位；`tokenSchema` 字段为 `title` / `description` / `docUrl`（非文案）/ `docLabel` / `fields`，`fields` 每项含 `key` / `label` / `placeholder` / `type`（`"text"` 或 `"password"`）/ `required` / `description`。
  - `tokenSchema` 字段说明（F-181）：`title`（LocalizedString，弹窗标题）、`description`（LocalizedString，弹窗说明）、`docUrl`（string，帮助文档链接，非文案不做本地化）、`docLabel`（LocalizedString，帮助链接展示文案）、`fields`（array，表单字段列表）。
- **连接器依赖**（F-183）：依赖 WorkBuddy 已上架连接器时，在 `dependencies.connectors` 中列出连接器 ID 即可，引导卡片信息由连接器自身提供。
- **注意事项**（F-184～F-187）：
  - ① `x-workbuddy` 写入用户配置时**被剥离**，不污染本地 `mcp.json`；
  - ② 已连接过的依赖再次召唤同名专家时**不会重复引导**（F-185）；
  - ③ **安全红线**：**Token 填写后由用户本地保存；专家包内严禁硬编码任何真实 Token / 密钥**（F-186）；
  - ④ `icon` 相对路径基于「该 MCP 声明文件所在目录」解析。

> 依赖声明小节在 D6 与 D7 两页**同文并列**（F-171～F-187 的来源代号均为 `D6、D7`），故本节不区分两页分别陈述。

## 七、头像规范（F-188）

| 项目 | 要求 |
| --- | --- |
| 格式 | PNG（推荐）或 JPG |
| 尺寸 | 512×512 px（正方形） |
| 大小 | 单张不超过 500KB |
| 风格 | 统一的漫画/插画风格，专业自然 |
| 内容 | 符合角色定位，不含违规内容 |

存放位置（F-189）：所有头像放在 `avatars/` 目录下，`plugin.json` 中使用相对路径引用；专家侧为单张 `expert.png`，专家团侧示例含 `team.png`、`team-lead.png` 与各成员头像。

## 八、行业分类（F-190）

选择最匹配的 `categoryId` 填入 `plugin.json`，共 **15 项**：

| categoryId | 分类名称 | 说明 |
| --- | --- | --- |
| 01-ProductDesign | 产品设计 | 产品管理、UI/UX、品牌设计、需求分析 |
| 02-Engineering | 技术工程 | 前后端开发、架构、DevOps、安全 |
| 03-GameSpatial | 游戏空间 | 游戏设计与开发、VR/AR/MR、空间计算 |
| 04-DataAI | 数据智能 | 数据分析、机器学习、知识管理、AI 应用 |
| 05-MarketingGrowth | 营销增长 | 广告投放、SEO/SEM、增长黑客、内容营销 |
| 06-ContentCreative | 内容创作 | 文案写作、视频制作、设计创意、多媒体 |
| 07-SalesCommerce | 销售商务 | 客户开发、销售策略、电商运营、BD |
| 08-FinanceInvestment | 金融投资 | 投资分析、风险管理、量化交易、财务 |
| 09-OperationsHR | 运营人力 | 运营策略、人力资源、行政管理、培训 |
| 10-ProjectQuality | 项目质量 | 项目管理、质量保证、测试、流程优化 |
| 11-SecurityCompliance | 法务安全 | 信息安全、合规审计、法律咨询、风控 |
| 12-IndustryConsultant | 行业顾问 | 行业咨询、战略规划、专业服务、供应链 |
| 13-TencentZone | 腾讯专家 | 由腾讯内部部门提供的专家，腾讯云、微信小程序、企业微信等腾讯技术栈 |
| 14-WorldWise | 全球发展 | 国际化业务、跨境贸易、全球市场洞察、海外拓展 |
| 15-Education | 教育学习 | 教育培训、在线学习、课程设计、学术研究、知识传播 |

专家团页**未见**「行业分类」小节（本束对照观察，非 F 编号事实）；专家团示例 `categoryId` 取值为 `"08-FinanceInvestment"`（F-194），沿用同一套取值，但**官方未给**专家团分类的独立规则清单。

## 九、专家市场（F-155～F-157）

- **展示位置**：专家展示在 WorkBuddy 客户端——点击左侧菜单【专家·技能·连接器】出现二级菜单，选择【专家】进入【专家市场】，点击横向二级 Tab【专家团】即可切换到【专家团市场】（F-155）。
- **用户交互**：点击对应专家/专家团弹出专家详情；点击【召唤专家】跳转对话框调用（F-156）。
- **专家创建工具**：点击市场右上角【我的专家】-【创建专家】/【创建专家团】，跳转进入对话补全提示词、开启创建（F-157）。
- 该小节在专家团页（D7）**未见**（见第二节对照表末行）；扩展阅读「开放平台解析失败原因」指引**未编入 F 编号**，此处仅作入口登记。

## 十、文档缺陷提示（勘误 E3）

D6 / D7 正文存在**悬空章节引用**，属文档内部引用缺陷：D6 出现「行业分类（见第九节）」「x-workbuddy 元信息（见 6.3）」「auth.tokenSchema …（见 6.4）」；D7 出现「.mcp.json …（可选，见第六节）」「（见 6.3）」「（见 6.4）」。上述「见 6.3 / 6.4 / 第六节 / 第九节」类**编号引用**在正文缓存中**找不到对应编号章节**，**不得据编号推断被引用内容**，需要其内容时应回源官方页面另行采集。处置依据见[核验报告 · 勘误清单 E3](../references/verification.md)。

> 事实登记、口径分层与页级覆盖分别见[来源代号与 F 编号事实登记](../references/article-source.md)、[核验报告](../references/verification.md)、[页级采集与覆盖台账](../references/source-manifest.md)。
