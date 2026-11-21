---
type: Reference
title: "论文事实台账（F-001 – F-072）"
description: "《A Programming Paradigm for Spatiotemporal Composability》arXiv v1 的 72 条编号事实，逐条标注页码与信源"
tags: [spatiotemporal-composability, cordis, facts, arxiv-2608-25512]
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
sources:
  - id: arxiv-abs
    resource: https://arxiv.org/abs/2608.25512
    title: arXiv 元数据页
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 全文 PDF
---

# 论文事实台账

> 本文件是事实登记的**第一份**，与 [paper-source.md](paper-source.md) 构成双份登记，两边 `F-\d{3}` 编号集合须相等且连续。
> 全部事实为客观陈述，不含因果推断与评价；页码按 PDF 文件页序（与正文印刷页码一致至 ±1）。
> 信源代号：`abs` = arXiv 元数据页；`pdf` = v1 全文；`repo` = 本知识库既有文件；`secondary` = 二手解读（仅登记其口径，不作事实依据）。

## A. 元数据与版本（F-001 – F-008）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-001 | 论文标题为 *A Programming Paradigm for Spatiotemporal Composability*，arXiv 编号 2608.25512，当前版本 v1 | abs / pdf p1 |
| F-002 | 作者三人：Yifan Shi（北京大学、DeepSeek-AI）、Wei Zhang（北京大学）、Tianyi Cui（DeepSeek-AI） | abs / pdf p1 |
| F-003 | v1 提交时间为 2026-08-26 08:22:19 UTC | abs submission history |
| F-004 | arXiv Comments 字段为「92 pages, 1 figure, 2 tables」 | abs |
| F-005 | 学科分类 cs.PL 与 cs.SE；ACM 分类 D.2.11、D.3.1、D.3.3 | abs |
| F-006 | arXiv 签发的 DOI 为 10.48550/arXiv.2608.25512 | abs |
| F-007 | 参考文献编号至 [126] | pdf 参考文献 |
| F-008 | 本库 `cordis/references/background-paper.md` 记录「草稿日期 2026 年 8 月 13 日」「约 88 页」「约 126 篇参考文献」 | repo |

## B. 问题与动机（F-009 – F-018）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-009 | §1.1 定义时间可组合性：组件移除时其对共享环境的修改须完整且安全地回退；要求追踪资源分配、事件注册与状态变更并有序回收 | pdf p4 |
| F-010 | §1.1 定义空间可组合性：组件须能声明、发现并解析彼此依赖；要求管理依赖拓扑并随依赖变化协调生命周期 | pdf p4 |
| F-011 | §1.1 静态对应物：时间维度归约为词法作用域（RAII、bracket patterns），空间维度归约为模块导入解析 | pdf p4 |
| F-012 | §1.2.1 VSCode 将全部扩展运行于共享的 extension host，未提供在运行时卸载单个扩展代码的机制 | pdf p4 |
| F-013 | §1.2.1 按安装量排序的前 100 个扩展中，87 个包含可执行代码，移除时需重启 extension host | pdf p5 |
| F-014 | §1.2.1 同一批前 100 个扩展中，仅 7 个声明了对非内置扩展的 `extensionDependencies` | pdf p5 |
| F-015 | §1.2.1 脚注 1 说明上述扩展数据取自 Visual Studio Code Marketplace，日期 2026-06-09 | pdf p5 |
| F-016 | §1.2.1 VSCode 提供 `deactivate` 钩子，其用途是 host 进程终止时的优雅关闭回调；该钩子把效应销毁与 `activate` 中的效应创建分离 | pdf p5 |
| F-017 | §1.2.1 `vscode.extensions.getExtension(...).exports` 返回值默认为 `any`，依赖方无法依赖受检接口 | pdf p5 |
| F-018 | §1.2.3 操作系统在进程粒度提供时间可组合性、容器编排器在服务粒度提供空间可组合性；重启会丢弃进程内累积状态，重建耗时数秒至数分钟 | pdf p5–6 |

## C. 预备知识与贡献（F-019 – F-023）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-019 | §1.3 列出五项贡献：可逆效应、响应式协同效应、上下文范式、动态组合演算及其元理论、Cordis 实现 | pdf p6 |
| F-020 | §2.1 效应系统把判断细化为 `Γ ⊢ t : T^effect`；单子式效应源于 Moggi、Wadler 在 Haskell 普及；代数效应源于 Plotkin & Power，效应处理器源于 Plotkin & Pretnar，Koka / Eff / OCaml 5 采纳 | pdf p7 |
| F-021 | §2.2 协同效应细化上下文为 `Γ^coeffect ⊢ t : T`；余单子式源于 Uustalu & Vene、Petricek 等；分级协同效应用预序半环 `(S, ≤, +, ×, 0, 1)`，0 未用、1 线性、n 有界、∞ 无限制 | pdf p7–8 |
| F-022 | §2.3 论文立场是 reify effect / coeffect 的概念结构供运行时直接操作，而非给静态类型系统增加标注 | pdf p8 |
| F-023 | §3 开篇说明局部保证止于其他组件进入；§3.3 统一两类上下文，§3.4 建立效应独立性与协同效应交换性 | pdf p9 |

## D. 可逆效应（F-024 – F-033）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-024 | §3.1 把效应建模为 `Γ → Γ × (Γ → Γ)`：作用于当前上下文，返回修改后的上下文与一个显式逆函数 | pdf p9 |
| F-025 | Definition 1 定义扭转组合 `(f₁,g₁) ∘ (f₂,g₂) ≔ (f₁∘f₂, g₂∘g₁)`，构成幺半群 `𝔗Γ`，单位 `(idΓ, idΓ)` | pdf p9 |
| F-026 | Definition 2 定义效应上下文 `∂Γ ≔ Γ × (Γ → Γ)`，即 `(γ, φ)`，其中 φ 是逆的累积器；初始态为 `(γ₀, idΓ)` | pdf p10 |
| F-027 | Definition 3 定义 `trackΓ = (f,g) ↦ (γ,φ) ↦ (f(γ), φ ∘ g)` | pdf p10 |
| F-028 | Theorem 5 证明 `trackΓ` 是从 `𝔗Γ` 到 `∂Γ → ∂Γ` 的幺半群同态 | pdf p10–11 |
| F-029 | Definition 6 定义 `recoverΓ = (γ,φ) ↦ (φ(γ), idΓ)`；Theorem 7 在 `g(f(γ)) = γ` 下证明 `φ(γ) = γ₀` 这一 soundness invariant 在追踪步后保持 | pdf p11 |
| F-030 | §3.1.2 列出 track/recover 两点局限：逆在看到状态前即固定、`recover` 全有或全无；Definition 8 定义 `𝔈Γ` 与见证版 `𝔈*Γ`，见证只要求 `g(δ) = γ` 在施加效应的那个状态成立 | pdf p12 |
| F-031 | Definition 9 定义效应组合 `f ⋄ g`；Theorem 10 证明 `(𝔈Γ, ⋄)` 为幺半群，单位 `ηΓ ≔ γ ↦ (γ, idΓ)` | pdf p13 |
| F-032 | Theorem 15 指出 `effectΓ` 不把 `𝔈*Γ` 映入 `𝔈*∂Γ`（除 `g∘f = idΓ` 外），但 soundness invariant 恒成立；Theorem 16 证明逆序回退使每个 revert 恢复其 application 所针对的状态 | pdf p14–15 |
| F-033 | Definition 17 定义递归的效应迭代器 `ℑΓ`，每次迭代产出新状态、逆函数与 `Maybe(ℑ)` 续延 | pdf p15 |

## E. 响应式协同效应与上下文范式（F-034 – F-043）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-034 | Definition 19 定义协同效应上下文 `Σ ≔ (k : K) ⇀ 𝒱k`，为有限偏函数，类型族 𝒱 保证每个键有对应值类型 | pdf p17 |
| F-035 | Definition 20 定义 `set(k,v)` 的类型为 `𝔈*Σ`，其逆为 `λσ'. σ' ∖ k`；论文表述为「协同效应操作本身即效应」 | pdf p17 |
| F-036 | §3.2.2 定义满足谓词 `σ ⊧ d ≔ ∀k ∈ d. k ∈ dom(σ)`，因 `dom(σ)` 有限而可判定 | pdf p18 |
| F-037 | Definition 21 定义协同效应规范 `𝔇Σ ≔ Set(K)`；Definition 22 定义 `notify_d` 三分类 activating / deactivating / neutral | pdf p18 |
| F-038 | Definition 23 给出两种 realization：in-place（原地修改 + 非平凡逆）与 derived（派生新上下文 + 恒等逆，回收即丢弃派生上下文） | pdf p19 |
| F-039 | Definition 24–25 定义隔离 `Σ_iso ≔ (K ⇀ R) × ((r : R) ⇀ 𝒱r)`，两层解析 `k → ρ(k) → σ(ρ(k))` | pdf p19–20 |
| F-040 | Definition 26–27 定义拦截 `Σ_inter ≔ ((k:K) → ℳk) × ((k:K) ⇀ (ℳk → 𝒱k))`；`get` 合并组件声明与上下文元数据，合并右偏使上下文元数据优先 | pdf p20–21 |
| F-041 | Definition 28 定义统一上下文 `Γ∞ ≔ μΓ. Γ × (Γ → Γ) × Σ`，三个投影为递归状态、本级逆累积器、协同效应上下文 | pdf p21 |
| F-042 | §3.3.2 以「无操作序列可区分」定义观测等价 `≃S`，§3.1 的所有等式改按该等价读取；Definition 42 给出迭代器独立性两条件（变换两两交换、一方变换不扰动另一方产出的逆与续延） | pdf p23、p27 |
| F-043 | Theorem 45 证明不同键上的操作相互独立；Definition 46 要求每个键携带交换性证明（witnessed coeffect），义务落在提供方；Theorem 47 给出 provision 与 operation 键集不交且共享键可交换时两迭代器独立的条件 | pdf p29–30 |

## F. 动态组合演算（F-044 – F-050）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-044 | Definition 48 定义组件为三元组 `(d, p, e)`：依赖规范、供给键集、见证效应迭代器；`p` 之外不得安装绑定 | pdf p31 |
| F-045 | Definition 49 定义 fiber 为七元组 `⟨d, p, e, π, σ, τ, θ⟩`；生命周期状态 `Θ ::= Inactive | Reloading(i,g,ω) | Active(g,ω) | Unloading(g,ω)` | pdf p32 |
| F-046 | Definition 50 定义状态携带注册表 `Fγ : 𝔑 ⇀ 𝔉Γ`，其父指针构成以 `root` 为根的树 | pdf p32 |
| F-047 | §4.2 给出九条规则：编排 `O-Insert` / `O-Retire` / `O-Remove`，生命周期 `L-Begin` / `L-Iter` / `L-Finish` / `L-Divert` / `L-Leave` / `L-Unload`；Figure 1 画八条，`O-Retire` 因在四个状态上均为自环而省略 | pdf p34 |
| F-048 | Definition 53 定义 target view 为声明键到**提供者名字**的映射（而非值），并定义 `quiet(γ)`；§4.2.2 说明记录提供者使「换了一个提供等价值的新 fiber」可被检出 | pdf p35 |
| F-049 | §4.2.2 `L-Leave` 只记录停用决定而不立即行动；`L-Unload` 是唯一应用 accumulator 的规则，其前提 `¬relied_n(γ)` 称为 guard | pdf p36–37 |
| F-050 | Definition 55 定义 confinement：效应函数只能写自身表与其声明键在提供方表中的值，不得读写其他表、控制字段或未被任何键绑定的位置 | pdf p38 |

## G. 元理论与扩展（F-051 – F-057）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-051 | Definition 63 给出注册表良构四条件（父指针落在注册表内、供给两两互斥、committed view 在声明键上全函数、被解析到的提供者已安装）；Theorem 64 证明九条规则保持良构性 | pdf p43 |
| F-052 | Theorem 68（Recovery exactness）证明施加 fiber 的 accumulator 后，各表与「该 fiber 从未开始」时其他步骤留下的表 `≃K`-等价；Corollary 69（Terminal recovery）给出 episode 关闭后 `σ_n = ∅`，满足 `O-Remove` 前提 | pdf p46–47 |
| F-053 | Theorem 70（Ordering）证明 `L-Begin` 仅在依赖已提供时发生、提供者撤回晚于依赖者停用、绑定在依赖者 episode 内稳定；Theorem 71（Resolution coherence）证明一次 transition 的所有迭代针对同一 resolution `ω` | pdf p47–48 |
| F-054 | Definition 72 定义优先关系 `n ≺ m ≔ p_n ∩ d_m ≠ ∅`；Theorem 73（Progress）在 ≺ 无环、`len(e_n) ≤ K`、名字集有限前提下给出无死锁与 `S(n) ≤ (K+3)(V(n)+1)` | pdf p49 |
| F-055 | Definition 74 定义 support set `A` 仅读 `τ, π, d, p`；Definition 76 定义 total on its provision（激活完成须安装 `p` 的全部键） | pdf p51–52 |
| F-056 | Theorem 80（Confluence）证明生命周期关系合流，规范形是从 `γ₀` 按 `⊲` 线性序各取一个 episode 的「一次性静态装配」；§4.3.5 明确该结论只谈状态、不谈过程期间产生的 emissions | pdf p54–55 |
| F-057 | §4.4 给出四个扩展：异步惯性（只取 `L-Divert` 的 landing 分支）、失败（错误写入 fiber、Confluence 排除失败 fiber）、隔离（键集放大为 `K × R`）、配置修订（retire→deactivate→remove→reinsert 的复合） | pdf p55–57 |

## H. 实现、案例与边界（F-058 – F-072）

| 编号 | 事实 | 出处 |
|---|---|---|
| F-058 | §5 给出三层架构：core library / component loader / 应用框架（Koishi）；Table 2 列出 `Γ∞ ↔ ctx`、`𝔈Γ,ℑΓ ↔ Effect callback`、`Σ ↔ ctx[@@store]`、`ω ↔ fiber.committed`、`target ↔ fiber.target`、`inertia ↔ fiber.inertia` 等映射 | pdf p57–58 |
| F-059 | §5.1.1 所有上下文变更经单一原语 `ctx.effect`（`effectiter_Γ` 的实现），同时接受 `𝔈Γ` 与 `ℑΓ`；运行时**不校验** witness，逆真能回退与键上操作可交换均为组件作者义务 | pdf p59 |
| F-060 | Algorithm 1 的 `execute` 在每次迭代前检查 guard，把产出的逆以前置方式 LIFO 累积；`ctx.effect` 的 `armed` 标志使 `dispose` 至多触发一次 | pdf p59–60 |
| F-061 | §5.1.2 三个符号槽 `@@store` / `@@isolate` / `@@intercept`，`ctx.get` 走两层解析；Algorithm 3 的 `notify` 仅对「键在 `fiber.inject` 且 realm 相同」的 fiber 调用 `refresh` | pdf p60–61 |
| F-062 | Algorithm 4 把 `ctx.use` 的实例化实现为父 fiber 的一个被追踪效应，其逆把子 fiber 的 target 置 ⊥ 并触发 unload；Algorithm 5 的 `refresh` / `reload` / `unload` 互相递归实现惯性，其中 Line 10 先标 UNLOADING、Line 14 提交 committed view、Line 25 等待依赖者进入 INACTIVE 后才执行 `dispose` | pdf p61–63 |
| F-063 | Algorithm 6 的 Proxy 沿 fiber 链向上解析属性，遇到「声明但未提交」抛 `INACTIVE_ACCESS`、到根仍未声明抛 `UNDECLARED_ACCESS` | pdf p64 |
| F-064 | Definition 81 定义 entry 六字段 `id / url / isolate / intercept / config / disabled`；§5.2.1 按字段差异分派最小扰动操作（`isolate` 重指派 realm、`intercept` 原地更新不触发 reload）；§5.2.2 把 HMR 分为模块分类、陈旧条目检测、事务化重载三阶段，无需开发者标注 acceptance boundary | pdf p65–69 |
| F-065 | §5.3 Koishi 有四年开发史与 4000+ 社区插件，服务端与 Web 控制台是两个独立 Cordis 应用；脚注 4 说明 Koishi 当前用 Cordis v3、论文呈现 v4，核心组合模型两版共享；Threats to validity 明确该证据为单生态、单宿主语言、观察性而非对照实验 | pdf p69 |
| F-066 | §6.1 系统边界判据：位置在系统能独占修改且能恢复原状时属「内」，否则属「外」，外部操作按 `idΓ` 处理；跨边界操作分 acquisition（`open` / `malloc` / `fork` 安装记录，可逆）与 emission（`write` / `send` 推数据越界，不可逆）两阶段 | pdf p70–71 |
| F-067 | §6.3 依赖声明构成 capability-based 访问控制，`inject` 是能力请求、context proxy 是能力中介；不可信代码的沙箱需要语言之外的执行边界 | pdf p72 |
| F-068 | §6.5 依赖环使相关组件永久 inactive，且可从声明静态预测；把双向交互分解为细粒度集成组件时，其数量在最坏情形随 n 二次增长 | pdf p74 |
| F-069 | §6.6 形式模型只提供按 key 的名义链接，缺版本/结构链接，导致接口漂移与键碰撞；三条应对为键命名空间、peer dependencies（Cordis 当前采用）、结构兼容性 | pdf p75 |
| F-070 | §7.1 与 Heunen 等的 dagger / inverse arrows 对比：论文要求的是单侧逆、运行时追踪、且不要求整个计算可逆 | pdf p78 |
| F-071 | §7.2 与 COP 对比：COP 的 layer 既不追踪也不回退副作用、激活不由依赖满足度驱动；与 AOP 对比：coeffect 是组件显式声明的横切点而非 oblivious 的 pointcut | pdf p79 |
| F-072 | §7.4 指出 FRP 的 glitch freedom 在 Cordis 无对应物，Cordis 只保证单次 transition 不跨两个 resolution（Theorem 71）；§8 把自我演化 agent harness 列为未来验证方向 | pdf p82–83 |

---

## 口径说明

- 本台账只登记论文原文与 arXiv 元数据可回溯的陈述。二手解读中的 DeepSeek Harness 产品数据（workspace 成员数、四种预设模式、启动命令等）不属论文范围，未纳入 F 编号。
- F-008 记录的是本库既有文件对**早期草稿**的描述，与 F-003/F-004 的 arXiv v1 口径构成版本差异，详见 [verification.md](verification.md)。
