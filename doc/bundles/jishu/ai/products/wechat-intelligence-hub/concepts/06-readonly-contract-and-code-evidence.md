---
type: Concept
title: "06 · 只读契约的代码级实现"
description: "从源码证明「只读」不是文档承诺而是结构性保证：read_only 统一置位、数据库 mode=ro 快照、零写入型函数，以及实验性接入助手的反向边界"
tags: [wechat-intelligence-hub, read-only, source-code, security, structural-guarantee]
---

# 06 · 只读契约的代码级实现

> 本篇起自源码（固定 commit `fb6a42c`），事实编号见 [../references/source-code-map.md](../references/source-code-map.md)（F-058~F-101），对账过程见 [../references/source-code-verification.md](../references/source-code-verification.md)。
> **与首轮的关系**：首轮 [01-local-first-readonly-architecture.md](01-local-first-readonly-architecture.md) 从官方文档层描述只读边界；本篇补上代码层的实现证据，并把边界画得更精确。

## 1. 首轮只能说到「文档承诺」，源码能说到「结构性保证」

首轮核验项 #8（只读/不发消息/不操作微信 UI）判为 ✅，但依据是官方 README 与 `SECURITY.md` 的**文字表述**——那是承诺，不是机制。本轮读源码后，可以把这句话从「它承诺只读」升级为「它**没有**不只读的可能」：

| 机制 | 源码事实 | 编号 |
|------|---------|------|
| 统一置位 | `tools_catalog()` 与 `tool_schema()` 两处均以字面量 `"read_only": True` 出现在列表推导式内，对 `TOOL_SPECS` **全部 30 个工具统一置位**，不存在逐项开关 | F-073 |
| 零写入面 | Reader 源码中不存在 `send_message` / `send_text` / `post_message` / `write_*` 等任何写入型函数 | F-074 |
| 快照只读 | 数据库以 `sqlite3.connect(f"file:{snapshot}?mode=ro", uri=True)` 只读打开；`Snapshot` 上下文管理器在创建失败时抛出「无法创建只读快照」 | F-075 |
| 工具清单即契约 | 工具元数据由 `TOOL_SPECS` 单一声明处生成，不存在「注册了但没进清单」的隐藏工具 | F-069、F-073 |

**这为什么重要**：一个「只读」项目若仅靠文档承诺，安全边界就取决于使用者的信任；而当只读是**由数据结构决定的**（工具清单里只有读、没有写），边界就不再是承诺而是事实。工具数量增加（30 项）与只读属性是同一个机制带来的——新增能力只能以「读」的形式进入。

## 2. 边界必须分两半：Reader 核心 vs 实验性接入助手

首轮勘误③ 把「不重签名」限定在 Reader 核心，本轮在 `SECURITY.md` 找到了**官方逐字**依据（F-091）：

> "The Reader and Intelligence Hub are read-only with respect to WeChat: they do not send messages or automate replies. **The separate experimental `rion-wechat-access` helper is not read-only**: after explicit review and confirmation it can invoke an external local provider with macOS administrator authorization, which may restart WeChat, debug its process and re-sign a shadow copy."

拆开看是三段递进的边界：

| 层 | 是否只读 | 副作用 | 代码位置 |
|----|---------|--------|---------|
| Reader 核心（`rion_wechat_reader.py`，3,465 行） | ✅ 是 | 无 | F-073~F-075 |
| 情报产品（`wechat_intelligence_hub.py` 等） | ✅ 是 | 仅本地生成报告 | F-097、F-099 |
| 实验性接入助手（`rion_wechat_access.py`，954 行，24 函数 / 1 类 `AccessError`） | ❌ **否** | 可能重启微信、调试进程、重签名影子副本 | F-091 |

**关键工程细节**：接入助手与 Reader 是**两个独立文件**（`rion_wechat_access.py` vs `rion_wechat_reader.py`），且 `SECURITY.md` 明确「Installation and daily reports never invoke acquisition」——即安装流程与日常日报链路**不触发**获取动作，获取只在显式请求时发生。

这条边界对采用者的实际含义：把 `wechat-cli` Skill 装进日常环境，与在 macOS 上授权跑一次取钥助手，是**两个风险等级完全不同的动作**。前者可以日常做，后者的授权与影响范围需要单独评估。

## 3. 一个容易被忽略的连带约束：回复能力只产出草稿

源码层面，「回复」这条链路的终点是**字符串**，不是 API 调用：

- CLI `reply` 子命令的 help 文本即写明「根据联系人上下文生成只读回复建议，**不发送微信**」（F-097）；
- `docs/USAGE.md` 问答节写明「不能。整个项目坚持微信只读，回复能力只生成草稿」，且「金额、日期、报价和承诺**必须由使用者核对**」（F-099）；
- `skills/wechat-intelligence-hub/SKILL.md` 第 14 行在硬约束里写「回复内容只能作为本地草稿」（F-099）。

注意最后一条的措辞：官方把「需要人工核对金额、日期、报价和承诺」写成了**使用者责任**。这是一个诚实的产品边界声明——它不承诺草稿内容正确，只承诺不会替你发出去。

## 4. 可迁移模式

**模式 M4：把安全边界从「承诺」下沉为「结构」。**

当一个产品的核心承诺是「我不会做 X」，那么「我不会做 X」应当由**数据结构**保证而不是由**开发纪律**保证。本项目的做法值得借鉴：

1. 用**单一工具声明处**（`TOOL_SPECS`）枚举全部能力，新增能力必须显式登记；
2. 在**生成元数据的统一位置**置位安全属性（`read_only: True`），而不是逐个函数标注；
3. 把**有副作用的例外**放进**独立的、与主链路物理分离的文件**，并在安全文档中显式点名其「非只读」属性。

第 3 点尤其关键：例外存在是必然的（总有需要写权限的场景），**关键在于例外是否被隔离到能被审计的地方**。本项目没有假装没有例外，而是把例外命名为 `experimental`、独立成文件、写进安全文档——这比声称「绝无例外」更可信。

下一站：[07-flagship-renderer-and-view-model.md](07-flagship-renderer-and-view-model.md)。
