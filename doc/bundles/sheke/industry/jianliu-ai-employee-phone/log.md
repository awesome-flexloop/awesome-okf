# 变更日志

## 2026-11-01

- 内容敏感度预检：`https://jianliu-ai.com/` 无登录、验证码、邀请码或付费墙，判为**公开内容（Public）**，入 `doc/bundles/sheke/industry/`。
- 采集：WebFetch 提取首页、`/solutions/`、`/phone/`、`/phone/products/`、`/cases/`、`/partner/`、`/news/`、`/news/104`；`sitemap.xml` 取栏目与文章计数；WebSearch 取外部软文与工商登记（启信宝、水滴信用）。
- 按七概念方法论执行场景 4（知识沉淀）链路 R → I → E → V → C：
  - R：[采集台账](references/source-manifest.md) 登记 S1~S13、公开性预检、同源判定与未采集项；[事实登记](references/site-facts.md) F-001~F-065，连续无跳号。
  - I：[五条洞察](concepts/08-insights.md)，每条含陈述/证据/反常识/行动四元组。
  - P0：C1~C16 核验（✅6 / ⚠️5 / ❌5）、E1~E4 口径差异、G1~G10 缺口，判定 `status: flagged`。
  - E：[两个 L1 模式](concepts/07-patterns.md)——四层证据分层法、三账验收法（各含 ≥3 反模式、检验标准与跨领域迁移示例）；共生成 16 个 Markdown（根 index + log + 9 篇 concepts + 3 篇 references + 2 个索引）。
  - V：V1~V6 共 6 条攻击（魔鬼代言人 ×2、新人、老板、未来、交叉一致性），采纳 5 条修正。
- 操作可复现性两问均不满足（无部署步骤/无后台截图/无参数配置），**不创建 `examples/`**。
- 未实测：未购买设备、未注册账号、未验证任何一项功能的真实可用性。

### 门禁结果

- `check-utf8.py`：**通过**（全库 12730 个文件均为有效 UTF-8）。
- `check-bundles-index.py`：3 处 +1 漂移，全部落在其他会话未跟踪 bundle `sheke/industry/kuaishou-wallpaper-publish-traffic`（总索引 701 vs 树 702、sheke 90 vs 91、industry 表合计 90 vs 91）；与本包无关，本包计数已按 +1 同步。
- `check-toctrees.py`：17 处问题**全部**指向 `kuaishou-wallpaper-publish-traffic`（未注册组 + 缺 toctree 条目）；本包 0 处。
- F 编号连续性：F-001~F-065 共 65 条，无缺号、无跳号、无重复。

### 已知环境基线

- 工作树中存在**其他会话**的未跟踪 bundle `sheke/industry/kuaishou-wallpaper-publish-traffic`，其在 `sheke/industry/index.md` 的 toctree 与分组表**未登记**。本包计数按「当前 worktree 已登记面 +1」计算（701 束 / sheke 90 束 / industry 41 束）；全量 gate 仍会因该未跟踪 bundle 报 +1 漂移，属**预存基线**，不计入本包缺陷。
- 未执行 Git 提交，等待用户明确提交请求。
