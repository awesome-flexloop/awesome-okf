# 核验报告

> 核验日期：2026-11-04
> 核验方式：GitHub API 元数据 + 官方 README 双语双份比对 + WebSearch 交叉核验
> 核验人：OKF Wiki Bot

## 总结

| 项 | 结果 |
|----|------|
| P0 声明数 | 10 |
| ✅ 通过 | **9** |
| ⚠️ 口径差异 | 1（双源并列，不判定源文有误） |
| ❌ 失败 | 0 |
| 单源/一手实测登记 | 4（F-023/025/026/027） |

**结论**：博文涉及的开源仓库、版本、支持格式、宿主清单、运行要求均可由官方 README 与 GitHub API 交叉印证，未发现虚构。唯一需并列登记的是**宿主口径差异**（文章称「豆包工作」，官方 README 宿主清单未列）——经双源核验后判定为「口径差异」而非「源文错误」，详见第 8 项。

## 逐项核验

### 1. 仓库存在性与元数据 — ✅ 通过

- GitHub API `api.github.com/repos/dmoshehun-prog/learn-from-materials` 返回：`id 1361079582`、public、非 fork、`default_branch: main`
- `license.spdx_id = MIT`、`language: Python`、`created_at 2026-09-08T07:48:21Z`
- 核验时点 `stargazers_count 1280`、`forks_count 121`、`open_issues_count 0`（**时点快照，非稳定值**）

### 2. 版本号 1.1.0 — ✅ 通过

- README badge `version-1.1.0-blue` 与正文 `## 1.1.0` 章节一致
- 安装包名亦为 `learn-from-materials-1.1.0.zip`

### 3. 支持格式清单 — ✅ 通过（宽于原文）

- 原文列举 PDF、EPUB、Word、PPT；官方 README 覆盖 PDF、EPUB、MOBI/AZW/AZW3、DOCX、PPTX/PPTM、HTML、Markdown、TXT、RTF 与多材料集合
- README EN 与 README_CN 双份一致
- 判定：原文为列举式概述而非完整清单，属**不完整而非错误**

### 4. 宿主清单与用户级安装目录表 — ✅ 通过

- README EN/CN 双份一致列出：WorkBuddy、Codex、Claude Code、GitHub Copilot CLI
- 目录表逐行核实：`~/.workbuddy/skills/`、`~/.agents/skills/`、`~/.claude/skills/`、`~/.copilot/skills/`
- 仓库 topics 含 `workbuddy`，与官方宿主清单侧证一致

### 5. 两种深度 / 六板块 / 三主题 — ✅ 通过

- 两种深度：快速了解（Quick Overview）与系统学习（Systematic Study），README 含对照表
- 六板块：核心框架、内容导学、术语大全、行动规则、动态自检、本地笔记
- 三主题：海盐云纱（Sea Salt）、黑白水墨（Ink Wash）、竹月清（Bamboo Moon），动效可关闭
- README EN 用英文主题名、README_CN 用中文主题名，双份对应

### 6. 运行要求：Python 3.10+ 与 Node.js 可选 — ✅ 通过

- README badge `Python-3.10%2B` 与「运行要求与兼容边界」一致
- Node.js 明确仅用于可选 JavaScript 回归检查，非必需

### 7. 豆包工作具备技能安装机制 — ✅ 通过（独立佐证）

- 豆包工作官方文档《技能》页：技能页安装按钮、「我安装的」管理、「更多技能」入口，并注明"技能无需安装也可在任务中直接使用"
- 豆包开放平台《技能接入指南》：终端用户可在豆包工作客户端的「插件&技能&伙伴」页面查看并安装已上架技能
- 第三方实践记录：可在豆包工作中新建技能并粘贴 `SKILL.md`（BibiGPT 等案例）

### 8. ⚠️ 宿主口径差异（豆包工作 vs 官方宿主清单）— 双源并列登记

- **源文口径**：作者明确称"我把这个 Skill 装到「豆包工作」"，并给出豆包工作内的三步操作与逐字提示词
- **官方口径**：README 宿主清单仅列 WorkBuddy、Codex、Claude Code、GitHub Copilot CLI，未列豆包工作
- **交叉核验**：第三方来源一致证实二者为不同公司产品（WorkBuddy=腾讯，与 CodeBuddy 同属 Buddy AI 产品线；豆包工作=字节跳动）

**判定**：属**口径差异**，不判定源文有误。理由——豆包工作确有官方技能安装机制（见第 7 项），且本 Skill 基于开放 Agent Skills 规范、`SKILL.md` 为标准格式，理论上可被任何识别 `SKILL.md` 的宿主加载；官方 README 只是"已验证宿主清单"未覆盖豆包工作。两说并列登记，读者可自行判断。

### 9. 命令行工具链 — ✅ 通过

- README「命令行工具」全节列出 `extract.py`、`methods.py bind`、`methodology.py bind`、`prepare_quick.py`、`pipeline.py assemble`、`render_page.py`、`finalize.py`，均在 Skill 根目录运行

### 10. 官方示例与版权边界 — ✅ 通过

- README「效果展示」以三类材料（传记《埃隆·马斯克传》、J.P. Morgan《2026 年中展望》、论文《Attention Is All You Need》）演示同一六板块格式
- README 明示 16 张截图为设计展示、非浏览器验收报告；仓库不含原始材料与完整生成结果；随包 Method Lab 为自编合成示例（MIT）

## 单源/一手实测登记（不可独立复核）

| 编号 | 内容 | 性质 |
|------|------|------|
| F-023 | 豆包工作内新建任务、选本地文件夹、发一句话安装技能（含逐字提示词） | 作者一手操作描述，界面路径单源 |
| F-025 | 作者实测样本为一份 54 页生成式 AI 报告 | 作者一手实测，样本不可独立核验 |
| F-026 | HTML 文件可在豆包工作内置浏览器预览 | 单源（原文），官方 README 未描述此入口 |
| F-027 | 内置浏览器「分享」→「生成链接」得到可访问链接 | 单源（原文），属宿主产品能力 |

## 风险与建议

1. **时效性**：`stale_after` 设为 2027-02-03（Skill 与宿主生态迭代快，3 个月后复核版本号与宿主清单）
2. **宿主口径**：概念与实战文档均已并列登记"官方宿主清单"与"文章宿主"两种口径，不使用绝对化表述
3. **数据引用**：star/fork 为核验时点快照，不写入正文结论性表述
4. **扫描件边界**：扫描 PDF 与图片型幻灯片需 OCR/视觉能力，缺失时对应范围被标记为未核验，读者不应默认全部材料可解析
