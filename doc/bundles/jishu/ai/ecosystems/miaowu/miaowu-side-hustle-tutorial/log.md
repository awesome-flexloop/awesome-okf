# 更新日志

## 2026-11-09

**New Bundle**: 新增 `miaowu-side-hustle-tutorial`（秒悟 Meoo 副业接单教程：从身边门店观察到首单成交）

* 微信公众号「秒悟Meoo」2026-10-29 公开文章《纳尼?！真有人靠 Meoo 做副业月入过万！》经 `seven-concepts-cmd`（知识沉淀场景，R→I→E→V→C）转化为 OKF v0.2 操作教程束
* 结构：`index.md` + `log.md` + `concepts/`（00-tutorial-map / 01-pick-a-store-and-observe / 02-write-the-hypothesis / 03-build-first-version / 04-run-stores-and-trial / 05-price-maintain-accept）+ `references/`（source-ledger：S1–S5 与 T-001–T-043 教程构造物 + verification：14 项 P0 核验）；**不设 `examples/`**（源文无可复现的安装/配置/代码流程，示例以正文"模板/清单"形式内联）
* 与同分组既有束 `miaowu-douzhanggui-case` 的**分工**：案例束负责「这一个案例发生了什么」（事实登记 F-001–F-060），本束负责「换一个人怎么照着做」（方法构造 T-001–T-043）；**事实不重复登记**，本束逐条 `derived_from` 指回案例束 F 编号

**R 阶段（事实采集）**

* 复用 S1（微信公开文章）作为唯一一手信源，不重复登记 F 编号；`references/source-ledger.md` 另列 S2（案例束）、S3（产品束 03-web-app-build）、S4（实训束）、S5（meoo.com）作为复用与交叉参照通道
* 复采范围：文章六段叙事（人物与背景 / 需求发现 / 工具层 / 客户开发 / 试用迭代 / 成交与后续 / 通用建议）
* 公开性预检沿用案例束结论：URL 无 `share?code=`/`token=`，无登录墙

**I 阶段（洞察）**

* 在案例束 5 条四元组洞察之上，把「不可直接照做」的叙述转为**可执行的因果链**：观察 → 假设 → 首版 → 跑店 → 报价 → 验收
* 关键判断：源文的可迁移部分是**顺序与判据**，不是产品与金额；教程据此把每一步拆成「目标 / 判据 / 动作 / 反模式」

**E 阶段（萃取）**

* 萃取六步主线与 43 条教程构造物（T-001–T-043），分为六组：地图与边界（T-001–T-002）、选题观察（T-003–T-010）、需求假设（T-011–T-018）、首版构建（T-019–T-028）、跑店试用（T-029–T-036）、成交维护验收（T-037–T-043）
* 每条 T 标注 `type: editorial_inference`、`status: inferred`、`derived_from` 指向 F 编号；**新增的是方法，不是新事实**
* 落盘 1 篇束索引 + 1 篇 concepts 索引 + 6 篇章节正文 + 1 篇 references 索引 + 2 篇参考文档

**V 阶段（对抗审查）**

* 14 项 P0 核验：结论为 **3 项 ✅ / 5 项 ⚠️ / 2 项 ❌ / 4 项口径限定**（详见 `references/verification.md`）
* 关键发现：#6「1 万元」为**单笔成交**，不可读作持续月收入；#13 源文**无市场调研**，教程第 01 章的三判据属本束补足的方法而非源文主张；#14 能否卖给第二三家源文自述**无答案**，教程第 05 章只给「何时停止/加价」的判断框架，不作成功率承诺
* 据此在束索引设「阅读前必知」，并在正文显式标注「可迁移的是方法，不是结果」

**C 阶段（闭环）**

* 注册四层索引并完成计数对账：本束自身贡献为 `miaowu` 7→8、`ecosystems` 105→106、`jishu/ai` 291→292、`jishu` 529→530、总索引 `total_bundles` 723→724；域数 9 与组数 64 不变（新束落既有 miaowu 组）
* 同步面：`doc/bundles/index.md`（frontmatter / 计数行 / mermaid 节点 / 域节标题 / ai 表行）、`doc/bundles/jishu/index.md`、`doc/bundles/jishu/ai/index.md`、`doc/bundles/jishu/ai/ecosystems/index.md`、`doc/bundles/jishu/ai/ecosystems/miaowu/index.md`（bullet + toctree + description）、`doc/index.md`、`README.md`
* 门禁运行记录（2026-11-09）：
  * `check-bundles-index.py` ✅ 通过：9 域 / 64 组 / 724 束，frontmatter、计数行、节标题、分组表、toctree 五面一致
  * `check-utf8.py` ✅ 通过：13095 个文件均为有效 UTF-8
  * `check-asset-baseline.py` ✅ 通过：HEAD 基线 13046 md / 9787 内容文档 / 100838428 字节，行尾归一残差 +399781（本束新增），基线口径一致
  * `check-toctrees.py` ❌ 首轮拦截 37 处：全部落在 `jishu/ai/ecosystems/tencent/` 下 `wecom-aibot-python-sdk`、`wecom-cli`、`wecom-unified` 三个既有目录（缺 `index.md` 或未接入 `tencent/index.md` toctree），**与本束无关**；本束 12 个 Markdown 文件均被 `concepts/index.md`、`references/index.md`、`index.md` 三层 toctree 完整收录，未产生任何新增拦截项
* 修复轮（2026-11-09）：为 `wecom-aibot-python-sdk`、`wecom-cli` 补建束根 `index.md`（前者另补 `examples/index.md`），并在 `tencent/index.md` 的导航表、相关链接与 toctree 中收录 `wecom-aibot-python-sdk`、`wecom-cli`、`wecom-unified`；复核结果：`check-toctrees.py` ✅ 0 拦截，`check-bundles-index.py` ✅ 9 域 / 64 组 / 727 束，`check-utf8.py` ✅ 13117 个文件，`check-asset-baseline.py` ✅（残差 +439230）
* 提交动作待用户指令，本次未执行 git commit