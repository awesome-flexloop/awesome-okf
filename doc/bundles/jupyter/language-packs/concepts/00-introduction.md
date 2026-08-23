---
type: Concept
title: "JupyterLab 语言包项目介绍"
description: "language-packs 项目定位——JupyterLab 生态多语言翻译 monorepo，Crowdin 众包+Bot 自动化驱动"
tags: [jupyterlab, language-pack, i18n, overview, localization]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:23:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-readme, resource: /references/repo-readme.md, title: "仓库根 README 信源" }
  - { id: repo-map, resource: /references/repo-map-source.md, title: "repository-map.yml 配置信源" }
---

# JupyterLab 语言包项目介绍

JupyterLab Language Packs 是 Jupyter 官方维护的多语言翻译包 monorepo，为 JupyterLab 及其生态扩展提供 30+ 种语言的界面翻译。项目采用 **Crowdin 众包翻译 + GitHub Bot 全自动化流水线** 模式，人类译者只需在 Crowdin 平台上翻译字符串，所有 Git 操作、包构建、PyPI 发布均由自动化流程完成。

## 项目定位

```
用户语言选择 → JupyterLab entry-point 发现 → 加载 .mo/.json 翻译 → 界面本地化
```

语言包本身是**纯数据包**——不包含 Python 逻辑代码，仅由 gettext 翻译文件（.po → 编译为 .mo/.json）和最小化的包元数据构成。JupyterLab 运行时通过 Python entry-point 机制自动发现已安装的语言包，根据用户设置加载对应的翻译文件。

## 核心特性

- **30+ 语言支持**：覆盖中文（简/繁）、日语、韩语、法语、德语、西班牙语等主要语种
- **17 个扩展覆盖**：JupyterLab 核心 + 16 个官方/主流扩展（Git、LSP、协作、Widget 等）
- **全自动流水线**：版本检测→字符串提取→Crowdin同步→翻译合并→版本提升→构建发布，全程 Bot 驱动
- **PyPI + conda-forge 双渠道发布**：`pip install` 或 `conda install` 一键安装
- **BSD-3-Clause 许可证**：完全开源

## 覆盖的扩展包

| 扩展 | 功能 |
|------|------|
| jupyterlab | JupyterLab 核心界面 |
| notebook | Notebook v7 界面 |
| jupyterlab-git | Git 版本控制集成 |
| jupyterlab-lsp | 语言服务器协议（代码补全/诊断） |
| jupyter-collaboration | 实时协作编辑 |
| jupyter-resource-usage | 资源使用监控 |
| jupyterlab_widgets (ipywidgets) | 交互式控件 |
| jupytext | 多格式笔记本支持 |
| nbdime | Notebook diff/merge |
| dask-labextension | Dask 集群管理 |
| jupyter-archive | 归档下载 |
| jupyterlab-recents | 最近文件 |
| jupyterlab-search-replace | 搜索替换 |
| jupyterlab-spreadsheet-editor | 电子表格编辑器 |
| jupyterlab-tour | 用户引导 |
| spellchecker | 拼写检查 |
| jupyter-chat | 聊天功能 |

## 与 JupyterLab 国际化的关系

JupyterLab 的国际化（i18n）基于 gettext 标准：
1. 开发者在源码中使用 `_()` 标记可翻译字符串
2. 构建时提取所有标记字符串生成 POT 模板
3. language-packs 仓库从各扩展仓库提取 POT，同步到 Crowdin
4. 译者在 Crowdin 翻译，翻译结果自动 PR 回合
5. 构建系统将 .po 编译为 .mo/.json，打包为 wheel 发布
6. 用户安装语言包后，JupyterLab 通过 entry-point 自动发现

## 支持的语言

当前仓库包含 31 个语言包目录（含 1 个伪语言包）：

- 欧洲语言：法语(fr-FR)、德语(de-DE)、西班牙语(es-ES)、意大利语(it-IT)、葡萄牙语-巴西(pt-BR)、荷兰语(nl-NL)、波兰语(pl-PL)、罗马尼亚语(ro-RO)、俄语(ru-RU)、乌克兰语(uk-UA)、捷克语(cs-CZ)、丹麦语(da-DK)、芬兰语(fi-FI)、希腊语(el-GR)、匈牙利语(hu-HU)、挪威语(no-NO)、加泰罗尼亚语(ca-ES)、立陶宛语(lt-LT)、爱沙尼亚语(et-EE)
- 亚洲语言：中文-简体(zh-CN)、中文-繁体(zh-TW)、日语(ja-JP)、韩语(ko-KR)、阿拉伯语(ar-SA)、希伯来语(he-IL)、土耳其语(tr-TR)、越南语(vi-VN)、印尼语(id-ID)、亚美尼亚语(hy-AM)
- 特殊：阿乔利语(ach-UG) —— 伪语言包，用于 Crowdin in-context 翻译测试

## 相关概念

- [整体架构概览](01-architecture-overview.md)
- [仓库目录结构](02-repository-structure.md)
- [Entry Point 语言包发现机制](10-entry-point-discovery.md)
