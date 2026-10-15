# 变更日志

> 倒序结构：新条目加在上方，日期标题格式为 `YYYY-MM-DD`。

## 2026-10-15 - V 阶段机械门禁与索引基数观测

- ✅ **Task 7 机械门禁全部通过**（在子模块 `projects/awesome-okf-xs/` 根目录直接运行底层脚本）：`python scripts/check-utf8.py` 退出码 **0**（11611 个文件均为有效 UTF-8）；`python scripts/check-toctrees.py` 首次运行退出码 **0**（本束相关项零命中），复跑时因**并行在途新束** `workbuddy-hardware-integration-whitepaper`（25 项「未收录/不可达」+ 缺 `index.md`，非本束）退出码转为 **1**——**本束相关项仍零命中**，按归属隔离**不修**；本束 14 个 `.md` 的全部 **71 条**相对链接逐一 `Test-Path` **全部存活**（失败 0）；零 `file:///`、零 `C:\Users`；14 文件 frontmatter 与 `okf_version` 位置合规（仅根 `index.md` 含 `okf_version`；`log.md` 与三个子目录 `index.md` 无 frontmatter）；`facts.md` 与 `article-source.md` 的 `F-\d{3}` 唯一集合均为 **64**、差集为空、连续 F-001~F-064、无重复；定向 Sphinx dummy 构建退出码 **0**、未引入本束相关错误（其余既有 WARNING 按归属隔离不修）。四视角对抗审查完整版已并入 `references/verification.md` 第七节。
- ⚠️ **索引基数观测（披露不修复）**：`tencent/index.md`「关于本分组」的「信源」基数为 **64**（本次按既有先例记增量 **+4**，即 64 → 68），该基数**无法由任何显式口径复现**。本会话机械复测：15 束根 `index.md` 的 `sources` 条目合计 **77**、`references/` 下 `.md`（去 `index.md`）合计 **60**；**排除本束后的 14 束恰为 73 / 57**——即 Task 6 所述「实测 73」「实测 57」系**未含新束**口径。基数 64 / 68 疑为**历史口径或并行在途演进**所致；本次**只记增量 +4、未重定基数**，不顺手修复（归属隔离）。

## 2026-10-15 - 初始版本

- ✅ 按七概念知识沉淀链路 `R→I→E→V` 完成（场景 4：知识沉淀；骨架按「平台公告教程化」判定为 `index + concepts + examples + references + log`）。
- ✅ 内容敏感度预检：`open.workbuddy.cn` 为腾讯 WorkBuddy 官方开放平台的**公开发布通知**（无访问控制、无 `code/token` 私域参数），判定**公开内容（Public）**，走标准工作流；spec 位于主仓 `.trae/specs/okf-wiki-ecosystem/workbuddy-open-platform-sharing-and-promotion-okf-wiki/`（spec.md / tasks.md / facts.md，Review 后补 review.md）。

### 七阶段执行

- **R（采集与编号）**：经受控浏览器在**已登录会话**中读取渲染后正文（`document.body.innerText`），取得 **A1（分享能力接入）、A2（推广管理）两篇公告完整正文**（非摘要、非截断，发布日期均 2026-10-14、栏目「平台公告」）；采集平台导航面 N1（`https://open.workbuddy.cn/`）、N2（`/dashboard`）可达性；从公告页侧边栏提取平台**模块地图 13 项**入口。产出 spec `facts.md` 与本束 `references/source-manifest.md`。
- **I（事实与核验）**：登记 **F-001 ~ F-064 共 64 条**编号事实（自本束起编，不与他束编号体系混合），编号连续无跳号无重复；产出 `references/article-source.md`（来源代号表 A1/A2/N1/N2 + 64 行事实表，与 `facts.md` 机械双份）与 `references/verification.md`（核验总表、勘误清单、五类口径分层并列登记表、信源距离评估、V 四视角对抗审查表、status 裁决）。
- **E（concepts + examples）**：产出 `concepts/`（`index.md` + `00-open-platform-overview` / `01-share-capability-integration` / `02-promotion-management` / `03-boundaries-versions-and-policy` 四篇，含 1 张接入链路 Mermaid 图）与 `examples/`（`index.md` + `00-integrate-share-capability` / `01-create-and-track-promotion` 两篇，四段结构「前置条件 / 操作步骤 / 结果判据 / 限制与边界」，未实跑处逐段标注）。
- **V（门禁与审查）**：本 Task 完成根 `index.md` 与 `log.md` 收口并核对三个子目录 `index.md` 的 toctree 条目完整性；机械门禁脚本运行与四视角自审在后续 Task 执行（见下方「门禁运行方式」）。

### 覆盖统计

| 项 | 值 |
| --- | --- |
| 公告正文 | A1、A2 两篇**完整正文**（非摘要、非截断） |
| 平台导航面 | N1、N2 均可达（仅核可达性） |
| 平台模块地图 | **13 项**入口，逐行标注「本次未采集，仅登记入口」（F-003 ~ F-016） |
| 编号事实 | **F-001 ~ F-064，共 64 条**（N-map 16 / A1-share 17 / A2-promotion 23 / X-policy 8） |
| 页级台账 | 声明处理页面集合 4 = 已处理集合 4，双向差集为空 |
| Markdown 文档 | **14 个**（根 `index.md` + `log.md` + concepts 5 + examples 3 + references 4） |

### 口径决策（五类分层并列，一律不得抹平）

1. **公告口径 vs 平台现状**：公告仅宣布能力上线，**未**给出接口字段、请求参数、响应格式、错误码、鉴权/签名算法、审核细则、限流/配额数字（F-061）——如需接口级内容须另立新束学习《PC 端开发手册》（F-062），不据公告推断。
2. **端边界**：分享能力接入**当前仅 PC 端**（Windows/macOS，F-030）；移动端（Android/iPhone/鸿蒙）公告原话「将陆续开放」属**规划态**（F-031），不写成已支持；与 A2 推广分享链接可在移动端打开（F-044）为两条不同能力。
3. **资产与付费边界**：专家/技能支持「分享链接 + 小程序码」（F-051）；连接器**暂时仅**支持分享链接（F-052）；Buddy 应用分享功能**正在规划中**（F-053）；免费资产两种（F-054），付费资产**暂时仅**支持分享链接（F-055）。
4. **版本时效与落差**：两篇公告 2026-10-14 / 均要求 **5.8.0**（F-058）；同组 `workbuddy-official-docs` 束核验文档线止于 **5.7.7（2026-10-08）**（该束事实 081/082/042 号，对应本束 F-059、F-060）——「公告先行于产品文档版本线」，**两口径并列、不择一**（与同组 `wecom-5-0-12-release`、`workbuddy-official-docs` 先例一致）。
5. **开放门槛**：分享能力接入面向**已通过企业认证的开发者**（F-029），公告未展开认证流程细节（F-063），不写成对任意个人开发者开放。

### 门禁运行方式

- **运行方式**：门禁在 git 子模块 `projects/awesome-okf-xs/` **根目录**直接运行底层脚本——`python scripts/check-utf8.py`（UTF-8 严格 roundtrip）、`python scripts/check-toctrees.py`（toctree 条目可达）、`python scripts/check-bundles-index.py`（五级索引计数一致）。
- ⚠️ **`invoke gates.*` 未运行**（子项目可选文档依赖 `invocations` 未确认安装）；**不声称**运行过 `invoke gates.*`，一律以直接运行底层脚本为准。
- ⚠️ 采集与复算过程中的临时产物（抓取缓存、合并/复算脚本）位于工作区外，未落入仓库；`facts.md` 为 spec 目录工作产物。
- ⚠️ 并行在途观测：同组索引可能被并行会话实时改写；若观察漂移，仅在 `log.md` 披露观测事实，不顺手修复（归属隔离）。

### 独立评审结论

- **留位（待填）**：独立上下文评审（R1）结果、检查点与量规评分待 Task 8 执行后回填本区，并接入 `review.md`。
