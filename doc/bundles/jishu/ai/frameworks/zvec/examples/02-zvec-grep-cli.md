---
type: Example
title: zvec-grep CLI 实战：为工作区建语义索引
description: zg 安装、示例书架索引构建、CLI 与 OpenCode Agent 双路径检索的完整实战流程
tags: [zvec, zvec-grep, zg, cli, mcp, example]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# zvec-grep CLI 实战：为工作区建语义索引

依据官方"快速上手"的可复现流程：安装 → 准备示例书架 → 建索引 → Agent 与 CLI 双路径检索。

## 安装

需要 Node.js 22 或更新版本：

```bash
npm install -g @zvec/zvec-grep
zg version
```

## 准备示例书架并建索引

下载两本公版书，用英文检索模型建索引（示例工作区是英文小说，故显式覆盖面向代码的默认模型）：

```bash
mkdir zg-mystery && cd zg-mystery
curl --retry 3 --retry-all-errors --progress-bar -fL \
  -o alice-in-wonderland.txt https://raw.githubusercontent.com/GITenberg/Alice-s-Adventures-in-Wonderland_11/master/11.txt \
  -o sherlock-holmes.txt https://raw.githubusercontent.com/GITenberg/The-Memoirs-of-Sherlock-Holmes_834/master/834.txt

zg index --embedding local/potion-retrieval-32m
```

索引保存于 `<workspace>/.zvec-grep/`，后续扫描自动排除该目录。代码工作区默认模型为 `local/potion-code-16m-v2`；大型工作区首次构建建议限定范围：

```bash
zg index --embedding local/potion-code-16m-v2 -g "src/**" -g "docs/**" -g "!dist/**"
```

## 面向 Agent：通过 OpenCode 提问

安装 OpenCode 后接入（提示词无需指定工具，Agent 自行选择）：

```bash
zg install --target opencode --yes
opencode run --model opencode/deepseek-v4-flash-free \
  "An unseen creature left a few marks. What did the detective infer? Cite local evidence."
```

Agent 内部会调用 `zvec_grep_search` 工具（`{"root":..., "query":..., "fts":[...], "fuse":true}` 形态），返回带 `sherlock-holmes.txt:5479-5516` 式可核验来源位置的证据。

## 面向用户：CLI 直接检索

```bash
zg query --human \
  "An unseen creature left a few marks. What did the detective infer?" \
  --limit 3
```

应优先返回 `sherlock-holmes.txt` 相关段落并附带来源位置。

## 常用检索变体

```bash
zg query --fts "AuthService"                 # BM25 关键词
zg query --vector "凭证在哪里校验"            # 纯语义
zg query --rg -n -F "AuthService" src        # 内置 ripgrep 穷举
zg query --hybrid "authentication flow" --fts "ForbiddenError" --fuse --limit 10
zg query "plugin lifecycle" -g "src/**" -g "!src/generated/**" -t ts
```

## 索引维护

```bash
zg index                     # 增量更新（复用模型与路径设置）
zg status                    # 文件、失败信息与建议
zg index --rebuild --embedding local/potion-multilingual-128m  # 换模型需重建
zg index --drop --yes        # 显式删除（破坏性）
```

## 相关概念

- [Agent 集成](/concepts/09-agent-integration.md)：检索路由与 MCP 工具面
- [总览](/concepts/00-overview.md)：zvec 与 zvec-grep 的产品分工
- [Embedding 与 Reranker](/concepts/07-embedding-reranker.md)
