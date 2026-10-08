# 生成日志（log.md）

## 2026-09-16：初始转化（R→I→E→V）

**信源**：微信公众号"技术宅SuperLaos"（老商）《我用3个免费模型，把WorkBuddy的成本砍到了零》（正文《免费大模型接入全攻略（2026-09 实战版）》，2026-09-10 08:40，IP 河北，整理日期 2026-09-09）。原始 URL `https://mp.weixin.qq.com/s/Nml1WTOv-m_P5Hs8hf9CIg` 302 落地 `https://mp.weixin.qq.com/s/qnQqCivPiuRfJIVMM-zTNQ`。

**方法论链路**：七概念场景 4（知识沉淀），由 blog-article-to-okf-wiki 七阶段工作流执行。

| 阶段 | 动作 | 产出 |
|---|---|---|
| 0 预检 | 公开博文（无访问控制参数）→ 标准工作流 | 敏感度结论（spec §1） |
| R | browser_use 取 #js_content 全文 16,218 字符（微信反爬确定，未走 WebFetch）；F-001~F-061 建账；3 个独立上下文子代理并行 P0 核验（Agnes 簇/dots 簇/AMD+全局价格簇）；F-062~F-088 回填；V 阶段第二轮独立复核追加 F-089 | spec facts.md（89 条）、本包 article-source.md、verification.md |
| I | 操作可复现性两问皆"是" → 技术教程/选型骨架（含 examples/）；归属 ai 域直挂束（与 free-llm-api-roundup 主题簇互链）；三层拆分 | spec §2/§3/§6 |
| E | 信源先行：references（2 篇）→ concepts（3 篇）→ examples（3 篇）→ 各级 index 最后写；全部具体声明带 F 编号；6 项 ❌ 勘误在正文呈现正确值 | 13 个文件 |
| V | 四视角审查 + 8 项机械门禁 + ai/index 与 bundles/index 计数接入；status=flagged 裁决 | 本日志、门禁记录（见下） |

**status 裁决**：flagged——标题级主推的 AMD 免费组合核验日已变（Vision-Exp 下架、1B→2B）、dots 通道 14 天后关闭、价格表 6 项硬错；三平台免费接入总论仍成立。stale_after=2026-11-30，到期前复核：① 10-01 后 dots.ai 直连政策；② AMD 名单/积分；③ §6 价格表。

**F 编号双份一致性**：spec `facts.md` 与本包 `references/article-source.md` 均含 F-001~F-089（61 博文事实 + 28 核验补充），编号连续无跳号、正则集合比对相等。F-089 为 V 阶段第二轮独立复核追加（Agnes Messages 端 x-api-key、视频免费档 1 RPM、AMD count_tokens 端点），已同步回转双份登记的 L 节。

**门禁记录**（✅ 为官方脚本实测，2026-09-16）：

- [x] UTF-8 严格 roundtrip：`scripts/check-utf8.py` 官方脚本实测"13 个文件均为有效 UTF-8"
- [x] 双份 F 编号集合一致（F-001~F-089 连续，正则集合比对相等）
- [x] 三级 toctree 完整：`scripts/check-toctrees.py doc` 实测"全部 index.md 引用有效，所有内容文档均可达"（本束根 index 缺 toctree 接线一项已补录 ai/index.md；concepts/02 的兄弟束链接层级错误 `../`→`../../` 已修复）
- [x] 相对链接全可达：bundle 内链接逐目标 Test-Path；跨束链接 ../../free-llm-api-roundup、../../agnes-ai/agnes-ai-models 已修正
- [x] 三级计数同步：`scripts/check-bundles-index.py doc` 实测"9 域 / 59 组 / 549 束，frontmatter、计数行、节标题、分组表、toctree 五面一致"（本束为当日多个并行转化束之一，计数以门禁实测为准）
- [x] 无 file:/// 绝对路径、无家目录信息残留
- [x] frontmatter 完整（博文 + 4 个权威源）；flagged 顶部明示在 index 与 verification
- [x] 勘误落实：7 项核心勘误在 index 速览表，正文各篇采用核验值并保留博文口径对照
- [x] Mermaid 语法：timeline/flowchart/sequenceDiagram 三类图标签闭合，无危险字符

> 上述 check-utf8/check-toctrees/check-bundles-index 均为 awesome-okf-xs 子项目自带 CI 门禁脚本（无需可选依赖），首次实测全通过（9/59/549）；`invoke gates.*` 封装任务需 invocations 可选依赖，未在当前环境运行。
>
> 随后复跑时全库门禁出现**他会话在飞束**漂移（非本束引入）：ai-agent/oracle 缺 log.md（该束 V 阶段未完成）、inurl-byok-free-models 与 inurl-unified-token 两个新束落地致目录树 549→551。本束 13 文件 scoped 复查（UTF-8、内联相对链接 broken=0、本束 toctree 接线）保持通过；全库计数与 oracle 断链归对应束的所有者会话修复，本任务不代写他束文件。

**互链登记**：本包 index/02 篇链接 free-llm-api-roundup（同主题广度束）与 agnes-ai/agnes-ai-models（代际互补）；对方束的回链未在本次一并修改（避免在 flagged 过期束内扩大变更），留待其下次更新时补链。
