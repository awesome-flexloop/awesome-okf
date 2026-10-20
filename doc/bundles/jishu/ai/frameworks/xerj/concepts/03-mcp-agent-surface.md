---
type: Concept
title: MCP 智能体接口
description: XERJ 内置的 MCP stdio 服务器——17 个工具的分工、代理与非代理之别、回环 admin.key 认证回退、max_tokens 硬预算，以及工具计数漂移
tags: [xerj, mcp, 智能体接口, 工具, 认证]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-facts
    resource: /references/facts.md
    title: XERJ 事实清单
  - id: xerj-insights
    resource: /references/insights.md
    title: 架构洞察与知识地图
---

# MCP 智能体接口

`xerj mcp` 让安装好的那一个二进制同时成为 MCP 服务器——不需要另外下载、不需要编译（MCP 工具不是「另装一个东西」，而是同一个二进制的另一个子命令）。它讲 MCP over stdio，即 stdin/stdout 上的换行分隔 JSON-RPC 2.0 消息（F-059），并把请求代理给**已经在运行**的节点；它不会自己启动节点。

## 工具全景：17 个

`xerj-mcp` 的 crate 文档记录该进程暴露 **17 个**工具（F-060），已发布 schema 文件 `landing/docs/agents/schemas/mcp-tools.json` 的 `tools[]` 长度也是 17（F-063），单元测试函数名直接叫 `tools_list_has_all_seventeen`（F-062）。

| 工具 | 对应端点 | 性质 |
|---|---|---|
| `xerj_search` | `POST /{index}/_search` | 薄代理 |
| `xerj_semantic_search` | `POST /{index}/_search`（`semantic`） | 薄代理 |
| `xerj_vector_search` | `POST /{index}/_search`（`knn`） | 薄代理 |
| `xerj_hybrid_search` | `POST /{index}/_search`（`hybrid`） | 薄代理 |
| `xerj_memory_store` | `POST /_memory/{ns}` | 薄代理 |
| `xerj_memory_recall` | `POST /_memory/{ns}/_recall` | 薄代理 |
| `xerj_brain_ego` | `GET /_graph/{brain}/ego` | 薄代理 |
| `xerj_brain_link` | `POST /_graph/{brain}/link` | 薄代理 |
| `xerj_brain_unlink` | `DELETE /_graph/{brain}/link/{id}` | 薄代理 |
| `xerj_brain_overview` | `GET /_graph/{brain}/overview` | 薄代理 |
| `xerj_plan` | `POST /_ask` | 薄代理 |
| `xerj_map` | `POST /autoindex-catalog/_search` | **非薄代理**：读 autoindex 目录，按字节上限裁剪 |
| `xerj_code_search` | 参考编码管线 | **非薄代理**：跑 `tools/xerj-code/` 管线，返回渲染后的文本 |
| `xerj_field_report` | `POST /api/field-report`（xerj.org） | **非薄代理**：提交字段报告 |
| `xerj_hub_find` | `xerj ask` 流程 | Corpus Hub：哪个语料能回答 |
| `xerj_hub_def` | `xerj ask` 流程 | Corpus Hub：一个定义 |
| `xerj_hub_ask` | `xerj ask` 流程 | Corpus Hub：一个问题 |

> **「薄代理」的准确含义**：它构造的请求**正是**引擎表面已经接受的那种请求，然后把引擎返回的东西**原样**交回智能体——包括错误与拒绝。因此**能用 MCP 做的事，一定也能用 curl 做；反之亦然**。代理层不引入任何新能力。
>
> 例外只有三个（`xerj_map`、`xerj_code_search`、`xerj_field_report`）与三个 hub 工具。

### 一个值得学的做法：工具清单不手写

`landing/docs/agents/schemas/mcp-tools.json` 由**活的 `tools/list` 响应生成**，不是手写的；CI 脚本 `scripts/mcp-schema-check.sh` 负责再生成并作为门禁，另有一个单元测试在文件与服务实际提供的清单分叉时让构建失败。README 记录了这个守卫存在的原因：那个文件曾经宣称有 6 个工具，而二进制实际提供 10 个。

MCP 客户端配置：

```json
{
  "mcpServers": {
    "xerj": {
      "command": "/home/you/.local/bin/xerj",
      "args": ["mcp"],
      "env": { "XERJ_URL": "http://localhost:9200" }
    }
  }
}
```

`command` 必须用**绝对路径**：从桌面图标启动的 MCP 宿主不继承你的 shell `PATH`。

## 认证：三层优先级 + 一个刻意的回退

认证解析顺序是（F-065）：

```
--auth  >  XERJ_AUTH  >  （仅当目标是回环地址时）本地 admin.key 发现
```

第三层是一个刻意的设计。源码注释解释了原因（F-067）：

> 认证默认开启，而 `xerj init` **有意**不把凭据写进 `.mcp.json`（那是项目作用域、通常会被提交的文件）——没有这层回退，官方的一键设置会对每次工具调用都 401（#961）。

回退有严格边界（F-066）：**只对回环 URL 触发**。本地可读的密钥发往另一台主机是凭据泄露，不是便利。回退生效时用的密钥文件路径会在 **stderr** 公布，从不静默（F-072）——MCP 宿主用任意 cwd 启动这个服务器，「相对路径候选解析到了哪个文件」正是 onboarding 用户需要看到的。

优先级还有一个细节：空的 `XERJ_AUTH` 视为未设置。已提交进 `.mcp.json` 的空值不应遮蔽发现逻辑并变成 `Authorization: `（空头）。

## token 预算

五个检索工具接受 `max_tokens` 并被**强制执行**（F-069）：响应文本**绝不**超过预算。执行细节：

- 用 XERJ 自己的 `StandardTokenizer`（UAX #29 分词）计数，而不是任何通用近似；
- 重叠的 file:line 段落**先去重再计预算**；
- 超预算的命中降级为「定位符」形式（只有 file:line，没有正文）。

这一点值得单独记住：多数 MCP 检索工具把 `max_tokens` 当作**提示词**（"尽量别超"），而这里它是**不变量**（"绝不超"）。在一个上下文预算即成本的智能体宿主里，只有后者才有意义。

## 工具描述里的诚实声明

MCP 的工具描述会被宿主直接读进上下文，所以「描述里说了什么」就是智能体会相信什么。`xerj-mcp` 在这一点上非常严格，其 crate 文档列了四条必须与引擎保持一致的诚实声明：

1. **未过滤 kNN 是 HNSW 服务 + 精确重打分**（实测 recall@10 为 1.00）；过滤 kNN 与其他不适格形态（非余弦、SQ8、小索引）走精确暴力扫描。工具描述如实写出两者。
2. **`rerank` 需要运维方配置的提供方**，这个服务器无法提供密钥；它也是唯一一个让节点把文档文本发给第三方的参数。描述里用原话写出这一点，并且**只承诺机制**（一个校准概率取代 `_score`），**从不承诺准确率数字**——因为用真实提供方模型的排序质量本项目未经验证。
3. **`hybrid` 只支持 `fusion: "rrf"` 与 `"linear"`**。`"learned"` 被原样转发并由引擎大声拒绝（400），因此 schema 只声明前两者。
4. **`xerj_brain_*` 操作的是链接索引，不是图数据库**：确定性词法检测加显式断言，无神经理解、无查询语言、无无界遍历。每一条 brain 工具描述都同时说出这两点，引擎的拒绝（例如跳数上限）也原样回传给智能体。

> **可迁移的方法论**：工具描述是智能体的「先验知识」。把限制写进描述，而不是让智能体撞上 400 再自己猜，等于把一次失败调用变成零次。

## `xerj_plan`：确定性规划器

`xerj_plan` 对应 `POST /_ask`（F-075）：输入 `{index, prompt}`，输出 `{query, plan[], confidence, indices[]}`。

- 它是**确定性规则引擎，不是 LLM**（F-131）；
- 无法在索引中落地的短语返回 **422** 并指名该短语，**从不猜测**（F-131）；
- 返回的每个查询都已通过节点自身的解析器（F-132）——也就是说，拿到的 `query` 可以直接放进 `_search` 正文，不会因语法错被拒。

对智能体来说这是一件很划算的事：「把自然语言过滤条件变成可执行查询」这件事不需要额外一次 LLM 调用，也不需要智能体自己猜字段名。

## `xerj_field_report`：默认发送

这个工具**默认发送**字段报告（F-077）：先开 GitHub PR（走 `xerj feedback --submit --github-only`），GitHub 不可用时才 POST 到 `https://xerj.org/api/field-report`。`confirm: false` 预览，`--disable-feedback` / `XERJ_DISABLE_FEEDBACK=true` 关闭。

上游的立场很明确：**用了 XERJ 就该留下一份字段报告**。仓库的 `AGENTS.md` 把它写成硬性要求——「如果你用了 XERJ，你欠它一份现场报告」，并特别指出「一份说清楚工具在哪里让人难受的报告，比一份客气的报告值钱得多」。

## 一个必须知道的事实漂移

`AGENTS.md` 与 `README.md` 都写「13 个工具」（F-200、F-201），而代码实际服务 **17 个**（F-060、F-062、F-063）。差别在于新增的 `xerj_field_report` 与三个 `xerj_hub_*` 工具。

这不是随机错误，而是**定向的漂移**（详见 [架构洞察](/references/insights.md) 的洞察 3）：

| 面 | 更新机制 | 状态 |
|---|---|---|
| `landing/docs/agents/schemas/mcp-tools.json` | 由活的 `tools/list` 生成 + CI 漂移门禁 + 单元测试 | **永远最新** |
| `README.md` / `AGENTS.md` | 人手维护 | **会滞后** |

> **行动**：任何关于「XERJ 有哪些工具 / 多少个」的陈述，一律以**代码或已发布 schema** 为准；人读文档只用于理解意图与边界。同样的漂移也出现在检测器数（README 写 8 个，注册表实际 9 个，F-202、F-139）与格式族数（`WHY_XERJ.md` 写 13，代码侧 25 个抽取器 / 28 个 `Family` 变体，F-203、F-029、F-030）。

## 其他实现细节

| 项 | 值 |
|---|---|
| 默认协议版本 | `2025-06-18`（F-068） |
| 默认端点 | `http://localhost:9200`（F-068） |
| 批量消息 | 单对象与 JSON-RPC 批量数组都支持（2024-11-05 用批量，2025-06-18 放弃批量）（F-074） |
| stdout 用途 | **专用于** JSON-RPC 流；诊断走 stderr（F-072） |
| 未知参数 | 直接报错退出，不静默忽略（F-073） |
| hub 工具的条件服务 | 未配置 hub 签名密钥时，`xerj_hub_*` 从 `tools/list` 与帮助文本中**整体省略**（F-070） |
| 帮助文本的工具名单 | 取自 `tool_specs()`，与 `tools/list` 同一列表（F-071） |

最后一条尤其值得学：`--help` 里那句「proxies N tools — ...」的 N 是从**实际服务的那份清单**算出来的，而不是手写常量。注释明确写着目标：这一屏不能一边说「13 个」，一边根帮助说实际提供多少个。

## 相关概念

- [00 整体架构](/concepts/00-overview.md)：MCP 在整体中的位置
- [02 autoindex 零配置流水线](/concepts/02-autoindex-pipeline.md)：`xerj_map` 读的目录从哪来
- [04 检索路径与响应裁剪](/concepts/04-search-query-path.md)：五个检索工具实际调用的表面
- [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md)：语义搜索工具的嵌入器真相
- [08 参考编码与语料库](/concepts/08-reference-coding.md)：`xerj_code_search` 的完整契约
- 事实来源：[事实清单](/references/facts.md)
