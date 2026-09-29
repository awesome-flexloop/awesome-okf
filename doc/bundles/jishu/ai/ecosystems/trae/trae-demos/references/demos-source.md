---
type: Reference
title: TRAE Demos 仓库资源索引
description: trae-demos 仓库源码位置、期数制目录结构、Demo Markdown 格式、多场景 Issue 模板和审核权重的信源登记簿
tags: [demos, trae, period-based, issue-templates, source-index, trae-demos]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/demos-source.md
    title: "Trae Demos 源码信源"
---

# TRAE Demos 仓库资源索引

本文档汇总 trae-demos 仓库的期数制组织、Demo 格式、投稿机制和审核标准。

## 仓库基本信息

| 项目 | 内容 |
|------|------|
| 仓库地址 | `trae-community/trae-demos`（GitHub） |
| 许可证 | MIT License，提交项目版权归原作者所有 |
| 定位 | 社区驱动的 TRAE 构建项目展示平台 |
| 语言支持 | 中英双语（README.md / README.zh-CN.md） |

## 仓库目录结构

```
trae-demos/
├── README.md                 # 英文 README
├── README.zh-CN.md           # 中文 README
├── CONTRIBUTING.md           # 英文贡献指南
├── CONTRIBUTING.zh-CN.md     # 中文贡献指南
├── LICENSE
├── assets/image/Demos.gif    # 横幅图片
├── demos/period-1/           # 第 1 期（2026.03）
│   ├── demo-1.md             # Minecraft Guilin City Walk（英文）
│   ├── demo-1.zh-CN.md       # 中文
│   ├── demo-2.md             # TraeClaw（英文）
│   └── demo-2.zh-CN.md       # 中文
└── .github/ISSUE_TEMPLATE/   # 7 个 YAML 模板
```

## 期数制组织

| 期数 | 发布时间 | 包含 Demo 数量 |
|------|---------|---------------|
| period-1 | 2026.03 | 2 个（Minecraft Guilin City Walk、TraeClaw） |

> ⚠️ **事实记录**：Demo #2（TraeClaw）文件头标注"Issue: #2 | April 2026"，与 README 中"Issue #1"标注存在不一致。

## 投稿 4 项 Must Have

1. 使用 TRAE 作为核心技术
2. 可访问（公开仓库或在线演示）
3. 代码质量良好且有基本文档
4. 完成度较高（polished）

## 5 个项目分类

Web Applications / Tools & Utilities / Games / AI Applications / Other。

## 审核评分权重

| 维度 | 权重 |
|------|------|
| TRAE Usage | 40% |
| Code Quality | 25% |
| Completeness | 20% |
| Documentation | 15% |

## 7 个 Issue 模板覆盖 5 种场景

| 场景 | 模板 |
|------|------|
| 投稿 Demo | submit_demo_en.yml / submit_demo_zh.yml |
| 报告问题 | report_demo_en.yml / report_demo.yml |
| 更新信息 | update_demo.yml |
| 需求征集 | want_demo.yml |

config.yml 禁用空 Issue（`blank_issues_enabled: false`），引导至 Discussions。

## 已收录 Demo

### Demo #1: Minecraft Guilin City Walk
- 作者 @MU-ty，Web App，JavaScript/TypeScript
- 核心亮点：PixelMap 像素地图、TRAE 在桂林社区活动、MC 风格 UI、管理员系统
- 本地运行：git clone → npm install → npm run dev

### Demo #2: TraeClaw
- 作者 @firerlAGI，Plugin/Extension，JavaScript/TypeScript
- 核心亮点：本地调用链路打通、npm 分发、完善排障体系
- 安装方式：向 OpenClaw 发送自然语言指令自动安装（非传统命令行）

## 相关链接

- [TRAE Demos 定位与期数制组织](../concepts/00-introduction.md)
- [Demo Markdown 文档格式](../concepts/01-demo-format.md)
- [投稿流程与多场景 Issue 模板](../concepts/02-contribution-process.md)
- [提交 Demo 示例](../examples/submit-demo.md)
