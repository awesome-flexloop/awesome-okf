# 变更日志（Log）

## 2026-10-10 · 初始生成（博文转化 R→I→E→V）

- **触发**：微信公众号「枫音AI」推文《Github已获10K星标，开源AI小说神器来了！》（2026-10-08 08:03）经 seven-concepts-cmd 方法论编排（场景4：知识沉淀 R→I→E→V）+ wechat-public-okf 转化规范生成 OKF bundle。
- **方法论编排日志（CMD-LOG）**：`cmd=seven-concepts` | session `sc-20261010-inkos-okf` | S0 CMD_START → S1 SCENARIO_DETECTED（knowledge 沉淀）→ S2 CHAIN_SELECTED（R→I→E→V→C）
- **信源获取**：微信公众号 WebFetch 成功（#js_content 全文）；GitHub 仓库 README + GitHub API（`stargazers_count=5595`、license=AGPL-3.0、主语言 TypeScript、建仓 2026-03-12、forks=1043、open_issues=123）。
- **公开性预检**：文章为公开可访问（无登录/验证码墙）；账号归属「枫音AI」；通过公开入口可访问 → Public 级别，落根 `doc/bundles/`。
- **事实登记**：F-001~F-048 连续 48 条（博文事实 F-001~F-028，含 author_claim 标注；核验补充 F-029~F-048 来自 GitHub 官方一手来源）；单侧登记（references/article-source.md，未建独立 spec facts.md）。
- **P0 核验**（核验日 2026-10-10）：4 条 P0 声明（F-001 星标、F-002 厂商站台、F-009/F-013/F-020 Agent 数量、F-022 审计维度）→ **0✅ / 4⚠️ / 0❌**，全部为口径偏差，无事实不成立。
  - ⚠️ **E-1 Agent 五 vs 十**：博文"五个"vs 官方 README 实际 **10 个角色**（雷达/规划师/编排师/建筑师/写手/观察者/反射器/归一化器/审计员/修订者，F-033）；博文漏掉了规划师/编排师/观察者/反射器——恰是"写得长记得住"的关键
  - ⚠️ **E-2 审计 37 vs 33 维**：博文称"37 个维度"（F-022），官方 README 为连续性审计员 **33 维**（F-037），37 无出处
  - ⚠️ **E-3 星标 10K vs 5.6K**：标题称"10K 星标"，核验日 GitHub API 实测 **5,595**（≈5.6K，F-046），"10K"为发布时点自宣/夸大口径
  - ⚠️ **E-4 厂商站台无出处**：博文称 Kimi/火山等多厂商站台（F-002），GitHub README 无任何厂商官方站台声明（F-047）
  - **补充**：博文只写"开源"，实际为 **AGPL-3.0**（F-032），正文补充 AGPL 传染性说明
- **骨架判定**：操作可复现性两问 → Q1 是、Q2 是但含限定（官方 README 提供完整命令与流程，但本包未真机执行）→ 设 `examples/`（1 篇），并施加限定：命令须经官方 README 逐字核验、examples 顶部显式标注"非博文实测、本包制作中未真机执行"。
- **归属判定**：`jishu/ai/products/inkos/`（AI 产品与终端工具组），与 orca-ade/loopx/wigolo/opencreator 等同为微信博文转化束；groups：ai→products→inkos。
- **文件**：10 个（root index/log + concepts 4 + examples 2 + references 3）。
- **状态**：draft；stale_after=2026-12-10（星标等指标强时效，缩短复核窗口）。

## 2026-10-10 · V 阶段（对抗审查 + 机械门禁）

> 门禁直接运行仓库 stdlib 脚本（`projects/awesome-okf-xs/scripts/`），未经 `invoke gates.*` 通道，故不声称"`invoke gates` 通过"。

- ✅ `scripts/check-toctrees.py`（本束路径）：通过——`index.md`（根/concepts/examples/references）引用全部有效，内容文档均可达；根 `index.md` 已追加到 `jishu/ai/products/index.md` 的 toctree。
- ✅ `scripts/check-utf8.py`：通过——11202 个文件均为有效 UTF-8（本束无 BOM、strict roundtrip 无乱码）。
- ✅ **相对链接全可达**：4 个正文档全部 `./`/`../` 链接逐一 Test-Path 通过；**V 中修复 1 条断链**——`concepts/02` 原写作 `../inkos/concepts/01-memory-and-agent-pipeline.md`（多一层，会解析到束外），已改为同目录 `01-memory-and-agent-pipeline.md`。
- ✅ **frontmatter 十项齐备**：8 个带 frontmatter 的文档（根 index + 3 concepts + 1 example + article-source + verification）全部含 `okf_version/type/title/description/tags/generated/verified/status/stale_after/sources`；3 个 `*/index.md`（concepts/examples/references）与 `log.md` 按本库约定不设 frontmatter。
- ✅ **F 集合连续**：`article-source.md` 正则提取 F-001~F-048 连续 48 条，无跳号无缺号。
- ✅ **勘误落实核对**：E-1（Agent 五vs十）、E-2（审计 37vs33）、E-3（星标 10Kvs5.6K）、E-4（厂商站台无出处）在根 index.md 先读提示、concepts 三篇与 references 中逐处按"博文口径/官方口径"双标注；AGPL-3.0 补充在 [00 概览](concepts/00-inkos-overview.md) 与根 index 显式呈现。
- ✅ **P0 统计一致**：根 index.md / verification.md / log.md 三处均为"4 项 P0 → 0✅/4⚠️/0❌"。
- ⚠️ **父索引总计数存在并发漂移（归他会话 WIP，未代为归一）**：`scripts/check-bundles-index.py` 当次报出 +3 总束数 / jishu 节标题与分组表和 +4/+7 漂移。经查源自**其他并发会话的在建束**（未跟踪目录：ecosystems/deepseek-harness、models/agent-lightning、practice 4 束、products/image-blaster·knocket·vidbee、comm/wifit3、gui/tauri、ml/pytorch-view-reshape、sheke/industry 2 束），按"谁添加谁对账"未代为归一。本束 inkos 相关计数已正确落位：`products/index.md` 24→26、`jishu/ai/index.md` 六大类 224→227 与 products 行 24→26、`doc/bundles/index.md` ai 行→227 / products 26 / total→607（frontmatter）·608（计数行）。

## 2026-10-10 · C 阶段（预留）

- **未执行提交**：用户未要求提交；且 `doc/bundles/index.md` 的计数正被其他并发会话在写，此刻提交共享索引有冲突风险，故原子提交留待并发会话收敛后（本次仅登记 inkos 相关变更与归属）。