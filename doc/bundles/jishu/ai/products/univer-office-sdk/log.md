# Univer 知识包变更日志

## 2026-11-20 · 初版生成（微信博文 → OKF Bundle）

- **来源**：微信公众号「Github喵」《Github 26k star，网页里嵌一个 Excel》（2026-11-19 14:30，四川），单源第三方推介文
- **方法论**：`@scene#47 创作文档` + `@scene#50 深度研究` → 七概念链路 R→I→E→V→A，由 `blog-article-to-okf-wiki` 七阶段负责产物形态
- **落点**：`doc/bundles/jishu/ai/products/univer-office-sdk/`（嵌套优先：子项目自治规范覆盖根 `docs/` 默认路由）
- **规模**：16 文件（6 concepts + 3 examples + 2 references + 3 目录 index + 根 index + 本日志）；F 编号事实 72 条（博文 55 + 官方核验补充 17），双份登记

### R（事实采集与官方核验）

- 首取微信正文，随后把「文章断言」与「官方事实」分账：GitHub REST API 取不可伪造元数据，jsDelivr 镜像取 `dev` 分支 README 全文（51,661 字节）逐段比对，官方安装文档 / 功能对比页 / `dream-num/skills` Contents API 补齐授权、运行时与 CLI 口径
- **24 项 P0/P1 核验：17✅ / 7⚠️ / 0❌**；7 项 ⚠️ 全部为动态时点数、命令写法演进、示例完整性或观点口径，无核心声明造假 → `status: stable`，但勘误须在正文逐条落实
- 关键分账结果：Star 标题 26k vs 官方现值 **30,434（2026-11-20）**；Luckysheet `archived=true` 且 description 逐字 "Luckysheet upgraded to Univer"；官方 description 逐字含 "for people and AI agents"
- **7 项官方补充边界**（博文未覆盖）：三 SDK 分层、开源版公式引擎性能低于商业版、版本纪律、preset/plugin 双模式、React peerDependencies 与 mobile experimental、快照 ≠ 文件、agent 治理的官方形态
- 一处易误判：`univer-cli` skill 在官方仓库**确实存在**（`hidden: true`），博文命令不是虚构，只是 `-s` 写法已被 `--skill build-with-univer` 取代 → 登记为「实体真实、写法已演进」而非 ❌

### I（骨架与归属）

- **操作可复现性两问**皆"是"（官方给出逐字可照做的安装/代码/命令，且已核验到 README）→ 技术教程类骨架，设 `examples/`，但显式标注「官方流程重组、本包未实机运行」
- 归属判据：Univer 本体是前端 Office SDK，易误判入 `jishu/document/`（实为 Sphinx/MyST 文档构建）或 `jishu/web/`（实为 ASGI 后端框架）；**官方定位含 AI agents**，且 `jishu/ai/products/` 是库内 40+ 个「微信博文七阶段转化」包聚集地 → 落 `products/`，不新建分组
- 概念层按「事实 → 洞察 → 机制 → 治理 → 萃取」递进，显式承载洞察四元组（G2）与三个可迁移模式（G3），不复述文章结构

### E（bundle 生成）

- 信源先行：`references/article-source.md` → `references/verification.md` → concepts → examples → 各级 index → 根 index
- F 编号双份登记用**机械生成**（从 bundle 侧抽表行生成 spec 侧，断言 F-001~F-072 连续且集合相等），避免手抄跳号
- 全部数字、命令、版本、事件名带 F 编号；博文省略的 Steady 等待段在 examples/01 按官方原文补回
- 相对路径：束内 concepts/examples/references 互相引用用 `../`；跨束关联用 `../<兄弟束>/index.md`，逐一核对目标存在

### V（对抗审查）

四视角审查采纳并落实：

1. 🔴 魔鬼代言人 → 「Apache-2.0 商用没问题」推不出「全功能免费」：补三 SDK 分层与授权边界三问、官方对比页披露的公式引擎性能差异
2. 🟠 老板视角 → 补采用提示：立项阶段就要区分「能存」与「能导出 Excel」，避免 PoC 跑通后才发现跨档授权
3. 🔵 未来视角 → 动态数字全部带时点、`stale_after: 2026-12-31`、登记四项复核安排（Star / skills 命令 / 功能矩阵 / CLI preview）
4. 🔗 链接自检 → 修复 1 处 `examples/01` 概念回链多跳一级（`../../concepts/` → `../concepts/`）

口径分层：博主观点（对比对象、体验时长、选型判断）与官方事实分表呈现；官方演示/自述亦标为「官方口径」，不与第三方评测混同。

### A（原子化）

- 6 个概念页各聚焦单一主题，均落在 500–5000 字符区间；交叉引用去重，不在多页重复展开同一张授权表
- 3 个 examples 各自闭环（嵌入 / 报价单与快照 / agent 治理），非官方示意代码单独标注

### 机械门禁与索引对账

改动前先测基线（toctree 0 断链 / 750 束五面对账 / 13543 文件 UTF-8），以区分「本束引入」与「既有存量」。改动后复跑结果：

| 门禁 | 改前 | 改后 | 结论 |
|------|------|------|------|
| `check-toctrees.py` | 通过 | 通过（全部 index.md 引用有效、内容文档均可达） | ✅ 零新增断链 |
| `check-bundles-index.py` | 750 束五面对账通过 | **751 束**五面对账通过（9 域 / 65 组） | ✅ 计数同步 |
| `check-utf8.py` | 13543 文件 | **13559 文件**（净增 16 = 本束文件数） | ✅ 严格 UTF-8 |
| `check-asset-baseline.py` | 通过 | 通过（单一真相源 751；HEAD 基线 104,170,183 字节） | ✅ 三处规模数字无矛盾 |
| `check-section-anchors.py`（仅本束） | — | 扫描 16 文件，锚点全部可解析 | ✅ 零新增断锚 |
| `check-line-form.py --no-git`（仅本束） | — | 16 文件 / 命中 0 条 | ✅ 无行合并故障 |
| 机械自检 | — | 断链 0 / F 编号双份各 72 且连续 / 全 LF 无 BOM / frontmatter 12 份齐备 / 概念页 2762–4017 字符 | ✅ 落在 500–5000 原子化区间 |

> `check-asset-baseline.py` 的字节基线锚定 HEAD，当前工作区残差 +92,228 字节为**本束在途内容**（未提交），提交后须在干净检出复跑自证。全库 `check-section-anchors.py` 的既有存量红不属本束，按「未新增」登记，不宣称全库通过。

计数同步点：

| 面 | 改前 | 改后 | 落点 |
|----|------|------|------|
| 全库束数 | 750 | 751 | `doc/bundles/index.md` frontmatter + 计数行、`doc/index.md`、`README.md` |
| jishu 域束数 | 552 | 553 | 总索引节标题 / 分组表 / mermaid、`README.md` 域表 |
| ai 组束数 | 313 | 314 | 总索引分组表、`doc/bundles/jishu/ai/index.md` |
| products 分组 | 42 | 43 | `doc/bundles/jishu/ai/products/index.md` 计数行 / 表格 / toctree、`ai/index.md` 分类表 |

> 既有漂移登记（非本次引入）：`doc/bundles/jishu/index.md` 导航页导语「309 束」为历史过期值（改后实际 314）。本会话按最小变更不扩大范围，留待单独对账任务；其余 17 处计数均已同步。

### C（提交）

- 本会话只写文件、不提交：子模块 `awesome-okf-xs` 新增 bundle 与索引计数调整，主仓 `.trae/specs/univer-office-sdk-okf-wiki/facts.md` 为双份登记之另一份
- `check-asset-baseline.py` 的字节基线锚定 HEAD，未提交时在途字节构成残差；提交后须在干净检出复跑自证
