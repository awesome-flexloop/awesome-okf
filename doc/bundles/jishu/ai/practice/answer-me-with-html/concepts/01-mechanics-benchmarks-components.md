---
okf_version: "0.2"
type: Concept
title: "机制、九种组件与基准"
description: "Agent 自主判断 + 组件指令 + CLI 渲染的运作机制，flow/sequence/tree/timeline/limits/annot/kv/callout/table 九种组件，页面与视频基准的核验与 token 经济性边界"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/A-9ViZO69NJ30ZTsofjYeQ
    title: "开源星探 2026-10-06 公众号文章"
  - id: github
    url: https://github.com/QingYunA/answer-me-with-html
    title: "answer-me-with-html 仓库 README"
last_modified: 2026-10-10
status: draft
stale_after: 2026-12-31
---

# 机制、九种组件与基准

## 运作机制

Agent 安装可使用以后，流程是自适应的（F-007）：

1. 你像往常一样提问（例如「Explain the TCP three-way handshake」「Redis or Memcached for our cache?」「Map out how the modules in this repo fit together」）；
2. Agent **自行判断**这个问题「值得做一页」；
3. Agent 写一段很短的 Markdown 草稿——标题 + 若干组件指令；
4. CLI `am` 接手排版、配色、画图、导出；
5. 约 50ms 后浏览器（或渲染结果）交付一张可读可分享的 HTML 页面。

页面保存在 `~/.answer-me-with-html/pages/` 目录下，右上角按钮可切换主题、明暗模式，以及复制生成该页面的 Markdown 草稿（核对仓库 README）。

## 九种组件

Agent 根据问题类型**自动**选组件，无需手动指定（F-008）：

| 组件 | 用途 / 典型场景 |
|------|----------------|
| `flow` | 架构图、调用链、决策分支；自动布局，支持分组、判断节点、数据库节点 |
| `sequence` | 多角色按时间顺序的消息交换，典型如 TCP 握手 |
| `tree` | 目录结构、模块树、分类体系 |
| `timeline` | 历史事件、发布记录、项目阶段 |
| `limits` | 一个值相对于其上限是多少 |
| `annot` | 逐词标注一句话，标出问题词与替换建议 |
| `kv` | 元数据、图纸标题块 |
| `callout` | 结论、提示、警告 |
| `table` | 多维度对比表；单元格写 `ok` / `no` / `warn` 自动渲染成 ✓ / ✗ / ! |

## 基准测试与核验

以下数字来自仓库 `bench/` 目录的官方自测（模式为 Claude Sonnet 5.5，同样的问题用直接写 HTML 与用本 Skill 两种方式对比）。

### 页面场景（3 topics × 3 runs，取中位数）

| 指标 | 直接让模型写 HTML | 用 answer-me-with-html | 优势 |
|------|:---:|:---:|:---:|
| 输出 token | 5,341 | **870** | 6.1× 更少 |
| 耗时 | 33 s | **12 s** | 2.8× 更快 |
| 单次成本 | $0.092 | **$0.067** | 27% 更便宜 |

### 讲解视频场景（单 topic，5 runs：3 手写 / 2 `am video`，取中位数）

| 指标 | 手写视频页面 | `am video` | 优势 |
|------|:---:|:---:|:---:|
| 输出 token | 27,839 | **1,566** | 17.8× 更少 |
| 耗时 | 202 s | **17 s** | 11.8× 更快 |

> ⚠️ **数据性质（F-011）**：视频侧是「单个主题、五轮」的量级参考，README 明确建议当作粗略量级而非精确比值；页面侧为同模型同规格 3×3 取中位数。

### 重要边界：省不省钱取决于上下文装载

README 特别提示（F-010，博客未强调）：Skill 会额外加入**两次短的往返（turns）**，而"每次往返都会重读上下文"。因此：

- 在**普通装载**下，省下的输出 token > 两次往返的复读成本 → 更快、更省、更便宜；
- 在**重型装载**（约 51,000 token 的工具/规则/技能上下文）下，两次额外往返的复读成本 > 省下的 token → 实测反而**贵约 20%**。

结论：token 节省几乎普遍成立（省的是「打字」），但**成本**优势不是绝对的，重度上下文 Agent 场景要按实测评估，不能把 README 的 $0.067 当成普适结论。

## 关键事实引用

基准与外设参数对应 [信源事实清单](../references/article-source.md) F-009~F-011，核验结论见 [P0 核验报告](../references/verification.md)。