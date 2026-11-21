---
type: Reference
title: "论文事实清单（双份登记之二）"
description: "按论文章节重排的 F-001 – F-072 事实索引，与 facts.md 构成双份一致性核对"
tags: [spatiotemporal-composability, cordis, facts, source-index]
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
sources:
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 全文 PDF
  - id: facts
    resource: facts.md
    title: 本包事实台账
---

# 论文事实清单（章节视图）

> 本文件是事实登记的**第二份**，按论文章节重排以便读者按图索骥。完整表述、页码与信源见 [facts.md](facts.md)。
> 双份核对的判据：两份文件用 `^\|\s*F-(\d{3})\s*\|` 提取的编号集合相等、连续、无跳号。

## 元数据（不在正文章节内）

| 编号 | 一句话事实 |
|---|---|
| F-001 | 标题、arXiv:2608.25512、v1 |
| F-002 | 三位作者与北大 / DeepSeek-AI 归属 |
| F-003 | v1 提交 2026-08-26 08:22:19 UTC |
| F-004 | 92 页 / 1 图 / 2 表 |
| F-005 | cs.PL、cs.SE 与三个 ACM 分类号 |
| F-006 | DOI 10.48550/arXiv.2608.25512 |
| F-007 | 参考文献编号至 [126] |
| F-008 | 本库既有包记录的早期草稿口径（8-13 / 88 页） |

## §1 Introduction

| 编号 | 一句话事实 |
|---|---|
| F-009 | 时间可组合性的定义与追踪要求 |
| F-010 | 空间可组合性的定义与拓扑要求 |
| F-011 | 静态对应物：词法作用域 / 模块导入解析 |
| F-012 | VSCode 共享 extension host，无运行时单扩展卸载 |
| F-013 | 前 100 扩展中 87 个含可执行代码 |
| F-014 | 前 100 扩展中仅 7 个声明非内置扩展依赖 |
| F-015 | 扩展数据取自 Marketplace，日期 2026-06-09 |
| F-016 | `deactivate` 仅用于进程终止，创建与销毁分离 |
| F-017 | `getExtension(...).exports` 默认 `any`，无受检契约 |
| F-018 | OS 进程级 / 容器服务级粗粒度替代及其代价 |
| F-019 | §1.3 五项贡献 |

## §2 Preliminaries

| 编号 | 一句话事实 |
|---|---|
| F-020 | 效应系统的判断形式与单子式 / 代数效应谱系 |
| F-021 | 协同效应的判断形式、余单子式 / 分级半环 |
| F-022 | 立场：reify 概念结构而非扩展静态标注 |
| F-023 | §3 导读：局部保证的边界与全局化路径 |

## §3.1 Revertible Effects

| 编号 | 一句话事实 |
|---|---|
| F-024 | 效应类型 `Γ → Γ × (Γ → Γ)` |
| F-025 | Definition 1 扭转组合与 `𝔗Γ` 幺半群 |
| F-026 | Definition 2 效应上下文 `∂Γ` 与累积器 |
| F-027 | Definition 3 `trackΓ` 公式 |
| F-028 | Theorem 5 `trackΓ` 为幺半群同态 |
| F-029 | Definition 6 `recoverΓ` 与 Theorem 7 不变式 |
| F-030 | 两点局限、Definition 8 `𝔈Γ` / `𝔈*Γ` 与见证条件 |
| F-031 | Definition 9 效应组合与 Theorem 10 幺半群 |
| F-032 | Theorem 15 / 16：提升不保见证、逆序回退恢复 |
| F-033 | Definition 17 效应迭代器 `ℑΓ` |

## §3.2 Reactive Coeffects / §3.3–3.4 上下文范式

| 编号 | 一句话事实 |
|---|---|
| F-034 | Definition 19 `Σ` 与类型族 |
| F-035 | Definition 20 `set(k,v) : 𝔈*Σ`，协同效应操作即效应 |
| F-036 | 满足谓词 `σ ⊧ d` 及其可判定性 |
| F-037 | Definition 21 规范、Definition 22 三分类通知 |
| F-038 | Definition 23 两种 realization |
| F-039 | Definition 24–25 隔离的两层解析 |
| F-040 | Definition 26–27 拦截与右偏元数据合并 |
| F-041 | Definition 28 统一上下文 `Γ∞` |
| F-042 | 观测等价 `≃S`、Definition 42 独立性两条件 |
| F-043 | Theorem 45 / Definition 46 / Theorem 47 |

## §4.1–4.2 组件、Fiber 与演算

| 编号 | 一句话事实 |
|---|---|
| F-044 | Definition 48 组件三元组 |
| F-045 | Definition 49 fiber 七元组与四状态 |
| F-046 | Definition 50 注册表与父指针树 |
| F-047 | §4.2 九条规则清单与 Figure 1 八条的原因 |
| F-048 | Definition 53 target view 记录提供者而非值 |
| F-049 | `L-Leave` / `L-Unload` 与 guard |
| F-050 | Definition 55 confinement |

## §4.3–4.4 元理论与扩展

| 编号 | 一句话事实 |
|---|---|
| F-051 | Definition 63 良构四条件与 Theorem 64 |
| F-052 | Theorem 68 与 Corollary 69 |
| F-053 | Theorem 70 与 Theorem 71 |
| F-054 | Definition 72 与 Theorem 73 |
| F-055 | Definition 74 support set 与 Definition 76 totality |
| F-056 | Theorem 80 汇流与「只谈状态」的限定 |
| F-057 | §4.4 四个扩展 |

## §5 实现与案例

| 编号 | 一句话事实 |
|---|---|
| F-058 | 三层架构与 Table 2 映射 |
| F-059 | `ctx.effect` 单一原语与 witness 不校验 |
| F-060 | Algorithm 1 guard / LIFO / armed |
| F-061 | 三个符号槽与 Algorithm 3 notify 判定 |
| F-062 | Algorithm 4 / 5 实例化、惯性状态机与三行 ordering |
| F-063 | Algorithm 6 Proxy 解析与两类访问错误 |
| F-064 | Definition 81 entry 六字段、字段分派、HMR 三阶段 |
| F-065 | Koishi 案例、v3/v4 脚注、Threats to validity |

## §6–§8 讨论、相关工作与结论

| 编号 | 一句话事实 |
|---|---|
| F-066 | 系统边界判据与 acquisition / emission 两阶段 |
| F-067 | capability 访问控制与沙箱边界 |
| F-068 | 依赖环静态可预测与细粒度分解的二次增长 |
| F-069 | 名义链接的两类问题与三条应对 |
| F-070 | 与 dagger / inverse arrows 的差异 |
| F-071 | 与 COP / AOP 的差异 |
| F-072 | 与 FRP 的差异及未来验证方向 |

---

## 事实采集边界

本清单覆盖论文的动机、形式化构造、演算、元定理、实现映射、案例与讨论。未纳入：二手解读文章中的 DeepSeek Harness 产品数据、第三方引文统计、以及本库既有包中的 Cordis 源码行号信息（后者见兄弟包 `cordis/`）。
