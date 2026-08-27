---
type: Reference
title: Trae Skills 源码信源
description: trae-skills 项目中 12 个技能目录、脚本文件与 CI 工作流的完整索引与源码路径映射。
tags: [trae-skills, reference, source, skills-index]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: facts
    title: trae-skills 源码事实清单
  - id: insights
    title: trae-skills 核心洞察与知识地图
---

## 项目概况

trae-skills 是 TRAE IDE 的社区维护 Agent Skills 集合，采用 MIT 许可证。项目位于社区仓库 `trae-community/trae-skills/`，包含 12 个技能目录、多个 Python/JS 辅助脚本以及一套自动化社区积分 GitHub Actions 工作流。

- 项目级安装路径：`.trae/skills/<skill-name>/SKILL.md`
- 全局级安装路径：`~/.trae/skills/<skill-name>/SKILL.md`

## 技能目录索引（12 个）

所有技能文件统一存放在 `skills/` 目录下，每个技能为一个独立子目录。

| # | 技能名称 (name) | 目录路径 | 类型模式 | 核心功能 |
|---|----------------|----------|----------|----------|
| 1 | `_template` | `skills/_template/` | 模板 | 技能编写模板，定义标准 SKILL.md 结构 |
| 2 | `cloudbase` | `skills/cloudbase/` | 纯 Prompt 型 | 腾讯云开发（TCB）应用构建/部署/调试，集成 CloudBase MCP |
| 3 | `cn-punctuation-checker` | `skills/cn-punctuation-checker/` | 纯 Prompt 型 | 中文文本中英文标点错误检测与批量修复 |
| 4 | `daily-hot-news` | `skills/daily-hot-news/` | 脚本辅助型 | 多平台热榜聚合（微博/百度/知乎/头条/B站/抖音），Python 脚本抓取 |
| 5 | `daily-trend-writer` | `skills/daily-trend-writer/` | Workflow 编排型 | 全自动公众号内容生产流水线，6 Phase 工作流 + subskills |
| 6 | `git-commit-generator` | `skills/git-commit-generator/` | 纯 Prompt 型 | 基于 git diff 生成 Conventional Commits 规范提交信息 |
| 7 | `kz-article-deep-analysis` | `skills/kz-article-deep-analysis/` | Workflow 编排型 | 非学术类文章深度解读，结构化分析报告生成（K叔，v1.0.3） |
| 8 | `trae-claw-install` | `skills/trae-claw-install/` | Workflow 编排型 | OpenClaw 仓库驱动部署工作流，跨平台路由（Windows/macOS/Linux） |
| 9 | `video-to-keyframes` | `skills/video-to-keyframes/` | 脚本辅助型 | 视频抽帧→转场检测→关键帧选择→HTML 画廊，4 个 Python 脚本流水线 |
| 10 | `web-design-teroop` | `skills/web-design-teroop/` | 纯 Prompt 型 | 首席设计架构师角色，创建/维护 .design-spec.md 设计规范文档 |
| 11 | `wechat-mini-program-development` | `skills/wechat-mini-program-development/` | 纯 Prompt 型 | 微信小程序标准项目结构搭建、请求封装、API 端点管理 |
| 12 | `zopia-api` | `skills/zopia_ai_skills/` | 脚本辅助型 | Zopia AI 视频制作 API 集成，项目创建/风格配置/Agent 对话/状态查询 |

## 技能子目录资源结构

每个技能目录可包含以下可选子目录：

| 子目录 | 用途 | 典型文件 |
|--------|------|----------|
| `examples/` | 输入输出示例 | `input.md`、`output.md` |
| `templates/` | 可复用模板文件 | `commit-message.txt`、`topic-brief.md`、`trend-board.md` |
| `resources/` | 参考文件、脚本、资源 | `scripts/fetch_news.py`、`conventional-commits-types.md`、`trend-sources.md` |
| `subskills/` | 子技能指令文件（Workflow 型） | `doc-coauthoring.md`、`mimeng-writing.md`、`wechat-article-writer.md` |
| `assets/` | 报告模板等资产 | `template.md` |
| `references/` | 方法论参考 | `methodology.md` |
| `scripts/` | 验证脚本等 | `verify.py` |

## Python 脚本索引

### daily-hot-news 脚本

| 脚本路径 | 功能 | 依赖 |
|----------|------|------|
| `skills/daily-hot-news/resources/scripts/fetch_news.py` | 多平台热榜数据抓取，4 层数据源降级（韩小韩→60s→小众独行→自建 DailyHotApi） | Python 标准库（无额外依赖） |
| `skills/daily-hot-news/resources/scripts/generate_report.py` | 将 fetch_news.py 的 JSON 输出转为 markdown/text/html 格式报告 | Python 标准库 |

fetch_news.py 命令行参数：
- `--platforms`：逗号分隔平台列表（weibo/baidu/zhihu/toutiao/bilibili/douyin），默认全部
- `--top`：每平台条目数，默认 10
- `--format`：输出格式 json/markdown，默认 json
- `--output`：输出文件路径，默认 stdout

generate_report.py 命令行参数：
- `--data`：JSON 数据文件路径（`-` 表示 stdin，必填）
- `--format`：输出格式 markdown/text/html，默认 markdown
- `--output`：输出文件路径

### kz-article-deep-analysis 脚本

| 脚本路径 | 功能 | 依赖 |
|----------|------|------|
| `skills/kz-article-deep-analysis/scripts/verify.py` | 技能结构验证（frontmatter/工作流章节/版本历史/参考文件检查） | Python 标准库 |

verify.py 检查项：
1. SKILL.md 是否存在
2. SKILL.md 是否包含 YAML frontmatter
3. frontmatter 是否包含 name/description/version
4. 是否包含 `## @工作流:` 章节
5. 是否包含 `## 版本历史` 章节
6. references/methodology.md 是否存在
7. assets/template.md 是否存在

命令行参数：`--skill <技能文件夹路径>`，返回 0 表示通过、1 表示失败。

### video-to-keyframes 脚本

| 脚本路径 | 功能 | 依赖 |
|----------|------|------|
| `skills/video-to-keyframes/resources/scripts/generate_daily_folder.py` | 生成以当前日期命名的文件夹 | Python 标准库 |
| `skills/video-to-keyframes/resources/scripts/extract_frames_and_describe.py` | 视频抽帧，计算清晰度/亮度/对比度/饱和度/运动指标 | numpy, opencv-python |
| `skills/video-to-keyframes/resources/scripts/select_keyframes.py` | dHash 转场检测、分段、候选关键帧评分与画廊生成 | numpy, opencv-python |
| `skills/video-to-keyframes/resources/scripts/run_video_workflow.py` | 一键编排脚本，串联抽帧→选帧→汇总文件 | numpy, opencv-python |

select_keyframes.py 评分公式（`_score` 函数）：
- 清晰度（sharpness）：权重 0.45
- 亮度适中度：权重 0.25
- 对比度（contrast）：权重 0.15
- 饱和度（saturation）：权重 0.05
- 低运动（low motion）：权重 0.10

一键运行命令：
```bash
python .\skills\video-to-keyframes\resources\scripts\run_video_workflow.py "<视频路径>" --day-folder "<当天文件夹>" --every-seconds 0.5 --max-frames 600
```

## GitHub Actions CI 工作流

### 社区积分工作流

| 文件路径 | 功能 |
|----------|------|
| `.github/workflows/community-points.yml` | Community Points 自动化积分工作流 |
| `.github/scripts/update-community-points.js` | Node.js 积分更新脚本 |

工作流触发条件：
- `workflow_dispatch`：手动加分（支持 manual_user/manual_points/manual_reason/manual_event_key 参数）
- `pull_request closed`：PR 合并 +1 分；若 PR 描述引用 close/fix/resolve #issueNumber，关联 Issue 额外 +1 分
- `issues closed`：Issue 关闭 +1 分；通过 GraphQL 查询是否由合并的 PR 解决

工作流特性：
- 权限：contents: write、pull-requests: read、issues: read
- 并发控制：concurrency group `community-points`（cancel-in-progress: false）
- 运行环境：ubuntu-latest
- 积分数据存储：`community-points-data` 分支（独立于 main 分支）
- 幂等机制：通过 ledger 中的 eventKey 防止重复计分
- Bot 忽略：自动忽略 `github-actions[bot]`、dependabot[bot] 及所有 `[bot]` 结尾用户

### 社区积分数据文件

| 文件路径 | 用途 |
|----------|------|
| `community-points.json` | 积分数据文件，结构 `{"scores": {}, "ledger": {}}` |
| `community-leaderboard.md` | 自动生成的 Markdown 排行榜 |

eventKey 格式：
- 手动加分：`manual:{eventSuffix}:{user}`
- PR 合并：`pr:{prNumber}:merged`
- PR 解决 Issue：`issue:{issueNumber}:resolved-by-pr:{prNumber}`
- Issue 关闭：`issue:{issueNumber}:closed`

## 相关概念

- [SKILL.md 格式规范](../concepts/01-skill-format.md)
- [技能分类与模板模式](../concepts/02-skill-categories.md)
- [纯 Prompt 型技能](../concepts/03-prompt-only-skills.md)
- [脚本辅助型技能](../concepts/04-script-assisted-skills.md)
- [Workflow 编排型技能](../concepts/05-workflow-skills.md)
- [社区积分机制](../concepts/06-community-points.md)
- [编写自定义 Skill](../concepts/07-write-skill.md)

## 相关示例

- [创建第一个 Skill](../examples/create-first-skill.md)
- [带 Python 脚本的 Skill 示例](../examples/skill-with-python-script.md)
- [触发条件设计示例](../examples/trigger-condition-design.md)
- [社区积分贡献示例](../examples/points-contribution.md)
