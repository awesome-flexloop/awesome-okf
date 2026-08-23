---
type: ChangeLog
title: 变更日志
description: JupyterLite Demo OKF bundle 的版本变更记录
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
---

# Changelog

## 2026-08-22

- 初始版本（v0.8.0）
- V阶段验证修复：
  - 修正 pyb2d 安装方式（`%pip install pyb2d` → `await piplite.install('pyb2d-jupyterlite-backend>=0.4.2')`）
  - 修正 p5.js `%show` 命令（移除不存在的尺寸参数 `%show 400 400` → `%show`）
  - 补充6个文件缺失的YAML frontmatter（facts.md, insights.md, log.md, concepts/index.md, examples/index.md, references/index.md）
  - 补充5个Reference文件缺失的source_type/source_path字段
- 基于 jupyterlite/demo 仓库生成 OKF v0.2 教程
- 包含 8 篇概念文档、7 篇实践示例、5 篇信源参考
- 覆盖站点部署、三大内核、%pip包管理、数据可视化、交互控件、地图、创意编程、站点定制
