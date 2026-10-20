# SST Bundle 变更日志

## 2026-10-20 — 初始版本（R→I→E→V→C）

- **源码基线**：SST `v4.17.2`，commit `e49ac31411f63ab4ed0d802b7e15d95f6b827e47`；正文源码链接均指向固定提交。
- **官网采集**：2026-10-20 查阅并登记 Basics、Components、Providers、Linking、CLI、SDK、Live、Console、State 页面；官网陈述以 W 编号标识，不与固定版本实现事实混用。
- **R 阶段**：登记 F-001–F-034 源码事实和 W-001–W-015 官网事实；事实清单不包含未核实的源码数量断言。
- **I 阶段**：形成五条架构洞察与教程知识地图，指导产品模型、CLI、组件、runtime、Link 与开发体验的阅读顺序。
- **E 阶段**：先登记源码与官网 references；分两批生成 7 篇 concepts 与 3 篇 examples；随后创建各级索引、日志和验证记录。所有示例均明确未进行真实云部署。
- **V 阶段进度**：固定 commit 的 Link 示例 API 已由 `git show` 独立复核；正文 frontmatter 与 bundle 内链接预检通过。项目 toctree、目录计数、全量 gates 与构建结果待最终回填到 `verification.md`。
- **C 阶段**：待 V 阶段质量门完成后关闭本次交付；按批准范围不创建 Git commit。
