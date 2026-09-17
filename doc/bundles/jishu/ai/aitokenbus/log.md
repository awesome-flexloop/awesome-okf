# 更新日志

## 2026-09-16

**Status**: `stable`（厂商/个人自宣内容，附强边界声明；非 flagged）

经 blog-article-to-okf-wiki 七阶段工作流生成：微信公众号"唐霜"博文（2026-07-22，约 3900 字）→ 3 篇概念文档 + 2 篇信源文档 + 索引/日志，共 8 个文件；无 examples（操作可复现性两问均为"否"，产品自述发布资讯骨架）。

**R 阶段（事实+核验）**：

- F-001~F-024 博文源事实 + F-025~F-037 核验补充事实，共 37 条，双份登记（spec facts.md ↔ references/article-source.md）编号连续无跳号。
- 12 项 P0：7 ✅ / 4 ⚠️ / 2 ❌（其中平台核心功能 6 项均 ✅ 或部分成立）。
- 核验手段：browser_use 实地探测站点公开页+前端代码+公开 API（未注册）；general_purpose_task 独立 WebSearch 厂商官方源。
- ❌ 勘误 1 项（非核心）：qwen-3.8 发文时点不存在（Qwen3.8 于 2026-08-03 发布，官方 ID `qwen3.8-*`，当时最新 Qwen3.7）；❌ 风险 1 项：零独立信源、无备案/主体/协议。
- ⚠️ 主要口径差：免费池供给（2 节点、1/35 模型可用）vs"免费无限"；ollama 零佐证（实为自研 SUMU）；跨池自动 failover 无说明；TC 属性无条款文本。
- 信源距离预判：个人开发者自宣 → 全部产品能力声明按 P0 核验，index 顶部加"厂商自述"提示块。

**I/E 阶段**：三层知识拆分（事实层 00 / 机制层 01 / 边界层 02）；信源先行（references 先于 concepts）；00 含 Mermaid 生态流转图；所有具体声明带 F 编号；主题关联互链 token-economy-explosion、domestic-model-token-export、free-llm-api-roundup。

**V 阶段**：直接运行子模块底层 gate 脚本（`invoke gates.*` 的同一实现，纯 stdlib 无依赖），三门全绿：

- `check-bundles-index.py`：9 域 / 59 组 / **555 束**五面一致；
- `check-toctrees.py`：全部 index.md 引用有效、所有内容文档可达；
- `check-utf8.py`：10412 个文件均为有效 UTF-8；
- 双份 F 编号正则比对一致（F-001~F-037，37=37，连续无跳号）；
- bundle 内相对链接逐一可达，无绝对链接与家目录路径泄漏。

> **并行会话计数说明**：入库当日有另一会话同时新增 16 个 WIP 束（ai 直挂 9 束 + ai-agent 嵌套 5 束 + tencent 1 束 + sheke/marketing 1 束），总索引在 538（已提交基线）→555（含全部 17 个新束）间多次漂移；本束按 gate「目录树地面真值」口径完成最终对账收敛（ai 组 203、jishu 422、全库 555），并修复了 ai/index.md 中他会话悬空在 toctree 块外的 8 条条目（含补登遗漏的 inurl-byok-free-models）。

**状态说明**：核心产品声明经实地核验成立 → stable；qwen 版本号错误属结语顺带提及（非主结论），走勘误不触发 flagged；2026-12-31 前安排复核（供给规模/主体合规/TC 规则/failover 文档）。
