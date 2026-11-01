# 变更日志

## 2026-10-31

- 内容敏感度预检：用户提供的 `mp.weixin.qq.com` 文章，无登录、验证码、邀请码或付费墙，判为**公开内容（Public）**，入 `doc/bundles/sheke/industry/`。
- 采集：WebFetch 直取页面正文（本次未被微信反爬拦截，无需回退 `agent-browser`）；标题《抖音突然成立大批公司，准备放手一搏》（电商派Pro，作者李响，2026-10-30）与页面一致。
- 按 `blog-article-to-okf-bundle` 模式执行 R → I → E → V：
  - **R**：[事实清单](references/article-source.md) F-001~F-036，连续无跳号；口径分 `page_fact`（28）/ `author_claim`（8）两类，无 `reporter_test`。
  - **P0**：完成 C1~C19 核验（15 项多源通过、3 项部分通过、1 项未通过）、E1~E5 口径差异与勘误、G1~G6 缺口，判定 `status: flagged`。
  - **I**：三层拆分——公司与时间线层、算力基建与投资层、AI 电商落地与转化层；作者判断（F-002、F-026、F-031~F-036）显式标「作者观点」。
  - **E**：先写 `references/`（信源先行），再写 3 篇 concepts，最后写 `index.md`；更新父级导航与计数面。
- 操作可复现性两问均不满足（无读者可照做的安装/配置/代码流程），**不创建 `examples/`**。
- 未实测：未实地核验数据中心与算力中心项目，算力投资额、公司注册信息均依赖公开工商信息与官方/媒体披露转引。

### 核验摘要

- ✅ 通过（15 项）：廊坊平舒数源（C1）、内蒙三家（C2）、中卫两家（C3）、Anew Labs（C4）、腾讯云廊坊（C8）、火山引擎芜湖+无为（C9）、太行算力（C10）、和林格尔（C11）、经营 AI+ 大赛（C12）、达人 +30%（C13）、商家 +74%（C14）、豆包领券/抖店板块（C16）、阿里 3800 亿元（C17）、腾讯 528 亿元（C18）、腾讯 AI 预付款（C19）。
- ⚠️ 部分通过（3 项）：廊坊时延来源标注不符（C5/E2）、算力指数与十强家数（C7/E3）、双 11 百万→千万增幅 94% vs 78%（C15/E4）。
- ❌ 未通过（1 项）：廊坊数据中心「**40 个**」与官方一致口径「**36 个**」冲突（C6/E1）——本报告唯一确定勘误。
- 口径差异 5 组（E1 数据中心数量勘误、E2 时延来源、E3 十强家数、E4 双 11 增幅、E5 Anew Labs 中文名）。
- 已知缺口 6 项（G1~G6）。

### 勘误落实

- 源文「廊坊 40 个数据中心」→ 正文（[01 · 廊坊算力禀赋](concepts/01-compute-base-and-investment.md)）与[速查表](index.md)均以官方口径 **36 个** 呈现，并标注「源文作 40 个」；核验报告单列 E1。**未静默照搬**。

### 门禁结果

- `invoke gates.*` 依赖不可用，按等价命令在 `projects/awesome-okf-xs/` 下直接执行底层脚本，结果见下方「执行记录」。

### 已知环境基线

- 计数更新按**磁盘实测真值 + 本包 +1** 计算：总索引 `total_bundles` 694→**695**、`sheke` 域 85→**86**、`industry` 分组 36→**37**。
- 本包未执行 Git 提交，等待用户明确提交请求。

## 2026-10-31 · 门禁执行记录

在 `projects/awesome-okf-xs/` 下按等价命令直接执行底层脚本（`invoke gates.*` 依赖不可用），实测结果：

| 门禁 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | ✅ 12620 个文件均为有效 UTF-8 |
| toctree | `python scripts/check-toctrees.py` | ✅ 全部 index.md 引用有效，所有内容文档均可达 |
| 总索引对账 | `python scripts/check-bundles-index.py` | ✅ 9 域 / 64 组 / **695 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致（首跑报 3 处漂移，修复后通过） |
| 资产基线口径 | `python scripts/check-asset-baseline.py` | ✅ 校验通过（`total_bundles` 单一真相源 695，三处规模数字一致） |
| Python 红线 | `python -m pytest tests/unit/test_no_future_annotations.py -q` | ✅ 11 passed |

- 首跑 `check-bundles-index.py` 拦截 3 处计数漂移：`total_bundles` 694 vs 目录树 695、sheke 节标题 85 vs 86、分组表之和 85 vs 86；已按目录树地面真值同步五面后复跑通过。
- 双份 F 编号一致性：spec `facts.md` 与 bundle `references/article-source.md` 均为 F-001~F-036，连续无跳号，集合一致。
- 本包未执行 Git 提交，等待用户明确提交请求。
