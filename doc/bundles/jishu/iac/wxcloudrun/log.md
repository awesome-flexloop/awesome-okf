# 微信云托管 Bundle 变更日志

## 2026-10-22 — 初始版本（R→I→E→V→C）

- **信源**：微信开放文档「云服务 → 云托管」官方文档站，2026-10-22 全量采集 **145 页**（根 1 / basic 4 / quickstart 10 / guide 40 / development 51 / Billing 6 / scene 26 / practice 5 / info 2）。抓取方式为脚本抽取 `<div id="docContent">` 至 `</main>` 的正文片段并做重复片段检测与页脚裁剪，落盘为纯文本后人工分主题深读。
- **R 阶段**：登记 **F-001~F-190** 共 190 条连续编号事实，逐条附来源 URL；另登记 **E-001~E-009** 共 9 条官方文档内部口径不一致的勘误。
- **I 阶段**：形成跨案例四元组洞察 **26 条**（陈述 / 证据 F 编号 / 反常识 / 行动），分布并固化到 7 篇概念文档中（3 + 4 + 4 + 4 + 4 + 4 + 3），每条均经脚本校验四要素齐备。
- **E 阶段**：按「信源先行」顺序生成 `references/`（事实登记表 → 覆盖度矩阵）→ `concepts/`（7 篇）→ `examples/`（4 篇）→ 各级 `index.md`；另萃取 3 条可迁移模式（封板发布单灰度、能力边界清单化交付、静默销毁风险治理）写入 `concepts/06-transferable-patterns.md`。
- **V 阶段**：双份 F 编号集合比对一致（190 = 190），bundle 全部 Markdown 中的 F 编号越界 0 个；9 条勘误均在正文按采信结论落实并标注口径差异；四级 toctree 完整、相对链接全可达、UTF-8 严格解码通过、敏感信息零残留；总索引五面计数同步至 661 束 / 63 组 / 9 域。逐项证据见 [verification.md](verification.md)。
- **V 阶段复审（fresh-context 对抗审查后修正）**：独立审查子代理检出 5 处 P0 事实性错误与若干 P1/P2 项，全部已修正并回写：
  - P0-1 `concepts/00-platform-model.md` 的 mermaid 把「整合底层资源」升级为「开通即创建」并杜撰 `serverless` → 改为「可整合」并删除 `serverless`；
  - P0-2 `concepts/05-security-and-migration.md` 把「计费按天结算」升级为「攻击当天完全不可见」 → 改为「费用与欠费信号次日显现，行为异常靠告警当天发现」（F-162）；
  - P0-3 `concepts/01-release-and-rollback.md` 的内网域名以现在时陈述，与 E-007 的「下线中」冲突 → 补时点限定并指向 E-007；
  - P0-4 `concepts/03` 与 `concepts/04` 号称「01/02/05/06 将在后续补齐」（实已存在） → 改为真实交叉引用；
  - P0-5 `verification.md` 声称「全仓零 `file:///`」（实有既有存量） → 收窄为「本包内」；
  - P1 `verification.md` 声称 frontmatter「九字段齐备」与「见 log.md 记录」两处过度宣称/悬空引用 → 改为实际门禁输出 + 明确标注「完整文档构建 未执行」+ 补「复核方式」行；
  - P1 「不支持项」计数口径矛盾：F-163 原文为 7 项，而 `concepts/05` 与 `examples/04` 的表只有 6 行（协议项合并了两句），正文却称 7 条 → 三处统一为 7 条，表行拆为「调用协议 / 传输协议」两行使行数与 F-163 条目数一一对应，`concepts/06` 的 7 条枚举也改为 F-163 逐字原文；
  - P1 `references/coverage-matrix.md` 写「6 篇概念文档」（实为 7 篇）、B-05 断言「正文不含时区处理指引」（与 `examples/01` 冲突）、第三节「未进入正文」口径未区分概念文档与示例文档 → 全部修正，并补口径澄清脚注（15 条未落入概念正文，其中 6 条已在 examples/ 落地，9 条全包未出现）；
  - P1 `concepts/05` 的 E-001 只提「以 50 为上限估算」，漏了更紧的 F-020（单环境总实例数上限 28，不可特殊申请） → 已补；
  - P1 E-009 采信空转：两处勘误说明未实际引用源文档数值 → 已补出 702 与 `720 − 12 = 708`，并明确采信源文档正文原值 702、标注「源文档算术存疑」；
  - P1 `concepts/04` 的刊例价全表缺「事实」列 → 已补 F-133~F-137 逐行对应；
  - P2 `concepts/02` 的 javascript 代码块缺来源标注 → 补为「官方文档调用示例原文（逐字引用 F-073）」；「结单」「webshell」两处补一句释义。
- **V 阶段二次复审（渲染层与依据归属）**：再次派发 fresh-context 独立审查子代理，检出 P0 = 0、P1 = 3、P2 = 4；并以自写脚本机械复现全部 P1 缺陷后全部修正：
  - P1-1 `concepts/01-release-and-rollback.md`「流水线与 CLI 部署」表表头仅 2 列（`维度 | 事实`）而数据行为 3 列 —— MyST/markdown-it 严格按表头列数渲染，**「事实」列整列被静默丢弃**；同行 `--releaseType=FULL|GRAY` 的管道符未转义同样切分单元格 → 表头补为 `维度 | 事实 | 依据`，管道符转义为 `\|`；
  - P1-2 `references/doc-source.md`（同源 spec 侧 `facts.md`）F-068 行 `--releaseType=FULL|GRAY` 未转义 → **来源 URL 整列消失**，损害可溯源性 → 两侧同步转义，并重跑派生脚本 `gen_doc_source.py` 重新生成 `doc-source.md`（校验输出 `F rows: 190 / E rows: 9 / min/max: 1 190 / continuous: True`）；
  - P1-3 `verification.md` 的 `concepts|examples|references/index.md` 未转义 → 证据列被切成 5 单元格、后半句丢失 → 转义为 `concepts\|examples\|references/index.md`；
  - P2-1 `concepts/02-call-and-identity.md` frontmatter 把 9 个 header 统称「9 个 X-WX 身份 header」→ 改为「9 个微信身份相关 header」；
  - P2-2 `examples/02-call-and-identity.md` 身份字段行同误 → 改为「8 个 `X-WX-*` + `X-Original-Forwarded-For`，共 9 个」（F-077 实为 8+1 构成）；
  - P2-3 `examples/02-call-and-identity.md` 前置条件「服务已上线」行挂 F-053（发布单三子流程）属无支撑引用 → 改挂 F-060（版本分线上/线下两种状态）并改写表述为「版本状态」；
  - P2-4 `examples/04-migration-and-cost.md` 的 F-015（按声明规格计费）与 F-017（按实际使用量计费）并列易被误读为「按使用率计费」→ 补「口径澄清（计费依据 vs 计量粒度）」说明块，明确 F-015 决定单价基准、F-017 决定用量计量粒度，合起来是「按声明规格的单价 × 按实际运行时长的用量」；
  - 修复后复跑门禁：表格列数扫描 **不一致 0 处**、`check-toctrees.py` / `check-bundles-index.py` / `check-utf8.py` 三门 exit 0、双份 F 编号集合仍 190 = 190、包内 F 引用越界 0、相对链接断链 0。
- **计数说明**：新增本束后，全库束数由 660 增至 661，`jishu` 域由 490 束增至 491 束，`iac` 组由 1 束增至 2 束；`doc/bundles/index.md` 的 frontmatter、计数行、域节标题、分组表束数列与末尾 toctree 五面一致。
- **C 阶段**：R→I→E→V→C 闭环完成；未在真实云托管环境部署验证；未执行 push。
