# 变更日志

## 2026-11-17

- 依据 claude.dev 官方博文《How the Claude Code team thinks about verification》（2026-11-16，Addy Osmani）生成知识包，落在 `jishu/ai/practice/claude-code-verification/`。
- 采用七概念 **R→I→E→A→V** 链路：R 采集 71 条事实（F-001 至 F-071）→ I 按「现象/根因/影响/建议」拆层 → E 萃取 6 个可迁移模式 → A 原子化为 6 篇概念页 + 2 篇实践 + 2 篇信源页 → V 四视角对抗审查。C 阶段以「产出可独立验证的文件束」落地，未改动 git 历史。
- 转化路线显式登记 `route: chaptered-summary`：深度摘要加原创改写，非逐字转录；正文按「为什么验证 → 用什么测 → 怎么落地 → 怎么管住验证器」重组。
- 原站正文为动态渲染，首轮抓取仅返回头部与部分段落；缺失段落由全文转载镜像补齐，与原站重叠段落逐段比对一致（E-0）。
- 回 code.claude.com 三页官方文档交叉核验，登记四处口径差异：`REVIEW.md` 的分支保护前提（E-1）、`/goal` 评估器不独立执行命令（E-2）、Code Review 服务与本地 `/code-review` 读不同文件（E-3）、内部数字与阈值均为团队自述（E-4）。
- 两篇 `examples/` 为可照做配方并各带验收清单，本库环境未执行，正文与核验报告均标注「非实测通过」。
- 事实登记三处对账：`F-001` 至 `F-071` 共 71 条，区间上界 ↔ 统计表 ↔ 交叉引用一致、连续无跳号。
- 索引接入：`practice/index.md` 增至 33 束 / 31 目录，`jishu/ai/index.md` 增至 306 束，`jishu/index.md` 与 `doc/bundles/index.md` 增至 545 束 / 742 束；`doc/index.md`、`README.md` 规模数字同步。
- 机械门禁（动笔前先测基线以区分存量）：`check-bundles-index` 通过（9 域 / 65 组 / 746 束，五面一致）、`check-utf8` 通过（13473 文件）、`check-toctrees` 全量与本束限定均通过、`check-section-anchors` 本束限定通过（15 文件零断链）、父仓 `check-line-form` 通过。
- `check-asset-baseline` 在提交前判为红：残差由 +45634 增至 +457195，增量即工作区在途内容字节（本束 69002 字节 + 并发会话新增束）。该门按项目纪律须在提交后复跑自证；本束 15 个文件经字节级确认全为 LF、无 BOM。
- 自查：70 条相对链接零断链；11 个内容页 frontmatter 齐备；概念/示例页字符数均在 500–5000；事实台账 71 条连续、引用无越界。
- 并发说明：执行期间另一会话在同一区域新增 4 束，共享计数台账按目录树瞬时真值同步（746 束）；未提交、未改动他方暂存区。
