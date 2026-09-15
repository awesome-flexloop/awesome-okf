# 生成日志（Log）

> 本日志记录星辰300 端侧 AI 知识包的生成过程、质量门与决策依据，供后续维护者审计与复核。方法论链路：**seven-concepts-cmd 七概念元编排（场景 4 知识沉淀，R→I→E→V→C）→ blog-article-to-okf-wiki 七阶段工作流**。CMD-LOG session：`sc-20260915-wechat-okf`。

## 2026-09-15：初始版本（R→I→E→V）

### R 阶段：信源先行与事实采集

- **对象**：微信公众号"硅基之声"《端侧AI算力新解法：CPU+NPU异构如何让嵌入式设备"本地觉醒"》（2026-09-14 08:30，约 1200 字，未署名）。
- **内容敏感度预检**：公开内容（无 token/邀请码，公众号公开链接）→ 标准工作流：spec 入 `.trae/specs/okf-wiki-ecosystem/`，bundle 入 `jishu/iot/`。
- **全文提取**：微信反爬，WebFetch 受限，经 browser_use 子代理读取 `#js_content` 取得全文。
- **信源定性**：博文为安谋科技官方通稿的自媒体二手改写（EET-China 2026-09-13 署名"白话IC"完整通稿、界面新闻 2026-09-07 标注"商讯"同稿），信源距离 = 厂商自宣；多媒体同稿不构成独立多源。
- **事实登记**：F-001 ~ F-029 连续编号（博文事实 F-001~F-015 + 核验补充 F-016~F-029），双份登记于主仓库规划区 `specs/okf-wiki-ecosystem/xingchen300-edge-ai-blog-okf-wiki/facts.md`（子模块外，非本包链接目标）与 references/article-source.md。
- **P0 权威核验**：两路独立 general_purpose_task 研究——
  - 厂商侧 V1~V6：平台/器件/板卡真实；四 demo 2026-07 WAIC 已演示（非"近日"）；STAR-MC2 系 Arm 与安谋合作开发且早于 M52 全球命名 16 个月；32MHz 为 MPS3 软核默认时钟。
  - Arm 侧 H1~H4：Helium 5×/15× 主体为 Cortex-M55（重点勘误）；U55 64–512 GOPS 配置区间、不原生支持 Transformer；"ESR"高置信为 SESR 漏字；五模型出处全部核实。

### I 阶段：骨架判定

- **两问判定**：①无分步可复现操作 → 不设 tutorials/how-to；②无可执行代码/配置产物 → 不设 examples。**结论：不设 examples/**，技术综述/资讯盘点类，9 文件结构（对标 jishu/ai/trae/bytedance-ai-consolidation）。
- **三层拆分**：事件事实层（00）→ 机制原理层（01）→ 生态/边界层（02）。
- **归属**：`jishu/iot/`（新建 bundle `xingchen-300-edge-ai`），排除 ai/（非通用 AI 平台）、ml/（非模型方法论）、sheke/industry/（技术事实为主）。
- **status 裁决**：核心声明可信、失败项为支撑性营销数字且勘误完整 → **stable**（不降级 flagged）；stale_after 2026-12-31。

### E 阶段：bundle 生成（信源先行顺序）

references/article-source → references/verification → references/index → concepts ×3 → concepts/index → index.md，共 9 个文件。所有具体声明挂 F 编号；勘误处采用权威值、不照搬博文；F-015 营销语句未作事实引用。

### V 阶段：机械门禁与索引接入

- **gates 环境说明**：`invoke <bundle>.gates` 依赖 invocations 环境，本会话不可用，以下为**手动等效核验**（逐项执行脚本/正则比对），未谎报 gates 通过。

| # | 门禁项 | 方法 | 结果 |
|---|--------|------|------|
| 1 | 双份 F 编号集合一致 | 正则 `^\|\s*F-(\d{3})\s*\|` 提取 facts.md 与 article-source.md 比对 | ✅ 均为 F-001~F-029 |
| 2 | 每级 index 含 toctree | 检查根 index / concepts/index / references/index 三个 ` ```{toctree} ` 块 | ✅ |
| 3 | toctree 条目文件存在 | 逐条对应文件系统检查 | ✅ |
| 4 | 无 file 协议绝对路径 | grep（检索 `file:` 前缀 URI） | ✅ |
| 5 | 相对链接可达 | 链接逐条解析 | ✅ |
| 6 | UTF-8 strict roundtrip | 读写校验 | ✅ |
| 7 | 无用户主目录绝对路径泄露 | grep（检索系统用户目录前缀） | ✅ |
| 8 | 计数与三级索引接入 | jishu/iot/index.md 导航+板块+toctree；bundles/index.md total_bundles | ✅ 见下节 |
| 9 | frontmatter YAML 可解析 | PyYAML safe_load 全部 9 文件 | ✅（修复 concept 02 两处含半角冒号未引号的 source title 后通过） |
| 10 | F 编号引用越界检查 | 正文 F-\d{3} 引用 ⊆ F-001~F-029 | ✅ 无越界；29 个编号全部至少被引用一次 |
| 11 | Mermaid 安全编码 | 复用根 check_mermaid.py 禁止项规则集（br 标签/带圈数字/中文方括号/嵌套 direction/subgraph 平衡）扫描 3 个图块 | ✅（清除 5 处节点标签内 `br` 换行后通过） |

**工具链说明（不谎报）**：

- 仓库根 `check_mermaid.py` 是硬编码到已废止路径 `.agents/docs/.../wsl-wiki` 的一次性脚本，当前直接运行即 FileNotFoundError；本表第 11 项复用其规则集对新图块做等效检查。
- `.agents/scripts/check-links.py` 的 `EXCLUDED_DIRS` 含 `projects`（git submodule 子树按设计跳过），对本包扫描报告"0 个 Markdown"属预期；本表第 3/5 项以独立 Python 脚本对包内 9 文件逐条解析相对链接与 toctree 目标完成等效核验。待子模块侧 CI（或 awesome-okf-xs 自有门禁）复跑确认。

- **四视角对抗审查**：
  - 事实溯源视角：每条具体声明可回溯 F 编号与 references；营销数字均带来源与口径限定。✅
  - 结构规范视角：frontmatter 字段、kebab-case 文件名、MyST toctree、无 examples 骨架与判定一致。✅
  - 读者可用视角：分层学习路径清晰；厂商自宣提示块置顶；勘误对照表可读。✅
  - 时效边界视角：stale_after + 4 条复核触发条件明示；WAIC 时间线纠正"近日"表述。✅

### 索引接入与计数

- `jishu/iot/index.md`：束数 5→6，导航表新增行、toctree 新增 `xingchen-300-edge-ai/index`，新增"📰 端侧 AI 资讯（博文核验）"板块。
- `bundles/index.md`：`total_bundles` 与正文总数 +1；jishu 域束数按实际口径同步 +1（修改前逐处读校，台账已记录既有不一致现状）。

## 文件清单

| 文件 | 说明 |
|------|------|
| index.md | 包入口（okf_version 0.2，性质声明 + 导航 + 边界） |
| log.md | 本文件 |
| concepts/index.md | 概念地图与学习路径 |
| concepts/00-platform-and-demos.md | 事件事实层 |
| concepts/01-cpu-npu-heterogeneous-design.md | 机制原理层（含 2 张 Mermaid 图） |
| concepts/02-model-zoo-and-trust-boundaries.md | 生态/边界层 |
| references/index.md | 信源清单与 F 编号段索引 |
| references/article-source.md | 博文事实双份登记 F-001~F-029 |
| references/verification.md | 12 项核验结论 + 勘误四张清单 + 权威 URL |

## 已知遗留

1. "ESR→SESR"漏字发生环节未证实（一手 slides 未公开），正文以"高置信"措辞表述。
2. 无第三方实测数据；20-30× 外推、440/425 亿等数字仅作厂商口径存档。
3. gates 未以 invoke 运行（环境不可用）；主仓库 check-links/check_mermaid 分别因 `projects` 排除规则与硬编码废止路径无法覆盖本包，均以等效脚本替代，待子模块 CI 环境复跑。
4. 计数口径既有不一致（jishu/index.md 组束数之和与其一级束总数、bundles/index.md 405 口径不同——一级束 vs 细目束两套口径），本次仅在各口径上分别 +1（110→111、384→385、405→406、537→538、IoT 5→6），未顺带做全量重对账。
5. 主仓库 `.trae/specs/` 下 spec.md + facts.md 为规划/过程产物，看板由 docgen 自动刷新，未手改 THEME_DASHBOARD 区。
