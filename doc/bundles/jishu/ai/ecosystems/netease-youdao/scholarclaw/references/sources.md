---
type: reference
title: ScholarClaw 信源登记
tags: [scholarclaw, academic-search, skill, sources]
sources:
  - id: scholarclaw-upstream
    resource: git@github.com:netease-youdao/ScholarClaw.git
    title: ScholarClaw 上游仓库（GitHub）
  - id: scholarclaw-vendor
    resource: vendor/netease-youdao/ScholarClaw/
    title: ScholarClaw 源码（vendor 子模块）
---

# ScholarClaw 信源登记

> 本知识束全部事实（F-sc-001~F-sc-064）均派生自下述信源，信源为公开开源仓库，内容为公开级别。

## 上游与基线

| 项目 | 值 |
|------|-----|
| 上游仓库 | `git@github.com:netease-youdao/ScholarClaw.git` |
| 固定基线 commit | `97bdb5e4a763d4f98d4603f5be876587c0871e0f` |
| 基线最后提交 | 2026-04-03 18:43:02 +0800，"update: 更新微信群二维码图片" |
| 本地路径 | `vendor/netease-youdao/ScholarClaw/`（git submodule，只读引用） |
| 许可证 | MIT（`LICENSE.txt`，Copyright (c) 2024 ScholarClaw） |
| 版本 | 1.4.1（`package.json` 与 `SKILL.md` frontmatter 一致） |

基线 commit 经 `git rev-parse HEAD` 在 vendor 子模块内实测核验（2026-09-09）。

## 关键信源文件清单

| 文件（相对 vendor 子模块根） | 角色 | 支撑事实 |
|------------------------------|------|---------|
| `SKILL.md` | LLM 技能契约：触发条件、SSE 事件、博客三步法、重试策略、依赖声明 | F-sc-043~F-sc-051 |
| `server/config.ts` | 配置接口、合并链、校验、搜索引擎/模式/状态常量 | F-sc-001~F-sc-007 |
| `server/index.ts` | `ScholarClawClient` 及全部 HTTP 路由方法、错误判定 | F-sc-008~F-sc-020 |
| `server/types.ts` | 分页/搜索/学术/引用/OpenAlex/博客/基准/推荐类型族 | F-sc-021~F-sc-028 |
| `scripts/common.sh` | 公共库：配置初始化、取值优先级、curl 统一模式、jq 美化 | F-sc-030 |
| `scripts/search.sh` | 通用搜索脚本（自实现 URL 编码） | F-sc-031 |
| `scripts/scholar.sh` | 学术搜索/查询分析脚本（`--max-time 60`） | F-sc-032 |
| `scripts/citations.sh`、`scripts/citations_stats.sh` | 引用列表与引用统计脚本 | F-sc-033 |
| `scripts/openalex_cited.sh`、`scripts/openalex_find.sh` | OpenAlex 两路由脚本（`jq -sRr @uri` 编码） | F-sc-034 |
| `scripts/blog_submit.sh` | 博客提交（multipart `-F` 表单） | F-sc-035 |
| `scripts/blog_status.sh`、`scripts/blog_result.sh` | 博客任务状态与结果查询 | F-sc-036 |
| `scripts/blog.sh` | 博客同步封装（提交→轮询→取结果；5s×600s） | F-sc-037 |
| `scripts/benchmark_chat.sh` | 基准对话脚本（SSE 模式分支、`-s` 参数） | F-sc-038 |
| `scripts/recommend_papers.sh`、`scripts/recommend_blogs.sh`、`scripts/paper_repos.sh` | 推荐三路由脚本 | F-sc-039 |
| `scripts/health.sh` | 健康检查脚本（`--max-time 10`，`-v` 详细模式） | F-sc-040 |
| `package.sh` | 打包脚本（dist/ + tar.gz/zip + sha256） | F-sc-041 |
| `install.sh` | 安装脚本（`~/.scholarclaw`、`sc-*` 别名） | F-sc-042、F-sc-064 |
| `package.json` | 版本/engines/空依赖/npm scripts 别名/`lobsterai` 元数据 | F-sc-057~F-sc-059 |
| `tsconfig.json` | TS 编译配置（target ES2020、strict、outDir dist） | F-sc-060 |
| `README.md` | 功能介绍、引擎表、API 参考表、环境变量表 | F-sc-061、F-sc-062 |
| `examples/basic-search.md`、`examples/scholar-search.md` | 通用搜索与学术搜索调用示例 | F-sc-053、F-sc-054 |
| `examples/sota-chat.md`、`examples/blog-generation.md` | SSE 对话与博客异步流程示例 | F-sc-055、F-sc-056 |
| `LICENSE.txt` | MIT 许可证 | 本文件许可证项 |
