---
okf_version: "0.2"
---

# rust-lang/rfcs 知识库：Rust 变更提案的流程、演进与治理

本知识包是 [rust-lang/rfcs](https://github.com/rust-lang/rfcs)（Rust 语言变更提案仓库）的系统化中文教程，基于 **master @ 354518a8c9025f40be6f730452c1bfe71a12dc22**（2026-08-15 基线）的深度阅读生成。仓库 `text/` 目录现存 639 个 RFC 文件（递归 648 个，含 3 个多章节子目录），编号横跨 0001~3984；其中 26 篇被精读（每篇 3~6 条事实）、7 篇抽样浏览，共提取 177 条可验证事实（F-rfcs-001~177）。

本知识包的核心透镜是**「RFC 编号 = PR 编号」机制**：仓库没有独立编号机构，提交时不预先分配编号，PR 被接受时文件以 PR 编号重命名（F-rfcs-006）——639 个文件对 3984 个编号位，约 84% 的空洞本身就是提案存活率的化石记录。所有内容遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)，事实编号（F-rfcs-xxx）可逐条溯源至 [信源登记簿](/references/rfcs-source-map.md)。

## 流程与治理（concepts/）

* [RFC 流程与模板](/concepts/00-rfc-process-and-template.md) — 提交流程、编号即 PR 编号、FCP 机制、9 章双解释文体、目录统计与头部格式演变。
* [RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) — active 只是入场券、修正案规则、postponed 重开、lang/compiler/libs 三团队分流准则、关键字保留、库团队重组。

## 语言演进主题家族（concepts/）

* [语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) — 闭包与 Fn trait 统一（0114）、if let（0160）、while let（0214）、let-else（3137）与链式 if let（2497 抽样）。
* [类型系统演进](/concepts/02-type-system-evolution.md) — trait 系统清理（0048）、UFCS（0132）、where 子句（0135）、coercions（0401）、const fn（0911）、union（1444）、ADT 种类（1506）、复合赋值（0953）、impl Trait 与 tagged unions（抽样）。
* [错误处理与安全演进](/concepts/03-error-safety-evolution.md) — panic 术语三分（0221）、Try trait（1859）、try 关键字（2388）、I/O 安全（3128）、debug_assert（0050）、? 与 catch 的起源（0243 抽样）。
* [异步与借用：NLL、Pin 与 futures](/concepts/04-async-and-borrowing.md) — 非词法生命周期（2094）、Pin/Unpin（2349）、futures API 稳定化（2592）、async/await（2394 抽样）。

## 架构与生态（concepts/）

* [编译器架构演进：HIR、MIR 与 dyno](/concepts/05-compiler-arch-evolution.md) — HIR 引入（1191）、MIR 中层表示（1211）、基于类型的数据访问（3192）与「先批准后部分拒绝」案例。
* [标准库与生态演进](/concepts/06-std-ecosystem-evolution.md) — Edition 机制（2052）、std::fs 扩展与 std::os 平台层级愿景（1044）。

## 信源登记簿（references/）

* [rust-lang/rfcs 信源登记](/references/rfcs-source-map.md) — 基线 commit、仓库根文件清单、text/ 目录统计、RFC Book 构建工具链（generate-book.py/book.toml/部署流程）、26 篇精读与 7 篇抽样 RFC 清单。

## 信任与生命周期说明

* **status 判定依据**：全部 9 个内容文档（8 个概念 + 1 个信源登记）均 `status: stable`。内容基于 rust-lang/rfcs 仓库（`external/libs/rust-lang/rfcs/` 目录，只读）的 177 条编号事实（F-rfcs-001~177，覆盖三段：流程与模板 33 条、精读 RFC 106 条、目录统计与抽样 13 条），经 source-code-to-okf-wiki 五阶段流程（R→I→E→V→C）生成；每篇文档行文中的事实编号可逐条对回事实清单。
* **stale_after 解释**：统一设置为 `2027-08-28`。RFC 仓库是持续合并的历史档案（最新 RFC 3984 为 2026-07-15），存量 RFC 的内容不会漂移；该日期作为对新增 RFC、流程修订（如 FCP 规则调整）与三团队准则变更的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-28）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-28），两者分离、可追溯。
* **精读样本说明**：26 篇精读 + 7 篇抽样覆盖 2014-03~2026-07 的提案谱系；行文中引用的全部 RFC 编号、元数据与章节结构均来自事实清单登记内容，未采信清单之外的材料。

本知识包共收录 9 个内容文档（8 个概念 + 1 个信源登记），另含 2 个子目录 index.md 与根 index.md、log.md；按规划省略 examples/ 目录。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
