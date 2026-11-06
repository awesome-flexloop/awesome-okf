---
okf_version: "0.2"
type: bundle
title: "WeChat Intelligence Hub：把微信聊天变成本地个人情报库"
description: "本地优先、只读的微信个人情报库——只读 Reader + 两个 Codex Skill、旗舰交互式日报与 Markdown/HTML 双报告、定向检索与承诺/待回复/商机信号、全虚构 Demo 与真实接入差距；两轮信源核验（首轮 22 项 P0/P1：14✅/8⚠️/0❌；源码轮 44 条代码级事实 + 8 项 ⚠️ 逐项对账）"
tags: [wechat-intelligence-hub, wechat, local-first, read-only, personal-intelligence, codex-skill, python, agpl-3-0, 博文转化, 源码转化, 概念骨架]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki+source-code-to-okf-wiki
  at: "2026-11-06T16:52:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-06T16:52:00+08:00"
status: stable
stale_after: 2027-03-06
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/LNyKE5lex4qBOmIS4Z-7sg
  - id: github-repo
    url: https://github.com/Rion-Wu-tech/wechat-intelligence-hub
  - id: github-api
    url: https://api.github.com/repos/Rion-Wu-tech/wechat-intelligence-hub
  - id: source-code
    resource: https://github.com/Rion-Wu-tech/wechat-intelligence-hub/tree/fb6a42c34160d2ffa66ed5f114f8d8cdabe7f5f9
    title: "固定 commit fb6a42c 的源码快照（源码轮信源）"
---

# WeChat Intelligence Hub：把微信聊天变成本地个人情报库

> **类型**：产品解析 / 概念综述（**无 `examples/`**——操作可复现性两问皆「否」；官方命令仅作路径说明登记于 concepts/04）
> **信源（两轮）**：① 微信公众号「开源食谱」《5 天攒 2000 星！让微信聊天变情报库，相见恨晚！》（原创，豆芽菜小萌，2026-09-24 07:02 北京）→ 2026-11-06 经 GitHub REST API 与官方 README 逐项核验；② **2026-11-06 源码轮**：本地源码固定于 commit `fb6a42c`，经 AST 解析与 Grep 独立复核补齐代码级事实
> **核验结论**：首轮 22 项 P0/P1 声明 **14✅ / 8⚠️ / 0❌**；源码轮对 8 项 ⚠️ 逐项对账 → **6 项坐实 / 1 项拆分（明暗主题坐实、四视图风格修正为设计期候选）/ 2 项维持（星标与「5 天」窗口）**，另新增 3 项源码级发现 → `status: stable`
> **数据时点**：Star 等动态数字为 2026-11-06 快照；**源码事实锚定 commit `fb6a42c`（2026-10-17），该 commit 领先唯一 tag `v0.9.2-preview.2` 共 13 个提交**

## 本文概要

[WeChat Intelligence Hub](https://github.com/Rion-Wu-tech/wechat-intelligence-hub) 是一个 Python 编写、`AGPL-3.0-only` 许可、2026-09-04 创建的本地优先微信个人情报库（F-041、F-055）。它的底层是一个**只读 Reader**，只读取本机已有的聊天记录；上层把消息流转成日报、待回复、承诺、商机与复联线索（F-026、F-044）。官方以「一个产品，两个 Skill」交付：`wechat-cli` 与 `wechat-intelligence-hub`，可在 Codex 里用自然语言调用（F-046、F-051）。

它的差异点不在「搜聊天记录」，而在**输出带时态的状态与行动项**。旗舰交互式日报按博文图注给出四个入口（综合行动 / 群聊日报 / 重点联系人 / 商单信号雷达），报告同时产出 Markdown 与 HTML（F-011、F-014、F-052）。没有真实数据读取条件时，可用**全虚构 Demo** 先把索引、判断与报告链路跑通（F-032、F-049）。

## 阅读路径

**先建立概念（约 15 分钟）**

1. [00 · 项目身份、热度时点与信源距离](concepts/00-what-is-wechat-intelligence-hub.md)——官方身份、三星标口径、四层信源距离
2. [01 · 本地优先只读架构与两个 Skill](concepts/01-local-first-readonly-architecture.md)——Reader/情报产品分层、数据边界、⚠️「不重签名」范围
3. [02 · 旗舰交互式日报、双格式报告与四种视图](concepts/02-flagship-daily-report-and-four-views.md)——上层产物长什么样、哪些是图注单源

**再理解能力与边界**

4. [03 · 定向检索、重点联系人与行动项](concepts/03-search-contacts-and-actions.md)——消息 → 状态 → 行动项
5. [04 · 官方命令路径与全虚构 Demo 的差距](concepts/04-official-workflow-and-demo-gap.md)——五步官方命令（未实机验证）与接入前数据纪律
6. [05 · 洞察、可迁移模式与采用边界](concepts/05-insights-and-adoption-boundaries.md)——三条洞察、M1~M3 模式、AGPL-3.0-only 商业授权

**🔬 源码轮增量（深入到实现层）**

7. [06 · 只读契约的代码级实现](concepts/06-readonly-contract-and-code-evidence.md)——只读如何从承诺变成结构性保证；接入助手的反向边界；模式 M4
8. [07 · 旗舰渲染器与视图模型的源码实现](concepts/07-flagship-renderer-and-view-model.md)——`PAGE_SPECS` 四路由、移动端响应式分支、主题切换机制；⚠️ 修正「四种视图风格」；模式 M5
9. [08 · 源码架构分层与计数口径](concepts/08-source-code-architecture-and-counts.md)——双 CLI 分层、四个不可混用的计数口径、版本锚点时点差；模式 M6
10. [09 · 报告安全模型与源码级采用边界](concepts/09-safety-and-adoption-boundaries-from-source.md)——失败关闭的渲染安全模型、回复草稿确定性模板、采用边界修订版；模式 M7

**需要查证时**

- [references/article-source.md](references/article-source.md)（F-001~F-057）· [references/verification.md](references/verification.md)（P0 报告 + 勘误四张清单）
- 🔬 [references/source-code-map.md](references/source-code-map.md)（F-058~F-101 源码事实）· [references/source-code-verification.md](references/source-code-verification.md)（源码级对账与漂移分类）

## 核心事实速查

| 项 | 值 | 出处 |
|----|-----|------|
| 主线仓库 | `Rion-Wu-tech/wechat-intelligence-hub` | F-041、F-057 |
| 创建 / 发文 / 核验 | 2026-09-04 / 2026-09-24 / 2026-11-06 | F-041、F-002、F-042 |
| 语言 / 许可 | Python / `AGPL-3.0-only`（闭源·OEM·白标需商业授权） | F-041、F-055 |
| 当前版本 | `v0.9.2-preview.2`（博文未提）；🔬 源码基线 commit `fb6a42c` **领先该 tag 13 个提交** | F-045、F-060、F-061 |
| Star | 博文 1,976（标题取整 2,000）→ **2,764（2026-11-06）** | F-006、F-007、F-042 |
| 分层 | 底层只读 Reader + 上层情报产品；四层目录 | F-026、F-047 |
| 交付 | 一个产品、两个 Skill：`wechat-cli` / `wechat-intelligence-hub` | F-046 |
| 报告产物 | `wechat_daily_full.md`、`wechat-report/`、`wechat_daily_report.html` | F-052 |
| 报告格式 | Markdown + HTML 双格式 | F-014 |
| 日报入口 | 综合行动 / 群聊日报 / 重点联系人 / 商单信号雷达（🔬 源码 `PAGE_SPECS` 坐实） | F-011、F-080 |
| 🔬 只读实现 | `read_only` 对全部 30 工具统一置位、`mode=ro` 只读快照、零写入型函数 | F-073~F-075 |
| 🔬 工具口径 | 源码 `TOOL_SPECS` **30** 项 / 266 个输入字段（README 称 29 项，差 1 项口径） | F-069、F-070 |
| 🔬 CLI 口径 | Reader 36 个 + 情报产品 37 个子命令（合计 73，角色不同不可混用） | F-076、F-078、F-079 |
| 安装 / Demo | `./scripts/install.sh --with-sqlcipher --with-html`；`run_demo.sh` | F-048、F-049 |
| 数据边界 | 本机、不进 Git、不上服务器、样例虚构；只读不保证零封控 | F-028、F-053、F-054 |

## ⚠️ 阅读前必知的四条口径勘误

1. **「5 天」不是「创建后 5 天」**：API 显示仓库创建于 2026-09-04，与发文 2026-09-24 相隔约 20 天；「5 天攒 2000 星」是**博文口径的星标增长窗口，未独立核验**（F-006~F-008、F-041）。标题 2000 与正文 1976 是同一时点的取整与精确值，不是矛盾。🔬 源码轮复测星标仍为 2,764、`pushed_at` 未变，维持 ⚠️（F-101）。
2. **「不重签名」只约束 Reader 核心**：官方确认 Reader 不获取密钥、不重签名、不注入、不 Hook（F-027），但 macOS **候选接入助手**可能重启微信、重签名副本，Windows 首次获取路径尚未合入（F-056）。不可泛化为全项目承诺。🔬 源码轮在 `SECURITY.md` 找到逐字依据，官方明确实验性助手「**is not read-only**」，并说明安装与日报链路**不触发**获取动作——首轮范围勘误被完全坐实（F-091）。
3. ~~**截图不等于验收**：四个入口名、四种视图、移动端、回复草稿、检索五维度均为**博文/图注单源**，官方 README 只有语义对应、未逐字给出名称。~~
   🔬 **源码轮修订（2026-11-06）**：该判断是当时未 clone 源码下的**审慎保守结论，非官方文档缺失**。源码与官方文档逐字坐实**四入口名**（`PAGE_SPECS` 常量）、**移动端**（`.mobile-routes` 响应式分支）、**明暗主题**（`theme-button` + `localStorage` + `data-theme`）、**回复草稿**（`USAGE.md` + `SKILL.md` + `_reply_draft` 代码）、**检索五维度**（`USAGE.md` 第 4 章）。**唯一需修正的是「四种视图风格」**：A~D 实为 2026-08-28 设计研究文档的「四套**待选**视觉风格」，结论为「采用 A 作为主框架」，且 `style-previews/` 10 个文件**无任何运行时引用**——运行时不存在四套可切换主题（F-087~F-090）。
4. **全虚构 Demo 证明链路，不证明真实数据可用**：官方 Demo 使用虚构数据（F-032、F-049）；完整历史需本人授权本地数据库，且只覆盖已同步到本机、当前可读的数据（F-034、F-054）。

## 采用提示与已知边界

- **许可证**：`AGPL-3.0-only`，闭源 / OEM / 白标需商业授权；修改后以网络服务对外提供会触发 AGPL 网络开源义务（F-055）。商业内嵌前建议法务确认。
- **成熟度**：`v0.9.2-preview.2` + commit `fb6a42c`；命令与目录结构可能漂移；本束命令为官方文档快照，**未实机验证**（F-045、F-048、F-060）。
- **平台风险**：只读不保证零封控、不保证任意微信版本长期兼容；macOS 新机器获取路径官方标注未实测（F-035、F-054、F-056）。
- **数字时效**：Star/功能集为 2026-11-06 核验时点快照，`stale_after: 2027-03-06`，到期前复核。
- **证据强度**：本束无 ❌ 级反证。首轮标题热度 hook 未独立核验；UI 层命名的「图注单源」判定已由源码轮解除，唯「四种视图风格」修正为设计期候选（F-101）。
- 🔬 **源码轮新增边界**：
  - **接入助手不是只读的**——`rion_wechat_access.py` 独立成文件、官方标注实验性，可能重启微信并重签名影子副本，需单独授权评估（F-091）；
  - **报告安全是「失败关闭」模型**——Pandoc 禁原始 HTML + nh3 白名单 + 哈希 CSP；缺 nh3 时报错而非降级；**加固不追溯旧 HTML**，升级后需重新生成（F-092~F-094）；
  - **回复草稿是确定性模板**（6 类 intent × 关系远近），非模型自由生成；语气取自最近 30 天跨联系人私聊聚合，样本不足时用中性草稿（F-096、F-098）；
  - **计数口径四不可混用**：30 工具 / 36 Reader CLI / 37 情报 CLI / 73 合计（F-079）。

## 信源与可信度

- 事实全集（F-001~F-057，博文 40 + 官方核验 17）：[references/article-source.md](references/article-source.md)
- P0 核验报告与勘误四张清单：[references/verification.md](references/verification.md)
- 🔬 源码事实全集（F-058~F-101，44 条）：[references/source-code-map.md](references/source-code-map.md)
- 🔬 源码级核验与首轮对账（8 项 ⚠️ 逐项 + 漂移分类 D1~D5 + 计数双口径复核）：[references/source-code-verification.md](references/source-code-verification.md)
- 信源距离：第三方开源推介号 → 已升级为 GitHub REST API 与官方 README 一手交叉核验 → **源码轮再升级为代码级事实**（AST + Grep 独立复核）。
- 归属歧义：检索中另有 `echoD886/wechat-intelligence-hub` 同名仓库，主线以官方 clone 地址与 API `full_name` 确认（F-057）；源码 remote 再次确认（F-058）。
- 同名仓库、`share?code=` 等私域信号均未出现；源码为公开开源代码，内容敏感度预检判定 Public，走标准 Spec Mode。

## 主题关联

- [wigolo](../wigolo/index.md)：同属「本地优先情报层」路线，但面向公开 Web（MCP 搜索/抓取）；本束面向本机聊天数据，二者互补。
- [agent-reach](../agent-reach/index.md)：同样以 Skill/CLI 形态给 Agent 装能力，可对照「能力层」与「情报产品」的边界划分。
- [inkos](../inkos/index.md)：同为 `AGPL-3.0` 许可的中文开源项目，可对照许可证采用边界。
- [creatorhub](../creatorhub/index.md)：同样涉及本地数据、隐私合规与「无 LICENSE/边界需勘误」类核验议题。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
