---
type: Concept
title: 权限、热更新与恢复
description: 在安装前判断作用范围，在热更新后核对资源清理、状态和配置覆盖。
source: ../references/creator-mode-facts.md
sources:
  - { id: facts, resource: ../references/creator-mode-facts.md }
  - { id: start, resource: "https://deepseek-harness.github.io/deepseek-harness/en/guide/quickstart" }
  - { id: basic, resource: "https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/" }
  - { id: publish, resource: "https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish" }
  - { id: hmr, resource: "https://deepseek-harness.github.io/deepseek-harness/en/develop/cordis-tutorial/06-composition-and-hmr" }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T10:15:04+08:00" }
status: draft
stale_after: 2026-12-04
---

# 权限、热更新与恢复

原文建议使用完全权限，并称插件管理器的操作需要该权限。[F-031](../references/creator-mode-facts.md) 官方入门页只确认操作会按当前权限策略请求审批。[F-058](../references/creator-mode-facts.md) **本教程不把完全权限作为默认前提。** 安装或修改配置前应查看当前版本实际请求的操作、路径、profile 与权限范围；无法判断时停在预览，不以减少弹窗为由扩大权限。

## 安装前先看变更范围

可以向 Agent 提出以下要求。这是本教程的安全约束，不是已确认存在的“安全模式”按钮：

```text
先检查当前运行时和插件管理能力，只给出方案与待变更文件。
说明目标 profile、依赖、网络访问、配置修改以及恢复方式。
不要安装、运行安装脚本、读取凭证或切换权限。
任何写入与执行都等我确认后再做。
```

首次练习使用独立测试目录和不含敏感会话、密钥或业务文件的受控环境。专用 profile 有助于限定配置组合，但 profile 本身不等于安全沙箱；不能据此推断文件、网络和凭证访问已经隔离。

模型请求发生在安装之前也可能收费。首次预览前，人工确认实际模型端点、计费来源、累计费用预算和最多尝试轮次；每轮查看服务端用量，无法确认余额或到达预算即停止，不假设客户端存在自动预算开关。企业试点还须核对发送的上下文、遥测、日志留存和删除规则，只允许获准的数据类别外发；目录没有密钥不等于上下文没有敏感信息。

安装批准应绑定已展示的源码、软件包来源、确定版本、传递依赖清单和安装生命周期脚本的执行范围。版本、依赖或脚本变化后重新审批，不将相同插件名视为内容相同的证明。

官方安装教程特别提醒，允许构建脚本相当于允许软件包代码在本机安装时执行，位于 Agent 沙箱之外；因此运行时的权限审批不能代替安装脚本审核。[官方短摘录与来源](../references/source-manifest.md)

## 检查依赖不等于检查激活

官方文档把插件 bundle 装入 profile，并提供配置查看与卸载方式。[F-060、F-061](../references/creator-mode-facts.md) 下列是官方教程的命令示意，**本次未执行**；要求已有可用 `dsh` CLI，以及从包含 `hello-plugin` 的目录运行。它不是作者五个插件的安装命令。

```sh
dsh plugin --profile demo add ./hello-plugin
dsh --profile demo --dump-config
dsh --profile demo
dsh plugin --profile demo remove dsh-hello-plugin
```

`add` 和 `remove` 会改变 profile；`--dump-config` 用于核对组合，不代表插件已启动。先确认包的实际名称、文件结构与 manifest，再决定是否执行。源码运行入口与已安装 CLI 入口应遵循当前官方教程，不混用。

验收时分别记录依赖安装、配置层出现、运行时激活、UI 挂载、交互正确。任何一层失败都不能宣布“插件完成”。

## 热更新仍有生命周期

官方 HMR 教程描述的是卸载旧实例，再加载新实例；缺少依赖的插件可能停在 `PENDING`，没有运行输出。[F-063](../references/creator-mode-facts.md)

对倒计时来说，旧计时器应在卸载时停止；对主题来说，旧样式与监听器应清理；对三维场景来说，需说明渲染循环和外部资源由谁释放。这些是验收要求，不是官方文档承诺所有生成代码都能自动做到。

官方基础示例用 `ctx.effect()` 注册显式清理函数。[F-059](../references/creator-mode-facts.md) 本次没有作者插件源码，不能确认其使用了该机制，也不能认定任意自行创建的资源都会被框架接管。

| 观察到的现象 | 优先核对 | 不能直接推出 |
|---|---|---|
| 安装后没有界面 | 配置层、插件状态、依赖与挂载位置 | 模型没有能力生成 |
| 热更新后计时变快 | 旧计时器、监听器、重复挂载 | 热更新本身有安全隔离 |
| 切回页面丢数据 | 内存状态、持久化存储、加载重置逻辑 | “无需重启”保证持久化 |
| 停用后样式残留 | 样式作用域与清理函数 | 停用必然自动恢复所有改动 |
| 改一项配置丢其他项 | 补丁对整行 config 的覆盖 | 配置层会自动深合并 |

这些是可能的排查方向，不是本次发现的运行时故障。

## 配置覆盖与恢复

官方说明后加载层覆盖前层，patch 替换整行 `config`，并不深合并。[F-062](../references/creator-mode-facts.md) 修改前应记录原配置及插件 ID；只补一个字段时，也需检查原行其余字段是否仍存在。

恢复时先停用或卸载本次扩展，再核对界面、会话、配置与资源状态。官方 HMR 文档中的 `disabled: true` 可保留配置条目而卸载插件；具体产品管理界面是否暴露该操作，取决于当前版本。不要手工删除不明 profile 或用户数据目录。

配置恢复采用以下人工验收流程，不假设卸载自动撤销用户补丁：

1. 修改前保留目标 profile 的 bundle 顺序、用户补丁、原配置行和解析后的配置基线；含敏感值的副本只留在受控本地，不进入公开知识包。
2. 停用扩展后，逐项比对批准的变更。只恢复本次修改的原行和顺序；若存在其他人的更新，先协调，不覆盖整个 profile。
3. 重新查看解析配置，确认原字段及其他插件配置保持不变，再检查界面、会话和资源清理证据。没有基线或不能确认差异时，记录“恢复未验收”，停止进一步改动。

练习通过不等于生产准入。生产使用还需明确升级回归、持久化数据备份与恢复、故障责任人和回退时限，并以实际业务任务记录模型费用、开发审核维护时间及替代方案；本次没有这些实测，不承诺收益。

本次学习未安装插件、未修改权限、未启动模型。读者要把自己的观察结果与[作者结果](creator-case-studies.md)分开记录。
