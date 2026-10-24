# 更新日志

## 2026-10-23 · 增补 AI Works 一键代部署

- **触发**：用户提供知乎专栏文章 `https://zhuanlan.zhihu.com/p/2079176428197603018`，要求学习并更新本 wiki。
- **公开性预检**：文章位于 `zhuanlan.zhihu.com`，无 `share?code=`/`token=`/邀请码，无需登录、无付费墙/验证码 → **Public**；产出落 `doc/bundles/`。
- **采集**：browser_use 渲染读取全文；页面标题《🚀 Vibe coding作品能直接上线？AI Works 一键代部署来了！》，发布方「知乎产品情报局」（已认证机构号），编辑于 2026-10-19 17:53（北京）；全文无「看山工作台/飞书/lark-cli/服务域」关键词（F-108）。
- **事实登记**：新增 F-084~F-108 共 25 条，双份登记于 spec 区 `facts.md` 与本 bundle `references/article-source.md`；两侧编号集合均为 F-001~F-108，连续无跳号。新增口径缺口 G10~G13（工程细节、审核标准与时长、10 个应用上限统计口径、视频 href）。
- **结构更新**：新增概念页 `concepts/09-ai-works-one-click-deploy.md`（部署更新层），`concepts/index.md` 9→10 篇并追加 toctree；`concepts/07-participation-path.md` 增加 3.5 节，链到 09；`concepts/00-overview.md` 阅读地图增加 09 与读取顺序第 5 条。
- **核验**：新增 C20–C28 共 9 项（6✅ / 3⚠️ / 0❌），P0 总数 19→28。C23（数据库）、C24（秘钥/代码不上传仓库）、C27（10 个应用上限）为 ⚠️ 平台自述、无独立复现；C28 为本包关键词检索确认该文不涉及看山工作台/飞书/服务域。
- **flag 状态**：保持 `status: flagged`。新源文只补部署链路，不解决第二弹活动规则的单源问题，不修正既有 5 项源文勘误；公告亦未提及「科学季」项目类型（F-108、G7）。
- **无 examples/**：公告提供的是平台操作指引，无命令文本、无版本、无实际输出，未满足「操作可复现」两问；部署流程以概念页承载，并在页内标注「未真机执行」。
- **文件**：15 → **16** 个（根 index + log + concepts 10 + references 3）。束数不变（仍为 1 束），故 `bundles/index.md` 计数面无需调整。
- **门禁**：随本轮更新复跑 check-bundles-index / check-toctrees / check-utf8 / check-links，结果见本轮最终验证记录。

**Verification（2026-10-23 增补后复跑）**：

- ✅ `scripts/check-bundles-index.py`：9 域 / 63 组 / 672 束，五面一致（本束仍为 1 束，计数面不变）。
- ✅ `scripts/check-toctrees.py`：全部 index.md 引用有效，09 经 `concepts/index` 可达。
- ✅ `scripts/check-utf8.py`：12273 个文件均为有效 UTF-8。
- ✅ 主仓 `check-links.py`（本束）：16 个 Markdown、89 个本地引用，0 断链。
- ✅ 双份 F 编号比对：`facts.md` 与 `article-source.md` 各 108 行，F-001~F-108 连续无跳号、无重复，声明列逐字一致（0 处差异）。
- ✅ 新页 frontmatter 齐备：`okf_version/type/title/description/tags/generated/verified/status/stale_after/sources`；`status: flagged`、`stale_after: 2026-12-31`。
- ✅ 勘误与缺口落实：G10~G13 已写入双份事实表；09 页显式标注「未真机执行」「项目类型待核」；根 index 与 verification 均保留 flagged 说明。

## 2026-10-22

**Generation**：由 spec 区 `zhihu-ai-science-workshop-okf-wiki`（Task 1~5）生成 AI 科学创新工坊第二弹知识包（Task 6）。

- **骨架判定**：无 `examples/`。理由：源文本体为活动规则宣告页，正文含 **0 个代码块、0 个表格**（F-011），为纯文本活动规则 + 名单 + 列表结构，不满足「操作可复现」两问；行动清单属设计产物，并入 concepts 路径层（07/08 篇承载）。同簇先例：`zhihu-monetization`、`big-tech-pontzi-track-selection`、`workbuddy-content-system` 均无 `examples/`。
- **归属决策**：`sheke/industry/` 新建独立束 `zhihu-ai-science-workshop`。理由：单一平台的赛事型创作激励规则解析，属行业/商业趋势分析型；**不并入 `zhihu-monetization`**——后者 F 编号已用至 F-067 且围绕「AI Works 广场 / 打卡挑战赛 / 科学季」三信源，塞入会突破其「三信源」结构前提并制造跨活动口径混用（两活动为**不同实体**：主办方、时间窗、玩法、奖励形态均不同）。
- **三层结构**：事实层（00 总览 + 01/02/03/04/05 五篇事实）→ 机制层（06 四元组洞察，根因/影响/建议全部标「洞察/推断」）→ 路径层（07 路径 + 08 风险，收益仅挂 F 或标「待验证」）；references 3 篇（`index` + `article-source` + `verification`）+ 根 index + log，共 15 个文件。
- **G3 生成顺序**：`references/article-source.md` → `references/verification.md` → `references/index.md` → `concepts/00` → `05` → `06` → `07` → `08` → `concepts/index.md` → 根 `index.md`（最后写）→ `log.md`。
- **双份一致性**：`references/article-source.md` 与 spec 区 `facts.md` 的 F 编号事实表双份登记，F-001~F-083 连续无跳号（83 行，集合相等、声明列逐字一致）。
- **核验状态**：P0 19 项核验结论（C1~C19）与勘误四张清单详见 `references/verification.md`；据此设 `status: flagged`、`stale_after: 2026-12-31`（保守失败管理：第二弹全部细节为平台单源，权威媒体仅覆盖第一期，7 处内链 href 不可复核）。
- **5 项源文勘误**：①「豆包标准模式会员卡」非官方产品名（官方为「豆包专业版·标准套餐」，¥68 是连续包月价，F-073）；②「第四步投稿要求实为 5 项」是首轮核验误判，实为 4 条（F-077）；③ 诺奖年份误标——官方为**诺贝尔物理学奖 2026**、**Halzen 一人独享**（Prize share 1/1），不可写成 2025 年度或「Halzen 与 IceCube 团队」（F-078）；④ 诺奖公布日 10-06 **早于**活动起始 10-09 三天，「落在活动窗口内」错误（F-081）；⑤「650 亿穿过人体」系转述失真——官方为「约 100 万亿/秒穿过人体」，「650 亿」原指**太阳中微子穿过小指甲**（F-080）。
- **去重判定**：7 篇检出参赛作品中，1 篇与另一篇**同作者同署名、正文同句**，不计入独立佐证；独立参赛作品为 **6 篇**（F-066~F-071），非 7 篇（F-072）。
- **防混用对照**（已在 00/04/08 篇显性化）：① 本活动**≠**「科学季 2026」（主办方、时间窗、玩法、奖励形态均不同）；② 两期工坊之间 10/1–10/8 空档无说明，两期是否共用「科学季」项目类型未获明示（G9）；③ 40,000 元现金奖池**不可**与 10 张豆包卡名义面值 680 元相加（F-082）；④ 「海量 Token」无量化口径（G2），**不可**用参赛者自述积分 36500 反推官方额度；⑤ 诺奖年份 2026 与获奖者 Halzen 个人不可写成 2025 年度或「与 IceCube 团队」。
- **索引更新**：industry 组导航表/toctree/description 三处 29→30 束；sheke 域 industry 行 29→30 束、域简介 29→30；总 `bundles/index.md` frontmatter `total_bundles` 670→671、正文计数行、mermaid sheke 75→76、社科域节标题 75→76、社科域分组表 industry 行 29→30。
- **结构范式**：对齐同簇 `zhihu-monetization`（NN-kebab-case.md + 内容导航表 + 隐藏 toctree 含 log + flagged/stale_after + 双 references 体例）与 `big-tech-pontzi-track-selection`（事实层挂 F 编号、机制层标推断、路径层零收益承诺）。

**Verification（Task 9 · 2026-10-22）**：awesome-okf-xs 子模块无 invoke 任务定义（`tasks.py` 不存在，`invoke gates.all` 通道不可用）→ 按 spec Task 9 约定执行**手动等效验证**，八项逐条如下（验证脚本一次性遍历 bundle 15 文件 + spec 区 facts.md 1 文件）：

- [x] ① UTF-8 strict roundtrip：`scripts/check-utf8.py` 通过——12254 个文件均为有效 UTF-8；
- [x] ② 双份 F 编号正则比对（`^\|\s*F-(\d{3})\s*\|`）：`references/article-source.md` 与 spec 区 `facts.md` 集合相等（各 83 条），F-001~F-083 连续无跳号、**83 行声明列逐字一致**（首轮比对曾发现 F-073 的信源定位与备注列措辞不一致，已按 spec 侧权威表述回填 bundle）；
- [x] ③ 三级 toctree 逐一 Test-Path：bundle 根 index 3 条目（concepts/index + references/index + log）、concepts/index 9 条目、references/index 2 条目、父级 `sheke/industry/index.md` 30 条目与 `sheke/index.md` 9 条目全部存在且可达；
- [x] ④ 三级计数同步（复用 `scripts/check-bundles-index.py` 的 `_count_bundles` 递归口径做地面真值）：总 671 / sheke 76 / industry 30，与总索引 frontmatter `total_bundles`、计数行、mermaid、节标题、分组表、域级简介、域级分组行、组级 description、组级导航行、组级 toctree 共 10 个计数面全部一致；`scripts/check-bundles-index.py` 独立通过（9 域 / 63 组 / 671 束，五面一致）；
- [x] ⑤ 相对链接可达 + 零绝对路径链接：全部相对形式链接解析可达；`file` 协议的绝对路径链接写法零命中（首轮曾发现 `concepts/00-overview.md` 的跨束链接少一层 `../`，已修正为 `../../zhihu-monetization/...`）；
- [x] ⑥ 敏感信息零残留：密钥样式（`sk-` / `ghp_` / `AKIA`）、键值赋值型敏感模式（token/password/secret/api_key）、本机绝对路径三种模式全部零命中；
- [x] ⑦ frontmatter 结构完整：14 个含 frontmatter 文件开/闭围栏齐备、无重复键、REQUIRED 字段（okf_version/type/title/description/generated/verified/status）齐备、正文非空；`log.md` 按体例无 frontmatter；
- [x] ⑧ 5 项源文勘误落实回验：勘误 1「标准套餐 + 连续包月」、勘误 2「投稿要求恒为 4 条」、勘误 3「2026 年度诺贝尔物理学奖 + 2026-10-06 早于活动起始」、勘误 4「100 万亿/秒穿过人体」、勘误 5「独立作品 6 篇」五个要点均在 bundle 正文中命中。

**结论**：八项全绿。验证过程中另发现并修复三类问题：① **F 编号重排后的交叉引用漂移**（facts/article-source 两表的行号已按勘误段重排为 F-073~F-083，但 concepts/00~04、verification.md 与两表内部备注列仍指向旧编号 F-070~F-080）——经 45 处定向锚定替换后编号引用与权威声明逐一对齐；② **frontmatter 首行开围栏丢失**（批量归一化脚本的拼接缺陷）——已由定向修复脚本补回 14 个文件；③ **F-073 双份登记措辞不一致 + `concepts/00-overview.md` 跨束链接层级错误**——已按 spec 侧权威表述与实际目录层级修正。

> **门禁边界说明**：`scripts/check-toctrees.py` 在本 bundle 范围内零报错；该脚本当前报的 2 条问题位于 `doc/bundles/sheke/finance/ponzi-scheme/`（未跟踪目录，属并行会话的在途产物），与本 bundle 无关，不在本任务修改范围。
