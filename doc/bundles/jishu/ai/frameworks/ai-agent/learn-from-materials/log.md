# 变更日志

## 2026-11-04 — 初始生成（v1）

- 来源博文：《一个神级学习 Skill，开源了！》（GitHubDaily，2026-11-03）
- 按 blog-article-to-okf-bundle 模式 L2 生成（**工具教程完整骨架，含 examples/**）
- R 阶段：41 条事实登记（F-001~F-041）；10 项 P0 核验（9 项 ✅ 通过 + 1 项 ⚠️ 口径差异）；4 项单源/一手实测登记
- I 阶段：4 concepts（项目概览 / 材料→学习网页机制 / 两种深度与方法论库 / 宿主集成与边界）+ 2 examples（安装与三步实操 / 产出与分享）
- E 阶段：生成 13 文件
  - index.md
  - concepts/index.md + 00-project-overview + 01-material-to-learning-page + 02-two-depths-and-methodology + 03-host-integration-and-boundaries
  - examples/index.md + 00-install-and-three-steps + 01-output-and-sharing
  - references/index.md + article-source + verification
  - log.md
- 索引登记：⏸️ **延后**（共享索引被并发的在途会话占用，为避免回滚其未提交变更，本次仅交付包体）。待处理目标值以 HEAD `3a6b6280` 干净基线为准——目录树 704 束 + 本包 1 = **705**；`ai-agent` 59→60、`frameworks` 92→93、ai 域 280→281、`jishu` 514→515；并需在 `ai-agent/index.md` toctree 追加 `learn-from-materials/index`
- status: verified；stale_after: 2027-02-03

### 关键核验结论

- ✅ 仓库 dmoshehun-prog/learn-from-materials 真实存在（id 1361079582、public、非 fork、MIT、Python）
- ✅ 版本 1.1.0、基于开放 Agent Skills 规范、支持 10+ 材料格式（宽于原文列举）
- ✅ 宿主清单与四行用户级安装目录表 README EN/CN 双份一致
- ✅ 两种深度、六板块、三主题、命令行链均与官方 README 一致
- ⚠️ 宿主口径差异：文章称「豆包工作」，官方宿主清单未列；豆包工作确有官方技能安装机制——双源并列，不判定源文有误
- ⚠️ 4 项单源/一手实测（豆包工作界面路径、54 页样本、内置浏览器预览、分享链接）已逐一登记

### 已知边界

- 官方 README 未描述豆包工作内的预览与分享入口（F-026/F-027 为原文单源）
- 仓库不含原始材料与完整生成结果，showcase 截图为设计展示而非验收报告
- 扫描 PDF 与图片型幻灯片依赖 OCR/视觉能力，缺失时对应范围标记为未核验
