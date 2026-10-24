---
okf_version: "0.2"
type: bundle
title: "看山工作台：AI 桌面工作平台产品手册与实操教程"
description: "知乎「看山工作台：产品介绍与使用手册」的知识化重组——本地文件与 Excel 写回、浏览器与 Quick Bar、飞书/企业微信/钉钉连接、本地记忆与定时任务、Coding 与 Git 恢复、安全边界；含 120 条 F 编号事实与 14 项 P0 核验。"
tags: [kanshan, 看山工作台, 知乎, AI桌面工作平台, 本地文件, Excel, QuickBar, 飞书, 企业微信, 钉钉, 定时任务, Coding, Git, 产品教程]
generated: { by: "seven-concepts-cmd", at: "2026-10-23T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-23T00:00:00+08:00" }
status: draft
stale_after: "2026-12-31"
sources:
  - id: manual
    resource: https://www.zhihu.com/parker/campaign/2078900697026905490
    title: "看山工作台：产品介绍与使用手册（采集于 2026-10-23）"
  - id: article-source
    resource: /references/article-source.md
    title: "F-001~F-120 事实清单"
  - id: verification
    resource: /references/verification.md
    title: "P0 核验与口径边界"
---

# 看山工作台：AI 桌面工作平台产品手册与实操教程

> **类型**：官方产品手册的知识化重组与教程化改写（非实机评测）。
> **信源**：知乎站内页面《看山工作台：产品介绍与使用手册》，2026-10-23 通过浏览器渲染采集全文；页面无需登录，无外链与按钮（F-112）。
> **核验**：14 项 P0 → **✅ 原文明确 11 项 / ⚠️ 计数不可精确复核 3 项 / ❌ 0 项**；整体为**平台单源**，未找到独立第三方评测（见 [verification.md](references/verification.md)）。

## 先读三条

1. **这是产品手册，不是实测报告**：所有操作步骤来自页面文字，本包**未安装客户端真机执行**；按钮名与流程可能随版本变化。
2. **页面无版本号与发布日期**（F-112）：并发上限、支持格式、Skills 可用性都可能变化；引用具体数字时请连同「2026-10-23 采集」一起转述。
3. **「本地文件不会上传到云端」是官方承诺，但数据流向未完全披露**（F-116）：原文同时说云端负责模型推理与多模态理解，未说明本地文件内容以何种形式参与推理。敏感材料请先脱敏，不要把这句话扩写为「任何数据都不离开本机」。

## 一句话定位

看山工作台是知乎推出的 **AI 桌面工作平台**（F-001）：在用户授权范围内处理本地文件、辅助操作浏览器、连接飞书/企业微信/钉钉、执行周期性任务，并可在指定项目目录中协助代码阅读、修改和测试（F-002、F-003）。官方用三个转变概括它——从「搬运材料」到「直接处理」，从「回答问题」到「交付结果」，从「一次性使用」到「持续执行」（F-007~F-009）。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|---|---|
| [00 · 看山工作台是什么](concepts/00-overview.md) | 产品定位、三个转变、云端与本地 Agent 分工、四类硬边界（OS/部署/并发/恢复）、适合与不适合 |
| [01 · 本地文件与 Excel](concepts/01-local-files-and-excel.md) | 支持格式、授权目录模型、Excel 读改写回五要素、多文件综合处理、导出格式与公式限制 |
| [02 · 浏览器与 Quick Bar](concepts/02-browser-and-quickbar.md) | 插件安装、独立环境与 Cookie 边界、四类网页任务、Quick Bar 七类操作与限制 |
| [03 · 企业协作工具](concepts/03-enterprise-collaboration.md) | 飞书 lark-cli（约 25 服务域）、企业微信 wecom-cli（14 服务）、钉钉 dws（22 MCP 服务）、OAuth 与机器人授权差异 |
| [04 · 本地记忆与定时任务](concepts/04-memory-and-scheduled-tasks.md) | 核心记忆/项目上下文、五种记忆操作、定时任务六字段、五类周期、3 并发上限、时间触发边界 |
| [05 · Coding 任务与文件恢复](concepts/05-coding-and-file-recovery.md) | 读改测跑查、本地服务回收、受管 Python 环境、Git 只读命令、恢复确认门、无回滚/快照 |
| [06 · 安全、权限与 FAQ](concepts/06-security-and-faq.md) | 四条安全承诺、六条 FAQ、数据流向两档边界、按任务分级的风险清单、六条安全习惯 |

### examples/ — 实操示例

> 本目录是**依据官方手册重组的可复制模板，不是真机实测记录**；执行前请以实际客户端界面为准。

| 文档 | 场景 |
|---|---|
| [00 · 从安装到第一个任务](examples/00-install-and-first-task.md) | macOS/Windows 安装、知乎账号登录、目录授权、首个 Excel 分析任务与验收点 |
| [01 · Excel 写回的五套模板](examples/01-excel-writeback-templates.md) | 分类写回、异常批注、多文件汇总、清洗去重、分析结论新表，附统一验收清单 |
| [02 · 浏览器与 Quick Bar 实操](examples/02-browser-quickbar.md) | 插件安装、竞品对比、表格提取、登录处理、Quick Bar 四例与失败排查 |
| [03 · 飞书、定时任务与 Coding](examples/03-feishu-schedule-and-coding.md) | 连接飞书、创建每日任务、代码修改、Git 恢复与三条硬边界 |

### references/ — 信源登记

| 文档 | 说明 |
|---|---|
| [article-source.md](references/article-source.md) | F-001~F-120 事实清单：产品定位、核心功能、技术与安全说明、使用手册、FAQ 与安全权限，外加本包核验补充 |
| [verification.md](references/verification.md) | 14 项 P0 核验、勘误四张清单、单源与不可复核清单、内部一致性核对、五项待核问题 |

| 类别 | 数量 |
|---|---|
| 概念文档 | 7 |
| 实操示例 | 4 |
| 信源参考 | 2 |
| 索引与日志 | 2 |

## 主题关联

| 关联 bundle | 关系 |
|---|---|
| [ToDesk AI 跨设备 AI 助手](../todesk-ai/index.md) | 同为「桌面/跨设备 AI 助手」产品教程；ToDesk 侧重远程设备操控，本束侧重本地文件与企业协作 |
| [Orca ADE 多 Agent 桌面工作台](../orca-ade/index.md) | 同为桌面工作台，但 Orca 面向多 Agent 编程舰队编排，本束面向个人知识工作与文件处理 |
| [Octop 腾讯云本地 AI 工作空间](../octop/index.md) | 同为「本地 Agent + 企业协作」路线；Octop 是可自托管的多用户平台，本束是 SaaS 客户端 |
| [BrowserAct 浏览器自动化 Agent](../browseract/index.md) | 浏览器能力对照：BrowserAct 是专门化自动化框架，本束的浏览器工具是内置插件能力 |

## 已知边界

- **平台单源**：未找到独立第三方评测；「AI 看山」是知乎 App 内的助手，与本页桌面工作台不是同一产品，不能互证。
- **无版本锚点**：页面未标注发布日期、版本号、最低系统版本；所有「当前」口径只对 2026-10-23 成立，`stale_after` 收紧到 2026-12-31。
- **服务计数为不完全枚举**：飞书「约 25」、企业微信「14」、钉钉「22」；原文逐条枚举飞书 21 项（8+6+5+2；合并扩展能力则 20 项）、企业微信 13 项、钉钉 17 项，差额未说明（F-113~F-115）。
- **数据流向未完全披露**：「文件不上云」与「云端模型推理/多模态理解」之间存在口径张力（F-116）；真实浏览器连接器的权限与数据回流也未披露（F-117）。
- **未真机实测**：所有示例均未在本机执行；安装包、按钮文案、权限入口可能随版本变化。
- **无外链可跳转**：页面无链接与按钮（F-112），无法从该页进入下载页、更新日志或帮助中心。
- **无操作级回滚/自动快照**：产品内建能力不提供，只能借助 Git 或事先备份（F-093、F-098）。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
