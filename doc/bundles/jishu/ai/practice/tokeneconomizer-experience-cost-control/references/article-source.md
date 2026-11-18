---
type: Reference
title: "TokenEconomizer 事实清单（F-001 ~ F-110）"
description: "微软研究院博客、arXiv:2610.22732v1、项目页与 GitHub README 四信源的客观事实编号登记"
tags: [TokenEconomizer, 事实清单, 信源, 成本控制, 编码Agent]
status: stable
generated: { by: "reference_agent/seven-concepts-r", at: "2026-11-17T12:20:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:20:00+08:00" }
sources:
  - id: blog
    resource: https://www.microsoft.com/en-us/research/blog/tokeneconomizer-learning-from-experience-to-make-ai-coding-agents-more-efficient/
    title: "TokenEconomizer: Learning from Experience to Make AI Coding Agents More Efficient（Microsoft Research Blog，2026-11-16）"
  - id: paper
    resource: https://arxiv.org/abs/2610.22732
    title: "TokenEconomizer: Experience-Driven Black-Box Cost Control for Coding Agents（arXiv:2610.22732v1）"
  - id: paper-html
    resource: https://arxiv.org/html/2610.22732v1
    title: "arXiv HTML 全文 v1"
  - id: project
    resource: https://tokeneconomizer.github.io
    title: "TokenEconomizer 项目页（交互图表、逐仓库数据、九个标注运行）"
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
    title: "microsoft/TokenEconomizer 开源仓库 README"
  - id: pub
    resource: https://www.microsoft.com/en-us/research/publication/tokeneconomizer-experience-driven-black-box-cost-control-for-coding-agents/
    title: "Microsoft Research 论文出版页"
---

# TokenEconomizer 事实清单

> 本表是**事实层**（七概念 R 阶段产物）：每条为信源明示内容，不含因果判断、不含推断、不含评价。共 **110 条**，编号 **F-001 ~ F-110** 连续。
> 口径类型：`博客` / `论文` / `项目页` / `仓库` / `出版页` / `交叉差异`（指多处信源表述不同，仅登记差异本身，不裁决）。
> **单份登记说明**：本束采用 `references/article-source.md` 单份事实台账，未建 `.trae/specs/` 双份副本——用户显式指定产出物落点为 `doc/bundles/`，写操作边界不越界。编号集合由 `log.md` 记录的机械校验自证连续。
> 采集时间：2026-11-17。信源距离：博客与出版页为作者团队发布，论文与仓库为一手材料，四者同源团队，无独立第三方复现材料。

---

## 一、信源与元信息（F-001 ~ F-014）

| 编号 | 客观事实 | 信源定位 | 口径类型 |
|---|---|---|---|
| F-001 | 微软研究院博客标题为 "TokenEconomizer: Learning from Experience to Make AI Coding Agents More Efficient"，标注 Published November 16, 2026 | 博客页首 | 博客 |
| F-002 | 论文英文标题为 "TokenEconomizer: Experience-Driven Black-Box Cost Control for Coding Agents" | arXiv abs / HTML 首页 | 论文 |
| F-003 | 论文编号 arXiv:2610.22732v1，分类 cs.CL，v1 提交于 2026-10-15 23:06:57 UTC | arXiv abs 提交历史 | 论文 |
| F-004 | 论文 HTML 页标注 License: CC BY 4.0 | arXiv HTML 页脚 | 论文 |
| F-005 | 论文列出 11 位作者：Aaron J. Li、Weijia Xu、Chandan Singh、Zixiao Chen、Jeevana Priya Inala、Charlotte Siska、Acar Tamersoy、Bin Yu、Ion Stoica、Michel Galley、Jianfeng Gao | arXiv HTML 首页 / BibTeX | 论文 |
| F-006 | 论文署名机构为 UC Berkeley、Microsoft Research、Microsoft Security 三家 | arXiv HTML 首页 / 仓库 README | 论文 |
| F-007 | 项目页地址为 tokeneconomizer.github.io，含交互图表、逐仓库数字与九个标注运行 | 项目页 / 仓库 README | 项目页 |
| F-008 | 开源仓库地址为 github.com/microsoft/TokenEconomizer | 博客 / 项目页 | 仓库 |
| F-009 | 仓库 README 尾部链接文本为「MIT LICENSE」（指向 LICENSE 文件），README 顶部徽章文本为 `license-Apache 2.0` | 仓库 README 首尾 | 交叉差异 |
| F-010 | 博客署名列 9 人：Aaron J. Li、Weijia Xu、Chandan Singh、Zixiao Chen、Jeevana Priya Inala、Bin Yu、Ion Stoica、Michel Galley、Jianfeng Gao | 博客作者行 | 博客 |
| F-011 | 微软出版页署名含 "Chinmay Singh"（链接 `/people/chsingh/`），论文、项目页、仓库 README 均写 "Chandan Singh" | 出版页 vs 其余三源 | 交叉差异 |
| F-012 | 出版页标注日期为 2026 年 10 月；博客标注 2026-11-16 | 出版页 / 博客 | 出版页 |
| F-013 | 论文 DOI 为 10.48550/arXiv.2610.22732 | arXiv abs | 论文 |
| F-014 | 本次采集覆盖四个信源：博客、arXiv HTML 全文、项目页、仓库 README；采集日 2026-11-17 | 本束采集记录 | 独立核验 |

## 二、问题设定与成本剖析（F-015 ~ F-030）

| 编号 | 客观事实 | 信源定位 | 口径类型 |
|---|---|---|---|
| F-015 | 每一轮请求重复计费的内容为：agent 指令、全部已加载工具描述、截至当前的会话历史 | 论文 §1 / 博客 / 项目页 | 论文 |
| F-016 | 成本剖析在 60 个 SWE-Bench 任务上运行未修改的 Claude Code，各仓库任务按顺序执行 | 论文 §2 / 博客 | 论文 |
| F-017 | 60 个剖析任务分布于 6 个仓库、每仓 10 个 | 论文 §2 / 表 6 / 项目页 | 论文 |
| F-018 | 某仓库累计至少 5 个已完成任务后，30% 的工具调用重复该仓库更早任务中的动作 | 论文 §2.2 / 博客 / 项目页 | 论文 |
| F-019 | 与另一仓库的完整历史比对，仅 7% 的调用匹配 | 论文 §2.2 / 博客 | 论文 |
| F-020 | 重复率从第 2、3 个任务的 14% 上升到至少 5 个前置任务后的 30% | 论文 §2.2 图 3(a) | 论文 |
| F-021 | 在至少半数任务中复现的动作，占该仓库工具调用收发字节的 12–28% | 论文 §2.2 | 论文 |
| F-022 | agent 每一轮被展示 23 个 tool schemas | 论文 §2.2 / 博客 / 项目页 | 论文 |
| F-023 | 其中 16 个工具从未被调用 | 论文 §2.2 / 博客 | 论文 |
| F-024 | 没有任何仓库调用的工具数超过 7 个 | 论文 §2.2 图 3(b) | 论文 |
| F-025 | 3 个工具占全部调用的 98% | 论文 §2.2 | 论文 |
| F-026 | 10 次失败执行占任务数的 17%，占总花费的 32% | 论文 §2.2 / 博客 / 项目页 | 论文 |
| F-027 | Matplotlib 失败轨迹 45 轮、成功轨迹 20 轮；Sphinx 失败 36 轮、成功 31 轮 | 论文 §2.2 | 论文 |
| F-028 | 45 条轨迹重复更早的失败签名；60 个任务 51% 的花费发生在轨迹首次重复之后 | 论文 §2.2 | 论文 |
| F-029 | 50 条成功轨迹中 36 条同样重复失败签名；重复后花费中超过一半来自最终成功的运行 | 论文 §2.2 | 论文 |
| F-030 | 三种固定策略为 RTK（压缩 shell 输出）、Serena（增加语义代码导航 MCP 工具）、RepoMap（Aider 仓库符号地图，上限 2,048 token） | 论文 §2.1 / 项目页 | 论文 |

## 三、固定策略的仓库依赖性（F-031 ~ F-040）

| 编号 | 客观事实 | 信源定位 | 口径类型 |
|---|---|---|---|
| F-031 | 三种固定策略在 Django 上均降本，在 SymPy 上均升本 | 论文 §2.1 / 项目页 | 论文 |
| F-032 | scikit-learn 上仅 RTK 降本；Sphinx 上仅 RepoMap 降本 | 论文 §2.1 / 项目页 | 论文 |
| F-033 | sklearn 逐策略成本变化：RTK −6.9%、Serena +28.6%、RepoMap +30.5%；默认 Pass@1 10/10 | 论文表 6 | 论文 |
| F-034 | SymPy 逐策略：RTK +7.3%、Serena +30.8%、RepoMap +9.8%；RepoMap 下 Pass@1 8/10 | 论文表 6 | 论文 |
| F-035 | Django 逐策略：RTK −19.9%、Serena −15.4%、RepoMap −16.2%；默认 Pass@1 9/10 | 论文表 6 | 论文 |
| F-036 | Sphinx 逐策略：RTK +0.6%、Serena +2.1%、RepoMap −7.5%；默认 Pass@1 6/10 | 论文表 6 | 论文 |
| F-037 | Matplotlib 逐策略：RTK −4.9%、Serena −4.8%、RepoMap +5.0%；默认 Pass@1 8/10 | 论文表 6 | 论文 |
| F-038 | xarray 逐策略：RTK −16.8%、Serena +4.7%、RepoMap −20.2%；默认 Pass@1 7/10 | 论文表 6 | 论文 |
| F-039 | §4.1 主比较排除 Serena，理由为工具剪枝可能移除其未使用 server 而混淆比较，且它是唯一在剖析中提高合并成本的固定策略 | 论文 §4.1 | 论文 |
| F-040 | 论文定义三个术语：meta-strategy（三条环境无关的过程）、policy（其学到的环境专属决策）、fixed strategy（在所有环境套用同一配置） | 论文 §3 开头 | 论文 |

## 四、黑盒外部控制器与形式化（F-041 ~ F-050）

| 编号 | 客观事实 | 信源定位 | 口径类型 |
|---|---|---|---|
| F-041 | 控制器不修改模型权重、不修改 agent-loop 代码 | 论文 §3 / 博客 / 仓库 README | 论文 |
| F-042 | 控制器只通过三个接口作用：instruction prefix（指令前缀）、loaded tools（已加载工具）、live event stream（实时事件流） | 论文 §3 / 项目页 | 论文 |
| F-043 | 优化单元是同一环境内按时间排序的 task stream τ₁…τₙ | 论文 §3 / 附录 E | 论文 |
| F-044 | 公式 (1)：`(ΔP_i, 𝒰_i, B_i) = 𝒞(τ_i, S_{i-1})` | 论文式 (1) / 项目页 | 论文 |
| F-045 | 每完成一条轨迹 ξᵢ，控制器更新三条元策略得到状态 S_{i+1} 供下一任务使用 | 论文 §3 / 项目页 | 论文 |
| F-046 | ΔPᵢ 为本任务激活的 micro-skills，𝒰ᵢ 为加载的工具集合，Bᵢ 为校准失败循环守卫的轮次预算 | 项目页 Method / 论文 §3 | 项目页 |
| F-047 | 控制器可以始终保留默认配置不动作 | 项目页 Method | 项目页 |
| F-048 | 控制器自身的模型调用计入触发该调用的任务 | 论文 §3 / 附录 E / 仓库 README | 论文 |
| F-049 | 成本口径为 mean cache-aware cost（式 4、式 5）：按未缓存输入 / 缓存输入 / 输出分别加权，再叠加辅助调用成本 Hᵢ | 论文附录 E 式 (4)(5) | 论文 |
| F-050 | 优化目标式 (6)：最小化期望平均成本，约束为期望质量不低于默认配置减 ε | 论文附录 E 式 (6) | 论文 |

## 五、三条元策略（F-051 ~ F-072）

| 编号 | 客观事实 | 信源定位 | 口径类型 |
|---|---|---|---|
| F-051 | micro-skills 每 5 个任务由 LLM proposer 从近期轨迹摘要生成一行仓库事实，每条附可执行 detectors | 项目页 Method / 论文表 4 | 项目页 |
| F-052 | 每个任务结束后由 detectors 检查确认 / 矛盾 / 是否需要该事实，此步骤不调用模型 | 项目页 Method / 论文 §3.1 | 项目页 |
| F-053 | 事实在 3 个「编辑文件互不重叠」的任务确认后才激活 | 论文表 4 / 项目页 | 论文 |
| F-054 | need gate 要求：在 ≥4 次触发的任务上，need rate ≥0.4 | 论文表 4 / 表 11 | 论文 |
| F-055 | 支持度式 (2)：`q_i(f) = Σ_{j<i} γ^{i−j} (1[ξⱼ confirms f] − λ·1[ξⱼ contradicts f])` | 论文式 (2) | 论文 |
| F-056 | 控制器配置 γ = 0.8、λ = 5 | 论文表 4 / 项目页 | 论文 |
| F-057 | qᵢ(f) < 0 或高风险技能出现任一矛盾，即永久退休 | 论文表 11 / 项目页 | 论文 |
| F-058 | 事实状态机三态：Candidate（从不注入）、Confirmed（按需注入）、Retired（永不复活，可用新 id 重提） | 论文表 11 | 论文 |
| F-059 | 附录 H 记录约五分之一被提议的技能在流内被退休 | 论文附录 H | 论文 |
| F-060 | 工具剪枝始终保留 shell 执行与文件读 / 写 / 编辑类核心工具 | 论文 §3.2 / 博客 / 项目页 | 论文 |
| F-061 | 工具连续 3 个任务未被调用，并经逐任务 LLM judge 判定不相关后被屏蔽 | 论文表 4 / 项目页 | 论文 |
| F-062 | judge 评审候选工具时，屏蔽任务描述中指向 PR、issue、commit、文件的链接 | 项目页 Method | 项目页 |
| F-063 | 每 5 个任务恢复完整工具目录复审；复审期间被调用的工具此后不再屏蔽 | 论文表 4 / 项目页 | 论文 |
| F-064 | 剪枝单位为 tool；Codex 上为 capability package | 论文表 4 | 论文 |
| F-065 | 附录 H 组合变体流末仍屏蔽 14.8（Sonnet 5）/ 14.5（Opus 4.8）个 schema，复审任务数 3.1 / 4.3 | 论文表 6 | 论文 |
| F-066 | 轮次预算 `B_i = β · Q_p({|ξ_j| : j<i, y_j=1})`，p = 90 分位、β = 1.25 | 论文式 (3) / 表 4 / 项目页 | 论文 |
| F-067 | 每次工具调用后由规则检查重复失败、密集错误或超出 Bᵢ，该层不调用模型 | 项目页 Method / 论文 §3.3 | 项目页 |
| F-068 | judge 以置信度 ≥ c = 0.7 判定卡住时，写入一条附「已尝试什么」摘要的 redirect | 论文表 4 / 项目页 | 论文 |
| F-069 | 控制器配置为「Redirects 1, then stop」，κ = 2.5 且严格停滞规则成立时强制停止 | 论文表 4 / 项目页 | 论文 |
| F-070 | Web-Bench 每个流仅 20 或 21 个任务，失败循环守卫改用预注册 30 轮预算，直到 5 个任务通过 | 论文附录 C | 论文 |
| F-071 | 安全基准每个任务都是新仓库，micro-skill 注入被关闭，仅保留两条元策略 | 论文 §4.3 / 附录 C / 项目页 | 论文 |
| F-072 | 附录 H 记录 judge 每流 9.9–13.1 次、redirects 3.9–5.3 次、aborts 1.4–2.2 次 | 论文表 6 | 论文 |

## 六、实验设置与结果（F-073 ~ F-091）

| 编号 | 客观事实 | 信源定位 | 口径类型 |
|---|---|---|---|
| F-073 | 277 个 SWE-Bench 任务分布于 6 仓库：scikit-learn 60、SymPy 60、Django 40、Sphinx 44、Matplotlib 34、xarray 39 | 论文 §4.1 | 论文 |
| F-074 | 277 个任务中 199 个来自 SWE-Bench Verified，78 个来自 full test split | 论文附录 D | 论文 |
| F-075 | 仓库内任务按时间顺序运行，控制器只从该仓库更早的工作学习 | 论文 §4.1 / 仓库 README | 论文 |
| F-076 | 五个 agent–model 组合：Claude Code + Sonnet 5、Claude Code + Opus 4.8、Copilot CLI + Sonnet 5、Codex + GPT-5.6 Terra、Codex + GPT-5.6 Sol | 论文 §4.1 | 论文 |
| F-077 | 每个设置跑完整六仓库任务集、3 个 seed；质量指标为 SWE-Bench Pass@1、Web-Bench cumulative Pass@2、安全基准 detection F1 | 论文表 1 说明 / §4.1 | 论文 |
| F-078 | 比较对象：默认 high effort、medium effort、low effort、RTK、RepoMap、TokenEconomizer、TE+RTK、TE+RepoMap | 论文 §4.1 / 表 1 | 论文 |
| F-079 | 表 1 中 TE 的 ΔCost（%）为 −23.6±1.8 / −30.9±2.1 / −24.7±1.2 / −26.1±2.1 / −18.4±1.5 | 论文表 1 | 论文 |
| F-080 | 表 1 默认配置 Pass@1 为 74.7±1.3 / 74.0±0.6 / 73.8±1.0 / 80.1±0.8 / 75.0±1.5 | 论文表 1 | 论文 |
| F-081 | 表 1 中 TE 的 Pass@1 为 76.0±1.2 / 73.0±0.6 / 74.7±1.0 / 81.7±0.7 / 77.6±1.3 | 论文表 1 | 论文 |
| F-082 | 降低推理强度使 Pass@1 下降 1.8–10.3 个百分点；TE 在 Opus 4.8 上下降 1.0 个百分点 | 论文 §4.2 / 博客 | 论文 |
| F-083 | TE+RTK 在 Claude Code + Opus 4.8 上达到 −33.2±1.7%、Pass@1 74.8±1.2 | 论文表 1 / §4.2 | 论文 |
| F-084 | 30 个 repository–setting cell 全部降本，幅度 5.2–40.1% | 论文 §4.2 / 图 5(a) | 论文 |
| F-085 | RTK 单独在 12 个 cell 上增加成本，RepoMap 单独在 15 个 cell 上增加成本 | 论文 §4.2 | 论文 |
| F-086 | 除 xarray 外各仓库初期成本更高；第 6 个任务起全部低于默认，最终累积节省 16.9–32.0% | 论文 §4.2 / 博客 / 项目页 | 论文 |
| F-087 | 表 2(a) 消融（ΔCost %，Sonnet 5）：micro-skills −11.8、tool pruning −13.2、loop guard −7.1、combined −23.6 | 论文表 2(a) | 论文 |
| F-088 | 表 2(a) 消融（ΔCost %，Opus 4.8）：−14.3、−17.7、−5.4、combined −30.9 | 论文表 2(a) | 论文 |
| F-089 | 各单策略变体 Pass@1 与默认相差 ≤3 个百分点；没有单一变体达到全栈节省幅度 | 论文 §4.2 | 论文 |
| F-090 | Web-Bench 102 任务 / 5 项目，ΔCost 为 Claude Code −21.2±1.3、Codex −16.0±1.5、Copilot CLI −18.7±1.9 | 论文表 2(b) | 论文 |
| F-091 | CredData 100 任务：−19.6 / −16.5 / −18.3；ReposVul 100 任务：−7.5 / −6.4 / −9.3；论文摘要写「6.4–21.2%」，博客写安全审计「6.4–19.6%」，仓库 README 写「6–20%」 | 论文表 2(b) / 摘要 / 博客 / 仓库 | 交叉差异 |

## 七、开源插件（F-092 ~ F-105）

| 编号 | 客观事实 | 信源定位 | 口径类型 |
|---|---|---|---|
| F-092 | 插件稳定支持 Claude Code、Codex、GitHub Copilot CLI、Pi 四种 agent | 仓库 README | 仓库 |
| F-093 | 实验性支持 opencode、Cursor Agent、Grok Build、Hermes Agent、Antigravity CLI、Factory Droid 六种 | 仓库 README | 仓库 |
| F-094 | 运行环境要求 Python 3.10+ 在 PATH 上；插件不需要自己的 API key，不处理凭据 | 仓库 README / 博客 | 仓库 |
| F-095 | 学到的内容保存在开发者本机 `~/.tokeneconomizer` | 仓库 README / 博客 | 仓库 |
| F-096 | 默认开关：toolprune = on、loopguard = on、microskills = off | 仓库 README Settings | 仓库 |
| F-097 | 插件默认参数：`microskills_propose_every`=3、`toolprune_evidence`=10、`toolprune_min_sessions`=2、`toolprune_sessions`=5、`toolprune_quiet_minutes`=60、`loopguard.envelope_min_samples`=5、`loopguard.judge_confidence`=0.7、`loopguard_nudges`=1、`loopguard.backstop_mult`=2.5、`droid_sidecall`=off | 仓库 README Settings 表 | 仓库 |
| F-098 | 插件每个动作以一行公告；任一部件失败，会话按未安装插件的方式继续 | 仓库 README | 仓库 |
| F-099 | fact proposer 与 judge / redirect 的模型调用走用户自己的 agent 与同一登录或套餐，其成本计入插件报告 | 仓库 README / 博客 | 仓库 |
| F-100 | 开源插件在 redirect 后仍卡住时提示开发者如何停止，不自行停止 turn | 博客 / 仓库 README | 博客 |
| F-101 | 常用命令：`status`、`microskills`、`toolprune`、`toolprune restore`、`config`、`config set <k>=<v>` | 仓库 README | 仓库 |
| F-102 | 工具剪枝按 agent 写入不同位置：Claude Code `.claude/settings.local.json`、Codex `.codex/config.toml`、Copilot CLI `.github/copilot/settings.local.json` | 仓库 README | 仓库 |
| F-103 | README 列出的受测版本区间含 Claude Code 2.1.300–2.1.310、Codex 0.153.1–0.164.0、Copilot CLI 1.0.83–1.0.102、Pi 1.2.0–1.3.0 | 仓库 README Supported versions | 仓库 |
| F-104 | `experiments/` 提供论文结果背后的 harness、launcher 与任务集，与已安装插件只共享 `tokeneconomizer/` | 仓库 README | 仓库 |
| F-105 | 包仅使用标准库；测试命令 `python -m pytest tests`，构建命令 `python3 scripts/build_plugin.py --out dist/marketplace` | 仓库 README | 仓库 |

## 八、局限与边界（F-106 ~ F-110）

| 编号 | 客观事实 | 信源定位 | 口径类型 |
|---|---|---|---|
| F-106 | 论文 §6 列出三类误判：micro-skill 过期、被剪工具重新需要、困难但有效的任务被误判为失败循环；三者各有恢复路径 | 论文 §6 | 论文 |
| F-107 | 论文实验覆盖三种广泛使用的编码 agent，未覆盖 Pi 等更精简的 harness | 论文 §6 | 论文 |
| F-108 | SWE-Bench 任务流是「相关但彼此独立的修复」，不是真实用户会话 | 论文 §6 | 论文 |
| F-109 | 四个采集信源均由作者团队发布；本次采集未取得独立第三方复现报告 | 本束采集记录 | 独立核验 |
| F-110 | 插件默认配置（microskills 关闭、循环干预不自行停止）与论文实验控制器配置不同 | 仓库 README vs 论文表 4 | 交叉差异 |

---

## 事实层自检（G1）

| 检查项 | 结果 |
|---|---|
| 事实条数 | 110 条，≥20 条门槛 |
| 编号连续性 | F-001 ~ F-110 连续，无跳号 |
| 因果 / 判断词 | 事实列无「因为」「所以」「导致」「错误」「失误」等词；差异仅登记为「表述不同」 |
| 可追溯性 | 每条含信源定位与口径类型 |
| 数字口径 | 逐组合、逐仓库、逐基准数字均取论文表格原值，不以博客的合并区间替代 |
| 冲突处理 | F-009、F-011、F-091、F-110 四处差异并存登记，不合并抹平 |
