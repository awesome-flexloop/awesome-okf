---
type: Concept
title: Demo Markdown 文档格式
description: trae-demos 中 Demo Markdown 文件的结构化字段设计、中英双语格式和 frontmatter 规范
tags: [demos, markdown-format, frontmatter, bilingual, trae-demos, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/demos-source.md
    title: "Trae Demos 源码信源"
---

# Demo Markdown 文档格式

每个 Demo 由一对中英双语 Markdown 文件组成（`demo-N.md` + `demo-N.zh-CN.md`），文件内容采用结构化字段设计，确保信息完整且格式统一。

## 文件头标注

每个 Demo 文件头部标注收录信息：

- 英文版：`Issue: #N | Month Year`（如 "Issue: #1 | March 2026"）
- 中文版：`收录于：第 N 期 | YYYY年M月`（如 "收录于：第 1 期 | 2026年3月"）

## 核心字段

基于已收录的两个 Demo（Minecraft Guilin City Walk 和 TraeClaw），Demo Markdown 包含以下结构化字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| 项目名称 | Demo 的标题，中英文各自语言 | "Minecraft Guilin City Walk \| 桂林像素漫步" |
| 作者（Author） | GitHub 用户名 | @MU-ty |
| 类型（Type） | 项目分类 | Web App / Plugin/Extension |
| 技术栈（Tech Stack） | 使用的技术 | JavaScript/TypeScript |
| GitHub 仓库 | 源码链接 | https://github.com/... |
| 在线演示（Demo） | 可访问的演示 URL | https://... 或标注无 |
| 核心亮点（Highlights） | 3-4 项核心特色 | 要点列表 |
| 本地运行/安装 | 运行或安装方式 | 命令行步骤或自然语言安装 |
| 预览图片 | 截图链接 | GitHub user-attachments 资源 |

## 中英双语格式

英文版和中文版分别维护独立文件，不是同一文件内双语混排：

- `demo-1.md`：全英文内容
- `demo-1.zh-CN.md`：全中文内容

两个文件结构完全对应，字段内容翻译为各自语言。

## Demo 展示案例对比

### Demo #1：传统 Web App 模式

Minecraft Guilin City Walk 代表典型的 Web 应用 Demo：
- **运行方式**：传统命令行（`git clone` → `npm install` → `npm run dev`）
- **在线演示**：有 GitHub Pages 部署
- **预览图片**：使用 GitHub user-attachments 链接（2 张截图）
- **亮点数量**：4 项核心亮点

### Demo #2：AI 代理安装模式

TraeClaw 代表创新的插件类 Demo：
- **安装方式**：非传统命令行，向 OpenClaw 发送自然语言指令让其自动阅读文档并安装
- **在线演示**：无（标记为 _No response_）
- **额外资源**：附微信公众号文章链接
- **亮点数量**：3 项核心亮点

两个 Demo 的对比展示了平台接受**多种形态**的项目——既有传统 Web 应用，也有 AI 工具链插件，安装方式不限定于命令行。

## 文档编写要点

1. **项目名称**：清晰准确，可附中文/英文副标题
2. **核心亮点**：3-4 条，每条突出一个独特卖点，避免泛泛而谈
3. **运行方式**：步骤清晰可复制，确保读者能成功运行
4. **截图**：提供至少 1-2 张预览图，展示项目实际效果
5. **技术栈**：列出主要技术，但无需罗列所有依赖

## 相关链接

- [TRAE Demos 定位与期数制组织](/concepts/00-introduction.md)
- [投稿流程与多场景 Issue 模板](/concepts/02-contribution-process.md)
- [提交 Demo 示例](/examples/submit-demo.md)
- [TRAE Demos 仓库资源索引](/references/demos-source.md)
