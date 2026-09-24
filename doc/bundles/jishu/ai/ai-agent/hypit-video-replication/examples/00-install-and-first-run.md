---
type: Example
title: "安装 Hypit Skill 并启动第一次视频工作流"
description: "按官方命令安装 Skill，准备项目目录，用参考视频启动 Agent 工作流。"
tags: ["Hypit", "安装", "Quickstart", "Codex"]
generated: { by: "reference_agent", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: repo
    resource: https://github.com/hypit-ai/hypit
---

# 安装与第一次运行

## 1. 安装 Skill

```bash
npx skills add hypit-ai/hypit -g
```

该命令来自 Hypit 官方 README（F-009）。安装 Skill 不等于获得模型账号或服务额度；首次运行仍需按 Agent 提示准备 Runtime 和凭证。

## 2. 准备项目边界

建议建立独立目录，至少包含：

```text
hypit-demo/
├── reference.mp4
├── product.png
├── logo.svg
└── notes.md
```

不要把无关素材和秘密密钥直接混入目录。对参考视频、人物、Logo 和产品图先确认使用授权。

## 3. 启动 Agent

示例提示：

```text
请打开当前项目，分析 reference.mp4 的开头、节奏、字幕、B-roll、切换和特效，
保留原结构，替换为 product.png 的产品介绍，并告诉我需要哪些模型服务。
```

没有参考视频时，也可以直接描述目标视频，让 Agent 从零创建工作流（F-006）。

## 4. 第一次验收

先看 Preview/Studio，再运行完整渲染。重点检查：

- 字幕是否跟随语音词，而不是停留在旧时间码；
- B-roll 是否支持对应解释；
- CTA、Logo 和产品是否出现在授权范围内；
- 生成模型、凭证和预算是否被明确列出。
