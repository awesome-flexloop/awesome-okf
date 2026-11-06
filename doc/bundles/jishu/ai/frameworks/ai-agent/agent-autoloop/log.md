# 变更日志

## 2026-11-06 · 知识包创建

- **来源**：微信公众号「数字生命卡兹克」2026-11-04 08:19 原创开源公告《开源我这折腾了1年的「Agent自动化系统」，愿所有人都能感受Agent的魅力。》；权威核验源为 `github.com/KKKKhazix/agent-autoloop` 的 `README.md` 与 `INSTALL.md`（`main` 分支，2026-11-06 快照）。项目作者与博文作者为同一人，属官方一手发布，非第三方综述、非厂商营销稿。
- **内容敏感度预检**：公开网页文本（微信短链无 `code=` / `token=` / 邀请码，面向公众发布的开源公告）→ Public，标准工作流，落 `doc/bundles/`。不触发扫描版版权材料路由；正文采用原创教程 + 事实转述 + 短语级引用，不逐字转录全文。
- **工作流**：`/七概念` 场景 4「知识沉淀」R→I→E→V→C，叠加 `blog-article-to-okf-wiki` 七阶段（敏感度预检 → 骨架两问 → 归属决策树 → F 编号事实采集 + P0 核验 → 三层知识拆分 → 信源先行生成 → 对抗审查与索引收尾）。
- **骨架判定**：操作可复现性两问皆为「是」——博文给出让 Agent 读 README/INSTALL 自行安装的提示词与试跑描述，官方补齐 Node 24 版本约束、`try` → `answer 1 2` → `status` 输入输出序列与 `sim/` / `benchmark` 复现命令 → 设 `examples/`。边界：示例来自官方文档但未在本机安装运行（本机 Windows，官方 Windows 版待定），全部实战篇与根入口均标注「未在本机实测」。
- **归属**：`jishu/ai/frameworks/ai-agent/agent-autoloop/`。主线实体为 Agent 运行时 / 编排中台；该分组导语明确容纳官方文档驱动的架构学习包与 R→I→E→V 资讯转化束，同组已有 `oracle`、`openviking`、`zhihu-open-platform`、`siemens-industrial-agent` 等同类先例。未新建分组。
- **事实登记**：F-001~F-068 连续无跳号（博文 42 + 官方核验补充 26）。双份登记于本包 `references/article-source.md` 与规格侧 `.trae/specs/okf-wiki-ecosystem/agent-autoloop-blog-okf-wiki/facts.md`，V 阶段机械比对集合相等。
- **P0 核验**：10 大项 5 ✅ / 5 ⚠️ / 0 ❌，核心声明（开源、内核+插件架构、五步流程、四机制、四类插件、安装与规则配置）无失败 → bundle `status: stable`，未触发 `flagged`。5 项 ⚠️ 均为口径差异、未测边界或博文未提的补充。勘误四张清单（日期/版本表、成效数字溯源表、口径对照表、引文逐字核对表）见 `references/verification.md`。
- **已登记的关键口径差**：约 1600 行 → 约 1650 行（含空行注释）；派活「1.5ms 以内」→ p99 1.82 ms；「断电也不丢」→ 强杀已确认不丢、整机断电没有单独测过；「装个 Node 就能跑」→ Node 24+ / Git / curl / macOS·Linux 且 Windows 待定；「装好就能直接用」→ 三档实测范围；`deliver-review` 仅博文单源；订阅额度与 API Key 合规博文未提；公司虚实中台成效数字为作者自述。
- **结构**：14 个文件 = 根 `index.md` + `log.md` + 3 个子目录 index + 概念层 4 + 实战层 3 + 信源层 2。导航计数 4+3+2+1=10（不含目录索引）。
- **索引收尾**：`ai-agent/index.md` 接入导航行与 toctree、`total_bundles` 61→62；`frameworks/index.md`（ai-agent 61→62、类合计 94→95）、`jishu/ai/index.md`（frameworks 94→95、域合计 286→287）、`jishu/index.md`（ai 286→287）、`bundles/index.md`（技术域 522→523、ai 分组 286→287、全库 712→713）逐级同步。`groups: 64`、`domains: 9` 不变。
- **主仓库侧规划底稿**：`.trae/specs/okf-wiki-ecosystem/agent-autoloop-blog-okf-wiki/`（`spec.md`、`facts.md`、`insights.md`、`tasks.md`、`review.md`）。

## V 阶段机械门禁（2026-11-06）

- **本束全绿**：`check-utf8.py <bundle>` 14 文件均为有效 UTF-8；`check-toctrees.py <bundle>` 引用有效、全部内容文档可达；`check-section-anchors.py <bundle>` 扫描 14 文件，锚点全部可解析。
- **全库**：`check-utf8.py` 12900 文件通过；`check-bundles-index.py` 9 域 / 64 组 / **713 束** 五面一致全绿；`check-toctrees.py` 剩 10 处，全部指向 `sheke/industry/ai-comic-drama-opc-transition`（另一并行会话正在写入、缺 `index.md`），**本束 0 问题**；`check-section-anchors.py` 全库存量 6500+ 处既有噪声与本束无关。
- **自建检查**：双份 F 编号 `facts.md` / `references/article-source.md` / 期望集合均为 68 条且连续无跳号，bundle 正文引用 0 越界；14 文件 0 断链、0 绝对路径残留、0 `file:///`；13 个 toctree 条目全部解析到真实 `.md`；10 个非保留文件全部含 `type`，`okf_version` 仅出现在 bundle 根 `index.md`。
- **工具链限制（如实登记）**：`invoke --list` 执行失败，报 `PackageNotFoundError: No package metadata was found for invocations`（`tasks/docs.py` 导入 `invocations` 时包元数据缺失）。因此**未运行** `invoke gates.toctrees` / `gates.bundles`，改为直接执行子项目 5 个官方 `scripts/check-*.py`（即 gates 底层实现，仅 stdlib）做等效验证。**不声称 invoke gates 通过**。
- **资产门禁剩余 1 项**：`check-asset-baseline.py` 原报 3 项「规模数字矛盾」（`README.md`、`doc/index.md`），已同步为 713 并清零；剩 `[行尾归一失效] 工作区归一后字节与 HEAD 残差超过容差`（残差随并行会话 WIP 写入浮动，交付前复跑为 `+190733`，不写死单一数值）。脚本自身处置建议为「请先提交或 stash 工作区变更再复跑」——当前工作区同时含本束变更与另一会话 WIP 目录，用户未要求 commit、他束 WIP 不得代提交，故保留该项并如实登记。
- **对抗审查**：四视角共 9 条意见、8 条采纳并落实修正、1 条经论证不采纳；V 门通过。明细见规格侧 `review.md`。
- **交付**：未创建 Git commit、未 push；`awesome-okf-xs` 为第一方 git submodule，需单独提交。
