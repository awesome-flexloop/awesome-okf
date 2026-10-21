# 变更日志（u2flash-free-month）

> 本文件只追加，不重写。计数遵循"读取现值 → 修改 → 复核"，不使用历史记忆值。

## 2026-10-21 · 建束（资讯速报，9 文件）

**背景**：用户提供云知声用户社群"U2Flash 免费月"群公告（含官方模型页、WorkBuddy 接入教程、问卷、飞书《问题Q&A》四链接），按 blog-article-to-okf-wiki 七阶段工作流（R→I→E→V，七概念元编排）转 OKF 知识包。

**阶段记录**：

- **阶段 0 预检**：公开内容（无访问控制参数），走标准工作流；spec 落主仓 `.trae/specs/okf-wiki-ecosystem/u2flash-free-month-okf-wiki/`，束落 `jishu/ai/practice/`（归属论证见 spec.md §3；强先例 deepseek-v41-flash-1017，不新建厂商分组）。
- **R 事实采集**：30 条 F 编号（F-001～F-030 连续）。S2/S3/S5 WebFetch 取证、S4 lark-cli 读取（rev.490）、S1 公告原文用户提供。P0 共 18 项：官方直证 13、官方 Q&A 单源 5、厂商自述 2、口径矛盾 1（计数有交叉，详见 verification.md §一）。
- **I 骨架判定**：操作可复现性两问——Q1 是（有配置/调用步骤）、Q2 否（官方文档+社群 Q&A 汇编，非作者实测）→ **不设 examples/**，操作内容入 concept 01。三层：事件事实 / 操作排障 / 机制趋势。
- **E 生成**：信源先行（article-source → verification），后 3 篇 concepts，各级 index 最后写；共 9 个文件。
- **V 审查**：3 条勘误（E-1 无限量 vs RPM/TPM；E-2 Base URL 两口径并存；E-3 公告错字"在得→再得"）；四视角 10 条意见，9 条落实、1 条留存（Anthropic 端点配置字段官方无示例，不臆造）。状态 `stable`（核心声明全部官方页核验为真，非核心赠品承诺以 ⚠️ 披露），`stale_after: 2026-11-15`。

**索引计数（读现值 → +1）**：practice 23 束/21 目录 → 24 束/22 目录；ai 256 → 257；bundles 总 657 → 658（jishu 487 → 488；组数 63、域数 9 不变）。

**机械门禁结果（2026-10-21 实跑）**：

- `scripts/check-utf8.py` ✅ 通过（12008 文件）。
- `scripts/check-bundles-index.py` ✅ 对账通过：9 域 / 63 组 / **658 束**，五面一致。
- `scripts/check-toctrees.py` ⚠️ 报 19 处不可达，**全部位于 `jishu/ai/products/vibeknow-cli/`（缺失 index.md）**——经 `git status` 核实为并行会话未跟踪（`??`）的在途工作区，与本次改动无关，本束 toctree 零问题，不顺手修改、不纳入本次提交。
- 手动等效项 ✅：双份 F 编号正则比对（30=30，集合相等、F-001～F-030 连续）；34 条相对链接 Test-Path 全可达（修复了 01 篇跨束链接少一级 `../` 的问题）；无真实 `file:///` 链接、无家目录路径；9 文件 frontmatter 必填字段齐备。

**产出文件（9）**：

```
u2flash-free-month/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-free-month-event.md
│   ├── 01-access-and-troubleshooting.md
│   └── 02-token-economics-and-funnel.md
└── references/
    ├── index.md
    ├── article-source.md
    └── verification.md
```

**复核要点（2026-11 月）**：① 11.1 后实际恢复价/限流与页面划线原价是否一致；② 5 亿 token 是否按问卷手机号到账、范围是否确限 U2-Flash；③ Q&A rev 增长后八问口径是否变化；④ WorkBuddy 是否开放 Anthropic 端点配置示例（V6 留存项）。
