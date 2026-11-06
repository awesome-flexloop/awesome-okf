# 变更日志

## 2026-11-06

- 使用 `/七概念`（`seven-concepts-cmd`）执行**知识沉淀/方法论**链路：**R → I → E → V → C（入库）**。场景识别依据：全面学习一篇公开文章并沉淀为可迁移教程。
- **启动协议**：从磁盘回读 `AGENTS.md` 原文，确认「启动协议 / 文档边界 / 内容敏感度预检」三锚点；三层路由为根 → `projects/AGENTS.md` → `projects/awesome-okf-xs/AGENTS.md`，并读取 `frontmatter.md`、`global-core-rules.md`、`bundle-structure.md`、`check-bundles-index.py` 等子项目规范。
- **内容敏感度预检**：主源 URL 含 `share_code` / `utm_psn`，判定为**分享追踪参数**而非 `share?code=`、`token=`、`invite=` 类访问控制凭据；文章为公开知乎专栏、无登录墙、正文可完整获取 → **Public**，走标准工作流入 `doc/bundles/`，不进 `playground/`，不创建公共 spec。
- **落位（I/E）**：源文主题是 AI 漫剧产业结构、OPC 与注意力经济，**不是** AI 工具实操教程；按 `doc/bundles/index.md` 判为 `sheke/industry/`「AI 行业与商业趋势」，新建 `ai-comic-drama-opc-transition`，采用 `index.md` / `log.md` / `concepts/` / `examples/` / `references/` 结构。

### R · 事实采集（G1）

- 提取主源全文，登记元信息、章节结构、三位受访者与平台方发言；建立 **F-001~F-062** 台账，连续无跳号、共 62 条。
- 因果句一律改写为陈述句并在「分类」列标 `作者判断`；事实层与主张层分离，按 **A 平台方公开口径 / B 受访者自述 / C 记者判断 / D 假设计算** 四层登记。
- 源文字词瑕疵不进 F 台账，统一移入核验报告 E-01（「人参参与到」「二原来你做一个」「投多少都都做不出头」等）。
- 外部交叉核验覆盖：2026 阅文创作大会时间地点（10-16 杭州）、侯晓楠身份与原话、DramaBuddy 升级 OPC 一站式平台、签约 5000 多个个人及个人工作室、前十大 OPC 年收入破 100 万、REDTEN / 玛尔芙依德（Malfoid）事件、平台侧 4.3 亿元 / +230% / 660 部破千万 / 107 部破亿等并列指标。深链不固化，记录「发布主体 + 指标名 + 时点 + 结论」四元组。

### I · 洞察 / E · 萃取

- 五条洞察均按**四元组**（陈述 / 证据 / 反常识 / 下次行动）书写，并显式给出失效条件；可迁移模式为「要素替代三段式」「瓶颈迁移判据」「总量/分配两层模型」「职能上移检查表」「预测四步降级」。
- **信源先行**：先落盘 `references/`（事实台账 → P0 核验报告 → 信源清单 → 目录索引），再写 `concepts/`，保证每篇洞察都能挂回 F/E 编号。
- **P0 核验**：22 项结论 **✅9 / ⚠️7 / ⭕6 / ❌0**；无确定事实错误，但存在 3 处口径张力与 2 处「把预测写成事实」风险 → 全包 `status: flagged`。
- **E-01~E-12 入库必标勘误**：文本校勘、30 倍人效的部/人口径、总流水与单部爆款分母冲突、「降 90%」抹掉「不止」、预测非事实、亏损率无分母、出海 9 月为预估、假设计算非实测、玛尔芙归属与首发、平台口径主体与时点、总量/分配层面混淆、批量剧/精品剧路线口径。
- **操作可复现性两问**：主文无输入输出样例、无版本、无可复现步骤 → `examples/` 不生成操作型示例或行动建议，只保留**可复算算例**与**判据清单**，并显式标注为编者构造。

### V · 对抗性审查（G2/G3/G4 与 V 门）

四视角 + 编者视角共 **6 条具体攻击意见，采纳 4 条、部分采纳 1 条**：

| 视角 | 处置 |
|---|---|
| 魔鬼代言人 · 两种叙事不独立 | ✅ 采纳：`concepts/04` 增设「利益立场检查」，平台与机构叙事分别标注主体，不合并计为独立印证 |
| 魔鬼代言人 · 平台增长数据与「无生存土壤」冲突 | ✅ 采纳：上升为 E-11，`concepts/03` 建立 L1 总量 / L2 分配两层模型 |
| 新人 · 「内容判断力」易被读成可培训写稿技能 | ✅ 采纳：`concepts/02` 首节即区分生产能力 / 筛选能力 / 可培训性 |
| 老板 · 据「机构无价值」裁撤会忽略非制作职能 | ✅ 采纳：`concepts/04` 增加六项组织职能清单，结论限定回制作环节 |
| 未来 · 「很快」与「3~5 年」时间尺度冲突、预测不可证伪 | 部分采纳：写入 E-05，并在 `concepts/05` 展开四步降级与 2027 事后检验清单 |
| 编者 · 模板化「如何转型 OPC」会把 flagged 预测变成行动指令 | ✅ 采纳：`examples/` 只保留算例与判据，不含建议 |

- G1 事实清单无因果词、G2 洞察四元组完整、G3 模式均给出 ≥1 个非本领域迁移验证、G4 行动项原子化（本场景不产出行动建议，行动项限于「引用纪律」与「事后检验观察项」）。

### C · 原子提交（入库）

- 落盘 **16 个 `.md`**：根 `index.md`、`log.md`、`concepts/` 7 个（index + 00~05）、`examples/` 3 个（index + 01~02）、`references/` 4 个（index + 3 篇参考）。
- 修复 `concepts/01` 与 `concepts/02` 中 `../../examples/` → `../examples/` 的相对路径错误。
- 三级索引注册：分组 `sheke/industry/index.md`（导航表新增一行、`42 束 → 43 束`、toctree 新增条目）、域 `sheke/index.md`（`industry 42 → 43`）、总索引 `doc/bundles/index.md`（`total_bundles / 计数行 / sheke 节标题 / Mermaid / industry 表行`）。
- **计数基线说明**：本次开工前总索引已被并行会话从 712 更新至 713 且五面一致；新 bundle 补齐根 `index.md` 后目录树才计入 1 束，故本次目标为 **714 束 / sheke 92 / industry 43**，以 `scripts/check-bundles-index.py` 的目录树地面真值为准。
### 质量门（收口）

- `invoke` 集合因环境缺 `invocations` 包元数据无法加载（`PackageNotFoundError: No package metadata was found for invocations`）；按仓库既有惯例绕过 invoke，直接运行 `scripts/` 下与 `gates.*` 同一实现的官方脚本。
- `scripts/check-bundles-index.py`：**通过**，9 域 / 64 组 / **714 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致。
- `scripts/check-utf8.py`：**通过**，`doc/` 下 12907 个文件均为有效 UTF-8。
- `scripts/check-toctrees.py`：全量报 **1 处**——并行会话在途束 `doc/bundles/jishu/ai/products/wechat-intelligence-hub` 缺 `index.md`；**本束 16 个文件零命中、全部可达、目录清单一致**。按仓库惯例不修他方在途束，仅在此注记。
- `scripts/check-asset-baseline.py`：本次计数变更引出的「规模数字矛盾」已消除——同步 `doc/index.md`、`README.md`（713 → 714、sheke 91 → 92、industry 42 → 43、合计 713 → 714）；余 1 项「行尾归一失效」为工作区存在大量未提交改动所致（脚本明确要求先提交或 stash 后复跑），非本束引入。
- `scripts/check-section-anchors.py`：全库既存 6500+ 处锚点/路径告警，**本束零命中**。
- `check-utf8` / `check-toctrees` / `check-bundles-index` / `check-asset-baseline` 四个 `--self-test` 探针 **4/4 通过**。
- **环境限制**：`pytest` 与 `sphinx` 未安装 → `gates.redline` 与 `invoke build` 无法在本环境执行；需在装有项目依赖的环境中补跑。
- **手动补充校验**：本束 16 个 `.md`、114 个本地相对链接零断链（含两处 `../../examples/` → `../examples/` 修复）；F-001~F-062 与 E-01~E-12 引用全覆盖且无越界；无 `file://` 或家目录绝对路径泄漏；12 个内容文档 `type` 字段齐备，三层 `index.md` 与 `log.md` 保留文件名无 frontmatter，根 `index.md` 带 `okf_version: "0.2"`。
- 未执行 Git 提交，等待用户明确提交请求。
