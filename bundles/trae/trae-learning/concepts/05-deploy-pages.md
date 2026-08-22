---
type: Concept
title: GitHub Pages 部署
description: 通过 GitHub Actions 双 job 工作流实现自动构建部署到 GitHub Pages，包含 build 和 deploy 步骤及双语 Issue 模板配置。
tags: [trae-learning, trae, github-pages, deploy, github-actions, cicd]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# GitHub Pages 部署

TRAE Learning 通过 GitHub Actions 实现 main 分支 push 即自动构建部署到 GitHub Pages，形成"内容贡献→部署上线→反馈收集→内容迭代"的完整闭环。

## 部署工作流：.github/workflows/deploy.yml

### 触发条件

工作流在以下情况触发运行：

- **push 到 main 分支**：代码合并后自动部署
- **手动触发**（workflow_dispatch）：在 Actions 页面手动运行

### 双 Job 架构

工作流包含 build 和 deploy 两个 job：

#### build job

- **运行环境**：ubuntu-latest
- **Node.js 版本**：20
- **步骤**：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | checkout | 拉取代码（fetch-depth: 0） |
| 2 | setup-node | 配置 Node.js 20 + npm 缓存 |
| 3 | configure-pages | 配置 GitHub Pages |
| 4 | npm ci | 安装依赖（使用 lock 文件） |
| 5 | npm run docs:build | 构建 VitePress 静态站点 |
| 6 | upload-pages-artifact | 上传构建产物（路径 `.vitepress/dist`） |

#### deploy job

- **依赖**：需要 build job 完成后运行
- **环境**：github-pages
- **步骤**：使用 `actions/deploy-pages@v4` 部署到 GitHub Pages

### 关键配置

VitePress 配置中的 `base: '/trae-learning/'` 必须与 GitHub Pages 的子路径匹配，否则资源路径会出错。

## 本地构建与预览

在推送之前，可以在本地验证构建结果：

```bash
npm run docs:build    # 构建静态站点
npm run docs:preview  # 预览构建结果
```

构建产物输出到 `.vitepress/dist` 目录。

## Issue 模板与社区反馈

项目配置了 7 个 YAML 格式的 Issue 模板，构建社区反馈闭环：

### 模板文件

| 文件 | 用途 | 语言 |
|------|------|------|
| config.yml | 空 Issue 重定向配置 | 中英双语 |
| learning_path.yml | 学习路线建议 | 中文 |
| learning_path_en.yml | Learning path suggestion | 英文 |
| resource_bug.yml | 资源问题报告 | 中文 |
| resource_bug_en.yml | Resource bug report | 英文（空文件） |
| resource_request.yml | 资源请求 | 中文 |
| resource_request_en.yml | Resource request | 英文 |

### config.yml 重定向

`config.yml` 通过 `contact_links` 将空 Issue 引导至 Discussions 讨论区：

- 中文："讨论区（学习交流/问题求助）"→ <https://github.com/orgs/trae-community/discussions>
- 英文："Discussion Forum (Learning Exchange/Q&A)"→ 同一地址

这避免了自由格式 Issue 难以分类处理的问题。

### learning_path.yml（学习路线建议）

- 标题前缀：`[路线] `
- 标签：`["learning-path", "enhancement"]`
- 表单字段：主题（必填）、面向人群（必填 dropdown：零基础/转行入门/有经验开发者/其他）、学完效果（必填）、章节建议（选填）、参考资料（选填）

### resource_bug.yml（资源问题）

- 标题前缀：`[资源问题] `
- 标签：`["bug", "resource"]`
- 表单字段：出问题位置（必填）、问题描述（必填）、修改建议（选填）

## 贡献闭环

整个社区贡献流程为：

1. **内容贡献**：通过 PR 提交新教程、修改现有内容
2. **自动部署**：合并到 main 分支后自动构建部署到 GitHub Pages
3. **反馈收集**：通过双语 Issue 模板收集学习路线建议和资源问题
4. **讨论交流**：Discussions 作为开放式讨论区
5. **内容迭代**：根据反馈持续改进内容

## 相关链接

- [VitePress 站点架构](/concepts/01-vitepress-setup.md)
- [Tutorials 实战教程](/concepts/04-tutorial-content.md)
- [本地预览与构建示例](/examples/local-preview.md)
- [文档站源码索引](/references/learning-source.md)
