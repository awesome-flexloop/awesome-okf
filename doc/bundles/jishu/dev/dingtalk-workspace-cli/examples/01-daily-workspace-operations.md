---
okf_version: "0.2"
type: Example
title: "演练：日常办公操作与输出控制"
description: "用 dws 完成找人、看日程、查文档、建待办等日常动作——读操作的直接执行、写操作的三段式、四种输出格式与投影、六类常见错误"
---

# 01 · 演练：日常办公操作与输出控制

> **性质**：命令取自仓库 `README.md` 的 Quick Start 与白板章节（F-079），**未在本机实跑**；`<...>` 为占位符，需替换为企业内的真实 ID。
> 相关概念：[03 命令面与产品组织](../concepts/03-command-surface-and-products.md)、[05 输出与 Schema 发现](../concepts/05-output-and-schema-discovery.md)、[06 安全、预览与审计](../concepts/06-safety-dry-run-and-audit.md)。

## 一条总原则

**读操作可以直接跑，写操作必须先预演再确认。** 这是 dws 把安全成本前移到命令契约的方式：`--dry-run` 让请求可见，`--yes` 才是真正的放行开关（F-047 ~ F-052）。

## 场景 1：找人

```bash
dws contact user search --query "engineering"
dws contact user get-self --jq '.result[0].orgEmployeeModel | {name: .orgUserName, dept: .depts[0].deptName, userId}'
```

第一条按关键词检索同事；第二条取自己的档案并用 `--jq` 只留下三个字段。Agent 场景应优先第二种写法——把返回从整棵组织树压到几行，显著节省上下文。

## 场景 2：看日程

```bash
dws calendar event list
```

默认列出今天的日程。需要跨天或指定时间窗时，以 `dws calendar event list --help` 输出的 flag 为准（例如时间范围与分页参数），不要凭印象拼参数。

## 场景 3：查文档与知识

```bash
dws doc search --query "quarterly"
dws drive list
dws minutes list mine
```

- `doc search` 检索钉钉文档；
- `drive list` 列出云盘文件；
- `minutes list mine` 列出自己创建的 AI 听记。

三者都属读操作，可直接执行；需要全量翻页时加 `--page-all`（默认 10 页、硬上限 500，见 F-058）。

## 场景 4：看白板

```bash
dws whiteboard +query --node "<whiteboard-node-id>" --view summary --format json
dws whiteboard render --source @whiteboard.json --output ./whiteboard-preview.svg --format json
dws whiteboard +diff --help
```

- `+query` 读取白板节点内容，`--view summary` 取摘要视图；
- `render` 在本地把 OpenNodes 源文件渲染成 SVG 预览，属于**本地预演**，不写服务端；
- `+diff` 用于在 `+update` 之前查看拟议变更。

白板是「先预览、后提交」最典型的场景：渲染保真度与警告需要人工过目，确认预览后才创建或更新。

## 场景 5：建待办（写操作三段式）

```bash
# 第一段：预演，不产生副作用
dws todo task create --title "Quarterly report" --executors "<your-userId>" --dry-run

# 第二段：确认参数无误后执行；Agent 必须显式 --yes
dws todo task create --title "Quarterly report" --executors "<your-userId>" --yes

# 第三段：回读验证
dws todo task list --dry-run
```

三段式对应三类证据：**预演证明请求长什么样，执行返回证明服务端接受了什么，审计日志证明谁在何时做了什么**（JSONL 哈希链，见概念 06）。

## 输出格式与投影

| 需求 | 写法 | 说明 |
|------|------|------|
| 人读 | 默认 table | 终端对齐，适合快速扫读 |
| 程序消费 | `--format json` | 稳定结构，Agent 首选 |
| 原样响应 | `--format raw` | 不经加工的服务端响应 |
| 落盘 | `-o <path>` 或 `--output <path>` | 结果写入文件，终端只留摘要 |
| 字段裁剪 | `--fields a,b,c` | 只保留指定字段 |
| 精确投影 | `--jq '<expr>'` | 任意 jq 表达式，最省 token |

组合示例：

```bash
dws contact user search --query "engineering" --format json --fields userId,name --output /tmp/contacts.json
dws contact user search --query "engineering" --jq '.result[] | {userId, name}'
```

## 输入注入

参数值过长或含特殊字符时，用 `@` 注入避免 shell 转义问题（F-045）：

```bash
dws whiteboard render --source @whiteboard.json --output ./whiteboard-preview.svg --format json
dws whiteboard render --source @- --output ./preview.svg --format json < whiteboard.json
```

- `@<path>`：从文件读取；
- `@-`：从标准输入读取。

`@` 前缀按严格规则判定，不做猜解——普通字符串不会被误当文件路径（F-045）。

## 六类常见错误

| 现象 | 根因 | 处置 |
|------|------|------|
| `unknown flag` | 用了不存在的 flag 或 snake_case | flag 一律 kebab-case，先看 `--help`（F-024） |
| `accepts no arguments` | 把自由文本当位置参数传入 | 改用对应的 `--query` / `--title` 等命名 flag |
| 输出为空但退出码 0 | 查询条件过窄或分页未翻 | 放宽关键词，或加 `--page-all` |
| 退出码 3 | 未登录或令牌无法刷新 | `dws auth login` 或切换 profile |
| 退出码 4 | 需要管理员审批或交互授权 | 发起 CLI 访问申请，审批后重试 |
| `--jq` 报错 | 表达式与返回结构不匹配 | 先不加 `--jq` 看一次结构再写投影 |

退出码全表与结构化错误字段见 [05 输出与 Schema 发现](../concepts/05-output-and-schema-discovery.md)。

## 探索未知命令的正确顺序

1. `dws --help` 看顶层服务域；
2. `dws <domain> --help` 看该域命令族；
3. `dws <domain> <verb> --help` 确认 flag 与必填项；
4. `dws schema "<domain> <verb>" --compact` 看结构化契约（参数约束、风险、确认要求）；
5. 写操作先 `--dry-run`，再执行。

`--help` 决定命令是否存在、二进制接受哪些 flag；Schema 决定参数约束与安全语义。二者冲突时视为契约漂移，只传 Cobra 接受的 flag，并采用更保守的安全语义（F-080）。

下一篇 → [02 Agent 工作流](02-agent-workflow.md)