---
type: Concept
title: 旧版 scrapli 到 scrapli2 迁移指南
description: 从旧版 scrapli 迁移到 scrapli2 的完整变化清单——Zig 核心架构、inputs 与 modes 新语义、Python/Go 破坏性变更与 PyPI 双包安装
tags: [scrapli, migration, libscrapli, zig, breaking-changes]
generated: { by: "doc_agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
    title: scrapli2 源码信源登记
---

## 迁移总览

scrapli2 是对旧版（legacy）scrapli 的大版本重写。由于 scrapli 的 API 表面积很小，变化虽然剧烈，但把既有代码迁移到新格式并不算特别困难。本文依据官方迁移文档（docs/migration.md）梳理全部变化，供从旧版迁移的用户快速对照。

## 总体变化

### 核心逻辑全部迁入 Zig

所有"聪明的东西"都在 Zig 里完成：libscrapli 现在是一切的核心，Python 和 Go 包只是围绕 libscrapli 的薄、惯用封装。scrapli/scrapligo 离开 libscrapli 无法工作（F-053、F-054）。

### "configurations" 概念取消，只剩 inputs

libscrapli 取消了发送 "configurations" 的概念。现在只有 inputs，可以在任意 "mode" 发送（当然包括 "configuration" mode）。随着这一心智模型的变化，generic 与 network driver 的划分不复存在（F-055）。

### scrapli community → scrapli definitions

scrapli community 已被 scrapli definitions 取代——这一转变从 scrapligo 就已开始，definitions 严格为 YAML。这让定义更可移植，代价是灵活性降低（F-056）。

### Cli 连接不再必须指定 platform

使用 Cli 连接时不再必须指定 platform——未提供时会自动选择一个非常通用的默认平台。不过官方文档仍建议提供与目标设备匹配的 platform，以获得正确的分页禁用等行为（F-057）。

### privilege levels → modes

privilege levels 被 "modes" 取代。这主要是语义变化——仍可以在给定的 mode/privilege level 发送输入，且多数 definitions 会在连接时尝试进入合理的默认/初始 mode（F-058）。

### NETCONF 支持增强

NETCONF 支持总体增强。虽然并未支持全部 RFC RPC，但提供了 "raw" RPC 方法（`raw_rpc`），可将任意需要的内容发送到 NETCONF 服务器（F-059）。

### 默认 bin transport 行为变化

默认 `bin` transport 有两项行为变化（F-060）：

- 默认禁用 strict key checking——这在历史上一直是新用户的痛点。官方建议你自行启用……但由你决定
- 默认不再以 `-F /dev/null` 跳过默认 ssh config 文件——即默认自动遵循用户 ssh config 文件中的设置

### auth_secondary 移除，改为 lookups

`auth_secondary`（历史上用作 enable 密码）已移除。该功能被 *lookups* 取代——本质上是 lookup 键及其对应值组成的数组，在 definition 中以如下形式引用：

```yaml
response: '__lookup::enable'
```

即使用 key 为 "enable" 的 lookup（F-061）。

## Python 变化

- **transport 库不再依赖**：不再支持 paramiko、asyncssh、ssh2-python——所有 transport 逻辑都在 libscrapli/C 依赖中实现（F-062）
- **TTP 移除**：TTP 支持已被移除。TTP 很好用，只是保留一条基本只有一行的额外 API 表面有点愚蠢，你可以轻松自行处理（F-063）
- **全关键字参数**：除必选参数外，全部强制为关键字参数（通过 `*` 实现），这让移动参数位置而不影响用户代码变得容易（F-064）
- **NETCONF 并入主包**：不再有独立的 NETCONF 包（scrapli-netconf），全部 NETCONF 功能位于 libscrapli，scrapli 包将其与 CLI 功能一同暴露（F-065）
- **Python 3.10+**：仅支持 Python 3.10+（类型注解是需要 3.10 的主因）。官方文档称，若确实需要，经少量修改最低可回溯至约 3.7（F-066）
- **mixin 取消**：不再有 mixin 机制。历史上 mixin 用于以一套公共功能同时提供同步与异步版本；现在同一 `Cli`/`Netconf` 类直接同时提供两种风格的方法，如 `get_config_async` 与 `get_config`（F-067）
- **community 定制影响**：scrapli community 弃用对少数平台（官方文档点名 FortiOS）的 "extra" 定制有影响——此类定制最终需要社区/个人自行维护，因为 libscrapli 后端不容易保留这类定制能力（F-068）
- **NETCONF subscriptions**：Python 现在支持处理 NETCONF subscriptions——旧版因 channel 处理数据的方式而无法实现。可参见官方相关示例（F-069）

## Go 变化

- **超时交由 contexts**：Go 包不再有 timeout options，超时改由 contexts 管理——正如你在任何合理的 Go 包中所期望的（F-070）
- **无 bring-your-own transport**：当前没有 "bring your own" transport 选项（F-070）
- **libscrapli 必需**：libscrapli 为必需依赖，首次运行时自动获取；也可提前自行处理（例如在容器场景）。参见安装文档的 Go 章节
- **NETCONF subscription**：Go 不再直接支持任何形式的 NETCONF subscription 建立，但支持获取 subscription/notification 消息——只是需要你自己多做一点订阅的建立工作（F-070）

## PyPI 双包与安装

由于旧版 scrapli（py）使用 calendar versioning，而新版 scrapli 总体转向 semantic versioning，PyPI 上现在存在 *两个* 项目——`scrapli` 与 `scrapli2`。两者是同一代码库，唯一差异是版本方案（F-045、F-046）：

| 包名 | 版本方案 |
|------|----------|
| `scrapli` | calendar versioning（保持旧行为不变，也避免 pip 在两种版本方案间比较混乱） |
| `scrapli2` | semantic versioning |

```bash
pip install scrapli    # calendar versioning
pip install scrapli2   # semantic versioning
```

可选 extras（F-048）：

```bash
pip install scrapli[textfsm]   # textfsm / ntc-templates 解析
pip install scrapli[genie]     # genie 解析
pip install scrapli[full]      # 两者兼得
```

## 旧版类名与 API 对应关系

下表帮助从旧版代码定位新 API。注意：旧版的 `Scrapli`、`AsyncScrapli`、`NetworkDriver`、`Channel` 等类名**不存在于 scrapli2**。

| 旧版（legacy scrapli） | scrapli2 | 说明 |
|---|---|---|
| `Scrapli` / `AsyncScrapli` | `Cli` | 同一类同时提供同步与异步方法（如 `send_input` / `send_input_async`） |
| `NetworkDriver` | `Cli` | generic 与 network driver 的划分已取消 |
| scrapli-netconf 独立包的驱动 | `Netconf` | NETCONF 并入 scrapli 主包 |
| `Channel` | 无对应类 | 通道逻辑位于 libscrapli 内部 |

在方法层面，迁移文档没有逐条给出方法映射表，但明确了概念对应：旧版把"发命令读输出"与"发送配置"分为不同操作（并因此区分 generic/network driver），而 scrapli2 只有 **inputs** 一种概念——旧版意义上的"发送配置"在新版中就是在指定 mode 下发送输入。因此，旧代码中"在某权限级别下发送配置"的模式，应改写为"进入对应 mode 后用统一的输入发送方法"（配合 `requested_mode` 等参数）；NETCONF 场景则迁移到 `Netconf` 类的方法对（如 `get_config` / `get_config_async`），未覆盖的 RPC 可经 `raw_rpc` 发送。请勿按旧版方法名逐一硬套——以概念差异为准重构调用点。

## 相关概念

- [/concepts/00-introduction.md](/concepts/00-introduction.md) — scrapli2 整体架构与 Zig+Python 混合设计
- [/concepts/04-cli-driver.md](/concepts/04-cli-driver.md) — 新版 `Cli` 驱动与输入发送方法
- [/concepts/07-netconf.md](/concepts/07-netconf.md) — 新版 `Netconf` 驱动、`raw_rpc` 与 subscriptions
- [/references/scrapli-source.md](/references/scrapli-source.md) — 源码信源登记
