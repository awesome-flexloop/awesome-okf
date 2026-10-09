# 变更日志（Log）

## 2026-10-08 - 初始版本

- ✅ 基于 **blog-article-to-okf-bundle** 方法论链路 **R→I→E→V→C** 生成（seven-concepts-cmd 场景 4 知识沉淀，session sc-20261008-wechat-article-okf）
- ✅ R 阶段（事实采集）：browser_use 打开微信文章（公开内容判定），提取 `#js_content` 全文约 1223 字；采集博文事实 25 条（F-001 ~ F-025：场景元信息 1 + 群友体验 10 + 老师简答展开 14），事实基准为 `.trae/specs/okf-wiki-ecosystem/wechat-presence-joy-meditation-blog-okf-wiki/facts.md`（唯一合法事实集）
- ✅ R 阶段 P0/P1 权威核验：WebSearch 三组交叉（佛教 pīti/sukha/七觉支/禅那次第；Benson 放松反应与 2013 PLOS ONE 基因表达研究；hypnopompic 半醒过渡期；冥想不良反应 Lindahl et al. 2017；信源生态喜马拉雅转述专辑），补充 8 条（F-026 ~ F-033）。6 项关键声明 3 ✅ / 2 ⚠️ / 1 ℹ️，**零勘误**，整包判 **stable**（主观体验+观点分层，非源文错误型）
- ✅ I 阶段：操作可复现性两问皆否（一次性自发个案、无版本化流程、无输入输出实测）→ 不设 examples/；归属 `sheke/personal-growth/`（排除 yixue：非古籍医典；排除 guoxue/daojia：非经典解读；该组已有 naval 微信博文转化先例）
- ✅ E 阶段（信源先行成文）：references/（2 篇 + index）→ concepts/（3 篇 + index）→ 根 index → log

### 信源

- **主信源（博文）**：https://mp.weixin.qq.com/s/x8WOQKShXQYSeGiKLv52Vw （微信公众号"身体自我修复研究者"，大方老师原创，2026-10-04 09:07 湖北，群问答约 1223 字，无配图/数据/引用链接）
- **核验/参照信源**：
  - Harvard Medical School：https://hms.harvard.edu/news/mind-body-genomics （放松反应与基因表达，F-028）
  - PMC 综述：https://pmc.ncbi.nlm.nih.gov/articles/PMC4475556/ （冥想生理学，F-028）
  - PLOS ONE 2017：https://doi.org/10.1371/journal.pone.0176239 （冥想相关挑战，F-031）
  - Britannica：https://www.britannica.com/topic/hypnopompic-state （半醒过渡期，F-029）
  - 巴利语相应部 SN 46《觉支相应》与《清净道论》通行学术译本（F-027，传统参照）
  - 喜马拉雅转述专辑：https://www.ximalaya.com/album/76860531 （信源生态，F-026）

### 文件清单（共 9 个文件）

| 文件路径 | 说明 |
|---------|------|
| `index.md` | Bundle 根索引（okf_version + 性质与可信声明、结构总览、分层导航、主题关联、信任与生命周期、已知边界 6 条、toctree） |
| `concepts/index.md` | 概念文档子目录索引（学习路径 + toctree） |
| `concepts/00-waking-softness-phenomenon.md` | 现象层：群聊师徒结构、体验五要素、两问与四句简答、知识身份逐句标注 |
| `concepts/01-traditional-science-mapping.md` | 参照层：pīti/sukha/轻安与禅那判准、放松反应证据边界、半醒过渡期、AI 术语溯源、三套参照并置 Mermaid 图 |
| `concepts/02-reading-meditation-experience.md` | 边界层：三层语言模型、可带走三点、六条不可外推承诺、不良反应信号与就医边界、AI 命名纪律、读者检查单 |
| `references/index.md` | 信源登记簿子目录索引（信源清单 + F 编号段索引 + 可信度说明） |
| `references/article-source.md` | 博文事实 F-001~F-025 + 核验定位 F-026~F-033 双份登记与分类统计 |
| `references/verification.md` | 定位型核验说明 + 6 项逐项核验表 + 三层语言 Mermaid 模型 + 安全边界 + 权威 URL |
| `log.md` | 本文件 |

### 质量门记录（V 阶段，2026-10-08 回填）

执行环境无 `invoke` 门禁命令，以下为按 G1–G4 纪律执行的**手动等效门禁**（PowerShell 机械校验，非目视）：

| 门 | 检查项 | 结果 |
|---|--------|------|
| G1 | UTF-8 strict roundtrip（spec facts.md + bundle 9/10 文件） | ✅ 10 文件全部 OK |
| G1 | F 编号机械比对：spec facts.md ↔ references/article-source.md | ✅ 各 33 条，range 1..33，集合一致、连续无缺号 |
| G1 | 禁用路径：file 协议绝对链接、Windows 用户目录绝对路径、`.temp/` 引用 | ✅ 0 处（正文与链接中均无；本行仅为检查项文字描述） |
| G2 | 文件计数：声明 9 文件 ↔ 实存（index/log + concepts 4 + references 3） | ✅ 三处一致 |
| G2 | toctree 条目存在性（严格解析 ```{toctree} 块，逐条 Test-Path） | ✅ 8/8 可达（根 3 + concepts/index 3 + references/index 2） |
| G2 | 相对链接机械校验（正则提取全部 Markdown 相对链接逐条 Test-Path） | ✅ 0 BROKEN（首轮发现 2 处同组互链层级错误，已修复后复跑全绿：根 index 与 concepts/02 指向 naval 束的相对层级） |
| G3 | 四视角对抗审查（读者/作者/学科/安全） | ✅ 见下"V 阶段修订" |
| G4 | frontmatter 完整性（okf_version 0.2 / type / 时间戳一致性 / source 溯源） | ✅ 9 文件齐备，时间戳统一 2026-10-08T17:00:00+08:00 |

**V 阶段修订（对抗审查产出）**：
1. Lindahl et al. 2017 删除未经本次检索证实的具体样本量 "n=73"，改为"基于对西方佛教禅修者的深度访谈"（verification.md + concepts/02 同步）。
2. F-029 删除出自二手汇编且混指 hypnagogic 的"约 37%"数字，改为 Britannica 口径"相当常见"，并在 spec facts.md 与 bundle 两侧同步注明弃用理由。
3. 同组互链相对路径 2 处层级错误修复（见 G2）。

**索引接入（V 收尾，机械计数以索引 frontmatter/toctree 为准，非目录计数——稀疏检出）**：
- `sheke/personal-growth/index.md`：total_bundles 10→11，导航表/阅读路径/toctree 三处增量；
- `sheke/index.md`：personal-growth 行 10→11，域简介追加本束定位；
- `bundles/index.md`：total_bundles 592→593，sheke 58→59（mermaid 图 + 分组标题），personal-growth 行 10→11 并追加本束简介。

**未跑项声明**：invoke gates 不可用，未执行自动化脚本门禁；Sphinx 构建未在本会话运行（toctree 结构与黄金先例 naval-learn-build-link 对齐）。

### stable 判定说明

本文无数字/日期/疗效/名人归属类硬事实，不适用"勘误型 flagged"规则；6 项核验未发现源文错误，故判 **stable**。但 stable 仅表示"事实层无失败项"，不构成对大方老师灵修体系的背书：全部超验主张（存在性快乐、量级增长、能量、维度、按神的方式生活）按观点层呈现，"内在阴阳融合"标注为 AI 生成非传统术语，全包顶部与核验报告均明示非医疗建议与不良反应就医边界。
