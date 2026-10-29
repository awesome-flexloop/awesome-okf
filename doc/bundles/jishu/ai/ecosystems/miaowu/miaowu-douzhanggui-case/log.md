# 更新日志

## 2026-10-29

**New Bundle**: 新增 `miaowu-douzhanggui-case`（秒悟 Meoo 副业案例：「豆掌柜」拼豆店门店管理应用）

* 微信公众号「秒悟Meoo」2026-10-29 01:00 公开文章《纳尼?！真有人靠 Meoo 做副业月入过万！》经 `seven-concepts-cmd`（R→I→E→V）转化为 OKF v0.2 单案例拆解束
* 结构：`index.md` + `log.md` + `concepts/`（00-case-overview / 01-need-discovery-and-tooling / 02-customer-development-and-trial / 03-deal-boundaries-and-insights）+ `references/`（source-ledger F-001–F-060 + verification 19 项 P0：9✅/9⚠️/1❌）；**不设 `examples/`**（源文无可复现的安装/配置/代码流程）

**R 阶段（事实采集）**

* 登记 S1–S5 信源台账：S1 为微信公开文章、S2–S4 为同分组既有束（仅主题关联，非独立第三方）、S5 为 Meoo 官方平台入口
* 机械登记 F-001–F-060 编号事实，分 8 段（文章身份与人物背景 / 需求发现 / 工具层与开发起点 / 客户开发与三类失败 / 试用与迭代 / 成交与后续 / 通用建议 / 结尾互动）
* 公开性预检：URL 无 `share?code=`/`token=`，无登录墙；WebFetch 单通道取到完整正文
* 识别并登记 7 项放弃核验项（应用真实性、成交流水、跑店细节、迭代计数、平台能力、后续进展、配图内容）

**I 阶段（洞察）**

* 冻结 5 条四元组洞察：①需求可来自「观察他人工作的困难」而非先有生意假设；②工具层降摩擦 ≠ 业务闭环；③免费试用的关键在交换条件而非免费；④成交条款含隐性维护成本，报价口径须接单时谈清；⑤单源案例证明「存在」不证明「可复制」

**E 阶段（萃取）**

* 提炼 2 个可迁移模式：模式 A「观察式需求发现法」（现场观察问题清单 → 合并式假设 → 找人验证）、模式 B「免费试用换反馈的转化法」（多客户跑店 + 可复用材料 + 免费时长与交换条件 + 现场迭代 + 报价边界）
* 落盘 4 篇概念文档与 2 篇参考文档（source-ledger / verification）；不设 `examples/`

**V 阶段（对抗审查）**

* 19 项 P0 核验：**9✅ / 9⚠️ / 1❌**
* 关键发现：全部事实为**单源**且发布账号即案例中工具的提供方（利益相关）；「1 万元」仅导语与回指各出现一次、正文成交句未复述（核验项 9）；「累计迭代数百次」为定性表述（核验项 13）；「可复制到第二三家」源文明确无答案，判 ❌（核验项 17）；标题「月入过万」与单笔 1 万元口径需区分（核验项 19）
* 据此在根索引设「阅读前必知的三件事」，并在正文显式标注「可迁移的是方法，不是结果」

**C 阶段（闭环）**

* 注册四层索引并完成计数对账：本束自身贡献为 `miaowu` 6→7、`ecosystems` 103→104、`jishu/ai` 277→278、`jishu` 510→511、总索引 `total_bundles` 692→693；域数 9 与组数 63 不变（新束落既有 miaowu 组）
* 同步面：`doc/bundles/index.md`（frontmatter / 计数行 / mermaid 节点 / 域节标题 / ai 表行）、`doc/bundles/jishu/index.md`、`doc/bundles/jishu/ai/index.md`、`doc/bundles/jishu/ai/ecosystems/index.md`、`doc/bundles/jishu/ai/ecosystems/miaowu/index.md`（bullet + toctree + description）、`doc/index.md`、`README.md`
* 门禁：`check-bundles-index.py` 对账通过（9 域 / 63 组 / 693 束）；`check-toctrees.py`、`check-utf8.py`、`check-links.py` 见运行记录
* 提交动作待用户指令，本次未执行 git commit
