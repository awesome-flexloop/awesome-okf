---
okf_version: "0.2"
type: Concept
title: "命令面与产品组织：按业务对象切分，而不是按 API 分组"
description: "dws 的命名约定、20 个服务域的职责划分、快捷命令与别名、bot 并入 chat 的迁移，以及 dev 产品这条例外通道"
sources:
  - id: repo
    resource: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
  - id: readme
    resource: "README.md"
  - id: index
    resource: "docs/command-index.md"
facts: [F-013, F-014, F-015, F-016, F-024, F-058, F-062]
---

# 03 · 命令面与产品组织

> 核心判断：产品不是按「开放平台的 API 分组」切，而是按**用户心智里的业务对象**切；因此会出现「机器人属于 chat」「开发能力自成一个 dev 产品」这类看似不合 API 目录的划分。

## 1. 命名约定

```text
dws <product> <resource> <verb> [flags]
     └ 业务域    └ 对象     └ 动作
```

（F-015、F-024）

| 层级 | 例子 | 说明 |
|------|------|------|
| 产品 | `chat`、`calendar`、`aitable` | 一级命令，对应业务域 |
| 资源 | `message`、`event`、`record` | 二级命令，对应被操作对象 |
| 动词 | `send`、`list`、`create` | 三级命令，对应动作 |
| 快捷命令 | 面向高频组合的别名 | 减少层级，但不改变底层契约 |

两条纪律：

1. flag 承载全部业务输入，位置参数只保留「选择器」用途（如命令路径本身）。
2. 别名只影响输入，不影响 Schema 中的规范路径——Agent 永远看到规范路径。

## 2. 20 个服务域的职责边界

| 服务域 | 它管什么 | 容易混淆的邻域 |
|--------|---------|---------------|
| `contact` | 人员、部门、组织关系 | 与 `chat` 的「群成员」不同，后者是会话视角 |
| `chat` | 单聊/群聊消息、会话、机器人 | 机器人能力已并入，不再有独立 `bot`（F-016） |
| `ding` | DING 消息与提醒 | 不是普通消息，触达语义更强 |
| `live` | 直播 | — |
| `calendar` | 日程、参与者、忙闲 | 与 `todo` 的时间语义不同 |
| `todo` | 待办与清单 | 不是审批任务 |
| `oa` | 审批实例与表单 | 与 `todo` 常被混用，前者有流程状态机 |
| `attendance` | 打卡、排班、考勤统计 | — |
| `report` | 日志/汇报 | — |
| `doc` | 文档正文与块结构 | 与 `wiki` 的目录树不同 |
| `sheet` | 电子表格单元格 | 与 `aitable` 的记录模型不同 |
| `aitable` | 多维表：表、字段、记录、视图 | 最复杂的一域，涉及字段类型 |
| `wiki` | 知识库空间与节点 | — |
| `drive` | 云盘文件与目录 | 与 `doc` 的「文档对象」不同 |
| `whiteboard` | 白板 | — |
| `minutes` | 会议纪要 | 与 `live` 的直播流不同 |
| `mail` | 邮件收发与文件夹 | — |
| `devdoc` | 开放平台文档检索 | 只读参考，不产生业务副作用 |
| `aisearch` | AI 搜索 | — |
| `api` | 原始 API 直连 | 逃生舱，不参与 Agent Schema（F-058、F-060） |
| `dev` | 本地开发桥接与会话 | 非业务域，是工具链入口（F-062） |

（F-013）

## 3. 规模口径：两把尺子

| 尺子 | 数值 | 含义 |
|------|------|------|
| 服务域 | 20 | README 列举的能力全集（F-013） |
| 产品 × 命令 | 13 × 180 | `pre` 环境命令索引快照（F-014） |

差异来源：命令索引是**某环境的接入快照**，服务域是**能力规划口径**。写文档时不要混用；需要引用时带上「快照」二字（见 [verification.md](../references/verification.md) 冲突 C-1）。

## 4. 三个组织决策及其理由

### 4.1 机器人并入 `chat`

`dws bot ...` 迁移为 `dws chat bot ...`（F-016）。

- 理由：机器人在用户心智里就是「会话里的一个成员」，独立成产品会让「发消息给机器人」与「以机器人身份发消息」分散在两处。
- 影响：老脚本需要改路径；但消息类能力从此只有一个入口。

### 4.2 `api` 作为逃生舱

`dws api` 可直连开放平台（F-058），但被排除在 Agent 可见 Schema 之外（F-060）。

- 理由：命令面追求「可枚举、可校验」，raw 通道天生不可枚举。
- 纪律：人类可用，Agent 不可见；使用时先 `--dry-run`，并受域名白名单约束（F-050）。

### 4.3 `dev` 自成一个产品

`dws dev connect` 把消息机器人桥接到本地 AI CLI，支持 `--unified-app-id` 与会话命令 `/new`、`/clear`（F-062）。

- 它不是「操作钉钉数据」，而是「把钉钉当入口，驱动本地开发工具」。
- 因此与业务域并列，而不是塞进 `chat`。

> **洞察**：产品划分真正遵循的是**动作的发生地**——数据在钉钉云端（20 个业务域），还是数据在本地机器（`dev`）。这条界线比 API 目录更能预测用户会去哪里找命令。

## 5. 命令发现的三条路径

| 路径 | 命令 | 适用 |
|------|------|------|
| 人类浏览 | `dws --help` → `dws chat --help` → `dws chat message --help` | 手动探索 |
| 机器查询 | `dws schema <path>` | Agent 决策（避免读 help 文本） |
| 关键字检索 | 开放平台文档域 `devdoc` | 不知道归哪个产品时 |

## 6. 反模式

| 反模式 | 问题 | 建议 |
|--------|------|------|
| 按 API 目录建命令 | 用户找不到「发消息」在哪 | 按业务对象建 |
| 用位置参数传长文本 | 无法稳定生成 Schema | 用 flag 或 `@file`（F-045） |
| 为兼容保留两套别名路径 | Schema 出现重复项 | 别名只在输入层，规范路径唯一 |
| 把 raw api 当常规集成 | 绕过安全元数据与审计 | 只作一次性排障 |

## 延伸

- 命令的内部契约：[01-command-contract-model.md](01-command-contract-model.md)
- 输出与 Schema 细节：[05-output-and-schema-discovery.md](05-output-and-schema-discovery.md)
- 上手示例：[examples/01-daily-workspace-operations.md](../examples/01-daily-workspace-operations.md)