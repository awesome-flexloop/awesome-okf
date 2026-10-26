# 术语对照 —— Designer-RSI

本页只做术语与口径校准，不复述机制。机制细节见 `concepts/`。

## 1. 记忆与技能

| 术语 | 英文 | 本包定义 | 易混淆点 |
|---|---|---|---|
| 参数记忆 | parametric memory | 模型权重中固化的能力与倾向 | 论文**没有**更新它；不要把本工作读成“模型自我训练” |
| 程序记忆 | procedural memory | 冻结模型之外、以自然语言技能形式保存的可复用做事流程 | 不是聊天记忆；聊天记忆回答“之前发生了什么”，程序记忆回答“这类任务通常怎么做”（F-009） |
| 技能 | skill | 一个 SKILL.md 文件：front matter 元数据 + 五节正文 | 不是固定宏；模型可调整、重排或部分采用（F-019、F-025） |
| 子库 | sub-bank | 按 app_mode 划分的 raster / vector / page_layout·any 三组 | 文件夹名必须等于技能名（F-019） |
| 技能库 | skill bank | 全部技能构成的可版本化外部记忆 | 技能统计不在 SKILL.md 内，而在外部 store（F-026、E-1） |
| 冷启动 | cold start | 无流量时从产品帮助文档播种技能库的四阶段流水线 | 产出 76 技能；它只提供 recall floor，不等于已优化（F-028–F-032） |

## 2. 演化机制

| 术语 | 英文 | 本包定义 | 易混淆点 |
|---|---|---|---|
| 加宽 | widening | 为反复出现但未被覆盖的子任务铸造新技能 | 触发条件是缺口标签累计 3 次，不是单次失败（F-043） |
| 加深 | deepening | 用技能自身的成功/失败历史修订既有技能 | 选择阈值（2 次失败）只是廉价启发式，发布由门控决定（F-046、F-047） |
| 缺口池 | coverage pool | 按 canonical label 持久化的未覆盖子任务集合 | mint 被拒后计数保留，不是清空（F-044） |
| 归因失败 | blamed failure | 轨迹总分低于 0.6 时，记到其检索到的每个技能上 | 无 blame 权重；同一失败会同时记到多个技能（F-046） |
| 定向编辑 | targeted edit | Reflector 点名章节与改动的局部修订 | 与“整体重写”相对；连续失败才升级（F-050） |
| 探索环 | exploration cycle | 重写被拒后，在有/无技能两臂上探测失败 prompt，裁决 update/delete/keep | 可选、一次性；keep 会把记录送回缺口池（F-050） |

## 3. 门控与评测

| 术语 | 英文 | 本包定义 | 易混淆点 |
|---|---|---|---|
| 回放门控 | replay gate | 在冻结上下文中双臂重放并成对判定，只放行无退化且有改进的候选 | 不是“平均分变高就上线”（F-052–F-058） |
| 现任版本 | incumbent | 重写场景中的旧版技能（V1） | mint 场景没有 incumbent，对照是 no-skill（F-053） |
| 无技能臂 | no-skill arm | 关闭技能检索的基线 Agent | 不是“空技能文件”，而是完全不走技能路径（F-016） |
| 平局带 | tie band | 记录胜率落在 0.5±δ 内视为平局，不计改进也不计退化 | δ 吸收 judge 抖动；全部打平会被拒绝（F-057、F-058） |
| 配对胜率 | pairwise win rate | GPT-5.4 盲测、双序比较下 Evolve 相对 Base 的胜出比例 | 不是绝对质量分，不能跨 benchmark 直接相加（F-074、F-088–F-090） |
| 完整度 | completeness | 从 brief 抽出 3–10 条可判定要求后的加权满足率 | 排除“用哪个工具/怎么实现”的要求，只评结果（F-062） |
| 美学分 | aesthetics | 1–10 分纯视觉质量评分，归一化到 0–1 | 明确忽略是否遵循 brief，避免与完整度纠缠（F-064） |
| 批评轴 | critique | 八个维度上的 major/minor 问题计数 | 诊断用，不进入 0.7/0.3 标量（F-065、F-066） |
| 标量分 | scalar score | 0.7×completeness + 0.3×aesthetic | 只用于选择修订对象，不用于发布决策（F-066） |
| 留存率 | retention / survival gap | 完整度达到某阈值的样本占比，及其相对基线的差值 | 与平均完整度不是同一指标（F-080–F-082） |
| 超加性 | superadditive | 两机制合用收益大于各自收益之和 | 论文报告 +3.85 完整度（F-096） |

## 4. 实验口径

| 术语 | 英文 | 本包定义 | 易混淆点 |
|---|---|---|---|
| 演化集 | evolution briefs | 1,406 条用户流量 brief + LLM 增广，用于五轮演化 | 与 200 条 held-out 严格不相交（F-069、F-070） |
| 留出集 | held-out set | 200 条人工编写 brief，五轮固定 | 用于内部 benchmark，不参与演化（F-070） |
| 成功率 | success rate | 900 秒内产出有效设计的比例 | 与质量分分开读；质量只在成功样本上算（F-078） |
| 生成质量 | generation quality | GenEval2 用 Soft-TIFA 几何平均、DPG 用算术平均、OneIG 用 VQAScore | 不同 benchmark 不可直接比大小（F-073） |
| 延迟开销 | latency overhead | Evolve 相对 Base 的平均 wall-clock 增量 | 论文报告 3.4%–6.2%，个别场景反而更快（F-087） |
