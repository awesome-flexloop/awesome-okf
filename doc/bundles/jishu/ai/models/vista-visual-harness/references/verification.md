---
type: reference
title: "VISTA 博文 P0 核验报告与勘误"
description: "对量子位 VISTA 博文的双轮独立权威核验记录——18 项 P0 声明逐条对照 arXiv 论文、项目页、GitHub 仓库与 ARC Prize 官方方法学，附 8 项勘误（E-1~E-8）。"
tags: [vista, verification, errata, arxiv, arc-prize, provenance]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-01-20
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ"
  - id: arxiv
    url: "https://arxiv.org/abs/2610.02200"
  - id: arxiv-html
    url: "https://arxiv.org/html/2610.02200v1"
  - id: project
    url: "https://vista-research.github.io/"
  - id: github
    url: "https://github.com/joshhhhhan/VISTA"
  - id: arc-methodology
    url: "https://docs.arcprize.org/methodology"
  - id: arc-agi3-paper
    url: "https://arxiv.org/abs/2603.24621"
  - id: anthropic-harness
    url: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
---

# VISTA 博文 P0 核验报告与勘误

> **核验结论摘要**：博文对论文核心声明的转述**准确率高**——第一轮 25 项 P0 声明中 **22 项完全一致、3 项需加限定**（组件名译法、BabyVision 评测子集、共同第一作者表述）；ARC-AGI-3 满分 100、动作数少 57.4%、GPT-5.6 Sol 得分 99、三组件机制、双笔记结构等核心声明均与论文原文一致。但存在 **1 项重大遗漏（论文自身的局限）、1 项归因越界、7 项口径/上下文省略**，均在本报告逐条落地。
> **状态判定**：`stable`（非 `flagged`）——核心声明全部通过独立核验，无需降级；勘误完整落实。
> **二轮独立复核**：交付后由全新上下文的独立审查代理复核 26 项高风险声明，结论为 0 项事实性错误、1 项 F 编号溯源缺陷（P0，已修）、3 项需补限定（P1，已修）、6 项结构/清晰度改进（P2，已修）。
> **第三轮（源码与论文补充）**：新增 **55** 条源码/论文事实（F-086~F-140），全部对固定 commit `c97c354f` 或论文原文逐条取证；据此新增勘误 **E-10~E-16**（动作空间口径、上下文口径、像素量化、history 粒度与双实现、压缩分叉、按键计数），并把引用限定清单由三条扩展为八条。
> **第三轮独立复核**：由全新上下文的独立代理用自写脚本复算 13 项计数、Grep 验证 ~120 个符号、逐字比对 17 段引文、逐条比对 18 条命令——结论 **0 项 P0、2 项 P1、9 项 P2、6 项 P3**，均为"引用精度"问题而非事实错误；P1/P2/P3 已全部闭环（新增 F-131~F-140 补齐计数类声明的独立背书）。
> **核验方式**：两轮独立上下文子代理分别对照 arXiv HTML 全文 + LaTeX 源码包、官方项目页、GitHub 仓库、ARC Prize 官方方法学与各作者机构主页取证。

## 一、P0 声明核验结果（18 项）

| # | 声明 | 结论 | 权威源证据 |
|---|------|------|-----------|
| P0-01 | 论文为《VISTA: A Visual Harness for Reasoning in an Interactive World》 | ✅ | arXiv:2610.02200，2026-10-01 提交，MIT，CC BY 4.0 |
| P0-02 | 三个核心组件为视觉观测 / 无损视觉记忆 / 视觉检查 | ⚠️ | §3.1 原文：visual observations / lossless visual memory / **visual inspection**。博文第三项作"主动视觉检查"，"主动"非论文用词 → **E-1** |
| P0-03 | 每一帧原样存到上下文之外，含动画中间帧，按回合号与帧号索引 | ✅ | §3.1 + §1："stores every frame returned by the environment, including intermediate animation frames, in its original form… indexed by turn and frame number" |
| P0-04 | Claude Opus 5.0 在 ARC-AGI-3 相对人类动作效率得分 100.00，完成全部 25 个公开游戏 | ✅ | 摘要 + §4.2 + 表1；官方记分卡可独立核验 |
| P0-05 | 所用动作数比首次游玩的人类基线少 57.4% | ✅ | §4.2："uses **7,302 actions** in total, **57.4% fewer** than the human reference of **17,135 actions**" |
| P0-06 | GPT-5.6 Sol 同样全部通关，得分 99 | ✅ | §1 + 表1 + 表2 题注：RHAE **99.00**，max reasoning effort |
| P0-07 | GameWorld 170 项任务成功率 40.0% → 63.3% | ✅ | §5.1（34 个浏览器游戏 / 170 任务 / 5 类题材）+ 图11 |
| P0-08 | AI GameStore 10 个游戏综合得分 47.3 → 140.3，人类中位数归一化为 100 | ✅ | §5.1 + 附录 A.3 公式5/6 + 图11。注：为**逐游戏归一化后的几何平均**，非原始分求和 |
| P0-09 | BabyVision 39 道迷宫与连线题准确率 41.0% → 63.2% | ⚠️ | §5.2 数字正确；但 BabyVision 全集为 **388 项任务 / 22 子类**，39 是所评估子集 → **E-6** |
| P0-10 | 64×64 画面放大为 512×512 PNG | ✅ | §4.3："a **512×512 PNG image**… obtained by **8× nearest-neighbor upscaling of the official 64×64 frame**" |
| P0-11 | inspect 工具可指定历史回合取画面、裁剪放大、多帧对比 | ✅ | 附录 A.4 算法1 + §3.1；另有 read_pixels 返回精确 RGB 值 |
| P0-12 | GUIDE.md 记跨关卡可复用规则，WORKING.md 记当前关卡状态与计划 | ✅ | §3.2 + 附录 A.2；A.4 补充 WORKING.md 跨 RESET 与上下文重启保留、关卡推进后清空 |
| P0-13 | 默认每次动作后只向模型展示最后一帧，中间帧归档待调 | ✅ | 图5 题注 + 附录 A.2 + 算法1 |
| P0-14 | VISTA 不训练任何新模型，只改变视觉信息的获取/保存/使用方式 | ✅ | §3.2："The harness is purely mechanical and **does not involve any trained model**" |
| P0-15 | 论文研究问题表述与"显式注意力"概念 | ✅ | §3.1："an *explicit attention mechanism* over the interaction history"；摘要 "long-horizon vision" |
| P0-16 | 既有做法为文本网格 + 代码世界模型；早期画面会被移出上下文或摘要替代 | ✅ | §4.2 + §4.3 + §1 + §3 |
| P0-17 | 未来方向为更接近物理世界的具身任务 | ✅ | §7："such as embodied tasks in environments that more closely resemble the physical world" |
| P0-18 | 作者名单与共同第一作者标注 | ⚠️ | 论文脚注为 "*Co-first authors.*"，项目页渲染为 "*co-leads*"；同事实两种表述。Qiushi Han 在 MIT ORC 名录登记名 **Josh Han**（邮箱与论文通讯一致） |

| P0-19 | 消融六步的真实标签与得分（(i) 图像观测 47.32 → (ii) 动作/时间上限 51.66 → (iii) 连续对话 65.82 → (iv) 双笔记 70.05 → (v) 无损视觉记忆+视觉检查 94.10 → (vi) 精确像素读出 99.00） | ✅ | §4.3 + 附录 A.2 + 图5 题注逐条对上；并确认 VISTA 自身组件在 (v)(vi) 才登场，(i)–(iv) 仍按官方协议每次动作自动获得至多 7 帧 |
| P0-20 | 成本/token 口径（308 图像 token vs ~4K 文本 token/帧；71.9M vs 30.7M token/局；780K→200K→100K 上下文；4× 比 8× 少 75% 图像 token） | ✅ | §4.3 + 图6b/图7b |
| P0-21 | 人类参考样本构成（GameWorld 两名 CS 研究生、每任务 100 动作预算；BabyVision Maze 95.0% / 连线 89.5%、加权 92.3%；AI GameStore Prolific 人类中位数） | ✅ | 附录 A.6 + §5.1 |
| P0-22 | ARC-AGI-3 规格（64×64、16 色、每环境 ≥6 关、含 Undo）与官方榜政策（公开集分数永不登官方榜、非 AGI 进展有效度量、社区榜自报不核验） | ✅ | arXiv:2603.24621 §2.3/§3.4/§4.3.1/§4.3.2 |
| P0-23 | 表 1 对比系统与 effort 差异（官方实现 Sol max 13.33、Opus 5.0 **high** 40.68†；Schema 95.35 / 98.98、ewma 98.97、Retrodict 99.86、Tycho 100.00；VISTA Sol max 99.00、Opus 5.0 **xhigh** 100.00） | ⚠️ | §4.2 表 1 —— 数值全对，但**推理强度与评测协议不同**，见勘误 E-9 |
| P0-24 | 工具签名与 `history` 工具（`inspect(question, views) -> images`，view/region 字段；`read_pixels`；`history`） | ✅ | 附录 A.4 算法 1 + §3.1 |
| P0-25 | 项目页数字（7,542 动作 / 56% / Sol 98.27 / 官方基线 30.16） | ✅ | vista-research.github.io 排行榜与说明 |

| P0-26 | 源码轮事实（F-086~F-140，共 55 条）经独立代理用**自写脚本**复核 | ✅ | 13/13 计数项**完全一致**（含"原始匹配数 vs 去重名数"双口径与非递归目录计数规则）；~120 个具名符号/常量/CLI 参数/环境变量/入口点**逐个 Grep 存在**；17 段引文 16 段逐字一致、1 段近失；18 条命令与 README/`scripts/` **逐条一致**，无杜撰选项 |
| P0-27 | 独立代理指出的 2 项 P1（AI GameStore 按键数、`history` 两套实现混谈） | ⚠️ | 均已修正：按键数 10 → **11**（E-16）；`history` 拆分为 core 与 ARC-AGI-3 两套语义并各自登记 F-135（E-15） |
| P0-28 | 独立代理指出的 9 项 P2（计数类声明缺独立 F 编号背书） | ⚠️ | 全部补登 F-131~F-140（契约层构成、固定版本与镜像常量、并发默认值、竞争模式符号、`history` 双实现、按键集、人类样本量、逐局动作数、答案协议、调色板校验），并在正文逐处挂接 |
| P0-29 | 独立代理指出的 6 项 P3（引文近失、指针偏移、措辞过宽） | ⚠️ | 全部修正：像素读出错误串补回 "The …has been reached."；`save_compact_checkpoint` 实现指针改为 `dispatcher.py:98` 派发 + `:187` 回执；四基准同构性表述限定到三个非 arc3 包；`start_turn`/`end_turn` 参数名更正 |
| P0-30 | 本地检出为 depth=1 浅克隆，提交总数无法本地复核 | ⚠️ | F-086 已补注"提交总数经 GitHub API 取得、本地不可复核" |

**附加核验（非 P0 但影响可信度）**：

- **Anthropic 脉络归因**：Anthropic《Effective harnesses for long-running agents》确实发布于 **2025-11-26**，含特性清单文件、`claude-progress.txt` 进度文件与 git 提交保存已完成工作 → 博文"去年 11 月"表述**成立**。但 **VISTA 论文并未引用该文**（64 条参考文献中唯一 Anthropic 出处是 Claude Opus 5 模型公告）→ **E-2**。
- **基线缺失**：博文只给"满分 100"，未给官方实现基线。论文表1：官方实现 Opus 5.0 RHAE **40.68**、GPT-5.6 Sol RHAE **13.33**（10,619 动作）→ **E-5**。
- **多次运行方差缺失**：附录 B.1 → GameWorld 63.33±2.37%、BabyVision 63.23±3.00%、ARC-AGI-3 Sol 99.04±0.17 → **E-4**。
- **论文局限完全缺失**：§6 数据污染可能性与私有集评估要求 → **E-3**（本报告最重大的遗漏项）。
- **代码已开源未提**：GitHub `joshhhhhan/VISTA`，MIT License → **E-7**。

## 二、勘误清单（E-1 ~ E-8）

| 编号 | 级别 | 类型 | 源文表述 | 权威口径 | 处置 |
|------|------|------|---------|---------|------|
| **E-1** | ⚠️ 轻微 | 组件名译法 | "主动视觉检查" | 论文 §3.1 **组件名**：`visual inspection`（图3c：`model-directed visual inspection`）。注：论文确实用 actively（"actively inspect" / "actively retrieve"），故问题仅在组件名译法 | 正文按论文组件名呈现并标注博文用词，不宣称"论文未用主动" |
| **E-2** | ⚠️ 需修正 | 归因越界 | 将 Anthropic 2025-11 harness 博文作为 VISTA 直接脉络前史叙述 | 该文存在且日期为 2025-11-26，但论文未引用 | 正文区分"博主叙述的脉络关联"与"论文实际引用" |
| **E-3** | ❌ 重大 | 关键局限缺失 | 未提及数据污染可能性 | §6：模型在公开基准之后发布，无法排除游戏已入训练数据；需私有集评估 | 正文显著位置补入，作为"满分 100"的必要限定 |
| **E-4** | ⚠️ 需补充 | 口径省略 | "63.3%""63.2%""99"无方差 | 附录 B.1：63.33±2.37% / 63.23±3.00% / 99.04±0.17 | 正文补入方差口径 |
| **E-5** | ⚠️ 需补充 | 基线缺失 | 只说"满分 100" | 表1：官方实现 Opus 5.0 = 40.68，GPT-5.6 Sol = 13.33 | 正文补入基线→VISTA 的提升幅度 |
| **E-6** | ⚠️ 信息补全 | 评测范围 | "在 BabyVision **选取的** 39 道迷宫与连线题上"（博文已限定为所选子集，非误读） | 全集 388 项任务 / 22 子类；39 为所评估的 20 迷宫 + 19 连线子集 | 正文补上全集规模并按论文精确表述 |
| **E-7** | ⚠️ 需补充 | 资产遗漏 | 未提代码 | GitHub `joshhhhhan/VISTA`，MIT License，含运行要求 | 正文补入（读者可行动性最高的信息） |
| **E-9** | ⚠️ 需限定 | 对比混淆 | 40.68 → 100.00 直接作为"提升幅度" | 40.68 为 Opus 5.0 **high** + 官方协议（5× 动作预算 / 12 小时，且由官方公布分数换算）；100.00 为 Opus 5.0 **xhigh** + 2,000 动作 / 48 小时 | 正文标注 effort 与协议差异，并给出严格同 effort 对照（Sol max 13.33 → 99.00） |
| **E-15** | ⚠️ 需分述 | 工具语义 | `history` 被合并描述为"attempts/events 视图 + start/end 区间" | **两套实现语义不同**：通用 `TaskContext`（`support.py:664`）用 `start`/`end`/`limit` 并返回 `{"events","truncated"}`；ARC-AGI-3 控制器（`arc3/*/controller.py:576`）用**必填** `view`（`attempts`/`events`）+ `start_turn`/`end_turn`/`limit` [F-135] | 正文拆为两行分别说明 |
| **E-16** | ⚠️ 需更正 | 计数 | AI GameStore 动作集写作"10 个按键" | `KEY_VALUES` 实为 **11** 项（UP/DOWN/LEFT/RIGHT/SPACE/Z/SHIFT/W/A/S/D），派生 `TAP_ACTIONS` 11、`HOLD_ACTIONS` 11、`MODEL_ACTIONS` 23 [F-136] | 正文改为 11 + 11 + NOOP |
| **E-10** | ⚠️ 需更正 | 基准规格 | 事实 F-084 写"5 个关键动作 + Undo" | ARC-AGI-3 §2.3.2：五个关键动作 **+ Undo + 一类坐标选择动作**（点击格子）[F-126] | 正文按 §2.3.2 精确表述；源码 `ACTION6` 即该类 |
| **E-11** | ⚠️ 需注明来源 | 上下文口径 | 论文称消融默认 200K 上下文 | 源码 `DEFAULT_MODEL_CONTEXT_WINDOW = 272000`（回落 128000）[F-127] | 两处均标注来源，不混用 |
| **E-12** | ⚠️ 需精确 | 工具语义 | "exact pixel readout / 数值 RGB 值" | 实现为 4 位/通道量化 + 64 符号调色板 [F-099] | 正文表述为"量化后的精确读出" |
| **E-13** | ⚠️ 粒度差异 | 工具语义 | `history` 被描述为"回看任意历史帧" | 源码返回动作/事件流（`attempts`/`events` 视图 + `start`/`end` 区间）[F-095] | 正文按"动作/事件回看"表述 |
| **E-14** | ⚠️ 源码更细 | 机制表述 | §3.2 统一叙述"上下文交接" | 压缩**按后端分叉**：Claude 原生压缩 / Codex 注入式检查点交接，且压缩边界后强制先存检查点 [F-108][F-122][F-128] | 正文分述两条路径 |

| **E-8** | ⚠️ 时序 | 版本差异 | 未区分项目页与论文 | 项目页（2026-08-05）数字系统性不同：7,542 动作 / 56% / Sol 98.27 / 基线 30.16；论文：7,302 / 57.4% / 99.00 / 40.68 | 正文一律以论文口径为准并标注项目页差异来源 |

## 三、核心声明与"不可省略的限定"四件套（第一轮口径）

> 第一轮交付时的口径。源码轮补充后限定清单扩展为**八条**，完整版见 [10 论文谱系与口径边界](../concepts/10-paper-lineage.md) 第六节。

引用 ARC-AGI-3 满分 100 这一结论时，必须同时给出：

1. **基线与其可比性**：官方实现 GPT-5.6 Sol（max）13.33、Opus 5.0（**high**）40.68 [F-077]。注意 40.68 是 high 推理强度、官方协议（每关 5× 人类基线动作预算 / 12 小时）下的**由官方公布逐局分数换算值**；VISTA 的 100.00 是 Opus 5.0（**xhigh**）、2,000 动作 / 48 小时协议——两者不只差 harness。严格同模型同 effort 的对比是 Sol(max)：13.33 → 99.00 [F-079]。
2. **数据污染可能性**：模型在公开基准之后发布，作者无法排除游戏已入训练数据 [F-068]
3. **未见题目上的表现**：需在 ARC-AGI-3 私有集（半私有 55 + 完全私有 55，且刻意与公开集分布外）上评估 [F-074]
4. **基准方的官方立场**：ARC Prize 明确"永不把任何系统的公开集分数登入官方榜"、公开集评估"绝不能视为 AGI 进展的有效度量"、社区榜分数自报且不予核验；官方另开源一个以人类回放即可在全部公开环境上取得 100% 的 harness [F-084]

## 四、RHAE 计分口径（官方方法学）

- 单关得分 = （人类基线动作数 / AI 动作数）²
- 单关上限：人类基线的 **1.15 倍**
- 未通关关卡计 **0**
- 游戏得分：各关得分的**加权平均**（以关卡序号 1-indexed 为权重）
- 总分：各游戏分的**平均**，最终落在 0%–100%
- 人类基线：每关"动作数最少者"的**上中位数**（upper median human）

> 这意味着"满分 100"要求完成全部 25 个游戏的全部关卡（含最后一关），而非部分关卡的高分累加。

## 五、核验未覆盖的边界

- 未验证 ARC-AGI-3 私有/半私有游戏环境（不在任何公开仓库，需 API key 授权）——本束不收录，仅引用其公开构成数据。
- 未复现论文实验（需付费模型 API + Docker 环境 + 大量算力）；所有实验数字均为**转述论文**，未独立重跑。
- 论文图11 的结果面板在 arXiv HTML 中缺失（仅渲染截图行），数值取自 arXiv LaTeX 源码包的 `figures/fig_results.pdf`，并由 §5.2 与附录 A.6 的人类参考值交叉印证。
- 未独立核验各基准论文本身的方法论质量（GameWorld / AI GameStore / BabyVision），仅核验 VISTA 论文对它们的引用与口径。
- 官方项目页标注 "Aug 5, 2026"，而 Kaiming He 个人主页的论文列表标注该 blogpost 为 "Aug 6, 2026"——日期存在 1 天差异，不影响任何结论，本束统一采用 arXiv Comments 字段的 2026-08-05。

## 六、关联

- 事实登记：[article-source.md](article-source.md)
- 知识地图：[knowledge-map.md](knowledge-map.md)
- 信源边界：[source-manifest.md](source-manifest.md)
