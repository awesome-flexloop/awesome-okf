---
okf_version: "0.2"
type: Concept
title: "输出契约：格式、投影、Schema 渐进查询与退出码"
description: "dws 如何让人和机器读同一份结果——四种输出格式、字段投影、分级 Schema、结构化错误与七个退出码的稳定语义"
sources:
  - id: repo
    resource: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
  - id: reference
    resource: "docs/reference.md"
  - id: readme
    resource: "README.md"
facts: [F-030, F-031, F-032, F-041, F-042, F-043, F-044, F-045, F-046]
---

# 05 · 输出契约

> 核心判断：命令行工具的可用性一半在「能不能调通」，另一半在「结果能不能被下游稳定消费」。dws 把后者也写成了契约：固定格式、固定错误结构、固定退出码。

## 1. 四种输出格式

| 格式 | 面向 | 典型用途 |
|------|------|---------|
| `table` | 人 | 终端速览（默认） |
| `json` | 机器 | 管道、Agent、脚本 |
| `raw` | 人/机器 | 原样透传服务端响应，排障用 |
| `pretty` | 人 | 仅 `schema` 使用，展开嵌套结构 |

（F-041）

```bash
dws contact ... --format json
dws schema chat message send --format pretty
```

> 注意：`pretty` 是 `schema` 的专属格式，业务命令不提供。这不是遗漏，而是**避免把「可读」与「可解析」混在一条输出里**。

## 2. 落盘与字段投影

| 能力 | 写法 | 解决的问题 |
|------|------|-----------|
| 落盘 | `-o result.json` | 避免管道被日志污染 |
| 字段投影 | `--fields id,name` | 只取需要的列，降低下游解析成本 |
| jq 过滤 | `--jq '.items[]'` | 在工具内置过滤，减少外部依赖 |

（F-042）

**实践建议**：Agent 场景优先 `--format json --fields ...`，不要用 `--format raw`。raw 保留服务端原始结构，字段名可能随接口变化，不适合作为长期契约。

## 3. Schema 的渐进披露

```bash
dws schema                          # 总览
dws schema chat                     # 产品层
dws schema chat message send        # 叶层
dws schema --all --compact          # 全量 + 白名单字段
```

（F-031）

叶层字段包含（F-032）：

| 字段 | 含义 | 对 Agent 的价值 |
|------|------|----------------|
| 规范路径 | 唯一标识 | 稳定引用，不受别名影响 |
| 参数 | 名称、类型、必填、枚举 | 生成合法调用 |
| 约束 | 互斥/依赖/至少一个 | 避免非法组合 |
| effect | 读/写/删除等效果 | 判断副作用 |
| risk | 风险等级 | 决定是否需确认 |
| confirmation | 确认要求 | 知道何时会被拦 |
| idempotency | 是否幂等 | 决定能否重试 |
| 适用/回避场景 | 自然语言指引 | 减少误用 |

`--compact` 只输出白名单字段，适合**契约比对**（版本间 diff）；`--all` 适合审计与全量检索，但体量大，不要直接喂给模型。

## 4. 七个退出码

| 码 | 语义 | 调用方应做什么 |
|----|------|---------------|
| 0 | 成功 | 正常解析输出 |
| 1 | 一般错误 | 读错误体的 hint/actions |
| 2 | 参数错误 | 修正命令或参数，不重试 |
| 3 | 认证/授权错误 | 重新登录 |
| 4 | 待交互授权 | 完成设备码确认后重试 |
| 5 | 权限不足 | 补 scope 或换账号，不重试 |
| 6 | 限流/服务端错误 | 退避重试 |

（F-043）

**纪律**：脚本不要用「非 0 即失败」一把梭。2 与 5 重试没有意义，4 需要人类介入，只有 6 适合自动退避。

## 5. 结构化错误

`--format json` 下错误体包含四段（F-044）：

```json
{
  "category": "auth",
  "reason": "token_expired",
  "hint": "run `dws auth login` to refresh credentials",
  "actions": ["dws auth login"]
}
```

- `category` 用于机器分流；
- `reason` 是稳定枚举，适合做告警规则；
- `hint` 给人看；
- `actions` 可直接被执行器消费（如自动弹出登录）。

## 6. 输入侧：文件注入与纠错

| 能力 | 写法 | 边界 |
|------|------|------|
| 文件注入 | `--text @message.txt` | 严格前缀判定，`@` 开头才当文件 |
| 标准输入 | `--text @-` | 从 stdin 读取 |
| 智能纠错 | 命名风格、粘连拆分、模糊匹配、值归一 | 只纠正可判定的笔误，不猜业务意图 |

（F-045、F-046）

`@` 规则的关键在「严格」：如果允许模糊判定，那么以 `@` 开头的真实文本（如邮箱别名）会被误当文件路径。宁可让用户加转义，也不做猜测。

> **洞察**：一份好的 CLI 输出契约，本质上是**给下游程序的一份 API**。dws 把格式、字段、错误、退出码四件事全部固定，才使「Agent 自动编排」从演示走向可运维。

## 7. 常见坑

| 坑 | 表现 | 修正 |
|----|------|------|
| 把 table 当数据源 | 列宽随终端变化 | 用 `--format json` |
| 忽略退出码 4 | 脚本卡在等待授权 | 检测 4 并提示人类 |
| 直接消费 raw | 服务端字段改名即崩 | 用 json + 显式字段 |
| 全量 Schema 塞上下文 | 超长、噪声多 | 分级查询 + `--compact` |

## 延伸

- 安全确认与审计：[06-safety-dry-run-and-audit.md](06-safety-dry-run-and-audit.md)
- Agent 调用范式：[07-agent-skills-and-events.md](07-agent-skills-and-events.md)
- 参考手册：[references/facts.md](../references/facts.md)（F-041 ~ F-046）