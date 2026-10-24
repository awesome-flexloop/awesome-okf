# 变更日志（Log）

## 2026-10-23 · 飞书服务域计数修正（复核）

- **触发**：用户指出飞书服务域数量与原文不符。
- **复核方式**：browser_use 重新打开原页面，定位「功能四：连接企业协作工具 → 飞书」，逐字读取并逐条计数。
- **原文**：飞书通过 lark-cli 接入，覆盖**约 25 个服务域**，主要包括——协作文档 8 项、沟通与日程 6 项、组织与流程 5 项、扩展能力 2 项（通用 OpenAPI 调用、查询接口参数）。
- **结论**：逐条 **21 项**；若将「扩展能力」合并为 1 项则为 **20 项**。原记「19 项 + 通用 OpenAPI = 20 项」漏计了「查询接口参数」这一独立条目。
- **修正**：F-113、`verification.md` P0-4 与 2.3 口径对照、`concepts/03` 计数口径、根 index「已知边界」统一改为「21 项（合并扩展能力则 20 项）」；「约 25」仍作为原文近似值保留，不改写为 25。
- **门禁**：随本轮更新复跑四项门禁（见下方最新验证条目）。

**Verification（2026-10-23 修正后复跑）**：

- ✅ `check-bundles-index.py`：9 域 / 63 组 / 672 束，五面一致（本轮未增减束数）。
- ✅ `check-toctrees.py`：全部 index.md 引用有效，所有内容文档可达。
- ✅ `check-utf8.py`：12273 个文件均为有效 UTF-8。
- ✅ `check-links.py`（本束）：18 个 Markdown、53 个本地引用，0 断链。
- ✅ 飞书计数复核：原文逐条 21 项（8+6+5+2；合并扩展能力则 20 项）；F-113、P0-4、2.3 口径对照、concepts/03、根 index 已统一。P0-4 仍判 ⚠️，因为「约 25」与 21 项之间仍有未说明差额。

## 2026-10-23 · 初始生成（官方手册知识化 R→I→E→V）

- **触发**：用户提供知乎站内页面《看山工作台：产品介绍与使用手册》（`https://www.zhihu.com/parker/campaign/2078900697026905490`），要求以 seven-concepts-cmd 全面学习并生成 OKF Wiki 教程。
- **方法论编排日志（CMD-LOG）**：`cmd=seven-concepts` | session `sc-20261023-kanshan-workbench-okf` | S0 CMD_START → S1 SCENARIO_DETECTED（knowledge 知识沉淀）→ S2 CHAIN_SELECTED（R→I→E→V；C 留待用户指令）→ G1/G2/G3/G4 逐门通过。
- **信源获取**：WebFetch 首次失败（知乎页面为 JS 渲染），改用 browser_use 子代理渲染读取全文；页面无需登录，无登录墙、付费墙、验证码；两次采集（摘要 + 逐字全文）一致。页面标题「看山工作台：产品介绍与使用手册」，最终 URL 未跳转。
- **公开性预检**：无 `share?code=`/`token=`/邀请码，域名 `zhihu.com` 为公开站点，页面无访问控制 → **Public**；产出落 `doc/bundles/`，未进入私域工作流。
- **事实登记**：F-001~F-120 连续 120 条，单侧登记于 [references/article-source.md](references/article-source.md)，未另建 spec `facts.md`。**偏差说明**：信源为单一官方页面，双份登记只会产生同步漂移风险；按 blog-article-to-okf-wiki 的「单源可单侧登记并注记」路径处理，在此留痕。
- **P0 核验**（核验日 2026-10-23）：14 项 → **✅ 原文明确 11 / ⚠️ 计数不可精确复核 3 / ❌ 0**。3 项 ⚠️ 均为服务计数（飞书约 25、企业微信 14、钉钉 22）与枚举项数不完全对应；另有真实浏览器连接器、并发上限版本口径、受管 Python 环境等边界问题，已在 P0 表说明列标注但保留「原文明确」判定。
- **骨架判定**（操作可复现性两问）：Q1 页面是否含读者可照做的安装/配置/调用流程 → **是**（第二部分 13 节使用手册）；Q2 流程是否具备可复现性（有步骤、有输入输出）→ **是，但有限定**（页面无版本号，本包未真机执行）→ 设 `examples/`（4 篇），并在 examples 顶部与根 index 显式标注「非实测」。
- **归属判定**：`jishu/ai/products/kanshan-workbench/`。主线实体为知乎 AI 桌面产品「看山工作台」；`products` 组已有 ToDesk AI、Orca ADE、Octop、BrowserAct 等桌面/终端产品束，语义匹配；未新建分组。
- **文件**：18 个（根 index/log + concepts 8 + examples 5 + references 3）。concepts 7 篇正文 + 1 篇目录 index；examples 4 篇正文 + 1 篇目录 index。
- **状态**：`draft`；`stale_after: 2026-12-31`（页面无版本号，产品迭代快，收紧复核窗口）。

## 2026-10-23 · V 阶段（对抗审查 + 机械门禁）

> 门禁直接运行子模块 stdlib 脚本（`projects/awesome-okf-xs/scripts/`），未经 `invoke gates.*` 通道，故不声称「`invoke gates` 通过」。

- ✅ `scripts/check-bundles-index.py`：通过——`9 域 / 63 组 / 672 束`，frontmatter、计数行、节标题、分组表、toctree 五面一致。
- ✅ `scripts/check-toctrees.py`：通过——全部 `index.md` 引用有效，所有内容文档均可达。
- ✅ `scripts/check-utf8.py`：通过——12272 个文件均为有效 UTF-8。
- ✅ **相对链接全可达**：主仓 `check-links.py` 以子模块为工作根、`--path doc/bundles/jishu/ai/products/kanshan-workbench` 扫描 18 个 Markdown、53 个本地引用与 2 个外部引用，本地引用 0 断链（外部链接默认不做可达性检查）。**V 中修复 1 条断链**：`examples/00-install-and-first-task.md` 原链接 `02-browser-and-quickbar.md` 指向不存在的文件名，已改为实际的 `02-browser-quickbar.md`。
- ✅ **F 集合连续**：正则 `^\|\s*F-(\d{3})\s*\|` 提取 F-001~F-120，共 120 条，无跳号、无重复。
- ✅ **敏感路径零残留**：全束扫描 `file:///`、`C:\Users\`、`/Users/`，零命中。
- ✅ **frontmatter 齐备**：14 个带 frontmatter 的文档（根 index + 7 concepts + 4 examples + 2 references）均含 `type/title/description/tags/generated/verified/status/stale_after/sources`；根 index 另含 `okf_version`。3 个 `*/index.md` 与 `log.md` 按本库约定不设 frontmatter。
- ✅ **勘误落实**：F-113~F-115 的服务计数口径、F-116 的云/本地数据流向张力、F-117~F-120 的连接器/并发/Python/PPT 待核项，均已在根 index「已知边界」、verification.md 与相关概念页显式呈现。
- ✅ **三级索引接入**：`products/index.md` 33→34（表行 + toctree + 正文计数）、`jishu/ai/index.md` 265→266（正文 + products 行）、`jishu/index.md` AI 行 265→266、`bundles/index.md` total 671→672 / jishu 497→498 / ai 265→266（frontmatter + 正文 + Mermaid + 节标题 + 分组表）。

## 2026-10-23 · C 阶段（预留）

- **未执行提交**：用户本次只要求生成知识包，未要求提交；且 `bundles/index.md` 等聚合文件可能存在并行会话在途改动。原子提交留待用户明确指令，按「子模块先提交 → 主仓 spec/子模块指针」顺序执行，不 push。
