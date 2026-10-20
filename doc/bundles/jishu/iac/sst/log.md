# SST Bundle 变更日志

## 2026-10-20 — 归档覆盖度矩阵到 references

- **变更**：把任务过程件 `coverage-matrix.md`（需求—事实—覆盖度矩阵）从 spec 规划目录移入本束 `references/`，并在 `references/index.md` 登记与补 toctree 条目。
- **原因**：spec 目录只保留过程件（spec/tasks/review/facts/insights），覆盖度矩阵属交付侧证据，归档到对应知识包才是它的自然归属；同时避免给 spec 目录白名单检查新增一条违规。

## 2026-10-20 — 初始版本（R→I→E→V→C）

- **源码基线**：SST `v4.17.2`，commit `e49ac31411f63ab4ed0d802b7e15d95f6b827e47`；正文源码链接均指向固定提交。
- **官网采集**：2026-10-20 查阅并登记 Basics、Components、Providers、Linking、CLI、SDK、Live、Console、State 页面；官网陈述以 W 编号标识，不与固定版本实现事实混用。
- **R 阶段**：登记 F-001–F-034 源码事实和 W-001–W-015 官网事实；事实清单不包含未核实的源码数量断言。
- **I 阶段**：形成五条架构洞察与教程知识地图，指导产品模型、CLI、组件、runtime、Link 与开发体验的阅读顺序。
- **E 阶段**：先登记源码与官网 references；分两批生成 7 篇 concepts 与 3 篇 examples；随后创建各级索引、日志和验证记录。所有示例均明确未进行真实云部署。
- **V 阶段**：固定 commit 的 Link 示例 API 已由 `git show` / `git grep` 独立复核；18 篇 Markdown 的元数据与 74 个本地链接通过检查；SST bundle 与父级 toctree、UTF-8、实时目录计数及 `py314 -m invoke gates.all` 全部通过。最终完整 HTML 构建退出码为 0，Sphinx 报告 268 条全库 warning；日志中未发现 SST 文档告警，定向严格构建的告警来自其他 bundle，具体边界见 `verification.md`。
- **计数说明**：实时索引对账为 9 域 / 63 组 / 654 束，`jishu` 为 484 束 / 19 组。相较规格初始预期多 2 束，来自 OpenCode/OpenTUI 并行工作；索引与实时目录树一致，本任务未修改并行 bundle。
- **C 阶段**：R→I→E→V→C 闭环完成；未执行真实云部署，未创建 Git commit。
