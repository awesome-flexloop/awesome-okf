---
type: Reference
title: rust-lang/rfcs 信源登记
description: rust-lang/rfcs 仓库基线信息、text/ 目录统计、RFC Book 构建工具链、26 篇精读与 7 篇抽样 RFC 清单
tags: [rust, rfcs, source, reference, rfc-process, mdbook]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: rfcs-repo
    resource: external/libs/rust-lang/rfcs
    title: rust-lang/rfcs 仓库（master @ 354518a8）
---

# rust-lang/rfcs 信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | rust-lang/rfcs |
| 基线 | master @ 354518a8c9025f40be6f730452c1bfe71a12dc22 |
| 基线日期 | 2026-08-15 |
| 仓库定位 | Rust 语言变更提案（RFC）的正式存储库 |
| 官方书入口 | <https://rust-lang.github.io/rfcs/> |
| Active RFC 列表 | <https://rfcbot.rs/> |
| 源码位置 | `external/libs/rust-lang/rfcs/`（本地只读，禁止修改） |
| 仓库总文件数 | 665 个（排除 `.git/`，F-rfcs-169） |

## 仓库根目录结构

仓库根目录（不含 `.git/` 与 `.github/`）的文件清单（F-rfcs-169）：

| 文件 | 用途 |
|------|------|
| `README.md` | RFC 流程总说明：提交流程、FCP 机制、生命周期、三团队准则入口 |
| `0000-template.md` | RFC 写作模板：4 个元数据字段 + 9 章节结构 |
| `text/` | 全部 RFC 正文（本 bundle 的主信源目录） |
| `generate-book.py` | mdBook（Rust 官方文档生成器）构建脚本，生成 `src/` 与 `SUMMARY.md` |
| `book.toml` | mdBook 配置：书名 "The Rust RFC Book" 及输出选项 |
| `lang_changes.md` | 语言团队（T-lang）的 RFC 判定准则 |
| `compiler_changes.md` | 编译器团队（T-compiler）的 RFC/MCP 判定准则 |
| `libs_changes.md` | 库团队（T-libs）的 RFC 判定准则 |
| `LICENSE-APACHE` / `LICENSE-MIT` | 双许可证文件 |
| `.gitattributes` / `.gitignore` / `renovate.json5` | 版本控制与依赖自动化配置 |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR review 约定模板 |
| `.github/workflows/deploy.yml` | GitHub Pages 自动部署工作流 |

## text/ 目录统计

本 bundle 全部概念文档的事实来源（采集于 2026-08-28 实测，F-rfcs-165~168）：

| 统计项 | 值 |
|--------|-----|
| 顶层 `.md` 文件数 | 639 个（F-rfcs-165） |
| 递归 `.md` 文件数（含子目录） | 648 个（F-rfcs-165） |
| 多章节子目录 | 3 个：`2856-project-groups`、`3392-leadership-council`、`3606-temporary-lifetimes-in-tail-expressions`（F-rfcs-166） |
| 编号范围 | `0001-private-fields` ~ `3984-libs-team-refactor`（F-rfcs-167） |
| 命名模式 | 4 位零填充编号 + 连字符 + 小写 kebab-case 描述名（F-rfcs-168） |

RFC 编号即 PR 编号：提交时不预先分配编号，PR 合并（RFC 被接受）时文件以 PR 编号重命名（F-rfcs-006）。639 个文件对 0001~3984 的编号区间，意味着约 84% 的编号位置没有对应文件——每个空洞大致对应一个被关闭的 PR，编号空洞本身是提案存活率的化石记录。

## RFC Book 构建工具链

仓库通过以下工具链将 `text/` 目录发布为在线书籍 <https://rust-lang.github.io/rfcs/>：

### generate-book.py

基于文件系统布局自动生成 mdBook 的 `SUMMARY.md`，并基于 `text` 目录内容生成 `src` 目录（F-rfcs-018）。其文档化的多章节布局约定为：RFC 通常保持单章节文件；特殊情况下用同名子目录放置额外页面（如 `0123-my-awesome-feature.md` + `0123-my-awesome-feature/extra-material.md`），静态内容（图片等）建议同样布局，章节按排序顺序呈现（F-rfcs-019）。

执行逻辑（F-rfcs-020）：先删除并重建 `src` 目录（清除切换分支后的陈旧链接）；对 `text/` 下每个条目及 `compiler_changes.md`、`lang_changes.md`、`libs_changes.md`、`README.md`（符号链接名为 `introduction.md`）创建符号链接；写入 `src/SUMMARY.md`；最后调用 `mdbook build`。

`SUMMARY.md` 的生成结构（F-rfcs-021）：`[Introduction](introduction.md)` + 三行 guidelines 链接（compiler/language/library changes）+ `collect()` 递归收集 `text/` 下 `.md` 条目（链接路径去掉前 5 个字符 `text/` 前缀，条目名去 `.md` 后缀）。

### book.toml

书名 "The Rust RFC Book"；HTML 输出设置 `smart-punctuation = true`、`no-section-label = true`、`git-repository-url` 与 `site-url = "/rfcs/"`；搜索 `heading-split-level = 0`；playground `runnable = false`；构建 `extra-watch-dirs = ["text"]`（F-rfcs-022）。

### GitHub Pages 部署

`.github/workflows/deploy.yml`：push 到 master 分支触发；环境变量 `MDBOOK_VERSION` 为 0.5.4（由 renovate 管理）；流程为 checkout（fetch-depth: 0）→ 安装 mdbook → 运行 `./generate-book.py` → 上传 `./book` 产物 → 部署到 github-pages 环境（F-rfcs-023）。

### PR review 约定

由于 RFC 涉及大量并行的难以跟随的对话，PR 模板要求使用对文本变更的 review comment threads（可点 diff 右上 "Comment on this file"）而非对 RFC 的直接评论（F-rfcs-024）。

## 精读 RFC 清单（26 篇）

本 bundle 深度阅读（每篇 3~6 条事实）的 26 篇 RFC 及其在概念文档中的归属：

| RFC 文件 | Start Date | 主题 | 事实编号 | 归属概念文档 |
|----------|-----------|------|---------|------------|
| `text/0114-closures.md` | 2014-07-29 | 闭包与 Fn trait 统一 | F-rfcs-034~038 | [01 语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) |
| `text/3137-let-else.md` | 2021-05-31 | let-else 语句 | F-rfcs-039~043 | [01 语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) |
| `text/0160-if-let.md` | 2014-08-26 | if let 表达式 | F-rfcs-044~048 | [01 语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) |
| `text/0214-while-let.md` | 2014-08-27 | while let 循环 | F-rfcs-049~053 | [01 语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) |
| `text/0132-ufcs.md` | 2014-03-17 | 统一函数调用语法 | F-rfcs-054~058 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/0135-where.md` | 2014-09-30 | where 子句 | F-rfcs-059~063 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/0911-const-fn.md` | 2015-02-25 | const 函数 | F-rfcs-064~069 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/1444-union.md` | 2015-12-29 | union 类型 | F-rfcs-070~074 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/0401-coercions.md` | 2014-10-30 | 类型强制转换 | F-rfcs-075~079 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/0221-panic.md` | 2014-09-23 | panic 术语重命名 | F-rfcs-080~084 | [03 错误处理与安全演进](/concepts/03-error-safety-evolution.md) |
| `text/1859-try-trait.md` | 2017-01-19 | Try trait | F-rfcs-085~089 | [03 错误处理与安全演进](/concepts/03-error-safety-evolution.md) |
| `text/2388-try-expr.md` | 2018-04-04 | try 关键字与 try 表达式 | F-rfcs-090~095 | [03 错误处理与安全演进](/concepts/03-error-safety-evolution.md) |
| `text/3128-io-safety.md` | 2021-05-24 | I/O 安全 | F-rfcs-139~144 | [03 错误处理与安全演进](/concepts/03-error-safety-evolution.md) |
| `text/0050-assert.md` | 2014-04-18 | debug_assert 宏 | F-rfcs-158~161 | [03 错误处理与安全演进](/concepts/03-error-safety-evolution.md) |
| `text/2094-nll.md` | 2017-08-02 | 非词法生命周期 | F-rfcs-096~101 | [04 异步与借用](/concepts/04-async-and-borrowing.md) |
| `text/2349-pin.md` | 2018-02-19 | Pin 与 Unpin | F-rfcs-102~107 | [04 异步与借用](/concepts/04-async-and-borrowing.md) |
| `text/2592-futures.md` | 2018-11-09 | futures API 稳定化 | F-rfcs-108~112 | [04 异步与借用](/concepts/04-async-and-borrowing.md) |
| `text/1191-hir.md` | 2015-07-06 | 高层中间表示 HIR | F-rfcs-113~117 | [05 编译器架构演进](/concepts/05-compiler-arch-evolution.md) |
| `text/1211-mir.md` | 2015-07-14 | 中层中间表示 MIR | F-rfcs-118~123 | [05 编译器架构演进](/concepts/05-compiler-arch-evolution.md) |
| `text/3192-dyno.md` | 2021-11-04 | 基于类型的数据访问 | F-rfcs-124~128 | [05 编译器架构演进](/concepts/05-compiler-arch-evolution.md) |
| `text/2052-epochs.md` | 2017-06-26 | Rust Edition 机制 | F-rfcs-129~133 | [06 标准库与生态演进](/concepts/06-std-ecosystem-evolution.md) |
| `text/1044-io-fs-2.1.md` | 2015-04-04 | std::fs 扩展 | F-rfcs-134~138 | [06 标准库与生态演进](/concepts/06-std-ecosystem-evolution.md) |
| `text/1506-adt-kinds.md` | 2016-02-07 | ADT 种类模型 | F-rfcs-145~148 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/0953-op-assign.md` | 2015-03-08 | 复合赋值 trait | F-rfcs-149~153 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/0048-traits.md` | 2014-06-10 | trait 系统清理 | F-rfcs-154~157 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/0342-keywords.md` | 2014-10-07 | 保留关键字 | F-rfcs-162~164 | [07 RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) |

## 抽样 RFC 清单（7 篇）

未列入精读清单、仅记录标题要点与状态的 7 篇抽样 RFC（F-rfcs-171~177）：

| RFC 文件 | Start Date | 要点 | 事实编号 | 归属概念文档 |
|----------|-----------|------|---------|------------|
| `text/0002-rfc-process.md` | 2014-03-11 | RFC 流程本身的定义（流程源头 RFC） | F-rfcs-171 | [00 RFC 流程与模板](/concepts/00-rfc-process-and-template.md) |
| `text/0243-trait-based-exception-handling.md` | 2014-09-16 | `?` 操作符与 `catch` 表达式的起源 | F-rfcs-172 | [03 错误处理与安全演进](/concepts/03-error-safety-evolution.md) |
| `text/2394-async_await.md` | 2018-03-30 | async/await 语法（2592 的姊妹 RFC） | F-rfcs-173 | [04 异步与借用](/concepts/04-async-and-borrowing.md) |
| `text/3984-libs-team-refactor.md` | 2026-07-15 | 库团队重组（编号最大的 RFC） | F-rfcs-174 | [07 RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) |
| `text/1522-conservative-impl-trait.md` | 2016-01-31 | 保守形式 impl Trait | F-rfcs-175 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |
| `text/2497-if-let-chains.md` | 2018-07-13 | if let 链式写法 | F-rfcs-176 | [01 语言演进：表达式与模式](/concepts/01-lang-evolution-expr-pattern.md) |
| `text/2195-really-tagged-unions.md` | 2017-10-30 | enum 布局属性形式化 | F-rfcs-177 | [02 类型系统演进](/concepts/02-type-system-evolution.md) |

## 事实登记口径说明

本 bundle 的事实清单共 177 条（F-rfcs-001~177），分三段：

- **A 段（流程与模板，001~033）**：README 流程、模板结构、三团队准则——主覆盖分配给 [00 RFC 流程与模板](/concepts/00-rfc-process-and-template.md)（001~007、013~017）、[07 RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md)（008~012、025~033）与本登记页（018~024，book 构建工具链类事实）。
- **B 段（精读 RFC，034~164）**：26 篇 RFC 的逐篇事实——按语言特性家族分配到概念文档 01~07。
- **C 段（目录统计与抽样，165~177）**：目录统计主覆盖在 [00 RFC 流程与模板](/concepts/00-rfc-process-and-template.md)（165~170），抽样事实（171~177）按各自主题归入对应概念文档。

## 相关概念

- [RFC 流程与模板](/concepts/00-rfc-process-and-template.md) — 提交流程、编号机制、模板结构与目录统计的语义解读
- [RFC 生命周期与团队治理](/concepts/07-rfc-lifecycle-governance.md) — 三团队准则文件（lang/compiler/libs changes）的完整解读
- [类型系统演进](/concepts/02-type-system-evolution.md) — 精读数量最多的主题家族（九篇 RFC + 两篇抽样）
