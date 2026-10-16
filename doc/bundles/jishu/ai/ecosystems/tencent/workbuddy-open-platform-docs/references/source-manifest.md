---
type: Reference
title: "WorkBuddy 开放平台开发者文档 · 页级采集与覆盖台账"
description: "D0～D10 共 11 个已声明 URL 的页级覆盖登记（URL、访问日期、页面标题、HTTP 状态与响应字节数、正文解析状态、知识归属文档、覆盖状态），含站点侧栏 17 篇 /docs/ 页逐条覆盖状态、非页面布局资源 layout-216c2d1532f8d94c 的显式排除依据，以及「已声明集合 = 已处理集合」双向差集为空（11 vs 11）与「侧栏 17 篇中已处理 10、未采集 7」的集合比对结论"
tags: [WorkBuddy, 开放平台, 开发者文档, 采集台账, 覆盖登记, OKF]
generated: { by: "process:seven-concepts-r", at: "2026-10-16" }
verified: { by: "process:seven-concepts-v", at: "2026-10-16" }
status: stable
stale_after: "2027-04-16"
sources:
  - { id: D0, resource: "https://open.workbuddy.cn/dashboard" }
  - { id: D1, resource: "https://open.workbuddy.cn/docs/what-is-open-platform" }
  - { id: D2, resource: "https://open.workbuddy.cn/docs/onboarding" }
  - { id: D3, resource: "https://open.workbuddy.cn/docs/monetization" }
  - { id: D4, resource: "https://open.workbuddy.cn/docs/skill" }
  - { id: D5, resource: "https://open.workbuddy.cn/docs/connector" }
  - { id: D6, resource: "https://open.workbuddy.cn/docs/expert" }
  - { id: D7, resource: "https://open.workbuddy.cn/docs/expert-team" }
  - { id: D8, resource: "https://open.workbuddy.cn/docs/buddy-app" }
  - { id: D9, resource: "https://open.workbuddy.cn/docs/third-party-app" }
  - { id: D10, resource: "https://open.workbuddy.cn/docs/openapi" }
---

# WorkBuddy 开放平台开发者文档 · 页级采集与覆盖台账

> 本台账记录**页级**覆盖：11 个已声明 URL 逐条登记，站点侧栏 `/docs/` 全集逐条登记。声明级覆盖见 `article-source.md`（F 编号事实），核验结论与五类口径分层见 `verification.md`。
> 全部数字取自 2026-10-16 的采集元数据（`pages[]` 与 `dashboard` 实测字段），用于证明可达性与解析状态；文档更新后字节数与会漂移，引用时须带核验时点。

## 一、采集方法与核验时点

- **核验时点**：2026-10-16（本束采集快照基准）。`stale_after` = 2027-04-16。
- **采集方式**：纯 HTTP GET（`Invoke-WebRequest`），**无登录会话依赖**，未注册开放平台账号、未申请任何认证与资质、未提交审核、未调用任何真实接口。11 个已声明 URL 全部返回 **HTTP 200**。
- **采集通道**：D1～D10 十篇 `/docs/` 页均为**服务端渲染**，纯 HTTP GET 即可取得正文，十页共用一个正文容器（容器类名 `prose-docs_root__dXUM0`，`div` 元素），未触发「受控浏览器渲染」通道切换——本次**无页面采集通道变化**。
- **登录依赖对比**：同组 `workbuddy-open-platform-sharing-and-promotion` 束的两篇平台公告位于 `/dashboard/contents/...`，需**已登录会话**方能读取渲染后正文；本束信源位于 `/docs/`，实测**无登录依赖**，两束的采集条件不同，不可互相套用。
- **导航面判定**：D0 `https://open.workbuddy.cn/dashboard` 实测 HTML **20,367 字节**，含 **8 个 `<script>`** 标签与 **1 个应用挂载点** → 判定为**客户端渲染的 SPA 外壳**，无可读文档正文；本束仅将其登记为**导航面**（核可达性），其登录后的工作台功能不在本束范围。

## 二、页级台账（11 行）

> 台账行以编号（D0～D10）标识，每行登记**七要素**：URL、访问日期、页面标题、HTTP 状态与响应字节数、正文解析状态、知识归属文档、覆盖状态。
> 「解析正文提取量」为正文容器可解析文本的字符数（`extract_chars` 实测值），用于证明该页正文**可解析**，**不等同于全文篇幅**，也不构成完整性判定。

| 编号 | URL | 访问日期 | 页面标题 | HTTP 状态与响应字节数 | 正文解析状态 | 知识归属文档 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D0 | <https://open.workbuddy.cn/dashboard> | 2026-10-16 | 开放平台首页（工作台）〔SPA 外壳，未取到文档级页面标题〕 | 200 / 20,367 B（含 8 个 `<script>`、1 个应用挂载点） | 无正文（SPA 外壳，仅达可达性与外壳特征） | `../index.md`「已知边界」；`../concepts/10-boundaries-versions-and-known-gaps.md` | 已登记（导航面，仅核可达性） |
| D1 | <https://open.workbuddy.cn/docs/what-is-open-platform> | 2026-10-16 | 开放平台概述 | 200 / 179,640 B | 服务端渲染，正文可读（解析正文提取量 416 字符） | `../concepts/00-overview-and-quickstart.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D2 | <https://open.workbuddy.cn/docs/onboarding> | 2026-10-16 | 入驻开放平台 | 200 / 196,648 B | 服务端渲染，正文可读（解析正文提取量 1,739 字符） | `../concepts/01-onboarding-and-qualification.md`；`../examples/00-onboarding-and-certification.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D3 | <https://open.workbuddy.cn/docs/monetization> | 2026-10-16 | 收入变现 | 200 / 204,634 B | 服务端渲染，正文可读（解析正文提取量 2,087 字符） | `../concepts/09-monetization-and-revenue.md`；`../examples/04-publish-and-manage-a-paid-asset.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D4 | <https://open.workbuddy.cn/docs/skill> | 2026-10-16 | 技能 | 200 / 203,841 B | 服务端渲染，正文可读（解析正文提取量 2,284 字符） | `../concepts/02-skill-development-and-marketplace.md`；`../examples/01-build-and-submit-a-skill.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D5 | <https://open.workbuddy.cn/docs/connector> | 2026-10-16 | 连接器 | 200 / 323,746 B | 服务端渲染，正文可读（解析正文提取量 13,675 字符） | `../concepts/03-connector-development-and-access-modes.md`；`../examples/02-build-and-submit-a-connector.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D6 | <https://open.workbuddy.cn/docs/expert> | 2026-10-16 | 专家 | 200 / 269,332 B | 服务端渲染，正文可读（解析正文提取量 11,006 字符） | `../concepts/04-expert-and-expert-team.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D7 | <https://open.workbuddy.cn/docs/expert-team> | 2026-10-16 | 专家团 | 200 / 286,687 B | 服务端渲染，正文可读（解析正文提取量 15,641 字符） | `../concepts/04-expert-and-expert-team.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D8 | <https://open.workbuddy.cn/docs/buddy-app> | 2026-10-16 | Buddy应用 | 200 / 357,854 B | 服务端渲染，正文可读（解析正文提取量 5,908 字符） | `../concepts/05-buddy-app-develop-and-publish.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D9 | <https://open.workbuddy.cn/docs/third-party-app> | 2026-10-16 | 第三方应用 | 200 / 334,620 B | 服务端渲染，正文可读（解析正文提取量 16,992 字符） | `../concepts/06-third-party-app-access.md` | 已学习（正文归纳覆盖，未逐字镜像） |
| D10 | <https://open.workbuddy.cn/docs/openapi> | 2026-10-16 | Open API 接口 | 200 / 422,451 B | 服务端渲染，正文可读（解析正文提取量 28,169 字符） | `../concepts/07-openapi-auth-and-conventions.md`；`../concepts/08-openapi-endpoint-catalog.md`；`../examples/03-oauth-and-call-openapi.md` | 已学习（正文归纳覆盖，未逐字镜像） |

> **体量分布**：D10（422,451 B / 解析正文提取量 28,169 字符）为 11 页中实测体量最大者；D1（179,640 B / 416 字符）与 D0（20,367 B / 无正文）为最小两页。上述字节数仅作可达性与形态登记，**不用于推断正文完整度或内容质量**。
> **标题口径**：页面标题取自实测页面标题字段，保留站点原始写法（如 D8 为「Buddy应用」、D10 为「Open API 接口」）；D0 为 SPA 外壳，未取到文档级页面标题，故标注为注释形式。

## 三、站点侧栏全集与覆盖状态（18 行）

> 核验时点从 `/docs/*` 各页 HTML 内嵌侧栏的 `/docs/` 链接命中集合提取。下表先列 **17 个 `/docs/` slug**（逐条含覆盖状态），再显式列出并排除 **1 项非页面布局资源**，合计 18 行。
> **登记纪律**：未采集页仅证明「该 slug 存在于站点侧栏」，**不得**据其名称推断功能细节。

| # | slug | 覆盖状态 | 对应台账编号 | 知识归属文档 |
| --- | --- | --- | --- | --- |
| 1 | `api-token` | 本次未采集，仅登记入口 | — | `../index.md`「已知边界」；`../concepts/10-boundaries-versions-and-known-gaps.md`（仅登记清单，不展开） |
| 2 | `buddy-app` | 已声明并处理 | D8 | `../concepts/05-buddy-app-develop-and-publish.md` |
| 3 | `connector` | 已声明并处理 | D5 | `../concepts/03-connector-development-and-access-modes.md`；`../examples/02-build-and-submit-a-connector.md` |
| 4 | `contact` | 本次未采集，仅登记入口 | — | `../index.md`「已知边界」；`../concepts/10-boundaries-versions-and-known-gaps.md`（仅登记清单，不展开） |
| 5 | `developer-profile` | 本次未采集，仅登记入口 | — | `../index.md`「已知边界」；`../concepts/10-boundaries-versions-and-known-gaps.md`（仅登记清单，不展开） |
| 6 | `expert` | 已声明并处理 | D6 | `../concepts/04-expert-and-expert-team.md` |
| 7 | `expert-team` | 已声明并处理 | D7 | `../concepts/04-expert-and-expert-team.md` |
| 8 | `layout-216c2d1532f8d94c` | **排除：非页面布局资源，不计入 `/docs/` 页面集合**（排除依据见下） | — | —（非页面资源，无知识归属） |
| 9 | `legal-basis-and-examples` | 本次未采集，仅登记入口 | — | `../index.md`「已知边界」；`../concepts/10-boundaries-versions-and-known-gaps.md`（仅登记清单，不展开） |
| 10 | `monetization` | 已声明并处理 | D3 | `../concepts/09-monetization-and-revenue.md`；`../examples/04-publish-and-manage-a-paid-asset.md` |
| 11 | `onboarding` | 已声明并处理 | D2 | `../concepts/01-onboarding-and-qualification.md`；`../examples/00-onboarding-and-certification.md` |
| 12 | `openapi` | 已声明并处理 | D10 | `../concepts/07-openapi-auth-and-conventions.md`；`../concepts/08-openapi-endpoint-catalog.md`；`../examples/03-oauth-and-call-openapi.md` |
| 13 | `operations-data` | 本次未采集，仅登记入口 | — | `../index.md`「已知边界」；`../concepts/10-boundaries-versions-and-known-gaps.md`（仅登记清单，不展开） |
| 14 | `service-categories-enterprise` | 本次未采集，仅登记入口 | — | `../index.md`「已知边界」；`../concepts/10-boundaries-versions-and-known-gaps.md`（仅登记清单，不展开） |
| 15 | `service-categories-individual` | 本次未采集，仅登记入口 | — | `../index.md`「已知边界」；`../concepts/10-boundaries-versions-and-known-gaps.md`（仅登记清单，不展开） |
| 16 | `skill` | 已声明并处理 | D4 | `../concepts/02-skill-development-and-marketplace.md`；`../examples/01-build-and-submit-a-skill.md` |
| 17 | `third-party-app` | 已声明并处理 | D9 | `../concepts/06-third-party-app-access.md` |
| 18 | `what-is-open-platform` | 已声明并处理 | D1 | `../concepts/00-overview-and-quickstart.md` |

### 3.1 非页面布局资源 `layout-216c2d1532f8d94c` 的排除依据

该命中出现在**每个** `/docs/*` 页面的 `/docs/` 链接命中集合中（在 D1～D10 十页的命中集合中恒等重现、不随页面内容变化），但**不是文档页**，故排除、**不计入**任何页面集合与覆盖率分母。判定依据（均为命名与出现方式层面的机械特征，未对其做过正文采集）：

1. **命名形态差异**：其形式为 `layout-` + 16 位十六进制串（`layout-216c2d1532f8d94c`），属前端构建产物的布局分片命名；而其余 17 项全部为词条式 kebab-case slug，两者形态不一致。
2. **出现方式差异**：它在 D1～D10 十页的 `/docs/` 命中集合中恒等重现（十个内容页的命中集合除 D5 多出 `api-token` 外完全一致），符合**页面模板级引用**的特征，而非随页面内容变化的文档条目。
3. **口径归一**：本束按已裁定的「站点侧栏 17 篇 `/docs/` 页」口径登记，非页面资源一律不计入页面集合。
4. **可复核性**：若后续需要确认其性质，应另立采集核实；**本束不据其名称或路径推断其内容与用途**，也不将其计入任何计数。

## 四、集合比对结论

| 项 | 值 |
| --- | --- |
| 本束已声明处理的 URL 集合 | 11（D0 导航面 + D1～D10 十篇 `/docs/` 内容页） |
| 已处理（取得采集结果）集合 | 11 |
| `已声明 − 已处理` | 0 |
| `已处理 − 已声明` | 0 |
| 双向差集 | **空**（`已声明页面集合 = 已处理集合`） |
| 站点侧栏 `/docs/` 页集合 | 17 |
| 其中已声明并处理 | 10（D1～D10） |
| 其中本次未采集，仅登记入口 | 7（`api-token` / `contact` / `developer-profile` / `legal-basis-and-examples` / `operations-data` / `service-categories-individual` / `service-categories-enterprise`） |
| `/docs/` 链接命中并集（去重后） | 18 = 17 篇 `/docs/` slug + 1 项非页面布局资源（`layout-216c2d1532f8d94c`） |
| 正文解析状态 = 正文可读（服务端渲染） | 10（D1～D10） |
| 正文解析状态 = 无正文（SPA 外壳） | 1（D0） |

**复核口径（如何用 `doc_links` 并集复现 18 个 slug）**：

1. 取采集元数据中 10 篇内容页（D1～D10）各自的 `/docs/` 链接命中集合字段 `doc_links`；
2. 对 10 个集合取**并集**、去重、按字典序排序 → 得 **18 项**（其中 `api-token` 仅出现在 D5 的命中集合中，其余 16 项在十页恒等重现）；
3. 从该 18 项中剔除非页面布局资源 `layout-216c2d1532f8d94c` → 得 **17 篇 `/docs/` slug**；
4. 将 17 篇与「已声明并处理」的 10 个 slug 求差集 → 得**未采集 7 篇**；与 D0（不在 `/docs/` 侧栏内，为独立导航面）合并，即本束 11 个已声明 URL 的完整闭环。

```python
# 复现口径示意（对采集元数据的 pages[].doc_links 取并集、去重、排序）
union = sorted({slug for page in pages for slug in page["doc_links"]})   # → 18 项
doc_slugs = [s for s in union if s != "layout-216c2d1532f8d94c"]        # → 17 项
uncollected = [s for s in doc_slugs if s not in DECLARED_10]            # → 7 项
```

> **结论**：`已声明页面集合 = 已处理集合`，双向差集为空；站点侧栏 17 篇 `/docs/` 页中已处理 10、本次未采集 7；非页面布局资源 1 项已显式排除。未采集 7 篇**只登记入口不求证能力**。

## 五、登记纪律

- **未采集 ≠ 不存在**：7 篇未采集页仅证明「该 slug 存在于站点侧栏」，**不得**据其名称（如 `api-token`、`operations-data`、`service-categories-*`）推断其功能细节、字段、权限或门槛。
- **区分「官方未发布该能力」与「本束未采集该页」**：前者由本束**不可断言**，后者如实标注为「本次未采集，仅登记入口」；不得把未采集写成不存在，也不得把未采集写成已核验。
- **文档未写明处一律标「官方未给」**：接口字段、限额、审核时长、结算比例、分成规则等文档未给出者，不得依据页面名称、同组其他束或常识补全。
- **不做替官方宣布的表述**：不得出现「已上线 / 已 GA / 已完成审核 / 功能已验证可用」类表述；本束信源为厂商官方开发者文档单源，未在本平台实跑任何开发、上架、审核或接口调用流程。
- **时效并列**：页面字节数、标题与字节量口径均绑定核验时点 2026-10-16；文档站未见统一版本号，版本与时效口径须与同组束并列登记（见第六节），不得择一。

## 六、指引入口（仅登记，不展开）

本束正文中「出现但未展开」的指事物，仅登记为入口，不做递归抓取与能力推断：

| 指事物类别 | 实例 | 本束处理方式 |
| --- | --- | --- |
| 站内文档页 | 未采集 7 篇 `/docs/` slug：`api-token` / `contact` / `developer-profile` / `legal-basis-and-examples` / `operations-data` / `service-categories-individual` / `service-categories-enterprise` | 仅登记 slug 与入口，不采集正文、不推断能力 |
| 平台工作台内部功能页 | `/dashboard` 登录后的资产、审核、收入等工作台功能页路径 | 未采集（D0 为 SPA 外壳，本束仅登记导航面）；同组 `workbuddy-open-platform-sharing-and-promotion` 束已登记 13 项平台模块地图，可交叉查阅 |
| 客户端版本要求 | 文档站未见统一版本号；并列登记为产品文档版本线与平台公告要求的客户端版本 | 并列登记、不择一、不展开：产品侧版本线见同组 `workbuddy-official-docs`，平台公告侧客户端版本门槛见同组 `workbuddy-open-platform-sharing-and-promotion` |
| 外部规范 | `MCP` 等第三方规范名（见 D5 章节骨架） | 仅登记规范名，未采集规范本体 |

> 上述指事物均**不在**本束的信源与事实编号范围内；如需其内容，应另立采集，不得以本台账登记充当已核验内容。
