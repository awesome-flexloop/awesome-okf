---
type: Concept
title: 创造模式与插件化工作台
description: 从模型、运行时与插件三个层次理解 Creator Mode，区分官方能力和文章单源工具名。
source: ../references/creator-mode-facts.md
sources:
  - { id: facts, resource: ../references/creator-mode-facts.md }
  - { id: official, resource: "https://deepseek.com/harness/en/" }
  - { id: publish, resource: "https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish" }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T10:01:28+08:00" }
status: draft
stale_after: 2026-12-04
---

# 创造模式与插件化工作台

DeepSeek 官方将 Creator 定位为创建自定义 Agent 预设的模式：保留 Standard 能力，增加运行时检查、插件试验和预设创作指导。[F-055](../references/creator-mode-facts.md) 作者把这些能力用于修改正在使用的工作台，制作输入区小组件、主题面板和三维交互场景。这些案例是作者报告，尚无本次独立运行证明。[F-020、F-021](../references/creator-mode-facts.md)

## 三个层次

| 层次 | 在任务中的角色 | 不应混淆的对象 |
|---|---|---|
| 模型 | 理解请求、提出方案与生成代码 | 模型能力不等于安装、授权与界面挂载成功 |
| Harness | 向 Agent 提供环境、工具、会话及执行能力 | 本地界面不等于模型本地推理 |
| Cordis 插件 | 在上下文中注册能力，由框架管理依赖与生命周期 | 使用同一加载机制不等于经过同一安全审核 |

官方说明模型、工具、Skills、会话、沙箱、存储、loop、调度和 UI 都由插件提供，通过服务与事件协作。[F-056](../references/creator-mode-facts.md) 从学习角度，可以把一次扩展理解为“找到已有能力及挂载位置，在受控范围增加插件，再核对结果与卸载行为”。这是一种阅读与验收框架，不是官方固定执行流水线。

## 创造模式增加了什么

原文称预设 ID 为 `cordis`，并列出 `cordis_inspect_list`、`cordis_inspect_query`、插件开发 Skills 和 `plugin_manager`。[F-023 至 F-026](../references/creator-mode-facts.md) 本次官方页面只确认检查、试验和预设指导这类能力，没有逐项确认这些工具的参数、输出结构与权限条件。

| 能力 | 读者可以要求 Agent 回答的内容 | 本次证据边界 |
|---|---|---|
| 检查运行时 | 哪些服务、扩展能力或 UI 挂载点当前存在 | 定位受官方支持；精确工具名来自文章 |
| 设计插件 | 需要什么输入、状态、依赖及清理逻辑 | 可参考官方插件教程，不猜测 UI 注册 API |
| 安装扩展 | 将安装到哪个 profile，哪些配置会变化 | 官方有 CLI 安装教程；文章的管理工具契约仍待核验 |
| 验证结果 | 安装状态、界面出现、交互变化、卸载恢复 | 作者结果只是案例，成功与否必须重新观察 |

工具是运行时可调用能力，Skills 是指导开发的方法资产，预设是 Agent 能力组合。不能把“安装一个 Skill”“挂载插件”和“选择 Creator”当作同一步。

## bundle 与 profile

官方安装教程中的 bundle 是带 `dsh.bundle` 声明的 npm 包，提供配置层；profile 是带 `dsh.profile` 的命名运行组合，保存有序 bundle 列表与用户补丁。[F-060](../references/creator-mode-facts.md)

这里的 npm bundle 与本库的 OKF 知识包同名但不同义。前者是软件分发与配置单元，后者是 Markdown 知识文档目录。本文谈安装时使用“插件 bundle”，谈本教程时使用“知识包”。

安装依赖也不必然激活插件。官方文档指出，没有 `dsh.bundle` 声明的包可作为普通依赖安装，但不会激活配置层。部署前应同时检查软件包、manifest 和实际加载配置，不能只看包管理器返回成功。

## 版本与学习入口

官方模型公告确认 `DeepSeek-V4.1-Flash-1017`，建议搭配 Harness `v0.2.1-rc.1` 或更新版本获得较佳体验。[F-064](../references/creator-mode-facts.md) 这不是 Creator 的最低版本声明，也不证明创造模式在文章发表当天首次上线。

官方仍称 Harness 为 developer preview，插件与 API 将继续演进。[F-057](../references/creator-mode-facts.md) 包内旧“2.0”标题是历史文章名称，不应用作版本约束。

已有可用环境时，从[首个插件练习](../examples/creator-first-plugin.md)开始；想判断原文五个案例能学到什么，读[五案例解读](creator-case-studies.md)；准备安装时先读[权限、热更新与恢复](creator-safety-and-lifecycle.md)。
