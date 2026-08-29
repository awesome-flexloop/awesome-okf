---
type: Reference
title: "信源登记（Source Registry）"
description: "mobilepa-bench 束信源登记：MobilePA-Bench 仓（README/LICENSE/站点文件/CI workflow/arXiv）与 Qwen-UI-Agent 网站仓（README/package.json/app 关键文件），逐项列相对路径与覆盖事实范围。"
tags: [MobilePA-Bench, Qwen-UI-Agent, 信源登记, 网站资产, arXiv]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
---

# 信源登记（Source Registry）

> **⚠️ 性质声明：两仓均为网站/论文资产，非实现代码仓**
>
> - **MobilePA-Bench**：仓库根经全量核查仅含 README/LICENSE/.gitignore/github-pages/ 纯静态站点与 .github/ CI 配置，"不存在任何基准任务数据、评测 harness、模型或智能体实现代码目录"，基准本体以 arXiv 论文（arXiv:2608.23035）形式发布（F-001）。README News 原文："2026-08-25: The project repository was opened with an interactive project page, leaderboard, and a private-evaluation link"（F-001）。
> - **Qwen-UI-Agent 网站仓**：README 顶部 IMPORTANT 块原文："**Website source only — this is not the Qwen-UI-Agent implementation repository.** ... It does **not** contain the model, training code, or agent implementation."；中文段："**本仓库仅为网站源码，并非 Qwen-UI-Agent 的项目实现代码仓。** ... 不包含模型、训练代码或智能体实现代码"（WEB-A-01）。实现代码指向官方仓库 **Tongyi-MAI/MAI-UI**："Looking for the Qwen-UI-Agent code? Visit the official project repository: **Tongyi-MAI/MAI-UI**"（WEB-A-02）。
>
> 因此本束不包含任何"运行评测"的操作指引；唯一的评测参与方式是私有评测通道的 endpoint 提交（F-008/F-009，见本束 `concepts/00-benchmark-overview.md`）。

---

## 信源根 1：MobilePA-Bench（本地镜像路径 `external/libs/tools/Tongyi-MAI/MobilePA-Bench`）

### 仓库内信源

| 信源文件 | 相对路径 | 覆盖事实 |
|---|---|---|
| README 主文档（99 行全文） | `README.md` | F-001~F-009、F-028、F-030 |
| 许可证 | `LICENSE` | F-030 |
| 项目页主文件（308 行全文） | `github-pages/index.html` | F-004、F-013~F-019、F-024、F-029、F-031 |
| 站点配置（评测入口注入） | `github-pages/static/js/site_config.js` | F-010 |
| 榜单数据（v1.5） | `github-pages/static/js/leaderboard_data.js` | F-011、F-012 |
| 案例数据（四维 × 3 案例） | `github-pages/static/js/case_studies_data.js` | F-020~F-022、F-032 |
| replay 演示数据 | `github-pages/static/js/replay_demo_data.js` | F-023 |
| 本地 vendor 依赖目录 | `github-pages/static/vendor/`（bulma/fontawesome/tabulator/jquery） | F-024 |
| leaderboard 截图脚本 | `.github/scripts/capture-leaderboard.mjs` | F-025 |
| Pages 部署 workflow | `.github/workflows/deploy-pages.yml` | F-026 |
| 预览更新 workflow（仅登记存在性） | `.github/workflows/update-leaderboard-preview.yml` | F-027 |

### 外部信源

| 信源 | URL | 覆盖事实 |
|---|---|---|
| arXiv 论文（基准本体） | https://arxiv.org/abs/2608.23035 | F-001、F-006、F-028 |
| 私有评测入口（secure submission portal） | https://116.62.42.171/login?next=/submit | F-008、F-010 |
| 页面模板致谢对象（Video-MME） | https://video-mme.github.io | F-029 |

> 说明：项目页经 GitHub Pages 部署（`deploy-pages.yml` 直接上传 `github-pages/` 静态目录，无构建步骤，F-026）；R 阶段未登记独立的项目页公网 URL，本束不虚构，站点内容以仓库内 `github-pages/` 文件为准。

---

## 信源根 2：Qwen-UI-Agent 网站仓（本地镜像路径 `external/libs/tools/Tongyi-MAI/Qwen-UI-Agent`）

### 仓库内信源

| 信源文件 | 相对路径 | 覆盖事实 |
|---|---|---|
| README | `README.md` | WEB-A-01~03、WEB-A-10、WEB-A-13、WEB-A-21~24 |
| 包清单与脚本 | `package.json` | WEB-A-04~06、WEB-A-20 |
| 静态导出配置 | `next.config.ts` | WEB-A-07 |
| 站点路径工具 | `app/sitePath.ts` | WEB-A-08 |
| 根布局（metadata） | `app/layout.tsx` | WEB-A-09 |
| 首页入口 | `app/page.tsx` | WEB-A-10 |
| 站点内容数据（1700+ 行） | `app/siteContent.ts` | WEB-A-11~15、WEB-A-21~23 |
| 真机基准子页 | `app/mobileworld-real/page.tsx`、`app/components/MobileWorldRealPage.tsx` | WEB-A-16 |
| 数据库 schema（故意留空） | `db/schema.ts` | WEB-A-17 |
| drizzle 配置 | `drizzle.config.ts` | WEB-A-18 |
| Vite 收尾插件 | `build/sites-vite-plugin.ts` | WEB-A-06 |
| Pages 部署 workflow | `.github/workflows/deploy-pages.yml` | WEB-A-19 |
| 测试与自检脚本 | `tests/rendered-html.test.mjs`、`scripts/validate-pages-prefix.mjs`、`scripts/export-self-contained.mjs` | WEB-A-20 |

### 外部信源

| 信源 | URL | 覆盖事实 |
|---|---|---|
| Qwen-UI-Agent 技术报告网站 | https://tongyi-mai.github.io/Qwen-UI-Agent/ | WEB-A-02、WEB-A-08 |
| 官方实现代码仓（非本束信源，仅指向） | https://github.com/Tongyi-MAI/MAI-UI | WEB-A-02 |

---

## 未覆盖项（按 R 阶段任务指示跳过，仅登记存在性或不引用）

| 类别 | 说明 |
|---|---|
| 图片/视频二进制、vendor 压缩库 | MobilePA-Bench 仓内媒体与压缩库未逐字节读取（F-024 仅登记目录清单） |
| `update-leaderboard-preview.yml` 细节 | 仅登记文件存在性（F-027） |
| LICENSE 正文 | 仅登记许可证类型结论（F-030，README 声明 + 文件存在性） |
| Qwen-UI-Agent 仓 `public/` 图片、`drizzle/` 迁移目录、`examples/d1/` 细节、`app/components/*.tsx` 正文 | R 阶段未读取；站点内容以 `siteContent.ts` 数据结构为准（WEB-A-10、WEB-A-17） |
| facts-websites.md B 部分（MAI-UI-blog，F-025~F-040） | 属 mai-ui 束登记范围，本束不引用；两篇 Notion 博客为重定向 stub，正文一律不引用 |
